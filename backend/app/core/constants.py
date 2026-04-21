"""
Application constants: timeouts, model configurations, and limits.
"""
import os

# ========== System Timeouts ==========
AGENT_TIMEOUT_SECONDS = 25      # Max time for a single agent node
GRAPH_TIMEOUT_SECONDS = 30      # Max total time for the entire LangGraph

# ========== Model Configuration per Agent ==========
# All agents now use Groq for consistency and performance
# - llama-3.3-70b-versatile: Best for analysis & reasoning
# - Groq provides free unlimited tier with exceptional speed

MODEL_CONFIGS = {
    "planner": {
        "provider": "groq",
        "name": "llama-3.3-70b-versatile",
        "temperature": 0.3,  # Balanced: creative planning with focus
        "supports_tools": True
    },
    "researcher": {
        "provider": "groq",
        "name": "llama-3.3-70b-versatile",
        "temperature": 0.2,  # Analytical: focused data gathering
        "supports_tools": True
    },
    "analyst": {
        "provider": "groq",
        "name": "qwen/qwen3-32b",
        "temperature": 0.1,  # Precise: deterministic analysis
        "supports_tools": False
    },
    "writer": {
        "provider": "groq",
        "name": "llama-3.3-70b-versatile",
        "temperature": 0.7,  # Creative: polished writing
        "supports_tools": False
    },
    "reviewer": {
        "provider": "groq",
        "name": "llama-3.3-70b-versatile",
        "temperature": 0.0,  # Strict: deterministic review
        "supports_tools": False
    }
}

# ========== Input Limits ==========
MAX_QUERY_LENGTH = 500
MAX_ITERATIONS = 3

# ========== Cache TTL ==========
CACHE_TTL_SECONDS = 3600  # 1 hour

# ========== Hugging Face API Notes ==========
# For gated models (e.g., Llama-3, Zephyr), you must:
# 1. Have a Hugging Face account
# 2. Accept the model's license terms on the HF website
# 3. Use a valid HF_API_TOKEN with permissions
# TinyLlama is open‑access, no special terms.
