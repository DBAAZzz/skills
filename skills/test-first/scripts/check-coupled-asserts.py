#!/usr/bin/env python3
"""test-first 兜底 lint：跨语言检查实现耦合断言（Python 3 标准库，无第三方依赖）。

规则（对应 test-first skill 原则 1）：测试断言可观测行为，不断言内部调用
次数或参数回放：

  - JS/TS : toHaveBeenCalled / toHaveBeenCalledTimes / toHaveBeenCalledWith 等
  - Python: assert_called* / assert_any_call / assert_has_calls / call_count
  - Go    : AssertCalled / AssertNumberOfCalls

豁免：交互本身是契约（如「恰好扣款一次」）时，在断言行同行或前 2 行内注释：

    expect(webhook).toHaveBeenCalledTimes(1) // bdd-waive: 契约=回调恰好投递一次

用法：
    python3 check-coupled-asserts.py <文件或目录>...
退出码：0 通过（或未找到测试文件），1 有违规，2 用法错误。

启发式按行匹配，宁漏报不误报。JS/TS 项目优先用 eslint 的 no-restricted-syntax
（见 references/lint-rules.md），本脚本兜底没有 eslint 的生态。

标题风格（业务主语命名）不在本脚本检查范围内：词表式检查会退化成
「加词过检」，其执行点是场景评审，见 SKILL.md 原则 5。
"""

from __future__ import annotations

import os
import re
import sys

WAIVER = "bdd-waive"

COUPLED = {
    "js": re.compile(r"\btoHaveBeen(?:Nth)?Called(?:Times|With)?\b"),
    "py": re.compile(
        r"\bassert_called\w*\b|\bassert_any_call\b|\bassert_has_calls\b|\bcall_count\b"
    ),
    "go": re.compile(r"\bAssertCalled\b|\bAssertNumberOfCalls\b"),
}

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "out", "coverage",
    "__pycache__", ".venv", "venv", "vendor",
}

JS_SUFFIXES = (
    ".test.ts", ".test.tsx", ".test.js", ".test.jsx", ".test.mjs", ".test.cjs",
    ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx",
)


def lang_of(path: str) -> str | None:
    """识别测试文件并返回语言标识；非测试文件返回 None。"""
    base = os.path.basename(path)
    if base.endswith(JS_SUFFIXES):
        return "js"
    if base.endswith("_test.go"):
        return "go"
    if base.endswith(".py") and (base.startswith("test_") or base.endswith("_test.py")):
        return "py"
    return None


def iter_test_files(paths: list[str]):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in sorted(files):
                    fp = os.path.join(root, f)
                    if lang_of(fp):
                        yield fp, lang_of(fp)
        elif lang_of(p):
            yield p, lang_of(p)


def check_file(path: str, lang: str) -> list[tuple[int, str]]:
    """返回 (行号, 细节) 违规列表。"""
    violations: list[tuple[int, str]] = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    for i, line in enumerate(lines):
        if not COUPLED[lang].search(line):
            continue
        # 豁免窗口：断言行及其前 2 行（豁免注释常写在 it( 行上方，与断言行隔一两行）
        window = "".join(lines[max(0, i - 2):i + 1])
        if WAIVER in window:
            continue
        violations.append((i + 1, line.strip()[:80]))

    return violations


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    files = list(iter_test_files(argv))
    if not files:
        print("check-coupled-asserts: 未找到测试文件")
        return 0

    total = 0
    for path, lang in files:
        for n, detail in check_file(path, lang):
            total += 1
            print(
                f"{path}:{n}: [coupled] 调用断言疑似绑定实现: {detail}\n"
                f"  优先断言可观测行为；若交互本身是契约，加注释 bdd-waive: <契约依据>"
            )

    print(f"check-coupled-asserts: {total} 处违规，扫描 {len(files)} 个测试文件")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
