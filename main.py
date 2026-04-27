import threading
import time
from tts import speak, wait_until_done
from greeting import get_greeting
from audio import play_listen, play_done, play_error
from stt import listen
from parser import parse, parse_chain, clean_input
from normalizer import normalize
from router import route, is_conversation
from llm import call_llm
from executor import execute
from ui import signals, run_app

conversation_history = []
TRIGGER_LOCK = threading.Lock()
STOP_WORDS = [
    "stop", "bye", "goodbye", "close", "exit", "end",
    "that's all", "thats all", "dismiss", "enough", "shut up",
]


def is_stop(text: str) -> bool:
    return any(word in text.lower() for word in STOP_WORDS)


def show(state: str, text: str = "", delay: float = 0.05):
    """Thread-safe UI update."""
    signals.show_ui.emit(state)
    if text:
        signals.set_text.emit(text)
    time.sleep(delay)  # let Qt process the signal


def handle_command(text: str) -> bool:
    # check for chained commands first
    chain = parse_chain(text)
    if chain:
        show("processing", f"{len(chain)} commands queued...")
        speak(f"Running {len(chain)} commands.")
        wait_until_done()
        for i, command in enumerate(chain):
            print(f"[Chain] {i+1}/{len(chain)}: {command}")
            show("processing", f"Step {i+1} of {len(chain)}...")
            execute(command)
            time.sleep(0.8)
        play_done()
        show("done", "All done.")
        speak("All done.")
        wait_until_done()
        return True

    # single command pipeline
    cleaned = clean_input(text)
    command = parse(cleaned)

    if not command:
        normalized = normalize(text)
        if normalized.lower() != cleaned.lower():
            command = parse(normalized)

    if not command:
        if not is_conversation(text):
            show("processing", f'"{text}"')
            model_size = route(text)
            command = call_llm(text, model_size)

    if command and command.get("action") not in (None, "unknown"):
        show("processing", f'"{text}"')
        result = execute(command)
        play_done()
        if not (isinstance(result, dict) and result.get("spoken")):
            show("done", "Done.")
            speak("Done.")
        wait_until_done()
        return True

    return False


def conversation_loop(initial_text: str):
    global conversation_history
    text = initial_text

    while True:
        show("processing", f'"{text}"', delay=0.1)

        # Try the command pipeline first — handles "open firefox", volume, etc.
        # even mid-conversation
        if handle_command(text):
            print(f"[ConvLoop] Handled as command: {text}")
            # Stay in conversation: listen for what they say next
            play_listen()
            show("listening", "")
            next_text = listen()
            show("processing", f'"{next_text}"' if next_text else "", delay=0.1)
            if not next_text or is_stop(next_text):
                speak("Alright.")
                wait_until_done()
                play_done()
                signals.hide_ui.emit()
                conversation_history = []
                return
            text = next_text
            continue

        # Not a command — send to Groq for conversational response
        from groq import Groq
        import os
        from dotenv import load_dotenv
        load_dotenv()

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Friday, a witty helpful personal AI assistant. "
                    "Keep responses conversational and short - 2-3 sentences max "
                    "since they will be spoken aloud. Be natural, not robotic."
                ),
            }
        ]
        for role, msg in conversation_history[-8:]:
            messages.append({
                "role": "user" if role == "User" else "assistant",
                "content": msg,
            })
        messages.append({"role": "user", "content": text})

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # fastest model
                messages=messages,
                temperature=0.7,
                max_tokens=120,  # keep it short for voice
            )
            from llm import update_token_count
            update_token_count(response.usage)
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = "Sorry, I couldn't reach my brain right now."
            print(f"[Groq] Error: {e}")

        conversation_history.append(("User", text))
        conversation_history.append(("Friday", reply))

        print(f"[Friday] {reply}")
        show("speaking", reply)
        speak(reply)
        wait_until_done()

        # Listen for follow-up
        play_listen()
        show("listening", "")
        next_text = listen()
        show("processing", f'"{next_text}"' if next_text else "", delay=0.1)

        if not next_text or len(next_text.split()) < 1:
            speak("Still here.")
            wait_until_done()
            play_listen()
            show("listening", "")
            next_text = listen()
            show("processing", f'"{next_text}"' if next_text else "", delay=0.1)

        if not next_text or is_stop(next_text):
            speak("Alright.")
            wait_until_done()
            play_done()
            signals.hide_ui.emit()
            conversation_history = []
            return

        text = next_text


def process_command():
    global conversation_history

    show("listening", "")
    speak(get_greeting())
    wait_until_done()

    play_listen()
    text = listen()
    show("processing", f'"{text}"' if text else "", delay=0.1)

    if not text or len(text.split()) < 2:
        signals.show_ui.emit("error")
        signals.set_text.emit("Didn't catch that")
        speak("Didn't catch that.")
        play_error()
        signals.hide_ui.emit()
        return

    print(f"[Input] {text}")
    if is_stop(text):
        signals.hide_ui.emit()
        return

    # try command pipeline first regardless
    if handle_command(text):
        time.sleep(1.5)
        signals.hide_ui.emit()
        return

    # only go to conversation if it genuinely isn't a command
    if is_conversation(text):
        conversation_loop(text)
    else:
        # LLM couldn't handle it as command either — now try chat
        conversation_loop(text)


def _run_process_command_guarded():
    try:
        process_command()
    finally:
        TRIGGER_LOCK.release()


def trigger_activation():
    if not TRIGGER_LOCK.acquire(blocking=False):
        print("[Friday] Busy with an active session. Ignoring trigger.")
        return
    threading.Thread(target=_run_process_command_guarded, daemon=True).start()


def hotkey_listener():
    import asyncio
    from socket_listener import socket_listener
    print("[Friday] Running silently. Send to /tmp/friday.sock to activate.")
    asyncio.run(socket_listener(trigger_activation))


if __name__ == "__main__":
    # hotkey
    t1 = threading.Thread(target=hotkey_listener, daemon=True)
    t1.start()

    from wakeword import start_wakeword_thread
    start_wakeword_thread(trigger_activation)

    run_app()