"""WSGI entry point for production deployment (Gunicorn)."""

import os
from app import create_app

# Determine environment
ENV = os.getenv("FLASK_ENV", "development")

# Create app
app = create_app(config_name=ENV)

if __name__ == "__main__":
    # Development server only - use Gunicorn in production
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=(ENV == "development")
    )
