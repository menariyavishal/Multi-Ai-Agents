"""Streaming query endpoint - POST /api/v1/stream"""

from flask import Blueprint, request, jsonify, Response
from app.services.workflow_manager import get_workflow_manager
from app.services.database_service import get_db_service, DatabaseService
from app.core.logger import get_logger
import uuid
import json
import asyncio
import time

logger = get_logger(__name__)

stream_bp = Blueprint('stream', __name__)


@stream_bp.route('/stream', methods=['POST'])
def stream_query():
    """Process a query with real-time streaming updates.
    
    Request JSON:
    {
        "query": "What are AI trends?",
        "max_iterations": 3
    }
    
    Response: Server-Sent Events (SSE) stream
    
    Event format (newline-delimited JSON):
    data: {"type": "agent_update", "agent": "planner", "status": "started"}
    data: {"type": "agent_update", "agent": "planner", "status": "completed"}
    data: {"type": "agent_update", "agent": "researcher", "status": "started"}
    ...
    data: {"type": "workflow_complete", "result": {...}}
    """
    
    session_id = str(uuid.uuid4())
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "status": "error",
                "error": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({
                "status": "error",
                "error": "Query is required"
            }), 400
        
        if len(query) > 1000:
            return jsonify({
                "status": "error",
                "error": "Query must be less than 1000 characters"
            }), 400
        
        max_iterations = data.get("max_iterations", 3)
        try:
            max_iterations = int(max_iterations)
            if max_iterations < 1 or max_iterations > 5:
                max_iterations = 3
        except (ValueError, TypeError):
            max_iterations = 3
        
        logger.info(f"[{session_id}] Starting streaming query: {query[:80]}")
        
        def event_stream():
            """Generate SSE events for streaming updates."""
            start_time = time.time()
            try:
                # Get workflow manager
                manager = get_workflow_manager(enable_checkpointing=True)
                
                # Yield start event
                yield f"data: {json.dumps({'type': 'workflow_start', 'session_id': session_id})}\n\n"
                
                # Run async streaming
                async def run_stream():
                    async for update in manager.process_query_streaming(
                        query=query,
                        max_iterations=max_iterations
                    ):
                        # Extract agent from update
                        agent = None
                        if update.get("planner_complete"):
                            agent = "planner"
                        elif update.get("researcher_complete"):
                            agent = "researcher"
                        elif update.get("analyst_complete"):
                            agent = "analyst"
                        elif update.get("writer_complete"):
                            agent = "writer"
                        elif update.get("reviewer_complete"):
                            agent = "reviewer"
                        
                        if agent:
                            yield f"data: {json.dumps({'type': 'agent_complete', 'agent': agent})}\n\n"
                
                # Run the async generator
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    for event in loop.run_until_complete(run_stream()):
                        yield event
                finally:
                    loop.close()
                
                # Process query and get final result
                result = manager.process_query(
                    query=query,
                    max_iterations=max_iterations,
                    verbose=False
                )
                
                summary = manager.get_result_summary(result)
                
                # Persist query and workflow state
                elapsed = time.time() - start_time
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
                
                db_service: DatabaseService = get_db_service()
                query_id = db_service.save_query_history(
                    user_id="anonymous",
                    query_text=query,
                    session_id=session_id,
                    agent_outputs=agent_outputs,
                    status="completed",
                    execution_time_seconds=elapsed,
                    iterations_used=iterations_used,
                    quality_score=quality_score
                )
                
                db_service.save_full_state_to_mongo(
                    session_id=session_id,
                    query=query,
                    workflow_state=result,
                    user_id="anonymous",
                    final_answer=result.get("final_answer", ""),
                    execution_time_seconds=elapsed,
                    status="completed"
                )
                
                logger.info(f"[{session_id}] Streaming query saved (id: {query_id})")
                
                # Yield complete event
                yield f"data: {json.dumps({'type': 'workflow_complete', 'result': summary})}\n\n"
            
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"[{session_id}] Streaming error: {str(e)}", exc_info=True)
                
                # Save error to history
                db_service: DatabaseService = get_db_service()
                db_service.save_query_history(
                    user_id="anonymous",
                    query_text=query,
                    session_id=session_id,
                    status="failed",
                    error_message=str(e),
                    execution_time_seconds=elapsed
                )
                
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return Response(
            event_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    
    except Exception as e:
        logger.error(f"[{session_id}] Stream endpoint error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
