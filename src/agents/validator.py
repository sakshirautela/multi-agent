import re
from datetime import datetime
from typing import Dict, Any, List
from src.state import ResearchState


def validator_node(state: ResearchState) -> Dict[str, Any]:
    """
    Auditor Agent:
    Validates all in-text citations against the verified source registry,
    detecting any hallucinated tags or orphan citations.
    """
    report_text = state.get("report_markdown", "")
    sources = state.get("sources", {})
    status_logs = list(state.get("status_logs", []))

    status_logs.append({
        "agent": "Validator",
        "message": "Auditing report for citation integrity and reference fidelity...",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    # Find all source citation tokens like [S1], [S2] in the report
    citation_pattern = r"\[(S\d+)\]"
    found_tokens = list(set(re.findall(citation_pattern, report_text)))

    valid_citations: List[str] = []
    invalid_citations: List[str] = []

    for token in found_tokens:
        if token in sources:
            valid_citations.append(token)
        else:
            invalid_citations.append(token)

    passed = len(invalid_citations) == 0
    total_found = len(found_tokens)

    notes = ""
    if invalid_citations:
        notes = f"Warning: Found {len(invalid_citations)} unverified citation tags ({', '.join(invalid_citations)})."
    else:
        notes = f"Audit Passed: All {total_found} citations successfully matched to real verified sources."

    status_logs.append({
        "agent": "Validator",
        "message": notes,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

    validation_result = {
        "total_citations_found": total_found,
        "valid_citations": valid_citations,
        "invalid_citations": invalid_citations,
        "passed": passed,
        "notes": notes
    }

    # Append validation certificate badge to report
    badge = (
        f"\n\n---\n"
        f"**Research Assistant Audit Certificate**:\n"
        f"- Verified Sources: `{len(sources)}`\n"
        f"- Total In-Text Citations Checked: `{total_found}`\n"
        f"- Citation Integrity Status: `{'PASSED (100% verified)' if passed else 'WARNING (unsupported tags detected)'}`\n"
    )
    if invalid_citations:
        badge += f"- Flagged Unverified References: `{', '.join(invalid_citations)}`\n"

    updated_report = report_text + badge

    return {
        "validation": validation_result,
        "report_markdown": updated_report,
        "status_logs": status_logs
    }
