from pathlib import Path

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "audio"
CACHE_DIR = AUDIO_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

REFERENCE_AUDIO_PATH = AUDIO_DIR / "reference.wav"
LOG_FILE_PATH = LOGS_DIR / "assistant.log"

# =========================
# ASSISTANT SETTINGS
# =========================
ASSISTANT_NAME = "Rem"
USER_NAME = "Daniel"

# Modos:
# "discreet" = fala apenas remetente
# "full" = fala remetente + mensagem
READ_MODE = "full"

# Ignorar mensagens de grupo
IGNORE_GROUPS = False

# Lista de contatos/grupos bloqueados
BLOCKLIST = {
    "Grupo Silenciado",
    "Promoções",
}

# Lista permitida (se estiver vazia, todos são permitidos)
ALLOWLIST = set()

# Evita repetir notificações iguais
ENABLE_DEDUPLICATION = True

# Tempo de memória de duplicação (segundos)
DEDUP_TTL_SECONDS = 30

# =========================
# VOICE SETTINGS
# =========================
# "light" = TTS local leve
# "clone" = futuro uso com reference.wav
VOICE_MODE = "clone"

# pyttsx3
TTS_RATE = 170
TTS_VOLUME = 1.0

# Frase base
INTRO_TEMPLATE = "Senhor {user}... há uma nova mensagem de {sender}."
MESSAGE_TEMPLATE = "Dizendo: {message}"
DISCREET_TEMPLATE = "Senhor {user}... nova mensagem de {sender}."