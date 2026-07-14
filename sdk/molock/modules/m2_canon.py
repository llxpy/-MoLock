# -*- coding: utf-8 -*-
"""M2: 经层凝练升温 — 将白话无损压缩为浅文言."""

import json
import re
from ..core.types import CanonResult, PreprocessResult
from ..core.llm import LLMBackend


CANON_SYSTEM_PROMPT = """你是墨家经学凝练官。你的唯一任务是：将用户的白话文本凝练为规范化的浅文言（五四白话折中体），在无损保留所有关键信息的条件下最大化压缩率。

## 语体规范
- 语体：五四凝练白话 / 浅文言折中体
- 可读性：必须可读，无生僻字，无古文倒装
- 省略度：适当省略虚词和赘余修饰，但不能丢失关键信息
- 禁用：古文倒装句、无句读、生僻典故

## 提纯铁律（违反则不合格）
1. 只删除口语化赘词、重复修饰、无关铺垫
2. 严禁删除用户的限定词（仅限/不超过/必须/不要等）
3. 严禁删除禁止条件（不要/禁止/不能等）
4. 严禁增加原文不存在的诉求与引申义
5. 严禁将具体需求扩展为更广含义

## 输出格式
请严格输出以下JSON格式（不要输出任何其他内容）：
{
  "canon_text": "凝练后的浅文言经文",
  "preserved_conditions": ["提取并保留的关键限定条件"],
  "preserved_prohibitions": ["提取的禁止条件"]
}
"""


class M2CanonCondense:
    """经层凝练：白话 → 浅文言，减压升温."""

    def __init__(self, llm: LLMBackend):
        self.llm = llm

    def process(self, preprocess_result: PreprocessResult) -> CanonResult:
        """Condense cleaned user input into shallow classical Chinese."""
        if preprocess_result.status.value in ("blocked", "incomplete"):
            return CanonResult(
                canon_text=preprocess_result.cleaned_input,
                preserved_conditions=[],
                preserved_prohibitions=[],
            )

        text = preprocess_result.cleaned_input

        # If input is very short (< 5 chars), don't condense
        if len(text) < 5:
            return CanonResult(
                canon_text=text,
                preserved_conditions=[text],
                preserved_prohibitions=[],
                condensation_ratio=1.0,
            )

        try:
            raw = self.llm.chat_json(CANON_SYSTEM_PROMPT, text)
            data = json.loads(raw)
        except (json.JSONDecodeError, Exception):
            # Fallback: use original text
            return CanonResult(
                canon_text=text,
                preserved_conditions=[text],
                preserved_prohibitions=[],
                condensation_ratio=1.0,
            )

        canon_text = data.get("canon_text", text)

        # Calculate condensation ratio
        ratio = len(canon_text) / max(len(text), 1)

        return CanonResult(
            canon_text=canon_text[:500],  # Safety cap
            preserved_conditions=data.get("preserved_conditions", []),
            preserved_prohibitions=data.get("preserved_prohibitions", []),
            condensation_ratio=round(ratio, 3),
        )
