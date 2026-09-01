"""Flask application factory."""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.core.logger import get_logger
from app.routes.v1 import v1_bp
from app.services.database_service import get_db_service

logger = get_logger(__name__)


def create_app(config_name: str = None) -> Flask:
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
    
    Returns:
        Configured Flask application
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    app = Flask(__name__)
    
    # Configure CORS across all routes for production frontend & development
    CORS(
        app,
        resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
                "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
                "expose_headers": ["Content-Type", "X-API-Key"],
                "supports_credentials": True,
                "max_age": 86400
            }
        }
    )
    
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
        return jsonify({
            "status": "error",
            "error": "Endpoint not found",
            "path": getattr(e, 'description', 'Unknown')
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle 405 errors."""
        return jsonify({
            "status": "error",
            "error": "Method not allowed"
        }), 405
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        logger.error(f"Server error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Internal server error"
        }), 500
    
    # Health check endpoint with DB connectivity status
    @app.route('/health', methods=['GET', 'OPTIONS'])
    def health_check():
        """Simple health check endpoint."""
        db_connected = False
        try:
            db_service = get_db_service()
            if db_service.client:
                db_service.client.admin.command('ping')
                db_connected = True
        except Exception:
            db_connected = False
            
        return jsonify({
            "status": "healthy",
            "environment": config_name,
            "version": "1.0.0",
            "database_connected": db_connected
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """API root endpoint."""
        return jsonify({
            "name": "Neuro-Agents Multi-Agent System",
            "version": "1.0.0",
            "status": "running",
            "environment": config_name,
            "endpoints": {
                "query": "/api/v1/query",
                "stream": "/api/v1/stream",
                "history": "/api/v1/history",
                "register": "/api/v1/register",
                "login": "/api/v1/login",
                "health": "/health"
            }
        }), 200
    
    # Register v1 API blueprint
    app.register_blueprint(v1_bp)
    
    logger.info("Flask app configured successfully")
    
    return app

