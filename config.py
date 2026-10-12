"""
Configuration for the Voice-Activated Personal Assistant.

Fill in your own API keys below, or set them as environment variables
with the same names (recommended so you never commit secrets to source
control).
"""

import os

# --- Assistant identity -----------------------------------------------
ASSISTANT_NAME = "Nova"          # Wake word used to address the assistant
LISTEN_TIMEOUT = 5               # Seconds to wait for the user to start speaking
PHRASE_TIME_LIMIT = 8            # Max seconds for a single spoken command

# --- Text-to-speech settings --------------------------------------------
TTS_RATE = 175                   # Words per minute
TTS_VOLUME = 1.0                 # 0.0 - 1.0

# --- OpenWeatherMap (https://openweathermap.org/api) --------------------
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
DEFAULT_CITY = os.environ.get("ASSISTANT_CITY", "London")
TEMP_UNITS = "metric"            # "metric" = Celsius, "imperial" = Fahrenheit

# --- NewsAPI (https://newsapi.org) --------------------------------------
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
NEWS_COUNTRY = "us"
NEWS_MAX_HEADLINES = 5

# --- Reminders -----------------------------------------------------------
REMINDERS_FILE = os.path.join(os.path.dirname(__file__), "reminders.json")
REMINDER_CHECK_INTERVAL = 15     # Seconds between checks for due reminders