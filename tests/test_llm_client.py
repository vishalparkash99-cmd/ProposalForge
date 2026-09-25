import json
from types import SimpleNamespace
from unittest.mock import Mock

from llm_client import request_proposal
from proposal_schema import SUBMIT_PROPOSAL_TOOL_NAME, Proposal

SECTION_VALUES = {
    "executive_summary": "Executive summary.",
    "proposed_solution": "Proposed solution.",
    "pilot_roadmap": "Pilot roadmap.",
    "why_our_company": "Company strengths.",
    "next_steps": "Next steps.",
}


def test_request_proposal_uses_a_mocked_structured_llm_call() -> None:
    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=[
                        SimpleNamespace(
                            function=SimpleNamespace(
                                name=SUBMIT_PROPOSAL_TOOL_NAME,
                                arguments=json.dumps(SECTION_VALUES),
                            )
                        )
                    ]
                )
            )
        ]
    )
    create = Mock(return_value=response)
    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    proposal = request_proposal(client, "test-model", "test prompt")

    assert isinstance(proposal, Proposal)
    assert proposal.to_dict() == SECTION_VALUES
    create.assert_called_once()
    request = create.call_args.kwargs
    assert request["model"] == "test-model"
    assert request["messages"] == [{"role": "user", "content": "test prompt"}]
    assert request["tools"][0]["function"]["name"] == SUBMIT_PROPOSAL_TOOL_NAME
    assert request["tool_choice"]["function"]["name"] == SUBMIT_PROPOSAL_TOOL_NAME
