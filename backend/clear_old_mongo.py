from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/multi_ai_agents", serverSelectionTimeoutMS=2000)
    db = client.multi_ai_agents
    deleted_convs = db.conversations.delete_many({})
    print(f"Purged {deleted_convs.deleted_count} old test conversations from MongoDB.")
except Exception as e:
    print(f"MongoDB purge error: {e}")
