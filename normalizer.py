import re


FILLERS = [
    "hey friday",
    "friday",
    "can you",
    "could you",
    "would you",
    "please",
    "for me",
    "just",
]

PHRASE_REWRITES = [
    (r"\b(turn|increase|raise) (the )?volume (up)?\b", "volume up"),
    (r"\b(make it|make the sound) louder\b", "volume up"),
    (r"\b(turn|decrease|lower) (the )?volume (down)?\b", "volume down"),
    (r"\b(make it|make the sound) quieter\b", "volume down"),
    (r"\bmute( it)?\b", "mute"),
    (r"\bunmute( it)?\b", "unmute"),
    (r"\bdim (the )?screen\b", "brightness down"),
    (r"\b(make|set) (the )?screen brighter\b", "brightness up"),
    (r"\btake (a )?(picture|photo) of (the )?screen\b", "screenshot"),
    (r"\bwhat('?s| is) (the )?battery\b", "battery status"),
    (r"\bpause (the )?music\b", "pause"),
    (r"\bskip (this )?(song|track)\b", "next song"),
    (r"\bgo back (a )?(song|track)\b", "previous song"),
    (r"\bminimize everything\b", "minimize all windows"),
    (r"\bopen my (downloads|documents|desktop|pictures|music|videos)( folder)?\b", r"open \1"),
]


def _strip_fillers(text: str) -> str:
    result = text.lower().strip()
    for filler in FILLERS:
        result = re.sub(rf"\b{re.escape(filler)}\b", " ", result)
    return " ".join(result.split())


def normalize(user_input: str) -> str:
    cleaned = _strip_fillers(user_input)
    if not cleaned:
        return user_input

    for pattern, replacement in PHRASE_REWRITES:
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            normalized = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            normalized = " ".join(normalized.split())
            if normalized:
                return normalized

    return cleaned