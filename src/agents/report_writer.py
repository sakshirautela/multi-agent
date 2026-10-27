from datetime import datetime
from typing import Dict, Any
from src.state import ResearchState
from src.config import call_llm

REPORT_WRITER_SYSTEM_PROMPT = """You are an Elite Technical Research Author and Report Writer.
Your task is to synthesize verified factual evidence and claims into a comprehensive, high-impact research briefing.

CRITICAL CITATION RULES:
1. Every factual statement, statistic, or technical architecture detail MUST cite its source using inline bracket tags like [S1], [S2].
2. Use ONLY the source IDs provided in the evidence context. Never invent citation tags or URLs.
3. If an assertion is speculative or lacks strong source backing, explicitly label it as unverified or an open question.
4. Conclude with a complete "References & Sources" section detailing each [S#] tag with its actual Title, Domain, and URL.

REPORT STRUCTURE REQUIRED:
# [Comprehensive Title]

## 1. Executive Summary
- Brief 2-3 paragraph synthesis of the most critical takeaways.

## 2. Key Findings & Empirical Claims
- Sourced bullet points highlighting proven outcomes, benchmarks, or consensus [S#].

## 3. In-Depth Analysis & Architectural Breakdown
- Thorough analysis of mechanisms, practical implementations, and industry patterns [S#].

## 4. Conflicting Viewpoints & Trade-Offs
- Discuss disagreements, performance overheads, or alternative methodologies identified [S#].

## 5. Limitations & Open Questions
- Areas where evidence was scarce or where further research is required.

## 6. References & Verified Sources
- [S1] [Source Title](URL) - Domain
"""


def report_writer_node(state: ResearchState) -> Dict[str, Any]:
    """
    Agent 3: Report Writer
    Synthesizes analyst evidence into a structured, cited markdown report.
    """
    topic = state.get("topic", "")
    analysis = state.get("analysis", {})
    sources = state.get("sources", {})
    status_logs = list(state.get("status_logs", []))

    status_logs.append({
        "agent": "ReportWriter",
        "message": "Synthesizing verified claims into a fully cited research report...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Prepare claims summary
    claims_list = analysis.get("claims", [])
    claims_text = "\n".join([
        f"- Claim: {c.get('claim')} | Source: [{c.get('source_id')}] | Evidence: \"{c.get('evidence_quote')}\" | Type: {c.get('category')}"
        for c in claims_list
    ])

    contradictions = analysis.get("contradictions", [])
    contradictions_text = "\n".join([f"- {c}" for c in contradictions]) if contradictions else "None observed."

    gaps = analysis.get("gaps", [])
    gaps_text = "\n".join([f"- {g}" for g in gaps]) if gaps else "None flagged."

    # Prepare sources reference table
    sources_ref_text = "\n".join([
        f"[{sid}] Title: {s.get('title')} | URL: {s.get('url')} | Domain: {s.get('domain')}"
        for sid, s in sources.items()
    ])

    user_prompt = f"""Topic: {topic}

Verified Claims & Evidence:
{claims_text or "No specific claims extracted."}

Contradictions Identified:
{contradictions_text}

Identified Gaps:
{gaps_text}

Available Source Registry:
{sources_ref_text or "No sources available."}

Write the complete research report following all citation and structuring rules.
"""

    report_markdown = call_llm(
        prompt=user_prompt,
        system_instruction=REPORT_WRITER_SYSTEM_PROMPT
    )

    # Ensure bibliography exists if model omitted it
    if "## 6. References" not in report_markdown and "## References" not in report_markdown:
        report_markdown += "\n\n## References & Verified Sources\n"
        for sid, s in sources.items():
            report_markdown += f"- [{sid}] [{s.get('title')}]({s.get('url')}) ({s.get('domain')})\n"

    status_logs.append({
        "agent": "ReportWriter",
        "message": f"Report generated successfully ({len(report_markdown.split())} words).",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    return {
        "report_markdown": report_markdown,
        "status_logs": status_logs
    }
