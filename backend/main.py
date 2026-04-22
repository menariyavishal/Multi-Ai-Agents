"""Flask application entry point."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    # Get configuration
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    print(f"\n{'='*60}")
    print("[*] Starting Multi-AI Agents Backend")
    print(f"{'='*60}")
    print(f"[+] Server: http://{host}:{port}")
    print(f"[+] Debug: {debug}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)
