"""Query processing endpoint - POST /api/v1/query"""

from flask import Blueprint, request, jsonify, g
from app.services.workflow_manager import get_workflow_manager
from app.services.database_service import get_db_service, DatabaseService
from app.models.conversation import Conversation
from app.core.logger import get_logger
import uuid
import time

logger = get_logger(__name__)

query_bp = Blueprint('query', __name__)


@query_bp.route('/query', methods=['POST'])
def process_query():
    """Process a user query through the 5-agent workflow and save to MongoDB.
    
    Request JSON:
    {
        "query": "What are AI trends?",
        "user_id": "user123",  # REQUIRED for saving to history
        "max_iterations": 3    # optional, default 3
    }
    
    Response JSON:
    {
        "status": "success" | "error",
        "session_id": "uuid",
        "conversation_id": "uuid",  # NEW - ID in MongoDB
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
    - 400: Bad request (missing query or user_id)
    - 429: Rate limited
    - 500: Server error
    """
    
    session_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Validate request
        if not request.is_json:
            logger.warning(f"[{session_id}] Invalid content-type: {request.content_type}")
            return jsonify({
                "status": "error",
                "session_id": session_id,
                "conversation_id": None,
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
                "conversation_id": None,
                "error": "Query is required and must not be empty",
                "result": None
            }), 400
        
        # Extract and validate user_id
        user_id = data.get("user_id", "").strip()
        if not user_id:
            logger.warning(f"[{session_id}] Missing user_id")
            return jsonify({
                "status": "error",
                "session_id": session_id,
                "conversation_id": None,
                "error": "user_id is required for saving conversation history",
                "result": None
            }), 400
        
        if len(query) > 1000:
            logger.warning(f"[{session_id}] Query too long: {len(query)} chars")
            return jsonify({
                "status": "error",
                "session_id": session_id,
                "conversation_id": None,
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
        
        logger.info(f"[{session_id}] Processing query for user {user_id}: {query[:80]}")
        
        # Get workflow manager
        manager = get_workflow_manager(enable_checkpointing=True)
        
        # Process query with user_id for database context
        result = manager.process_query(
            query=query,
            user_id=user_id,
            max_iterations=max_iterations,
            verbose=False
        )
        
        # Extract summary
        summary = manager.get_result_summary(result)
        
        # DEBUG: Print summary analysis to see what we're returning
        print(f"\n[DEBUG_SUMMARY] Analysis keys: {list(summary.get('analysis', {}).keys())}")
        print(f"[DEBUG_SUMMARY] Has 'insights'? {'insights' in summary.get('analysis', {})}")
        print(f"[DEBUG_SUMMARY] Full summary: {summary}\n")
        
        elapsed = time.time() - start_time
        logger.info(f"[{session_id}] Query processed successfully in {elapsed:.2f}s")
        
        # Extract agent outputs and metadata
        # Note: LangGraph puts data directly in `result`, not in `result.final_state`
        
        # Save conversation to MongoDB
        try:
            db_service: DatabaseService = get_db_service()
            
            if db_service.is_connected():
                conversation = Conversation(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    query=query,
                    plan=result.get("plan", ""),
                    research=result.get("research", ""),
                    content=summary.get("final_answer", ""),
                    analysis=result.get("analysis", {}),
                    final_output=summary.get("final_answer", ""),
                    data_classification=result.get("data_classification", "COMBINED"),
                    quality_score=result.get("quality_score", 0.0) if isinstance(result.get("quality_score"), (int, float)) else 0.0,
                    quality_level=result.get("quality_level", "medium") or "medium",
                    processing_time_seconds=elapsed,
                    tags=extract_tags(query)
                )
                
                save_success = db_service.save_conversation(conversation)
                logger.info(f"[{session_id}] Conversation saved to MongoDB: {save_success}")
            else:
                logger.warning(f"[{session_id}] MongoDB not connected - conversation not saved")
        
        except Exception as db_error:
            logger.error(f"[{session_id}] Error saving to MongoDB: {str(db_error)}")
            # Don't fail the query if database save fails - data is still returned
        
        # FINAL DEBUG before return
        import json
        analysis_to_send = summary.get('analysis', {})
        print(f"\n[FINAL_DEBUG] Type of analysis_to_send: {type(analysis_to_send)}")
        print(f"[FINAL_DEBUG] analysis_to_send keys: {list(analysis_to_send.keys())}")
        print(f"[FINAL_DEBUG] 'insights' in analysis_to_send: {'insights' in analysis_to_send}")
        if 'insights' in analysis_to_send:
            insights_val = analysis_to_send['insights']
            print(f"[FINAL_DEBUG] insights type: {type(insights_val)}, value: {insights_val}")
        print(f"[FINAL_DEBUG] About to jsonify\n")
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "conversation_id": conversation_id,
            "result": summary,
            "error": None
        }), 200
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[{session_id}] Query processing failed: {str(e)}", exc_info=True)
        
        return jsonify({
            "status": "error",
            "session_id": session_id,
            "conversation_id": None,
            "result": None,
            "error": f"Internal server error: {str(e)}"
        }), 500


def extract_tags(query: str) -> list:
    """Extract tags from query for better search."""
    # Simple keyword extraction - can be improved with NLP
    keywords = [
        "weather", "news", "stock", "finance", "ai", "python", "javascript",
        "current", "today", "tomorrow", "trend", "analysis", "price", "rate"
    ]
    
    query_lower = query.lower()
    tags = [kw for kw in keywords if kw in query_lower]
    return tags[:5]  # Limit to 5 tags


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
