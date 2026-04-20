---
name: copilot-update
description: >-
  This skill should be used when the user asks to "update copilot
  instructions", "refresh copilot config", "sync copilot instructions with
  the repo", or when the repository structure, conventions, or architecture
  has changed and .github/copilot-instructions.md needs to reflect those
  changes.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
argument-hint: "[optional section to update, e.g. \"project layout\"]"
---

# Update Copilot Code Review Instructions

Update `.github/copilot-instructions.md` to reflect the current state of the repository, ensuring GitHub Copilot has accurate context for pull request reviews.

## Workflow

### 1. Read the Current File

Read `.github/copilot-instructions.md`. If it does not exist, stop and suggest `/copilot-init` instead.

### 2. Determine Scope

If `$ARGUMENTS` specifies a section or topic, focus the update on that area only.

If no specific area is given, audit all sections for drift:

**Repository Summary** — Read `README.md` and `CLAUDE.md`. Has the project's purpose or scope changed?

**Build, Test, and Lint** — Read `pyproject.toml`, `package.json`, `Makefile`, or equivalent. Have commands changed? Have new tools been added? Have environment variables changed?

**Architecture** — Are there new components, services, or external dependencies not mentioned? Have high-risk areas changed?

**Project Layout** — Run `ls` on the top-level directory. Are there new directories or important files not listed? Check `.github/workflows/` for CI changes.

**Key Abstractions** — Are listed types still the most important? Have new key abstractions been added?

**Dependencies and Non-Obvious Relationships** — Have new coupling points been introduced?

**Planning Documents** — Are there new docs in `docs/` that code should align with? Have existing plans been updated?

**Coding Conventions** — Has linter/formatter config changed? Have conventions in `CLAUDE.md` or `CONTRIBUTING.md` been updated? Check for new commit prefixes or style rules.

**Code Review Focus Areas** — Are listed areas still relevant? Should new areas be added based on recent work? Check recent PR review history for recurring patterns that required multiple review rounds to catch — these indicate missing focus areas. Key patterns to look for:
- Error handling gaps (silent failures producing misleading output)
- Missing truncation/pagination handling
- Multi-valued field parsing (tokenization before matching)
- N+1 query patterns (loop of single calls vs batch API)
- Input validation inconsistencies across code paths
- Shell script portability issues (GNU-only flags)
- Code duplication across modules
- Security issues (command injection, unsanitized external input)
- Documentation drift (behavior changes without README/CLAUDE.md updates)

If the "Code Review Focus Areas" section does not include a documentation consistency item (checking README.md/CLAUDE.md updates when user-facing behavior changes), add one.

**What NOT to Flag** — Are there new patterns reviewers should not flag? Are existing items still applicable?

### 3. Apply Updates

For each section that needs updating:

1. Read relevant source files to get accurate current information
2. Update the section with concrete, verified content
3. Do not add generic boilerplate — every line must be specific to this repo
4. Preserve existing structure and section ordering
5. Do not rewrite sections that are already accurate
6. **Bump the rev marker** — if the file has a `<!-- rev: N -->` comment and a corresponding `[copilot-instructions rev N]` echo line, increment both to N+1 whenever any content changes are made

Constraints:
- The Role section must always state Copilot is a code reviewer only
- Keep the file concise — reference material, not documentation
- Verify every fact against actual repo contents

### 4. Update CLAUDE.md

If the `CLAUDE.md` reference to `copilot-instructions.md` is missing or outdated, update it.

### 5. Report

Print a summary:
- Sections updated (with brief description of what changed)
- Sections verified as current (no changes needed)
- Sections where accuracy could not be verified (suggest manual review)
