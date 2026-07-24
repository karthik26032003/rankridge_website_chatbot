from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.helpers.config import settings

DATABASE_URL = settings.DATABASE_URL

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
