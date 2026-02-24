"""
Application configuration.

Database selection:
- Development: Supabase PostgreSQL via DATABASE_URL (falls back to local SQLite)
- Testing:     SQLite in-memory (isolated, fast)
- Production:  Supabase PostgreSQL via DATABASE_URL env variable

For Supabase, set DATABASE_URL in your .env file:
  DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
"""
import os
from dotenv import load_dotenv

# Load .env file if present (local development)
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _engine_options(db_url: str | None) -> dict:
    """
    Return SQLAlchemy engine options appropriate for the database.
    PostgreSQL (Supabase) needs SSL; SQLite does not.
    """
    if db_url and db_url.startswith("postgresql"):
        return {
            "connect_args": {"sslmode": "require"},
            "pool_pre_ping": True,   # verify connection before use
        }
    return {}


class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    # Use Supabase if DATABASE_URL is set, otherwise fall back to local SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'spendsmart_dev.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options(os.environ.get("DATABASE_URL"))


class TestingConfig:
    DEBUG = False
    TESTING = True
    # Always use in-memory SQLite for tests — fast and isolated
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class ProductionConfig:
    DEBUG = False
    TESTING = False
    # Production MUST have DATABASE_URL set (Supabase connection string)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options(os.environ.get("DATABASE_URL"))

    @classmethod
    def validate(cls):
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError(
                "DATABASE_URL environment variable is required in production. "
                "Set it to your Supabase PostgreSQL connection string."
            )


_CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env: str | None = None):
    """Return the config class for the given environment name."""
    env = env or os.environ.get("FLASK_ENV", "development")
    cfg = _CONFIG_MAP.get(env)
    if cfg is None:
        raise ValueError(
            f"Unknown environment '{env}'. "
            f"Valid values: {list(_CONFIG_MAP.keys())}"
        )
    return cfg
