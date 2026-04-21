"""API v1 routes."""

from flask import Blueprint

# Create v1 API blueprint
v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# Import route handlers to register them
from app.routes.v1.query import query_bp
from app.routes.v1.history import history_bp
from app.routes.v1.register import register_bp
from app.routes.v1.stream_query import stream_bp

# Register sub-blueprints
v1_bp.register_blueprint(query_bp)
v1_bp.register_blueprint(history_bp)
v1_bp.register_blueprint(register_bp)
v1_bp.register_blueprint(stream_bp)

__all__ = ['v1_bp']
