# -*- coding: utf-8 -*-
"""
MoLock — 墨学经说双链语义约束推理框架 SDK.

基于先秦墨家"经说"逻辑体系，为大语言模型提供中文语义约束前置推理能力。
7模块流水线：预处理 → 经凝练 → 自检 → 三锁约束 → 意图路由 → 约束推理 → 后校验。

Usage:
    from molock import MoLock

    molock = MoLock(api_key="sk-...")
    result = molock.process("你的中文问题")
    print(result.final_output)

    # 高级用法
    result = molock.process("设计一个可爱风格的网页", mode_override="diverge")
"""

from .core.types import (
    PipelineResult,
    PreprocessResult,
    CanonResult,
    VerifyResult,
    ConstraintResult,
    RouteResult,
    ReasonResult,
    PostVerifyResult,
    DegradationLevel,
    RouteMode,
    PreprocessStatus,
    VerifyStatus,
)
from .core.pipeline import MoLockPipeline as MoLock
from .core.llm import LLMBackend

__version__ = "1.0.0"
__author__ = "孙巍珑"
__all__ = [
    "MoLock",
    "LLMBackend",
    "PipelineResult",
    "DegradationLevel",
    "RouteMode",
]
