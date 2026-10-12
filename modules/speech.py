"""
Speech I/O layer: wraps SpeechRecognition (speech-to-text) and pyttsx3
(text-to-speech) behind a small, testable interface.
"""

import threading

import speech_recognition as sr
import pyttsx3

from config import TTS_RATE, TTS_VOLUME, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT


class SpeechIO:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", TTS_RATE)
        self.engine.setProperty("volume", TTS_VOLUME)
        self._speak_lock = threading.Lock()

        # Calibrate once for ambient noise so recognition is more reliable.
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def speak(self, text: str) -> None:
        """Speak text aloud and also print it, so the console mirrors what's said.
        Thread-safe: the background reminder watcher can call this too."""
        with self._speak_lock:
            print(f"Assistant: {text}")
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self) -> str:
        """
        Listen on the microphone and return recognized text (lowercased),
        or an empty string if nothing could be understood.
        """
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )
            except sr.WaitTimeoutError:
                return ""

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[speech] Recognition service error: {e}")
            return ""