from typing import Literal
from langgraph.graph import StateGraph, START, END
from src.state import ResearchState
from src.agents.orchestrator import orchestrator_node
from src.agents.researcher import researcher_node
from src.agents.analyst import analyst_node
from src.agents.report_writer import report_writer_node
from src.agents.validator import validator_node


def loop_incrementer_node(state: ResearchState) -> dict:
    """Increments the iteration counter before re-entering researcher."""
    current_loop = state.get("loop_count", 0)
    return {"loop_count": current_loop + 1}


def route_analyst_decision(state: ResearchState) -> Literal["loop_incrementer", "report_writer"]:
    """
    Decides whether to perform an additional search round based on evidence completeness.
    """
    analysis = state.get("analysis", {})
    loop_count = state.get("loop_count", 0)
    max_loops = state.get("max_loops", 2)
    needs_more = analysis.get("needs_more_research", False)
    new_queries = state.get("search_queries", [])

    if needs_more and new_queries and loop_count < max_loops:
        return "loop_incrementer"
    return "report_writer"


def build_research_graph():
    """
    Constructs and compiles the complete multi-agent LangGraph workflow.
    """
    builder = StateGraph(ResearchState)

    # Register Nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("loop_incrementer", loop_incrementer_node)
    builder.add_node("report_writer", report_writer_node)
    builder.add_node("validator", validator_node)

    # Standard Edges
    builder.add_edge(START, "orchestrator")
    builder.add_edge("orchestrator", "researcher")
    builder.add_edge("researcher", "analyst")

    # Conditional Routing from Analyst
    builder.add_conditional_edges(
        "analyst",
        route_analyst_decision,
        {
            "loop_incrementer": "loop_incrementer",
            "report_writer": "report_writer"
        }
    )

    builder.add_edge("loop_incrementer", "researcher")
    builder.add_edge("report_writer", "validator")
    builder.add_edge("validator", END)

    return builder.compile()


# Pre-compiled workflow graph instance
research_graph = build_research_graph()
