import subprocess
from pathlib import Path

BASE = Path(__file__).parent

def _play(filename: str):
    try:
        # Popen runs asynchronously, no need for threading
        subprocess.Popen(["paplay", str(BASE / filename)])
    except FileNotFoundError:
        print("[Audio] paplay not found, please install pulseaudio/pipewire-pulse")
    except Exception as e:
        print(f"[Audio] {e}")

def play_listen():
    _play("listen.wav")

def play_done():
    _play("done.wav")

def play_error():
    _play("error.wav")

def play_processing():
    pass