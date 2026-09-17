# Lint 化配置：把测试规范变成工具强制

对应 SKILL.md 原则 5。lint 的入选标准：违规客观有害、工具判定不会错杀。名单保持短。

## 原则 → 规则对照

| 原则 | 规则 | 工具 |
|---|---|---|
| 测行为不测实现 | 禁调用次数/参数回放断言；禁测试内条件分支 | `no-restricted-syntax`；`no-conditional-in-test` |
| 分级隔离 | 单测目录禁 import 真实基础设施 | `import/no-restricted-paths` 或 eslint-plugin-boundaries |
| 防作弊 | 禁 `.only`、`skip`、注释掉的测试进主干 | `no-focused-tests`、`no-disabled-tests`、`no-commented-out-tests` |

标题风格（业务主语命名，SKILL.md 原则 3）**不进 lint**。词表式 `mustMatch` 会退化成「加词过检」：字符串合规不等于行为描述到位，而每次违规人只会把词加进列表让它过——工具成了负担，约定本身没人再想。标题的执行点是场景评审（SKILL.md 工作流程第 2 步）。团队若仍想要硬约束，可用 `jest/valid-title` 的 `mustMatch` 自配词表，但默认不推荐。

## JavaScript / TypeScript

jest 用 eslint-plugin-jest；vitest 用 @vitest/eslint-plugin，规则同名、前缀换 `vitest/`。

```js
// eslint.config.js
import jest from "eslint-plugin-jest";

export default [
  {
    files: ["**/*.test.{ts,tsx}", "**/*.spec.{ts,tsx}"],
    ...jest.configs["flat/recommended"],
    rules: {
      // 原则 1：测试里写条件分支，多半是在适配多种实现路径
      "jest/no-conditional-in-test": "error",
      "jest/no-conditional-expect": "error",
      // 防 .only / skip / 注释代码混进主干
      "jest/no-focused-tests": "error",
      "jest/no-disabled-tests": "warn",
      "jest/no-commented-out-tests": "error",
      "jest/no-identical-title": "error",
    },
  },
  {
    files: ["**/*.test.{ts,tsx}", "**/*.spec.{ts,tsx}"],
    rules: {
      // 原则 1：调用断言只在交互本身是契约时允许，且必须注明依据
      "no-restricted-syntax": ["error", {
        selector: "CallExpression[callee.type='MemberExpression'][callee.property.name=/^toHaveBeen(Nth)?Called(With|Times)?$/]",
        message: "优先断言可观测行为（返回值/存储/发出的消息）。仅当交互本身是契约（如恰好扣款一次）时使用，并加 eslint-disable 注释写明契约。",
      }],
    },
  },
];
```

契约性副作用的豁免写法——豁免必须带理由，否则 lint 等于没设：

```ts
// eslint-disable-next-line no-restricted-syntax -- 契约：支付成功回调恰好投递一次（场景：user is notified once ...）
expect(webhook).toHaveBeenCalledTimes(1);
```

### 分级边界：单测目录禁真实基础设施

```js
// eslint-plugin-import
"import/no-restricted-paths": ["error", {
  zones: [{
    target: "./tests/unit",
    from: "./src/infrastructure",
    message: "单测必须内存级可运行；需要真实 DB/网络的测试放 tests/integration。",
  }],
}],
```

边界更复杂（多包、多层）时换 eslint-plugin-boundaries，按 element type（unit / integration / e2e）声明允许矩阵。这条规则同时是 test-tiers.md 分级策略能成立的前提：隔离做不到，按层级选跑就是纸面的。

## Python

- ruff 开启 `PT` 规则族（flake8-pytest-style）：`PT009`（用原生 assert，不用 unittest 断言）、`PT011`（`pytest.raises` 必须给 `match`，防过宽异常断言）、`PT012`（raises 块只留一行）、`PT018`（复合断言拆开，失败信息才定位得到行为）。
- 需要 PM 直接读写场景文本时升级 pytest-bdd：`.feature` 文件天然 Given/When/Then，step 定义保持薄——薄 step 才逼测试断言行为而非步骤实现。

## Go

- testifylint：testify 用法体检（expected/actual 参数顺序、禁 float 等值断言等）。
- 单测与集成用 build tag 或目录物理分开（`//go:build integration`），CI 按 tag 选跑。

## 跨语言兜底脚本

`../scripts/check-coupled-asserts.py`（Python 3 标准库，无第三方依赖）只查一件事：实现耦合断言——JS 的 `toHaveBeenCalled*`、Python 的 `assert_called*` / `call_count`、Go 的 `AssertCalled` / `AssertNumberOfCalls`。契约性副作用豁免：断言行同行或前 2 行内加注释 `bdd-waive: <契约依据>`。有违规退出码为 1，可直接挂 pre-commit 或 CI 前置 job：

```bash
python3 <skills 目录>/test-first/scripts/check-coupled-asserts.py tests/ src/
```

脚本是启发式实现（按行正则），宁漏报不误报；JS/TS 项目优先用上面的 eslint `no-restricted-syntax`，脚本留给没有 eslint 的生态。

## CI 接入

把测试 lint 作为秒级前置 job，挂在所有测试任务之前——`.only` 混入、耦合断言这类问题，不值得启动完整测试环境才发现。编排示例见 [test-tiers.md](test-tiers.md) 的 CI 一节。
