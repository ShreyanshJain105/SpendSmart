"""Entry-point for local development.

Production deployments should use a WSGI server (gunicorn, etc.) pointing
at `app:create_app()` directly.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
