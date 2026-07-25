from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.helpers.config import settings


def _normalize_db_url(url: str) -> str:
    """Point Postgres URLs at the installed psycopg (v3) driver.

    Managed hosts (Railway, Heroku, …) hand out `postgres://` or
    `postgresql://` URLs. SQLAlchemy rejects the former and defaults the latter
    to psycopg2 — but this app ships psycopg v3, so force the `+psycopg` dialect.
    """
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _normalize_db_url(settings.DATABASE_URL)

# check_same_thread is a SQLite-only flag; it must not be passed to other
# drivers (e.g. Postgres), so only set it when running on SQLite.
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
