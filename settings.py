from pathlib import Path

DB_PATH = Path("chat.db")
SQL_URL = f"sqlite:///{DB_PATH}"

DEFAULT_MODEL = "llama3:8b"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TOP_P = 0.9
DEFAULT_SEED = 42

DEFAULT_SYSTEM_PROMPT = (
    "You are a story teller AI. Your task is to create engaging and imaginative stories based on user prompts"
)

# Summarization thresholds
SUMMARY_LIMIT_CHARS = 8000
SUMMARY_KEEP_LAST = 8