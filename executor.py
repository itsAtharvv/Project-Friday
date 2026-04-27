import subprocess
import os
import json
import webbrowser
import threading
import time
import psutil
from difflib import get_close_matches
from pathlib import Path
from urllib.parse import quote_plus
from parser import APP_ALIASES
import linux_executor

VOLUME_AVAILABLE = True
BRIGHTNESS_AVAILABLE = True

APP_MAP = {
    "terminal":   "foot",
    "explorer":   "nautilus", 
    "browser":    "firefox",
}

INDEX_FILE = "app_index.json"

SEARCH_ENGINES = {
    "google":  "https://www.google.com/search?q=",
    "youtube": "https://www.youtube.com/results?search_query=",
    "github":  "https://github.com/search?q=",
    "maps":    "https://www.google.com/maps/search/",
    "spotify": "https://open.spotify.com/search/",
}

def build_index() -> dict:
    index = linux_executor.build_linux_index()
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    print(f"[Index] Built with {len(index)} apps")
    return index

def load_index() -> dict:
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            return json.load(f)
    return build_index()

def fuzzy_match(target: str, index: dict) -> str | None:
    target = target.lower().strip()
    if target in index:
        return index[target]

    close_match = get_close_matches(target, list(index.keys()), n=1, cutoff=0.8)
    if close_match:
        best = close_match[0]
        print(f"[Fuzzy] '{target}' -> '{best}'")
        return index[best]

    matches = [key for key in index if target in key]
    if matches:
        best = min(matches, key=len)
        print(f"[Fuzzy] '{target}' -> '{best}'")
        return index[best]
    matches = [key for key in index if key in target]
    if matches:
        best = max(matches, key=len)
        print(f"[Fuzzy] '{target}' -> '{best}'")
        return index[best]
    target_words = set(target.split())
    scored = []
    for key in index:
        common = target_words & set(key.split())
        if common:
            scored.append((len(common), key))
    if scored:
        best = max(scored)[1]
        print(f"[Fuzzy] '{target}' -> '{best}'")
        return index[best]
    return None

def resolve_alias(target: str) -> str:
    target = target.lower().strip()
    if target in APP_ALIASES:
        return APP_ALIASES[target]
    close_match = get_close_matches(target, list(APP_ALIASES.keys()), n=1, cutoff=0.8)
    if close_match:
        return APP_ALIASES[close_match[0]]
    return target

def execute(command: dict):
    action = command.get("action")

    if action == "open":
        target = command.get("target", "").lower().strip()
        if target in APP_MAP:
            subprocess.Popen(APP_MAP[target], shell=True)
            print(f"[Executor] Opened (map): {target}")
            return
        index = load_index()
        lnk = fuzzy_match(target, index)
        if lnk:
            try:
                linux_executor.open_app_linux(lnk)
                print(f"[Executor] Opened: {lnk}")
            except Exception as e:
                print(f"[Executor] Failed: {e}")
        else:
            print(f"[Executor] Not found: '{target}'")

    elif action == "close":
        target = command.get("target", "").lower()
        closed = False
        processes = []
        for proc in psutil.process_iter(["name", "pid"]):
            name = proc.info.get("name") or ""
            name_lower = name.lower()
            processes.append((name_lower, proc))
            if target == name_lower:
                proc.kill()
                print(f"[Executor] Closed: {name}")
                closed = True
                break
        if not closed:
            substring_matches = [item for item in processes if target in item[0] or item[0] in target]
            if substring_matches:
                name_lower, proc = min(substring_matches, key=lambda item: len(item[0]))
                proc.kill()
                print(f"[Executor] Closed: {proc.info.get('name')}")
                closed = True
        if not closed:
            close_match = get_close_matches(target, [name for name, _ in processes], n=1, cutoff=0.8)
            if close_match:
                for name_lower, proc in processes:
                    if name_lower == close_match[0]:
                        proc.kill()
                        print(f"[Executor] Closed: {proc.info.get('name')}")
                        closed = True
                        break
        if not closed:
            print(f"[Executor] Process not found: '{target}'")

    elif action == "search":
        engine = command.get("engine", "google").lower()
        if engine not in SEARCH_ENGINES:
            engine = "google"
        query = quote_plus(command.get("query", ""))
        base = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["google"])
        webbrowser.open(base + query)
        print(f"[Executor] Search {engine}: {query}")

    elif action == "url":
        webbrowser.open(command.get("url", ""))
        print(f"[Executor] URL: {command.get('url')}")

    elif action == "system":
        cmd = command.get("command", "")
        # Replace Windows commands with Linux
        if cmd == "shutdown /s /t 0":
            cmd = "systemctl poweroff"
        elif cmd == "shutdown /r /t 0":
            cmd = "systemctl reboot"
        elif "rundll32" in cmd and "LockWorkStation" in cmd:
            linux_executor.lock_screen()
            print("[Executor] Screen locked")
            return
        elif "rundll32" in cmd and "SetSuspendState" in cmd:
            cmd = "systemctl suspend"
            
        subprocess.Popen(cmd, shell=True)
        print(f"[Executor] System: {cmd}")
        
    elif action == "silent_mode":
        from tts import set_silent_mode
        set_silent_mode(True)
        print("[Executor] Silent mode ON")

    elif action == "volume":
        if command.get("value") == "unmute":
            from tts import set_silent_mode
            set_silent_mode(False)
            print("[Executor] Silent mode OFF")
        linux_executor.set_volume(command.get("value", ""))

    elif action == "brightness":
        linux_executor.set_brightness(command.get("value", ""))

    elif action == "screenshot":
        linux_executor.take_screenshot()

    elif action == "timer":
        seconds = command.get("seconds", 0)
        t = threading.Thread(target=linux_executor.timer_notification, args=(seconds,), daemon=True)
        t.start()

    elif action == "open_folder":
        path = command.get("path", "")
        subprocess.Popen(["xdg-open", path])
        print(f"[Executor] Opened folder: {path}")

    elif action == "create_folder":
        name = command.get("name", "new folder")
        parent = command.get("path")
        base_path = Path(parent) if parent else Path.home()
        path = base_path / name
        path.mkdir(parents=True, exist_ok=True)
        print(f"[Executor] Created folder: {path}")

    elif action == "type":
        text = command.get("text", "")
        time.sleep(1.5)
        linux_executor.paste_text(text)
        print(f"[Executor] Typed: {text}")

    elif action == "workspace":
        linux_executor.switch_workspace(command.get("workspace", "1"))
        
    elif action == "move_workspace":
        linux_executor.move_to_workspace(command.get("workspace", "1"))

    elif action == "switch":
        target = command.get("target", "")
        linux_executor.switch_window(target)

    elif action == "window":
        cmd = command.get("command", "")
        if cmd == "minimize_all":
            linux_executor.minimize_all_windows()

    elif action == "clipboard":
        cmd = command.get("command", "")
        linux_executor.clipboard_action(cmd)

    elif action == "media":
        cmd = command.get("command", "")
        linux_executor.media_action(cmd)

    elif action == "battery":
        battery = psutil.sensors_battery()
        if battery:
            status = "charging" if battery.power_plugged else "discharging"
            print(f"[Battery] {battery.percent:.0f}% - {status}")
            subprocess.run(["notify-send", "Friday", f"Battery: {battery.percent:.0f}% ({status})"])
        else:
            print("[Battery] No battery found")

    elif action == "empty_recycle_bin":
        linux_executor.empty_recycle_bin()
        print("[Executor] Recycle bin emptied")
        
    elif action == "token_status":
        from llm import get_token_status
        from tts import speak
        used = get_token_status()
        speak(f"Used {used} tokens this minute out of 6000.")

    elif action == "coding_request":
        from llm import generate_code
        from tts import speak
        from audio import play_error, play_done
        
        query = command.get("query")
        code = generate_code(query)
        if not code:
            speak("Got an empty response.")
            play_error()
            return {"spoken": True, "result": "Empty response"}
            
        if code == "RATE_LIMIT":
            speak("Rate limit hit, try again in a moment.")
            play_error()
            return {"spoken": True, "result": "Rate limit"}
            
        speak("Ready to paste. Switching focus in 3 seconds.")
        time.sleep(3)
        if len(code) > 3000:
            speak("Large response incoming, pasting now.")
        else:
            speak("Pasting now.")
        res = linux_executor.paste_code_to_editor(code)
        play_done()
        if res == "fallback":
            speak("Couldn't paste, copied to clipboard instead.")
        return {"spoken": True, "result": "Paste sequence complete"}

    elif action == "tts_voice":
        from tts import set_voice, speak
        preset = command.get("preset", "")
        labels = {
            "uk_female": "British female",
            "uk_male": "British male",
            "us_female": "American female",
            "us_male": "American male",
        }
        if set_voice(preset):
            label = labels.get(preset, preset.replace("_", " "))
            message = f"Voice changed to {label}."
        else:
            message = "I could not find that voice. Say available voices to hear options."
        print(f"[TTS] {message}")
        speak(message)
        return {"spoken": True, "result": message}

    elif action == "tts_voice_list":
        from tts import available_voices, speak
        voices = ", ".join(sorted(available_voices().keys()))
        message = f"Available voices are: {voices}."
        print(f"[TTS] {message}")
        speak(message)
        return {"spoken": True, "result": message}

    elif action == "task":
        task = command.get("task")
        if task == "create_project":
            from tasks import create_project
            project_type = command.get("type", "python")
            threading.Thread(
                target=create_project,
                args=(project_type,),
                daemon=True
            ).start()
        elif task == "push_to_github":
            from tasks import push_to_github
            threading.Thread(
                target=push_to_github,
                daemon=True
            ).start()

    elif action == "unknown":
        print(f"[Executor] Can't handle: {command.get('reason')}")

if __name__ == "__main__":
    import sys
    if "--reindex" in sys.argv:
        build_index()