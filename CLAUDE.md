# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nueuro-Agents** is an industrial-grade multi-agent AI system that processes complex queries through a LangGraph state machine pipeline of five specialized AI agents:

1. **Planner** - Decomposes queries into actionable steps (Groq, temp 0.3)
2. **Researcher** - Gathers real-world data via web search/databases (Groq, temp 0.2)
3. **Analyst** - Extracts patterns and insights (Groq, temp 0.1)
4. **Writer** - Synthesizes analysis into polished output (Groq, temp 0.7)
5. **Reviewer** - Quality assurance, can route back for revisions (Groq, temp 0.0)

## Quick Commands

### Development Server
```bash
cd backend
python main.py              # Flask dev server at http://localhost:5000
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app  # Production server
```

### Testing
```bash
cd backend
pytest tests/ -v --cov=app          # Run all tests
pytest tests/test_planner_agent.py -v  # Specific test file
pytest -m integration               # Integration tests only
```

### Code Quality
```bash
cd backend
black app/ tests/        # Format code
isort app/ tests/        # Sort imports
pylint app/              # Lint
```

### Docker
```bash
docker-compose up --build   # Full stack (backend, frontend, MongoDB)
```

### Database Initialization
```bash
python backend/scripts/init_sqlite.py   # Required
python backend/scripts/init_mongo.py    # Optional
```

## Architecture Overview

### Backend Structure (`backend/app/`)

```
app/
├── workflow/           # LangGraph State Machine
│   ├── state.py        # WorkflowState TypedDict (shared state between agents)
│   ├── graph.py        # StateGraph compilation with 5 agent nodes
│   ├── edges.py        # Conditional routing (reviewer can loop to writer)
│   └── checkpointer.py # SqliteSaver for pause/resume
│
├── agents/             # 5 specialized LangGraph nodes
│   ├── base.py         # BaseAgent with LLMFactory
│   ├── planner.py      # Planning node
│   ├── researcher.py   # Research node with MCP tools
│   ├── analyst.py      # Analysis node
│   ├── writer.py       # Writing node
│   └── reviewer.py     # Review node with quality scoring
│
├── mcp_servers/        # MCP tools per agent
│   ├── base_mcp.py     # Abstract MCP base class
│   └── {agent}_mcp.py  # Agent-specific tools (web search, DB queries)
│
├── services/           # Business logic
│   ├── workflow_manager.py  # High-level workflow API
│   ├── graph_runner.py      # LangGraph execution engine
│   ├── db_service.py        # SQLite + MongoDB operations
│   └── validation.py        # Input sanitization
│
├── routes/             # HTTP endpoints
│   ├── health.py       # GET /health
│   └── v1/
│       ├── query.py         # POST /api/v1/query
│       └── stream_query.py  # SSE streaming
│
├── middleware/         # Auth, rate limiting, error handling
├── core/               # Logger, constants, LLMFactory
└── schemas/            # Pydantic models
```

### LangGraph Workflow

```
START → Planner → Researcher → Analyst → Writer → Reviewer → END
                                                        ↓
                                                [NEEDS_REVISION]
                                                        ↓
                                                    Writer (cycle)
```

**Key patterns:**
- **Shared State**: `WorkflowState` TypedDict passed between all agents
- **Conditional Routing**: Reviewer can loop back to Writer via `needs_revision` edge
- **Checkpointing**: State persistence via `SqliteSaver` for pause/resume
- **Factory Pattern**: `LLMFactory.get_llm(role)` for Groq model selection

### Entry Points

- `backend/main.py` - Development entry point (Flask debug mode)
- `backend/wsgi.py` - Production entry point (Gunicorn WSGI)
- `backend/app/__init__.py` - Flask application factory (`create_app()`)
- `backend/app/services/workflow_manager.py` - `WorkflowManager.process_query()`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/query` | Submit query for processing |
| GET | `/api/v1/stream_query/<session_id>` | Stream results (SSE) |
| GET | `/api/v1/history?limit=10&offset=0` | Get query history |
| POST | `/api/v1/register` | Register user, get API key |
| GET | `/health` | Health check |

## Configuration

All config via `.env` (copy from `backend/.env.example`):

**Required:**
- `GROQ_API_KEY` - Groq API key (all agents use `llama-3.3-70b-versatile`)

**Optional APIs:**
- `OPENWEATHER_API_KEY`, `NEWS_API_KEY`, `ALPHA_VANTAGE_API_KEY` - Data sources
- `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID` - Web search

**Database:**
- `SQLITE_PATH=data/nueuro_agents.db`
- `MONGO_URI=mongodb://localhost:27017/nueuro_agents`

**Flask:**
- `SECRET_KEY`, `FLASK_ENV`, `DEBUG`

**Rate Limiting:**
- `RATELIMIT_REQUESTS=100`, `RATELIMIT_WINDOW=3600`

**Timeouts:**
- `AGENT_TIMEOUT=25`, `GRAPH_TIMEOUT=30`, `MAX_ITERATIONS=3`

## Development Notes

- All agents use Groq `llama-3.3-70b-versatile` with different temperatures
- MongoDB is optional - SQLite works for development
- Tests skip automatically if required env vars are missing
- Frontend is static HTML/CSS/JS served separately (Nginx in production)
- LangGraph checkpointing enables pause/resume of long-running queries

## Documentation Files

- `PROJECT_DOCUMENTATION.md` - Detailed system architecture
- `ARCHITECTURE_CONFIRMED.md` - Agent flow verification
- `DEVELOPMENT_PHASES.md` - 12-phase implementation roadmap
- `HOW_TO_RUN_TESTS.md` - Test execution guide
