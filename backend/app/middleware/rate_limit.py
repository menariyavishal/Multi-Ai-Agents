"""Rate limiting middleware using token bucket algorithm."""

from functools import wraps
from typing import Optional, Tuple
from time import time
from flask import request, jsonify, g
from app.core.logger import get_logger
from app.exceptions.custom import RateLimitExceeded
import os

logger = get_logger(__name__)

# Configuration from environment
RATE_LIMIT_REQUESTS = int(os.getenv('RATELIMIT_REQUESTS', 100))
RATE_LIMIT_WINDOW = int(os.getenv('RATELIMIT_WINDOW', 3600))  # seconds (1 hour default)

# In-memory token bucket storage (use Redis in production)
TOKEN_BUCKETS = {}


class TokenBucket:
    """Token bucket for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens available, False otherwise
        """
        now = time()
        elapsed = now - self.last_refill
        
        # Refill bucket based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def remaining(self) -> int:
        """Get remaining tokens."""
        now = time()
        elapsed = now - self.last_refill
        return int(min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        ))


def get_client_identifier() -> str:
    """Get unique client identifier from request.
    
    Priority:
    1. X-API-Key header (if present)
    2. X-Forwarded-For header (for proxies)
    3. Remote address
    
    Returns:
        Client identifier string
    """
    # Check for API key first
    api_key = request.headers.get('X-API-Key', '').strip()
    if api_key:
        return f"api_key:{api_key[:20]}"
    
    # Check for forwarded IP (proxy)
    forwarded_for = request.headers.get('X-Forwarded-For', '').strip()
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0]}"
    
    # Fall back to remote address
    return f"ip:{request.remote_addr}"


def check_rate_limit(client_id: Optional[str] = None, tokens: int = 1) -> Tuple[bool, int, int]:
    """Check if client is within rate limit.
    
    Args:
        client_id: Client identifier (auto-detected if None)
        tokens: Tokens to consume
        
    Returns:
        Tuple of (allowed: bool, remaining: int, reset_time: float)
    """
    if client_id is None:
        client_id = get_client_identifier()
    
    # Create or get bucket for client
    if client_id not in TOKEN_BUCKETS:
        refill_rate = RATE_LIMIT_REQUESTS / RATE_LIMIT_WINDOW
        TOKEN_BUCKETS[client_id] = TokenBucket(RATE_LIMIT_REQUESTS, refill_rate)
    
    bucket = TOKEN_BUCKETS[client_id]
    allowed = bucket.consume(tokens)
    remaining = bucket.remaining()
    
    logger.debug(f"Rate limit check for {client_id}: allowed={allowed}, remaining={remaining}")
    
    return allowed, remaining, RATE_LIMIT_WINDOW


def rate_limit_decorator(limit: Optional[int] = None, window: Optional[int] = None):
    """Decorator to rate limit endpoint.
    
    Args:
        limit: Max requests per window (default from config)
        window: Time window in seconds (default from config)
        
    Usage:
        @app.route('/api/expensive')
        @rate_limit_decorator(limit=10, window=60)
        def expensive_endpoint():
            ...
    """
    _limit = limit or RATE_LIMIT_REQUESTS
    _window = window or RATE_LIMIT_WINDOW
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = get_client_identifier()
            
            # Create bucket if not exists
            if client_id not in TOKEN_BUCKETS:
                refill_rate = _limit / _window
                TOKEN_BUCKETS[client_id] = TokenBucket(_limit, refill_rate)
            
            bucket = TOKEN_BUCKETS[client_id]
            
            if not bucket.consume(1):
                remaining = bucket.remaining()
                logger.warning(f"Rate limit exceeded for {client_id}")
                
                return jsonify({
                    "status": "error",
                    "error": "Rate limit exceeded",
                    "details": f"Maximum {_limit} requests per {_window}s allowed",
                    "retry_after": _window
                }), 429
            
            # Store rate limit info in response headers
            remaining = bucket.remaining()
            g.rate_limit_remaining = remaining
            g.rate_limit_reset = int(time()) + _window
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def apply_rate_limit_headers(response):
    """Apply rate limit information to response headers.
    
    Call this in after_request handler.
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response
    """
    if hasattr(g, 'rate_limit_remaining'):
        response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
    
    if hasattr(g, 'rate_limit_reset'):
        response.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
    
    response.headers['X-RateLimit-Limit'] = str(RATE_LIMIT_REQUESTS)
    
    return response


def cleanup_expired_buckets(max_age_seconds: int = 86400):
    """Remove expired buckets from memory (older than max_age).
    
    Args:
        max_age_seconds: Remove buckets not used for this many seconds
    """
    now = time()
    expired = [
        client_id for client_id, bucket in TOKEN_BUCKETS.items()
        if (now - bucket.last_refill) > max_age_seconds
    ]
    
    for client_id in expired:
        del TOKEN_BUCKETS[client_id]
        logger.debug(f"Cleaned up expired rate limit bucket: {client_id}")
