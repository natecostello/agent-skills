---
name: code-review
description: >-
  Code review a pull request — runs parallel sub-agent reviewers (CLAUDE.md
  compliance, bugs, git history, prior PR comments, code comments,
  documentation), scores findings for confidence, and posts results as a
  single GitHub PR review with inline comments anchored to modified lines.
  Use when the user says "code review", "review PR", "code review PR", or
  "/code-review". Accepts a PR number; pass `force` or `re-review` to override
  the duplicate-review gate.
license: Apache-2.0
metadata:
  author: Anthropic
  modified-by: natecostello
  version: "0.1"
allowed-tools: Bash(gh issue view:*), Bash(gh search:*), Bash(gh issue list:*), Bash(gh pr comment:*), Bash(gh pr diff:*), Bash(gh pr view:*), Bash(gh pr list:*), Bash(gh pr edit:*), Bash(gh label create:*), Bash(gh api:*)
disable-model-invocation: false
---

Provide a code review for the given pull request.

<custom>Note: custom and ignore tags are used to mark up the "stock" skill/command.  Treat text bounded by "<custom></custom>" as insertions  Treat text bounded by "<ignore></ignore>" as deletions.</custom>

To do this, follow these steps precisely:

1. Use a Haiku agent to check if the pull request (a) is closed, (b) is a draft, or (c) does not need a code review (eg. because it is an automated pull request, or is very simple and obviously ok). If so, do not proceed.

   For duplicate-review detection (d): if there is already a review from you (identifiable by the "Generated with [Claude Code](https://claude.ai/code) using /code-review" footer in the review body) whose `commit_id` matches the current PR HEAD SHA, *skip the review work* (steps 1.5 through 8). Do not re-review, do not re-post, do not touch the `:in-progress` / `:reviewed` labels. Instead, jump directly to **step 9 (approval gate)** and then exit. Rationale: between the prior review and this invocation, the author may have resolved threads that were blocking approval — the skill grants `:approved` in that case without needing a new commit. A stale review on an older SHA does not gate — re-review the new commits.

   Override: if the command arguments include `force` or `re-review` (in addition to the PR number), skip the duplicate-review gate entirely and proceed. The (a)/(b)/(c) gates still apply.
<custom>
1.5. Signal "review in progress" by labeling the PR with `claude/code-review:in-progress`, so other agents or humans monitoring the PR know a review is underway. Also pre-create the `claude/code-review:reviewed` and `claude/code-review:approved` labels that steps 8.i and 8.j will apply on completion. Remove any stale `:approved` from the PR — a new HEAD invalidates prior approval regardless of this run's outcome, and the approval gate in step 8.j will re-apply it if the new review earns it. Run:

     gh label create "claude/code-review:in-progress" --color 1f6feb --description "Claude Code review in progress" --force --repo <owner>/<repo> 2>/dev/null || true
     gh label create "claude/code-review:reviewed"    --color 0e8a16 --description "Claude Code review complete"    --force --repo <owner>/<repo> 2>/dev/null || true
     gh label create "claude/code-review:approved"    --color 2ea043 --description "Claude code-review reviewer approved this PR" --force --repo <owner>/<repo> 2>/dev/null || true
     gh pr edit <N> --remove-label "claude/code-review:approved" --repo <owner>/<repo> 2>/dev/null || true
     gh pr edit <N> --add-label "claude/code-review:in-progress" --repo <owner>/<repo>

     The `--force` makes `gh label create` idempotent (overwrites color/description if the label already exists). The `|| true` swallows the "already exists" error on older gh versions. The in-progress label MUST be removed in step 8 (or at any earlier exit after this point).
</custom>
2. Use another Haiku agent to give you a list of file paths to (but not the contents of) any relevant CLAUDE.md files from the codebase: the root CLAUDE.md file (if one exists), as well as any CLAUDE.md files in the directories whose files the pull request modified
3. Use a Haiku agent to view the pull request, and ask the agent to return a summary of the change
4. Then, launch <ignore>5</ignore><custom>6</custom> parallel Sonnet agents to independently code review the change. The agents should do the following, then return a list of issues and the reason each issue was flagged (eg. CLAUDE.md adherence, bug, historical git context, etc.):
   a. Agent #1: Audit the changes to make sure they compily with the CLAUDE.md<custom>, ADRs (if used on this project), and any other specification or planning files </custom>. Note that CLAUDE.md is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
   b. Agent #2: Read the file changes in the pull request, then do a shallow scan for obvious bugs. Avoid reading extra context beyond the changes, focusing just on the changes themselves. Focus on large bugs, and avoid small issues and nitpicks. Ignore likely false positives.
   c. Agent #3: Read the git blame and history of the code modified, to identify any bugs in light of that historical context
   d. Agent #4: Read previous pull requests that touched these files, and check for any comments on those pull requests that may also apply to the current pull request.
   e. Agent #5: Read code comments in the modified files, and make sure the changes in the pull request comply with any guidance in the comments.
<custom>
   f. Agent #6: Audit documentation files (e.g., README.md, etc.) for consistency with code changes within the PR.
</custom>
5. For each issue found in #4, launch a parallel Haiku agent that takes the PR, issue description, and list of CLAUDE.md files (from step 2), and returns a score to indicate the agent's level of confidence for whether the issue is real or false positive. To do that, the agent should score each issue on a scale from 0-100, indicating its level of confidence. For issues that were flagged due to CLAUDE.md instructions, the agent should double check that the CLAUDE.md actually calls out that issue specifically. The scale is (give this rubric to the agent verbatim):
   a. 0: Not confident at all. This is a false positive that doesn't stand up to light scrutiny, or is a pre-existing issue.
   b. 25: Somewhat confident. This might be a real issue, but may also be a false positive. The agent wasn't able to verify that it's a real issue. If the issue is stylistic, it is one that was not explicitly called out in the relevant CLAUDE.md.
   c. 50: Moderately confident. The agent was able to verify this is a real issue, but it might be a nitpick or not happen very often in practice. Relative to the rest of the PR, it's not very important.
   d. 75: Highly confident. The agent double checked the issue, and verified that it is very likely it is a real issue that will be hit in practice. The existing approach in the PR is insufficient. The issue is very important and will directly impact the code's functionality, or it is an issue that is directly mentioned in the relevant CLAUDE.md.
   e. 100: Absolutely certain. The agent double checked the issue, and confirmed that it is definitely a real issue, that will happen frequently in practice. The evidence directly confirms this.<custom>  Documentation issues should be scored 100.</custom>
6. Filter out any issues with a score less than 80. The remaining set (which may be empty) is the review's blocking findings. Proceed to step 7, step 8 (review submission), and step 9 (approval gate) regardless of the filtered count — step 8.f requires a review to be submitted even in the zero-findings case, and step 9's approval gate runs for every invocation that reaches this point. "Do not proceed" here applies only to per-finding inline-comment handling on the empty set, not to the review submission, labeling, or approval path.
7. Use a Haiku agent to repeat the eligibility check from #1, to make sure that the pull request is still eligible for code review.
<ignore>
8. Finally, use the gh bash command to comment back on the pull request with the result. <custom>Include a summary comment of all comments.  Use inline comments for specific comments</custom> When writing your comment, keep in mind to:
   a. Keep your output brief
   b. Avoid emojis
   c. Link and cite relevant code, files, and URLs
</ignore>
<custom>
8. Submit the review as a single GitHub PR *review* (not an issue comment) so each finding becomes a
   resolvable review thread with a "Resolve conversation" button. Do not use `gh pr comment` for this.

   a. Resolve the PR head SHA:
      HEAD_SHA=$(gh api repos/<owner>/<repo>/pulls/<N> --jq '.head.sha')

   b. Build a JSON payload with these top-level fields:
      - `commit_id`: the PR head SHA
      - `event`: always `"COMMENT"`. Do not use `APPROVE` or `REQUEST_CHANGES`. Rationale:
        GitHub rejects both `APPROVE` and `REQUEST_CHANGES` when the review author and the PR
        author resolve to the same GitHub user account — the common case for solo-maintained
        repos where `/code-review` runs under the PR author's login. Blocking vs. non-blocking
        is instead signalled by the finding count in the body marker (`<!-- code-review-findings: N -->`)
        and the task list under `## Findings (N)` (see 8g). If/when this skill runs under a
        distinct reviewer identity, switching blocking findings to `REQUEST_CHANGES` is a
        follow-up, tracked outside this skill.
      - `body`: the review summary (format below)
      - `comments`: array of inline comments, one per finding (see 8c and 8e for anchoring)

   c. Each `comments[]` entry:
      - `path`: file path as it appears in `gh pr diff`
      - `line`: new-file line number to anchor on (the line must appear in a diff hunk or GitHub
        returns 422)
      - `side`: "RIGHT" for added or context lines; "LEFT" only for lines the PR deletes
      - For multi-line spans: add `start_line` and `start_side`; the span ends at `line`/`side`
      - `body`: prose explanation followed, when a mechanical fix exists, by a fenced
        ```suggestion block containing the exact replacement for the anchored line(s)```
      - Do not use `position` (deprecated in favor of `line`/`side`)

   d. Submit the payload with a single API call, using `--input` to avoid quoting issues with nested
      arrays:

      cat > /tmp/review.json <<'EOF'
      {
        "commit_id": "<HEAD_SHA>",
        "event": "COMMENT",
        "body": "...",
        "comments": [
          {
            "path": "src/foo.py",
            "line": 42,
            "side": "RIGHT",
            "body": "Prose explanation.\n```suggestion\nreplacement line\n```"
          }
        ]
      }
      EOF
      gh api repos/<owner>/<repo>/pulls/<N>/reviews -X POST --input /tmp/review.json

   e. Anchoring fallback — prefer inline, fall back to body only when unavoidable. Goal: every
      actionable finding should become a GitHub review thread (each inline comment is a thread),
      because downstream tooling like `/pr-resolve-comments` discovers work via the
      `reviewThreads` GraphQL field.

      - **File-level findings** (concern a file that appears in the PR diff but don't map to a
        specific diff line — e.g., "missing license header", "file-level convention violation"):
        post as an inline comment on the lowest new-file line of that file that appears in a hunk
        (`line: 1, side: "RIGHT"` works for newly added files). Prefix the comment `body` with
        `(file-level) ` so the reader sees the context immediately. Example:

          {
            "path": "src/new_module.py",
            "line": 1,
            "side": "RIGHT",
            "body": "(file-level) New module is missing the Apache-2.0 license header required by CLAUDE.md."
          }

      - **Truly cross-cutting findings** (architectural concerns with no single file anchor, or
        findings about untouched files that the PR should have touched): these cannot be inline.
        Include them in the review `body` under `## Findings (N)` as a task list item with a
        full-SHA blob URL when citing code, and omit the `see inline comment at ...` tail.

   f. No-issues case: still submit a review with `event: "COMMENT"`, the body format below with
      `N = 0` (marker + `## Findings (0)` heading + the literal closing line
      "No issues found. Checked for bugs and CLAUDE.md compliance."), and an empty or omitted
      `comments` array. Keeping the marker present even for zero findings lets tooling reliably
      detect that a `/code-review` review ran.

   g. Review body format (Copilot style). The first line MUST be the machine-readable marker
      — downstream tooling greps for it before parsing the body. `N` is the finding count and
      must match between the marker and the `## Findings (N)` heading:

      <!-- code-review-findings: N -->
      ## Pull request overview
      <one-paragraph summary reused from step 3>

      **Changes:**
      - <bullet 1>
      - <bullet 2>
      - <bullet 3>

      ### Reviewed changes
      | File | Description |
      | ---- | ----------- |
      | <path> | <one-line purpose> |

      ## Findings (N)

      - [ ] <short title> — see inline comment at <path>:<line>
      - [ ] <short title> — see inline comment at <path>:<line>
      (For cross-cutting findings with no inline anchor, use:
       `- [ ] <short title> — <prose with full-SHA blob URL>`)

      🤖 Generated with [Claude Code](https://claude.ai/code) using /code-review

      <sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>

      Rules for the marker + findings block:
      - The HTML comment `<!-- code-review-findings: N -->` is on its own line at the very top
        of the body. Do not wrap it in anything.
      - `N` is the total count of task-list items under `## Findings (N)` (inline + cross-cutting).
      - Task checkboxes are authored as `- [ ]` (unchecked). `/pr-resolve-comments` ticks them
        off as findings are addressed.
      - Zero-findings form:

          <!-- code-review-findings: 0 -->
          ## Pull request overview
          ...

          ## Findings (0)

          No issues found. Checked for bugs and CLAUDE.md compliance.

          🤖 Generated with [Claude Code](https://claude.ai/code) using /code-review

          <sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>

   h. Keep the body brief, avoid emojis in finding text (the trailing robot + feedback line is the
      only exception), and link or cite relevant code/files/URLs with full-SHA blob URLs only in the
      body — inline comments anchor to files/lines natively and do not need URLs.

   i. After the review is submitted, swap the in-progress label for the reviewed label:

         gh pr edit <N> --remove-label "claude/code-review:in-progress" --add-label "claude/code-review:reviewed" --repo <owner>/<repo>

      If you exit early anywhere between step 1.5 and here (e.g. PR became ineligible at the step 7
      recheck, or review submission fails), only remove the in-progress label — do not add the
      reviewed label, since no review was actually posted:

         gh pr edit <N> --remove-label "claude/code-review:in-progress" --repo <owner>/<repo>

</custom>

<custom>
## 9. Approval gate (MANDATORY — runs after every invocation that reaches this point)

This is a separate phase from step 8. It runs on BOTH paths:

- **Fresh-review path:** after step 8.i (label swap) completes.
- **Duplicate-skip path:** entered directly from step 1(d) — nothing from 1.5 through 8 has run,
  but the approval gate still evaluates because threads may have been resolved since the prior
  review was posted.

It does NOT run if the skill exited early before this point (e.g. step 7 ineligibility, review
submission failure). In those cases the in-progress label was already removed per step 8.i's
early-exit guidance; `:approved` is simply not touched.

Evaluate whether this PR has earned `claude/code-review:approved`. Apply the label only if ALL
three conditions hold:

- **(a) No blocking findings on the current-HEAD review.** Determine this from the actual
  posted review body, not from step 6's in-memory filter result. The body's first line is the
  machine-readable marker `<!-- code-review-findings: N -->` (see step 8.g); fetch the latest
  /code-review review for the current HEAD and require `N == 0`. Fallback for legacy reviews
  predating the marker: accept `## Findings (0)` or the literal string "No issues found" in
  the body. This applies equally to the fresh-review and duplicate-skip paths.
- **(b) Every review thread this reviewer opened on this PR is resolved.** Scope: threads
  whose first comment's enclosing review body contains the `/code-review` footer. Paginate
  through ALL threads — a single `reviewThreads(first:N)` page can silently miss unresolved
  threads on busy PRs:

      CURSOR=null
      UNRESOLVED=0
      while :; do
        PAGE=$(gh api graphql \
          -F owner=<owner> -F repo=<repo> -F number=<N> -F cursor="$CURSOR" \
          -f query='
          query($owner:String!, $repo:String!, $number:Int!, $cursor:String) {
            repository(owner:$owner, name:$repo) {
              pullRequest(number:$number) {
                reviewThreads(first:100, after:$cursor) {
                  pageInfo { hasNextPage endCursor }
                  nodes {
                    isResolved
                    comments(first:1) { nodes { pullRequestReview { body } } }
                  }
                }
              }
            }
          }')
        UNRESOLVED=$((UNRESOLVED + $(jq '[.data.repository.pullRequest.reviewThreads.nodes[]
          | select(.comments.nodes[0].pullRequestReview.body | contains("/code-review"))
          | select(.isResolved == false)] | length' <<<"$PAGE")))
        HAS_NEXT=$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' <<<"$PAGE")
        [ "$HAS_NEXT" = "true" ] || break
        CURSOR=$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor' <<<"$PAGE")
      done

  Require `UNRESOLVED -eq 0`.
- **(c) HEAD is unchanged since the review was submitted.** Race guard against a push that
  landed between step 8 (review POST) and this step. Re-fetch HEAD immediately before adding
  the label and compare to the review's `commit_id`:

      CURRENT_HEAD=$(gh pr view <N> --repo <owner>/<repo> --json headRefOid -q .headRefOid)
      # Apply label only if CURRENT_HEAD matches the review commit_id

If all three pass:

   gh pr edit <N> --add-label "claude/code-review:approved" --repo <owner>/<repo>

If any fails: do not add `:approved` and do not post additional comments. The review body has
already communicated any findings; a future invocation (new HEAD or late thread resolution)
will re-evaluate the gate.

Intentionally does NOT check threads opened by other reviewers (Copilot, human). That's the
PR author's merge-gate concern, not this reviewer's.

Do NOT attempt `event: "APPROVE"` on the review itself — GitHub rejects self-approval when
the review author and PR author authenticate as the same GitHub user (the common case for
solo-maintained repos where /code-review runs under the PR author's login). The label is the
approval signal; downstream consumers gate on it.

## 10. Termination checklist (STOP before returning to the caller)

Before terminating, explicitly confirm each of the following. If you cannot answer "yes" to an
applicable item, do not terminate — go back and complete it.

- [ ] **Eligibility gate (step 1) evaluated.** If the PR was ineligible (closed/draft/automated/trivial),
      you exited before step 1.5 and no labels were touched — skip the remaining items.
- [ ] **Path selected.** Either the fresh-review path (1.5 → 8) ran to completion, or the
      duplicate-skip path (1(d)) routed directly to step 9. One of these must be true.
- [ ] **Labels reconciled.** On the fresh-review path: `:in-progress` was removed and `:reviewed`
      was added in step 8.i (or only `:in-progress` was removed on early exit between 1.5 and 8.i).
      On the duplicate-skip path: labels were intentionally untouched.
- [ ] **Approval gate (step 9) evaluated.** This runs on BOTH the fresh-review and duplicate-skip
      paths. `:approved` was either added (all three conditions passed) or intentionally not added
      (at least one condition failed). Evaluation must have occurred — silently skipping step 9 is
      the primary failure mode this checklist guards against.

Only after all applicable items are confirmed may you return to the caller.
</custom>

<custom>
## Output Contract

Downstream skills — notably `/pr-resolve-comments` — depend on a stable output shape from
`/code-review`. Any change to this contract requires a coordinated update to the consumers
(see epic #6 and follow-up #21).

- **Review submission.** A single review per run, submitted via
  `gh api repos/:owner/:repo/pulls/:num/reviews -X POST` with `event: "COMMENT"`. Never
  `APPROVE` or `REQUEST_CHANGES` (see step 8b for the self-review rationale).

- **Body marker (primary discovery signal).** The review body's first line is the HTML
  comment `<!-- code-review-findings: N -->`, where `N` is the integer finding count (0 if
  none). Downstream tooling greps this marker before parsing; it must appear even in the
  no-issues case.

- **Findings heading + task list.** The body contains `## Findings (N)` with the same `N`
  as the marker, followed by a GitHub-flavoured-Markdown task list — one `- [ ]` per
  finding. Each item reads
  `- [ ] <short title> — see inline comment at <path>:<line>`
  for inline-anchored findings, or
  `- [ ] <short title> — <prose with full-SHA blob URL>`
  for cross-cutting findings that have no inline anchor. `/pr-resolve-comments` ticks the
  boxes as findings are resolved.

- **Inline comment schema.** Each `comments[]` entry in the review payload includes:
  - `path`: file path as shown in `gh pr diff`
  - `line`: new-file line number within a diff hunk
  - `side`: `"RIGHT"` for added/context lines, `"LEFT"` for deletions
  - `body`: prose; optionally followed by a fenced ` ```suggestion ` block with a
    mechanical replacement
  - Multi-line spans: add `start_line` + `start_side`
  - **File-level findings** use the lowest in-hunk new-file line of the target file
    (typically `line: 1, side: "RIGHT"` for newly added files) and prefix the body with
    `(file-level) ` so the reader sees the context immediately.
  - Do not use the deprecated `position` field.
  Every inline comment becomes a GitHub review thread, which `/pr-resolve-comments`
  discovers via the `reviewThreads` GraphQL field.

- **Footer.** The body ends with the two-line footer:

      🤖 Generated with [Claude Code](https://claude.ai/code) using /code-review

      <sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>

- **Labels.** The PR transitions `claude/code-review:in-progress` (set in 1.5) →
  `claude/code-review:reviewed` (set in 8.i) on successful submission. On early exit after
  1.5, only the in-progress label is removed. Additionally, `claude/code-review:approved`
  is applied in step 9 (approval gate) when all three conditions pass (no blocking findings,
  all /code-review-authored threads resolved, HEAD unchanged), and is removed in step 1.5 at
  the start of every fresh-review run since a new HEAD invalidates prior approval.
  Downstream consumers MAY gate merges on `:approved`.

- **`commit_id`.** Always set to the PR HEAD SHA at submission time, so consumers can
  correlate a review with the commit it covers.
</custom>

Examples of false positives, for steps 4 and 5:

- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter, typechecker, or compiler would catch (eg. missing or incorrect imports, type errors, broken tests, formatting issues, pedantic style issues like newlines). No need to run these build steps yourself -- it is safe to assume that they will be run separately as part of CI.
- General code quality issues (eg. lack of test coverage, general security issues, poor documentation), unless explicitly required in CLAUDE.md
- Issues that are called out in CLAUDE.md, but explicitly silenced in the code (eg. due to a lint ignore comment)
- Changes in functionality that are likely intentional or are directly related to the broader change
- Real issues, but on lines that the user did not modify in their pull request

Notes:

- Do not check build signal or attempt to build or typecheck the app. These will run separately, and are not relevant to your code review.
- Use `gh` to interact with Github (eg. to fetch a pull request, or to create inline comments), rather than web fetch
- Make a todo list first
- You must cite and link each bug (eg. if referring to a CLAUDE.md, you must link it)
- For your final comment, follow the following format precisely (assuming for this example that you found 3 issues):

---

### Code review

Found 3 issues:

1. <brief description of bug> (CLAUDE.md says "<...>")

<link to file and line with full sha1 + line range for context, note that you MUST provide the full sha and not use bash here, eg. https://github.com/anthropics/claude-code/blob/1d54823877c4de72b2316a64032a54afc404e619/README.md#L13-L17>

2. <brief description of bug> (some/other/CLAUDE.md says "<...>")

<link to file and line with full sha1 + line range for context>

3. <brief description of bug> (bug due to <file and code snippet>)

<link to file and line with full sha1 + line range for context>

🤖 Generated with [Claude Code](https://claude.ai/code) <custom>using /code-review</custom>

<sub>- If this code review was useful, please react with 👍. Otherwise, react with 👎.</sub>

---

- Or, if you found no issues:

---

### Code review

No issues found. Checked for bugs and CLAUDE.md compliance.

🤖 Generated with [Claude Code](https://claude.ai/code)

- When linking to code, follow the following format precisely, otherwise the Markdown preview won't render correctly: https://github.com/anthropics/claude-cli-internal/blob/c21d3c10bc8e898b7ac1a2d745bdc9bc4e423afe/package.json#L10-L15
  - Requires full git sha
  - You must provide the full sha. Commands like `https://github.com/owner/repo/blob/$(git rev-parse HEAD)/foo/bar` will not work, since your comment will be directly rendered in Markdown.
  - Repo name must match the repo you're code reviewing
  - # sign after the file name
  - Line range format is L[start]-L[end]
  - Provide at least 1 line of context before and after, centered on the line you are commenting about (eg. if you are commenting about lines 5-6, you should link to `L4-7`)
