import whisper


class SpeechToText():
    def __init__(self):
        self.model = whisper.load_model('small')

    def transcribe(self, file_path):
        result = self.model.transcribe(file_path)
        return result["text"]
