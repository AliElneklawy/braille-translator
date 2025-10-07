from pathlib import Path

import pyttsx3


class TTS:
    def __init__(self, voice_rate: int = 152) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", voice_rate)
        self._voices = self.engine.getProperty("voices") or []

    def set_voice_by_index(self, index: int) -> None:
        if not self._voices:
            return

        index = max(0, min(index, len(self._voices) - 1))
        self.engine.setProperty("voice", self._voices[index].id)

    def say(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

    def save_file(
        self,
        text: str,
        output_dir: str | Path | None = None,
        filename: str = "tts.ogg",
    ) -> Path:
        output_dir = Path(output_dir or ".").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / str(filename)

        self.engine.save_to_file(text, str(output_path))
        self.engine.runAndWait()
        
        return output_path
