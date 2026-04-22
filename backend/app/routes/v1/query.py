"""Query processing endpoint - POST /api/v1/query"""

from flask import Blueprint, request, jsonify, g
from app.services.workflow_manager import get_workflow_manager
from app.services.db_service import get_db_service
from app.core.logger import get_logger
import uuid
import time

logger = get_logger(__name__)

query_bp = Blueprint('query', __name__)


@query_bp.route('/query', methods=['POST'])
def process_query():
    """Process a user query through the 5-agent workflow.
    
    Request JSON:
    {
        "query": "What are AI trends?",
        "max_iterations": 3  # optional, default 3
    }
    
    Response JSON:
    {
        "status": "success" | "error",
        "session_id": "uuid",
        "result": {
            "query": "...",
            "status": "approved" | "needs_revision",
            "iterations_used": 1,
            "execution_time_seconds": 15.5,
            "plan": "...",
            "research_summary": "...",
            "analysis": {...},
            "review": {...},
            "final_answer": "...",
            "agent_completion": {...}
        },
        "error": null
    }
    
    HTTP Status:
    - 200: Success
    - 400: Bad request (missing query)
    - 429: Rate limited
    - 500: Server error
    """
    
    session_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Validate request
        if not request.is_json:
            logger.warning(f"[{session_id}] Invalid content-type: {request.content_type}")
            return jsonify({
                "status": "error",
                "session_id": session_id,
                "error": "Content-Type must be application/json",
                "result": None
            }), 400
        
        data = request.get_json()
        
        # Extract and validate query
        query = data.get("query", "").strip()
        if not query:
            logger.warning(f"[{session_id}] Missing or empty query")
            return jsonify({
                "status": "error",
                "session_id": session_id,
                "error": "Query is required and must not be empty",
                "result": None
            }), 400
        
        if len(query) > 1000:
            logger.warning(f"[{session_id}] Query too long: {len(query)} chars")
            return jsonify({
                "status": "error",
                "session_id": session_id,
                "error": "Query must be less than 1000 characters",
                "result": None
            }), 400
        
        # Extract max_iterations
        max_iterations = data.get("max_iterations", 3)
        try:
            max_iterations = int(max_iterations)
            if max_iterations < 1 or max_iterations > 5:
                max_iterations = 3
        except (ValueError, TypeError):
            max_iterations = 3
        
        logger.info(f"[{session_id}] Processing query: {query[:80]}")
        
        # Get workflow manager
        manager = get_workflow_manager(enable_checkpointing=True)
        
        # Process query
        result = manager.process_query(
            query=query,
            max_iterations=max_iterations,
            verbose=False
        )
        
        # Extract summary
        summary = manager.get_result_summary(result)
        
        elapsed = time.time() - start_time
        logger.info(f"[{session_id}] Query processed successfully in {elapsed:.2f}s")
        
        # Extract agent outputs and metadata for persistence
        agent_outputs = {
            "plan": result.get("plan", ""),
            "research": result.get("research", ""),
            "analysis": result.get("analysis", ""),
            "draft": result.get("draft", ""),
            "review_feedback": result.get("review_feedback", {}),
            "routing_decision": result.get("routing_decision", "")
        }
        
        quality_score = result.get("final_quality_score", None)
        iterations_used = result.get("final_iteration_count", 1)
        
        # Save to SQLite history (user_id optional for now)
        db_service = get_db_service()
        query_id = db_service.save_query_history(
            user_id="anonymous",  # Will be replaced with authenticated user_id
            query_text=query,
            session_id=session_id,
            agent_outputs=agent_outputs,
            status="completed",
            execution_time_seconds=elapsed,
            iterations_used=iterations_used,
            quality_score=quality_score
        )
        
        # Save full workflow state to MongoDB
        db_service.save_full_state_to_mongo(
            session_id=session_id,
            query=query,
            workflow_state=result,
            user_id="anonymous",
            final_answer=result.get("final_answer", ""),
            execution_time_seconds=elapsed,
            status="completed"
        )
        
        logger.info(f"[{session_id}] Query history saved (id: {query_id})")
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "result": summary,
            "error": None
        }), 200
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[{session_id}] Query processing failed: {str(e)}", exc_info=True)
        
        # Save error to history
        db_service = get_db_service()
        db_service.save_query_history(
            user_id="anonymous",
            query_text=query,
            session_id=session_id,
            status="failed",
            error_message=str(e),
            execution_time_seconds=elapsed
        )
        
        return jsonify({
            "status": "error",
            "session_id": session_id,
            "result": None,
            "error": f"Internal server error: {str(e)}"
        }), 500


@query_bp.route('/status/<session_id>', methods=['GET'])
def get_query_status(session_id):
    """Get execution status of a query session.
    
    Response JSON:
    {
        "status": "success",
        "session_id": "uuid",
        "execution_status": "completed" | "processing" | "not_found",
        "message": "..."
    }
    """
    logger.info(f"Checking status for session: {session_id}")
    
    try:
        # In a full implementation, this would check a database
        # For now, we return a simple status
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "execution_status": "completed",
            "message": "Query execution completed"
        }), 200
    
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "session_id": session_id,
            "error": str(e)
        }), 500
