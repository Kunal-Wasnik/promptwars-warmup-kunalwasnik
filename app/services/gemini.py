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
_ARCHITECT_INSTRUCTION = """You are the Lead Curriculum Architect for FlowLearn.
Your goal is to transform any complex topic into a clear, engaging learning path.

TASKS:
1. Provide a fascinating 2-3 sentence overview of the topic.
2. Identify 5 foundational concepts that are crucial for mastery.
3. Formulate a 'suggested_prompt' that challenges the user to explain the topic using the Feynman Technique.
4. Use the Search Tool to find 2-3 high-quality educational resources.

RESPOND ONLY with a valid JSON object using EXACTLY this structure (no extra keys, no markdown fences):
{
  "topic": "<topic name>",
  "difficulty": "<difficulty level>",
  "overview": "<fascinating overview>",
  "key_concepts": ["<concept 1>", "<concept 2>", "<concept 3>", "<concept 4>", "<concept 5>"],
  "suggested_prompt": "<Feynman Challenge prompt>",
  "links": [
    {"title": "<page title>", "url": "<full url>"}
  ]
}
"""

_EVALUATOR_INSTRUCTION = """You are the Feynman Mastery Evaluator.
Analyze the student's explanation with precision. Identify scientific accuracy, missing technical terms, and subtle misconceptions.

RESPOND ONLY with a valid JSON object using EXACTLY this structure (no extra keys, no markdown fences):
{
  "topic": "<topic name>",
  "difficulty": "<difficulty level>",
  "explanation": "<original text>",
  "correct": ["<precise correct point>"],
  "missing": ["<critical missing term or concept>"],
  "misconceptions": ["<identified misconception>"]
}"""

_MENTOR_INSTRUCTION = """You are the Adaptive Learning Mentor.
Your mission is to fill the knowledge gaps identified by the Evaluator with a rich, structured micro-lesson.

TASKS:
1. Validate the user's progress.
2. Explain the missing concepts using vivid analogies and clear examples.
3. Use Markdown (bolding, lists, headings) to make the lesson highly readable.

RESPOND ONLY with a valid JSON object using EXACTLY this structure (no extra keys, no markdown fences):
{
  "correct": ["<keep from input>"],
  "missing": ["<keep from input>"],
  "misconceptions": ["<keep from input>"],
  "micro_lesson": "<rich markdown content with headings and analogies>",
  "mastery_score": <int 0-100>,
  "encouragement": "<personalized motivational message>",
  "next_steps": "<specific actionable advice>"
}"""

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

    return json.loads(text[start:end + 1])


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

    # Normalize next_steps to always be a string
    next_steps = mentor_data.get("next_steps", "")
    if isinstance(next_steps, list):
        next_steps = " ".join(next_steps)

    return GapAnalysis(
        correct=mentor_data.get("correct", eval_data.get("correct", [])),
        missing=mentor_data.get("missing", eval_data.get("missing", [])),
        misconceptions=mentor_data.get("misconceptions", eval_data.get("misconceptions", [])),
        micro_lesson=mentor_data.get("micro_lesson", ""),
        mastery_score=int(mentor_data.get("mastery_score", 0)),
        encouragement=mentor_data.get("encouragement", ""),
        next_steps=next_steps,
    )
