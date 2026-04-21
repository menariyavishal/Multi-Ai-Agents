"""Flask application factory."""

from flask import Flask
from app.core.logger import get_logger
from app.routes.v1 import v1_bp

logger = get_logger(__name__)


def create_app(config_name: str = "development") -> Flask:
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
    
    Returns:
        Configured Flask application
    """
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name == "production":
        app.config.update(
            DEBUG=False,
            JSON_SORT_KEYS=False,
            PROPAGATE_EXCEPTIONS=True
        )
    elif config_name == "testing":
        app.config.update(
            TESTING=True,
            DEBUG=True
        )
    else:  # development
        app.config.update(
            DEBUG=True,
            JSON_SORT_KEYS=False
        )
    
    logger.info(f"Creating Flask app with config: {config_name}")
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors."""
        return {
            "status": "error",
            "error": "Endpoint not found",
            "path": e.description
        }, 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle 405 errors."""
        return {
            "status": "error",
            "error": "Method not allowed"
        }, 405
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        logger.error(f"Server error: {str(e)}")
        return {
            "status": "error",
            "error": "Internal server error"
        }, 500
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return {"status": "healthy"}, 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """API root endpoint."""
        return {
            "name": "Neuro-Agents Multi-Agent System",
            "version": "1.0.0",
            "status": "running",
            "documentation": "/api/docs",
            "endpoints": {
                "query": "/api/v1/query",
                "stream": "/api/v1/stream",
                "history": "/api/v1/history/<query_hash>",
                "register": "/api/v1/register",
                "health": "/health"
            }
        }, 200
    
    # Register v1 API blueprint
    app.register_blueprint(v1_bp)
    
    logger.info("Flask app configured successfully")
    
    return app
