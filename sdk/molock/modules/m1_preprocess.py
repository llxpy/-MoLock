# -*- coding: utf-8 -*-
"""M1: 预处理与防注入 — 纯规则模块，无LLM调用."""

import re
from ..core.types import PreprocessResult, PreprocessStatus
from ..data.injection_patterns import (
    INJECTION_PATTERNS, CONFLICT_PATTERNS
)


class M1Preprocess:
    """Input cleaning, injection detection, completeness check, conflict marking."""

    def __init__(self):
        self.blocked_reason = ""

    def process(self, raw_input: str) -> PreprocessResult:
        """Run full preprocessing pipeline."""
        if not raw_input or not raw_input.strip():
            return PreprocessResult(
                status=PreprocessStatus.INCOMPLETE,
                cleaned_input="",
                raw_input=raw_input,
                missing_dimensions=["主体", "目标", "场景"],
            )

        # Step 1: Clean text
        cleaned = self._clean(raw_input)

        # Step 2: Injection detection
        injection, pattern = self._detect_injection(cleaned)
        if injection:
            return PreprocessResult(
                status=PreprocessStatus.BLOCKED,
                cleaned_input=cleaned,
                raw_input=raw_input,
                injection_detected=True,
                injection_pattern=pattern,
            )

        # Step 3: Completeness check
        missing = self._check_completeness(cleaned)
        if len(missing) >= 2:
            return PreprocessResult(
                status=PreprocessStatus.INCOMPLETE,
                cleaned_input=cleaned,
                raw_input=raw_input,
                missing_dimensions=missing,
            )

        # Step 4: Conflict detection
        conflicts = self._detect_conflicts(cleaned)
        status = PreprocessStatus.CONFLICT if conflicts else PreprocessStatus.PASS

        return PreprocessResult(
            status=status,
            cleaned_input=cleaned,
            raw_input=raw_input,
            conflicts=conflicts,
            missing_dimensions=missing,
        )

    def _clean(self, text: str) -> str:
        """Remove noise, normalize whitespace."""
        # Remove zero-width and invisible characters
        text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove markdown code fences in plain text
        text = re.sub(r'```[\s\S]*?```', '', text)
        return text.strip()

    def _detect_injection(self, text: str) -> tuple:
        """Check for prompt injection patterns."""
        for pattern in INJECTION_PATTERNS:
            match = pattern.search(text)
            if match:
                return True, match.group(0)
        return False, None

    def _check_completeness(self, text: str) -> list[str]:
        """Check if essential dimensions are present."""
        missing = []
        # Subject: anything that could be the actor
        has_subject = bool(re.search(
            r'(我|我们|你|您|他|她|他们|帮|请|希望|要|想|需要|设计|创建|生成|查询|分析|写|画|制作)', text
        ))
        if not has_subject:
            missing.append("主体（谁要做 / 为谁做）")

        # Goal: anything that could be a target outcome
        has_goal = len(text) >= 6  # At minimum, enough characters for a goal
        if not has_goal:
            missing.append("目标（要达成什么结果）")

        return missing

    def _detect_conflicts(self, text: str) -> list[str]:
        """Detect semantic conflicts like opposing styles/scopes."""
        conflicts = []
        for group_a, group_b, conflict_type in CONFLICT_PATTERNS:
            hit_a = any(w in text for w in group_a)
            hit_b = any(w in text for w in group_b)
            if hit_a and hit_b:
                a_word = next(w for w in group_a if w in text)
                b_word = next(w for w in group_b if w in text)
                conflicts.append(f"[[CONFLICT:{conflict_type}]] {a_word} vs {b_word}")
        return conflicts
