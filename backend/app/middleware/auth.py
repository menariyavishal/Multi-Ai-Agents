"""Authentication middleware for API key validation."""

from functools import wraps
from flask import request, jsonify, g
from app.services.db_service import get_db_service
from app.core.logger import get_logger

logger = get_logger(__name__)


def require_api_key(f):
    """Decorator to require API key validation for protected endpoints.
    
    Usage:
        @app.route('/api/protected')
        @require_api_key
        def protected_endpoint():
            user_id = g.user_id  # Access authenticated user_id
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract API key from header
        api_key = request.headers.get('X-API-Key', '').strip()
        
        if not api_key:
            logger.warning("Missing API key in request")
            return jsonify({
                "status": "error",
                "error": "API key required (X-API-Key header)"
            }), 401
        
        # Validate API key
        db_service = get_db_service()
        user_id = db_service.validate_api_key(api_key)
        
        if not user_id:
            logger.warning(f"Invalid API key: {api_key[:10]}...")
            return jsonify({
                "status": "error",
                "error": "Invalid API key"
            }), 401
        
        # Store user_id in g for use in endpoint
        g.user_id = user_id
        g.api_key = api_key
        
        logger.info(f"API key validated for user: {user_id}")
        return f(*args, **kwargs)
    
    return decorated_function


def extract_optional_api_key():
    """Extract and validate optional API key from request header.
    
    Returns:
        user_id if API key valid, "anonymous" if no key provided, None if invalid
    """
    api_key = request.headers.get('X-API-Key', '').strip()
    
    if not api_key:
        logger.debug("No API key provided, using anonymous user")
        return "anonymous"
    
    db_service = get_db_service()
    user_id = db_service.validate_api_key(api_key)
    
    if user_id:
        logger.info(f"API key validated: {api_key[:10]}...")
        return user_id
    else:
        logger.warning(f"Invalid API key: {api_key[:10]}...")
        return None
