"""
Mock LLM for development and testing
Allows full system testing without hitting API quotas
"""
from typing import Optional, Any
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult
from langchain_core.messages import AIMessage

class MockLLM(BaseLLM):
    """Mock LLM that returns predefined responses for testing."""
    
    agent_role: str = "mock"
    
    def _generate(
        self,
        prompts: list[str],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate mock responses based on agent role."""
        
        outputs = []
        
        for prompt in prompts:
            # Predefined responses per agent role
            responses = {
                "planner": "I will break down this task into clear planning steps: 1) Analyze requirements 2) Design solution 3) Create implementation plan.",
                "researcher": "Based on my research, here are the key findings: • Important insight 1 • Important insight 2 • Important insight 3",
                "analyst": "Analysis complete. Key metrics: • Performance: High • Efficiency: Optimal • Status: Ready",
                "writer": "Here is the detailed content:\n\nIntroduction: This provides context.\n\nBody: This explains the main points.\n\nConclusion: This summarizes findings.",
                "reviewer": "Review Status: ✓ Quality is excellent ✓ Meets requirements ✓ Ready for deployment",
            }
            
            response = responses.get(self.agent_role, responses["planner"])
            
            outputs.append(
                LLMResult(
                    generations=[[AIMessage(content=response)]],
                )
            )
        
        return LLMResult(generations=[output.generations[0] for output in outputs])
    
    @property
    def _llm_type(self) -> str:
        return "mock"
    
    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"agent_role": self.agent_role}

    def invoke(self, input: str, **kwargs) -> Any:
        """Invoke the mock LLM."""
        responses = {
            "planner": "Planning task: 1) Analyze requirements 2) Design approach 3) Create plan",
            "researcher": "Research findings: Key insight A, Key insight B, Key insight C",
            "analyst": "Analysis: Performance is high, metrics are optimal",
            "writer": "Written content: Introduction, Body paragraphs, Conclusion",
            "reviewer": "Review status: ✓ Quality approved ✓ Ready for deployment",
        }
        response_text = responses.get(self.agent_role, responses["planner"])
        return AIMessage(content=response_text)
