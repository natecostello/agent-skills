# copilot-instructions.md Template

Use this template when creating `.github/copilot-instructions.md`. Replace all `<angle bracket>` placeholders with concrete, verified information from the repository. Omit any section that does not apply.

---

```markdown
# Copilot Instructions

## Role

You are a code reviewer only. Deliver all feedback as inline review comments with
suggestion blocks on the PR. Include concrete code suggestions wherever possible
rather than descriptive-only feedback.

Do NOT act as a coding agent. Do NOT open sub-PRs, create branches, or push commits.
All feedback must be review comments.

## Repository Summary

<1-3 sentences: what this project does, who it's for, what makes it distinctive.
Include the primary language and framework.>

## Build, Test, and Lint

<Exact commands with brief notes. Adapt to the project's package manager.>

```bash
<install-command>      # Install dependencies
<test-command>         # Run tests (<approximate time>)
<lint-command>         # Lint
<format-command>       # Format check
<typecheck-command>    # Type check (if applicable)
```

<Environment variables needed at runtime, if any.>
<Test categories, markers, or flags that control what runs.>

## Architecture

<Brief description of the system architecture: what the major components are,
how they connect, and what external services they depend on.>

<High-risk areas where changes have outsized impact. Examples:
- "cloud/app.py deploys to Modal GPU — a broken deploy blocks all downstream work"
- "src/db/migrations/ — migration errors are hard to reverse in production">

## Project Layout

<Tree or list of top-level directories and key files with one-line descriptions.>

Configuration files:
<List config files and what they configure. Examples:
- pyproject.toml — dependencies, ruff config, mypy config, pytest config
- .github/workflows/ci.yml — CI pipeline: lint, typecheck, test>

## Key Abstractions

<List the 3-8 most important types, classes, or interfaces with one-line descriptions.
These are the things a reviewer needs to know exist to give useful feedback.>

## Dependencies and Non-Obvious Relationships

<Things not obvious from reading a single file. Examples:
- "cloud/app.py has its own pip dependency list, separate from pyproject.toml"
- "The test database is shared across test files — ordering matters"
- "Style reference images must be 64px tall grayscale PNGs">

## Planning Documents

<If the repo has planning docs that code should align with, list them and tell the
reviewer to check implementation against these plans. Omit if no planning docs exist.>

## Coding Conventions

<Concrete rules from linter config, CLAUDE.md, CONTRIBUTING.md. Only include
conventions a reviewer should enforce. Examples:
- Python 3.12+, managed with uv
- from __future__ import annotations in every file
- Type hints on all public function signatures
- pathlib.Path for file paths, not string manipulation
- Ruff for linting and formatting (line-length 99)>

## Review Priority

Focus review effort in this order. Do not spend budget on lower tiers until higher
tiers have been thoroughly checked. A round that catches a typo but misses a silent
data-loss bug is a failed review.

1. **Correctness** — Would this work if implemented/deployed as written? Check data
   flow between components, implicit assumptions, edge cases, join/key consistency,
   and off-by-one or empty-input scenarios
2. **Breaking changes** — Does this silently break existing behavior, contracts, or
   downstream consumers?
3. **Security** — Injection, data exposure, unsafe operations, credential handling
4. **Compatibility** — Version requirements, platform assumptions, dependency
   constraints that aren't documented
5. **Consistency** — Naming, conventions, cross-reference accuracy
6. **Cosmetics** — Formatting, wording, documentation polish

## Plan and Design Document Reviews

When reviewing plans, ADRs, RFCs, or other design documents (not code):

- Verify described steps would work correctly if implemented as written
- Check that data formats, schemas, and join keys are consistent across components
- Flag implicit assumptions that could cause silent failures at implementation time
- Check version or compatibility requirements are stated, not assumed
- Verify edge cases are addressed (different input formats, missing data, empty sets)
- Do not focus on prose style or markdown formatting — focus on technical soundness

## Code Review Focus Areas

<6-12 numbered items specific to THIS project. Each names a concrete thing to check
and why it matters. Be specific enough that reviewers catch issues in the FIRST round.

Include project-specific items AND applicable items from this checklist:

1. **Type safety** — flag bare dict, list, tuple without type parameters
2. **Security** — no hardcoded API keys, no command injection via string interpolation.
   In shell scripts: use Bash arrays for file lists, not unquoted string expansion;
   sanitize external input before interpolation
3. **Error handling and fallbacks** — when a batch operation fails and is caught,
   callers must not silently fall through to a misleading fallback. Track success
   with explicit flags (e.g. `query_ok`) to distinguish "succeeded, no results"
   from "failed" — each case should render differently
4. **Truncation propagation** — when a function signals truncation (e.g. via a
   sentinel key or flag on the last result), callers must detect it and surface
   a notice or avoid claiming completeness
5. **Multi-valued field parsing** — when a field can contain multiple
   delimited values (e.g. comma/slash/pipe separated), always tokenize into
   individual terms before matching. For protection checks, protect if ANY term
   matches. For filtering, filter only if ALL terms match the criterion
6. **N+1 query patterns** — flag loops that call a query function per item
   when a batch API exists. Map batch results back to inputs by key
7. **Code duplication** — shared helpers should live in a single module. Flag
   any utility function duplicated across files
8. **Input validation consistency** — when multiple code paths validate the
   same input type, they must use identical validation logic (same regex,
   same rules). Flag inconsistencies like startsWith vs regex
9. **Shell script portability** — if scripts claim cross-platform support
   (macOS/Linux), flag GNU-only flags (sort -V, sed -i without '', etc.)
10. **Plan alignment** — verify implementation matches planning docs
11. **Documentation consistency** — if the PR changes user-facing behavior, CLI
    commands, flags, configuration, public interfaces, or architecture, check
    whether `README.md` and `CLAUDE.md` were updated to match. Flag PRs that
    change behavior without updating docs>

<Keep only the items that apply to THIS project. Add project-specific items.
The goal is 6-12 focused items that catch real issues on the first review round.>

## What NOT to Flag

<5-8 items that would waste reviewer and developer time. Tailor to the project's
actual patterns. Examples:
- Do not suggest adding docstrings to test functions
- Do not flag print() in scripts — they use print deliberately, not logging
- Do not suggest reorganizing imports beyond what the linter enforces
- Do not flag # noqa or # type: ignore without checking for a valid reason
- Do not suggest adding __all__ exports — this is not a library>
```
