"""User registration endpoint - POST /api/v1/register"""

from flask import Blueprint, request, jsonify
from app.core.logger import get_logger
import uuid
import hashlib

logger = get_logger(__name__)

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new user and generate API key.
    
    Request JSON:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secure_password"
    }
    
    Response JSON:
    {
        "status": "success" | "error",
        "user_id": "uuid",
        "api_key": "sk_...",
        "message": "...",
        "error": null
    }
    
    HTTP Status:
    - 201: User created
    - 400: Bad request
    - 409: User already exists
    - 500: Server error
    """
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "status": "error",
                "error": "Content-Type must be application/json",
                "user_id": None,
                "api_key": None
            }), 400
        
        data = request.get_json()
        
        # Validate input fields
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        
        if not username or len(username) < 3:
            logger.warning("Invalid username: too short")
            return jsonify({
                "status": "error",
                "error": "Username must be at least 3 characters",
                "user_id": None,
                "api_key": None
            }), 400
        
        if not email or "@" not in email:
            logger.warning("Invalid email format")
            return jsonify({
                "status": "error",
                "error": "Valid email address required",
                "user_id": None,
                "api_key": None
            }), 400
        
        if not password or len(password) < 8:
            logger.warning("Invalid password: too short")
            return jsonify({
                "status": "error",
                "error": "Password must be at least 8 characters",
                "user_id": None,
                "api_key": None
            }), 400
        
        # In a full implementation, check for existing user
        # For now, generate new IDs
        
        user_id = str(uuid.uuid4())
        api_key = f"sk_{uuid.uuid4().hex[:32]}"
        
        # Hash password (in production, use bcrypt or argon2)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        logger.info(f"Registering new user: {username} ({user_id})")
        
        # In a full implementation, save to database
        # For now, return success
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "api_key": api_key,
            "username": username,
            "message": f"User {username} registered successfully. Save your API key.",
            "error": None
        }), 201
    
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": f"Registration failed: {str(e)}",
            "user_id": None,
            "api_key": None
        }), 500


@register_bp.route('/validate-key', methods=['POST'])
def validate_api_key():
    """Validate an API key.
    
    Request JSON:
    {
        "api_key": "sk_..."
    }
    
    Response JSON:
    {
        "status": "success" | "error",
        "valid": true | false,
        "user_id": "uuid" | null,
        "message": "..."
    }
    """
    
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "valid": False,
                "user_id": None,
                "message": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        api_key = data.get("api_key", "").strip()
        
        if not api_key:
            return jsonify({
                "status": "error",
                "valid": False,
                "user_id": None,
                "message": "API key is required"
            }), 400
        
        logger.info(f"Validating API key: {api_key[:20]}...")
        
        # In a full implementation, check against database
        # For now, basic validation
        is_valid = api_key.startswith("sk_") and len(api_key) > 20
        
        if is_valid:
            return jsonify({
                "status": "success",
                "valid": True,
                "user_id": str(uuid.uuid4()),
                "message": "API key is valid"
            }), 200
        else:
            return jsonify({
                "status": "success",
                "valid": False,
                "user_id": None,
                "message": "API key is invalid"
            }), 200
    
    except Exception as e:
        logger.error(f"Key validation failed: {str(e)}")
        return jsonify({
            "status": "error",
            "valid": False,
            "user_id": None,
            "message": str(e)
        }), 500
