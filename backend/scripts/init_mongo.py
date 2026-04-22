"""MongoDB database initialization script."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "neuro_agents"


def init_mongo():
    """Initialize MongoDB database with collections and indexes."""
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print(f"✓ Connected to MongoDB: {MONGO_URI}")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        print("   Make sure MongoDB is running. You can start it with:")
        print("   - Docker: docker run -d -p 27017:27017 --name mongodb mongo:6")
        print("   - Or install MongoDB locally: https://www.mongodb.com/try/download/community")
        return False
    
    # Get database
    db = client[DB_NAME]
    
    print(f"\nInitializing MongoDB database: {DB_NAME}")
    
    # 1. Create agent_responses collection
    try:
        if "agent_responses" not in db.list_collection_names():
            db.create_collection(
                "agent_responses",
                validator={
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["session_id", "query", "workflow_state"],
                        "properties": {
                            "session_id": {"bsonType": "string"},
                            "query": {"bsonType": "string"},
                            "workflow_state": {"bsonType": "object"},
                            "final_answer": {"bsonType": "string"},
                            "execution_time_seconds": {"bsonType": "double"},
                            "status": {"bsonType": "string"},
                            "timestamp": {"bsonType": "date"},
                            "user_id": {"bsonType": "string"}
                        }
                    }
                }
            )
            print("✓ Created 'agent_responses' collection with JSON schema validation")
        else:
            print("✓ 'agent_responses' collection already exists")
    except Exception as e:
        print(f"⚠ Could not create collection with schema validation: {str(e)}")
        # Try without schema validation
        if "agent_responses" not in db.list_collection_names():
            db.create_collection("agent_responses")
            print("✓ Created 'agent_responses' collection (without schema)")
    
    # 2. Create TTL index (90 days = 7776000 seconds)
    try:
        db.agent_responses.create_index(
            "timestamp",
            expireAfterSeconds=7776000  # 90 days
        )
        print("✓ Created TTL index on 'timestamp' field (90 days)")
    except Exception as e:
        print(f"⚠ Could not create TTL index: {str(e)}")
    
    # 3. Create other useful indexes
    try:
        db.agent_responses.create_index("session_id")
        db.agent_responses.create_index("user_id")
        db.agent_responses.create_index([("timestamp", -1)])  # Most recent first
        print("✓ Created performance indexes (session_id, user_id, timestamp)")
    except Exception as e:
        print(f"⚠ Could not create indexes: {str(e)}")
    
    # Close connection
    client.close()
    
    print(f"\n✅ MongoDB database initialized: {DB_NAME}")
    return True


if __name__ == "__main__":
    init_mongo()
