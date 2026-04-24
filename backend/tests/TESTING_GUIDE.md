# 🧪 Testing Documentation

## Overview

The test suite for Nueuro-Agents is organized into two categories:

1. **Unit Tests** (`unit/`) - Individual component testing
2. **Integration Tests** (`integration/`) - Multi-component workflow testing

---

## 📁 Directory Structure

```
tests/
├── unit/                           # Unit Tests
│   ├── __init__.py
│   ├── test_analyst.py            # Analyst agent unit tests
│   ├── test_db_service.py         # Database service unit tests
│   ├── test_graph_runner.py       # Graph runner component tests
│   ├── test_planner_agent.py      # Planner agent unit tests
│   ├── test_planner_implementation.py # Planner implementation details
│   ├── test_researcher_query_analysis.py # Researcher query parsing
│   ├── test_reviewer.py           # Reviewer agent unit tests
│   ├── test_workflow_graph.py     # Workflow graph structure
│   └── test_writer.py             # Writer agent unit tests
│
├── integration/                    # Integration Tests
│   ├── __init__.py
│   ├── test_api_endpoints.py      # API endpoint testing
│   ├── test_database.py           # Database with components
│   ├── test_groq_integration.py   # Groq LLM integration
│   ├── test_researcher_data_gathering.py # Researcher with data sources
│   ├── test_researcher_workflow.py # Researcher in workflow context
│   ├── test_workflow_integration.py # Full workflow testing
│   └── test_workflow_manager.py   # Workflow manager integration
│
├── conftest.py                     # Pytest configuration & fixtures
├── __init__.py                     # Package initialization
└── README.md                       # This file
```

---

## 🧪 Unit Tests

Unit tests focus on **individual components** in isolation, without external dependencies.

### Coverage by Component

#### 🤖 Agent Tests
| Test File | Purpose | Component |
|-----------|---------|-----------|
| `test_analyst.py` | Tests Analyst agent logic | Analyst Agent |
| `test_planner_agent.py` | Tests Planner agent logic | Planner Agent |
| `test_planner_implementation.py` | Tests planner implementation details | Planner Agent |
| `test_researcher_query_analysis.py` | Tests query analysis | Researcher Agent |
| `test_reviewer.py` | Tests Reviewer agent logic | Reviewer Agent |
| `test_writer.py` | Tests Writer agent logic | Writer Agent |

#### 🔧 Component Tests
| Test File | Purpose | Component |
|-----------|---------|-----------|
| `test_db_service.py` | Tests database operations | DatabaseService |
| `test_graph_runner.py` | Tests graph runner | GraphRunner |
| `test_workflow_graph.py` | Tests workflow graph structure | WorkflowGraph |

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific unit test
pytest tests/unit/test_analyst.py -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html

# Run specific test function
pytest tests/unit/test_analyst.py::TestAnalyst::test_analyze -v
```

---

## 🔗 Integration Tests

Integration tests focus on **multiple components working together**, testing cross-layer interactions and full workflows.

### Coverage by Workflow

#### 🌐 API & External Integration
| Test File | Purpose | Tests |
|-----------|---------|-------|
| `test_api_endpoints.py` | REST API endpoint functionality | Query, History, Search endpoints |
| `test_groq_integration.py` | LLM provider integration | Groq API calls, LLM responses |

#### 🔄 Workflow Components
| Test File | Purpose | Tests |
|-----------|---------|-------|
| `test_researcher_data_gathering.py` | Data gathering with sources | Wikipedia, News, Google, Database |
| `test_researcher_workflow.py` | Researcher in workflow context | Researcher with plan input |
| `test_workflow_integration.py` | Full pipeline workflow | All 5 agents working together |
| `test_workflow_manager.py` | Workflow orchestration | Query processing end-to-end |

#### 💾 Data Persistence
| Test File | Purpose | Tests |
|-----------|---------|-------|
| `test_database.py` | Database operations in context | CRUD with agents, persistence |

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific integration test
pytest tests/integration/test_workflow_integration.py -v

# Run with timeout (for long-running tests)
pytest tests/integration/ -v --timeout=60

# Run only fast tests (skip slow ones)
pytest tests/integration/ -v -m "not slow"
```

---

## 🚀 Running All Tests

### Complete Test Suite

```bash
# Run all tests (unit + integration)
cd backend
pytest tests/ -v

# Run all tests with coverage report
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run with parallel execution (faster)
pytest tests/ -v -n auto
```

### Test Filtering

```bash
# Run only tests matching a pattern
pytest tests/ -k "analyst" -v

# Run tests excluding integration
pytest tests/ -v --ignore=tests/integration/

# Run tests excluding unit
pytest tests/ -v --ignore=tests/unit/

# Run only tests with 'workflow' in name
pytest tests/ -k "workflow" -v
```

### Test Markers

```bash
# Run tests marked as 'fast'
pytest tests/ -m "fast" -v

# Run tests marked as 'slow' (usually integration)
pytest tests/ -m "slow" -v

# Run tests marked as 'database'
pytest tests/ -m "database" -v
```

---

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# Generate and display coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# View HTML report
# Open htmlcov/index.html in browser
```

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| **Agents** | 85%+ | — |
| **Services** | 80%+ | — |
| **Routes** | 75%+ | — |
| **Middleware** | 85%+ | — |
| **Overall** | 80%+ | — |

---

## 🔧 Test Configuration

### conftest.py

The `conftest.py` file contains:
- Pytest fixtures (shared test utilities)
- Database setup/teardown
- Mock LLM responses
- API client fixtures

### Fixtures Available

```python
# Database fixture
@pytest.fixture
def db():
    """Provides test database connection"""
    
# API client fixture
@pytest.fixture
def client():
    """Provides Flask test client"""
    
# Mock LLM fixture
@pytest.fixture
def mock_llm():
    """Provides mocked LLM responses"""
```

---

## ✅ Test Checklist

Before committing code:

- [ ] All unit tests pass: `pytest tests/unit/ -v`
- [ ] All integration tests pass: `pytest tests/integration/ -v`
- [ ] Coverage is above 80%: `pytest --cov=app`
- [ ] No linting errors: `pylint app/`
- [ ] Code is formatted: `black app/`
- [ ] Imports are sorted: `isort app/`

---

## 🐛 Debugging Tests

### Run Single Test with Debug

```bash
pytest tests/unit/test_analyst.py::TestAnalyst::test_analyze -v -s
```

### Run with Print Statements

```bash
pytest tests/ -v -s  # -s shows print output
```

### Run with PDB (Python Debugger)

```bash
pytest tests/ -v --pdb  # Drops into debugger on failure
```

### Run with Detailed Traceback

```bash
pytest tests/ -v --tb=long
```

---

## 📝 Writing New Tests

### Unit Test Template

```python
"""Test module for [component]"""
import pytest
from app.[module] import [Component]

class Test[Component]:
    """Tests for [Component]"""
    
    def setup_method(self):
        """Setup before each test"""
        self.component = [Component]()
    
    def test_functionality(self):
        """Test specific functionality"""
        result = self.component.method()
        assert result == expected_value
```

### Integration Test Template

```python
"""Integration test for [workflow]"""
import pytest
from app.services import WorkflowManager
from app.models import Conversation

class TestWorkflowIntegration:
    """Tests for [workflow] integration"""
    
    def test_full_workflow(self, client):
        """Test full workflow execution"""
        response = client.post('/api/v1/query', json={
            'query': 'test query',
            'user_id': 'test_user'
        })
        assert response.status_code == 200
        assert response.json['status'] == 'completed'
```

---

## 🔄 Continuous Integration

### GitHub Actions

Tests run automatically on:
- **Push** to main branch
- **Pull requests**
- **Scheduled** (daily at 2 AM UTC)

### Local Pre-commit Checks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📈 Test Metrics

### Current Test Statistics

```
Unit Tests:        9 files, ~250 test cases
Integration Tests: 7 files, ~150 test cases
Total Coverage:    80%+ overall
Execution Time:    ~45 seconds (all tests)
```

### Performance Benchmarks

| Test Suite | Time | Status |
|-----------|------|--------|
| Unit Tests | ~20s | ✓ Fast |
| Integration Tests | ~25s | ✓ Medium |
| All Tests | ~45s | ✓ Acceptable |

---

## 🆘 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Make sure you're in backend directory
cd backend

# Install development dependencies
pip install -r requirements-dev.txt
```

#### MongoDB Connection Errors
```bash
# Start MongoDB
mongod

# Or use in-memory mode (tests should auto-fallback)
```

#### Timeout Errors
```bash
# Increase timeout
pytest tests/ --timeout=120
```

#### Test File Not Found
```bash
# Run from correct directory
cd backend
pytest tests/
```

---

## 📚 Testing Best Practices

### ✅ Do

- ✓ Keep tests isolated (no cross-test dependencies)
- ✓ Use descriptive test names
- ✓ Test one thing per test
- ✓ Use fixtures for setup
- ✓ Mock external dependencies
- ✓ Clean up after tests

### ❌ Don't

- ✗ Hardcode paths or values
- ✗ Use real API keys in tests
- ✗ Make actual network calls
- ✗ Leave tests in pending state
- ✗ Test multiple things in one test
- ✗ Have slow tests (> 5 seconds)

---

## 📞 Support

For issues with tests:
1. Check test output carefully
2. Review relevant test file
3. Check conftest.py for fixtures
4. Run with `-v -s` flags for details
5. Open issue on GitHub

---

## Summary

| Aspect | Details |
|--------|---------|
| **Total Tests** | ~400 test cases |
| **Unit Tests** | 9 files in `unit/` |
| **Integration Tests** | 7 files in `integration/` |
| **Coverage Target** | 80%+ |
| **Run Command** | `pytest tests/ -v` |
| **Quick Start** | `pytest tests/unit/ -v` |

