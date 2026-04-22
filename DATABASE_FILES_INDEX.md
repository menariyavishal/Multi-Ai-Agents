# MongoDB Database Files Organization

**Last Updated:** April 22, 2024

---

## 📂 Complete File Structure

All MongoDB and database-related files are organized in logical locations for easy access and maintenance.

### **Scripts Folder** (`backend/scripts/`)
Quick access to all database utilities:

```
backend/scripts/
├── init_mongo.py                    ✅ Initialize MongoDB
├── seed_mongodb.py                  ✅ Seed test data
├── demo_mongodb_history.py          ✅ Interactive demo
├── init_sqlite.py                   (Legacy)
└── README.md                        📖 Quick reference guide
```

**What they do:**
- `init_mongo.py` - Connect to MongoDB, create collections and indexes
- `seed_mongodb.py` - Generate 3 test users with 8 conversations each
- `demo_mongodb_history.py` - Interactive demo of all features

---

### **Core Database Code** (`backend/app/`)

#### **Models** (`app/models/`)
```
backend/app/models/
├── conversation.py                  📋 Pydantic models:
│                                     - Conversation
│                                     - UserProfile
│                                     - ConversationSummary
│                                     - ConversationMessage
└── __init__.py                      🔗 Export models
```

#### **Services** (`app/services/`)
```
backend/app/services/
├── database_service.py              💾 MongoDB CRUD operations:
│                                     - save_conversation()
│                                     - get_conversation()
│                                     - get_user_conversations()
│                                     - search_conversations()
│                                     - create_user() / get_user()
│                                     - get_stats()
├── db_service.py                    (Backup/alternate name)
└── __init__.py                      🔗 Export services
```

#### **Routes** (`app/routes/v1/`)
```
backend/app/routes/v1/
├── query.py                         📤 POST /api/v1/query
│                                     - Now saves to MongoDB
│                                     - Returns conversation_id
│
└── history.py                       📥 5 New endpoints:
                                      1. GET /api/v1/history (list all)
                                      2. GET /api/v1/conversation/{id}
                                      3. GET /api/v1/search
                                      4. GET /api/v1/stats
                                      5. (Preserved) Checkpoint endpoints
```

#### **Tests** (`backend/tests/`)
```
backend/tests/
├── test_database.py                 ✅ 20+ test cases:
│                                     - Model tests
│                                     - Service tests
│                                     - Integration tests
└── (other test files)
```

---

### **Documentation** (Root Directory)

```
/
├── MONGODB_SETUP.md                 📖 Complete setup guide
│                                     - Local MongoDB setup
│                                     - MongoDB Atlas setup
│                                     - All endpoint examples
│                                     - Troubleshooting
│
├── MONGODB_IMPLEMENTATION.md        🔧 Technical details
│                                     - Architecture
│                                     - Database schema
│                                     - Integration points
│                                     - Deployment info
│
└── DATABASE_FILES_INDEX.md          📂 This file (reference)
```

---

### **Configuration** (`backend/`)

```
backend/
├── .env                             🔐 Environment variables:
│                                     - MONGODB_URI
│                                     - MONGODB_DB_NAME
│
├── .env.example                     📋 Template (safe for GitHub)
│
└── requirements.txt                 📦 Dependencies:
                                      - pymongo>=4.0.0
                                      - All others unchanged
```

---

## 🚀 Quick Access Guide

### **To Initialize MongoDB:**
```bash
cd backend/scripts
python init_mongo.py
```

### **To Seed Test Data:**
```bash
cd backend/scripts
python seed_mongodb.py
```

### **To See Interactive Demo:**
```bash
cd backend/scripts
python demo_mongodb_history.py
```

### **To Run Database Tests:**
```bash
cd backend
pytest tests/test_database.py -v
```

### **To View MongoDB Data:**
- Use MongoDB Compass GUI
- Or use MongoDB Atlas dashboard (if cloud)

---

## 📊 File Count Summary

| Category | Count | Location |
|----------|-------|----------|
| **Scripts** | 3 | `backend/scripts/` |
| **Models** | 2 | `backend/app/models/` |
| **Services** | 1 | `backend/app/services/` |
| **Routes** | 2 (updated) | `backend/app/routes/v1/` |
| **Tests** | 1 | `backend/tests/` |
| **Documentation** | 3 | `root/` |
| **Config** | 2 (updated) | `backend/` |
| **Total** | **14** | Various |

---

## 🔄 File Dependencies

```
┌─────────────────────────────────────────────┐
│        API Endpoints                         │
│  (routes/v1/query.py)                        │
│  (routes/v1/history.py)                      │
└────────────────┬────────────────────────────┘
                 │ calls
                 ↓
┌─────────────────────────────────────────────┐
│        DatabaseService                       │
│  (services/database_service.py)              │
└────────────────┬────────────────────────────┘
                 │ uses
                 ↓
┌─────────────────────────────────────────────┐
│        Pydantic Models                       │
│  (models/conversation.py)                    │
└─────────────────────────────────────────────┘
                 │ stored in
                 ↓
┌─────────────────────────────────────────────┐
│        MongoDB Collections                   │
│  - conversations                             │
│  - users                                     │
└─────────────────────────────────────────────┘
```

---

## 🔐 What Each File Contains

### **Models** (`conversation.py`)
- `Conversation` - Full conversation document
- `UserProfile` - User profile and statistics
- `ConversationSummary` - Summary for list views
- `ConversationMessage` - Individual message

### **Services** (`database_service.py`)
**CRUD Operations:**
- `save_conversation()` - Store conversation
- `get_conversation()` - Retrieve by ID
- `get_user_conversations()` - Get user's history
- `search_conversations()` - Full-text search
- `create_user()` - Create user profile
- `get_user()` - Retrieve user profile
- `get_stats()` - Get user statistics
- `_update_user_stats()` - Update after query
- `_create_indexes()` - Create MongoDB indexes

### **Routes** (`query.py`, `history.py`)
**New Endpoints:**
1. `POST /api/v1/query` - Query + auto-save (updated)
2. `GET /api/v1/history` - Get conversation list
3. `GET /api/v1/conversation/{id}` - Get full conversation
4. `GET /api/v1/search` - Search conversations
5. `GET /api/v1/stats` - Get user statistics

### **Scripts**
- `init_mongo.py` - Initialize and verify MongoDB
- `seed_mongodb.py` - Create test data or clean
- `demo_mongodb_history.py` - Interactive feature demo

---

## ✅ Verification Checklist

After implementation, verify:

- [x] All files created in correct locations
- [x] Models properly imported in app
- [x] Services properly imported in routes
- [x] API endpoints work with user_id
- [x] MongoDB connection configured in .env
- [x] Test database.py passes
- [x] Demo script runs without errors
- [x] Seed script creates test data
- [x] Documentation complete and clear

---

## 📝 File Sizes (Approximate)

| File | Lines | Size |
|------|-------|------|
| conversation.py | 70 | 2.5 KB |
| database_service.py | 350 | 11 KB |
| query.py (updated) | 200 | 7 KB |
| history.py (updated) | 400 | 15 KB |
| test_database.py | 300 | 11 KB |
| init_mongo.py | 100 | 3.5 KB |
| seed_mongodb.py | 250 | 8 KB |
| demo_mongodb_history.py | 250 | 8 KB |
| **TOTAL** | **1,920** | **65 KB** |

---

## 🎯 Next Steps

1. **Review all files** in their organized locations
2. **Run initialization:** `python backend/scripts/init_mongo.py`
3. **Seed test data:** `python backend/scripts/seed_mongodb.py`
4. **Test endpoints:** `python backend/scripts/demo_mongodb_history.py`
5. **Review documentation:** Read MONGODB_SETUP.md and MONGODB_IMPLEMENTATION.md
6. **Run tests:** `pytest backend/tests/test_database.py`
7. **Push to GitHub** when ready

---

## 📖 Documentation References

| Document | Purpose |
|----------|---------|
| **MONGODB_SETUP.md** | User-focused setup guide with examples |
| **MONGODB_IMPLEMENTATION.md** | Technical implementation details |
| **DATABASE_FILES_INDEX.md** | This file - file organization reference |
| **backend/scripts/README.md** | Quick reference for scripts |

---

## 🔗 Important Links

- **MongoDB Setup:** [MONGODB_SETUP.md](../MONGODB_SETUP.md)
- **Implementation Details:** [MONGODB_IMPLEMENTATION.md](../MONGODB_IMPLEMENTATION.md)
- **Scripts Reference:** [backend/scripts/README.md](../backend/scripts/README.md)
- **Test File:** [backend/tests/test_database.py](../backend/tests/test_database.py)

---

**Status:** ✅ All files organized and production-ready

**Benefit:** Clear, organized database system easy to understand, maintain, and extend.
