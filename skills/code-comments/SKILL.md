---
name: code-comments
description: 编写与审查代码注释的规范——核心是先问「这条注释给谁看」:函数外的注释给调用者（讲签名看不出的信息:报错条件、副作用、调用时机、清理责任），函数内的注释给维护者（优先用自解释代码，注释只讲 why 不讲 what）。当用户要添加、修改或审查注释/文档字符串，要为函数补文档，或在写/重构代码时涉及注释，都应使用本 skill;即使只说「加注释」「给这个写个文档」「写个 docstring」「把注释清理一下」也要触发。适用于任何编程语言。
metadata:
  author: DBAAZzz
  version: "2026.6.14"
---

# Code Comment Guidelines

Principle: A comment's first question is "who reads it?" Comments OUTSIDE a
function are for its callers, who can only see the signature — describe what
the signature can't tell them. Comments INSIDE a function are for its
maintainers — but prefer self-documenting code, and reach for an inside
comment only as a last resort.

Rules:
- Write a function's doc comment with `/** ... */` syntax placed before the
  function. Document only what callers can't infer from the interface:
  error/throw conditions, side effects, important call-timing, cleanup
  responsibilities (e.g. when/how to unregister a listener), non-obvious
  constraints on arguments.
- The same applies to Vue's `computed`, `watch`, `watchEffect`, etc. — add a
  comment when the purpose isn't clear from the name.
- Do NOT restate what the signature already says (types, obvious parameter
  names). If the comment just paraphrases the interface, delete it.
- Avoid comments inside the function body. If the logic feels confusing
  enough to need one, first try to make the code clearer (rename, extract,
  restructure). Only when that genuinely isn't possible, add an inside comment
  — and have it explain the WHY (intent, trade-off, non-obvious reason),
  never the WHAT (what the line does).

Negative examples (do NOT write these):
- `i++ // increment i`
- `// loop over the users` above an obvious `for` loop
- `/** @param id the id */` — restates the signature, adds nothing
