"""SQLite database initialization script."""

import sqlite3
import os
from pathlib import Path

# Database path
DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "app.db"


def init_sqlite():
    """Initialize SQLite database with schema."""
    
    # Create data directory if it doesn't exist
    DB_DIR.mkdir(exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("Creating SQLite tables...")
    
    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    print("✓ Created 'users' table")
    
    # 2. API Keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    print("✓ Created 'api_keys' table")
    
    # 3. Query History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            query_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT,
            query_text TEXT NOT NULL,
            query_hash TEXT,
            agent_outputs TEXT,
            status TEXT,
            error_message TEXT,
            execution_time_seconds REAL,
            iterations_used INTEGER,
            quality_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    print("✓ Created 'query_history' table")
    
    # Create indexes for performance
    print("\nCreating indexes...")
    
    # Users indexes
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    print("✓ Created users indexes")
    
    # API Keys indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active)")
    print("✓ Created api_keys indexes")
    
    # Query History indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_history_user_id ON query_history(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_history_session_id ON query_history(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_history_query_hash ON query_history(query_hash)")
    print("✓ Created query_history indexes")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"\n✅ SQLite database initialized: {DB_PATH}")


if __name__ == "__main__":
    init_sqlite()
