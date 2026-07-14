# -*- coding: utf-8 -*-
"""MoLock Pipeline — 墨学经说双链推理编排器.

Orchestrates the 7-module sequential pipeline with 3-level degradation.
"""

from .types import (
    PipelineResult, PreprocessStatus, VerifyStatus,
    DegradationLevel, RouteMode,
)
from .llm import LLMBackend
from ..modules.m1_preprocess import M1Preprocess
from ..modules.m2_canon import M2CanonCondense
from ..modules.m3_verify import M3CanonVerify
from ..modules.m4_constraint import M4Constraint
from ..modules.m5_router import M5IntentRouter
from ..modules.m6_reason import M6Reason
from ..modules.m7_postverify import M7PostVerify


class MoLockPipeline:
    """Complete MoLock dual-chain semantic constraint pipeline.

    Usage:
        from molock import MoLock

        molock = MoLock(api_key="sk-...")
        result = molock.process("你的问题")
        print(result.final_output)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        temperature: float = 0.0,
        verbose: bool = False,
    ):
        """Initialize MoLock pipeline.

        Args:
            api_key: OpenAI-compatible API key.
            base_url: API base URL. Defaults to DeepSeek.
            model: Model name.
            temperature: Default temperature for LLM calls.
            verbose: Print pipeline progress to stdout.
        """
        self.verbose = verbose
        self.llm = LLMBackend(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
        )

        # Initialize all modules
        self.m1 = M1Preprocess()
        self.m2 = M2CanonCondense(self.llm)
        self.m3 = M3CanonVerify(self.llm)
        self.m4 = M4Constraint(self.llm)
        self.m5 = M5IntentRouter()
        self.m6 = M6Reason(self.llm)
        self.m7 = M7PostVerify(self.llm)

    def process(
        self,
        text: str,
        mode_override: str | None = None,
    ) -> PipelineResult:
        """Run the full MoLock pipeline on user input.

        Args:
            text: User's raw input text.
            mode_override: Optional manual override for routing mode.
                One of: 'diverge', 'strict', 'mixed'.

        Returns:
            PipelineResult with structured output and all module results.
        """
        result = PipelineResult()

        # ── M1: Preprocess ──
        self._log("[M1] 预处理与防注入...")
        preprocess = self.m1.process(text)
        result.preprocess = preprocess

        if preprocess.status == PreprocessStatus.BLOCKED:
            result.final_output = "检测到潜在指令注入，已拒绝执行。请用正常需求描述重试。"
            result.error = "injection_blocked"
            return result

        if preprocess.status == PreprocessStatus.INCOMPLETE:
            missing = "、".join(preprocess.missing_dimensions)
            result.final_output = (
                f"您的需求中以下信息尚不完整，请补充：{missing}。\n补充后我将立即启动推理。"
            )
            result.error = "incomplete_input"
            return result

        cleaned_input = preprocess.cleaned_input

        # ── M2: Canon Condensation ──
        self._log("[M2] 经层凝练...")
        canon = self.m2.process(preprocess)
        result.canon = canon
        result.canon_text = canon.canon_text

        # ── M3: Canon Self-Verify ──
        self._log("[M3] 经文自检...")
        verify = self.m3.process(cleaned_input, canon)
        result.canon_verify = verify

        # Degradation trigger: M3 failed → L2
        if verify.status == VerifyStatus.FAIL:
            self._log("  ⚠ 经文自检失败，触发 L2 一级降级")
            result.degradation_level = DegradationLevel.L2
            result.degradation_reason = "经文自检重试超限"
            # L2: Use original text, skip canon
            result.canon_text = cleaned_input
        else:
            result.canon_text = canon.canon_text

        # ── M4: Constraint Generation ──
        self._log("[M4] 说层三锁约束...")
        constraint = self.m4.process(
            original_text=cleaned_input,
            canon_text=result.canon_text if result.degradation_level == DegradationLevel.L1 else cleaned_input,
            conflicts=preprocess.conflicts,
        )
        result.constraint = constraint
        result.constraint_text = constraint.full_text

        # ── M5: Intent Routing ──
        self._log("[M5] 意图路由...")
        routing = self.m5.process(cleaned_input, user_override=mode_override)
        result.routing = routing
        result.mode = routing.mode.value

        # ── M6: Constrained Reasoning ──
        self._log(f"[M6] 约束内推理（{routing.mode.value}模式）...")
        reasoning = self.m6.process(
            user_input=cleaned_input,
            constraint=constraint,
            mode=routing.mode,
        )
        result.reasoning = reasoning

        # ── M7: Post-Verification ──
        self._log("[M7] 双源后校验...")
        post_verify = self.m7.process(
            original_text=cleaned_input,
            constraint_text=constraint.full_text,
            output=reasoning.output,
            mode=routing.mode,
        )
        result.post_verify = post_verify

        if post_verify.status == VerifyStatus.FAIL:
            # Degradation trigger: M7 failed → L2
            if result.degradation_level == DegradationLevel.L1:
                self._log("  ⚠ 后置校验失败，触发 L2 一级降级")
                result.degradation_level = DegradationLevel.L2
                result.degradation_reason = "后置校验重推超限"
                # L2: Re-run without canon
                reasoning2 = self.m6.process(
                    user_input=cleaned_input,
                    constraint=constraint,
                    mode=RouteMode.MIXED,
                )
                result.reasoning = reasoning2
                result.final_output = (
                    f"[降级输出 L2] 原始推理未通过校验，已切换为混合审慎模式重推。\n\n"
                    f"{reasoning2.output}"
                )
            else:
                result.degradation_level = DegradationLevel.L3
                result.degradation_reason = "L2降级后仍校验失败"
                result.final_output = (
                    f"[兜底输出 L3] 墨锁双链架构已完全关闭。\n\n{reasoning.output}"
                )
        else:
            result.final_output = reasoning.output

        self._log(f"[完成] 降级级别: {result.degradation_level.value}, 模式: {result.mode}")
        return result

    def reset(self):
        """Reset router state (for new conversations)."""
        self.m5.reset()

    def _log(self, msg: str):
        if self.verbose:
            print(msg)
