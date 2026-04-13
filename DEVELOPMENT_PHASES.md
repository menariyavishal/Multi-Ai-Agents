# Nueuro-Agents: Detailed Development Phases (LangGraph + LangChain Edition)

This plan breaks down the project into 12 phases, each with specific deliverables, technologies, and success criteria. The architecture is based on LangGraph (state machine) + LangChain (tool calling) + MCP servers per agent. The frontend is decoupled (static HTML/CSS/JS). All phases are designed for a college mini‑project timeline (approx. 6–8 weeks).

## Phase 1: Project Setup & Environment Configuration (Week 1)

**Goal:** Create the directory structure, virtual environment, and base configuration files – no code yet.

### Tasks:

- Create the complete folder tree as defined in the updated structure (including workflow/, agents/, mcp_servers/, etc.).
- Initialize Git repository and .gitignore (exclude venv/, __pycache__/, logs/, data/, .env).
- Create .env.example with placeholders for:
  - GEMINI_API_KEY, HF_API_TOKEN (optional)
  - MONGO_URI, SQLITE_PATH
  - RATELIMIT_REQUESTS, RATELIMIT_WINDOW
- Create requirements.txt with:
  ```
  flask==3.1.0
  gunicorn==21.2.0
  python-dotenv==1.0.0
  pydantic==2.7.0
  langchain==0.2.0
  langgraph==0.1.0
  langchain-google-genai==1.0.0
  langchain-huggingface==0.1.0
  langchain-mcp-adapters==0.1.0   # if available; otherwise custom wrapper
  pymongo==4.6.0
  diskcache==5.6.0
  pytest==8.2.0
  ```
- Create requirements-dev.txt with black, pylint, isort, pre-commit.
- Write README.md with setup instructions.
- Create empty __init__.py files in all Python packages.

### Deliverables:
- Directory tree, environment files, dependency lists, README.

---

## Phase 2: Core Infrastructure – Config, Logging, LLM Factory (Week 1‑2)

**Goal:** Implement low‑level utilities that will be used by agents and services.

### Tasks:

#### app/config.py
- Define Config, DevConfig, ProdConfig, TestConfig classes.
- Load environment variables with python-dotenv.
- Provide methods like `get_llm_config(agent_role)` returning provider, model name, API key.

#### app/extensions.py
- Singleton pattern for:
  - SQLite connection (or SQLAlchemy engine)
  - MongoDB client (lazy init)
  - Cache (diskcache.Cache)
  - LangGraph checkpointer (init later)

#### core/logger.py
- Configure Python logging: console (INFO) for dev, rotating file (DEBUG) for prod.
- Add `get_logger(__name__)` function.

#### core/constants.py
- Define timeouts (agent timeout = 25s, total graph timeout = 30s).
- Max query length (500), max iterations (3).
- Default model names per agent role.

#### core/llm_factory.py
- Implement `LLMFactory.get_llm(agent_role: str)` that returns a LangChain BaseChatModel (e.g., ChatGoogleGenerativeAI or HuggingFaceEndpoint).
- Cache LLM instances per role to avoid re‑initialisation.
- Handle missing API keys gracefully (raise ConfigError).

### Deliverables:
- Working config loading, logging, LLM factory that can return Gemini or HF models.

---

## Phase 3: Database Layer – SQLite + MongoDB (Week 2)

**Goal:** Create database schemas and service classes for user management, API keys, and conversation history.

### Tasks:

#### scripts/init_sqlite.py
- Create users, api_keys, query_history tables (see schema in documentation).
- Use sqlite3 module. Add indexes.

#### scripts/init_mongo.py
- Create agent_responses collection with JSON schema validation.
- Create TTL index on timestamp (90 days).

#### services/db_service.py
- Class DatabaseService with methods:
  - `register_user(username, email, password_hash)` → api_key
  - `validate_api_key(api_key)` → user_id
  - `save_query_history(user_id, query, agent_outputs, status, error_msg)`
  - `save_full_state_to_mongo(session_id, graph_state)`
  - `get_history(user_id, limit, offset)`
- Unit tests (using pytest with temporary SQLite and mock MongoDB).

### Deliverables:
- SQLite schema, MongoDB collections, DB service class with basic CRUD.

---

## Phase 4: MCP Servers – Tools per Agent (Week 2‑3)

**Goal:** Implement each agent's MCP server as a set of LangChain Tool objects.

### Tasks:

#### mcp_servers/base_mcp.py
- Abstract class BaseMCPServer with `get_tools()` -> `List[BaseTool]` method.

#### mcp_servers/planner_mcp.py
- Tool: task_decomposition (optional – could be done by LLM directly; keep simple for now).

#### mcp_servers/researcher_mcp.py
- Tools: web_search(query: str), news_search(topic: str), database_lookup(table, filter) (mock for now).
- Use requests to call SerpAPI or NewsAPI (if keys available).
- Wrap each as a @tool decorator from LangChain.

#### mcp_servers/analyst_mcp.py
- Tools: extract_trends(data: str), calculate_statistics(numbers: List[float]).
- Implement simple logic or call Hugging Face inference.

#### mcp_servers/writer_mcp.py
- Tools: check_grammar(text: str), apply_style_guide(text: str, style: str).
- Initially pass‑through (no heavy NLP).

#### mcp_servers/reviewer_mcp.py
- Tools: fact_check(statement: str), readability_score(text: str).
- Fact‑check could call a search tool again.

### Deliverables:
- Each MCP server returns a list of LangChain tools. Unit tests for each tool (mocking external APIs).

---

## Phase 5: LangGraph Workflow – State & Graph Definition (Week 3)

**Goal:** Define the shared state and build the graph skeleton without agent logic (just placeholder nodes).

### Tasks:

#### workflow/state.py
- Define GraphState(TypedDict) with all fields:
  ```python
  query: str
  plan: Optional[str]
  research_findings: Optional[str]
  analysis_insights: Optional[str]
  draft: Optional[str]
  review_score: Optional[float]
  review_feedback: Optional[str]
  final_answer: Optional[str]
  iteration_count: int
  error: Optional[str]
  ```

#### workflow/checkpointer.py
- Create a SqliteSaver (LangGraph built‑in) or MemorySaver for dev.
- Use `from langgraph.checkpoint.sqlite import SqliteSaver`.

#### workflow/graph.py
- Import StateGraph from langgraph.graph.
- Add placeholder nodes: planner_node, researcher_node, analyst_node, writer_node, reviewer_node, finalize_node.
- Define edges: sequential from planner → researcher → analyst → writer → reviewer.
- Add conditional edge from reviewer: if review_score < 0.7 → writer, else → finalize.
- Compile graph with checkpointer.
- Expose `get_graph()` function.

### Deliverables:
- A compiled LangGraph that can be invoked (with dummy node functions) and prints state transitions.

---

## Phase 6: Agent Nodes – Implementing LangGraph Node Functions (Week 3‑4)

**Goal:** Implement each agent node to call the appropriate LLM (via LLM factory) and optionally use its MCP tools.

### Tasks:

#### agents/base.py
- Helper function `run_llm_with_tools(state, agent_role, system_prompt, tools)` that uses LangChain's bind_tools and invoke.

#### agents/planner.py
- Node function:
  - Takes state, gets Gemini LLM.
  - Prompts: "Break down the user query into 3-4 steps."
  - Updates state["plan"].

#### agents/researcher.py
- Loads Hugging Face Mistral LLM and researcher_mcp tools.
- Calls LLM with the plan and asks to use web_search tool as needed.
- Updates state["research_findings"].

#### agents/analyst.py
- Similar, using Llama‑3 and analyst tools.
- Extracts insights from research findings.

#### agents/writer.py
- Uses Gemini, no tools (or grammar tool).
- Writes draft based on analysis.

#### agents/reviewer.py
- Uses Zephyr.
- Outputs a score (0‑1) and feedback.
- Returns {"review_score": score, "review_feedback": feedback}.

#### agents/finalize.py
- Saves final answer to state["final_answer"].
- Triggers DB storage (via service).

### Deliverables:
- All node functions ready. Graph can be invoked end‑to‑end (with real LLM calls).

---

## Phase 7: Graph Runner Service & API Integration (Week 4)

**Goal:** Create a service that runs the LangGraph and expose it via Flask REST API.

### Tasks:

#### services/graph_runner.py
- Class GraphRunner:
  - `__init__` loads compiled graph.
  - `run_sync(query, session_id, user_id)` – invokes graph with config={"configurable": {"thread_id": session_id}}.
  - `run_stream(query, ...)` – yields node outputs using graph.astream().

#### routes/v1/query.py
- POST /api/v1/query – validates request, checks API key, rate limit.
- Calls graph_runner.run_sync(...).
- Returns JSON with final_answer and metadata.

#### routes/v1/stream_query.py (optional for real‑time UI)
- Use Flask's Response with generator to stream SSE events from graph.astream().

#### routes/v1/history.py
- GET endpoint returning user history from SQLite.

#### routes/v1/register.py
- POST for new user (generates API key).

### Deliverables:
- Fully functional REST API that can process queries and return answers.

---

## Phase 8: Middleware & Security (Week 4‑5)

**Goal:** Implement authentication, rate limiting, error handling, request logging.

### Tasks:

#### middleware/auth.py
- Decorator `require_api_key` that reads `Authorization: Bearer <key>` header.
- Validates against SQLite api_keys table.
- Sets request.user_id.

#### middleware/rate_limit.py
- Token bucket implementation in memory (dictionary per API key).
- Limit: 100 requests per hour (configurable).
- Returns 429 if exceeded.

#### middleware/error_handler.py
- Register `@app.errorhandler(Exception)` to return consistent JSON error responses.
- Handle GraphTimeout, RateLimitExceeded, InvalidAPIKey.

#### middleware/request_id.py
- Generate UUID4 per request, add to g.request_id, inject into response headers.

#### middleware/request_logger.py
- Log each request: method, path, request_id, status, duration.

### Deliverables:
- Secure API endpoints with rate limiting and logging.

---

## Phase 9: Frontend – Static UI with Real‑Time Updates (Week 5)

**Goal:** Build a decoupled frontend that consumes the API and visualises the agent pipeline.

### Tasks:

#### frontend/src/index.html
- Basic structure: input form, output area, agent visualisation panel.

#### frontend/src/css/style.css
- Modern, responsive, similar to earlier design but cleaner.

#### frontend/src/js/app.js
- Submit query via fetch to /api/v1/query.
- Display final answer.
- Optionally, if streaming endpoint exists, use EventSource to update agent statuses in real time.

#### frontend/src/js/agents-visualizer.js
- Highlights current agent, shows checkmark when completed.

#### Serving frontend
- For development, Flask can serve static files from frontend/src. For production, Nginx in Docker.

### Deliverables:
- Functional web UI that interacts with the backend API.

---

## Phase 10: Testing & Quality Assurance (Week 5‑6)

**Goal:** Achieve >70% test coverage for critical components.

### Tasks:

#### Unit tests (tests/unit/)
- test_llm_factory.py – mock API responses.
- test_db_service.py – use in‑memory SQLite.
- test_mcp_servers.py – mock external calls.
- test_agents.py – test each node function with dummy state.

#### Integration tests (tests/integration/)
- test_graph.py – run full graph with mocked LLMs and tools (ensure conditional routing works).
- test_api.py – test endpoints with test client, authentication, rate limiting.

#### Load test (manual)
- Simulate 5 concurrent queries, verify no crashes and timeouts.

#### Linting & formatting
- Run black, isort, pylint, fix issues.

### Deliverables:
- Test report, code coverage HTML, lint‑clean codebase.

---

## Phase 11: Docker Containerisation (Week 6)

**Goal:** Package the application for production submission.

### Tasks:

#### docker/Dockerfile.backend
- Multi‑stage: build stage (install deps) and runtime stage (copy only necessary files).
- Use python:3.11-slim.
- Set environment variables, expose port 8000.
- Run with Gunicorn: `gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app`.

#### docker/Dockerfile.frontend
- Use nginx:alpine, copy frontend/src to /usr/share/nginx/html.

#### docker/docker-compose.yml
- Services:
  - backend – builds from Dockerfile.backend, depends on mongodb.
  - frontend – builds from Dockerfile.frontend, ports 80:80.
  - mongodb – uses mongo:6, with volume for persistence.
- Network bridge for communication.

#### docker/nginx.conf
- Reverse proxy configuration (optional, if backend and frontend need unified entry).

#### Test Docker
- `docker-compose up --build`, verify end‑to‑end.

### Deliverables:
- Working Docker Compose stack, ready for submission.

---

## Phase 12: Documentation & Final Polish (Week 6‑7)

**Goal:** Complete all documentation and prepare submission package.

### Tasks:

- Update README.md – Project description, setup instructions (local + Docker), API examples, screenshots.
- Write API.md – Detailed API reference with request/response samples.
- Write ARCHITECTURE.md – Explain LangGraph workflow, state, checkpoints, MCP tools.
- Write DEPLOYMENT.md – Steps to deploy on a VPS or local Docker.
- Generate PROJECT_DOCUMENTATION.md (the one you have) – Update with final implementation details.
- Create a short demo video / screen recording (optional but recommended for college).
- Final code review – Remove dead code, ensure all environment variables are documented.
- Zip submission – Exclude logs/, data/, __pycache__, .env.

### Deliverables:
- Complete documentation, clean repository, submission package.

---

## Summary of Phases

| Phase | Name | Duration | Key Output |
|-------|------|----------|------------|
| 1 | Setup & Environment | Week 1 | Directory tree, requirements, README |
| 2 | Core Infrastructure | Week 1‑2 | Config, logging, LLM factory |
| 3 | Database Layer | Week 2 | SQLite + MongoDB schemas, DB service |
| 4 | MCP Servers (LangChain Tools) | Week 2‑3 | Tools per agent (web search, stats, etc.) |
| 5 | LangGraph Workflow | Week 3 | State, graph skeleton, checkpointer |
| 6 | Agent Nodes | Week 3‑4 | Full node implementations with LLM calls |
| 7 | Graph Runner & API | Week 4 | REST endpoints, streaming (optional) |
| 8 | Middleware & Security | Week 4‑5 | Auth, rate limiting, error handling |
| 9 | Frontend UI | Week 5 | Static HTML/CSS/JS, agent visualiser |
| 10 | Testing & QA | Week 5‑6 | Unit + integration tests, linting |
| 11 | Docker Containerisation | Week 6 | Dockerfiles, compose, final build |
| 12 | Documentation & Submission | Week 6‑7 | Complete docs, demo, zip package |

**Total estimated time:** 6‑7 weeks (suitable for a semester project).

---

## Notes

- This phased plan ensures incremental delivery, with each phase building on the previous one.
- The use of LangGraph is fully integrated from Phase 5 onward.
- MCP servers are implemented as LangChain tools in Phase 4.
- The final product is a state‑of‑the‑art multi‑agent system ready for college evaluation.
- **Additional files may be considered and created during development as needed.**
