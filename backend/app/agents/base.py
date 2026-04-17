"""Base Agent class for all agent implementations."""

from typing import Any, Dict
from abc import ABC, abstractmethod
from app.core.llm_factory import LLMFactory
from app.core.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, agent_role: str):
        """Initialize agent with specified role.
        
        Args:
            agent_role: Role of the agent (planner, researcher, writer, analyst, reviewer)
        """
        self.agent_role = agent_role
        self.llm = LLMFactory.get_llm(agent_role)
        logger.info(f"Initialized {agent_role} agent")
    
    @abstractmethod
    def call(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with agent's output
        """
        pass
