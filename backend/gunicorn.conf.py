"""Production Gunicorn Configuration for Multi-AI Agents Backend."""

import os
import multiprocessing

# Server socket
port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Worker processes & threading
# Use threaded workers to handle concurrent LLM streams and long-running agent workflows
workers = int(os.getenv("WEB_CONCURRENCY", 2))
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_class = "gthread"

# Worker lifecycle & timeouts
# 120s timeout ensures multi-step agent research and writing graphs complete without interruption
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
capture_output = True

# Process naming
proc_name = "multi_ai_agents_backend"
