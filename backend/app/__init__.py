"""
Application factory.

Using the factory pattern means:
- Tests can spin up isolated app instances with different configs.
- Extensions are initialised exactly once, with the correct config.
- There are no module-level side-effects that make imports order-dependent.
"""
import structlog
from flask import Flask
from flask_cors import CORS

from config import get_config
from app.database import init_db


def create_app(env: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(get_config(env))

    # Allow the React dev-server (localhost:5173) to reach the API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Structured logging — always log as JSON so log aggregators can parse it
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

    # Database
    init_db(app)

    # Blueprints — thin HTTP layer only, no business logic lives here
    from app.routes.transactions import transactions_bp
    from app.routes.categories import categories_bp
    from app.routes.budgets import budgets_bp
    from app.routes.analytics import analytics_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(budgets_bp, url_prefix="/api/budgets")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # Centralised error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app
