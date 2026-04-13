# Nueuro-Agents: Multi-Agent AI System

A state-of-the-art, industrial-grade multi-agent AI system that processes complex, multi-step user queries through a sophisticated LangGraph state machine orchestrated pipeline of five specialized AI agents.

## Quick Start

### Prerequisites

- Python 3.11+
- Git
- MongoDB (optional, for production)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/menariyavishal/Multi-Ai-Agents.git
   cd Multi-Ai-Agents
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Initialize databases:**
   ```bash
   python backend/scripts/init_sqlite.py
   python backend/scripts/init_mongo.py  # Optional
   ```

### Running the Application

#### Development Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:5000`

#### Production Server (Gunicorn)

```bash
cd backend
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app
```

#### With Docker

```bash
docker-compose up --build
```

Backend: `http://localhost:8000`
Frontend: `http://localhost:80`

## Project Structure

```
Nueuro-Agents/
├── backend/                    # Server-side logic
│   ├── app/
│   │   ├── workflow/          # LangGraph state machine
│   │   ├── agents/            # 5 specialized agents
│   │   ├── mcp_servers/       # MCP tools per agent
│   │   ├── core/              # Config, logging, LLM factory
│   │   ├── services/          # Business logic
│   │   ├── routes/            # REST API endpoints
│   │   ├── middleware/        # Auth, rate limiting
│   │   ├── schemas/           # Request/response models
│   │   └── exceptions/        # Custom exceptions
│   ├── scripts/               # DB initialization
│   ├── tests/                 # Unit & integration tests
│   ├── requirements.txt       # Core dependencies
│   ├── requirements-dev.txt   # Dev dependencies
│   ├── main.py               # Development entry point
│   └── wsgi.py               # Production entry point
├── frontend/                  # Static UI
│   └── src/
│       ├── index.html        # Main HTML file
│       ├── css/style.css     # Styling
│       └── js/               # JavaScript logic
├── docker/                    # Docker configuration
├── logs/                      # Application logs
├── data/                      # Local data storage
└── README.md
```

## The Multi-Agent Pipeline

The system processes queries through 5 specialized agents:

1. **Planner** (Gemini 2.0 Flash)
   - Decomposes user query into actionable steps
   - Identifies required data and tools

2. **Researcher** (Mistral-7B)
   - Gathers real-world data via web search and databases
   - Provides factual grounding

3. **Analyst** (Llama-3-8B)
   - Extracts patterns, statistics, and insights
   - Processes raw research data

4. **Writer** (Gemini 2.0 Flash)
   - Synthesizes analysis into polished, readable output
   - Applies formatting and style

5. **Reviewer** (Zephyr-7B)
   - Conducts quality assurance checks
   - Verifies facts and can route back to writer for improvements

## API Endpoints

### Query Processing
- **POST** `/api/v1/query` - Submit a query for processing
- **GET** `/api/v1/stream_query/<session_id>` - Stream query results (SSE)

### History & Management
- **GET** `/api/v1/history?limit=10&offset=0` - Get user query history
- **POST** `/api/v1/register` - Register a new user and get API key

### System
- **GET** `/health` - Health check

## Configuration

All configuration is managed via `.env` file. Key variables:

```env
GEMINI_API_KEY=your_key
HF_API_TOKEN=your_token
MONGODBURI=mongodb://localhost:27017/nueuro_agents
FLASK_ENV=development
RATELIMIT_REQUESTS=100
RATELIMIT_WINDOW=3600
```

## Development

### Running Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
pylint app/
```

## Technical Stack

- **Backend Framework:** Flask 3.1 + Gunicorn
- **AI Orchestration:** LangGraph + LangChain
- **LLM Providers:** Google Gemini + Hugging Face
- **Databases:** SQLite + MongoDB
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript
- **Containerization:** Docker + Docker Compose
- **Testing:** pytest + pytest-cov

## Documentation

- [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) - Detailed system architecture
- [DEVELOPMENT_PHASES.md](DEVELOPMENT_PHASES.md) - Implementation roadmap
- [API.md](API.md) - Detailed API reference (coming soon)
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical deep-dive (coming soon)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please follow the code style guidelines and ensure all tests pass before submitting a pull request.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check existing documentation

---

**Status:** Active Development (Phase 1 Complete)
**Last Updated:** April 14, 2026
