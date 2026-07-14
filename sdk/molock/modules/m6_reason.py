# -*- coding: utf-8 -*-
"""M6: 约束内推理 — 在三锁契约内执行正式推理."""

from ..core.types import ReasonResult, RouteMode, ConstraintResult
from ..core.llm import LLMBackend


DIVERGE_REASON_PROMPT = """你是墨家推理官（发散模式）。你将在以下三锁约束的**允许维度内**充分发挥创意和联想能力。

## 你的约束契约
{constraint}

## 推理规则
1. 在词义锁定义的精确语义区间内推理，不越界
2. 在边界锁允许的维度内自由发挥创意
3. 不违反规则锁的底线约束
4. 可以合理延伸和创意发散，但不能超出约束边界

## 用户需求
{user_input}

请在约束框架内给出你的推理结果。"""


STRICT_REASON_PROMPT = """你是墨家推理官（收敛模式）。你将在以下三锁约束内进行严格推理，不允许任何形式的自由发挥。

## 你的约束契约
{constraint}

## 推理规则（零容忍）
1. 严格在词义锁定义的语义区间内推理，一字不多、一字不少
2. 绝对不越过边界锁划定的禁止推演维度
3. 严格遵守规则锁的每一条底线
4. 禁止任何形式的"额外补充"、"合理猜测"、"常识推断"
5. 只说原文信息能直接支持的结论

## 用户需求
{user_input}

请在约束框架内给出严格推理结果。"""


MIXED_REASON_PROMPT = """你是墨家推理官（混合审慎模式）。

## 你的约束契约
{constraint}

## 推理规则
1. 核心结论必须严格在约束内（词义锁+边界锁+规则锁）
2. 辅助细节可以适度展开，但不能突破约束边界
3. 任何扩展内容需标注"【推测】"前缀

## 用户需求
{user_input}

请给出平衡的推理结果。"""


REASON_TEMPLATES = {
    RouteMode.DIVERGE: DIVERGE_REASON_PROMPT,
    RouteMode.STRICT: STRICT_REASON_PROMPT,
    RouteMode.MIXED: MIXED_REASON_PROMPT,
}


class M6Reason:
    """约束内推理：在三锁契约内执行."""

    def __init__(self, llm: LLMBackend):
        self.llm = llm

    def process(
        self,
        user_input: str,
        constraint: ConstraintResult,
        mode: RouteMode,
    ) -> ReasonResult:
        """Execute reasoning within three-lock constraints."""
        template = REASON_TEMPLATES.get(mode, MIXED_REASON_PROMPT)

        system_prompt = template.format(
            constraint=constraint.full_text or "无特殊约束",
            user_input=user_input,
        )

        user_prompt = user_input

        try:
            output = self.llm.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3 if mode == RouteMode.DIVERGE else 0.0,
            )
        except Exception:
            output = "[推理执行失败，触发降级]"

        return ReasonResult(output=output, mode=mode)
