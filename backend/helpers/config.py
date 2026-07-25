from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (…/rankridge_website_chatbot).
# config.py lives at backend/helpers/config.py, so the root is three levels up.
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

    # Database. Defaults to a local SQLite file for development; set to a
    # Postgres URL (e.g. Railway's DATABASE_URL) in production so leads and
    # chat history survive redeploys.
    DATABASE_URL: str = "sqlite:///./chatbot.db"

    # Comma-separated list of origins allowed to call the API. "*" allows any
    # origin (needed while the website calls the backend cross-origin). Narrow
    # this to the site's domain(s) once the production backend URL is fixed.
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Strip stray whitespace/newlines that sneak in when pasting values into a
    # dashboard (e.g. Railway variables). A trailing newline in MODEL_NAME or
    # the API key silently breaks the OpenAI call.
    @field_validator(
        "OPENAI_API_KEY", "MODEL_NAME", "ADMIN_KEY", "DATABASE_URL", "ALLOWED_ORIGINS",
        mode="before",
    )
    @classmethod
    def _strip_whitespace(cls, value):
        return value.strip() if isinstance(value, str) else value

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


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
