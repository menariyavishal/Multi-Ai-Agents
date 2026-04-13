"""
Application constants: timeouts, model configurations, and limits.
"""
import os

# ========== System Timeouts ==========
AGENT_TIMEOUT_SECONDS = 25      # Max time for a single agent node
GRAPH_TIMEOUT_SECONDS = 30      # Max total time for the entire LangGraph

# ========== Model Configuration per Agent ==========
# OPTIMIZATION: Use Gemini ONLY for Planner to preserve free tier quota
# Other agents use HuggingFace for lightweight inference
# Note: Tool calling (bind_tools) is ONLY supported by Gemini models.

MODEL_CONFIGS = {
    "planner": {
        "provider": "google",
        "name": "gemini-2.0-flash",          # Gemini used ONLY for planning
        "temperature": 0.2,
        "supports_tools": True
    },
    "researcher": {
        "provider": "huggingface",          # Switch to HF to save Gemini quota
        "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Lightweight model
        "temperature": 0.1,
        "supports_tools": False             # HF models don't support tools
    },
    "analyst": {
        "provider": "huggingface",
        "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "temperature": 0.1,
        "supports_tools": False
    },
    "writer": {
        "provider": "huggingface",          # Switch to HF to save Gemini quota
        "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "temperature": 0.7,
        "supports_tools": False
    },
    "reviewer": {
        "provider": "huggingface",          # Switch to HF to save Gemini quota
        "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "temperature": 0.0,
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
