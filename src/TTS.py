import os

import pyttsx3


class TTS:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 152)

    def say(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

    def save_file(self, text: str, current_dir):
        self.engine.save_to_file(text, os.path.join(current_dir, "tts.ogg"))
        self.engine.runAndWait()
