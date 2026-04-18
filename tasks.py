import os
import subprocess
from pathlib import Path
from tts import speak
from stt import listen
from parser import clean_input
import time

PROJECTS_DIR = Path(r"C:\Users\Atharv\Documents\Projects")
GITHUB_USERNAME = "your_github_username"  # change this once

PROJECT_TEMPLATES = {
    "python": {
        "files": {
            "main.py": "# Entry point\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n",
            "requirements.txt": "",
            ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n",
            "README.md": "# {name}\n\n## Setup\n\n```bash\npip install -r requirements.txt\n```\n",
        },
        "folders": ["src", "tests"],
    },
    "web": {
        "files": {
            "index.html": "<!DOCTYPE html>\n<html>\n<head>\n  <meta charset='UTF-8'>\n  <title>{name}</title>\n  <link rel='stylesheet' href='style.css'>\n</head>\n<body>\n  <script src='script.js'></script>\n</body>\n</html>\n",
            "style.css": "* { margin: 0; padding: 0; box-sizing: border-box; }\n",
            "script.js": "// {name}\n",
            ".gitignore": "node_modules/\n.env\n",
            "README.md": "# {name}\n",
        },
        "folders": [],
    },
    "node": {
        "files": {
            "index.js": "// {name}\n\nconst express = require('express');\nconst app = express();\n\napp.listen(3000, () => console.log('Running on port 3000'));\n",
            ".gitignore": "node_modules/\n.env\n",
            "README.md": "# {name}\n",
        },
        "folders": ["src", "routes"],
        "post_commands": ["npm init -y"],
    },
    "generic": {
        "files": {
            "README.md": "# {name}\n",
            ".gitignore": ".env\n",
        },
        "folders": [],
    },
}


def ask(question: str) -> str:
    speak(question)
    time.sleep(len(question.split()) * 0.35 + 0.8)
    response = listen()
    return clean_input(response).strip() if response else ""


def create_project(project_type: str = "python"):
    name = ask("What should I name the project?")
    if not name:
        speak("Didn't catch the name, cancelling.")
        return

    name = name.strip().replace(" ", "_").replace("-", "_")
    project_path = PROJECTS_DIR / name

    if project_path.exists():
        speak(f"A project called {name} already exists. Should I open it instead?")
        time.sleep(2)
        response = listen()
        if response and "yes" in response.lower():
            open_in_editor(project_path)
        return

    speak(f"Creating {project_type} project called {name}.")

    template = PROJECT_TEMPLATES.get(project_type, PROJECT_TEMPLATES["generic"])
    project_path.mkdir(parents=True, exist_ok=True)

    for folder in template.get("folders", []):
        (project_path / folder).mkdir(exist_ok=True)

    for filename, content in template.get("files", {}).items():
        (project_path / filename).write_text(
            content.replace("{name}", name), encoding="utf-8"
        )

    print(f"[Task] Created project at {project_path}")

    # run post commands (npm init etc)
    for cmd in template.get("post_commands", []):
        subprocess.run(cmd.split(), cwd=project_path, capture_output=True)

    # venv for python
    if project_type == "python":
        speak("Should I set up a virtual environment?")
        time.sleep(2)
        response = listen()
        if response and "yes" in response.lower():
            subprocess.Popen(["python", "-m", "venv", "venv"], cwd=project_path)
            speak("Virtual environment created.")

    speak(f"Done. Should I open {name} in your editor?")
    time.sleep(2)
    response = listen()
    if response and "yes" in response.lower():
        open_in_editor(project_path)
    else:
        speak("Project is ready.")


def push_to_github():
    # Step 1: which project
    response = ask("Which project do you want to push?")
    if not response:
        speak("Didn't catch that, cancelling.")
        return

    # fuzzy match project folder
    project_name = response.strip().replace(" ", "_")
    matches = [
        p for p in PROJECTS_DIR.iterdir()
        if p.is_dir() and (
            project_name.lower() in p.name.lower() or
            p.name.lower() in project_name.lower()
        )
    ]

    if not matches:
        speak(f"Couldn't find a project called {response}. Check your projects folder.")
        return

    project_path = matches[0]
    speak(f"Found {project_path.name}.")

    # Step 2: which repo
    repo = ask("What's the GitHub repo name?")
    if not repo:
        speak("Didn't catch the repo name, cancelling.")
        return

    repo = repo.strip().replace(" ", "-")
    remote_url = f"https://github.com/{GITHUB_USERNAME}/{repo}.git"

    speak(f"Pushing {project_path.name} to {repo}.")

    try:
        # init if not already a git repo
        git_dir = project_path / ".git"
        if not git_dir.exists():
            subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
            speak("Initialized git repo.")

        # check if remote exists
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_path, capture_output=True, text=True
        )
        if result.returncode != 0:
            # add remote
            subprocess.run(
                ["git", "remote", "add", "origin", remote_url],
                cwd=project_path, capture_output=True
            )

        # stage all
        subprocess.run(["git", "add", "."], cwd=project_path, capture_output=True)

        # commit
        result = subprocess.run(
            ["git", "commit", "-m", "update"],
            cwd=project_path, capture_output=True, text=True
        )
        if "nothing to commit" in result.stdout:
            speak("Nothing new to commit.")
            return

        # push
        result = subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            cwd=project_path, capture_output=True, text=True,
            timeout=30
        )

        if result.returncode == 0:
            speak(f"Successfully pushed {project_path.name} to GitHub.")
            print(f"[Git] Push successful → {remote_url}")
        else:
            error = result.stderr.strip()
            print(f"[Git] Push failed: {error}")
            if "master" in error:
                # try master branch
                subprocess.run(
                    ["git", "push", "-u", "origin", "master"],
                    cwd=project_path, capture_output=True
                )
                speak("Pushed to master branch.")
            else:
                speak("Push failed. Check your GitHub credentials or repo name.")

    except subprocess.TimeoutExpired:
        speak("Push timed out. Check your internet connection.")
    except Exception as e:
        speak("Something went wrong with the push.")
        print(f"[Git] Error: {e}")


def open_in_editor(path: Path):
    try:
        subprocess.Popen(["windsurf", str(path)])
        speak("Opening in Windsurf.")
    except FileNotFoundError:
        try:
            subprocess.Popen(["code", str(path)])
            speak("Opening in VS Code.")
        except FileNotFoundError:
            os.startfile(str(path))
            speak("Opened in file explorer.")
