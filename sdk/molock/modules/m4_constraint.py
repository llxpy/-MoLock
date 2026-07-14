# -*- coding: utf-8 -*-
"""M4: 说层三锁约束 — 核心护栏：词义锁 + 边界锁 + 规则锁."""

import json
from ..core.types import ConstraintResult, CanonResult
from ..core.llm import LLMBackend
from ..data.ambiguous_words import AMBIGUOUS_WORDS, EXCLUSION_TEMPLATES


CONSTRAINT_SYSTEM_PROMPT = """你是墨家说学约束官。你的唯一任务是：针对经文，生成三锁语义契约（词义锁、边界锁、规则锁）。

## 三锁结构

### 1. 词义锁
- 扫描输入，找出所有可能有歧义的词
- 对每个歧义词，锁定其在此语境下的唯一精确含义
- 同时排除所有可能的引申义和歧义项
- 格式：[歧义词]：本条唯一释义，排除[引申义1]、[引申义2]...

### 2. 边界锁
- 明确划分可推理维度与禁止推理维度
- 精确区分"用户说了什么"和"模型不能自行补充什么"
- 将用户未说明、不能从用户说的推断出的内容标记为不可推理区
- 格式：允许推演：[维度1、维度2...]  /  禁止推演：[维度1、维度2...]

### 3. 规则锁
- 设定推理的形式底线
- 禁止反事实假设作为推理前提
- 禁止构建原文中不存在的动机/因果链条
- 禁止角色分配无明确证据
- 设定推演规模上限

## 约束松紧
根据用户需求判定：
- tight（严格）：事实核对、数据分析、逻辑推理类任务
- loose（宽松）：创意设计、头脑风暴、开放探索类任务

## 输出格式
{
  "gloss_lock": "词义锁全文",
  "boundary_lock": "边界锁全文",
  "rule_lock": "规则锁全文",
  "tightness": "tight | loose"
}
"""


class M4Constraint:
    """说层约束锁真：三锁语义契约生成."""

    def __init__(self, llm: LLMBackend):
        self.llm = llm

    def process(
        self,
        original_text: str,
        canon_text: str,
        conflicts: list[str] = None,
    ) -> ConstraintResult:
        """Generate three-lock constraints from double-source input."""

        # Build hint for known ambiguous words
        ambiguous_hints = []
        for word in AMBIGUOUS_WORDS:
            if word in original_text or word in canon_text:
                template = EXCLUSION_TEMPLATES.get(word, "")
                hint = f"- **{word}**"
                if template:
                    hint += f"（建议：{template}）"
                ambiguous_hints.append(hint)

        hint_text = ""
        if ambiguous_hints:
            hint_text = "\n## 已知歧义词（必须锁定）\n" + "\n".join(ambiguous_hints)

        conflict_text = ""
        if conflicts:
            conflict_text = "\n## 语义冲突（双端保留，不消解）\n" + "\n".join(conflicts)

        user_prompt = (
            f"## 用户原文\n{original_text}\n\n"
            f"## 经文\n{canon_text}"
            f"{hint_text}"
            f"{conflict_text}"
        )

        try:
            raw = self.llm.chat_json(CONSTRAINT_SYSTEM_PROMPT, user_prompt)
            data = json.loads(raw)
        except (json.JSONDecodeError, Exception):
            return ConstraintResult(
                gloss_lock="",
                boundary_lock="",
                rule_lock="",
                tightness="loose",
                full_text="",
            )

        full_text = (
            f"【说-词义锁】\n{data.get('gloss_lock', '')}\n\n"
            f"【说-边界锁】\n{data.get('boundary_lock', '')}\n\n"
            f"【说-规则锁】\n{data.get('rule_lock', '')}"
        )

        return ConstraintResult(
            gloss_lock=data.get("gloss_lock", ""),
            boundary_lock=data.get("boundary_lock", ""),
            rule_lock=data.get("rule_lock", ""),
            tightness=data.get("tightness", "loose"),
            full_text=full_text,
        )
