"""Error handling middleware for standardized error responses."""

from typing import Optional
from flask import jsonify, request
from app.core.logger import get_logger
from app.exceptions.custom import RateLimitExceeded, ValidationError, WorkflowError

logger = get_logger(__name__)


def setup_error_handlers(app):
    """Register error handlers for Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        logger.warning(f"Bad request: {str(error)}")
        return jsonify({
            "status": "error",
            "error": "Bad request",
            "details": str(error.description) if hasattr(error, 'description') else str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        logger.warning(f"Unauthorized access: {str(error)}")
        return jsonify({
            "status": "error",
            "error": "Unauthorized",
            "details": "API key required or invalid"
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        logger.warning(f"Forbidden access: {str(error)}")
        return jsonify({
            "status": "error",
            "error": "Forbidden",
            "details": "Access denied"
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        logger.debug(f"Resource not found: {request.path}")
        return jsonify({
            "status": "error",
            "error": "Not found",
            "details": f"Endpoint '{request.path}' not found"
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Rate Limit Exceeded errors."""
        logger.warning(f"Rate limit exceeded for {request.remote_addr}")
        return jsonify({
            "status": "error",
            "error": "Rate limit exceeded",
            "details": "Too many requests. Please wait before trying again."
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Internal server error",
            "details": "An unexpected error occurred. Please try again later."
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        logger.error(f"Service unavailable: {str(error)}")
        return jsonify({
            "status": "error",
            "error": "Service unavailable",
            "details": "The service is temporarily unavailable. Please try again later."
        }), 503
    
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error):
        """Handle custom RateLimitExceeded exception."""
        logger.warning(f"Rate limit exceeded: {str(error)}")
        return jsonify({
            "status": "error",
            "error": "Rate limit exceeded",
            "details": str(error)
        }), 429
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle custom ValidationError exception."""
        logger.warning(f"Validation error: {str(error)}")
        return jsonify({
            "status": "error",
            "error": "Validation failed",
            "details": str(error)
        }), 400
    
    @app.errorhandler(WorkflowError)
    def handle_workflow_error(error):
        """Handle custom WorkflowError exception."""
        logger.error(f"Workflow error: {str(error)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Workflow processing failed",
            "details": str(error)
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exception."""
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "An unexpected error occurred",
            "details": "Please contact support if the issue persists"
        }), 500


def create_error_response(status: str, error: str, details: Optional[str] = None, code: int = 500):
    """Create standardized error response.
    
    Args:
        status: Status indicator (e.g., "error", "warning")
        error: Error type/title
        details: Detailed error message
        code: HTTP status code
        
    Returns:
        Tuple of (JSON response, HTTP code)
    """
    response = {
        "status": status,
        "error": error
    }
    if details:
        response["details"] = details
    
    return jsonify(response), code
