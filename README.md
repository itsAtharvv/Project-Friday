# Project Friday 🤖

A sophisticated Windows-based AI voice assistant that enables complete PC control through natural voice commands. Triggered with **Ctrl+Shift+Space**, Friday intelligently routes commands to AI models, executes them, and provides voice feedback.

---

## ✨ Features

### **Voice Activation & Interface**
- 🎤 Global hotkey trigger: **Ctrl+Shift+Space**
- 🎨 Real-time PyQt6 UI with animated 48-bar audio visualizer
- 🔊 Voice feedback with text display
- 📊 Visual state indicators: listening → processing → speaking → done

### **System Control**
- Power management: shutdown, restart, sleep, lock screen
- Volume control: up, down, mute, unmute, set percentage (0-100)
- Brightness control: up, down, set percentage (0-100)
- Screenshot capture with timestamp
- Battery status check
- Empty recycle bin, minimize all windows

### **Application Management**
- Launch any installed app by voice: "open chrome", "start vscode"
- Close apps: "close spotify", "kill notepad"
- Switch between apps: "switch to chrome"
- 50+ app shortcuts with fuzzy matching
- App aliases: chrome→Google Chrome, resolve→DaVinci Resolve, etc.

### **Web & Search**
- Multi-engine search: Google, YouTube, GitHub, Maps, Spotify
- Examples: "search github for python auth", "search lofi on youtube"
- Direct URL navigation: "visit google.com", "open https://example.com"
- Website shortcuts: "open gmail", "open chatgpt"

### **File & Folder Operations**
- Quick folder access: "open downloads", "show documents folder"
- Create folders by voice: "create folder named Projects"
- Location-aware: "create folder in downloads called Invoices"
- Smart alias resolution: download→downloads, desk→desktop, etc.

### **Typing & Clipboard**
- Voice dictation: "type hello world" → pastes into active window
- Clipboard control: copy, paste, clear clipboard
- Automatic fallback to clipboard for special characters

### **Media Control**
- Music playback: skip, next, previous, pause, resume
- Works with Spotify, local players, and media controls

### **Timers**
- Create timers by voice: "set timer for 5 minutes"
- Variations: "10 second timer", "remind me in 1 hour"
- Popup notification when timer completes

### **OCR & Screen Reading** 📸
- **Read mode**: "read screen", "what does it say" → extracts visible text
- **Describe mode**: "what's on my screen", "describe screen" → provides summary
- Uses local Ollama vision model (no API costs)

### **Multi-Turn Conversation** 💬
- Natural dialogue: "what is machine learning?", "how does encryption work?"
- Maintains last 8 conversation turns
- Automatic context-aware responses
- Stop with: "stop", "bye", "goodbye", "end", "that's all", "enough"

### **Command Chaining** ⛓️
Combine multiple commands in one sentence:
- "open chrome **and** search youtube for lofi"
- "open documents **then** create folder named Invoices"
- Separators: "and", "then", "and then", "after that", "also"

### **Project Scaffolding** 🛠️
Create complete project structures by voice:

**Python Project**
```
"new python project"
├── Creates: main.py, requirements.txt, README.md, .gitignore
├── Folders: src/, tests/
├── Optional: Virtual environment setup
```

**Web Project**
```
"new web project"
├── Creates: index.html, style.css, script.js, README.md, .gitignore
```

**Node Project**
```
"new node project"
├── Creates: index.js, README.md, .gitignore
├── Runs: npm init -y
├── Folders: src/, routes/
```

- Interactive voice prompts for project name
- Auto-opens in Windsurf, VS Code, or File Explorer

### **GitHub Integration** 🚀
Push projects to GitHub entirely by voice:

**Command**: "push to github", "git push", "push my project"

**Automated workflow**:
1. Select project (fuzzy-matched from Projects folder)
2. Enter GitHub repo name
3. Auto-init git, add remote, stage files, commit, push
4. Handles branch detection (main/master)
5. Credential caching (after first manual push)

---

## 🏗️ Architecture

| Module | Purpose |
|--------|---------|
| **main.py** | Hotkey listener, command pipeline, event orchestration |
| **parser.py** | 40+ regex patterns for command parsing |
| **executor.py** | System automation, app launching, file operations |
| **router.py** | LLM model selection, conversation intent routing |
| **stt.py** | Whisper speech-to-text, silence detection |
| **tts.py** | Edge TTS voice generation, async playback |
| **llm.py** | Groq API integration (dual models) |
| **normalizer.py** | Ollama local model for language simplification |
| **ocr.py** | Screen capture + Ollama vision for text extraction |
| **tasks.py** | Project scaffolding, Git automation |
| **ui.py** | PyQt6 audio visualizer |
| **greeting.py** | Time-aware personalized greetings |
| **audio.py** | Sound effect playback |

---

## 📋 Complete Command Reference

### System Commands
```
shutdown              → Power down
restart               → Reboot system
sleep                 → Hibernate
lock (or lock screen) → Lock workstation
screenshot           → Save to Desktop
battery              → Show battery status
empty recycle bin    → Purge trash
minimize all         → Win+D (show desktop)
```

### Volume Control
```
volume up            → +5%
volume down          → -5%
mute                 → Silence
unmute               → Restore
volume 75            → Set to 75%
```

### Brightness Control
```
brightness up        → +10%
brightness down      → -10%
dim screen           → -10%
brightness 50        → Set to 50%
```

### Media Control
```
skip (or next)       → Next track
go back (or previous)→ Previous track
pause                → Pause/resume
resume               → Play
```

### Application Management
```
open chrome          → Launch app
launch vscode        → Start editor
close spotify        → Kill app
switch to discord    → Alt+Tab
```

### Web & Search
```
search cats          → Google search
search github for api→ GitHub search
search youtube for music→ YouTube
play lofi on spotify → Spotify search
visit reddit.com     → Open URL
open youtube         → Go to homepage
```

### Files & Folders
```
open downloads       → Show Downloads
show documents       → Show Documents folder
type hello world     → Paste text
create folder work   → Make folder
create folder in desktop called Screens→ Location-specific
copy                 → Ctrl+C
paste                → Ctrl+V
clear clipboard      → Clear
```

### Timers
```
set timer for 5 minutes→ 5-min countdown
10 second timer      → 10-sec countdown
remind me in 1 hour  → 60-min countdown
```

### OCR / Screen Reading
```
read screen          → Extract visible text
what does it say     → Read text
what's on my screen  → Describe screen
describe screen      → 2-3 sentence summary
```

### Project Creation
```
new python project   → Create Python scaffold
create web project   → Create HTML/CSS/JS scaffold
new node project     → Create Node scaffold
new project          → Default to Python
```

### GitHub
```
push to github       → Push current project
git push             → Alternative
push my project      → Alternative
upload to github     → Alternative
```

### Conversation (Chat Mode)
```
what is AI?          → Chat response
how does encryption work?→ Explanation
tell me about Python→ Information query
explain machine learning→ Learning
```

---

## 🚀 Installation

### Requirements
- **Windows 10/11** (hotkey system is Windows-only)
- **Python 3.11+**
- **Microphone** for input
- **Internet** for Groq API
- **Ollama** for local models (optional but recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/itsAtharvv/project-friday.git
cd project-friday
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Groq API
1. Get free API key from https://console.groq.com/keys
2. Create `.env` file in project root:
	```env
	GROQ_API_KEY=your_api_key_here
	```

### Step 4: Install Ollama (Optional but Recommended)
Download from https://ollama.com/download

Required models:
```bash
ollama pull gemma4:e2b    # Text normalization
ollama pull gemma4:e4b    # Screen OCR
ollama serve              # Run in separate terminal
```

### Step 5: Run Friday
```bash
python main.py
```

Access with **Ctrl+Shift+Space**

### Step 6: Setup Git Credentials (for GitHub integration)
```bash
git config --global credential.helper store
```

Then do one manual git push anywhere — credentials are cached forever.

---

## ⚙️ Configuration

### GitHub Username (for push_to_github)
Edit tasks.py line 10:
```python
GITHUB_USERNAME = "your_github_username"
```

### Voice Settings
- **TTS Voice**: UK English (Ryan) — configurable in tts.py
- **STT Model**: Whisper small (local, ~1GB)
- **LLM Models**: Groq (remote, requires API)
- **Conversation turns**: 8 (configurable in main.py)

---

## 🎯 Usage Examples

### Example 1: Create & Push a Python Project
```
User: "new python project"
Friday: "What should I name the project?"
User: "my_api"
Friday: "Creating python project..."
[Opens in editor]

User: "push my project"
Friday: "Successfully pushed to GitHub."
```

### Example 2: Multi-Command Chaining
```
User: "open chrome and search youtube for lofi and set volume to 50"
Friday: "Running 3 commands."
[All commands execute in sequence]
```

### Example 3: OCR & Chat
```
User: "read screen"
Friday: [Extracts and speaks visible text]

User: "what is artificial intelligence?"
Friday: "AI refers to... [intelligent response]"
```

---

## 🛠️ Troubleshooting

### **Hotkey not working**
- Ensure Friday is running: `python main.py`
- Check that no other app has Ctrl+Shift+Space registered
- Run as Administrator if needed

### **Microphone issues**
- Test in Windows Sound Settings
- Ensure microphone is default input device

### **STT errors ("Didn't catch that")**
- Speak clearly and closer to mic
- Reduce background noise
- Check internet connection

### **OCR not working**
- Ensure Ollama is running: `ollama serve`
- Verify models: `ollama list`

### **Groq API errors**
- Verify `.env` has valid `GROQ_API_KEY`
- Check rate limits (free tier: 30 requests/minute)

### **Git push authentication fails**
- Run first manual push: `git push -u origin main`
- Ensure credentials cached: `git config credential.helper` → `store`

---

## ⚠️ Known Limitations

1. **Windows-only** - Paths and commands are Windows-specific
2. **Ollama optional** - Gracefully skips if unavailable
3. **English-only** - No multi-language support
4. **Microphone required** - No text input fallback
5. **Internet-dependent** - Groq API requires connection
6. **No persistent history** - Conversations cleared on exit

---

## 🚀 Future Enhancements

- [ ] Multi-language support
- [ ] Email/Calendar integration
- [ ] Browser automation
- [ ] Custom wake word
- [ ] Offline LLM support
- [ ] Mac/Linux support

---

## 📄 License
MIT License — Feel free to fork, modify, and use!

---

## 🎉 Credits
Built with ❤️ by Atharv  
Powered by: Whisper, Groq, Edge TTS, Ollama, PyQt6

---

**Made with AI. Controlled by Voice. Ready for the future.** 🚀