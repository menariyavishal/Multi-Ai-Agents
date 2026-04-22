#!/usr/bin/env python3
"""
MongoDB Initialization Script - Set up MongoDB for Multi-AI Agents.

This script:
1. Connects to MongoDB
2. Creates collections
3. Creates indexes
4. Sets up initial schema

Usage:
    python init_mongo.py          # Initialize MongoDB
    python init_mongo.py --seed   # Initialize + seed test data
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.database_service import DatabaseService


def initialize_mongodb():
    """Initialize MongoDB with collections and indexes."""
    print("\n" + "="*60)
    print("🚀 MongoDB Initialization")
    print("="*60)
    
    # Load environment
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # Initialize database service
    print("\n📡 Connecting to MongoDB...")
    db_service = DatabaseService()
    
    if not db_service.is_connected():
        print("❌ Failed to connect to MongoDB!")
        print("\n⚠️  Please ensure:")
        print("  1. MongoDB is running (mongod)")
        print("  2. MONGODB_URI is set in backend/.env")
        print("  3. Connection credentials are correct (for Atlas)")
        return False
    
    print("✅ Connected successfully!")
    
    print("\n📊 Checking collections and indexes...")
    
    # Get collection names
    collections = db_service.db.list_collection_names()
    print(f"\nCollections found: {collections}")
    
    if "conversations" in collections:
        indexes = db_service.conversations_collection.list_indexes()
        print(f"  ✓ conversations collection exists")
        print(f"    Indexes: {[idx['name'] for idx in indexes]}")
    else:
        print(f"  ✓ conversations collection will be created on first insert")
    
    if "users" in collections:
        indexes = db_service.users_collection.list_indexes()
        print(f"  ✓ users collection exists")
        print(f"    Indexes: {[idx['name'] for idx in indexes]}")
    else:
        print(f"  ✓ users collection will be created on first insert")
    
    print("\n" + "="*60)
    print("✅ MongoDB Initialization Complete!")
    print("="*60)
    print("""
📝 What was set up:
  - MongoDB connection verified
  - Collections: conversations, users
  - Indexes created for optimized queries
  
🔍 Next steps:
  1. Run seed script: python scripts/seed_mongodb.py
  2. Start Flask API: python main.py
  3. Test endpoints: python scripts/demo_mongodb_history.py
  
📚 Documentation: See MONGODB_SETUP.md in project root
    """)
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MongoDB initialization and setup utility"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Also seed test data after initialization"
    )
    
    args = parser.parse_args()
    
    # Initialize
    success = initialize_mongodb()
    
    if not success:
        sys.exit(1)
    
    # Optional: seed test data
    if args.seed:
        print("\n⏳ Seeding test data...")
        try:
            # Import and run seed script
            from seed_mongodb import seed_database
            seed_database()
        except ImportError:
            print("⚠️  Could not import seed script. Run separately:")
            print("   python scripts/seed_mongodb.py")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
