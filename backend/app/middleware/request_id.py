"""Request ID middleware for request tracing and logging."""

from flask import request, g
from app.core.logger import get_logger
import uuid
from functools import wraps

logger = get_logger(__name__)


def generate_request_id() -> str:
    """Generate a unique request ID.
    
    Returns:
        UUID4 as string
    """
    return str(uuid.uuid4())


def add_request_id():
    """Add unique request ID to each request.
    
    Call this in before_request handler.
    Stores ID in g.request_id for use throughout request lifecycle.
    """
    # Check if client provided request ID
    request_id = request.headers.get('X-Request-ID', '').strip()
    
    # Generate new ID if not provided
    if not request_id:
        request_id = generate_request_id()
    
    # Store in g for access throughout request
    g.request_id = request_id
    
    # Log request start
    logger.info(
        f"[{request_id}] {request.method} {request.path} - "
        f"Client: {request.remote_addr}"
    )


def include_request_id_in_response(response):
    """Include request ID in response headers.
    
    Call this in after_request handler.
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response
    """
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
        
        # Log response
        logger.info(
            f"[{g.request_id}] Response: {response.status_code} - "
            f"{request.method} {request.path}"
        )
    
    return response


def request_id_required(f):
    """Decorator to require request ID header.
    
    Usage:
        @app.route('/api/trace-required')
        @request_id_required
        def traced_endpoint():
            request_id = g.request_id
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_id = request.headers.get('X-Request-ID', '').strip()
        
        if not request_id:
            logger.warning("Missing required X-Request-ID header")
            return {
                "status": "error",
                "error": "Request ID required",
                "details": "X-Request-ID header is required for this endpoint"
            }, 400
        
        g.request_id = request_id
        return f(*args, **kwargs)
    
    return decorated_function


class RequestIDLogger:
    """Context manager for logging with request ID.
    
    Usage:
        with RequestIDLogger('operation_name') as log:
            log.info("Starting operation")
            # do work
            log.debug("Intermediate step")
            log.info("Completed")
    """
    
    def __init__(self, operation_name: str):
        """Initialize logger context.
        
        Args:
            operation_name: Name of operation being logged
        """
        self.operation_name = operation_name
        self.request_id = getattr(g, 'request_id', 'no-request-id')
        self.logger = logger
    
    def __enter__(self):
        """Enter context."""
        self.logger.info(f"[{self.request_id}] Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type:
            self.logger.error(
                f"[{self.request_id}] Failed: {self.operation_name} - {str(exc_val)}",
                exc_info=True
            )
        else:
            self.logger.info(f"[{self.request_id}] Completed: {self.operation_name}")
    
    def info(self, message: str):
        """Log info with request ID."""
        self.logger.info(f"[{self.request_id}] {message}")
    
    def debug(self, message: str):
        """Log debug with request ID."""
        self.logger.debug(f"[{self.request_id}] {message}")
    
    def warning(self, message: str):
        """Log warning with request ID."""
        self.logger.warning(f"[{self.request_id}] {message}")
    
    def error(self, message: str, exc_info: bool = False):
        """Log error with request ID."""
        self.logger.error(f"[{self.request_id}] {message}", exc_info=exc_info)


def get_request_id() -> str:
    """Get current request ID.
    
    Returns:
        Request ID from g.request_id or 'no-request-id' if not set
    """
    return getattr(g, 'request_id', 'no-request-id')
