from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.core.config import settings

# Create SQLAlchemy synchronous engine
# If running with SQLite in tests or PostgreSQL in production/local
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Automatically add sslmode=require and pooler support for remote PostgreSQL (Supabase / Render)
    if "sslmode=" not in settings.DATABASE_URL:
        connect_args["sslmode"] = "require"
    if "pooler.supabase.com" in settings.DATABASE_URL or ":6543" in settings.DATABASE_URL:
        connect_args["prepare_threshold"] = None
    connect_args["connect_timeout"] = 5

# Format DATABASE_URL for psycopg v3 if plain postgresql:// or postgres:// is provided
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+psycopg://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> bool:
    """Verifies database connectivity by executing a lightweight SELECT 1 query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
