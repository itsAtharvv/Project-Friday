import re

SIMPLE_PATTERNS = [
    r"^open\s+.+$",
    r"^(close|launch|start)\s+.+$",
    r"^(shutdown|restart|sleep|lock)$",
    r"^(volume|brightness)\s+(up|down|mute|unmute|\d+)$",
    r"^(screenshot|battery|show battery|battery status|empty recycle bin|minimize all|minimize all windows|copy|paste|clear clipboard)$",
    r"^(next|next song|previous song|previous song|pause|pause music|resume|skip|skip song|go back)$",
]

LARGE_TRIGGERS = [
    "search", "look up", "find", "play", "show me", "open website", "go to", "visit"
]

CONVO_TRIGGERS = [
    "what is", "what are", "how do", "how does", "why does", "why is",
    "who is", "who are", "when is", "when did", "where is", "where are",
    "explain", "tell me", "i don't know", "i dont know", "help me",
    "what should", "can you", "could you tell", "what do you think",
    "define", "describe", "give me", "suggest", "recommend",
    "how are you", "what's up", "how's it going", "talk to me",
    "i feel", "i am", "i'm", "do you", "are you", "will you",
    "can you help", "i need", "i want", "tell me about",
]

# these always go to command pipeline, never straight to chat
COMMAND_TRIGGERS = [
    "weather", "forecast", "temperature", "search", "find",
    "look up", "open", "close", "play", "volume", "brightness",
    "screenshot", "timer", "shutdown", "restart", "battery",
    "navigate", "go to", "show me", "pull up", "what time",
]

COMMAND_REGEX_TRIGGERS = [
    r"\bwea?the?r\b",      # weather / wheather
    r"\bweatehr\b",        # common transposition
    r"\btemp(?:erature)?\b",
    r"\btemprature\b",     # common misspelling
    r"\bforecast\b",
]

def route(user_input: str) -> str:
    text = user_input.strip().lower()

    # Direct search / browse intent usually needs the larger model if parsing failed.
    for trigger in LARGE_TRIGGERS:
        if trigger in text:
            return "large"

    # If it looks like a command we already know how to handle, prefer the small model.
    for pattern in SIMPLE_PATTERNS:
        if re.match(pattern, text):
            return "small"

    word_count = len(text.split())
    if word_count <= 6:
        return "small"

    return "large"


def is_conversation(user_input: str) -> bool:
    text = user_input.lower().strip()

    # command triggers override conversation
    for trigger in COMMAND_TRIGGERS:
        if trigger in text:
            return False

    for pattern in COMMAND_REGEX_TRIGGERS:
        if re.search(pattern, text):
            return False

    return any(trigger in text for trigger in CONVO_TRIGGERS)