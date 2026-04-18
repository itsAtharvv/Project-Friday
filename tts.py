import asyncio
import threading
import tempfile
import os

import edge_tts
import sounddevice as sd
import soundfile as sf

VOICE_PRESETS = {
    "uk_female": "en-GB-SoniaNeural",
    "uk_male": "en-GB-RyanNeural",
    "us_female": "en-US-AriaNeural",
    "us_male": "en-US-GuyNeural",
}
VOICE = VOICE_PRESETS["uk_female"]

_tts_done = threading.Event()


def available_voices() -> dict[str, str]:
    """Return supported voice presets."""
    return VOICE_PRESETS.copy()


def set_voice(preset: str) -> bool:
    """Set active TTS voice by preset key. Returns True if applied."""
    global VOICE
    key = (preset or "").strip().lower()
    voice = VOICE_PRESETS.get(key)
    if not voice:
        return False
    VOICE = voice
    return True


def get_voice() -> str:
    """Return the currently active voice ID."""
    return VOICE


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