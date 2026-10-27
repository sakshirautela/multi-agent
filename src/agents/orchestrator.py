import json
import re
from datetime import datetime
from typing import Dict, Any
from src.state import ResearchState
from src.config import call_llm

ORCHESTRATOR_SYSTEM_PROMPT = """You are a Principal AI Research Orchestrator.
Your goal is to break down a user's research topic into structured investigative angles.

You must respond ONLY with a valid JSON object with the following schema:
{
  "sub_questions": [
    "Question exploring core mechanisms, architecture, or definitions",
    "Question exploring concrete practical implementations or benchmarks",
    "Question exploring challenges, limitations, or opposing viewpoints"
  ],
  "search_queries": [
    "optimized web search query 1",
    "optimized web search query 2",
    "optimized web search query 3"
  ]
}

Guidelines:
1. Make search queries concise, specific, and keyword-rich (avoid full conversational questions for queries).
2. Cover foundational aspects as well as the latest cutting-edge developments.
3. Return raw JSON without markdown codeblock backticks if possible, or inside standard ```json.
"""


def orchestrator_node(state: ResearchState) -> Dict[str, Any]:
    """
    Analyzes the user's research topic and generates sub-questions and initial search queries.
    """
    topic = state.get("topic", "").strip()
    status_logs = list(state.get("status_logs", []))

    status_logs.append({
        "agent": "Orchestrator",
        "message": f"Decomposing research topic: '{topic}'",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    user_prompt = f"Decompose this research topic into 3-4 sub-questions and search queries:\nTopic: {topic}"

    response_text = call_llm(
        prompt=user_prompt,
        system_instruction=ORCHESTRATOR_SYSTEM_PROMPT,
        json_mode=True
    )

    # Clean JSON markdown if present
    cleaned = response_text.strip()
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        cleaned = match.group(0)

    try:
        data = json.loads(cleaned)
        sub_questions = data.get("sub_questions", [
            f"What are the foundations of {topic}?",
            f"What are key implementations and case studies for {topic}?",
            f"What are limitations and challenges of {topic}?"
        ])
        search_queries = data.get("search_queries", [
            f"{topic} architecture overview",
            f"{topic} implementation benchmarks",
            f"{topic} limitations and challenges"
        ])
    except Exception as e:
        # Fallback if model returned unstructured text
        sub_questions = [
            f"What is {topic} and how does it work?",
            f"What are modern best practices and implementations for {topic}?",
            f"What are limitations and open challenges regarding {topic}?"
        ]
        search_queries = [
            f"{topic} latest developments",
            f"{topic} architecture analysis",
            f"{topic} comparison and trade-offs"
        ]

    status_logs.append({
        "agent": "Orchestrator",
        "message": f"Generated {len(sub_questions)} sub-questions and {len(search_queries)} search queries.",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "sub_questions": sub_questions,
        "search_queries": search_queries,
        "status_logs": status_logs
    }
