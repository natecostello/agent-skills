---
name: pr-status
description: >-
  Show the current status of a pull request — CI checks, review decision, draft
  state, merge readiness, unresolved review threads, and unchecked task items.
  Use when the user says "status of PR", "check PR", "PR status", "is PR ready
  to merge", or "/pr-status". Pass "all" to summarize every open and recently
  merged PR.
argument-hint: [optional PR number, or "all"]
license: MIT
metadata:
  author: natecostello
  version: "0.1"
---

Show the current status of a pull request.

Argument: $ARGUMENTS (optional PR number, e.g. "42". Special values: "all" shows all open + recently merged PRs. If empty, detect from current branch)

## Instructions

You are generating a status snapshot for a pull request. Follow these steps carefully.

**CRITICAL: Task items (unchecked checkboxes in the PR body) are the primary view of remaining work. You MUST always parse and display them. Never skip step 2f.**

### Step 1: Identify the PR(s)

**If the argument is "all":**
Fetch both open and recently merged PRs:
```
gh pr list --state open --json number,headRefName,baseRefName,title,state,mergeable,reviewDecision,isDraft,url
gh pr list --state merged --limit 10 --json number,headRefName,baseRefName,title,state,mergedAt,url
```
Process each PR through Steps 2-4. For merged PRs, skip merge-readiness checks (CI, mergeable, ahead/behind) — only show the merge date, task items, and any unresolved review threads.

**If a PR number was provided** (e.g. "42"):
```
gh pr view $ARGUMENTS --json number,headRefName,baseRefName,title,state,mergeable,reviewDecision,isDraft,url,mergedAt
```
If the PR state is MERGED, note the merge date and skip merge-readiness checks.

**If no argument was provided** (empty string), try the current branch:
```
gh pr view --json number,headRefName,baseRefName,title,state,mergeable,reviewDecision,isDraft,url,mergedAt
```

If that fails, list open PRs and ask which one to check:
```
gh pr list --state open --json number,headRefName,title
```

Extract the owner and repo from the remote:
```
gh repo view --json owner,name -q '.owner.login + "/" + .name'
```

### Step 2: Gather all status signals

Run ALL of the following in parallel to build a complete picture.
For MERGED PRs, only run 2b, 2f, and 2g — skip the rest.

**2a. CI checks** (open PRs only):
```
gh pr checks {pr_number}
```
**IMPORTANT:** Do NOT use `--json` with `gh pr checks` — it silently returns empty results in some versions of `gh`. Use the plain text output and parse the tab-separated columns (name, status, duration, url).

**2b. Review threads (unresolved comments):**
```
gh api graphql -f query='query { repository(owner: "{owner}", name: "{repo}") { pullRequest(number: {pr_number}) { reviewThreads(first: 100) { nodes { isResolved comments(first: 1) { nodes { path author { login } body } } } } } } }'
```

**IMPORTANT:** Use inline values in the GraphQL query (as shown above), NOT `$`-prefixed variables with `-f`/`-F` flags. GraphQL variable names can pick up invisible Unicode artifacts from conversation context, causing silent query failures.

**2c. Reviews** (open PRs only):
```
gh pr view {pr_number} --json reviews --jq '.reviews[] | {author: .author.login, state: .state}'
```

Also check if the Copilot review is an error (state is COMMENTED but body contains the error):
```
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews --jq '[.[] | select(.user.login == "copilot-pull-request-reviewer[bot]")] | last | .body'
```
If the body contains "encountered an error" or "unable to review", report the review as **ERRORED** (not COMMENTED) and list it as a blocking issue with the suggestion to re-request: `/pr-resolve-comments {pr_number}`

**2d. Labels and assignees** (open PRs only):
```
gh pr view {pr_number} --json labels,assignees
```

**2e. Branch status** (open PRs only):
```
git fetch origin {baseRefName} {headRefName} 2>/dev/null
git rev-list --left-right --count origin/{baseRefName}...origin/{headRefName}
```

**2f. Task items in PR body — MANDATORY, never skip this:**
```
gh pr view {pr_number} --json body --jq '.body'
```
You MUST parse the body text and extract ALL checkbox items:
- Count checked items: lines matching `- [x]` or `- [X]` (case-insensitive)
- Count unchecked items: lines matching `- [ ]`
- Extract the full text of each unchecked item for display
- If the body is empty or has no checkboxes, report "No task items"

**Distinguish DEFERRED from blocking items:**
- Items in a `## Deferred` section (not checkboxes — just bullet points with issue links) are NOT blocking. Display them under a separate "Deferred work" heading.
- Items containing `~~DEFERRED~~` or tagged with `#{issue_number}` and the word "deferred" are NOT blocking. Display them under "Deferred work" instead of "Blocking Issues."
- **Only genuinely unchecked test/verification items are blocking** — list those in the Blocking Issues section.

**2g. Copilot sub-PRs:**
```
gh pr list --state open --json number,headRefName,title --search "head:copilot/sub-pr-{pr_number}"
```

### Step 3: Compile the status report

**For OPEN PRs**, present:

```
## PR #{number}: {title}
Branch: {headRefName} → {baseRefName}
URL: {url}
State: {state} {isDraft ? "(Draft)" : ""}

### Merge readiness
- Mergeable: {MERGEABLE / CONFLICTING / UNKNOWN}
- Review decision: {APPROVED / CHANGES_REQUESTED / REVIEW_REQUIRED / none}
- Branch: {N} commits ahead, {M} behind {baseRefName}

### CI checks
- ✅ {check_name} — passed
- ❌ {check_name} — failed
- ⏳ {check_name} — in progress
- ⏭️ {check_name} — skipped
(or "No CI checks configured")

### Review comments
- {N} unresolved thread(s)
  - {file}:{line} — {reviewer}: {first 80 chars of comment}...
- {M} resolved thread(s)
(or "No review comments")

### Reviews
- {reviewer}: {APPROVED / CHANGES_REQUESTED / COMMENTED}
(or "No reviews yet")

### Task items
- {N} of {M} tasks complete
  - ☐ {unchecked item text}
  - ☐ {unchecked item text}
(or "No task items" if the PR body has no checkboxes)

### Deferred work
- {description} — #{issue_number}
(or omit this section if no deferred items exist)

### Copilot sub-PRs
- PR #{sub_number}: {title} ({branch})
(or "None")

### Blocking issues
List anything that prevents merging:
1. {issue description} → suggested fix
```

**For MERGED PRs**, present a shorter format:

```
## PR #{number}: {title} ✅ MERGED
Branch: {headRefName} → {baseRefName}
URL: {url}
Merged: {mergedAt}

### Task items
- {N} of {M} tasks complete
  - ☐ {unchecked item text} ← not completed before merge
(or "All tasks complete" / "No task items")

### Review comments
- {N} unresolved thread(s) remaining
(or "All threads resolved")
```

### Step 4: Assess overall readiness

**For OPEN PRs**, end with a one-line summary:

- **Ready to merge** — all checks pass, no conflicts, approved (or no review required), no unresolved threads, no unchecked task items (DEFERRED items with tracked issues do NOT block merge)
- **Almost ready** — minor issues only (e.g., unresolved comments but no code changes needed, or CI pending, or only DEFERRED items remain)
- **Blocked** — has conflicts, failing CI, changes requested, unresolved threads requiring code changes, or unchecked non-deferred task items in the PR body

For each blocking issue, suggest the appropriate command:
- Unresolved comments → `/pr-resolve-comments {pr_number}`
- CI failures → `/pr-resolve-ci-failures {pr_number}`
- Merge conflicts → `/resolve-pr-conflicts {pr_number}`
- Unchecked task items → "Complete test plan items before merging" (list each unchecked item)
- Changes requested / needs approval → "Requires human review"
- Draft PR → "Convert to ready for review when done"

**For MERGED PRs**, end with:
- **Clean merge** — all tasks were complete, all threads resolved
- **Merged with loose ends** — list unchecked tasks or unresolved threads that remain
