from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VoiceConfig:
    use_microphone: bool = True
    speak_responses: bool = True


class VoiceInterface:
    """Handles speech-to-text input and text-to-speech output with fallbacks."""

    def __init__(self, config: VoiceConfig | None = None) -> None:
        self.config = config or VoiceConfig()

        self._recognizer = None
        self._microphone = None
        self._tts_engine = None

        if self.config.use_microphone:
            try:
                import speech_recognition as sr

                self._recognizer = sr.Recognizer()
                self._microphone = sr.Microphone()
            except Exception:
                self._recognizer = None
                self._microphone = None

        if self.config.speak_responses:
            try:
                import pyttsx3

                self._tts_engine = pyttsx3.init()
            except Exception:
                self._tts_engine = None

    def listen(self) -> str:
        if self._recognizer is None or self._microphone is None:
            return input("You (type, mic unavailable): ").strip()

        import speech_recognition as sr

        with self._microphone as source:
            print("Listening... (say 'exit' to quit)")
            self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = self._recognizer.listen(source, timeout=8, phrase_time_limit=10)

        try:
            text = self._recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return input("Speech service unavailable. Type instead: ").strip()

    def speak(self, text: str) -> None:
        print(f"Agent: {text}")
        if self._tts_engine:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
