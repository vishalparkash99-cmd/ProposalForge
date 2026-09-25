import unittest
from unittest.mock import patch

from proposal_pipeline import generate_proposal_artifact
from proposal_schema import Proposal


class ProposalPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = Proposal(
            executive_summary="A concise executive summary.",
            proposed_solution="A practical solution architecture.",
            pilot_roadmap="A four-week pilot roadmap.",
            why_our_company="Evidence of delivery experience.",
            next_steps="A clear approval and kickoff path.",
        )

    @patch("proposal_pipeline.request_proposal")
    @patch("proposal_pipeline.create_client")
    def test_orchestrates_prompt_api_spinning_and_export(
        self,
        create_client: object,
        request_proposal: object,
    ) -> None:
        create_client.return_value = object()
        request_proposal.return_value = self.proposal

        artifact = generate_proposal_artifact(
            api_key="test-key",
            base_url="https://example.test/v1",
            model="test-model",
            company_context="Company context",
            client_name="Apex Logistics Global",
            capabilities=["Agentic AI / LLMs"],
            rfp_text="Client requirements",
            humanize_level="Standard B2B",
            enable_humanizer=True,
        )

        create_client.assert_called_once_with("test-key", "https://example.test/v1")
        request_proposal.assert_called_once()
        prompt = request_proposal.call_args.args[2]
        self.assertIn("Client requirements", prompt)
        self.assertEqual(artifact.proposal, self.proposal)
        self.assertIn("Problem Breakdown & Executive Summary", artifact.text)
        self.assertTrue(artifact.docx_data.startswith(b"PK"))
        self.assertIsNotNone(artifact.spinner_result)

    @patch("proposal_pipeline.request_proposal")
    @patch("proposal_pipeline.create_client")
    def test_skips_spinning_when_disabled(
        self,
        create_client: object,
        request_proposal: object,
    ) -> None:
        create_client.return_value = object()
        request_proposal.return_value = self.proposal

        artifact = generate_proposal_artifact(
            api_key="test-key",
            base_url="https://example.test/v1",
            model="test-model",
            company_context="Company context",
            client_name="Apex Logistics Global",
            capabilities=[],
            rfp_text="Client requirements",
            humanize_level="Standard B2B",
            enable_humanizer=False,
        )

        self.assertIsNone(artifact.spinner_result)
        self.assertEqual(artifact.text, self.proposal.to_text())


if __name__ == "__main__":
    unittest.main()
