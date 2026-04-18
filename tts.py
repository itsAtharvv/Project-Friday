import asyncio
import threading
import tempfile
import os

import edge_tts
import sounddevice as sd
import soundfile as sf

VOICE = "en-GB-RyanNeural"

_tts_done = threading.Event()


def speak(text: str):
    """Non-blocking Edge TTS playback that signals when audio is finished."""
    _tts_done.clear()

    def _run():
        try:
            asyncio.run(_async_speak(text))
        except Exception as e:
            print(f"[TTS] Error: {e}")
        finally:
            _tts_done.set()

    threading.Thread(target=_run, daemon=True).start()


async def _async_speak(text: str):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(tmp_path)

        data, samplerate = sf.read(tmp_path)
        sd.play(data, samplerate)
        sd.wait()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def wait_until_done():
    """Block until TTS finishes speaking."""
    _tts_done.wait()