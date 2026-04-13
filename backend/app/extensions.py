"""
Global extensions and singletons: cache, database clients, etc.
Initialised when the Flask app starts.
"""
import os
import diskcache
from app.config import Config
from app.core.logger import get_logger

logger = get_logger(__name__)

# ---------- Cache (diskcache) ----------
# Use absolute path inside the data directory
CACHE_DIR = os.path.join(os.path.dirname(Config.SQLITE_PATH), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
cache = diskcache.Cache(CACHE_DIR)

# ---------- Database placeholders ----------
# These will be initialised in init_extensions()
db_client = None      # SQLite connection (or SQLAlchemy engine)
mongo_client = None   # MongoDB client

# ---------- Initialisation ----------
def init_extensions():
    """
    Called by the Flask app factory after config is loaded.
    Sets up database connections, etc.
    """
    global db_client, mongo_client
    
    # SQLite initialisation (will be replaced with proper service in Phase 3)
    import sqlite3
    os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True)
    db_client = sqlite3.connect(Config.SQLITE_PATH, check_same_thread=False)
    db_client.row_factory = sqlite3.Row
    logger.info(f"SQLite connection established at {Config.SQLITE_PATH}")
    
    # MongoDB (optional, only if MONGO_URI is set and we are not in a test environment)
    if Config.MONGO_URI and Config.MONGO_URI != "mongodb://localhost:27017/":
        try:
            from pymongo import MongoClient
            mongo_client = MongoClient(Config.MONGO_URI)
            # Test connection
            mongo_client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Continuing without MongoDB.")
            mongo_client = None
    else:
        logger.info("MongoDB disabled (no URI or default localhost).")
    
    logger.info("Extensions initialised successfully")


def close_extensions():
    """Clean up connections on app shutdown."""
    global db_client, mongo_client
    if db_client:
        db_client.close()
        logger.info("SQLite connection closed")
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")
    cache.close()
    logger.info("All extensions closed")
