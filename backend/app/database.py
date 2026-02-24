"""
SQLAlchemy database instance.

Keeping the `db` object here — rather than in `app/__init__.py` — breaks the
circular-import cycle: models import `db`, and the factory imports models.

PostgreSQL / Supabase note
--------------------------
We pass connection parameters as keyword args via a psycopg2 `creator` function
to avoid a Windows-specific issue where psycopg2's DSN-string path cannot
resolve pooler hostnames, even when stdlib sockets can reach them fine.
"""
import os
import urllib.parse

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _pg_creator(url: str):
    """
    Build a no-argument factory that opens a psycopg2 connection with explicit
    keyword arguments rather than a DSN string. This sidesteps a Windows
    client bug where psycopg2's built-in getaddrinfo fails on Supabase pooler
    hostnames despite the host being TCP-reachable.
    """
    import psycopg2
    r = urllib.parse.urlparse(url)
    kw = dict(
        host=r.hostname,
        port=r.port or 5432,
        dbname=r.path.lstrip("/"),
        user=r.username,
        password=urllib.parse.unquote(r.password or ""),
        sslmode="require",
        connect_timeout=15,
    )
    return lambda: psycopg2.connect(**kw)


def init_db(app):
    """Attach SQLAlchemy to *app* and create all tables."""
    db_url: str = app.config.get("SQLALCHEMY_DATABASE_URI", "")

    if db_url.startswith("postgresql"):
        # Inject creator into engine options BEFORE db.init_app so that
        # Flask-SQLAlchemy 3.x picks it up when it builds the engine.
        existing = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            **existing,
            "creator": _pg_creator(db_url),
            "pool_pre_ping": True,
        }

    db.init_app(app)

    with app.app_context():
        # Import models so SQLAlchemy registers their metadata before create_all.
        # Order matters for FK resolution.
        from app.models import category, transaction, budget  # noqa: F401
        db.create_all()
