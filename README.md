# MoLock — Mohist Dual-Chain Semantic Constraint Reasoning

> A constraint-first anti-hallucination reasoning framework for Chinese LLMs, inspired by the 2,400-year-old Mohist "Canon + Explanation" (经说) logical system.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![条款:](https://img.shields.io/badge/License-MIT-yellow.svg)] (https://opensource.org/licenses/MIT)
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
User Input   用户输入
  │
  ▼
[00] Preprocess & Injection Guard     — Sanitize, detect prompt injection[00]预处理&注射防护&消毒，检测提示注射
  │
  ▼
[01] Canon Condensation (经凝练)       — Compress vernacular → Classical Chinese, strip noise压缩白话文言文，去除杂音
  │
  ▼
[02] Canon Self-Verification (经自检)  — Cross-check against original to prevent information loss[02]佳能自我验证与原件交叉核对，防止信息丢失
  │
  ▼
[03] Explanation Constraints (说约束)  — 3-lock mechanism: Word Lock + Boundary Lock + Rule Lock3锁机制：字锁、边界锁、规则锁
  │
  ▼
[04] Intent Router (意图路由)          — Auto-classify: Divergent / Convergent / Mixed reasoning mode[04]意图路由器自动分类：发散/收敛/混合推理模式
  │
  ▼
[05] Constrained Reasoning (推理执行)  — Reason strictly within the semantic contract约束推理（Constrained Reasoning）严格在语义契约内进行推理
  │
  ▼
[06] Post-Verification (后置校验)      — Dual-threshold: loose for divergent, zero-tolerance for convergent双门槛：发散宽松，收敛零容忍
  │
  ▼
Output   输出
```

**Constraint-first philosophy**: unlike post-hoc guard systems, MoLock builds the semantic fence *before* the model starts thinking. The model never enters hallucination territory in the first place.约束优先哲学：与事后保护系统不同，MoLock在模型开始思考之前就建立了语义栅栏。这个模型从一开始就不会进入幻觉领域。

---

## Experimental Results   ##实验结果

**100-question benchmark** (9 semantic ambiguity types, DeepSeek-v4-flash, 4-group comparison):**100题基准测试**（9种语义歧义类型，DeepSeek-v4-flash， 4组比较）：

| Group | Avg Score | Hallucination Rate | Tokens ||分组|平均得分|幻觉率| token |
|:--|:--|:--|:--|
| Bare (裸调) | 4.42 | 17% | 10,716 |
| Chain-of-Thought | 4.63 | 11% | 35,113 ||思想链| 4.63 | 11% | 35113 |
| English (英文) | 4.56 | 13% | 14,897 ||英语(英文)| 4.56 | 13% | 14,897 |
| **MoLock** | **4.74** | **8%** | 31,820 |

### By Task Type   ###按任务类型

MoLock excels at **pragmatic** Chinese tasks (implicature, role inference, negation scope) and trails only on **formal-logical** tasks (NLI):MoLock擅长于**语用**中文任务（含意、角色推理、否定范围），只在**形式逻辑**任务（NLI）上落后。

| Task Type | MoLock vs Bare | MoLock vs CoT ||任务类型| MoLock vs Bare | MoLock vs CoT |
|:--|:--|:--|
| Role Inference | **+1.20** | **+1.20** ||角色推断| ** 1.20** | ** 1.20** |
| Negation Scope | **+0.80** | **+0.80** || ** 0.80** | ** 0.80** |
| Implicit Causality | **+0.53** | **+0.60** || ** 0.53** | ** 0.60** |
| Null Placeholders | **+0.27** | **+0.30** ||空占位符| ** 0.27** | ** 0.30** |
| NLI (Formal Logic) | -0.36 | -0.40 || NLI（形式逻辑）| -0.36 | -0.40 |

> Full data: [`experiment/results/`](experiment/results/)完整数据：[' experiment/results/ ']（experiment/results/）完整数据：[' experimental /results/ '](experimental /results/) （experimental /results/）

---

## Installation   # #安装

MoLock is built as a WorkBuddy Skills chain. Each module is independent; load the orchestrator to run the full pipeline.MoLock是作为WorkBuddy技能链构建的。每个模块是独立的；加载编排器以运行整个管道。

1. Copy the 7 folders under `skills/` to your WorkBuddy skills directory1. 复制“skills/”下的7个文件夹到你的WorkBuddy skills目录
2. Load **墨学双链总控编排** (orchestrator) — it auto-chains all 7 modules2. Load **墨学双链总控编排** (orchestrator) — it auto-chains all 7 modules
3. For partial use: load individual modules (e.g., `03-说约束锁真` for semantic constraint only)3. 对于部分使用：加载单个模块（例如，‘ 03- ’仅用于语义约束）

---

## Project Structure   项目结构

```
molock/
├── skills/   ├──技能/
│   ├── 墨学双链总控编排/          # Orchestrator (full pipeline)
│   ├── 00-预处理与防注入/          # Preprocess & injection guard│   ├── 00-预处理与防注入/          # Preprocess & injection guard
│   ├── 01-经凝练升温/              # Canon condensation
│   ├── 02-经文自检/                # Canon self-verification
│   ├── 03-说约束锁真/              # Explanation constraints (3-lock)
│   ├── 04-动态意图路由/            # Intent router (v2.0)
│   └── 05-模式联动后置校验/        # Post-verification
├── experiment/   ├──实验/
│   ├── test_bank.json              # 100-question benchmark表表所示。json # 100问题基准
│   ├── run_batch.py                # Batch experiment runner│├──run_batch.py #批处理实验运行器
│   ├── merge_batches.py            # Result merger → Excel│├──merge_batch .py # Result合并&rarr│├──merge_batch .py # Result merger → Excel│├──merge_batch .py # Result
│   └── results/                    # Experimental data│├──results/ #实验数据
├── paper/
│   └── 墨锁MoLock_论文_定稿版.md     # Full paper (Chinese)
├── README.md                        # English (this file)├──README。md# English（此文件）
├── README_CN.md                     # Chinese├──README_CN。md #中文
└── LICENSE   └──勘探许可证
```

---

## Citation   # #引用

If you use MoLock in your research, please cite:如果您在研究中使用MoLock，请引用：

```bibtex   ’”bibtex
@misc{sun2026molock,
  title   = {MoLock: Mohist Dual-Chain Semantic Constraint Reasoning for Chinese LLMs},title = {MoLock: Mohist双链语义约束推理中文法学硕士}，
  author  = {Sun, Weilong},2. Load **墨学双链总控编排** (orchestrator) — it auto-chains all 7 modules
  year    = {2026},年= {2026}，
  note    = {arXiv preprint},2. Load **墨学双链总控编排** (orchestrator) — it auto-chains all 7 modules
  url     = {https://github.com/llxpy/-MoLock}
}
```

---

## Author

**Weilong Sun (孙巍珑)** — Independent Researcher

- GitHub: [@LLXPY](https://github.com/LLXPY)
- Juejin: [@LLXPY](https://juejin.cn/user/LLXPY)

---

## License

MIT License — use, modify, distribute freely. Attribution appreciated.

---

*"My ancestors solved the AI hallucination problem 2,400 years ago. I just translated it into code."*
