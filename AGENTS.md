# 编写 Skill 的规范

这个仓库只放**手写**的个人 skill。新增或修改 skill 时，严格遵循 Anthropic 官方最佳实践：
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

## 目录约定

每个 skill 是 `skills/<name>/` 下的一个目录，`<name>` 用 `kebab-case`：

```
skills/<name>/
├── SKILL.md          # 必需
├── references/       # 可选：按需加载的文档，一个概念一个文件
├── scripts/          # 可选：可执行脚本
└── assets/           # 可选：输出资源
```

## SKILL.md

frontmatter 至少包含 `name` 和 `description`（skills CLI 的硬性要求）。`description` 是 skill 是否被触发的**唯一决定因素**——要写清「做什么」+「什么时候用」，并略带主动语气（Claude 倾向于「欠触发」）。

```markdown
---
name: <kebab-case-name>
description: 一句话说清能力 + 触发场景，例如"当用户提到 X、要做 Y、或处理 Z 类文件时使用，即使没明确点名"。
metadata:
  author: <你的名字>
  version: "2026.6.14"
---

# Skill Name

目的与做法（一两段）。

## 何时使用
- 场景 1
- 场景 2

## 工作流程
命令式语气写步骤，并解释「为什么」，而不是堆砌大写 MUST/NEVER。

## 输出格式
有固定结构就用模板定义。
```

## 渐进式加载（三层）

1. **name + description** — 始终在上下文，决定触发。
2. **SKILL.md 正文** — 触发后加载，建议 < 500 行；接近上限就拆层级，并在正文里清楚指向 `references/` 里该读哪个文件。
3. **bundled 资源** — 需要时才读，可无限大；脚本无需读入即可执行。

## 编写原则

1. **为 agent 而写**，不要照搬文档原文——综合、提炼成 LLM 易消费的形式。
2. **解释 why**，不只是 how——今天的模型有很好的 theory of mind，给了理由会做得更好。
3. **保持精简**，删掉不发挥作用的内容；`references/` 大文件（> 300 行）加目录。
4. **一个概念一个文件**，大主题拆进 `references/`。
5. **带可运行的代码示例**。
6. **重复出现的脚本沉淀到 `scripts/`**——若多个用法都要写同一个辅助脚本，写一次放进去，让 skill 调用它。

## 安全

skill 不得包含恶意代码或会让用户「意外」的行为；不要创建用于未授权访问、数据外泄等用途的 skill。
