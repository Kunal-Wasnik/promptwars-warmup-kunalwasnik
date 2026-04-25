from pydantic import BaseModel, Field
from typing import List, Optional, Union

class FlowLearnState(BaseModel):
    """The shared state passed between agents in the FlowLearn ADK workflow."""
    topic: str
    difficulty: str
    
    # Curriculum Architect Output
    overview: Optional[str] = None
    key_concepts: List[str] = Field(default_factory=list)
    suggested_prompt: Optional[str] = None
    
    # Feynman Evaluator Output
    explanation: Optional[str] = None
    correct: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    
    # Adaptive Mentor Output
    micro_lesson: Optional[str] = None
    mastery_score: int = 0
    encouragement: Optional[str] = None
    next_steps: Optional[Union[str, List[str]]] = None
