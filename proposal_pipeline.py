from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from export import export_proposal_docx
from llm_client import create_client, request_proposal
from prompts import build_proposal_prompt
from proposal_schema import Proposal
from wordspinner import WordSpinner, WordSpinnerResult


@dataclass(frozen=True, slots=True)
class ProposalArtifact:
    proposal: Proposal
    text: str
    spinner_result: WordSpinnerResult | None
    docx_data: bytes


def generate_proposal_artifact(
    api_key: str,
    base_url: str,
    model: str,
    company_context: str,
    client_name: str,
    capabilities: Sequence[str],
    rfp_text: str,
    humanize_level: str,
    enable_humanizer: bool,
) -> ProposalArtifact:
    prompt = build_proposal_prompt(
        company_context=company_context,
        client_name=client_name,
        capabilities=capabilities,
        rfp_text=rfp_text,
        humanize_level=humanize_level,
        enabled_humanizer=enable_humanizer,
    )
    client = create_client(api_key, base_url)
    proposal = request_proposal(client, model, prompt)
    text = proposal.to_text()
    spinner_result = WordSpinner().spin(text) if enable_humanizer else None
    docx_data = export_proposal_docx(proposal, client_name)
    return ProposalArtifact(
        proposal=proposal,
        text=spinner_result.text if spinner_result is not None else text,
        spinner_result=spinner_result,
        docx_data=docx_data,
    )
