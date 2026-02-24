"""
Pytest configuration and shared fixtures.

All fixtures use the 'testing' config which uses SQLite in-memory —
each test run gets a fresh, isolated database.
"""
import pytest

from app import create_app
from app.database import db as _db


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing."""
    flask_app = create_app("testing")
    return flask_app


@pytest.fixture(scope="function")
def db(app):
    """
    Yield the db instance with all tables created, then drop everything
    after the test so the next test starts clean.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    """Flask test client bound to the in-memory database."""
    with app.test_client() as c:
        yield c


@pytest.fixture
def seed_category(db, app):
    """Create and return a 'Groceries' category for use in tests."""
    from app.models.category import Category
    with app.app_context():
        cat = Category(name="Groceries", icon="🛒", color="#22c55e")
        db.session.add(cat)
        db.session.commit()
        db.session.refresh(cat)
        return cat
