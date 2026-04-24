"""Request logging middleware for tracking request/response cycles."""

import time
from flask import request, g
from app.core.logger import get_logger
from app.middleware.request_id import get_request_id

logger = get_logger(__name__)


def init_request_logging(app):
    """Initialize request logging middleware."""

    @app.before_request
    def log_request_start():
        """Log request start with timing."""
        g.request_start_time = time.time()

        request_id = get_request_id()
        user_id = getattr(g, 'user_id', 'anonymous')

        logger.info(
            f"Request started: {request.method} {request.path} - "
            f"User: {user_id}, Request-ID: {request_id}"
        )

    @app.after_request
    def log_request_completion(response):
        """Log request completion with timing and status."""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time

            request_id = get_request_id()
            user_id = getattr(g, 'user_id', 'anonymous')

            logger.info(
                f"Request completed: {request.method} {request.path} - "
                f"Status: {response.status_code}, Duration: {duration:.3f}s - "
                f"User: {user_id}, Request-ID: {request_id}"
            )

            # Add performance headers
            response.headers['X-Request-Duration'] = f"{duration:.3f}"

        return response

    @app.teardown_request
    def log_request_error(exception):
        """Log request errors if any occurred."""
        if exception is not None:
            request_id = get_request_id()
            user_id = getattr(g, 'user_id', 'anonymous')

            logger.error(
                f"Request error: {request.method} {request.path} - "
                f"Error: {exception} - "
                f"User: {user_id}, Request-ID: {request_id}",
                exc_info=True
            )

    logger.info("Request logging middleware initialized")


def log_request_metrics(method, path, status_code, duration, user_id="anonymous"):
    """Log detailed request metrics for monitoring."""
    request_id = get_request_id()

    metrics = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration": duration,
        "user_id": user_id,
        "request_id": request_id,
        "timestamp": time.time()
    }

    logger.info(f"Request metrics: {metrics}")

    # For production, you might want to send this to a metrics system
    # like Prometheus, Datadog, or CloudWatch


def log_slow_requests(threshold_seconds=5.0):
    """Decorator to log slow requests."""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            duration = time.time() - start_time

            if duration > threshold_seconds:
                request_id = get_request_id()
                user_id = getattr(g, 'user_id', 'anonymous')

                logger.warning(
                    f"Slow request: {request.method} {request.path} - "
                    f"Duration: {duration:.3f}s (threshold: {threshold_seconds}s) - "
                    f"User: {user_id}, Request-ID: {request_id}"
                )

            return result

        return decorated_function

    return decorator