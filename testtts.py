import sounddevice as sd
from kokoro_onnx import Kokoro

k = Kokoro('kokoro-v1.0.onnx', 'voices-v1.0.bin')
samples, sr = k.create('Hello, I am Friday, your personal assistant.', voice='af_heart', speed=1.0, lang='en-us')
sd.play(samples, sr)
sd.wait()