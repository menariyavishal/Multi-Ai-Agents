#!/usr/bin/env python3
"""
MongoDB Database Scripts - Index and Quick Reference

All MongoDB-related scripts are organized here for easy access.
This folder contains tools for database initialization, seeding, and testing.
"""

import os
import sys


def print_database_scripts_menu():
    """Print available database scripts."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║        MongoDB Database Scripts - Multi-AI Agents              ║
╚════════════════════════════════════════════════════════════════╝

📂 Available Scripts in backend/scripts/

1. 🚀 init_mongo.py
   Initialize MongoDB and create collections/indexes
   
   Usage:
     python init_mongo.py          # Just initialize
     python init_mongo.py --seed   # Initialize + seed data

2. 🌱 seed_mongodb.py
   Create test data for development
   
   Usage:
     python seed_mongodb.py        # Create 3 users with 8 conversations each
     python seed_mongodb.py --clean # Delete all test data

3. 🎬 demo_mongodb_history.py
   Interactive demo showing all MongoDB features
   
   Usage:
     python demo_mongodb_history.py
   
   Demonstrates:
     - Save conversation (query endpoint)
     - Retrieve history
     - Get specific conversation
     - Search conversations
     - Get user statistics

4. 🗄️ init_sqlite.py
   SQLite initialization (optional legacy database)

════════════════════════════════════════════════════════════════

⚡ Quick Start (3 Steps):

Step 1: Initialize MongoDB
   cd backend/scripts
   python init_mongo.py

Step 2: Seed Test Data
   python seed_mongodb.py

Step 3: Run Demo
   python demo_mongodb_history.py

════════════════════════════════════════════════════════════════

📖 Documentation Files (in project root):
   - MONGODB_SETUP.md              Complete setup guide
   - MONGODB_IMPLEMENTATION.md     Technical details

🏗️ Core Database Files (in backend/app/):
   - models/conversation.py        Data models
   - services/database_service.py  MongoDB service
   - routes/v1/history.py          API endpoints
   - routes/v1/query.py            Query endpoint (saves to DB)
   - tests/test_database.py        Database tests

════════════════════════════════════════════════════════════════

🔧 Environment Setup (.env):
   
   MONGODB_URI=mongodb://localhost:27017/multi_ai_agents
   MONGODB_DB_NAME=multi_ai_agents
   
   Or for MongoDB Atlas:
   MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/...

════════════════════════════════════════════════════════════════

💡 Tips:

1. Before running any script, ensure:
   - MongoDB is running (mongod for local)
   - .env is configured with MONGODB_URI
   - Backend environment variables loaded

2. Test connection:
   python -c "from app.services.database_service import get_db_service; print('Connected!' if get_db_service().is_connected() else 'Failed')"

3. View data with MongoDB Compass:
   - Download: https://www.mongodb.com/products/compass
   - Connect to: mongodb://localhost:27017

════════════════════════════════════════════════════════════════

📞 Troubleshooting:

Cannot connect to MongoDB?
   1. Check mongod is running: mongod
   2. Check MONGODB_URI in backend/.env
   3. For Atlas: verify IP whitelist and credentials

Demo script fails?
   1. Start Flask API first: python main.py
   2. MongoDB must be initialized first: python init_mongo.py
   3. Check .env is properly configured

════════════════════════════════════════════════════════════════
    """)


def main():
    """Display menu and usage information."""
    print_database_scripts_menu()


if __name__ == "__main__":
    main()
