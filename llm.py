import json
import re
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_MAP = {
    "small": "llama-3.1-8b-instant",
    "large": "llama-3.3-70b-versatile",
}

SYSTEM_PROMPT = """You are a Windows PC assistant. Map the user's command to one of these exact JSON actions.
Output ONLY raw JSON. No markdown, no explanation.

AVAILABLE ACTIONS:

{"action": "open", "target": "app name"}
{"action": "close", "target": "app name"}
{"action": "search", "engine": "google/youtube/spotify/github/maps", "query": "search term"}
{"action": "url", "url": "https://example.com"}
{"action": "volume", "value": "up/down/mute/unmute/0-100"}
{"action": "brightness", "value": "up/down/0-100"}
{"action": "screenshot"}
{"action": "timer", "seconds": 60}
{"action": "battery"}
{"action": "media", "command": "next/previous/pause"}
{"action": "window", "command": "minimize_all"}
{"action": "system", "command": "shutdown /s /t 0"}
{"action": "open_folder", "path": "C:/Users/Atharv/Downloads"}
{"action": "type", "text": "text to type"}
{"action": "clipboard", "command": "copy/paste/clear"}

Examples:
increase volume → {"action": "volume", "value": "up"}
make it louder → {"action": "volume", "value": "up"}
turn brightness down → {"action": "brightness", "value": "down"}
skip song → {"action": "media", "command": "next"}
search for lofi on youtube → {"action": "search", "engine": "youtube", "query": "lofi"}

If truly cannot map to any action:
{"action": "unknown", "reason": "brief reason"}
"""

CONVO_PROMPT = """You are Friday, a helpful personal AI assistant.
Answer the user's question or respond naturally and concisely.
Keep responses short — 2-3 sentences max since this will be spoken aloud.
"""

def call_llm(user_input: str, model_size: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=MODEL_MAP[model_size],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        print(f"[DEBUG] Raw output:\n{raw}")
        return parse_json(raw)
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return {"action": "unknown", "reason": str(e)}

def chat(user_input: str, model_size: str, history=None) -> str:
    try:
        messages = [{"role": "system", "content": CONVO_PROMPT}]
        if history:
            for role, message in history[-6:]:
                messages.append({
                    "role": "user" if role == "User" else "assistant",
                    "content": message
                })
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL_MAP[model_size],
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return "Sorry, I couldn't process that."

def parse_json(raw: str) -> dict:
    raw = re.sub(r"```json|```", "", raw).strip()
    candidates = re.findall(r'\{.*?\}', raw, re.DOTALL)
    if not candidates:
        return {"action": "unknown", "reason": "no JSON found"}
    for candidate in reversed(candidates):
        try:
            command = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if validate_command(command):
            return command
    return {"action": "unknown", "reason": "bad or invalid JSON"}

def validate_command(command: dict) -> bool:
    if not isinstance(command, dict):
        return False
    action = command.get("action")
    if not isinstance(action, str):
        return False
    if action == "unknown":
        return isinstance(command.get("reason"), str)
    if action in {"screenshot", "battery"}:
        return True
    if action == "open":
        return isinstance(command.get("target"), str) and bool(command.get("target"))
    if action == "close":
        return isinstance(command.get("target"), str) and bool(command.get("target"))
    if action == "search":
        engine = command.get("engine")
        query = command.get("query")
        return isinstance(engine, str) and engine in {"google", "youtube", "spotify", "github", "maps"} and isinstance(query, str) and bool(query)
    if action == "url":
        return isinstance(command.get("url"), str) and bool(command.get("url"))
    if action == "volume":
        value = command.get("value")
        return isinstance(value, str) and (value in {"up", "down", "mute", "unmute"} or value.isdigit())
    if action == "brightness":
        value = command.get("value")
        return isinstance(value, str) and (value in {"up", "down"} or value.isdigit())
    if action == "timer":
        return isinstance(command.get("seconds"), int) and command.get("seconds", 0) > 0
    if action == "media":
        return command.get("command") in {"next", "previous", "pause"}
    if action == "window":
        return command.get("command") == "minimize_all"
    if action == "system":
        return isinstance(command.get("command"), str) and bool(command.get("command"))
    if action == "open_folder":
        return isinstance(command.get("path"), str) and bool(command.get("path"))
    if action == "type":
        return isinstance(command.get("text"), str) and bool(command.get("text"))
    if action == "clipboard":
        return command.get("command") in {"copy", "paste", "clear"}
    return False