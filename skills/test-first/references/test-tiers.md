# 测试分级与精准运行

对应 SKILL.md 原则 4。目标：改两行代码，秒级知道关键路径没坏；全量信心交给定期任务，不靠人肉等待。

## 分级模型

| 层级 | 范围 | 依赖 | 时长量级 | 触发时机 |
|---|---|---|---|---|
| 冒烟 smoke | 关键 happy path 5–15 条 | 内存 / fake | 秒 | 每次提交前 |
| 行为单测 unit | 模块行为（本 skill 的主体） | 内存 / fake，禁真实 IO | 秒–分 | 改动相关即跑 |
| 集成 integration | 跨模块、真实 DB / 队列 / HTTP | 测试容器或测试环境 | 分钟 | PR |
| e2e | 关键用户旅程 | 完整环境 | 十分钟级 | 主分支、夜间 |

层级用目录或 tag **物理隔离**（`tests/unit`、`tests/integration`、`tests/e2e`，或 Go 的 build tag），并用 lint 边界强制依赖方向（见 [lint-rules.md](lint-rules.md) 的分级边界一节）。隔离做不到，按层选跑就是纸面的——单测里混进一个连真库的用例，「秒级反馈」就没了。

## 精准运行：按改动 + 依赖图选测

- **vitest**：`vitest related <files> --run` 跑与指定文件有 import 关系的测试；`vitest changed --run` 基于 git 改动。
- **jest**：`jest --changedSince=origin/main`；`jest --findRelatedTests src/order.ts`。
- **pytest**：`pytest --lf --ff`（上次失败优先）适合本地迭代；`pytest-testmon` 按覆盖率依赖图选测，适合 CI。
- **monorepo**：`nx affected:test`、`turbo run test --filter=...[origin/main]`；Bazel / Pants 原生依赖图最精确。

精准是「选择运行集」，不是「删减测试集」。skip 的测试必须带 issue 链接和到期时间，否则就是在悄悄删测试。

## CI 编排示例（GitHub Actions 骨架，按生态替换命令）

```yaml
jobs:
  test-lint:                # 秒级前置：.only、耦合断言、边界违规
    runs-on: ubuntu-latest
    steps:
      - run: pnpm eslint 'tests/**' 'src/**/*.test.*'
      - run: python3 <skills 目录>/test-first/scripts/check-coupled-asserts.py tests/ src/

  affected:                 # PR：受影响单测 + 冒烟
    runs-on: ubuntu-latest
    steps:
      - run: pnpm vitest related --run $(git diff --name-only origin/main...HEAD | grep -E '\.(ts|tsx)$')
      - run: pnpm vitest run tests/smoke/

  integration:              # PR：受影响模块的集成测试
    runs-on: ubuntu-latest
    steps:
      - run: pnpm test:integration -- --changedSince=origin/main

  full:                     # main 合并 + 夜间 cron：全量含 e2e
    if: github.ref == 'refs/heads/main' || github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - run: pnpm test:all
```

夜间全量（`on.schedule`）是精准策略的安全网。全量红了不得用「PR 是绿的」搪塞——漏检说明分级或依赖图有洞，先补洞。

## 精准策略躲不掉全量的时刻

- 改共享基础设施：测试工具、fixture、全局配置、CI 镜像——依赖图之外的影响面，直接全量。
- 发布前：全量 + e2e。
- 分级边界刚建立、历史测试归属未清时：先全量跑几轮校准，再信精准。
