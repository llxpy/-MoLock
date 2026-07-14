# -*- coding: utf-8 -*-
"""M5: 动态意图路由 v2.0 — 8层判定流水线，纯规则（无需LLM）."""

import re
from ..core.types import RouteResult, RouteMode
from ..data.injection_patterns import (
    DIVERGE_WORDS, STRICT_WORDS,
    NEGATION_WORDS, INFORMAL_DIVERGE,
    PROTECTED_TERMS, IMPLICIT_DIVERGE,
)


class M5IntentRouter:
    """Dynamic intent routing: 8-layer pipeline + manual override."""

    def __init__(self):
        self.previous_mode: RouteMode | None = None

    def process(
        self,
        cleaned_input: str,
        user_override: str | None = None,
    ) -> RouteResult:
        """Route user intent to diverge/strict/mixed mode."""

        # Layer 0: Manual override (highest priority)
        if user_override:
            mode_map = {
                "diverge": RouteMode.DIVERGE,
                "strict": RouteMode.STRICT,
                "mixed": RouteMode.MIXED,
            }
            mode = mode_map.get(user_override, RouteMode.MIXED)
            self.previous_mode = mode
            return RouteResult(
                mode=mode,
                confidence=1.0,
                diagnostics={"reason": "manual_override", "override": user_override},
                user_override=user_override,
            )

        text = cleaned_input
        diagnostics = {}

        # Layer 0: Negation prefix detection
        negated_diverges, negated_stricts, negation_spans = self._detect_negation(text)
        diagnostics["negated_diverges"] = negated_diverges
        diagnostics["negated_stricts"] = negated_stricts

        # Layer 1: Informal diverge phrases (force diverge)
        for phrase in INFORMAL_DIVERGE:
            if phrase in text:
                self.previous_mode = RouteMode.DIVERGE
                return RouteResult(
                    mode=RouteMode.DIVERGE,
                    confidence=0.95,
                    diagnostics={"reason": "informal_diverge", "phrase": phrase},
                )

        # Layer 2: Implicit intent heuristics
        implicit_score = 0.0
        for pattern, weight in IMPLICIT_DIVERGE:
            if re.search(pattern, text):
                implicit_score += weight
        diagnostics["implicit_score"] = implicit_score

        # Layer 3: Protected terms (don't split)
        protected_hits = [t for t in PROTECTED_TERMS if t in text]
        diagnostics["protected_hits"] = protected_hits

        # Temporarily mask protected terms
        masked_text = text
        for i, term in enumerate(protected_hits):
            masked_text = masked_text.replace(term, f"__PROTECTED_{i}__")

        # Layer 4: Word table scan
        diverge_score = 0.0
        strict_score = 0.0
        diverge_hits = []
        strict_hits = []

        for word, weight in DIVERGE_WORDS.items():
            if word in masked_text:
                # Check if this word is in a negation span
                if self._in_negation_span(word, text, negation_spans, NEGATION_WORDS):
                    continue
                diverge_score += weight
                diverge_hits.append(word)

        for word, weight in STRICT_WORDS.items():
            if word in masked_text:
                if self._in_negation_span(word, text, negation_spans, NEGATION_WORDS):
                    continue
                strict_score += weight
                strict_hits.append(word)

        # Layer 6: Negation-adjusted recount
        diagnostics["diverge_score"] = diverge_score
        diagnostics["strict_score"] = strict_score
        diagnostics["diverge_hits"] = diverge_hits
        diagnostics["strict_hits"] = strict_hits

        # Layer 7: Short text adaptation
        text_len = len(text)
        if text_len <= 3 and self.previous_mode:
            # Inherit previous mode for very short texts
            return RouteResult(
                mode=self.previous_mode,
                confidence=0.6,
                diagnostics={"reason": "short_text_inheritance", **diagnostics},
            )

        # Layer 8: Final decision
        if implicit_score >= 0.9:
            mode = RouteMode.DIVERGE
            reason = "implicit_intent"
        elif diverge_score > strict_score * 1.2:
            mode = RouteMode.DIVERGE
            reason = "diverge_dominant"
        elif strict_score > diverge_score * 1.2:
            mode = RouteMode.STRICT
            reason = "strict_dominant"
        else:
            mode = RouteMode.MIXED
            reason = "balanced"

        confidence = abs(diverge_score - strict_score) / max(diverge_score + strict_score, 1)

        self.previous_mode = mode
        return RouteResult(
            mode=mode,
            confidence=round(min(confidence, 1.0), 2),
            diagnostics={"reason": reason, **diagnostics},
        )

    def _detect_negation(self, text: str) -> tuple[list, list, list]:
        """Detect negation words and their scope."""
        negated_diverges = []
        negated_stricts = []
        spans = []

        for neg in sorted(NEGATION_WORDS, key=len, reverse=True):
            idx = text.find(neg)
            if idx >= 0:
                # Determine scope: from neg word to next punctuation
                after = text[idx + len(neg):]
                end_match = re.search(r'[，。,\.\s;；！!？?、]', after)
                end = idx + len(neg) + (end_match.start() if end_match else len(after))
                spans.append((idx, end, neg))

                # Check what's in the scope
                scope = text[idx + len(neg):end]
                for word in DIVERGE_WORDS:
                    if word in scope:
                        negated_diverges.append(word)
                for word in STRICT_WORDS:
                    if word in scope:
                        negated_stricts.append(word)

        return negated_diverges, negated_stricts, spans

    def _in_negation_span(
        self, word: str, text: str, spans: list, negation_words: list
    ) -> bool:
        """Check if a word falls within a detected negation span."""
        idx = text.find(word)
        if idx < 0:
            return False
        for start, end, neg in spans:
            if start <= idx < end:
                return True
        return False

    def reset(self):
        """Reset previous mode state (for new conversations)."""
        self.previous_mode = None
