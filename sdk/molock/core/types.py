# -*- coding: utf-8 -*-
"""Type definitions for MoLock pipeline."""

from dataclasses import dataclass, field
from typing import Literal, Optional
from enum import Enum


class DegradationLevel(str, Enum):
    L1 = "L1"  # 正常态：经+说双链完整推理
    L2 = "L2"  # 一级降级：废弃经文，用户原文+说约束，白话推理
    L3 = "L3"  # 二级降级：完全关闭双链，原生推理兜底


class RouteMode(str, Enum):
    DIVERGE = "diverge"   # 发散优先
    STRICT = "strict"     # 收敛优先
    MIXED = "mixed"       # 混合审慎


class PreprocessStatus(str, Enum):
    PASS = "pass"
    BLOCKED = "blocked"
    INCOMPLETE = "incomplete"
    CONFLICT = "conflict"


class VerifyStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass
class PreprocessResult:
    status: PreprocessStatus
    cleaned_input: str
    injection_detected: bool = False
    injection_pattern: Optional[str] = None
    missing_dimensions: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    raw_input: str = ""


@dataclass
class CanonResult:
    canon_text: str = ""
    preserved_conditions: list[str] = field(default_factory=list)
    preserved_prohibitions: list[str] = field(default_factory=list)
    condensation_ratio: float = 0.0


@dataclass
class VerifyResult:
    status: VerifyStatus  # type: ignore
    verified: bool = False
    issues: list[str] = field(default_factory=list)
    retry_count: int = 0


@dataclass
class ConstraintResult:
    gloss_lock: str = ""       # 词义锁
    boundary_lock: str = ""    # 边界锁
    rule_lock: str = ""        # 规则锁
    tightness: str = ""        # tight / loose
    full_text: str = ""        # 约束全文


@dataclass
class RouteResult:
    mode: RouteMode
    confidence: float = 0.0
    diagnostics: dict = field(default_factory=dict)
    user_override: Optional[str] = None


@dataclass
class ReasonResult:
    output: str = ""
    mode: RouteMode = RouteMode.MIXED


@dataclass
class PostVerifyResult:
    status: VerifyStatus
    violations: list[str] = field(default_factory=list)
    retry_count: int = 0


@dataclass
class PipelineResult:
    """Complete MoLock pipeline output."""
    architecture: str = "mojia-dual-chain"
    version: str = "1.0.0"

    # Pipeline status
    degradation_level: DegradationLevel = DegradationLevel.L1
    degradation_reason: str = ""

    # Module outputs
    preprocess: Optional[PreprocessResult] = None
    canon: Optional[CanonResult] = None
    canon_verify: Optional[VerifyResult] = None
    constraint: Optional[ConstraintResult] = None
    routing: Optional[RouteResult] = None
    reasoning: Optional[ReasonResult] = None
    post_verify: Optional[PostVerifyResult] = None

    # Final output
    final_output: str = ""
    canon_text: str = ""
    constraint_text: str = ""
    mode: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "architecture": self.architecture,
            "version": self.version,
            "degradation_level": self.degradation_level.value,
            "degradation_reason": self.degradation_reason,
            "preprocess_status": self.preprocess.status.value if self.preprocess else None,
            "canon_text": self.canon_text,
            "constraint_text": self.constraint_text,
            "mode": self.mode,
            "final_output": self.final_output,
            "post_verify_status": self.post_verify.status.value if self.post_verify else None,
            "error": self.error,
        }

    def __repr__(self) -> str:
        if self.error:
            return f"<PipelineResult error={self.error}>"
        return (
            f"<PipelineResult "
            f"level={self.degradation_level.value} "
            f"mode={self.mode} "
            f"output_len={len(self.final_output)}>"
        )
