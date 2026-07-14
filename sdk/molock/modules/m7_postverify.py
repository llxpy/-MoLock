# -*- coding: utf-8 -*-
"""M7: 双源后校验 — 对照原文和约束契约进行最终校验."""

import json
from ..core.types import PostVerifyResult, VerifyStatus, RouteMode
from ..core.llm import LLMBackend


STRICT_VERIFY_PROMPT = """你是墨家后置校验官（收敛模式/零容忍）。

## 校验标准
1. **忠实度（一字不多）**：推理结果中是否存在原文没有的信息？
2. **准确性**：核心结论是否正确？逻辑是否自洽？
3. **越界检测**：是否超出了约束契约的允许范围？

出现任何一处超出原文的信息、越界推断或逻辑不自洽 → 不合格。

## 用户原文
{original}

## 约束契约
{constraint}

## 推理结果
{output}

## 输出格式
{{
  "pass": true/false,
  "violations": ["违规项1", "违规项2"],
  "reason": "简要说明"
}}
"""


LOOSE_VERIFY_PROMPT = """你是墨家后置校验官（发散模式/宽松校验）。

## 校验标准（宽松）
1. **核心语义**：核心结论是否合理？
2. **越界检测**：是否明显超出约束契约的允许范围？（合理的创意延伸不算违规）
3. **虚构检测**：是否虚构了不存在的事实？

仅在出现明显虚构、彻底越界或核心结论错误时 → 不合格。

## 用户原文
{original}

## 约束契约
{constraint}

## 推理结果
{output}

## 输出格式
{{
  "pass": true/false,
  "violations": ["违规项1"],
  "reason": "简要说明"
}}
"""


class M7PostVerify:
    """双源后校验：模式联动差异化校验."""

    MAX_RETRIES = 2

    def __init__(self, llm: LLMBackend):
        self.llm = llm

    def process(
        self,
        original_text: str,
        constraint_text: str,
        output: str,
        mode: RouteMode,
    ) -> PostVerifyResult:
        """Post-verify reasoning output against original + constraints."""

        if mode == RouteMode.STRICT:
            system_prompt = STRICT_VERIFY_PROMPT
        else:
            system_prompt = LOOSE_VERIFY_PROMPT

        user_prompt = system_prompt.format(
            original=original_text,
            constraint=constraint_text or "无特殊约束",
            output=output,
        )

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                raw = self.llm.chat_json("""请严格按JSON格式输出校验结果。""", user_prompt)
                data = json.loads(raw)
            except (json.JSONDecodeError, Exception):
                if attempt < self.MAX_RETRIES:
                    continue
                return PostVerifyResult(
                    status=VerifyStatus.FAIL,
                    violations=["校验模块异常"],
                    retry_count=attempt,
                )

            if data.get("pass", False):
                return PostVerifyResult(
                    status=VerifyStatus.PASS,
                    violations=[],
                    retry_count=attempt,
                )

            if attempt < self.MAX_RETRIES:
                continue

        return PostVerifyResult(
            status=VerifyStatus.FAIL,
            violations=data.get("violations", ["后置校验重推超限"]),
            retry_count=self.MAX_RETRIES,
        )
