import threading
from pathlib import Path

import sounddevice as sd
import soundfile as sf


BASE = Path(__file__).parent


def _play(filename: str):
    def _run():
        try:
            data, sr = sf.read(str(BASE / filename))
            sd.play(data, sr)
            sd.wait()
        except Exception as e:
            print(f"[Audio] {e}")

    threading.Thread(target=_run, daemon=True).start()


def play_listen():
    _play("listen.wav")


def play_done():
    _play("done.wav")


def play_error():
    _play("error.wav")


def play_processing():
    pass  # silence during processing