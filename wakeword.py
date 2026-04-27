import threading
import traceback
import sounddevice as sd
import numpy as np


def _find_best_mic_device():
    """
    Prefer a hardware input device whose native sample rate is 16000 Hz
    (ideal for openwakeword). Falls back to the system default if none found.
    The default PipeWire/PulseAudio device resamples from 44100 Hz, which
    degrades wakeword detection scores significantly.
    """
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d["max_input_channels"] > 0 and int(d["default_samplerate"]) == 16000:
            print(f"[WakeWord] Found native 16kHz mic: [{i}] {d['name']}")
            return i
    # fallback
    default_idx = sd.default.device[0]
    print(f"[WakeWord] No native 16kHz mic found, using default device [{default_idx}]")
    return default_idx


def start_wakeword_thread(trigger_callback):
    try:
        import openwakeword
        from openwakeword.model import Model
    except ImportError:
        print("[WakeWord] openwakeword not installed. Wake word disabled.")
        return

    def _run():
        try:
            print("[WakeWord] Loading model hey_jarvis_v0.1...")
            paths = openwakeword.get_pretrained_model_paths()
            jarvis_path = [p for p in paths if "hey_jarvis" in p]
            if not jarvis_path:
                print("[WakeWord] ERROR: No hey_jarvis model found in pretrained paths!")
                return
            print(f"[WakeWord] Using model: {jarvis_path[0]}")
            owwModel = Model(wakeword_model_paths=jarvis_path)

            mic_device = _find_best_mic_device()
            print(f"[WakeWord] Listening for wake word on device [{mic_device}]...")

            with sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype="int16",
                blocksize=1280,
                device=mic_device,
            ) as mic_stream:
                while True:
                    audio, overflowed = mic_stream.read(1280)
                    if overflowed:
                        print("[WakeWord] WARNING: audio buffer overflow")

                    # sounddevice returns shape (frames, channels) — extract mono channel
                    chunk = audio[:, 0] if audio.ndim == 2 else audio.flatten()

                    prediction = owwModel.predict(chunk)

                    # Use max over all model scores — works regardless of key name
                    score = float(max(prediction.values())) if prediction else 0.0

                    if score > 0.5:
                        print(f"[WakeWord] Wake word detected! (score: {score:.2f})")
                        trigger_callback()
                        # Cooldown to avoid rapid re-trigger
                        sd.sleep(2000)

        except Exception as e:
            print(f"[WakeWord] FATAL ERROR in wakeword thread: {e}")
            traceback.print_exc()

    threading.Thread(target=_run, daemon=True).start()

