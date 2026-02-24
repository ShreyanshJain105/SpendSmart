"""
Centralised error handling.

All HTTP error responses share the same JSON envelope:
    { "error": "<human-readable message>", "code": <http_status_int> }

This consistency is important for the frontend — it never has to guess the
response shape when something goes wrong.
"""
import structlog
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

log = structlog.get_logger()


def register_error_handlers(app):
    """Attach all error handlers to *app*."""

    @app.errorhandler(400)
    def bad_request(exc):
        log.warning("bad_request", error=str(exc))
        return jsonify({"error": "Bad request", "code": 400}), 400

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"error": "Resource not found", "code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"error": "Method not allowed", "code": 405}), 405

    @app.errorhandler(ValidationError)
    def validation_error(exc):
        """Marshmallow raises this when schema.load() fails."""
        log.warning("validation_error", messages=exc.messages)
        return (
            jsonify({"error": "Validation failed", "code": 422, "details": exc.messages}),
            422,
        )

    @app.errorhandler(IntegrityError)
    def integrity_error(exc):
        """SQLAlchemy raises this on unique/FK constraint violations."""
        log.warning("integrity_error", error=str(exc.orig))
        return (
            jsonify({"error": "Conflict: data violates a uniqueness or foreign key constraint", "code": 409}),
            409,
        )

    @app.errorhandler(ValueError)
    def value_error(exc):
        log.warning("value_error", error=str(exc))
        return jsonify({"error": str(exc), "code": 400}), 400

    @app.errorhandler(500)
    def internal_error(exc):
        log.error("internal_server_error", error=str(exc))
        return jsonify({"error": "Internal server error", "code": 500}), 500
