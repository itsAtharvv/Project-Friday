import re
from difflib import get_close_matches
from urllib.parse import quote_plus

FILLER_WORDS = [
    "can you", "could you", "would you", "please", "hey friday",
    "friday", "i want to", "i need to", "for me", "just", "my", "the"
]

CODING_ACTIONS = ["write", "code", "create", "generate"]
CODING_KEYWORDS = ["python", "javascript", "js", "html", "css", "bash", "script", "function", "class", "program", "algorithm", "api", "server", "bot", "app", "tool", "calculator", "converter", "parser", "scraper"]

def is_coding_request(text: str) -> bool:
    lower = text.lower()
    has_action = any(re.search(rf"\b{w}\b", lower) for w in CODING_ACTIONS)
    has_keyword = any(re.search(rf"\b{w}\b", lower) for w in CODING_KEYWORDS)
    return has_action and has_keyword

CHAIN_SEPARATORS = [
    " and then ", " then ", ", then ",
    " after that ", ", after that ",
    " and also ", " also ",
    " and ",
]

def clean_input(text: str) -> str:
    text = text.lower().strip().rstrip(".,!?")
    filler_pattern = r"\b(?:" + "|".join(re.escape(word) for word in sorted(FILLER_WORDS, key=len, reverse=True)) + r")\b"
    text = re.sub(filler_pattern, " ", text, flags=re.IGNORECASE)
    return " ".join(text.split())


def split_chain(text: str) -> list[str]:
    lower = text.lower().strip()
    for sep in CHAIN_SEPARATORS:
        if sep in lower:
            parts = lower.split(sep)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) > 1:
                return parts
    return [text]


def parse_chain(user_input: str) -> list[dict] | None:
    parts = split_chain(user_input)
    if len(parts) == 1:
        return None

    commands = []
    for part in parts:
        cmd = parse(clean_input(part))
        if not cmd:
            return None
        commands.append(cmd)

    return commands if len(commands) > 1 else None

SEARCH_ENGINES = {
    "google":   "https://www.google.com/search?q=",
    "youtube":  "https://www.youtube.com/results?search_query=",
    "github":   "https://github.com/search?q=",
    "maps":     "https://www.google.com/maps/search/",
    "spotify":  "https://open.spotify.com/search/",
}

WEBSITE_SHORTCUTS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "spotify": "https://open.spotify.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
}

SEARCH_ENGINE_ALIASES = {
    "yt": "youtube",
    "tube": "youtube",
    "git": "github",
    "gmaps": "maps",
    "map": "maps",
}

WEATHER_TERMS = [
    "weather", "forecast", "temperature", "temp", "temprature", "weatehr", "whether"
]

WEATHER_FIXES = {
    "weatehr": "weather",
    "temprature": "temperature",
    "wheather": "weather",
    "whether": "weather",
}

APP_ALIASES = {
    "chrome":        "google chrome",
    "vscode":        "visual studio code",
    "vs code":       "visual studio code",
    "explorer":      "file explorer",
    "premiere":      "adobe premiere pro 2026",
    "photoshop":     "adobe photoshop 2026",
    "after effects": "adobe after effects 2025",
    "resolve":       "davinci resolve",
    "obs":           "obs studio",
    "powershell":    "windows powershell",
    "torrent":       "qbittorrent",
}

OPEN_PATTERN       = re.compile(r"^(open|launch|start)\s+(.+)$", re.IGNORECASE)
CLOSE_PATTERN      = re.compile(r"^(close|kill|quit|exit)\s+(.+)$", re.IGNORECASE)
SEARCH_FOR_PATTERN = re.compile(r"^search\s+(.+?)\s+for\s+(.+)$", re.IGNORECASE)
SEARCH_ON_PATTERN  = re.compile(r"^search\s+(.+?)\s+on\s+(.+)$", re.IGNORECASE)
SEARCH_BARE_PATTERN = re.compile(r"^search\s+(.+)$", re.IGNORECASE)
PLAY_PATTERN       = re.compile(r"^play\s+(.+?)(?:\s+on\s+(.+))?$", re.IGNORECASE)
URL_PATTERN        = re.compile(r"^(visit|go to|open website|open site)\s+(.+)$", re.IGNORECASE)
VOLUME_PATTERN     = re.compile(r"^volume\s+(up|down|mute|unmute|\d+)$", re.IGNORECASE)
BRIGHTNESS_PATTERN = re.compile(r"^brightness\s+(up|down|\d+)$", re.IGNORECASE)
TIMER_PATTERNS     = [
    re.compile(r"^set\s+(?:a\s+)?timer\s+for\s+(\d+)\s*(seconds?|minutes?|hours?)$", re.IGNORECASE),
    re.compile(r"^set\s+(?:a\s+)?(\d+)\s*(seconds?|minutes?|hours?)\s+timer$", re.IGNORECASE),
    re.compile(r"^(?:a\s+)?(\d+)\s*(seconds?|minutes?|hours?)\s+timer$", re.IGNORECASE),
    re.compile(r"^timer\s+for\s+(\d+)\s*(seconds?|minutes?|hours?)$", re.IGNORECASE),
    re.compile(r"^remind me in\s+(\d+)\s*(seconds?|minutes?|hours?)$", re.IGNORECASE),
]
FOLDER_PATTERN     = re.compile(r"^open\s+(downloads|documents|desktop|pictures|music|videos)\s*(?:folder)?$", re.IGNORECASE)
TYPE_PATTERN       = re.compile(r"^type\s+(.+)$", re.IGNORECASE)
WORKSPACE_PATTERN  = re.compile(r"^(?:switch|go)\s+to\s+workspace\s+(\d+)$", re.IGNORECASE)
MOVE_WORKSPACE_PATTERN = re.compile(r"^move\s+(?:window\s+|this\s+|it\s+)?to\s+workspace\s+(\d+)$", re.IGNORECASE)
SWITCH_PATTERN     = re.compile(r"^(?:focus|switch\s+to)\s+(.+)$", re.IGNORECASE)
NEW_FOLDER_PATTERN = re.compile(r"^create\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called\s+|named\s+)?(.+?)(?:\s+(?:in|on|under)\s+(downloads|documents|desktop|pictures|music|videos))?$", re.IGNORECASE)
NEW_FOLDER_IN_PATTERN = re.compile(r"^create\s+(?:a\s+)?(?:new\s+)?folder\s+(?:in|on|under)\s+(downloads|documents|desktop|pictures|music|videos)\s+(?:called\s+|named\s+)?(.+)$", re.IGNORECASE)
CREATE_PROJECT_PATTERN = re.compile(
    r"^(?:create|make|new|start)\s+(?:a\s+)?(\w+)\s+project$", re.IGNORECASE
)
SET_VOICE_PATTERN = re.compile(
    r"^(?:change|set|switch)(?:\s+my)?\s+voice(?:\s+to)?\s*(.*)$", re.IGNORECASE
)
USE_VOICE_PATTERN = re.compile(
    r"^(?:use|make it|make)\s+(.+?)\s+voice$", re.IGNORECASE
)

VOICE_PRESET_ALIASES = {
    "uk female": "uk_female",
    "british female": "uk_female",
    "female british": "uk_female",
    "sonia": "uk_female",
    "sonia neural": "uk_female",
    "uk male": "uk_male",
    "british male": "uk_male",
    "male british": "uk_male",
    "ryan": "uk_male",
    "ryan neural": "uk_male",
    "us female": "us_female",
    "american female": "us_female",
    "aria": "us_female",
    "aria neural": "us_female",
    "us male": "us_male",
    "american male": "us_male",
    "guy": "us_male",
    "guy neural": "us_male",
}

SYSTEM_COMMANDS = {
    "shutdown":             {"action": "system", "command": "shutdown /s /t 0"},
    "restart":              {"action": "system", "command": "shutdown /r /t 0"},
    "sleep":                {"action": "system", "command": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"},
    "lock":                 {"action": "system", "command": "rundll32.exe user32.dll,LockWorkStation"},
    "lock screen":          {"action": "system", "command": "rundll32.exe user32.dll,LockWorkStation"},
    "turn off":             {"action": "system", "command": "shutdown /s /t 0"},
    "turn off computer":    {"action": "system", "command": "shutdown /s /t 0"},
    "restart computer":     {"action": "system", "command": "shutdown /r /t 0"},
    "take a screenshot":    {"action": "screenshot"},
    "take screenshot":      {"action": "screenshot"},
    "screenshot":           {"action": "screenshot"},
    "take a pic":           {"action": "screenshot"},
    "take a photo":         {"action": "screenshot"},
    "turn volume up":       {"action": "volume", "value": "up"},
    "turn volume down":     {"action": "volume", "value": "down"},
    "increase volume":      {"action": "volume", "value": "up"},
    "decrease volume":      {"action": "volume", "value": "down"},
    "lower volume":         {"action": "volume", "value": "down"},
    "raise volume":         {"action": "volume", "value": "up"},
    "mute":                 {"action": "volume", "value": "mute"},
    "unmute":               {"action": "volume", "value": "unmute"},
    "silent mode":          {"action": "silent_mode", "value": "on"},
    "turn brightness up":   {"action": "brightness", "value": "up"},
    "turn brightness down": {"action": "brightness", "value": "down"},
    "dim screen":           {"action": "brightness", "value": "down"},
    "increase brightness":  {"action": "brightness", "value": "up"},
    "decrease brightness":  {"action": "brightness", "value": "down"},
    "lower brightness":     {"action": "brightness", "value": "down"},
    "raise brightness":     {"action": "brightness", "value": "up"},
    "skip":                 {"action": "media", "command": "next"},
    "skip song":            {"action": "media", "command": "next"},
    "next":                 {"action": "media", "command": "next"},
    "next song":            {"action": "media", "command": "next"},
    "previous song":        {"action": "media", "command": "previous"},
    "go back":              {"action": "media", "command": "previous"},
    "pause":                {"action": "media", "command": "pause"},
    "pause music":          {"action": "media", "command": "pause"},
    "pause spotify":        {"action": "media", "command": "pause"},
    "resume":               {"action": "media", "command": "pause"},
    "empty recycle bin":    {"action": "empty_recycle_bin"},
    "show battery":         {"action": "battery"},
    "battery status":       {"action": "battery"},
    "battery":              {"action": "battery"},
    "battery level":        {"action": "battery"},
    "minimize all":         {"action": "window", "command": "minimize_all"},
    "minimize all windows": {"action": "window", "command": "minimize_all"},
    "hide windows":         {"action": "window", "command": "minimize_all"},
    "copy":                 {"action": "clipboard", "command": "copy"},
    "copy selection":       {"action": "clipboard", "command": "copy"},
    "paste":                {"action": "clipboard", "command": "paste"},
    "paste clipboard":      {"action": "clipboard", "command": "paste"},
    "clear clipboard":      {"action": "clipboard", "command": "clear"},
    "token status":         {"action": "token_status"},
    "how many tokens":      {"action": "token_status"},
    "new python project":   {"action": "task", "task": "create_project", "type": "python"},
    "create python project":{"action": "task", "task": "create_project", "type": "python"},
    "new web project":      {"action": "task", "task": "create_project", "type": "web"},
    "create web project":   {"action": "task", "task": "create_project", "type": "web"},
    "new node project":     {"action": "task", "task": "create_project", "type": "node"},
    "create node project":  {"action": "task", "task": "create_project", "type": "node"},
    "new project":          {"action": "task", "task": "create_project", "type": "python"},
    "create project":       {"action": "task", "task": "create_project", "type": "python"},
    "push to github":       {"action": "task", "task": "push_to_github"},
    "push to git":          {"action": "task", "task": "push_to_github"},
    "push project":         {"action": "task", "task": "push_to_github"},
    "git push":             {"action": "task", "task": "push_to_github"},
    "push my project":      {"action": "task", "task": "push_to_github"},
    "upload to github":     {"action": "task", "task": "push_to_github"},
    "list voices":          {"action": "tts_voice_list"},
    "available voices":     {"action": "tts_voice_list"},
    "voice options":        {"action": "tts_voice_list"},
}

FOLDER_PATHS = {
    "downloads":  str(__import__('pathlib').Path.home() / "Downloads"),
    "documents":  str(__import__('pathlib').Path.home() / "Documents"),
    "desktop":    str(__import__('pathlib').Path.home() / "Desktop"),
    "pictures":   str(__import__('pathlib').Path.home() / "Pictures"),
    "music":      str(__import__('pathlib').Path.home() / "Music"),
    "videos":     str(__import__('pathlib').Path.home() / "Videos"),
}

FOLDER_ALIASES = {
    "video":     "videos",
    "vid":       "videos",
    "download":  "downloads",
    "doc":       "documents",
    "document":  "documents",
    "pic":       "pictures",
    "picture":   "pictures",
    "photo":     "pictures",
    "photos":    "pictures",
    "image":     "pictures",
    "images":    "pictures",
    "desk":      "desktop",
}

FOLDER_KEYWORDS = ["downloads", "documents", "desktop", "pictures", "music", "videos"]
FOLDER_INTENT_PATTERN = re.compile(r"^(open|go to|visit|show|browse)\b", re.IGNORECASE)


def resolve_search_engine(raw_engine: str) -> str:
    engine = raw_engine.lower().strip()
    engine = SEARCH_ENGINE_ALIASES.get(engine, engine)
    for key in SEARCH_ENGINES:
        if key in engine:
            return key
    match = get_close_matches(engine, SEARCH_ENGINES.keys(), n=1, cutoff=0.75)
    return match[0] if match else "google"


def resolve_system_command(lower: str) -> dict | None:
    if lower in SYSTEM_COMMANDS:
        return SYSTEM_COMMANDS[lower]

    match = get_close_matches(lower, SYSTEM_COMMANDS.keys(), n=1, cutoff=0.88)
    if match:
        return SYSTEM_COMMANDS[match[0]]
    return None


def normalize_folder_name(word: str) -> str | None:
    if word in FOLDER_KEYWORDS:
        return word

    match = get_close_matches(word, FOLDER_KEYWORDS, n=1, cutoff=0.8)
    return match[0] if match else None


def looks_like_url(text: str) -> bool:
    text = text.strip().lower()
    return bool(
        re.match(r"^(https?://|www\.)\S+$", text)
        or re.search(r"\b[\w-]+\.(com|net|org|io|co|edu|gov|dev|app|ai|me|us|uk)\b", text)
    )


def normalize_url(text: str) -> str:
    url = text.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "https://" + url.lstrip("/")


def extract_folder(text: str) -> dict | None:
    """Check if text is asking to open a known folder."""
    text = text.lower().strip()

    for alias, real in FOLDER_ALIASES.items():
        text = re.sub(rf'\b{re.escape(alias)}\b', real, text)

    for word in re.findall(r"[a-z]+", text):
        folder = normalize_folder_name(word)
        if folder:
            return {"action": "open_folder", "path": FOLDER_PATHS[folder]}

    return None


def resolve_website_shortcut(target: str) -> str | None:
    target = target.lower().strip()
    target = re.sub(r"^(the\s+)?(website|site|page)\s+of\s+", "", target)
    target = re.sub(r"\s+(website|site|page)$", "", target)

    if target in WEBSITE_SHORTCUTS:
        return WEBSITE_SHORTCUTS[target]

    match = get_close_matches(target, list(WEBSITE_SHORTCUTS.keys()), n=1, cutoff=0.85)
    if match:
        return WEBSITE_SHORTCUTS[match[0]]

    return None

def resolve_alias(target: str) -> str:
    return APP_ALIASES.get(target.lower().strip(), target.lower().strip())


def normalize_weather_text(text: str) -> str:
    normalized = text
    for wrong, right in WEATHER_FIXES.items():
        normalized = re.sub(rf"\b{re.escape(wrong)}\b", right, normalized, flags=re.IGNORECASE)
    return " ".join(normalized.split())


def resolve_voice_preset(raw_voice: str) -> str | None:
    voice_text = re.sub(r"[^a-z0-9\s]", " ", (raw_voice or "").lower())
    voice_text = " ".join(voice_text.split())

    for suffix in (" voice", " one"):
        if voice_text.endswith(suffix):
            voice_text = voice_text[: -len(suffix)].strip()

    if voice_text in VOICE_PRESET_ALIASES:
        return VOICE_PRESET_ALIASES[voice_text]

    match = get_close_matches(voice_text, VOICE_PRESET_ALIASES.keys(), n=1, cutoff=0.78)
    if match:
        return VOICE_PRESET_ALIASES[match[0]]

    return None


def is_weather_request(text: str) -> bool:
    words = re.findall(r"[a-z]+", text.lower())
    for word in words:
        if word in WEATHER_TERMS:
            return True
        close = get_close_matches(word, WEATHER_TERMS, n=1, cutoff=0.82)
        if close:
            return True
    return False

def parse(user_input: str) -> dict | None:
    text = user_input.strip().rstrip(".,!?")
    cleaned = clean_input(text)
    lower = cleaned.lower()

    if is_coding_request(cleaned):
        return {"action": "coding_request", "query": user_input}

    # System / one-word commands
    system_command = resolve_system_command(lower)
    if system_command:
        return system_command

    # Voice selection commands
    m = SET_VOICE_PATTERN.match(cleaned)
    if m:
        raw_voice = m.group(1).strip()
        if not raw_voice:
            return {"action": "tts_voice_list"}
        preset = resolve_voice_preset(raw_voice)
        if preset:
            return {"action": "tts_voice", "preset": preset}
        return {"action": "tts_voice_list"}

    m = USE_VOICE_PATTERN.match(cleaned)
    if m:
        preset = resolve_voice_preset(m.group(1).strip())
        if preset:
            return {"action": "tts_voice", "preset": preset}
        return {"action": "tts_voice_list"}

    # folder check early — only for commands that actually sound like folder requests
    if FOLDER_INTENT_PATTERN.match(lower) and any(word in lower for word in ["folder", "directory"] + FOLDER_KEYWORDS):
        result = extract_folder(cleaned)
        if result:
            return result

    # Weather intent (including misspellings like "weatehr" / "temprature")
    if is_weather_request(cleaned):
        weather_query = normalize_weather_text(cleaned)
        if weather_query in {"weather", "forecast", "temperature", "temp"}:
            weather_query = "weather forecast"
        return {"action": "search", "engine": "google", "query": weather_query}

    # Website shortcuts like "open youtube" or "open github"
    m = OPEN_PATTERN.match(cleaned)
    if m:
        website = resolve_website_shortcut(m.group(2))
        if website:
            return {"action": "url", "url": website}

    # Volume
    m = VOLUME_PATTERN.match(cleaned)
    if m:
        val = m.group(1).lower()
        return {"action": "volume", "value": val}

    # Brightness
    m = BRIGHTNESS_PATTERN.match(cleaned)
    if m:
        val = m.group(1).lower()
        return {"action": "brightness", "value": val}

    # Timer
    for pattern in TIMER_PATTERNS:
        m = pattern.match(cleaned)
        if m:
            amount = int(m.group(1))
            unit = m.group(2).lower()
            if "minute" in unit:
                amount *= 60
            elif "hour" in unit:
                amount *= 3600
            return {"action": "timer", "seconds": amount}

    # Folder shortcuts (before open pattern)
    m = FOLDER_PATTERN.match(cleaned)
    if m:
        folder = m.group(1).lower()
        return {"action": "open_folder", "path": FOLDER_PATHS[folder]}

    # Create folder with optional destination
    m = NEW_FOLDER_IN_PATTERN.match(cleaned)
    if m:
        folder = m.group(1).lower()
        name = m.group(2).strip()
        return {"action": "create_folder", "name": name, "path": FOLDER_PATHS[folder]}

    # Create folder
    m = NEW_FOLDER_PATTERN.match(cleaned)
    if m:
        name = m.group(1).strip()
        folder = m.group(2).lower() if m.group(2) else None
        if folder:
            return {"action": "create_folder", "name": name, "path": FOLDER_PATHS[folder]}
        return {"action": "create_folder", "name": name}

    # Workspace
    m = WORKSPACE_PATTERN.match(cleaned)
    if m:
        return {"action": "workspace", "workspace": m.group(1)}

    # Move to workspace
    m = MOVE_WORKSPACE_PATTERN.match(cleaned)
    if m:
        return {"action": "move_workspace", "workspace": m.group(1)}

    # Type text
    m = TYPE_PATTERN.match(cleaned)
    if m:
        return {"action": "type", "text": m.group(1).strip()}

    # Switch to app / Focus window
    m = SWITCH_PATTERN.match(cleaned)
    if m:
        return {"action": "switch", "target": m.group(1).strip().lower()}

    # Close app
    m = CLOSE_PATTERN.match(cleaned)
    if m:
        return {"action": "close", "target": m.group(2).strip().lower()}

    # Search "search youtube for X"
    m = SEARCH_FOR_PATTERN.match(cleaned)
    if m:
        return {"action": "search", "engine": resolve_search_engine(m.group(1)), "query": m.group(2).strip()}

    # Search "search X on youtube"
    m = SEARCH_ON_PATTERN.match(cleaned)
    if m:
        return {"action": "search", "engine": resolve_search_engine(m.group(2)), "query": m.group(1).strip()}

    # Search "search cats"
    m = SEARCH_BARE_PATTERN.match(cleaned)
    if m:
        return {"action": "search", "engine": "google", "query": m.group(1).strip()}

    # Play
    m = PLAY_PATTERN.match(cleaned)
    if m:
        engine = resolve_search_engine(m.group(2)) if m.group(2) else "spotify"
        return {"action": "search", "engine": engine, "query": m.group(1).strip()}

    # URL
    m = URL_PATTERN.match(cleaned)
    if m:
        url = m.group(2).strip()
        url = normalize_url(url)
        return {"action": "url", "url": url}

    if looks_like_url(cleaned):
        return {"action": "url", "url": normalize_url(cleaned)}

    if cleaned.lower().startswith("open ") and looks_like_url(cleaned[5:].strip()):
        return {"action": "url", "url": normalize_url(cleaned[5:].strip())}

    if cleaned.lower().startswith("go to ") and looks_like_url(cleaned[6:].strip()):
        return {"action": "url", "url": normalize_url(cleaned[6:].strip())}

    # Create project pattern (e.g. "create a python project")
    m = CREATE_PROJECT_PATTERN.match(cleaned)
    if m:
        ptype = m.group(1).lower()
        if ptype not in ("python", "web", "node"):
            ptype = "python"
        return {"action": "task", "task": "create_project", "type": ptype}

    # Open app (last so folder pattern runs first)
    m = OPEN_PATTERN.match(cleaned)
    if m:
        target = resolve_alias(m.group(2).strip())
        return {"action": "open", "target": target}

    return None