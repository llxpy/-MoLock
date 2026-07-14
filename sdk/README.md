# MoLock SDK

墨锁（MoLock）Python SDK — 基于墨家"经说双链"的大语言模型中文语义约束推理框架。

## 安装

```bash
pip install molock
```

或从源码安装：

```bash
cd molock/sdk
pip install -e .
```

## 快速开始

```python
from molock import MoLock

# 初始化（支持任意 OpenAI 兼容 API）
molock = MoLock(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1",  # 或其他兼容端点
    model="deepseek-chat",
)

# 处理中文输入
result = molock.process("设计一个可爱风格的青少年网页")

# 查看结果
print(result.final_output)      # 最终推理输出
print(result.degradation_level)  # 降级级别 (L1/L2/L3)
print(result.mode)               # 推理模式 (diverge/strict/mixed)
print(result.canon_text)         # 凝练经文
print(result.constraint_text)    # 三锁约束全文
```

## 高级用法

```python
# 手动指定推理模式
result = molock.process("查一下新能源汽车销量", mode_override="strict")
result = molock.process("写一个科幻故事开头", mode_override="diverge")

# 查看完整诊断信息
d = result.to_dict()
print(d["degradation_level"])
print(d["mode"])

# 查看原始推理输出
print(result.reasoning.output)
```

## 支持的 API

任何 OpenAI 兼容 API 均可：

- DeepSeek: `base_url="https://api.deepseek.com/v1"`, `model="deepseek-chat"`
- 通义千问: `base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"`, `model="qwen-plus"`
- OpenAI: `base_url="https://api.openai.com/v1"`, `model="gpt-4o"`
- 本地模型: 使用 Ollama/vLLM 等

## 架构

```
用户输入 → M1预处理 → M2经凝练 → M3经文自检 → M4三锁约束
  → M5意图路由 → M6约束推理 → M7双源后校验 → 结构化输出
                                        ↓ 失败
                                    三级降级兜底
```

## License

MIT
