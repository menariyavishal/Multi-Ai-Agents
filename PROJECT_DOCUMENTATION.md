Nueuro-Agents: Detailed Project Overview (LangGraph + LangChain Edition)
1. Project Identity & Core Concept
Nueuro‑Agents is an industrial‑grade multi‑agent AI system that processes complex user queries through a state‑machine orchestrated pipeline of five specialised AI agents. Unlike simple linear scripts, the system uses LangGraph to build a cyclic, condition‑aware graph where each agent is a node that can update a shared state and even decide to loop back (e.g., reviewer requesting another research pass). This makes the system more robust, observable, and adaptable than a rigid chain.

Key innovation:
Each agent has its own “mind” (different LLMs – Gemini or Hugging Face) and its own MCP (Model Context Protocol) server providing specialised tools (web search, database query, code execution). The entire workflow is compiled into a LangGraph StateGraph with built‑in checkpointing, allowing pause/resume, human‑in‑the‑loop, and streaming of intermediate outputs.

Target output quality:
Superior to single‑LLM systems because agents focus on subtasks, use external tools, and the graph can reroute based on intermediate results (e.g., if the reviewer finds the draft insufficient, it can send it back to the writer).

2. System Architecture (LangGraph‑Based)
The system replaces the old linear pipeline with a directed cyclic graph of nodes (agents). Each node receives a shared state (current plan, research data, analysis, draft, review score) and returns updates to that state.

State definition (workflow/state.py):
A TypedDict or Pydantic model containing fields like:

query (original user input)

plan (output of planner)

research_findings (raw + structured data)

analysis_insights (key takeaways)

draft (writer’s output)

review_feedback (critique and score)

final_answer (after approval)

iteration_count (for loops)

error (for exception handling)

Graph nodes (agents/):
Each agent is a LangGraph node – a Python function that takes the current state, calls its LLM (via LangChain’s ChatGoogleGenerativeAI or HuggingFaceEndpoint), optionally invokes its MCP server (wrapped as LangChain tools), and returns a dictionary with the fields it updated.

Conditional edges:
The reviewer node can output a review_score. If the score is below a threshold, the graph routes back to the writer node (with feedback). If the score is acceptable, it proceeds to the final answer node.

Checkpointing (workflow/checkpointer.py):
LangGraph’s MemorySaver or SqliteSaver stores the state after every node execution. This allows the system to resume a long‑running query from the last checkpoint – essential for handling timeouts or manual approval.

Graph compilation (workflow/graph.py):
The nodes and edges are added to a StateGraph, compiled with a checkpointer, and exposed as a Runnable that can be invoked or streamed.

3. Tech Stack (Updated with LangChain & LangGraph)
Layer	Technology	Rationale
Backend Framework	Flask 3.1 + Gunicorn	Lightweight, easy to integrate with LangGraph as a callable.
AI Orchestration	LangGraph + LangChain	Stateful, cyclic workflows; built‑in checkpointing; tool calling; streaming.
LLM Providers	Google Gemini 2.0 Flash + Hugging Face	Gemini for speed/cost; Hugging Face models (Mistral, Llama‑3, Zephyr) for specialisation.
LangChain Integrations	langchain-google-genai, langchain-huggingface	Standardised interface for all LLMs.
MCP Servers	Custom Python + langchain-mcp-adapters	Each agent’s MCP tools are exposed as LangChain Tool objects for easy calling.
User & API Key DB	SQLite3	Simple, file‑based.
Chat History DB	MongoDB (optional)	Stores full graph state snapshots (rich history).
Checkpoint Persistence	LangGraph SqliteSaver or MongoDBSaver	Saves graph state between runs; enables pause/resume.
Caching	diskcache	Cache identical query results (final answer).
Rate Limiting	Token‑bucket middleware (custom)	Per API key.
Request Validation	Pydantic v2	Type‑safe request/response models.
Logging	Python logging + structlog (optional)	JSON logs for production.
Testing	pytest, pytest-asyncio, responses	Mock LangChain LLM calls and MCP tools.
Containerisation	Docker + Docker Compose	Backend, frontend (Nginx), MongoDB.
Frontend	HTML5, CSS3, vanilla JS (static)	Fetches /api/v1/query and can display streamed node outputs via SSE.
Why LangGraph instead of a simple chain?

Looping: Reviewer can send writer back for improvements.

Observability: Built‑in streaming of each node’s output to the frontend.

Resilience: Checkpointing allows retry from the last successful node.

Extensibility: Easy to add human‑in‑the‑loop nodes or parallel branches.

4. Updated Directory Structure (Key Additions)
The structure now includes a workflow/ folder and uses LangGraph concepts:

Nueuro-Agents/
├── backend/                          # All server‑side logic
│   ├── app/
│   │   ├── __init__.py               # App factory (create_app)
│   │   ├── config.py                 # Environment‑aware config (dev/staging/prod)
│   │   ├── extensions.py             # DB, cache, LangChain tools registry
│   │   │
│   │   ├── workflow/                 # 🆕 LangGraph State Machine
│   │   │   ├── __init__.py
│   │   │   ├── state.py              # Defines the GraphState (TypedDict/Pydantic)
│   │   │   ├── graph.py              # Compiles the nodes/edges into a StateGraph
│   │   │   └── checkpointer.py       # LangGraph memory saver (connects to SQLite/Mongo)
│   │   │
│   │   ├── agents/                   # 5 specialised agents (LangGraph Nodes)
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base node class returning state updates
│   │   │   ├── planner.py
│   │   │   ├── researcher.py         # Uses LangChain tool-calling
│   │   │   ├── analyst.py
│   │   │   ├── writer.py
│   │   │   └── reviewer.py           # Contains routing logic (e.g., conditional edges)
│   │   │
│   │   ├── mcp_servers/              # MCP implementations wrapped for LangChain
│   │   │   ├── __init__.py
│   │   │   ├── base_mcp.py
│   │   │   ├── planner_mcp.py
│   │   │   ├── researcher_mcp.py     # Uses langchain-mcp-adapters
│   │   │   ├── analyst_mcp.py
│   │   │   ├── writer_mcp.py
│   │   │   └── reviewer_mcp.py
│   │   │
│   │   ├── core/                     # Low‑level utilities
│   │   │   ├── __init__.py
│   │   │   ├── llm_factory.py        # Returns ChatGoogleGenerativeAI or HuggingFaceEndpoint
│   │   │   ├── logger.py             # Structured logging
│   │   │   └── constants.py          # Timeouts, model names
│   │   │
│   │   ├── services/                 # Business logic bridging API and Graph
│   │   │   ├── __init__.py
│   │   │   ├── graph_runner.py       # 🆕 Replaces orchestrator; invokes the LangGraph
│   │   │   ├── db_service.py         # Query history abstraction
│   │   │   └── validation.py         # Input sanitisation
│   │   │
│   │   ├── routes/                   # HTTP endpoints (REST API only)
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── query.py          # POST /v1/query (triggers graph_runner)
│   │   │   │   ├── history.py
│   │   │   │   └── register.py
│   │   │   └── health.py
│   │   │
│   │   ├── middleware/               # Cross‑cutting concerns
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── rate_limit.py
│   │   │   ├── error_handler.py
│   │   │   └── request_id.py
│   │   │
│   │   ├── schemas/                  # Request/response models (Pydantic v2)
│   │   │   ├── __init__.py
│   │   │   └── query.py
│   │   │
│   │   └── exceptions/               # Custom exceptions
│   │       ├── __init__.py
│   │       └── custom.py             # GraphTimeout, MCPError
│   │
│   ├── scripts/                      # DB init, migrations, seed data
│   │   ├── init_sqlite.py
│   │   └── init_mongo.py
│   │
│   ├── tests/                        # Backend tests
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── requirements.txt              # 🆕 Added: langgraph, langchain-google-genai, etc.
│   ├── requirements-dev.txt
│   ├── main.py                       # Dev server entry point
│   └── wsgi.py                       # Gunicorn entry point
│
├── frontend/                         # Static UI (decoupled from backend)
│   ├── public/
│   ├── src/
│   │   ├── index.html
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   └── agents-visualizer.js  # Can now visualize LangGraph stream events!
│   │   └── assets/
│   ├── package.json
│   └── README.md
│
├── docker/                           # Containerisation (final submission)
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── logs/
├── data/
├── .env.example
├── .gitignore
├── README.md
└── PROJECT_DOCUMENTATION.md

The frontend can now listen to streaming events from the graph (via graph.astream()) and update the agent visualiser in real time.

5. Key Features (Enhanced by LangGraph)
Feature	How LangGraph Enables It
Cyclic refinement	Reviewer node can route back to writer node with feedback.
Streaming intermediate outputs	Graph’s astream() yields each node’s output as it completes.
Pause & resume	Checkpoint persistence – a request can survive a server restart.
Human‑in‑the‑loop	Interrupt graph at a node, wait for human input, then resume.
Parallel execution	Future extension: researcher and analyst could run in parallel branches.
Retry & fallback	Graph can catch exceptions and route to an error handler node.
Full traceability	Every state change is recorded; can replay any conversation.
Other core features (unchanged):

Multi‑LLM support (Gemini + Hugging Face per agent).

MCP servers per agent for real‑time data (web search, DB queries).

User management, API keys, rate limiting.

REST API + decoupled static frontend.

Docker containerisation for final submission.

6. Data Flow (Graph Execution)
User submits query → Flask route calls graph_runner.invoke(query, session_id).

Graph starts with initial state { "query": "...", "iteration_count": 0 }.

Planner node → calls Gemini LLM → updates state plan.

Researcher node → calls Hugging Face Mistral + MCP web search tool → updates research_findings.

Analyst node → calls Llama‑3 + MCP analysis tool → updates analysis_insights.

Writer node → calls Gemini → updates draft.

Reviewer node → calls Zephyr → outputs review_score and review_feedback.

If review_score < 0.7 → graph routes back to Writer (with feedback).

Else → proceeds to Finalize node.

Finalize node → sets final_answer and saves to databases.

Streamed responses → frontend receives each node’s output in real time.

All state transitions are automatically saved to the checkpointer (SQLite or MongoDB).

7. Resource Optimisation (Same as before – college laptop friendly)
Memory: ~250 MB (with LangGraph overhead) – still fine.

No local GPU: Hugging Face models called via Inference API.

Checkpointer uses SQLite (no extra daemon).

Thread pool for concurrent requests: 2‑3 workers.

MongoDB optional; disabled locally.