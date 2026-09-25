from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from difflib import unified_diff

BUZZWORD_DICTIONARY: tuple[str, ...] = (
    "delve",
    "tapestry",
    "testament",
    "moreover",
    "robust",
    "leverage",
    "synergy",
    "beacon",
    "embark",
    "holistic",
    "seamlessly",
    "transformative",
    "pivotal",
    "spearhead",
    "cutting-edge",
    "game-changer",
    "best-of-breed",
    "paradigm shift",
    "in conclusion",
    "navigate the landscape",
    "unlock the potential",
    "double-click",
)
DEFAULT_BUZZWORDS = BUZZWORD_DICTIONARY

_SENTENCE_BOUNDARY_RE = re.compile(r"[.!?]+[\"'”’)\]]*[ \t]*|\n+[ \t]*")
_PUNCTUATION_RE = re.compile(r"[.!?]+[\"'”’)\]]*")


@dataclass(frozen=True, slots=True)
class BuzzwordHit:
    term: str
    matched_text: str
    start: int
    end: int
    line: int
    column: int
    sentence_index: int
    sentence: str

    @property
    def location(self) -> str:
        return f"line {self.line}, column {self.column}"


SentenceRewriter = Callable[[str, Sequence[BuzzwordHit]], str | None]


@dataclass(frozen=True, slots=True)
class WordSpinnerResult:
    original_text: str
    text: str
    hits: tuple[BuzzwordHit, ...]
    diff: str
    rewrite_attempted: bool

    @property
    def changed(self) -> bool:
        return self.text != self.original_text

    @property
    def hit_count(self) -> int:
        return len(self.hits)

    @property
    def review(self) -> str:
        if self.diff:
            return self.diff
        if not self.hits:
            return "WordSpinner found no dictionary buzzwords."

        lines = [
            "WordSpinner review mode: no automatic rewrite was requested."
        ]
        for index, hit in enumerate(self.hits, start=1):
            lines.extend(
                (
                    f"Hit {index}: {hit.term!r} at {hit.location} "
                    f"(sentence {hit.sentence_index + 1})",
                    f"- Before: {hit.sentence}",
                    f"+ After:  {hit.sentence}",
                )
            )
        return "\n".join(lines)


def _normalise_term(value: str) -> str:
    return " ".join(value.casefold().split())


def _compile_dictionary(buzzwords: Sequence[str]) -> tuple[re.Pattern[str] | None, dict[str, str]]:
    cleaned = {
        _normalise_term(word): _normalise_term(word)
        for word in buzzwords
        if isinstance(word, str) and word.strip()
    }
    if not cleaned:
        return None, {}

    terms = sorted(cleaned, key=lambda word: (-len(word), word))
    alternatives = []
    for term in terms:
        alternatives.append(r"\s+".join(re.escape(part) for part in term.split()))
    pattern = re.compile(
        r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)",
        flags=re.IGNORECASE,
    )
    return pattern, cleaned


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start = 0
    for boundary in _SENTENCE_BOUNDARY_RE.finditer(text):
        punctuation = _PUNCTUATION_RE.match(boundary.group(0))
        sentence_end = (
            boundary.start() + punctuation.end()
            if punctuation is not None
            else boundary.start()
        )
        if sentence_end > start:
            spans.append((start, sentence_end))
        start = boundary.end()
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def _line_and_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    last_newline = text.rfind("\n", 0, offset)
    column = offset + 1 if last_newline == -1 else offset - last_newline
    return line, column


class WordSpinner:
    def __init__(
        self,
        buzzwords: Sequence[str] = DEFAULT_BUZZWORDS,
        rewriter: SentenceRewriter | None = None,
    ) -> None:
        self.buzzwords = tuple(buzzwords)
        self._pattern, self._canonical_terms = _compile_dictionary(self.buzzwords)
        self._rewriter = rewriter

    def detect(self, text: str) -> tuple[BuzzwordHit, ...]:
        if not text or self._pattern is None:
            return ()

        spans = _sentence_spans(text)
        hits: list[BuzzwordHit] = []
        for match in self._pattern.finditer(text):
            start, end = match.span()
            sentence_index = next(
                (
                    index
                    for index, (sentence_start, sentence_end) in enumerate(spans)
                    if sentence_start <= start and end <= sentence_end
                ),
                0,
            )
            sentence_start, sentence_end = spans[sentence_index]
            line, column = _line_and_column(text, start)
            hits.append(
                BuzzwordHit(
                    term=self._canonical_terms[_normalise_term(match.group(0))],
                    matched_text=match.group(0),
                    start=start,
                    end=end,
                    line=line,
                    column=column,
                    sentence_index=sentence_index,
                    sentence=text[sentence_start:sentence_end],
                )
            )
        return tuple(hits)

    def spin(
        self,
        text: str,
        rewriter: SentenceRewriter | None = None,
    ) -> WordSpinnerResult:
        hits = self.detect(text)
        if not hits:
            return WordSpinnerResult(text, text, hits, "", False)

        selected_rewriter = rewriter if rewriter is not None else self._rewriter
        rewrite_attempted = selected_rewriter is not None
        rewritten_text = (
            self._rewrite_flagged_sentences(text, hits, selected_rewriter)
            if selected_rewriter is not None
            else text
        )
        diff = "\n".join(
            unified_diff(
                text.splitlines(keepends=True),
                rewritten_text.splitlines(keepends=True),
                fromfile="before",
                tofile="after",
            )
        )
        return WordSpinnerResult(text, rewritten_text, hits, diff, rewrite_attempted)

    @staticmethod
    def _rewrite_flagged_sentences(
        text: str,
        hits: Sequence[BuzzwordHit],
        rewriter: SentenceRewriter,
    ) -> str:
        spans = _sentence_spans(text)
        hits_by_sentence: dict[int, list[BuzzwordHit]] = defaultdict(list)
        for hit in hits:
            hits_by_sentence[hit.sentence_index].append(hit)

        replacements: list[tuple[int, int, str]] = []
        for sentence_index in sorted(hits_by_sentence):
            sentence_start, sentence_end = spans[sentence_index]
            sentence = text[sentence_start:sentence_end]
            replacement = rewriter(
                sentence,
                tuple(hits_by_sentence[sentence_index]),
            )
            if replacement is None:
                continue
            if not isinstance(replacement, str):
                raise TypeError("Sentence rewriter must return a string or None")
            replacements.append((sentence_start, sentence_end, replacement))

        rewritten_text = text
        for sentence_start, sentence_end, replacement in reversed(replacements):
            rewritten_text = (
                rewritten_text[:sentence_start]
                + replacement
                + rewritten_text[sentence_end:]
            )
        return rewritten_text


def detect_buzzwords(
    text: str,
    buzzwords: Sequence[str] = DEFAULT_BUZZWORDS,
) -> tuple[BuzzwordHit, ...]:
    return WordSpinner(buzzwords).detect(text)


def spin_text(
    text: str,
    buzzwords: Sequence[str] = DEFAULT_BUZZWORDS,
    rewriter: SentenceRewriter | None = None,
) -> WordSpinnerResult:
    return WordSpinner(buzzwords, rewriter).spin(text)
