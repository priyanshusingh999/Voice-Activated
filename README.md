# Voice-Activated Personal Assistant

A local Python assistant that listens for a wake word and can check the
weather, read news headlines, and set/track reminders — spoken aloud via
text-to-speech.

## Features

- **Speech in / speech out** — uses `SpeechRecognition` (Google Web Speech
  API by default) for listening and `pyttsx3` (offline) for speaking.
- **Weather** — current conditions for any city via OpenWeatherMap.
- **News** — top headlines via NewsAPI.
- **Reminders** — natural-language reminders ("remind me to call mom at
  6pm", "remind me to stretch in 20 minutes"), persisted to disk and
  announced automatically when they come due, even mid-conversation.
- **Text mode fallback** (`--text`) for testing without a microphone/speaker.

## Setup

1. **Install system audio dependencies** (needed for `PyAudio`):
   - macOS: `brew install portaudio`
   - Ubuntu/Debian: `sudo apt-get install portaudio19-dev python3-pyaudio`
   - Windows: usually installs cleanly via pip.

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get free API keys:**
   - Weather: https://openweathermap.org/api (free tier is enough)
   - News: https://newsapi.org (free tier is enough)

4. **Configure your keys** — either edit `config.py` directly, or set
   environment variables so you never commit secrets:
   ```bash
   export OPENWEATHER_API_KEY="your_key_here"
   export NEWS_API_KEY="your_key_here"
   export ASSISTANT_CITY="Bhopal"   # optional default city
   ```

## Running

**With microphone and speaker:**
```bash
python main.py
```
Say the wake word (default `"Nova"`, configurable in `config.py`) followed
by a command:

- "Nova, what's the weather?"
- "Nova, what's the weather in Tokyo?"
- "Nova, what's the news?"
- "Nova, remind me to call mom at 6pm"
- "Nova, remind me to stretch in 20 minutes"
- "Nova, what are my reminders?"
- "Nova, help"
- "Nova, stop" / "exit" / "quit"

**Without a microphone (typed input, for testing):**
```bash
python main.py --text
```
In this mode you don't need to say the wake word — just type commands
directly.

## Project structure

```
voice_assistant/
├── main.py              # Entry point: wake-word loop, command routing
├── config.py             # API keys and tunable settings
├── requirements.txt
├── modules/
│   ├── speech.py          # SpeechRecognition + pyttsx3 wrapper
│   ├── weather.py         # OpenWeatherMap lookup
│   ├── news.py             # NewsAPI headline lookup
│   └── reminders.py       # Natural-language parsing, storage, background watcher
└── reminders.json         # Created automatically to persist reminders
```

## Notes & possible extensions

- Recognition uses Google's free web API by default, which requires an
  internet connection. Swap in `recognize_sphinx` (offline, via
  `pocketsphinx`) in `modules/speech.py` if you need it to work offline.
- Reminder time parsing is handled by `dateparser`, so many phrasings work
  ("tomorrow at noon", "in 2 hours", "next Monday at 9am").
- To add new commands, add another `if` branch in `handle_command()` in
  `main.py`.
- The reminder watcher runs on a background thread, so a reminder can fire
  and be spoken even while the assistant is otherwise idle listening.