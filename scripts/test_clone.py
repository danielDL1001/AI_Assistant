from TTS.api import TTS

# carrega modelo
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# gera áudio usando reference.wav
tts.tts_to_file(
    text="Olá Daniel, isso é um teste com voz clonada.",
    file_path="output.wav",
    speaker_wav=["audio/reference.wav"],
    language="pt"
)