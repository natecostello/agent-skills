---
name: audit-repo
description: >-
  Start an independent audit loop monitoring a GitHub repo for merged PRs.
  Reviews diffs, DA reports, metrics, and process compliance with graduated
  response (watch → warn → block) and corrective action recommendations.
  Trigger with "/audit-repo owner/repo" or "start auditing this repo".
license: MIT
metadata:
  author: natecostello
  version: "0.1"
disable-model-invocation: true
argument-hint: <owner/repo> [--interval 5m] [--audit-dir /path/to/audit/log]
---

# Audit Repo

Independent auditor loop for monitoring an autonomous agent working on a GitHub
repository. Reviews every merged PR for safety, quality, and process compliance.
Detects rule violations and development friction, then prescribes corrective
actions targeting the scaffolding itself (CLAUDE.md, skills, Copilot instructions,
CI).

## Arguments

- `owner/repo` (required) — the GitHub repository to monitor
- `--interval` (optional, default: `5m`) — polling interval
- `--audit-dir` (optional, default: `~/audit-logs/<repo>`) — where to write the audit log

## Setup

1. Parse the arguments. Extract `owner/repo`, interval, and audit directory.
2. Create the audit directory if it doesn't exist.
3. Initialize the audit log (`log.md`) with a header if it doesn't exist.
4. Record the current timestamp as the "last checked" marker.
5. Write the monitoring prompt (below) to `{audit_dir}/prompt.md`, with all
   `{owner/repo}` and `{audit_dir}` placeholders interpolated to their actual values.
6. Start the loop: `/loop <interval> @{audit_dir}/prompt.md`

## Monitoring Prompt

Write the following to `{audit_dir}/prompt.md` (with placeholders resolved):

````
Self-check preamble — before doing any evaluation, echo these values:
  Repo: {owner/repo}
  Audit dir: {audit_dir}
  Last entry timestamp: <parsed from last line of {audit_dir}/log.md>
  PRs to review: <list PR numbers>

Check the repo {owner/repo} for PRs merged since the last audit entry in
{audit_dir}/log.md. Parse the timestamp from the last entry line (format:
YYYY-MM-DD HH:MM). Convert to ISO-8601 with UTC offset for the gh query:
  gh pr list -R {owner/repo} --state merged --search "merged:>YYYY-MM-DDTHH:MM:00Z" --limit 100 --json number,title,mergedAt

Skip any PR whose number already appears in {audit_dir}/log.md (deduplication).

For each new merged PR:
1. Read the full diff: gh pr diff {number} -R {owner/repo}
2. Read the PR body: gh pr view {number} -R {owner/repo} --json body,title,mergedAt,additions,deletions,changedFiles
3. Check for DA report in the PR description (look for "Devil's advocate" or "DA review")
4. Check for metrics update: gh api repos/{owner/repo}/contents/docs/metrics.md -H "Accept: application/vnd.github.raw" 2>/dev/null
5. Read the commit messages: gh pr view {number} -R {owner/repo} --json commits

Evaluate each PR on TWO dimensions:

### Dimension 1: Safety (same as before)
- Security: injection risks, exposed secrets, resource exhaustion vectors
- Cost: infrastructure changes that increase spend
- Privacy: unqualified "data never leaves" claims or similar
- Governance: modifications to protected CLAUDE.md sections

### Dimension 2: Process & Quality
Check every PR against these process signals. Each finding gets logged
with a short description and a corrective action recommendation.

**Rule compliance:**
- DA review present? Look for "Devil's advocate" or "DA review" or
  "no concerns raised" in PR body. Missing = violation.
- Copilot review present? Check PR reviews for copilot-pull-request-reviewer.
  Missing = violation.
- Branch naming convention? Must match `feat/`, `fix/`, `chore/`, `docs/`
  + issue number. Check: `gh pr view {number} --json headRefName`
- Commit convention? Imperative, lowercase, prefixed (feat:, fix:, chore:,
  docs:). Check: `gh pr view {number} --json commits`
- Issue linked? PR body should contain "Closes #N" or "Fixes #N".
  No linked issue = violation.
- Labels applied? Every issue/PR should have labels. Cost-affecting PRs
  MUST have `cost-impact`. ADR PRs MUST have `adr`.
- Metrics updated? After each merge, `docs/metrics.md` should have a new
  entry. Check: `gh api repos/{owner/repo}/contents/docs/metrics.md`
  and verify the PR count matches merged PR count.
- ADR written when needed? If the PR changes deployment architecture,
  cost config, or security posture, there should be an ADR.

**Quality signals (patterns across PRs):**
- Copilot round inflation: 4+ review rounds on a single PR suggests
  the agent is pushing sloppy code and iterating via review. Track the
  trend across PRs.
- DA rubber-stamping: If 5+ consecutive PRs have "no concerns raised",
  the DA prompt may be too weak or the agent is gaming it.
- Reverts: Any revert PR is an automatic WATCH. Two reverts = WARN.
- CI failures after merge: Check Actions for red on main branch.
  `gh run list -R {owner/repo} -b main --status failure --json databaseId`
- Missing tests: PR adds functionality but no test files changed.
  Check `changedFiles` for test file presence.
- Scope creep: PR touches 15+ files or 500+ lines for a single issue.
  Not always bad, but worth flagging.
- Stale branches: Check for branches not merged after 48+ hours.
  `gh api repos/{owner/repo}/branches --jq '.[].name'`
- Self-modification violations: Did the agent modify protected CLAUDE.md
  sections, global skills, or global settings?
- Skills quality: Are created skills actually being used? Are they
  tested through the PR workflow?
- Multi-issue iterations: If multiple PRs merge with timestamps close
  together (within minutes) and the iteration logs show only one
  iteration ran, the agent is handling multiple issues per iteration
  instead of exiting with CONTINUE after each one. This risks context
  exhaustion and stalls. Automatic WARN — this is a reliability issue,
  not just a style preference.

### Corrective Actions

For every WATCH or WARN finding, include a concrete corrective action
recommendation. Corrective actions target the scaffolding, not the
code — the goal is to prevent recurrence by fixing the system.

**Categories of corrective action:**

1. **CLAUDE.md (project-local):** Suggest additions or clarifications
   to the agent's CLAUDE.md that would prevent the violation. Example:
   "Add to CLAUDE.md PR Workflow: 'Every PR that adds a new endpoint
   MUST include a test that hits the endpoint.'"

2. **CLAUDE.md (global):** Suggest changes to ~/.claude/CLAUDE.md if
   the pattern applies across projects. These are rare — only recommend
   when the same issue would affect any project.

3. **Copilot instructions:** Suggest additions to
   `.github/copilot-instructions.md` that would cause Copilot to catch
   the issue in review. Example: "Add to copilot-instructions.md:
   'Flag PRs that modify fly.toml without a cost-impact label.'"

4. **Skills:** Suggest new skills or modifications to existing skills.
   Example: "Create a /pre-merge-checklist skill that verifies DA
   review, Copilot review, CI, labels, and linked issue before merge."

5. **CI pipeline:** Suggest CI checks that would catch the issue
   automatically. Example: "Add a CI step that fails if a PR modifies
   docs/architecture/ without the `adr` label."

6. **Other scaffolding:** Issue templates, PR templates, label
   automation, branch protection rules, etc.

**Corrective action format in the audit log:**

```
YYYY-MM-DD HH:MM — PR #N: WATCH [no-da-report]: Missing DA review
  ↳ Corrective: CLAUDE.md (local): Add to Autonomy Rules checklist —
    "Verify DA review section exists in PR body before merging"
```

```
YYYY-MM-DD HH:MM — PR #N: WARN [missing-tests]: 3rd consecutive PR with no tests (issue #M created)
  ↳ Corrective: Copilot instructions: Add "Flag PRs that add new
    Python files without corresponding test files"
  ↳ Corrective: CI: Add pytest --co (collect-only) check that fails
    if test count doesn't increase when src/ files are added
```

Multiple corrective actions per finding are fine — list all that apply.

**When recommending corrective actions:**
- Be specific enough that the agent (or human) could implement the
  change with no ambiguity
- Quote the exact section/file to modify
- Prefer the least invasive fix (Copilot instruction > CLAUDE.md rule
  > CI check > new skill)
- Do NOT recommend corrective actions for one-off mistakes that the
  agent self-corrected in the same PR

Apply graduated response:

### WATCH (log only)
Minor concern, first occurrence. Assign a kebab-case tag from this
vocabulary: `unpinned-image`, `missing-tests`, `no-da-report`,
`no-linked-issue`, `no-copilot-review`, `unqualified-privacy-claim`,
`cost-increase`, `scope-creep`, `branch-naming`, `commit-convention`,
`missing-labels`, `missing-metrics`, `missing-adr`, `copilot-round-inflation`,
`da-rubber-stamp`, `revert`, `ci-failure-on-main`, `self-modification`,
`stale-branch`, `multi-issue-iteration`. If none fit, create a new kebab-case tag.

Append to {audit_dir}/log.md:
"YYYY-MM-DD HH:MM — PR #N: WATCH [tag]: <description>"
No GitHub action.

### WARN (GitHub issue, non-blocking)
Grep {audit_dir}/log.md for prior WATCH entries with the same [tag].
If a matching tag exists and the current PR doesn't fix it, escalate
to WARN. Also escalate for a single moderate-severity issue.
Create a GitHub issue:
  gh issue create -R {owner/repo} \
    --title "Audit warning: <short description>" \
    --label "audit:warning" \
    --body "<detailed explanation with PR references>

  🤖 Generated by independent auditor via [Claude Code](https://claude.ai/code)"

Append to {audit_dir}/log.md:
"YYYY-MM-DD HH:MM — PR #N: WARN: <description> (issue #M created)"

### BLOCK (GitHub issue, stops the loop)
Bright-line violation. Create a blocking issue:
  gh issue create -R {owner/repo} \
    --title "Audit BLOCK: <short description>" \
    --label "priority:blocking" \
    --body "<detailed explanation of the violation>

  🤖 Generated by independent auditor via [Claude Code](https://claude.ai/code)"

Append to {audit_dir}/log.md:
"YYYY-MM-DD HH:MM — PR #N: BLOCK: <description> (issue #M created)"

After creating the blocking issue and appending to the log, cancel the
audit loop immediately: run `CronList` to find this loop's job id
(match by the prompt or schedule you started with), then
`CronDelete <job-id>`.

### Bright Lines (block immediately)
- Projected steady-state cost exceeds $25/mo
- Security vulnerability in an exposed endpoint
- Unqualified privacy claims ("data never leaves your machine" without
  distinguishing local LLM vs cloud LLM vs remote demo)
- Modification of governance/protected sections in CLAUDE.md

### What NOT to block on
- Style or formatting disagreements
- Approach differences (the agent chose differently than you would)
- Things the agent could self-correct in a subsequent iteration
- Missing nice-to-haves that aren't in the spec

The bar for blocking is: "this will cause real harm if it ships."

### No new PRs
If no new PRs have merged since the last check, append:
"YYYY-MM-DD HH:MM — No new activity"
Do NOT create issues or take any action.

### Terminal Status (REQUIRED)

After every check, print a brief status summary to the terminal so the
operator can glance at the CLI and see the loop is alive. Format:

```
[AUDIT HH:MM] repo — N PRs reviewed | OK: N | WATCH: N | WARN: N | BLOCK: N | Correctives: N open | Total merged: N | Open issues: N
```

Examples:
```
[AUDIT 14:35] natecostello/genechat-mcp-remote-demo — 1 PR reviewed | OK: 1 | WATCH: 0 | WARN: 0 | BLOCK: 0 | Correctives: 0 open | Total merged: 3 | Open issues: 8
[AUDIT 14:40] natecostello/genechat-mcp-remote-demo — No new activity | Correctives: 0 open | Total merged: 3 | Open issues: 8
[AUDIT 14:45] natecostello/genechat-mcp-remote-demo — 2 PRs reviewed | OK: 1 | WATCH: 1 | WARN: 0 | BLOCK: 0 | Correctives: 2 open | Total merged: 5 | Open issues: 6
```

This line is always printed, even on "no new activity" checks. It serves
as a heartbeat — if the operator doesn't see a new line every interval,
the loop has stopped.
````

## Audit Log Format

The audit log at `{audit_dir}/log.md` uses this format:

```markdown
# Audit Log: {owner/repo}
Started: YYYY-MM-DD HH:MM

## Entries

YYYY-MM-DD HH:MM — PR #1: OK — "chore: initial bootstrap" (3 files, +120/-0, 1 Copilot round, DA clean)
YYYY-MM-DD HH:MM — PR #2: WATCH [unpinned-image]: Dockerfile doesn't pin base image version
  ↳ Corrective: Copilot instructions: Add "Flag Dockerfiles with unpinned base images (e.g., python:3.11-slim without @sha256 digest)"
YYYY-MM-DD HH:MM — PR #3: OK — "feat: add fly.toml" (2 files, +45/-0, 2 Copilot rounds, DA raised 1 concern addressed)
YYYY-MM-DD HH:MM — PR #4: WARN [unpinned-image]: Base image still unpinned after 2 PRs (issue #12 created)
  ↳ Corrective: CLAUDE.md (local): Add to PR Workflow — "Dockerfiles MUST pin base images with digest or exact version tag"
  ↳ Corrective: CI: Add hadolint or similar Dockerfile linter to catch unpinned images
YYYY-MM-DD HH:MM — PR #5: WATCH [no-linked-issue]: Missing linked issue — PR created without "Closes #N"
  ↳ Corrective: CLAUDE.md (local): Add to Autonomy Rules — "Every PR MUST reference an issue via 'Closes #N' in the body"
YYYY-MM-DD HH:MM — PR #6: WATCH [copilot-round-inflation]: 4 Copilot review rounds — agent iterating via review instead of pre-validating
  ↳ Corrective: Skills: Create /pre-push-check skill that runs ruff, tests, and Dockerfile build locally before pushing
YYYY-MM-DD HH:MM — No new activity
```

Each entry is one line (corrective actions indented below with ↳). OK entries
include: title, file count, lines changed, Copilot review rounds, DA result.
This makes it scannable while keeping corrective actions attached to their finding.

## Periodic Process Report

Every 5 PRs (or when a pattern emerges across 3+ PRs), append a process
summary block to the audit log:

```markdown
## Process Report (PRs #1-#5)

### Trends
- Avg Copilot rounds: 2.4 (target: trending down)
- DA signal rate: 40% (healthy range)
- PRs with linked issues: 4/5 (80%)
- PRs with tests: 3/5 (60%)
- Branch naming compliance: 5/5 (100%)

### Outstanding Corrective Actions
| # | Finding | Corrective | Target | Status |
|---|---------|------------|--------|--------|
| 1 | Unpinned base image (PR #2, #4) | Copilot instructions + CI linter | .github/copilot-instructions.md, CI | Open |
| 2 | Missing linked issues (PR #5) | CLAUDE.md rule | CLAUDE.md | Open |

### Recommendations
- Priority: Add Dockerfile linter to CI — this has recurred twice and
  Copilot isn't catching it
- Consider: /pre-push-check skill to reduce Copilot review rounds
```

Track corrective action status across reports:
- **Open** — recommended but not yet implemented by the agent
- **Implemented** — the agent picked it up (check for the change in a
  subsequent PR)
- **Declined** — the agent or human explicitly chose not to implement
  (note why)

If a corrective action stays Open for 5+ PRs, escalate from WATCH to
WARN with a GitHub issue.

## Stopping

The audit loop runs until:
- You stop it manually (Ctrl-C or close the session)
- You cancel the scheduled job by finding its id via `CronList`, then
  running `CronDelete <job-id>`
- A BLOCK finding: the agent cancels the loop as part of the BLOCK
  workflow above (`CronList` + `CronDelete <job-id>`)
