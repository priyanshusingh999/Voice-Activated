"""
Reminder management: create, persist, and watch for due reminders.

Reminders are stored as JSON on disk so they survive restarts. A background
thread wakes up periodically and hands any due reminders back to the app
via a callback so they can be spoken aloud.
"""

import json
import os
import re
import threading
import time
import uuid
from datetime import datetime, timedelta

import dateparser

from config import REMINDERS_FILE, REMINDER_CHECK_INTERVAL

_lock = threading.Lock()


def _load() -> list:
    if not os.path.exists(REMINDERS_FILE):
        return []
    with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save(reminders: list) -> None:
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2, default=str)


def _extract_time_phrase(command: str) -> tuple[str, str]:
    """
    Split a command like "remind me to call mom at 5pm" or
    "remind me to check the oven in 20 minutes" into (task, time phrase).
    Falls back to treating the whole command as the task if no time
    marker is found, in which case the caller should ask for a time.
    """
    match = re.search(r"\b(at|in|on)\b\s+(.+)$", command)
    if not match:
        return command.strip(), ""
    task = command[: match.start()].strip()
    time_phrase = match.group(0).strip()
    return task, time_phrase


def parse_reminder_command(command: str) -> dict:
    """
    Parse a natural-language reminder request such as:
        "remind me to take out the trash at 7pm"
        "remind me to stretch in 30 minutes"
    Returns {"task": str, "due": datetime} or {"error": str}.
    """
    text = command.lower()
    text = re.sub(r"^(please\s+)?remind me to\s+", "", text).strip()

    task, time_phrase = _extract_time_phrase(text)
    if not task:
        return {"error": "I didn't catch what you want to be reminded about."}
    if not time_phrase:
        return {"error": "I didn't catch when you want to be reminded."}

    due = dateparser.parse(
        time_phrase, settings={"PREFER_DATES_FROM": "future"}
    )
    if due is None:
        return {"error": f"I couldn't understand the time '{time_phrase}'."}
    if due <= datetime.now():
        due = due + timedelta(days=1)  # e.g. "at 7am" already passed today

    return {"task": task, "due": due}


def add_reminder(task: str, due: datetime) -> dict:
    with _lock:
        reminders = _load()
        reminder = {
            "id": str(uuid.uuid4()),
            "task": task,
            "due": due.isoformat(),
            "notified": False,
        }
        reminders.append(reminder)
        _save(reminders)
    return reminder


def list_pending() -> list:
    with _lock:
        reminders = _load()
    return [r for r in reminders if not r["notified"]]


def _mark_notified(reminder_id: str) -> None:
    with _lock:
        reminders = _load()
        for r in reminders:
            if r["id"] == reminder_id:
                r["notified"] = True
        _save(reminders)


class ReminderWatcher(threading.Thread):
    """Background thread that periodically fires due reminders."""

    def __init__(self, on_due):
        """
        on_due: callable(reminder_dict) invoked (from this background
        thread) whenever a reminder becomes due.
        """
        super().__init__(daemon=True)
        self.on_due = on_due
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            now = datetime.now()
            for reminder in list_pending():
                due = datetime.fromisoformat(reminder["due"])
                if due <= now:
                    _mark_notified(reminder["id"])
                    self.on_due(reminder)
            self._stop_event.wait(REMINDER_CHECK_INTERVAL)

    def stop(self):
        self._stop_event.set()