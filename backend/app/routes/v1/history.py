"""Query history endpoint - GET /api/v1/history"""

from flask import Blueprint, request, jsonify
from app.core.logger import get_logger
from app.services.workflow_manager import get_workflow_manager
from app.services.database_service import get_db_service

logger = get_logger(__name__)

history_bp = Blueprint('history', __name__)


# ========== MongoDB Conversation History Endpoints ==========

@history_bp.route('/history', methods=['GET'])
def get_conversation_history():
    """Get all conversations for a user from MongoDB.
    
    Query Parameters:
    - user_id: (REQUIRED) User identifier
    - limit: Number of conversations to return (default: 20, max: 100)
    - skip: Number of conversations to skip for pagination (default: 0)
    
    Response JSON:
    {
        "status": "success" | "error",
        "user_id": "...",
        "conversations": [
            {
                "conversation_id": "uuid",
                "title": "What is AI?",
                "query": "What are the latest AI trends?",
                "created_at": "2024-04-22T10:30:45Z",
                "data_classification": "COMBINED",
                "quality_score": 0.92,
                "processing_time_seconds": 5.2
            },
            ...
        ],
        "total_count": 150,
        "error": null
    }
    """
    
    try:
        # Extract and validate user_id
        user_id = request.args.get("user_id", "").strip()
        if not user_id:
            return jsonify({
                "status": "error",
                "user_id": None,
                "conversations": [],
                "error": "user_id query parameter is required",
                "total_count": 0
            }), 400
        
        # Extract pagination parameters
        try:
            limit = int(request.args.get("limit", 20))
            skip = int(request.args.get("skip", 0))
            
            # Validate ranges
            limit = min(max(limit, 1), 100)  # 1-100
            skip = max(skip, 0)
        except ValueError:
            limit = 20
            skip = 0
        
        logger.info(f"Retrieving conversation history for user {user_id} (limit={limit}, skip={skip})")
        
        # Get from MongoDB
        db_service = get_db_service()
        conversations = db_service.get_user_conversations(user_id, limit=limit, skip=skip)
        
        # Get total count for pagination info
        total_count = 0
        if db_service.is_connected():
            try:
                total_count = db_service.conversations_collection.count_documents({"user_id": user_id})
            except:
                pass
        
        logger.info(f"Found {len(conversations)} conversations for user {user_id}")
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "conversations": [conv.dict() for conv in conversations],
            "total_count": total_count,
            "limit": limit,
            "skip": skip,
            "error": None
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "user_id": request.args.get("user_id"),
            "conversations": [],
            "error": str(e),
            "total_count": 0
        }), 500


@history_bp.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get full details of a specific conversation from MongoDB.
    
    Path Parameters:
    - conversation_id: UUID of the conversation
    
    Query Parameters:
    - user_id: (REQUIRED) User identifier to verify ownership
    
    Response JSON:
    {
        "status": "success" | "error",
        "conversation": {
            "conversation_id": "uuid",
            "user_id": "...",
            "title": "What is AI?",
            "query": "What are the latest AI trends?",
            "plan": "...",
            "research": "...",
            "content": "...",
            "analysis": {...},
            "final_output": "...",
            "data_classification": "COMBINED",
            "quality_score": 0.92,
            "quality_level": "high",
            "created_at": "2024-04-22T10:30:45Z",
            "processing_time_seconds": 5.2,
            "tags": ["ai", "trends"]
        },
        "error": null
    }
    """
    
    try:
        if not conversation_id:
            return jsonify({
                "status": "error",
                "conversation": None,
                "error": "conversation_id is required in URL path"
            }), 400
        
        # Extract user_id for ownership verification
        user_id = request.args.get("user_id", "").strip()
        
        logger.info(f"Retrieving conversation {conversation_id} for user {user_id}")
        
        # Get from MongoDB
        db_service = get_db_service()
        conversation = db_service.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({
                "status": "error",
                "conversation": None,
                "error": f"Conversation {conversation_id} not found"
            }), 404
        
        # Verify ownership (security check)
        if user_id and conversation.user_id != user_id:
            logger.warning(f"Unauthorized access attempt: user {user_id} tried to access conversation of user {conversation.user_id}")
            return jsonify({
                "status": "error",
                "conversation": None,
                "error": "Access denied: You do not own this conversation"
            }), 403
        
        logger.info(f"Successfully retrieved conversation {conversation_id}")
        
        return jsonify({
            "status": "success",
            "conversation": conversation.dict(),
            "error": None
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "conversation": None,
            "error": str(e)
        }), 500


@history_bp.route('/search', methods=['GET'])
def search_conversations():
    """Search conversations by keyword.
    
    Query Parameters:
    - user_id: (REQUIRED) User identifier
    - q: (REQUIRED) Search query string
    - limit: Number of results to return (default: 10, max: 50)
    
    Response JSON:
    {
        "status": "success" | "error",
        "user_id": "...",
        "query": "AI",
        "results": [...],  # Same as conversation list
        "total_found": 15,
        "error": null
    }
    """
    
    try:
        # Extract parameters
        user_id = request.args.get("user_id", "").strip()
        search_query = request.args.get("q", "").strip()
        
        if not user_id:
            return jsonify({
                "status": "error",
                "user_id": None,
                "results": [],
                "error": "user_id query parameter is required"
            }), 400
        
        if not search_query:
            return jsonify({
                "status": "error",
                "user_id": user_id,
                "results": [],
                "error": "q (search query) parameter is required"
            }), 400
        
        if len(search_query) > 100:
            return jsonify({
                "status": "error",
                "user_id": user_id,
                "results": [],
                "error": "Search query must be less than 100 characters"
            }), 400
        
        try:
            limit = int(request.args.get("limit", 10))
            limit = min(max(limit, 1), 50)
        except ValueError:
            limit = 10
        
        logger.info(f"Searching conversations for user {user_id} with query: {search_query}")
        
        # Search in MongoDB
        db_service = get_db_service()
        results = db_service.search_conversations(user_id, search_query, limit=limit)
        
        logger.info(f"Found {len(results)} conversations matching '{search_query}'")
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "query": search_query,
            "results": [result.dict() for result in results],
            "total_found": len(results),
            "error": None
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "results": [],
            "error": str(e),
            "total_found": 0
        }), 500


@history_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics from MongoDB.
    
    Query Parameters:
    - user_id: (REQUIRED) User identifier
    
    Response JSON:
    {
        "status": "success" | "error",
        "user_id": "...",
        "stats": {
            "total_conversations": 42,
            "total_queries": 42,
            "average_quality_score": 0.87,
            "last_query_at": "2024-04-22T10:30:45Z"
        },
        "error": null
    }
    """
    
    try:
        user_id = request.args.get("user_id", "").strip()
        
        if not user_id:
            return jsonify({
                "status": "error",
                "user_id": None,
                "stats": {},
                "error": "user_id query parameter is required"
            }), 400
        
        logger.info(f"Retrieving stats for user {user_id}")
        
        # Get from MongoDB
        db_service = get_db_service()
        stats = db_service.get_stats(user_id)
        
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "stats": stats,
            "error": None
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving user stats: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "user_id": request.args.get("user_id"),
            "stats": {},
            "error": str(e)
        }), 500


# ========== Original Checkpoint History Endpoints ==========
def get_query_history(query_hash):
    """Get execution history (checkpoints) for a query.
    
    Query Parameters:
    - query_hash: Hash or identifier of the query
    
    Response JSON:
    {
        "status": "success" | "error",
        "query_hash": "...",
        "checkpoints": [
            {
                "checkpoint_path": "data/checkpoints/query_HASH/iter_01_planner_TIMESTAMP.json",
                "agent": "planner",
                "iteration": 1,
                "timestamp": "2024-01-15T10:30:45Z"
            },
            ...
        ],
        "error": null
    }
    """
    
    try:
        if not query_hash:
            return jsonify({
                "status": "error",
                "query_hash": query_hash,
                "error": "query_hash is required",
                "checkpoints": []
            }), 400
        
        logger.info(f"Retrieving history for query: {query_hash}")
        
        # Get workflow manager
        manager = get_workflow_manager(enable_checkpointing=True)
        
        # Get execution history (checkpoints)
        checkpoints = manager.get_execution_history(query_hash)
        
        logger.info(f"Found {len(checkpoints)} checkpoints for query: {query_hash}")
        
        return jsonify({
            "status": "success",
            "query_hash": query_hash,
            "checkpoints": checkpoints,
            "error": None,
            "total_checkpoints": len(checkpoints)
        }), 200
    
    except Exception as e:
        logger.error(f"History retrieval failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "query_hash": query_hash,
            "error": str(e),
            "checkpoints": []
        }), 500


@history_bp.route('/checkpoint/<checkpoint_id>', methods=['GET'])
def get_checkpoint(checkpoint_id):
    """Retrieve a specific checkpoint state.
    
    Query Parameters:
    - checkpoint_id: Path or identifier of checkpoint
    
    Response JSON:
    {
        "status": "success" | "error",
        "checkpoint_id": "...",
        "state": {...},  # Full workflow state
        "error": null
    }
    """
    
    try:
        if not checkpoint_id:
            return jsonify({
                "status": "error",
                "checkpoint_id": checkpoint_id,
                "error": "checkpoint_id is required",
                "state": None
            }), 400
        
        logger.info(f"Retrieving checkpoint: {checkpoint_id}")
        
        # Get workflow manager
        manager = get_workflow_manager(enable_checkpointing=True)
        
        # In a full implementation, load the checkpoint
        # For now, return a message
        return jsonify({
            "status": "success",
            "checkpoint_id": checkpoint_id,
            "message": "Checkpoint retrieval functionality available",
            "error": None
        }), 200
    
    except Exception as e:
        logger.error(f"Checkpoint retrieval failed: {str(e)}")
        return jsonify({
            "status": "error",
            "checkpoint_id": checkpoint_id,
            "error": str(e),
            "state": None
        }), 500
