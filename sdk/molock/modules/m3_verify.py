# -*- coding: utf-8 -*-
"""M3: 经文自检 — 防失真，逐条比对关键条件."""

import json
from ..core.types import VerifyResult, VerifyStatus, CanonResult
from ..core.llm import LLMBackend


VERIFY_SYSTEM_PROMPT = """你是墨家经文质检官。你的任务是：以挑剔的视角，逐条检查经文是否有信息丢失、语义漂移或擅自加料。

## 检查标准
1. **条件完整性**：原文中每个关键限定条件是否都被保留在经文中？
2. **禁止加料**：经文中是否存在原文没有的诉求、引申或扩展？
3. **语义准确性**：经文中的每个表述是否与原文对应部分语义一致？
4. **禁止扩义**：是否有将具体需求泛化的现象？

## 判定规则
- 存在任何条件丢失 → 不合格
- 存在任何擅自加料 → 不合格
- 存在语义扭曲/扩义 → 不合格
- 全部通过 → 合格

## 输出格式
{
  "verified": true/false,
  "issues": ["若有问题，列出具体问题描述"],
  "score": 1-5分（5=完美保留，1=严重失真）
}
"""


class M3CanonVerify:
    """经文自检：挑剔视角逐条审核，防止失真."""

    MAX_RETRIES = 2

    def __init__(self, llm: LLMBackend):
        self.llm = llm

    def process(
        self,
        original_text: str,
        canon_result: CanonResult,
    ) -> VerifyResult:
        """Verify canon against original text. Retry up to MAX_RETRIES times."""
        for attempt in range(self.MAX_RETRIES + 1):
            user_prompt = (
                f"## 原文\n{original_text}\n\n"
                f"## 经文\n{canon_result.canon_text}\n\n"
                f"## 保留条件清单\n" +
                "\n".join(f"- {c}" for c in canon_result.preserved_conditions)
            )

            try:
                raw = self.llm.chat_json(VERIFY_SYSTEM_PROMPT, user_prompt)
                data = json.loads(raw)
            except (json.JSONDecodeError, Exception):
                continue

            verified = data.get("verified", False)
            issues = data.get("issues", [])

            if verified:
                return VerifyResult(
                    status=VerifyStatus.PASS,
                    verified=True,
                    issues=issues,
                    retry_count=attempt,
                )

            # If not verified and retries remain, the canon should be regenerated
            # In this simple SDK, we just flag the failure
            if attempt < self.MAX_RETRIES:
                continue

        # All retries exhausted
        return VerifyResult(
            status=VerifyStatus.FAIL,
            verified=False,
            issues=["经文自检重试超限，触发一级降级"],
            retry_count=self.MAX_RETRIES,
        )
