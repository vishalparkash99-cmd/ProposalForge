import unittest

from wordspinner import (
    WordSpinner,
    detect_buzzwords,
    spin_text,
)


class BuzzwordDetectionTests(unittest.TestCase):
    def test_detects_case_insensitively_and_preserves_source_location(self) -> None:
        text = "We delve into a robust plan.\nMoreover, our tapestry helps."

        hits = detect_buzzwords(text)

        self.assertEqual([hit.term for hit in hits], ["delve", "robust", "moreover", "tapestry"])
        self.assertEqual([hit.line for hit in hits], [1, 1, 2, 2])
        self.assertEqual([hit.column for hit in hits], [4, 17, 1, 15])
        self.assertEqual([hit.sentence_index for hit in hits], [0, 0, 1, 1])
        self.assertEqual(hits[0].matched_text, "delve")
        self.assertEqual(hits[2].matched_text, "Moreover")

    def test_reports_repeated_occurrences_and_does_not_match_substrings(self) -> None:
        text = "Delve into development. delve; DELVE the tapestry."

        hits = WordSpinner().detect(text)

        self.assertEqual(len(hits), 4)
        self.assertEqual([hit.matched_text for hit in hits], ["Delve", "delve", "DELVE", "tapestry"])
        self.assertNotIn("development", [hit.matched_text for hit in hits])

    def test_custom_dictionary_can_replace_the_maintained_dictionary(self) -> None:
        text = "A bespoke solution."

        hits = WordSpinner(("bespoke",)).detect(text)

        self.assertEqual([hit.term for hit in hits], ["bespoke"])


class WordSpinnerRewriteTests(unittest.TestCase):
    def test_rewriter_is_called_once_per_flagged_sentence_only(self) -> None:
        calls: list[tuple[str, tuple[str, ...]]] = []

        def rewrite(sentence: str, hits: tuple[object, ...]) -> str:
            calls.append((sentence, tuple(hit.term for hit in hits)))
            return sentence.replace("delve", "examine").replace(
                "Moreover,", "Also,"
            )

        text = (
            "We delve into a robust plan. This sentence stays unchanged.\n"
            "Moreover, we leverage the existing platform."
        )

        result = spin_text(text, rewriter=rewrite)

        self.assertEqual(
            calls,
            [
                ("We delve into a robust plan.", ("delve", "robust")),
                ("Moreover, we leverage the existing platform.", ("moreover", "leverage")),
            ],
        )
        self.assertEqual(
            result.text,
            "We examine into a robust plan. This sentence stays unchanged.\n"
            "Also, we leverage the existing platform.",
        )
        self.assertTrue(result.changed)
        self.assertIn("--- before", result.diff)
        self.assertIn("+++ after", result.diff)

    def test_review_mode_keeps_source_and_returns_visible_before_after(self) -> None:
        result = spin_text("We must delve into this requirement.")

        self.assertFalse(result.changed)
        self.assertEqual(result.hit_count, 1)
        self.assertIn("- Before: We must delve into this requirement.", result.review)
        self.assertIn("+ After:  We must delve into this requirement.", result.review)

    def test_no_hits_does_not_invoke_rewriter(self) -> None:
        calls: list[str] = []

        def rewrite(sentence: str, hits: tuple[object, ...]) -> str:
            calls.append(sentence)
            return sentence

        result = spin_text("A direct sentence with no flagged language.", rewriter=rewrite)

        self.assertEqual(calls, [])
        self.assertEqual(result.hits, ())
        self.assertEqual(result.review, "WordSpinner found no dictionary buzzwords.")


if __name__ == "__main__":
    unittest.main()
