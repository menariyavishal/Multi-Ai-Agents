"""
Structured logging setup with console and rotating file handlers.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance. Ensures handlers are added only once per logger name.
    Logs go to console (INFO level) and a rotating file (DEBUG level).
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler (human-readable)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # File handler (with timestamps, rotates at 5MB)
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=5_000_000,  # 5 MB
            backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


def log_request(request_id: str, user_id: str, method: str, path: str, status: int, duration_ms: float):
    """Utility to log HTTP request details in a consistent format."""
    logger = get_logger("http.requests")
    logger.info(
        f"Request {request_id} | User {user_id} | {method} {path} | "
        f"Status {status} | Duration {duration_ms:.2f}ms"
    )
