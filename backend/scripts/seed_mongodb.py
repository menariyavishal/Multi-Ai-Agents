#!/usr/bin/env python3
"""
MongoDB seed script - Creates test data for development and testing.

Usage:
    python seed_mongodb.py          # Create test data
    python seed_mongodb.py --clean  # Clear all data
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__) + '/..')

from app.models.conversation import Conversation, UserProfile
from app.services.database_service import DatabaseService


def get_sample_conversations(user_id: str, count: int = 5) -> list:
    """Generate sample conversations for testing."""
    
    sample_queries = [
        "What are the latest AI trends in 2024?",
        "How does machine learning work?",
        "What is the weather forecast for tomorrow?",
        "Tell me about quantum computing",
        "How can I learn Python programming?",
        "What are the top AI companies?",
        "Explain neural networks simply",
        "What is the current BTC price?",
        "How does blockchain technology work?",
        "What are the best AI tools for productivity?"
    ]
    
    data_classifications = ["REAL_TIME", "HISTORICAL", "COMBINED"]
    quality_levels = ["low", "medium", "high"]
    
    conversations = []
    
    for i in range(count):
        query = sample_queries[i % len(sample_queries)]
        
        conv = Conversation(
            user_id=user_id,
            query=query,
            title=f"{query[:50]}...",
            plan=f"Analyze and research: {query}",
            research=f"Gathered data from multiple sources about: {query}. "
                    f"Found current trends, historical context, and expert opinions.",
            content=f"Comprehensive analysis of {query}. "
                   f"This includes multiple perspectives and recent developments.",
            analysis={
                "key_findings": [
                    "Finding 1: ...",
                    "Finding 2: ...",
                    "Finding 3: ..."
                ],
                "data_sources": 4,
                "credibility": 0.9
            },
            final_output=f"Final polished response about {query}. "
                        f"This has been reviewed and validated for accuracy.",
            data_classification=random.choice(data_classifications),
            quality_score=round(random.uniform(0.65, 0.99), 2),
            quality_level=random.choice(quality_levels),
            processing_time_seconds=round(random.uniform(2.5, 8.5), 1),
            tags=extract_tags(query)
        )
        
        # Set different creation times (spread over past 30 days)
        days_ago = random.randint(0, 29)
        hours_ago = random.randint(0, 23)
        conv.created_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        
        conversations.append(conv)
    
    return conversations


def extract_tags(query: str) -> list:
    """Extract tags from query."""
    keywords = [
        "weather", "news", "stock", "finance", "ai", "python", "javascript",
        "current", "today", "tomorrow", "trend", "analysis", "price", "rate",
        "ml", "blockchain", "crypto", "learning", "productivity"
    ]
    
    query_lower = query.lower()
    tags = [kw for kw in keywords if kw in query_lower]
    return tags[:5]


def seed_database():
    """Seed MongoDB with test data."""
    print("\n" + "="*60)
    print("🌱 MongoDB Seed Data Script")
    print("="*60)
    
    # Load environment
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # Initialize database service
    print("\n📡 Connecting to MongoDB...")
    db_service = DatabaseService()
    
    if not db_service.is_connected():
        print("❌ Failed to connect to MongoDB!")
        print("\n⚠️  Please ensure:")
        print("  1. MongoDB is running")
        print("  2. MONGODB_URI is set in backend/.env")
        print("  3. Connection credentials are correct (for Atlas)")
        return False
    
    print("✅ Connected successfully!")
    
    # Create test users and conversations
    test_users = [
        ("user_demo_001", "demo1@example.com", "Demo User 1"),
        ("user_demo_002", "demo2@example.com", "Demo User 2"),
        ("user_demo_003", "demo3@example.com", "Demo User 3"),
    ]
    
    total_conversations = 0
    
    for user_id, email, name in test_users:
        print(f"\n👤 Creating data for user: {user_id}")
        
        # Create user profile
        user = UserProfile(
            user_id=user_id,
            email=email,
            name=name,
            total_conversations=0,
            total_queries=0,
            average_quality_score=0.0
        )
        
        db_service.create_user(user)
        print(f"   ✓ User profile created")
        
        # Create conversations
        conversations = get_sample_conversations(user_id, count=8)
        
        for conv in conversations:
            success = db_service.save_conversation(conv)
            if success:
                total_conversations += 1
        
        print(f"   ✓ Created {len(conversations)} conversations")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ Seeding Complete!")
    print("="*60)
    print(f"""
📊 Summary:
  - Users created: {len(test_users)}
  - Total conversations: {total_conversations}
  
💾 Test Data Ready!

🔍 Query it with:
  
  # Get history for user 1
  curl "http://localhost:5000/api/v1/history?user_id=user_demo_001"
  
  # Get stats
  curl "http://localhost:5000/api/v1/stats?user_id=user_demo_001"
  
  # Search conversations
  curl "http://localhost:5000/api/v1/search?user_id=user_demo_001&q=AI"

📚 MongoDB Compass:
  View data at mongodb://localhost:27017 (if using local MongoDB)
  Or via MongoDB Atlas dashboard
    """)
    
    return True


def clean_database():
    """Delete all test data from MongoDB."""
    print("\n" + "="*60)
    print("🗑️  MongoDB Clean Script")
    print("="*60)
    
    response = input("\n⚠️  WARNING: This will DELETE ALL conversation and user data!\n"
                    "Are you sure? (type 'yes' to confirm): ").strip().lower()
    
    if response != "yes":
        print("❌ Aborted.")
        return False
    
    # Load environment
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # Initialize database service
    print("\n📡 Connecting to MongoDB...")
    db_service = DatabaseService()
    
    if not db_service.is_connected():
        print("❌ Failed to connect to MongoDB!")
        return False
    
    print("✅ Connected successfully!")
    
    try:
        # Delete collections
        print("\n🗑️  Deleting collections...")
        
        conv_count = db_service.conversations_collection.delete_many({})
        print(f"   ✓ Deleted {conv_count.deleted_count} conversations")
        
        user_count = db_service.users_collection.delete_many({})
        print(f"   ✓ Deleted {user_count.deleted_count} users")
        
        print("\n✅ All data cleaned!")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {str(e)}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MongoDB seed/clean utility for Multi-AI Agents"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete all data from MongoDB instead of seeding"
    )
    
    args = parser.parse_args()
    
    if args.clean:
        success = clean_database()
    else:
        success = seed_database()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
