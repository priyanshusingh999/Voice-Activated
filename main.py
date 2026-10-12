

import re
import sys
from datetime import datetime

from config import ASSISTANT_NAME
from modules.speech import SpeechIO
from modules import news, remainder as reminders, weateher as weather


WAKE_WORD = ASSISTANT_NAME.lower()


class TextIO:
    """Fallback console-only I/O, used with --text so the assistant can be
    tried out on machines without a working microphone/speaker."""

    def speak(self, text: str) -> None:
        print(f"Assistant: {text}")

    def listen(self) -> str:
        try:
            return input("You: ").strip().lower()
        except EOFError:
            return "exit"


def strip_wake_word(command: str) -> str:
    pattern = rf"^\s*{re.escape(WAKE_WORD)}[,]?\s*"
    return re.sub(pattern, "", command, flags=re.IGNORECASE).strip()


def handle_command(command: str, io) -> bool:
    """
    Process a single recognized command. Returns False if the assistant
    should shut down, True otherwise.
    """
    command = command.strip()
    if not command:
        return True

    if any(word in command for word in ("exit", "quit", "stop", "goodbye")):
        io.speak("Goodbye!")
        return False

    if "weather" in command:
        city_match = re.search(r"\bin\s+([a-zA-Z\s]+)$", command)
        city = city_match.group(1).strip() if city_match else None
        io.speak(weather.get_weather(city))
        return True

    if "news" in command or "headline" in command:
        io.speak(news.get_headlines())
        return True

    if "my reminders" in command or "pending reminders" in command or command == "reminders":
        pending = reminders.list_pending()
        if not pending:
            io.speak("You have no pending reminders.")
        else:
            parts = []
            for r in pending:
                due = datetime.fromisoformat(r["due"])
                parts.append(f"{r['task']} on {due.strftime('%A at %I:%M %p')}")
            io.speak("Here's what's pending: " + "; ".join(parts))
        return True

    if "remind" in command:
        result = reminders.parse_reminder_command(command)
        if "error" in result:
            io.speak(result["error"] + " Try something like: remind me to call mom at 6pm.")
        else:
            reminders.add_reminder(result["task"], result["due"])
            when = result["due"].strftime("%A at %I:%M %p")
            io.speak(f"Okay, I'll remind you to {result['task']} on {when}.")
        return True

    if "help" in command or "what can you do" in command:
        io.speak(
            "I can check the weather, read the news, and set reminders. "
            f"Just say {ASSISTANT_NAME}, followed by your request."
        )
        return True

    io.speak("Sorry, I didn't understand that. Say 'help' to hear what I can do.")
    return True


def main():
    use_text_mode = "--text" in sys.argv

    io = TextIO() if use_text_mode else SpeechIO()

    watcher = reminders.ReminderWatcher(
        on_due=lambda r: io.speak(f"Reminder: {r['task']}")
    )
    watcher.start()

    io.speak(
        f"Hi, I'm {ASSISTANT_NAME}. Say '{ASSISTANT_NAME}' followed by a "
        "command, such as 'what's the weather' or 'remind me to call mom at 6pm'."
    )

    try:
        while True:
            heard = io.listen()
            if not heard:
                continue

            if use_text_mode:
                # In text mode, don't require the wake word every time -
                # just process what was typed directly.
                command = heard
            else:
                if WAKE_WORD not in heard:
                    continue
                command = strip_wake_word(heard)

            keep_running = handle_command(command, io)
            if not keep_running:
                break
    except KeyboardInterrupt:
        io.speak("Goodbye!")
    finally:
        watcher.stop()


if __name__ == "__main__":
    main()