import unittest

from prompts import build_humanizer_rules, build_proposal_prompt


class PromptConstructionTests(unittest.TestCase):
    def test_builds_a_complete_structured_output_prompt(self) -> None:
        prompt = build_proposal_prompt(
            company_context="A regulated enterprise engineering firm.",
            client_name="Apex Logistics Global",
            capabilities=["Agentic AI / LLMs", "Cloud & Enterprise Architecture"],
            rfp_text="Reduce manual reconciliation effort.",
            humanize_level="Conversational Enterprise",
        )

        self.assertIn("A regulated enterprise engineering firm.", prompt)
        self.assertIn("Apex Logistics Global", prompt)
        self.assertIn("Agentic AI / LLMs, Cloud & Enterprise Architecture", prompt)
        self.assertIn("Reduce manual reconciliation effort.", prompt)
        self.assertIn("submit_proposal", prompt)
        self.assertIn("Do not return unstructured prose.", prompt)

    def test_disabled_humanizer_omits_style_rules(self) -> None:
        rules = build_humanizer_rules("Standard B2B", enabled=False)

        self.assertEqual(rules, "")


if __name__ == "__main__":
    unittest.main()
