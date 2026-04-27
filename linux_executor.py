import subprocess
import time
import os
from pathlib import Path
import json

def paste_text(text: str) -> bool:
    try:
        subprocess.run(["wtype", text], check=True)
        return True
    except subprocess.CalledProcessError:
        subprocess.run(["wl-copy", text])
        return False
    except FileNotFoundError:
        subprocess.run(["wl-copy", text])
        print("[Executor] wtype not found, copied to clipboard")
        return False

def set_volume(value: str):
    if value == "mute":
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])
    elif value == "unmute":
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])
    elif value == "up":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
    elif value == "down":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
    elif value.isdigit():
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])

def set_brightness(value: str):
    try:
        if value == "up":
            subprocess.run(["brightnessctl", "set", "10%+"])
        elif value == "down":
            subprocess.run(["brightnessctl", "set", "10%-"])
        elif value.isdigit():
            subprocess.run(["brightnessctl", "set", f"{value}%"])
    except FileNotFoundError:
        print("[Brightness] brightnessctl not installed")

def take_screenshot():
    subprocess.run('grim -g "$(slurp)" - | wl-copy', shell=True)

def lock_screen():
    subprocess.run(["hyprctl", "dispatch", "global", "caelestia:lock"])

def timer_notification(seconds: int):
    print(f"[Timer] Started for {seconds} seconds")
    time.sleep(seconds)
    subprocess.run(["notify-send", "Friday Timer", "Done!", "--urgency=critical"])
    print("[Timer] Done")

def clipboard_action(cmd: str):
    if cmd == "copy":
        subprocess.run(["wtype", "-M", "ctrl", "c", "-m", "ctrl"])
    elif cmd == "paste":
        subprocess.run(["wtype", "-M", "ctrl", "v", "-m", "ctrl"])
    elif cmd == "clear":
        subprocess.run(["wl-copy", "--clear"])

def empty_recycle_bin():
    trash_path = os.path.expanduser("~/.local/share/Trash")
    subprocess.run(f"rm -rf {trash_path}/files/* {trash_path}/info/*", shell=True)

def open_app_linux(lnk: str):
    # In Linux, desktop files are launched using gtk-launch or directly if executable
    if lnk.endswith(".desktop"):
        # gtk-launch expects just the filename without path or extension
        app_name = Path(lnk).stem
        subprocess.Popen(["gtk-launch", app_name])
    else:
        # Fallback to xdg-open
        subprocess.Popen(["xdg-open", lnk])

LINUX_APP_DIRS = [
    Path("/usr/share/applications"),
    Path(os.path.expanduser("~/.local/share/applications"))
]

def build_linux_index() -> dict:
    index = {}
    for base in LINUX_APP_DIRS:
        if not base.exists():
            continue
        for desk in base.rglob("*.desktop"):
            try:
                content = desk.read_text(errors="ignore")
                # Skip hidden or background entries
                if "NoDisplay=true" in content or "Hidden=true" in content:
                    continue
                # Extract Name= field
                name = None
                for line in content.splitlines():
                    if line.startswith("Name="):
                        name = line.split("=", 1)[1].strip().lower()
                        break
                if name:
                    index[name] = str(desk)
                # Also index by stem as fallback
                stem = desk.stem.lower().strip()
                if stem not in index:
                    index[stem] = str(desk)
                # Also index by last part after dot (e.g. org.mozilla.firefox -> firefox)
                short = stem.split(".")[-1]
                if short and short not in index:
                    index[short] = str(desk)
            except Exception:
                continue
    return index

def media_action(cmd: str):
    if cmd == "next":
        subprocess.run(["playerctl", "next"])
    elif cmd == "previous":
        subprocess.run(["playerctl", "previous"])
    elif cmd == "pause":
        subprocess.run(["playerctl", "play-pause"])

def switch_workspace(n: str):
    subprocess.run(["hyprctl", "dispatch", "workspace", n])

def move_to_workspace(n: str):
    subprocess.run(["hyprctl", "dispatch", "movetoworkspace", n])

def switch_window(target: str):
    subprocess.run(["hyprctl", "dispatch", "focuswindow", f"class:{target}"])

def minimize_all_windows():
    pass

def notify(title: str, body: str, urgency: str = "normal"):
    subprocess.run(["notify-send", title, body, f"--urgency={urgency}"])

def paste_code_to_editor(code: str):
    # TODO: Replace wtype with editor extension socket integration
    try:
        # Give user time to click into editor window
        time.sleep(1.5)
        subprocess.run(["wtype", "--delay", "5", code], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["wl-copy", code])
        return "fallback"
    except FileNotFoundError:
        subprocess.run(["wl-copy", code])
        return "fallback"
    return "ok"

