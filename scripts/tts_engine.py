from TTS.api import TTS
import os
import tempfile

from scripts.config import VOICE_MODE, REFERENCE_AUDIO_PATH


class TTSEngine:
    def __init__(self):
        if VOICE_MODE == "clone":
            print("Carregando modelo de voz (XTTS)...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        else:
            import pyttsx3
            self.engine = pyttsx3.init()

    def speak(self, text: str):
        if VOICE_MODE == "clone":
            self._speak_clone(text)
        else:
            self._speak_light(text)

    def _speak_light(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

    def _speak_clone(self, text: str):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_path = temp_file.name
        temp_file.close()

        self.tts.tts_to_file(
            text=text,
            file_path=temp_path,
            speaker_wav=[str(REFERENCE_AUDIO_PATH)],
            language="pt"
        )

        os.system(f"aplay {temp_path}")