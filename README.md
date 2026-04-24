# 🤖 Nueuro-Agents: Industrial-Grade Multi-Agent AI System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-State%20Machine-brightgreen)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?logo=mongodb&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1+-red?logo=flask&logoColor=white)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![License](https://img.shields.io/badge/License-MIT-blue)
![Tests](https://img.shields.io/badge/Tests-201%20Passing-brightgreen)

*A sophisticated multi-agent AI orchestration system processing complex queries through LangGraph state machine with 5 specialized agents*

[🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#-architecture) • [📊 API](#-api-endpoints) • [🧪 Testing](#-testing) • [🐳 Deployment](#-deployment) • [📚 Documentation](#-documentation)

</div>

---

## ✨ Features & Capabilities

### 🧠 Five Specialized AI Agents

| Agent | Temperature | Purpose | LLM Model |
|-------|-------------|---------|-----------|
| **🎯 Planner** | 0.3 | Strategic planning & decomposition | Groq llama-3.3-70b |
| **🔍 Researcher** | 0.2 | Real-time data gathering | Groq llama-3.3-70b |
| **📊 Analyst** | 0.1 | Pattern extraction & insights | Groq llama-3.3-70b |
| **✍️ Writer** | 0.7 | Content synthesis & polish | Groq llama-3.3-70b |
| **✅ Reviewer** | 0.0 | Quality assurance & routing | Groq llama-3.3-70b |

### 🔄 Advanced Orchestration
- ✅ **LangGraph State Machine** - Production-grade workflow engine
- ✅ **Revision Loops** - Reviewer routes back to Writer for improvements
- ✅ **Checkpoint Persistence** - Pause/resume long-running queries
- ✅ **Comprehensive Error Handling** - Graceful failure management
- ✅ **Request Tracing** - End-to-end request tracking

### 💾 Database & Storage
- ✅ **MongoDB** - Primary conversation history & analytics
- ✅ **SQLite** - Development fallback with auto-init
- ✅ **Full CRUD Operations** - Complete data lifecycle management
- ✅ **Full-Text Search** - Query history by keywords
- ✅ **User Management** - Multi-tenant support with API keys

### 🔐 Security & Performance
- ✅ **API Key Authentication** - `X-API-Key` header validation
- ✅ **Token Bucket Rate Limiting** - Configurable request throttling
- ✅ **Request ID Tracing** - Distributed tracing support
- ✅ **Standardized Error Handling** - Consistent error responses
- ✅ **Performance Logging** - Request/response metrics

### 🚀 REST API
- ✅ `POST /api/v1/query` - Synchronous query processing
- ✅ `POST /api/v1/stream` - Server-Sent Events streaming
- ✅ `GET /api/v1/history` - Conversation history (paginated)
- ✅ `GET /api/v1/search` - Full-text search conversations
- ✅ `GET /api/v1/conversation/<id>` - Retrieve specific conversation
- ✅ `GET /api/v1/stats` - User statistics & analytics
- ✅ `POST /api/v1/register` - User registration & API key generation
- ✅ `GET /health` - System health check

---

## 🏗️ Architecture

### 📈 Multi-Agent Pipeline Flow

```
┌────────────────────────────────────────────────────────────┐
│                   USER QUERY INPUT                          │
└────────────────┬───────────────────────────────────────────┘
                 ↓
        ┌────────────────────┐
        │   PLANNER (0.3)    │ → Plan decomposition
        └────────┬───────────┘
                 ↓
        ┌────────────────────┐
        │  RESEARCHER (0.2)  │ → Data gathering
        └────────┬───────────┘
                 ↓
        ┌────────────────────┐
        │   ANALYST (0.1)    │ → Pattern extraction
        └────────┬───────────┘
                 ↓
        ┌────────────────────┐
        │    WRITER (0.7)    │ → Content synthesis
        └────────┬───────────┘
                 ↓
        ┌────────────────────┐
        │   REVIEWER (0.0)   │ → Quality validation
        └─────┬──────┬───────┘
              │      │
         APPROVED  REVISION
              │      │
              ↓      └──────→ [WRITER LOOP]
        ┌──────────┐
        │  FINAL   │
        │ ANSWER   │
        └─────┬────┘
              ↓
    ┌─────────────────────┐
    │ MongoDB + Response  │
    └─────────────────────┘
```

### 🗂️ Directory Structure

```
Nueuro-Agents/
├── 📁 backend/                           # Core application
│   ├── 📁 app/
│   │   ├── 🔄 workflow/                 # LangGraph orchestration
│   │   │   ├── state.py                 # Workflow state definition
│   │   │   ├── graph.py                 # Graph compilation
│   │   │   ├── edges.py                 # Conditional routing
│   │   │   └── checkpointer.py          # State persistence
│   │   ├── 🤖 agents/                   # Five specialized agents
│   │   │   ├── planner.py               # Planning agent
│   │   │   ├── researcher.py            # Research & data gathering
│   │   │   ├── analyst.py               # Analysis & insights
│   │   │   ├── writer.py                # Content synthesis
│   │   │   └── reviewer.py              # Quality assurance
│   │   ├── 💾 services/                 # Business logic layer
│   │   │   ├── workflow_manager.py      # High-level workflow API
│   │   │   ├── database_service.py      # MongoDB & SQLite CRUD
│   │   │   ├── graph_runner.py          # LangGraph execution
│   │   │   └── validation.py            # Input validation
│   │   ├── 🌐 routes/                   # REST API endpoints
│   │   │   ├── health.py                # Health check
│   │   │   └── v1/
│   │   │       ├── query.py             # Query processing
│   │   │       ├── stream_query.py      # SSE streaming
│   │   │       ├── history.py           # History management
│   │   │       ├── search.py            # Search endpoint
│   │   │       └── register.py          # User registration
│   │   ├── 🔒 middleware/               # Security & logging
│   │   │   ├── auth.py                  # API key authentication
│   │   │   ├── rate_limit.py            # Rate limiting
│   │   │   ├── error_handler.py         # Error responses
│   │   │   ├── request_id.py            # Request tracing
│   │   │   └── request_logger.py        # Performance logging
│   │   ├── ⚙️ core/                     # Core utilities
│   │   │   ├── logger.py                # Logging system
│   │   │   ├── llm_factory.py           # LLM creation
│   │   │   ├── constants.py             # Configuration
│   │   │   └── mock_llm.py              # Mock for testing
│   │   ├── 📊 models/                   # Data models
│   │   │   └── conversation.py          # Conversation schema
│   │   ├── 🛡️ exceptions/               # Custom exceptions
│   │   │   └── custom.py                # Exception definitions
│   │   └── 📝 schemas/                  # Request/response schemas
│   │       └── query.py                 # Query validation
│   ├── 🧪 tests/                        # Test suite (201 tests)
│   │   ├── unit/                        # Unit tests (86)
│   │   ├── integration/                 # Integration tests (115)
│   │   ├── conftest.py                  # Test fixtures
│   │   └── TESTING_GUIDE.md             # Test documentation
│   ├── 📄 main.py                       # Development server
│   ├── 🚀 wsgi.py                       # Production entry point
│   ├── 📋 requirements.txt              # Dependencies
│   └── 📋 requirements-dev.txt          # Dev dependencies
├── 📁 frontend/                          # User interface
│   └── 📁 src/
│       ├── index.html                   # Main HTML
│       ├── 🎨 css/style.css             # Styling
│       └── 💻 js/                       # JavaScript logic
├── 🐳 docker/                            # Container config
│   ├── Dockerfile.backend               # Backend image
│   ├── Dockerfile.frontend              # Frontend image
│   └── docker-compose.yml               # Orchestration
├── 📊 logs/                              # Application logs
├── 💾 data/                              # Local data storage
└── 📖 README.md                          # This file
```

---

## 🚀 Quick Start

### 📋 Prerequisites

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime environment |
| Git | 2.0+ | Version control |
| MongoDB | 5.0+ | Optional (production) |
| Docker | 20.0+ | Optional (containers) |

### 🔧 Installation (5 minutes)

```bash
# 1️⃣ Clone repository
git clone https://github.com/menariyavishal/Multi-Ai-Agents.git
cd Multi-Ai-Agents

# 2️⃣ Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r backend/requirements.txt

# 4️⃣ Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 5️⃣ Initialize databases
python backend/scripts/init_sqlite.py
python backend/scripts/init_mongo.py  # Optional

# 6️⃣ Verify installation
python backend/verify_installation.py
```

### 🎯 Running the Application

#### Development Mode
```bash
cd backend
python main.py
# 🌐 Access: http://localhost:5000
# 📊 Monitor: Check logs/ directory
```

#### Production Mode
```bash
cd backend
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app
# 🌐 Access: http://localhost:8000
# 📊 Workers: 2 processes
```

#### Docker Deployment
```bash
docker-compose up --build
# 🌐 Backend: http://localhost:8000
# 🌐 Frontend: http://localhost:80
# 🗄️ MongoDB: localhost:27017
```

---

## 📊 API Endpoints

### Query Processing

#### Synchronous Processing
```bash
curl -X POST http://localhost:5000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What are AI trends in 2024?",
    "user_id": "user123",
    "max_iterations": 3
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "conv-12345",
  "result": {
    "query": "What are AI trends in 2024?",
    "status": "approved",
    "iterations_used": 2,
    "execution_time_seconds": 45.3,
    "plan": "...",
    "research_summary": "...",
    "analysis": {...},
    "final_answer": "..."
  }
}
```

#### Streaming (Server-Sent Events)
```bash
curl -X POST http://localhost:5000/api/v1/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "...","max_iterations": 3}'

# Stream output:
data: {"type":"workflow_start","session_id":"..."}
data: {"type":"agent_complete","agent":"planner"}
data: {"type":"agent_complete","agent":"researcher"}
data: {"type":"agent_complete","agent":"analyst"}
data: {"type":"agent_complete","agent":"writer"}
data: {"type":"agent_complete","agent":"reviewer"}
data: {"type":"workflow_complete","result":{...}}
```

### History & Search

#### Get Conversation History
```bash
curl -X GET "http://localhost:5000/api/v1/history?limit=10&offset=0" \
  -H "X-API-Key: your-api-key"
```

#### Search Conversations
```bash
curl -X GET "http://localhost:5000/api/v1/search?q=AI%20trends&limit=5" \
  -H "X-API-Key: your-api-key"
```

#### Get Specific Conversation
```bash
curl -X GET "http://localhost:5000/api/v1/conversation/conv-12345" \
  -H "X-API-Key: your-api-key"
```

### User Management

#### Register User
```bash
curl -X POST http://localhost:5000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'
```

**Response:**
```json
{
  "user_id": "user-12345",
  "api_key": "sk_live_abc123xyz...",
  "created_at": "2024-04-25T10:30:00Z"
}
```

---

## ⚙️ Configuration

### Environment Variables

#### Required
```env
# LLM Provider
GROQ_API_KEY=gsk_...           # Groq API key
```

#### Optional - Data Sources
```env
# Real-time data
OPENWEATHER_API_KEY=...         # Weather data
NEWS_API_KEY=...                # News articles
ALPHA_VANTAGE_API_KEY=...       # Stock market data
GOOGLE_SEARCH_API_KEY=...       # Google Custom Search
GOOGLE_SEARCH_ENGINE_ID=...     # CSE ID
```

#### Database Configuration
```env
# SQLite (default)
SQLITE_PATH=data/nueuro_agents.db

# MongoDB (production)
MONGO_URI=mongodb://localhost:27017/nueuro_agents
MONGODB_DATABASE=nueuro_agents
```

#### Flask Settings
```env
FLASK_ENV=development           # development | production
DEBUG=True                       # Enable debug mode
SECRET_KEY=your-secret-key-here # Session encryption
```

#### Rate Limiting
```env
RATELIMIT_REQUESTS=100          # Requests per window
RATELIMIT_WINDOW=3600           # Time window (seconds)
```

#### Workflow Configuration
```env
AGENT_TIMEOUT=25                # Agent execution timeout
GRAPH_TIMEOUT=30                # Full workflow timeout
MAX_ITERATIONS=3                # Maximum revision loops
```

---

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Test Categories

```bash
# Unit tests only (86 tests)
pytest tests/unit/ -v

# Integration tests only (115 tests)  
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_planner_agent.py -v

# With Groq API integration
pytest -m groq -v

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Test Results Summary

| Category | Tests | Status | Coverage |
|----------|-------|--------|----------|
| Unit Tests | 86 | ✅ Passing | 92% |
| Integration Tests | 115 | ✅ Passing | 88% |
| **Total** | **201** | **✅ Passing** | **90%** |

---

## 🐳 Deployment

### Docker Compose (Recommended)
```bash
docker-compose up --build

# Services running:
# ✅ Backend: http://localhost:8000
# ✅ Frontend: http://localhost:80
# ✅ MongoDB: localhost:27017
```

### Environment Variables (Production)
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=strong-random-secret-key-here

# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/nueuro_agents

# Rate Limiting (higher for production)
RATELIMIT_REQUESTS=1000
RATELIMIT_WINDOW=3600

# API Keys
GROQ_API_KEY=your_production_key
```

### Production Checklist
- [ ] Set `DEBUG=False` in environment
- [ ] Use strong `SECRET_KEY`
- [ ] Configure MongoDB with authentication
- [ ] Setup MongoDB backups
- [ ] Enable request logging
- [ ] Configure monitoring alerts
- [ ] Setup CI/CD pipeline
- [ ] Enable SSL/TLS certificates
- [ ] Configure rate limits appropriately
- [ ] Setup automated testing

---

## 📈 Roadmap

### Phase 8 ✅ Complete
- [x] All 5 agents implemented
- [x] LangGraph workflow
- [x] 10 REST API endpoints
- [x] MongoDB + SQLite integration
- [x] Authentication & rate limiting
- [x] 201 comprehensive tests
- [x] Production-ready backend

### Phase 9 🚀 In Progress
- [ ] Frontend UI completion
- [ ] Real-time analytics dashboard
- [ ] Advanced search features
- [ ] Custom agent creation
- [ ] OpenAPI documentation

### Phase 10 📊 Planned
- [ ] Redis caching layer
- [ ] WebSocket support
- [ ] Advanced monitoring
- [ ] Performance optimization
- [ ] Enterprise features

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[TESTING_GUIDE.md](backend/tests/TESTING_GUIDE.md)** | Comprehensive testing guide |
| **[BACKEND_AUDIT_REPORT.md](backend/BACKEND_AUDIT_REPORT.md)** | File inventory & checklist |
| **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** | System architecture |
| **[CLAUDE.md](CLAUDE.md)** | Development guidelines |

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **LLM** | Groq | Latest | AI backbone |
| **Orchestration** | LangGraph | 0.1.0+ | State machine |
| **Framework** | Flask | 3.1+ | REST API |
| **Databases** | MongoDB | 5.0+ | Production data |
| **Fallback** | SQLite | 3.40+ | Development |
| **Testing** | Pytest | 7.0+ | Test framework |
| **Container** | Docker | 20.0+ | Deployment |
| **Frontend** | HTML/CSS/JS | ES6+ | UI |

---

## 📝 License

MIT License © 2024 Nueuro-Agents Team

See [LICENSE](LICENSE) for details.

---

## 👥 Contributing

### How to Contribute

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** Pull Request

### Code Standards
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Ensure all tests pass
- Add type hints

---

## 📞 Support & Contact

| Channel | Link |
|---------|------|
| 🐛 **Report Bugs** | [GitHub Issues](https://github.com/menariyavishal/Multi-Ai-Agents/issues) |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/menariyavishal/Multi-Ai-Agents/discussions) |
| 📧 **Email** | contact@example.com |
| 🌐 **Website** | https://nueuro-agents.io |

---

<div align="center">

### 🌟 Show Your Support

If this project helped you, please give it a star! ⭐

**Built with ❤️ by the Nueuro-Agents Team**

![Built with Love](https://img.shields.io/badge/Built%20with-❤️-red)
![Python Powered](https://img.shields.io/badge/Powered%20by-Python-blue?logo=python&logoColor=white)

[Back to Top](#-nueuro-agents-industrial-grade-multi-agent-ai-system)

</div>

