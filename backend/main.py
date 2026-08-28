"""Flask application entry point."""

import os
import sys
import warnings
from dotenv import load_dotenv

# Suppress noisy deprecation & third-party library warnings
warnings.filterwarnings("ignore")

# Force UTF-8 encoding on Windows console output to prevent charmap encoding errors
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Silence Werkzeug development server warning banner
try:
    import werkzeug.serving
    if hasattr(werkzeug.serving, 'cli'):
        werkzeug.serving.cli.show_server_banner = lambda *args: None
except Exception:
    pass

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.llm_factory import LLMFactory
LLMFactory.clear_cache()

from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    # Get configuration
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    print(f"\n{'='*60}")
    print("[*] Multi-AI Agents Backend Server Active")
    print(f"{'='*60}")
    print(f"[+] Server Address: http://{host}:{port}")
    print(f"[+] Debug Mode: {debug}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)
