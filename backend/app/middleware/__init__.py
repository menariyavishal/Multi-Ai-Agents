"""Flask middleware modules for request handling, authentication, rate limiting, and error handling."""

from app.middleware.auth import require_api_key, extract_optional_api_key
from app.middleware.error_handler import setup_error_handlers
from app.middleware.rate_limit import rate_limit_decorator, check_rate_limit
from app.middleware.request_id import add_request_id

__all__ = [
    'require_api_key',
    'extract_optional_api_key',
    'setup_error_handlers',
    'rate_limit_decorator',
    'check_rate_limit',
    'add_request_id',
]
