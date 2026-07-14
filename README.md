# MoLock — Mohist Dual-Chain Semantic Constraint Reasoning

> A constraint-first anti-hallucination reasoning framework for Chinese LLMs, inspired by the 2,400-year-old Mohist "Canon + Explanation" (经说) logical system.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[中文文档](README_CN.md)

---

## TL;DR

**MoLock is a 7-module Skills pipeline that puts semantic guardrails *before* reasoning, not after.** It reduces hallucination rate from 17% to 8% on a 100-question Chinese semantic ambiguity benchmark, while raising average score from 4.42 to 4.74 (out of 5.0).

---

## The Problem

Chinese LLMs have a built-in disadvantage: the language itself has enormous semantic ambiguity. Words like 还行 ("it's okay") can mean anywhere from "barely passing" to "I'm unhappy but won't say so directly." Models fill these gaps with hallucinated narratives.

The common fix — use English APIs — works but sidesteps the real issue. **Chinese deserves a native solution.**

---

## The Insight

Over 2,400 years ago, Mozi's school — the only engineer-philosophers among China's pre-Qin thinkers — faced exactly this problem. They needed to describe precise physical phenomena (optics, mechanics, geometry) using Classical Chinese, a language with inherently wide semantic ranges.

Their solution:

- **Canon (经)**: ultra-compact statements that capture the core semantics with zero redundancy
- **Explanation (说)**: per-word glosses that lock down each ambiguous term's meaning, boundaries, and inference rules

This "define then deduce" structure is the oldest known constraint language in human history. MoLock brings it into the LLM era.

---

## Architecture

```
User Input
  │
  ▼
[00] Preprocess & Injection Guard     — Sanitize, detect prompt injection
  │
  ▼
[01] Canon Condensation (经凝练)       — Compress vernacular → Classical Chinese, strip noise
  │
  ▼
[02] Canon Self-Verification (经自检)  — Cross-check against original to prevent information loss
  │
  ▼
[03] Explanation Constraints (说约束)  — 3-lock mechanism: Word Lock + Boundary Lock + Rule Lock
  │
  ▼
[04] Intent Router (意图路由)          — Auto-classify: Divergent / Convergent / Mixed reasoning mode
  │
  ▼
[05] Constrained Reasoning (推理执行)  — Reason strictly within the semantic contract
  │
  ▼
[06] Post-Verification (后置校验)      — Dual-threshold: loose for divergent, zero-tolerance for convergent
  │
  ▼
Output
```

**Constraint-first philosophy**: unlike post-hoc guard systems, MoLock builds the semantic fence *before* the model starts thinking. The model never enters hallucination territory in the first place.

---

## Experimental Results

**100-question benchmark** (9 semantic ambiguity types, DeepSeek-v4-flash, 4-group comparison):

| Group | Avg Score | Hallucination Rate | Tokens |
|:--|:--|:--|:--|
| Bare (裸调) | 4.42 | 17% | 10,716 |
| Chain-of-Thought | 4.63 | 11% | 35,113 |
| English (英文) | 4.56 | 13% | 14,897 |
| **MoLock** | **4.74** | **8%** | 31,820 |

### By Task Type

MoLock excels at **pragmatic** Chinese tasks (implicature, role inference, negation scope) and trails only on **formal-logical** tasks (NLI):

| Task Type | MoLock vs Bare | MoLock vs CoT |
|:--|:--|:--|
| Role Inference | **+1.20** | **+1.20** |
| Negation Scope | **+0.80** | **+0.80** |
| Implicit Causality | **+0.53** | **+0.60** |
| Null Placeholders | **+0.27** | **+0.30** |
| NLI (Formal Logic) | -0.36 | -0.40 |

> Full data: [`experiment/results/`](experiment/results/)

---

## Installation

MoLock is built as a WorkBuddy Skills chain. Each module is independent; load the orchestrator to run the full pipeline.

1. Copy the 7 folders under `skills/` to your WorkBuddy skills directory
2. Load **墨学双链总控编排** (orchestrator) — it auto-chains all 7 modules
3. For partial use: load individual modules (e.g., `03-说约束锁真` for semantic constraint only)

---

## Project Structure

```
molock/
├── skills/
│   ├── 墨学双链总控编排/          # Orchestrator (full pipeline)
│   ├── 00-预处理与防注入/          # Preprocess & injection guard
│   ├── 01-经凝练升温/              # Canon condensation
│   ├── 02-经文自检/                # Canon self-verification
│   ├── 03-说约束锁真/              # Explanation constraints (3-lock)
│   ├── 04-动态意图路由/            # Intent router (v2.0)
│   └── 05-模式联动后置校验/        # Post-verification
├── experiment/
│   ├── test_bank.json              # 100-question benchmark
│   ├── run_batch.py                # Batch experiment runner
│   ├── merge_batches.py            # Result merger → Excel
│   └── results/                    # Experimental data
├── paper/
│   └── 墨锁MoLock_论文_定稿版.md     # Full paper (Chinese)
├── README.md                        # English (this file)
├── README_CN.md                     # Chinese
└── LICENSE
```

---

## Citation

If you use MoLock in your research, please cite:

```bibtex
@misc{sun2026molock,
  title   = {MoLock: Mohist Dual-Chain Semantic Constraint Reasoning for Chinese LLMs},
  author  = {Sun, Weilong},
  year    = {2026},
  note    = {arXiv preprint},
  url     = {https://github.com/llxpy/-MoLock}
}
```

---

## Author

**Weilong Sun (孙巍珑)** — Independent Researcher

- GitHub: [@LLXPY](https://github.com/llxpy)
- Juejin: [@LLXPY](https://juejin.cn/post/7661939225987006498)

---

## License

MIT License — use, modify, distribute freely. Attribution appreciated.

---

*"My ancestors solved the AI hallucination problem 2,400 years ago. I just translated it into code."*
