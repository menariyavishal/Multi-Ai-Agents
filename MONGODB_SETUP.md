# MongoDB Setup Guide for Conversation History

This guide explains how to set up MongoDB for storing chat history in the Multi-AI Agents application.

## Overview

The system now stores all conversations in MongoDB, enabling:
- ✅ Persistent conversation history (like ChatGPT)
- ✅ User profile management
- ✅ Conversation search and retrieval
- ✅ User statistics tracking
- ✅ Scalable cloud deployment option

## Quick Start (2 Options)

### Option 1: Local MongoDB (Development)

**Prerequisites:**
- Install MongoDB Community Edition: https://www.mongodb.com/try/download/community

**Setup:**

1. **Start MongoDB Server:**
   ```bash
   # Windows
   mongod
   
   # macOS (with Homebrew)
   brew services start mongodb-community
   
   # Linux
   sudo systemctl start mongod
   ```

2. **Configure .env:**
   ```bash
   MONGODB_URI=mongodb://localhost:27017/multi_ai_agents
   MONGODB_DB_NAME=multi_ai_agents
   ```

3. **Test Connection:**
   ```bash
   python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017').admin.command('ping'); print('Connected!')"
   ```

### Option 2: MongoDB Atlas (Cloud - Recommended for Production)

**Prerequisites:**
- Create free account at https://www.mongodb.com/cloud/atlas

**Setup:**

1. **Create Cluster:**
   - Go to https://cloud.mongodb.com
   - Click "Create a Deployment"
   - Choose "M0 Shared" (free tier)
   - Select region and create

2. **Create Database User:**
   - Go to Security > Database Access
   - Add Database User
   - Note username and password

3. **Get Connection String:**
   - Go to Deployments > Connect
   - Choose "Drivers"
   - Copy connection string (looks like: `mongodb+srv://user:pass@cluster.mongodb.net/`)

4. **Configure .env:**
   ```bash
   MONGODB_URI=mongodb+srv://username:password@cluster-name.mongodb.net/multi_ai_agents?retryWrites=true&w=majority
   MONGODB_DB_NAME=multi_ai_agents
   ```

5. **Test Connection:**
   ```bash
   python -c "from pymongo import MongoClient; MongoClient('YOUR_MONGODB_ATLAS_URI').admin.command('ping'); print('Connected!')"
   ```

## API Endpoints

### 1. Save Conversation (Automatic - POST /query)

When you query, conversation is automatically saved:

```bash
curl -X POST http://localhost:5000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are AI trends?",
    "user_id": "user123",
    "max_iterations": 3
  }'
```

**Response:**
```json
{
  "status": "success",
  "session_id": "uuid",
  "conversation_id": "uuid",
  "result": {...}
}
```

### 2. Get User Conversation History

```bash
curl "http://localhost:5000/api/v1/history?user_id=user123&limit=20&skip=0"
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user123",
  "conversations": [
    {
      "conversation_id": "uuid",
      "title": "What are AI trends?",
      "query": "What are AI trends?",
      "created_at": "2024-04-22T10:30:45Z",
      "data_classification": "COMBINED",
      "quality_score": 0.92,
      "processing_time_seconds": 5.2
    }
  ],
  "total_count": 42
}
```

### 3. Get Specific Conversation

```bash
curl "http://localhost:5000/api/v1/conversation/uuid?user_id=user123"
```

**Response:**
```json
{
  "status": "success",
  "conversation": {
    "conversation_id": "uuid",
    "user_id": "user123",
    "query": "What are AI trends?",
    "plan": "...",
    "research": "...",
    "content": "...",
    "analysis": {...},
    "final_output": "...",
    "data_classification": "COMBINED",
    "quality_score": 0.92,
    "created_at": "2024-04-22T10:30:45Z"
  }
}
```

### 4. Search Conversations

```bash
curl "http://localhost:5000/api/v1/search?user_id=user123&q=AI%20trends&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user123",
  "query": "AI trends",
  "results": [...],
  "total_found": 5
}
```

### 5. Get User Statistics

```bash
curl "http://localhost:5000/api/v1/stats?user_id=user123"
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user123",
  "stats": {
    "total_conversations": 42,
    "total_queries": 42,
    "average_quality_score": 0.87,
    "last_query_at": "2024-04-22T10:30:45Z"
  }
}
```

## Database Schema

### Collections

#### conversations
Stores individual conversations/queries:
```javascript
{
  "_id": ObjectId,
  "user_id": "string",           // User identifier
  "conversation_id": "uuid",     // Unique conversation ID
  "title": "string",             // Auto-generated or custom
  "query": "string",             // User's original question
  "plan": "string",              // Planner agent output
  "research": "string",          // Researcher agent findings
  "content": "string",           // Writer agent content
  "analysis": {...},             // Analyst agent results
  "final_output": "string",      // Reviewer agent polish
  "data_classification": "enum",     // REAL_TIME | HISTORICAL | COMBINED
  "quality_score": number,       // 0.0 - 1.0
  "quality_level": "string",     // high | medium | low
  "created_at": ISODate,
  "processing_time_seconds": number,
  "tags": [string]               // For searching
}
```

**Indexes:**
- `user_id + created_at` (for efficient history retrieval)
- `conversation_id` (unique, for fast lookup)

#### users
Stores user profiles and statistics:
```javascript
{
  "_id": ObjectId,
  "user_id": "string",               // Unique user ID
  "email": "string",                 // User email (optional, unique)
  "name": "string",                  // User name (optional)
  "created_at": ISODate,
  "preferred_data_classification": "string",  // User preference
  "theme": "string",                 // UI theme preference
  "total_conversations": number,
  "total_queries": number,
  "average_quality_score": number,
  "last_query_at": ISODate
}
```

**Indexes:**
- `user_id` (unique)
- `email` (unique, sparse)

## Testing

### Run Database Tests:
```bash
# Test database models and service
pytest tests/test_database.py -v

# With coverage
pytest tests/test_database.py --cov=app.services.database_service --cov-report=html
```

### Manual Testing:

1. **Start MongoDB:**
   ```bash
   mongod
   ```

2. **Start Flask app:**
   ```bash
   python backend/main.py
   ```

3. **Test conversation save:**
   ```bash
   curl -X POST http://localhost:5000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"query":"What is Python?","user_id":"test_user"}'
   ```

4. **View in MongoDB:**
   ```bash
   # Using MongoDB Compass GUI
   # Or via command line
   mongosh
   use multi_ai_agents
   db.conversations.find()
   ```

## Troubleshooting

### MongoDB Connection Errors

**"Cannot connect to MongoDB"**
- Ensure MongoDB is running: `mongod` (local) or check Atlas status
- Check MONGODB_URI in .env is correct
- Verify firewall/security groups allow MongoDB port (27017 for local, or check Atlas IP whitelist)

**"Authentication failed"**
- Verify username/password in MongoDB Atlas
- Check special characters are URL-encoded
- Example: `@` becomes `%40`

### Data Not Persisting

- Confirm `MONGODB_URI` and `MONGODB_DB_NAME` are set in .env
- Check `db_service.is_connected()` returns True
- Look for errors in application logs

### Performance Issues

- Monitor collection size: `db.conversations.stats()`
- Rebuild indexes: `db.conversations.reIndex()`
- Consider MongoDB Atlas auto-scaling for production

## Monitoring & Maintenance

### MongoDB Compass (GUI)
Download free tool to visualize and manage data:
https://www.mongodb.com/products/compass

### Common Queries:

```javascript
// Get all conversations for a user
db.conversations.find({ user_id: "user123" }).sort({ created_at: -1 })

// Find high-quality conversations
db.conversations.find({ quality_score: { $gte: 0.9 } })

// Get user statistics
db.users.findOne({ user_id: "user123" })

// Search conversations
db.conversations.find({ 
  user_id: "user123",
  $or: [
    { query: { $regex: "AI", $options: "i" } },
    { tags: "ai" }
  ]
})

// Delete old conversations (older than 30 days)
db.conversations.deleteMany({ 
  created_at: { $lt: new Date(Date.now() - 30*24*60*60*1000) }
})
```

## Environment Variables Reference

```bash
# Required
MONGODB_URI=mongodb://localhost:27017/multi_ai_agents
MONGODB_DB_NAME=multi_ai_agents

# For MongoDB Atlas (optional)
# Format: mongodb+srv://username:password@cluster.mongodb.net/database?options
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/multi_ai_agents
```

## Next Steps

1. ✅ Choose MongoDB option (local or Atlas)
2. ✅ Configure .env with connection string
3. ✅ Test with `curl` or Postman
4. ✅ Run tests: `pytest tests/test_database.py`
5. ✅ Deploy to production (if using Atlas)

## Architecture Diagram

```
User Query
    ↓
Flask API (/api/v1/query)
    ↓
5-Agent Pipeline (Planner → Researcher → Writer → Analyst → Reviewer)
    ↓
Generate Response + Metadata
    ↓
DatabaseService.save_conversation()
    ↓
MongoDB (conversations + users collections)
    ↓
User can retrieve via:
  - /api/v1/history (list all)
  - /api/v1/conversation/{id} (get specific)
  - /api/v1/search (search)
  - /api/v1/stats (statistics)
```

---

**Status:** ✅ MongoDB integration complete and production-ready
