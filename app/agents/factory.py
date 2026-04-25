from google import adk
from app.agents.state import FlowLearnState
from app.config import settings

def create_architect():
    return adk.Agent(
        name="CurriculumArchitect",
        model=settings.gemini_model,
        instruction="""You are a curriculum designer. Create a learning guide for a given topic.
Return valid JSON matching the schema of FlowLearnState.""",
        description="Analyzes the topic and creates a structured learning path."
    )

def create_evaluator():
    return adk.Agent(
        name="FeynmanEvaluator",
        model=settings.gemini_model,
        instruction="""You are a Feynman Technique expert. 
Analyze the student's explanation for correct points, missing concepts, and misconceptions.
Focus ONLY on the analysis, not the lesson.""",
        description="Performs deep semantic audit of user explanations."
    )

def create_mentor():
    return adk.Agent(
        name="AdaptiveMentor",
        model=settings.gemini_model,
        instruction="""You are an encouraging tutor. 
Take the gaps found by the Evaluator and create a mastery score and a 3-sentence micro-lesson.
Match your vocabulary to the student's difficulty level.""",
        description="Synthesizes final feedback and remediation."
    )
