"""
Application constants: timeouts, model configurations, and limits.
"""
import os

# ========== System Timeouts ==========
AGENT_TIMEOUT_SECONDS = 120     # Max time for a single agent node
GRAPH_TIMEOUT_SECONDS = 180     # Max total time for the entire LangGraph

# ========== Model Configuration per Agent ==========
# All agents use Groq openai/gpt-oss-120b for ultra-fast, accurate real-time answers

MODEL_CONFIGS = {
    "planner": {
        "provider": "groq",
        "name": "openai/gpt-oss-120b",
        "temperature": 0.2,
        "supports_tools": True
    },
    "researcher": {
        "provider": "groq",
        "name": "openai/gpt-oss-120b",
        "temperature": 0.2,
        "supports_tools": True
    },
    "analyst": {
        "provider": "groq",
        "name": "openai/gpt-oss-120b",
        "temperature": 0.1,
        "supports_tools": False
    },
    "writer": {
        "provider": "groq",
        "name": "openai/gpt-oss-120b",
        "temperature": 0.3,
        "supports_tools": False
    },
    "reviewer": {
        "provider": "groq",
        "name": "openai/gpt-oss-120b",
        "temperature": 0.0,
        "supports_tools": False
    }
}

# ========== Input Limits ==========
MAX_QUERY_LENGTH = 50000
MAX_ITERATIONS = 3

# ========== Cache TTL ==========
CACHE_TTL_SECONDS = 3600  # 1 hour
