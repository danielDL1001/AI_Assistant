import os
import platform
import queue
import tempfile
import threading
from pathlib import Path
from TTS.api import TTS
from scripts.config import REFERENCE_AUDIO_PATH, VOICE_MODE



class TTSEngine:
    """Thread-safe TTS engine that always speaks in background."""

    def __init__(self, logger=None):
        self.logger = logger
        self._queue: queue.Queue[str] = queue.Queue()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        if VOICE_MODE == "clone":
            if self.logger:
                self.logger.info("Loading XTTS voice cloning model...")
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self.engine = None
        else:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.tts = None

        self._worker.start()

    def speak(self, text: str) -> None:
        text = text.strip()
        if text:
            self._queue.put(text)

    def _worker_loop(self) -> None:
        while True:
            text = self._queue.get()
            try:
                if VOICE_MODE == "clone":
                    self._speak_clone(text)
                else:
                    self._speak_light(text)
            except Exception as exc:  # pragma: no cover - defensive path
                if self.logger:
                    self.logger.exception("TTS failed for text=%s | error=%s", text, exc)
            finally:
                self._queue.task_done()

    def _speak_light(self, text: str) -> None:
        if not self.engine:
            return
        self.engine.say(text)
        self.engine.runAndWait()

    def _speak_clone(self, text: str) -> None:
        if not self.tts:
            return
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = Path(temp_file.name)

        self.tts.tts_to_file(
            text=text,
            file_path=str(temp_path),
            speaker_wav=[str(REFERENCE_AUDIO_PATH)],
            language="pt"
        )

        self._play_audio(temp_path)

        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            if self.logger:
                self.logger.warning("Could not remove temporary audio file: %s", temp_path)

    def _play_audio(self, wav_path: Path) -> None:
        system = platform.system().lower()

        if "windows" in system:
            os.system(f'powershell -c "(New-Object Media.SoundPlayer \"{wav_path}\").PlaySync();"')
            return

        if os.system(f'command -v aplay >/dev/null 2>&1') == 0:
            os.system(f'aplay "{wav_path}" >/dev/null 2>&1')
            return

        # fallback on Linux/macOS when aplay is not available
        os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{wav_path}" >/dev/null 2>&1')
