#!/usr/bin/env python
import sqlite3
from pathlib import Path

db_path = Path('data/app.db')

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, email FROM users')
    users = cursor.fetchall()
    
    print('SQLite Users:')
    if users:
        for username, email in users:
            print(f'  {username:20} | {email}')
    else:
        print('  (no users found)')
    
    conn.close()
else:
    print(f'Database not found at {db_path}')
