import json
import unittest
from types import SimpleNamespace

from proposal_schema import (
    PROPOSAL_SCHEMA,
    PROPOSAL_TOOL,
    SUBMIT_PROPOSAL_TOOL_NAME,
    MalformedModelResponse,
    Proposal,
    parse_proposal_response,
)

SECTION_VALUES = {
    "executive_summary": "A concise executive summary.",
    "proposed_solution": "A practical solution architecture.",
    "pilot_roadmap": "A four-week pilot roadmap.",
    "why_our_company": "Evidence of delivery experience.",
    "next_steps": "A clear approval and kickoff path.",
}


def tool_response(arguments: object) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=[
                        SimpleNamespace(
                            function=SimpleNamespace(
                                name=SUBMIT_PROPOSAL_TOOL_NAME,
                                arguments=json.dumps(arguments),
                            )
                        )
                    ]
                )
            )
        ]
    )


class StructuredProposalTests(unittest.TestCase):
    def test_schema_declares_each_section_as_a_required_string_field(self) -> None:
        self.assertEqual(
            set(PROPOSAL_SCHEMA["properties"]), set(SECTION_VALUES)
        )
        self.assertEqual(set(PROPOSAL_SCHEMA["required"]), set(SECTION_VALUES))
        self.assertFalse(PROPOSAL_SCHEMA["additionalProperties"])
        self.assertEqual(
            PROPOSAL_TOOL["function"]["name"], SUBMIT_PROPOSAL_TOOL_NAME
        )

    def test_parses_valid_tool_arguments_into_independent_fields(self) -> None:
        proposal = parse_proposal_response(tool_response(SECTION_VALUES))

        self.assertIsInstance(proposal, Proposal)
        self.assertEqual(proposal.to_dict(), SECTION_VALUES)
        self.assertIn("Executive Summary", proposal.to_text())
        self.assertIn("Next Steps", proposal.to_text())

    def test_rejects_a_plain_text_response(self) -> None:
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=None))]
        )

        with self.assertRaisesRegex(MalformedModelResponse, "did not call"):
            parse_proposal_response(response)

    def test_rejects_missing_or_empty_sections(self) -> None:
        incomplete = dict(SECTION_VALUES)
        del incomplete["next_steps"]
        with self.assertRaisesRegex(MalformedModelResponse, "missing fields"):
            parse_proposal_response(tool_response(incomplete))

        empty = dict(SECTION_VALUES, next_steps="  ")
        with self.assertRaisesRegex(MalformedModelResponse, "non-empty string"):
            parse_proposal_response(tool_response(empty))


if __name__ == "__main__":
    unittest.main()
