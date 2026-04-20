---
name: copilot-init
description: >-
  This skill should be used when the user asks to "set up copilot review",
  "create copilot instructions", "initialize copilot", "add copilot as a
  reviewer", "configure copilot for this repo", or needs to create a
  .github/copilot-instructions.md file for GitHub Copilot code review.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
disable-model-invocation: true
argument-hint: "[optional focus areas, e.g. \"focus on security\"]"
---

# Initialize Copilot Code Review Instructions

Create `.github/copilot-instructions.md` to give GitHub Copilot the project context it needs for informed pull request reviews. Copilot is configured as a code reviewer only — not as a coding agent.

## Workflow

### 1. Verify Prerequisites

Confirm this is a git repository and the file does not already exist:

```bash
git rev-parse --show-toplevel
ls .github/copilot-instructions.md 2>/dev/null
```

If the file exists, stop and suggest `/copilot-update` instead. Create `.github/` if absent.

### 2. Analyze the Repository

Gather the following by reading actual files with Glob, Grep, and Read. Do not guess.

**Project identity** — Read `README.md`, `CLAUDE.md`, or equivalent. Identify primary language(s), framework(s), project type (library, CLI, web app, API, monorepo).

**Build and tooling** — Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, or equivalent. Identify the package manager and extract exact commands for install, build, test, lint, format, and type check. Note environment variables and prerequisites.

**Project layout** — List top-level directories and purposes. Identify source, test, and config file locations. Find CI/CD configuration in `.github/workflows/` or equivalent.

**Architecture** — Identify major components, external service dependencies, and high-risk areas where changes have outsized impact.

**Conventions** — Read linter/formatter config. Check `CLAUDE.md`, `CONTRIBUTING.md`, or style guides. Check commit conventions from recent `git log`.

**Planning documents** — Check for `docs/` with architecture or planning documents that code should align with.

**Note:** The template includes universal sections (Review Priority, Plan and Design Document Reviews) that apply to all repos. Always include these — they are not project-specific and should not be omitted.

### 3. Write the File

Create `.github/copilot-instructions.md` using the template in [references/template.md](references/template.md). Fill every section with concrete, verified information from Step 2. Omit sections that do not apply rather than writing placeholder content.

If `$ARGUMENTS` specifies focus areas, emphasize those in the review focus areas section.

### 4. Add CLAUDE.md Reference

If `CLAUDE.md` exists, add a reference near the conventions or CI section:

```markdown
## Code Review

GitHub Copilot is configured as a PR code reviewer. Its instructions are in
[`.github/copilot-instructions.md`](.github/copilot-instructions.md). Copilot reviews
deliver inline comments with suggestion blocks. Use `/resolve-pr-comments` to process
review feedback.
```

### 5. Report

Print what was created and remind about:
- Enabling Copilot code review in repo Settings > Copilot > Code review
- Adding Copilot as a default reviewer in branch protection rules
- Using `/copilot-update` to keep the file current

## Additional Resources

### Reference Files

- **[`references/template.md`](references/template.md)** — Complete template for `copilot-instructions.md` with all recommended sections and guidance comments
