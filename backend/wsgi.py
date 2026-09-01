"""WSGI entry point for production deployment (Gunicorn)."""

import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

from app import create_app

# Determine environment
ENV = os.getenv("FLASK_ENV", "production")
PORT = int(os.getenv("PORT", os.getenv("FLASK_PORT", 8000)))
HOST = os.getenv("HOST", "0.0.0.0")

# Create app instance
app = create_app(config_name=ENV)

if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=(ENV == "development")
    )

