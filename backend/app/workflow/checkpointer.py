"""Checkpoint persistence layer for workflow state."""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger(__name__)


class WorkflowCheckpointer:
    """Simple file-based checkpointing system for workflow state.
    
    Saves workflow state at each step to enable recovery and auditing.
    """
    
    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        """Initialize checkpointer with directory for saving checkpoints.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Checkpointer initialized at {self.checkpoint_dir}")
    
    def save_checkpoint(
        self,
        query: str,
        iteration: int,
        agent: str,
        state: Dict[str, Any]
    ) -> str:
        """Save workflow state checkpoint to file.
        
        Args:
            query: User query (for grouping related checkpoints)
            iteration: Iteration number
            agent: Which agent just completed
            state: Current workflow state
        
        Returns:
            Path to saved checkpoint file
        """
        try:
            # Create query-specific subdirectory
            query_hash = hash(query) % 10000  # Simple hash for directory naming
            query_dir = self.checkpoint_dir / f"query_{query_hash}"
            query_dir.mkdir(parents=True, exist_ok=True)
            
            # Create checkpoint filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"iter_{iteration:02d}_{agent}_{timestamp}.json"
            filepath = query_dir / filename
            
            # Prepare state for serialization (remove non-serializable objects)
            serializable_state = {}
            for key, value in state.items():
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    serializable_state[key] = value
                else:
                    # Skip non-serializable values
                    logger.debug(f"Skipping non-serializable field: {key} ({type(value).__name__})")
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(serializable_state, f, indent=2)
            
            logger.info(f"Checkpoint saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
            return ""
    
    def load_checkpoint(self, checkpoint_path: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from checkpoint file.
        
        Args:
            checkpoint_path: Path to checkpoint file
        
        Returns:
            Loaded state or None if failed
        """
        try:
            with open(checkpoint_path, 'r') as f:
                state = json.load(f)
            logger.info(f"Checkpoint loaded: {checkpoint_path}")
            return state
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
            return None
    
    def list_checkpoints(self, query: str) -> list:
        """List all checkpoints for a given query.
        
        Args:
            query: User query to find checkpoints for
        
        Returns:
            List of checkpoint file paths
        """
        query_hash = hash(query) % 10000
        query_dir = self.checkpoint_dir / f"query_{query_hash}"
        
        if not query_dir.exists():
            return []
        
        checkpoints = sorted(query_dir.glob("iter_*.json"))
        return [str(cp) for cp in checkpoints]
    
    def get_latest_checkpoint(self, query: str) -> Optional[str]:
        """Get the most recent checkpoint for a query.
        
        Args:
            query: User query
        
        Returns:
            Path to latest checkpoint or None
        """
        checkpoints = self.list_checkpoints(query)
        return checkpoints[-1] if checkpoints else None
    
    def cleanup_old_checkpoints(self, query: str, keep_count: int = 5):
        """Remove old checkpoints, keeping only recent ones.
        
        Args:
            query: User query
            keep_count: Number of recent checkpoints to keep
        """
        checkpoints = self.list_checkpoints(query)
        
        if len(checkpoints) > keep_count:
            to_remove = checkpoints[:-keep_count]
            for checkpoint in to_remove:
                try:
                    os.remove(checkpoint)
                    logger.debug(f"Removed old checkpoint: {checkpoint}")
                except Exception as e:
                    logger.error(f"Failed to remove checkpoint {checkpoint}: {str(e)}")
