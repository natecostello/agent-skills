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

   For duplicate-review detection (d): skip ONLY if there is already a review from you (identifiable by the "Generated with [Claude Code](https://claude.ai/code) using /code-review" footer in the review body) whose `commit_id` matches the current PR HEAD SHA. A stale review on an older SHA does not gate — re-review the new commits.

   Override: if the command arguments include `force` or `re-review` (in addition to the PR number), skip the duplicate-review gate entirely and proceed. The (a)/(b)/(c) gates still apply.
<custom>
1.5. Signal "review in progress" by labeling the PR with `claude/code-review:in-progress`, so other agents or humans monitoring the PR know a review is underway. Also pre-create the `claude/code-review:reviewed` label that step 8.i will apply on completion. Run:

     gh label create "claude/code-review:in-progress" --color 1f6feb --description "Claude Code review in progress" --force --repo <owner>/<repo> 2>/dev/null || true
     gh label create "claude/code-review:reviewed"    --color 0e8a16 --description "Claude Code review complete"    --force --repo <owner>/<repo> 2>/dev/null || true
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
6. Filter out any issues with a score less than 80. If there are no issues that meet this criteria, do not proceed.
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
      - `event`: "COMMENT" (never APPROVE or REQUEST_CHANGES unless the user explicitly asks)
      - `body`: the review summary (format below)
      - `comments`: array of inline comments, one per finding that anchors to a line the PR actually
        modifies

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

   e. Findings that do not live on a modified line (docs consistency about untouched files,
      architectural concerns, cross-cutting issues) cannot be inline — include them in the review
      `body` with a full-SHA blob URL as context, not in `comments[]`.

   f. No-issues case: still submit a review with `event: "COMMENT"`, a body that follows the template
      below with a closing line "No issues found. Checked for bugs and CLAUDE.md compliance.", and
      an empty or omitted `comments` array. This keeps the review footprint consistent.

   g. Review body format (Copilot style):
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

      Found N issues. See inline comments below.
      (Or: "No issues found. Checked for bugs and CLAUDE.md compliance.")

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
