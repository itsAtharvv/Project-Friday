import base64
import os
import tempfile

import pyautogui
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def ocr_screen(prompt: str = "Read and extract all text visible in this image. Output only the text, nothing else.") -> str:
    try:
        shot = pyautogui.screenshot()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            shot.save(f.name)
            tmp = f.name

        with open(tmp, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        os.remove(tmp)

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "gemma4:e4b",
                "prompt": prompt,
                "images": [img_b64],
                "stream": False,
                "keep_alive": 0,
            },
            timeout=60,
        )
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "Ollama is not running."
    except Exception as e:
        return f"OCR failed: {e}"


def describe_screen() -> str:
    return ocr_screen("Describe what you see on this screen in 2-3 sentences.")


def answer_from_screen(question: str) -> str:
    return ocr_screen(f"Look at this screen and answer: {question}")
