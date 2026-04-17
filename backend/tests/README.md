# Backend Tests

Professional pytest test suite for the Multi-AI-Agents backend.

## Test Structure

```
tests/
├── __init__.py                    # Test package
├── conftest.py                    # Shared fixtures and configuration
├── test_groq_integration.py      # Groq API integration tests
├── test_planner_agent.py         # Planner agent tests
```

## Running Tests

### Install pytest (if not already installed):
```bash
pip install pytest pytest-asyncio
```

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_groq_integration.py
pytest tests/test_planner_agent.py
```

### Run specific test class:
```bash
pytest tests/test_groq_integration.py::TestGroqAPI
pytest tests/test_planner_agent.py::TestPlannerAgent
```

### Run specific test:
```bash
pytest tests/test_groq_integration.py::TestGroqAPI::test_groq_api_invoke
```

### Run with verbose output:
```bash
pytest -v
```

### Run only integration tests:
```bash
pytest -m integration
```

## Test Requirements

Tests require the following environment variables to be set in `.env`:

- `GROQ_API_KEY` - Your Groq API key (required for Groq tests)
- `HF_API_TOKEN` - Your HuggingFace API token (optional, for HF tests)
- `MONGODB_URI` - MongoDB connection URI (optional, defaults to localhost)

## Test Coverage

### Groq API Tests (`test_groq_integration.py`)
- ✅ API initialization with valid credentials
- ✅ Query invocation and response validation
- ✅ Response quality checks

### Planner Agent Tests (`test_planner_agent.py`)
- ✅ LLMFactory creates Groq LLM for planner role
- ✅ Planner LLM invokes queries successfully
- ✅ Generated plans are structured and meaningful
- ✅ Temperature settings are correct
- ✅ LLM instance caching works properly

## Notes

- Tests skip automatically if required environment variables are not set
- Tests use pytest fixtures for dependency injection
- Each test is isolated and can run independently
