import requests

def _looks_like_command(text: str) -> bool:
    text = text.strip().lower()
    return bool(text) and len(text.split()) <= 8

NORMALIZE_PROMPT = """Convert natural language into a short command. Be aggressive about simplification.
Output ONLY the simplified command. No explanation, no punctuation at the end.

increase volume → volume up
turn it up → volume up
make it louder → volume up
lower the volume → volume down
turn it down → volume down
make it quieter → volume down
mute it → volume mute
unmute → volume unmute
dim the screen → brightness down
make screen brighter → brightness up
hey friday open chrome for me → open chrome
can you please open discord → open discord
open my downloads folder → open downloads
take a picture of screen → screenshot
what's the battery → battery status
pause the music → pause
skip this song → next song
go back a song → previous song
minimize everything → minimize all windows
"""

def normalize(user_input: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma4:e2b",
                "prompt": f"{NORMALIZE_PROMPT}\n{user_input} →",
                "stream": False,
            },
            timeout=15
        )
        result = response.json().get("response", "").strip().strip('"').strip("'")
        if result and _looks_like_command(result):
            return result
        return user_input
    except:
        return user_input