import pyttsx3
import os

class TTS():
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 152)

    def say(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
    
    def save_file(self, text: str, current_dir, voice_id: int = 0):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[voice_id].id)
        self.engine.save_to_file(text, os.path.join(current_dir, "tts.ogg"))
        self.engine.runAndWait()

        
