import random
from datetime import datetime


def get_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        time_of_day = "morning"
    elif hour < 17:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    greetings = [
        f"Good {time_of_day} Atharv, what's on your mind?",
        f"Hey Atharv, good {time_of_day}. What should we tackle first?",
        f"Hi Atharv, hope your {time_of_day} is going well. What do you need?",
        f"Good {time_of_day}, Atharv. Ready when you are.",
        f"Atharv, good {time_of_day}. How can I help today?",
        f"Hello Atharv, wishing you a great {time_of_day}. What's the plan?",
        f"Good {time_of_day} Atharv. Want to continue where we left off?",
        f"Hi Atharv. It's a nice {time_of_day} to get things done.",
        f"Good {time_of_day}, Atharv. Tell me what you'd like to work on.",
        f"Hey Atharv, happy {time_of_day}. I'm listening.",
        "At it again, boss. What's first?",
        "Feeling motivated today? Let's make it count.",
        "Ready to lock in? I am.",
        "Back in action, Atharv. What are we building?",
        "Let's cook, boss. What's the mission?",
        "New task, same hustle. What's up?",
        "I'm here and fully dialed in.",
        "Say the word and we start.",
        "Need speed, clarity, or both?",
        "What's the game plan today?",
        "Time to make progress. Where do we begin?",
        "Let's get moving. What's the priority?",
        "Good to see you back. What's next?",
        "All systems ready. Send it.",
        "Boss mode on. What are we tackling?",
        "Want to pick up from the last step?",
        "Let's turn ideas into output.",
        "I am ready when you are, chief.",
        "Need a quick win or deep work session?",
        "What's on deck, Atharv?",
        "Locked in and listening.",
        "Let's make this a productive run.",
        "Fresh start. What do you want to do first?",
        "We are back. What should I handle?",
        "Momentum check: should we continue or pivot?",
        "I am all ears. Hit me with it.",
        "Let's make today a strong one.",
        "Alright boss, what are we crushing next?",
        "You bring the goal, I will bring the execution.",
        "Ready for round two. What's the move?",
    ]

    return random.choice(greetings)