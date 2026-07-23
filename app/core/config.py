from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (…/chatbot_backend). config.py lives at app/core/config.py,
# so the root is two directories up.
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_NAME: str
    SYSTEM_PROMPT: str = "You are a helpful AI assistant."
    # Website knowledge is kept in a plain-text file so it can be updated
    # without touching code or the system prompt. Path is relative to the
    # project root unless an absolute path is given.
    WEBSITE_KNOWLEDGE_FILE: str = "website_knowledge.txt"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 500
    ADMIN_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()


def load_website_knowledge() -> str:
    """Read the current website knowledge from disk.

    Read fresh on every call so edits to the .txt file take effect
    immediately, without restarting the server.
    """
    path = Path(settings.WEBSITE_KNOWLEDGE_FILE)
    if not path.is_absolute():
        path = BASE_DIR / path

    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def get_system_prompt() -> str:
    """Compose the full system prompt by injecting the latest website
    knowledge into the SYSTEM_PROMPT template's {{WEBSITE_KNOWLEDGE}}
    placeholder."""
    knowledge = load_website_knowledge()
    return settings.SYSTEM_PROMPT.replace("{{WEBSITE_KNOWLEDGE}}", knowledge)
