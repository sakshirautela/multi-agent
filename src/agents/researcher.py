from datetime import datetime
from typing import Dict, Any
from src.state import ResearchState
from src.tools.search import search_web_queries


def researcher_node(state: ResearchState) -> Dict[str, Any]:
    """
    Agent 1: Researcher
    Executes web searches for active queries, deduplicates, and compiles structured source cards.
    """
    search_queries = state.get("search_queries", [])
    existing_sources = state.get("sources", {})
    status_logs = list(state.get("status_logs", []))
    loop_count = state.get("loop_count", 0)

    round_label = f"(Round {loop_count + 1})" if loop_count > 0 else "(Initial Round)"
    status_logs.append({
        "agent": "Researcher",
        "message": f"Executing search {round_label} for {len(search_queries)} queries...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Execute search with deduplication
    updated_sources = search_web_queries(
        queries=search_queries,
        max_results_per_query=3,
        existing_sources=existing_sources
    )

    new_count = len(updated_sources) - len(existing_sources)
    status_logs.append({
        "agent": "Researcher",
        "message": f"Retrieved {new_count} new distinct sources. Total indexed sources: {len(updated_sources)}.",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "sources": updated_sources,
        "status_logs": status_logs
    }
