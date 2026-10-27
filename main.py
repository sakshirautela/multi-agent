import os
import sys
import re
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from src.config import config
from src.graph import research_graph

console = Console()


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', cleaned)[:50]


def run_research(topic: str, save_report: bool = True):
    active_prov = config.active_provider.upper()
    active_mod = config.openai_model if config.active_provider == "openai" else config.gemini_model
    console.print(Panel.fit(
        f"[bold cyan]Multi-Agent AI Research Assistant[/bold cyan]\n"
        f"[dim]Topic:[/dim] [bold white]{topic}[/bold white]\n"
        f"[dim]LLM Provider:[/dim] {active_prov} ({active_mod}) | "
        f"[dim]Search Engine:[/dim] {'Tavily (Active)' if config.tavily_api_key else 'DuckDuckGo Fallback (Active)'} | "
        f"[dim]Max Loops:[/dim] {config.max_research_loops}",
        title="[bold green]Workflow Initialized[/bold green]",
        border_style="cyan"
    ))

    initial_state = {
        "topic": topic,
        "sub_questions": [],
        "search_queries": [],
        "sources": {},
        "analysis": {},
        "loop_count": 0,
        "max_loops": config.max_research_loops,
        "report_markdown": "",
        "validation": {},
        "status_logs": []
    }

    final_state = initial_state
    with console.status("[bold yellow]Multi-agent research in progress...", spinner="dots") as status:
        for output in research_graph.stream(initial_state):
            for node_name, node_state in output.items():
                logs = node_state.get("status_logs", [])
                latest_msg = logs[-1]["message"] if logs else f"Completed {node_name}"
                status.update(f"[bold cyan][{node_name.upper()}][/bold cyan] {latest_msg}")
                console.print(f"  [green]✓[/green] [bold]{node_name}[/bold]: {latest_msg}")
                final_state.update(node_state)

    console.print()
    console.rule("[bold green]Research Complete[/bold green]")

    # Print summary statistics table
    sources = final_state.get("sources", {})
    analysis = final_state.get("analysis", {})
    validation = final_state.get("validation", {})
    claims = analysis.get("claims", [])

    table = Table(title="Execution Summary", border_style="dim")
    table.add_column("Metric", style="cyan")
    table.add_column("Count / Status", style="green")

    table.add_row("Total Verified Sources", str(len(sources)))
    table.add_row("Extracted Claims", str(len(claims)))
    table.add_row("Research Loops Executed", str(final_state.get("loop_count", 0)))
    table.add_row("Total Citations Checked", str(validation.get("total_citations_found", 0)))
    table.add_row("Citation Audit Passed", "YES" if validation.get("passed", False) else "WARNINGS FLAGGED")

    console.print(table)
    console.print()

    # Display Report
    report_md = final_state.get("report_markdown", "")
    console.print(Panel(Markdown(report_md), title="[bold]Final Research Report[/bold]", border_style="green"))

    # Save to disk
    if save_report and report_md:
        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = sanitize_filename(topic)
        filename = f"{slug}_{timestamp}.md"
        filepath = os.path.join(reports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_md)

        console.print(f"\n[bold green]Report saved to:[/bold green] [underline]{filepath}[/underline]\n")

    return final_state


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_topic = " ".join(sys.argv[1:])
    else:
        console.print("[bold yellow]Enter a research topic[/bold yellow] (e.g. 'Latest developments in AI Agents and Multi-Agent Orchestration'):")
        query_topic = input("> ").strip()
        if not query_topic:
            query_topic = "Latest developments in Multi-Agent AI Architectures"

    run_research(query_topic)
