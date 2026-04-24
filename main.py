from __future__ import annotations

from voice_agent.agent import VoiceTodoAgent
from voice_agent.voice import VoiceConfig, VoiceInterface


def main() -> None:
    print("Voice Todo Agent started.")
    print("Say/type your command. Say 'exit' or 'quit' to stop.")

    agent = VoiceTodoAgent()
    voice = VoiceInterface(VoiceConfig(use_microphone=True, speak_responses=True))

    while True:
        try:
            user_text = voice.listen()
        except Exception as exc:
            print(f"Input error: {exc}")
            continue

        if not user_text:
            voice.speak("I did not hear anything. Please try again.")
            continue

        if user_text.strip().lower() in {"exit", "quit", "bye"}:
            voice.speak("Goodbye!")
            break

        reply = agent.process(user_text)
        voice.speak(reply)


if __name__ == "__main__":
    main()
