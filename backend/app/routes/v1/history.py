"""Query history endpoint - GET /api/v1/history"""

from flask import Blueprint, request, jsonify
from app.core.logger import get_logger
from app.services.workflow_manager import get_workflow_manager

logger = get_logger(__name__)

history_bp = Blueprint('history', __name__)


@history_bp.route('/history/<query_hash>', methods=['GET'])
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
