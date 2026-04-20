---
name: adr-new
description: >-
  Create a new Architecture Decision Record. Use when the user says "new ADR",
  "create ADR", "write an ADR", "document this decision", or needs to record an
  architectural decision.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
disable-model-invocation: true
argument-hint: "<short title of the decision, e.g. \"use SQLite for caching\">"
---

# Create a New Architecture Decision Record

Create a new ADR in `docs/architecture/` following the MADR 4.0 template.

## Workflow

### 1. Verify ADR Directory Exists

```bash
ls docs/architecture/README.md 2>/dev/null
```

If the directory doesn't exist, stop and suggest running `/adr-init` first.

### 2. Determine the Next ADR Number

```bash
ls docs/architecture/[0-9]*.md 2>/dev/null | sort -n | tail -1
```

Extract the highest number and increment by 1. Pad to 4 digits (e.g., `0004`).

### 3. Gather Decision Context

If `$ARGUMENTS` provides a title, use it. Otherwise, ask the user for:
- What decision needs to be made?
- What problem is this solving?

Then research the codebase to understand the context:
- Read relevant source files to understand current architecture
- Check existing ADRs for related decisions
- Identify the specific forces/constraints at play

### 4. Draft the ADR

Use the template in [references/template.md](references/template.md). Fill in:

- **Frontmatter**: Set status to `proposed`, today's date, decision-makers (ask the user if not obvious)
- **Title**: Short noun phrase (from argument or discussion)
- **Context**: 2-5 sentences describing the problem and forces
- **Decision Drivers**: 3-5 bullet points of constraints/requirements
- **Considered Options**: Always include "Status quo / do nothing" as the baseline option. Include at least one additional alternative (ideally 2). Every rejected option must have a specific reason tied to an actual constraint — not vague ("too complex") but concrete ("incompatible with our no-external-runtime-deps constraint per ADR-0003")
- **Decision Outcome**: Which option was chosen and why
- **Consequences**: Good, neutral, and bad outcomes
- **Confirmation**: How to verify correct implementation
- **Pros and Cons**: Detailed analysis of each option
- **More Information**: Leave as "To be implemented in PR #TBD" if the PR doesn't exist yet

Related ADRs: Check existing ADRs and link any that are related.

### 5. Write the File

Write to `docs/architecture/NNNN-<kebab-case-title>.md`.

### 6. Update the ADR Index

Read `docs/architecture/README.md` and add a new row to the index table:

```markdown
| [NNNN](NNNN-kebab-case-title.md) | Short description | Proposed |
```

### 7. Report

Print:
- Path to the new ADR
- Reminder to update status from `proposed` to `accepted` after the implementing PR merges
- Reminder to update the "More Information" section with the PR number after submission
