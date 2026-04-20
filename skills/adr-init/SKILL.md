---
name: adr-init
description: >-
  Set up ADR (Architecture Decision Record) scaffolding for a project. Use when
  the user says "init ADR", "set up ADRs", "add ADR support", "initialize
  architecture decisions", or needs to create the ADR directory structure and
  guidance.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
disable-model-invocation: true
argument-hint: "[optional project path]"
---

# Initialize ADR Scaffolding

Set up the directory structure, templates, guidance, and tooling references for Architecture Decision Records using MADR 4.0.

## Workflow

### 1. Verify This Is a Git Repository

```bash
git rev-parse --show-toplevel
```

If not a git repo, stop and inform the user.

### 2. Check for Existing ADR Setup

```bash
ls docs/architecture/README.md 2>/dev/null
```

If the directory and README already exist, report what's already set up and ask if the user wants to update/regenerate any components.

### 3. Ask Who the Decision-Maker(s) Are

Before creating any files, ask the user:

> "Who should be listed as the default decision-maker(s) for ADRs in this project? This will be added to the project guidance so future ADRs include proper attribution. (e.g., a name, role, or team)"

Wait for the user's response before proceeding. Store their answer for use in Step 5.

### 4. Create the ADR Directory

```bash
mkdir -p docs/architecture
```

### 5. Create the ADR Index (README.md)

Use the template from [references/adr-readme-template.md](references/adr-readme-template.md) to create `docs/architecture/README.md` with an empty ADR table.

### 6. Add ADR Guidance to Project CLAUDE.md

If `CLAUDE.md` exists in the project root, add an ADR section. If it doesn't exist, create one with just the ADR section.

Add the following section (adapt to the project's existing structure):

```markdown
## Architecture Decision Records

ADRs are stored in `docs/architecture/` using [MADR 4.0](https://adr.github.io/madr/) format.

### When to write an ADR

Write an ADR when a decision:
- Changes how data flows between major components
- Affects public APIs or interfaces
- Changes the build, deployment, or packaging architecture
- Involves trade-offs between competing concerns that were debated
- Is hard to reverse once implemented
- Affects non-functional requirements (performance, security, privacy)

Do NOT write an ADR for: bug fixes, dependency updates, formatting changes, or routine refactoring.

### Default decision-maker(s)

<decision-maker(s) from Step 3>

### Template conventions

- **Frontmatter** must include `status`, `date`, `decision-makers`, and `related ADRs`
- Optional frontmatter: `consulted`, `informed` (per MADR 4.0 RACI convention)
- **Plan references**: If a planning document was created, reference it in Decision Outcome with the commit hash where it can be found
- **PR references**: Include implementing PR number and merge date in "More Information"

### Numbering and lifecycle

- Files: `docs/architecture/NNNN-kebab-case-title.md` (4-digit zero-padded)
- Status values: `proposed`, `accepted`, `rejected`, `deprecated`, `superseded by ADR-NNNN`
- New ADRs start as `proposed`; update to `accepted` when the implementing PR merges
- Use `rejected` when an approach was evaluated and deliberately not adopted — these are valuable records

### Amendments and updates

- For partial updates to an existing decision, create a new ADR referencing the original
- Update the original's "More Information" with "Amended by ADR-NNNN" but keep its status as `accepted`
- Reserve `superseded by ADR-NNNN` for complete replacement of a decision
- ADRs can be written retroactively — use the original decision date and note "(retroactive)" in More Information

### Before starting non-trivial work

1. Read `docs/architecture/README.md` index
2. Identify ADRs whose topics are relevant to the files being modified
3. Read each relevant ADR in full
4. Honor constraints from `accepted` ADRs — if planned work would violate or obsolete one, draft a superseding ADR before proceeding

### ADR guardrails

- Never set status to `accepted` without human confirmation that a PR was merged
- Never edit the "Decision Outcome" section of an `accepted` ADR — supersede it instead
- Never delete any ADR file regardless of status
- Every rejected option must have a specific reason tied to an actual constraint — not vague ("too complex") but concrete ("incompatible with our no-external-runtime-deps constraint per ADR-0003")
- Always read the existing ADR index before drafting a new one (prevents number collisions and redundant ADRs)

### After a PR implementing a `proposed` ADR merges

1. Update `status` from `proposed` to `accepted`
2. Fill in the "More Information" section with PR number and merge date
3. Update the status column in `docs/architecture/README.md`
4. Check Consequences for any follow-on actions — surface uncompleted items to the user

### Superseding an existing ADR

1. Draft a new ADR (via `/adr-new`) with the new decision
2. In the new ADR's frontmatter, add `related ADRs: "Supersedes ADR-NNNN"`
3. In Context, explain why the prior decision is being revisited
4. After human approves the new ADR:
   - Update the old ADR's status to `superseded by ADR-NNNN`
   - Update `docs/architecture/README.md` for both records
```

### 7. Add ADR Link to README.md

If `README.md` exists and has an Architecture section, add a link to the ADR directory. Look for headings like "## Architecture", "## Design", or "## How It Works".

Add a sentence like:
```
Architecture decisions are documented as [ADRs](docs/architecture/).
```

### 8. Add ADR Section to CONTRIBUTING.md

If `CONTRIBUTING.md` exists, add an Architecture Decisions section:

```markdown
## Architecture Decisions

Significant design decisions are recorded as [Architecture Decision Records (ADRs)](docs/architecture/) using the [MADR 4.0](https://adr.github.io/madr/) format.

**When to write an ADR:** If your change affects data flow, public APIs, build/deployment architecture, or module boundaries — write an ADR. See the full criteria in `CLAUDE.md`.

**Process:** Create a new ADR in `docs/architecture/` using the next sequential number. Set status to `proposed` until the implementing PR merges, then update to `accepted`. Reference the implementing PR in the "More Information" section.
```

### 9. Add ADR Section to PR Template

If `.github/PULL_REQUEST_TEMPLATE.md` exists, add an Architecture section:

```markdown
## Architecture
<!-- If this PR adds, changes, or removes an ADR in docs/architecture/, check the box and link it -->
- [ ] ADR created/updated: <!-- link to ADR -->
- [x] No architectural decision needed
```

### 10. Add ADR Review Focus to Copilot Instructions

If `.github/copilot-instructions.md` exists, add an ADR compliance focus area to the "Code Review Focus Areas" section:

```
N. **ADR compliance** — if the PR adds or modifies an ADR in `docs/architecture/`, verify it follows MADR 4.0 format (frontmatter with status/date/related ADRs, Decision Drivers, Considered Options with pros/cons, Decision Outcome with Consequences and Confirmation). If the PR changes architecture without an ADR, flag it as needing one
```

### 11. Report

Print a summary of what was created/modified:
- ADR directory and index
- CLAUDE.md guidance
- README.md link
- CONTRIBUTING.md section
- PR template section
- Copilot instructions focus area

Remind the user:
- Use `/adr-new <title>` to create new ADRs
- Existing decisions can be captured retroactively
- The `/adr-new` skill uses the MADR 4.0 template with the project's conventions

## Additional Resources

### Reference Files

- **[`references/adr-readme-template.md`](references/adr-readme-template.md)** — Template for the ADR index README
- The `/adr-new` skill contains the full MADR 4.0 ADR template at `~/.claude/skills/adr-new/references/template.md`
