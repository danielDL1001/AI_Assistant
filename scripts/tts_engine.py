import pyttsx3
from scripts.config import VOICE_MODE, TTS_RATE, TTS_VOLUME


class TTSEngine:
    def __init__(self):
        self.engine = None

        if VOICE_MODE == "light":
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", TTS_RATE)
            self.engine.setProperty("volume", TTS_VOLUME)

    def speak(self, text: str):
        if VOICE_MODE == "light":
            self._speak_light(text)
        elif VOICE_MODE == "clone":
            self._speak_clone(text)
        else:
            raise ValueError(f"VOICE_MODE inválido: {VOICE_MODE}")

    def _speak_light(self, text: str):
        if not self.engine:
            raise RuntimeError("Engine TTS leve não inicializada.")

        self.engine.say(text)
        self.engine.runAndWait()

    def _speak_clone(self, text: str):
        # FUTURO:
        # Aqui entraremos com uma engine de clonagem real
        # baseada em audio/reference.wav
        print(f"[CLONE MODE FUTURO] {text}")