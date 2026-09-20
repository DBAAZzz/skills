# My Skills

我个人手写的 [Agent Skills](https://agentskills.io/home) 集合，遵循 [skills CLI](https://github.com/vercel-labs/skills) 的标准布局（`skills/<name>/SKILL.md`）。

## Skills

| Skill | 说明 |
|-------|------|
| [code-ablation](skills/code-ablation) | 严苛自审与极简重构（代码消融）：切换架构师视角做减法，剔除过度设计与无效防御，契约驱动测试重构，交付精简实现 |
| [code-comments](skills/code-comments) | 代码注释规范：函数外注释给调用者、函数内注释给维护者，只讲 why 不讲 what |
| [context-compression](skills/context-compression) | 开发者上下文压缩：交付代码分析/Review/方案结论时，重组成「没读过当前代码的开发者也能快速理解」的表达——先整体后细节、先为什么后怎么做，术语保留但不用术语解释术语 |
| [pre-mortem](skills/pre-mortem) | 技术方案/现有代码的「事前验尸」：假设它已经失败，从失败的未来倒推隐患，挂代码证据、按失败原型分级，只诊断不修复 |
| [self-documenting-code](skills/self-documenting-code) | 帮助代码尽可能做到自解释：优先通过命名、代码结构、类型、API、运行时校验和测试表达规则，避免用注释重复代码或提醒本应由程序保证的约束；对于代码无法表达的原因、兼容性、外部限制、性能/安全取舍等信息，保留并优化注释 |
| [test-first](skills/test-first) | 测试用例编写规范与测试先行工作流：测行为不测实现，BDD 验收场景先行（业务主语命名 + Given/When/Then），测试先于实现并先红后绿，分级精准运行，有害违规 lint 化 |

## 安装

```bash
pnpx skills add DBAAZzz/skills --skill='*'        # 全部，加 -g 装到全局
pnpx skills add DBAAZzz/skills --skill=<name>     # 单个
```

编写规范见 [AGENTS.md](AGENTS.md)。

## License

[MIT](LICENSE.md)
