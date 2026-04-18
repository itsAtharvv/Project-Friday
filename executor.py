import subprocess
import os
import json
import webbrowser
import threading
import time
import pyautogui
import psutil
from difflib import get_close_matches
from pathlib import Path
from urllib.parse import quote_plus
from parser import APP_ALIASES

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except Exception:
    BRIGHTNESS_AVAILABLE = False

VOLUME_AVAILABLE = True  # always True now, no dependencies
NIRCMD = r"C:\Users\Atharv\Documents\Projects\Project friday\nircmd.exe"

APP_MAP = {
    "explorer":   "explorer.exe",
    "notepad":    "notepad.exe",
    "calculator": "calc.exe",
    "cmd":        "cmd.exe",
    "terminal":   "wt",
    "taskmgr":    "taskmgr.exe",
}

START_MENU_PATHS = [
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs"),
]

INDEX_FILE = "app_index.json"

SEARCH_ENGINES = {
    "google":  "https://www.google.com/search?q=",
    "youtube": "https://www.youtube.com/results?search_query=",
    "github":  "https://github.com/search?q=",
    "maps":    "https://www.google.com/maps/search/",
    "spotify": "https://open.spotify.com/search/",
}


def build_index() -> dict:
    index = {}
    for base in START_MENU_PATHS:
        for lnk in base.rglob("*.lnk"):
            name = lnk.stem.lower().strip()
            index[name] = str(lnk)
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


def paste_text(text: str) -> bool:
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        pyautogui.hotkey("ctrl", "v")
        root.destroy()
        return True
    except Exception:
        return False


def set_volume(value: str):
    import os
    nircmd_exists = os.path.exists(NIRCMD)

    if value == "mute":
        if nircmd_exists:
            subprocess.Popen([NIRCMD, "mutesysvolume", "1"])
        else:
            pyautogui.press('volumemute')
        print("[Volume] Muted")

    elif value == "unmute":
        if nircmd_exists:
            subprocess.Popen([NIRCMD, "mutesysvolume", "0"])
        else:
            pyautogui.press('volumemute')
        print("[Volume] Unmuted")

    elif value == "up":
        if nircmd_exists:
            subprocess.Popen([NIRCMD, "changesysvolume", "6553"])
        else:
            for _ in range(5): pyautogui.press('volumeup')
        print("[Volume] Up")

    elif value == "down":
        if nircmd_exists:
            subprocess.Popen([NIRCMD, "changesysvolume", "-6553"])
        else:
            for _ in range(5): pyautogui.press('volumedown')
        print("[Volume] Down")

    elif value.isdigit():
        level = int(value)
        if nircmd_exists:
            nircmd_level = int((level / 100) * 65535)
            subprocess.Popen([NIRCMD, "setsysvolume", str(nircmd_level)])
        else:
            print("[Volume] Can't set exact level without nircmd")
        print(f"[Volume] Set to {level}%")


def timer_thread(seconds: int):
    print(f"[Timer] Started for {seconds} seconds")
    time.sleep(seconds)
    pyautogui.alert(f"Timer done! ({seconds}s)", title="Friday Timer")
    print("[Timer] Done")


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
                os.startfile(lnk)
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
            base_name = name_lower[:-4] if name_lower.endswith(".exe") else name_lower
            if target == name_lower or target == base_name:
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
            print(f"[Executor] Unknown search engine '{engine}', using google")
            engine = "google"
        query = quote_plus(command.get("query", ""))
        base = SEARCH_ENGINES.get(engine, SEARCH_ENGINES["google"])
        webbrowser.open(base + query)
        print(f"[Executor] Search {engine}: {query}")

    elif action == "url":
        webbrowser.open(command.get("url", ""))
        print(f"[Executor] URL: {command.get('url')}")

    elif action == "system":
        subprocess.Popen(command.get("command", ""), shell=True)
        print(f"[Executor] System: {command.get('command')}")

    elif action == "volume":
        set_volume(command.get("value", ""))

    elif action == "brightness":
        if not BRIGHTNESS_AVAILABLE:
            print("[Brightness] screen-brightness-control not available")
            return
        val = command.get("value", "")
        current = sbc.get_brightness()[0]
        if val == "up":
            sbc.set_brightness(min(100, current + 10))
        elif val == "down":
            sbc.set_brightness(max(0, current - 10))
        elif val.isdigit():
            sbc.set_brightness(int(val))
        print(f"[Executor] Brightness: {val}")

    elif action == "screenshot":
        path = str(Path.home() / "Desktop" / f"screenshot_{int(time.time())}.png")
        pyautogui.screenshot(path)
        print(f"[Executor] Screenshot saved: {path}")

    elif action == "timer":
        seconds = command.get("seconds", 0)
        t = threading.Thread(target=timer_thread, args=(seconds,), daemon=True)
        t.start()

    elif action == "open_folder":
        path = command.get("path", "")
        os.startfile(path)
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
        time.sleep(0.3)
        if not paste_text(text):
            pyautogui.typewrite(text, interval=0.05)
        print(f"[Executor] Typed: {text}")

    elif action == "switch":
        target = command.get("target", "")
        for proc in psutil.process_iter(["name", "pid"]):
            name = proc.info.get("name") or ""
            if target in name.lower():
                pyautogui.hotkey("alt", "tab")
                print("[Executor] Switched (alt+tab)")
                break

    elif action == "window":
        cmd = command.get("command", "")
        if cmd == "minimize_all":
            pyautogui.hotkey("win", "d")
            print("[Executor] Minimized all windows")

    elif action == "clipboard":
        cmd = command.get("command", "")
        if cmd == "copy":
            pyautogui.hotkey("ctrl", "c")
        elif cmd == "paste":
            pyautogui.hotkey("ctrl", "v")
        elif cmd == "clear":
            pyautogui.hotkey("win", "v")
        print(f"[Executor] Clipboard: {cmd}")

    elif action == "media":
        cmd = command.get("command", "")
        if cmd == "next":
            pyautogui.press("nexttrack")
        elif cmd == "previous":
            pyautogui.press("prevtrack")
        elif cmd == "pause":
            pyautogui.press("playpause")
        print(f"[Executor] Media: {cmd}")

    elif action == "battery":
        battery = psutil.sensors_battery()
        if battery:
            status = "charging" if battery.power_plugged else "discharging"
            print(f"[Battery] {battery.percent:.0f}% - {status}")
            pyautogui.alert(f"Battery: {battery.percent:.0f}% ({status})", title="Friday")
        else:
            print("[Battery] No battery found")

    elif action == "empty_recycle_bin":
        subprocess.Popen("PowerShell.exe -Command Clear-RecycleBin -Force", shell=True)
        print("[Executor] Recycle bin emptied")

    elif action == "ocr":
        from ocr import ocr_screen, describe_screen
        from tts import speak

        mode = command.get("mode", "read")
        signals_ui = None
        try:
            from ui import signals
            signals_ui = signals
        except Exception:
            pass

        print("[OCR] Taking screenshot and reading...")
        if signals_ui:
            signals_ui.show_ui.emit("processing")
            signals_ui.set_text.emit("Reading screen...")

        if mode == "describe":
            result = describe_screen()
        else:
            result = ocr_screen()

        print(f"[OCR] Result: {result}")
        speak(result)
        return {"spoken": True, "result": result}

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