from __future__ import annotations

from collections.abc import Sequence

from proposal_schema import SUBMIT_PROPOSAL_TOOL_NAME

HUMANIZATION_LEVELS: tuple[str, ...] = (
    "Standard B2B",
    "Conversational Enterprise",
    "Ultra-Natural / Direct",
)


def build_humanizer_rules(humanize_level: str, enabled: bool = True) -> str:
    if not enabled:
        return ""
    return f"""
    CRITICAL INSTRUCTION - HUMANIZED WRITING STYLE ({humanize_level}):
    - Write like an experienced Principal Solutions Architect talking directly to a client executive.
    - Use short, punchy sentences mixed with clear technical explanations.
    - Use active voice, simple B2B English, and focus heavily on practical ROI and implementation realities.
    - Sound confident, grounded, and human—no corporate fluff or dramatic intros.
    """


def build_proposal_prompt(
    company_context: str,
    client_name: str,
    capabilities: Sequence[str],
    rfp_text: str,
    humanize_level: str,
    enabled_humanizer: bool = True,
    tool_name: str = SUBMIT_PROPOSAL_TOOL_NAME,
) -> str:
    humanizer_rules = build_humanizer_rules(humanize_level, enabled_humanizer)
    return f"""
    You are a Principal Enterprise Architect at the company described below.
    Generate a high-converting, professional proposal based on the following client request.

    {humanizer_rules}

    Company Context:
    {company_context}

    Client Name: {client_name}
    Selected Capabilities: {', '.join(capabilities)}

    Client Requirements:
    {rfp_text}

    Submit the completed proposal through the {tool_name} tool.
    Do not return unstructured prose. Each tool argument field must contain one complete,
    polished proposal section, and the tool schema is the source of truth.
    """
