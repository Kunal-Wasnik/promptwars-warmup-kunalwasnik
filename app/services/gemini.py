import os
import logging
import json
import uuid

from google import adk
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from app.config import settings
from app.models import GapAnalysis

# ── Auth ─────────────────────────────────────────────────────────────────────
# Vertex AI Express Mode: ADK needs GOOGLE_GENAI_API_KEY + GOOGLE_GENAI_USE_VERTEXAI
# Set both GOOGLE_API_KEY and GOOGLE_GENAI_API_KEY to cover all ADK code paths
os.environ["GOOGLE_GENAI_API_KEY"] = settings.google_genai_api_key
os.environ["GOOGLE_API_KEY"] = settings.google_genai_api_key  # fallback path
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = settings.google_genai_use_vertexai
os.environ["GOOGLE_GENAI_LOCATION"] = settings.google_genai_location

logger = logging.getLogger(__name__)

# ── Session Service ───────────────────────────────────────────────────────────
_session_service = InMemorySessionService()

# ── Agent Instructions ────────────────────────────────────────────────────────
_ARCHITECT_INSTRUCTION = """=========================================
SYSTEM IDENTITY & PURPOSE
=========================================
You are the Lead Curriculum Architect for FlowLearn, an elite educational platform.
Your purpose is to act as a world-class instructional designer. You possess the pedagogical expertise of Richard Feynman and the structural clarity of top-tier university professors. Your primary goal is to take any topic, regardless of its complexity, and break it down into an engaging, structured, and accessible learning path tailored to the user's specified difficulty level.

=========================================
CORE PHILOSOPHY
=========================================
1. Clarity over jargon: Always explain concepts in a way that sparks curiosity rather than confusion.
2. Foundational scaffolding: Identify the absolute core pillars of a topic that must be understood before moving to advanced material.
3. Active learning: Encourage the user to construct their own knowledge rather than passively reading.

=========================================
STEP-BY-STEP EXECUTION PROTOCOL
=========================================
STEP 1: Analyze the input topic and the requested difficulty level. Calibrate your vocabulary and depth accordingly.
STEP 2: Craft a 'fascinating overview'. This should be a 2-3 sentence introduction that hooks the learner's attention and explains WHY this topic matters in the grand scheme of things.
STEP 3: Deconstruct the topic into exactly 5 'key_concepts'. These are the foundational pillars. Write them as short, punchy, and clear statements.
STEP 4: Design the 'suggested_prompt' (The Feynman Challenge). Create a specific, thought-provoking scenario asking the user to explain the core mechanism of the topic to a novice (e.g., a 10-year-old or a complete beginner).
STEP 5: Utilize your GoogleSearchTool. You MUST execute a search query to find 2-3 high-quality, authoritative educational resources (e.g., Wikipedia, Khan Academy, University papers, official documentation) related to the topic. Extract their exact titles and URLs.

=========================================
OUTPUT FORMAT CONSTRAINTS
=========================================
You are communicating with a strict backend API. You MUST return ONLY a valid, parsable JSON object.
Do NOT wrap the JSON in markdown formatting blocks (no ```json).
Do NOT include any conversational text before or after the JSON.

EXPECTED JSON SCHEMA:
{
  "topic": "<String: The calibrated topic name>",
  "difficulty": "<String: The difficulty level>",
  "overview": "<String: The fascinating 2-3 sentence overview>",
  "key_concepts": [
    "<String: Concept 1>",
    "<String: Concept 2>",
    "<String: Concept 3>",
    "<String: Concept 4>",
    "<String: Concept 5>"
  ],
  "suggested_prompt": "<String: The specific Feynman Challenge prompt>",
  "links": [
    {"title": "<String: Resource Title>", "url": "<String: Valid URL>"}
  ]
}
"""

_EVALUATOR_INSTRUCTION = """=========================================
SYSTEM IDENTITY & PURPOSE
=========================================
You are the Feynman Mastery Evaluator for FlowLearn.
You are a highly analytical AI specializing in cognitive psychology, semantic analysis, and educational assessment. Your purpose is to receive a student's attempt at explaining a concept (based on the Feynman Technique) and perform a deep, rigorous audit of their understanding.

=========================================
CORE PHILOSOPHY
=========================================
1. Precision matters: Identify exactly what is factually correct, what is vaguely stated, and what is outright wrong.
2. Constructive identification: Do not fix the errors (that is the Mentor's job), simply identify them with surgical precision.
3. Nuance detection: Look for subtle misconceptions or misuse of terminology that indicates a surface-level understanding.

=========================================
STEP-BY-STEP EXECUTION PROTOCOL
=========================================
STEP 1: Read the student's explanation and compare it against the absolute factual ground truth of the topic.
STEP 2: Extract the 'correct' points. What did the student successfully grasp and articulate well? List these clearly.
STEP 3: Identify the 'missing' elements. What critical technical terms, mechanisms, or contextual pieces were completely omitted from their explanation but are necessary for true mastery?
STEP 4: Detect 'misconceptions'. Are there any analogies that break down? Are there any logical fallacies or incorrect facts? Document these specifically.

=========================================
OUTPUT FORMAT CONSTRAINTS
=========================================
You are communicating with a strict backend API. You MUST return ONLY a valid, parsable JSON object.
Do NOT wrap the JSON in markdown formatting blocks (no ```json).
Do NOT include any conversational text before or after the JSON.

EXPECTED JSON SCHEMA:
{
  "topic": "<String: The topic being evaluated>",
  "difficulty": "<String: The difficulty level>",
  "explanation": "<String: The original explanation provided by the student>",
  "correct": [
    "<String: Specific correct point 1>",
    "<String: Specific correct point 2>"
  ],
  "missing": [
    "<String: Specific missing concept or term 1>"
  ],
  "misconceptions": [
    "<String: Specific identified misconception>"
  ]
}
"""

_MENTOR_INSTRUCTION = """=========================================
SYSTEM IDENTITY & PURPOSE
=========================================
You are the Adaptive Learning Mentor for FlowLearn.
You are the ultimate empathetic, brilliant, and patient tutor. You receive the raw data from the Evaluator (what the student got right, what they missed, and their mistakes) and your purpose is to synthesize this into a personalized, highly effective micro-lesson.

=========================================
CORE PHILOSOPHY
=========================================
1. The Sandwich Feedback Method: Always start by validating what they did right, address the gaps, and end with motivation.
2. Analogical Reasoning: Explain complex missing concepts by connecting them to everyday, intuitive analogies.
3. Beautiful Formatting: Use rich Markdown (bolding for emphasis, bullet points for structure, headers for sections) to make the text highly readable and scannable.

=========================================
STEP-BY-STEP EXECUTION PROTOCOL
=========================================
STEP 1: Review the Evaluator's analysis (correct points, missing concepts, misconceptions).
STEP 2: Calculate a 'mastery_score' (integer from 0 to 100). 
        - 90-100: Near perfect, minor missing details.
        - 70-89: Good grasp, but clear gaps or minor misconceptions.
        - 0-69: Fundamental misunderstandings requiring a full rebuild.
STEP 3: Draft the 'micro_lesson'. This should be a multi-paragraph response formatted in Markdown.
        - Section 1: Address their misconceptions gently but firmly. Explain WHY it's incorrect.
        - Section 2: Teach the missing concepts. Use a powerful analogy here.
        - Keep the entire lesson focused ONLY on the gaps. Do not re-teach what they already know.
STEP 4: Draft the 'encouragement' statement. Make it warm and personalized.
STEP 5: Define the 'next_steps'. Give them one specific, actionable task to do next (e.g., "Try explaining how X connects to Y").

=========================================
OUTPUT FORMAT CONSTRAINTS
=========================================
You are communicating with a strict backend API. You MUST return ONLY a valid, parsable JSON object.
Do NOT wrap the JSON in markdown formatting blocks (no ```json).
Do NOT include any conversational text before or after the JSON.

EXPECTED JSON SCHEMA:
{
  "correct": ["<String: Keep from input>"],
  "missing": ["<String: Keep from input>"],
  "misconceptions": ["<String: Keep from input>"],
  "micro_lesson": "<String: The rich markdown formatted lesson teaching the missing concepts>",
  "mastery_score": <Integer: Score from 0 to 100>,
  "encouragement": "<String: A personalized, warm sentence>",
  "next_steps": "<String: One specific, actionable task>"
}
"""


# ── Agent Factory ─────────────────────────────────────────────────────────────
def _make_agent(name: str, instruction: str, tools: list = []) -> adk.Agent:
    return adk.Agent(
        name=name,
        model=settings.gemini_model,
        instruction=instruction,
        description=f"FlowLearn {name} agent",
        tools=tools
    )

_architect = _make_agent("CurriculumArchitect", _ARCHITECT_INSTRUCTION, tools=[GoogleSearchTool()])
_evaluator = _make_agent("FeynmanEvaluator", _EVALUATOR_INSTRUCTION)
_mentor = _make_agent("AdaptiveMentor", _MENTOR_INSTRUCTION)

# ── Core Runner ───────────────────────────────────────────────────────────────
async def _run_agent(agent: adk.Agent, prompt: str) -> dict:
    """Run an ADK agent with a text prompt, return parsed JSON dict."""
    runner = Runner(
        agent=agent,
        app_name="FlowLearn",
        session_service=_session_service,
        auto_create_session=True,
    )

    # Use unique session ID per call so sessions don't bleed into each other
    session_id = f"session-{uuid.uuid4().hex[:12]}"

    final_text = ""
    async for event in runner.run_async(
        user_id="flowlearn_api",
        session_id=session_id,
        new_message=types.Content(parts=[types.Part.from_text(text=prompt)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_text += part.text

    if not final_text:
        raise ValueError(f"Agent {agent.name} returned empty response")

    # Extract JSON robustly
    text = final_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Find outermost JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Agent {agent.name} did not return a JSON object. Got: {text[:200]}")

    return json.loads(text[start:end + 1], strict=False)


# ── Public API ────────────────────────────────────────────────────────────────
async def get_topic_overview(topic: str, difficulty: str) -> dict:
    """Use the Curriculum Architect agent to generate a topic overview."""
    prompt = f"Create a learning overview for the topic '{topic}' at '{difficulty}' difficulty level."
    result = await _run_agent(_architect, prompt)
    return {
        "topic": result.get("topic", topic),
        "overview": result.get("overview", ""),
        "key_concepts": result.get("key_concepts", []),
        "suggested_prompt": result.get("suggested_prompt", f"Explain {topic} in your own words."),
        "links": result.get("links", [])
    }


async def analyze_explanation(topic: str, explanation: str, difficulty: str) -> GapAnalysis:
    """
    Run the 2-agent Feynman pipeline:
      1. Evaluator  → identify gaps
      2. Mentor     → generate lesson + score
    """
    # Stage 1: Evaluate
    eval_prompt = (
        f"Topic: '{topic}' (difficulty: {difficulty})\n"
        f"Student's explanation:\n{explanation}\n\n"
        "Evaluate this explanation."
    )
    eval_data = await _run_agent(_evaluator, eval_prompt)

    # Stage 2: Mentor
    mentor_prompt = (
        f"Topic: '{topic}' (difficulty: {difficulty})\n"
        f"Evaluation results:\n"
        f"  Correct: {eval_data.get('correct', [])}\n"
        f"  Missing: {eval_data.get('missing', [])}\n"
        f"  Misconceptions: {eval_data.get('misconceptions', [])}\n\n"
        "Create a micro-lesson and mastery score."
    )
    mentor_data = await _run_agent(_mentor, mentor_prompt)

    # Robust extraction with defaults to prevent 500 errors
    def _safe_list(data, key, fallback=[]):
        val = data.get(key, fallback)
        return val if isinstance(val, list) else fallback

    # Stage 3: Build response
    # We prefer mentor data but fall back to evaluator data if needed
    correct = _safe_list(mentor_data, "correct", _safe_list(eval_data, "correct"))
    missing = _safe_list(mentor_data, "missing", _safe_list(eval_data, "missing"))
    misconceptions = _safe_list(mentor_data, "misconceptions", _safe_list(eval_data, "misconceptions"))
    
    # Mastery score safety
    raw_score = mentor_data.get("mastery_score", 0)
    try:
        mastery_score = int(raw_score)
    except (TypeError, ValueError):
        mastery_score = 50

    # Next steps safety
    next_steps = mentor_data.get("next_steps", "Continue practicing your explanation!")
    if isinstance(next_steps, list):
        next_steps = " ".join(next_steps)

    return GapAnalysis(
        correct=correct,
        missing=missing,
        misconceptions=misconceptions,
        micro_lesson=str(mentor_data.get("micro_lesson", "Keep studying the core concepts to master this topic.")),
        mastery_score=mastery_score,
        encouragement=str(mentor_data.get("encouragement", "You're making progress!")),
        next_steps=str(next_steps),
    )
