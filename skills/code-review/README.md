# code-review

Independent code reviewer for GitHub pull requests. Runs parallel sub-agent reviewers
(CLAUDE.md compliance, bugs, git history, prior PR comments, code comments, docs), scores
findings for confidence, and posts a single GitHub review with inline comments anchored to
modified lines. See [`SKILL.md`](./SKILL.md) for the full workflow.

## Labels

- `claude/code-review:in-progress` — review running
- `claude/code-review:reviewed` — review posted at some HEAD
- `claude/code-review:approved` — no blocking findings on current HEAD AND every thread
  this reviewer opened is resolved AND HEAD unchanged since the review. Downstream merge
  gates (e.g. ralph `temp-ralph.txt` STEP 10) key off this label.

`:approved` is removed automatically at the start of every fresh-review run — a new HEAD
invalidates prior approval. If the new review lands clean, the label is re-applied in the
same invocation.

## Usage patterns

### One-off review (default)

Invoke in any Claude Code session:

```
/code-review <PR-number>
```

Runs the full review workflow, posts a GitHub review with inline findings, applies
`:reviewed`, and applies `:approved` if the gate passes. Exits.

If the author then pushes fix commits, re-invoke `/code-review <PR-number>` manually to
re-review the new HEAD and re-evaluate the gate. If the author only resolved threads
without pushing (HEAD unchanged), re-invocation hits the duplicate-review short-circuit and
re-evaluates the gate without posting a second review.

### Continuous multi-PR monitoring (e.g. against a ralph loop)

For environments where new PRs arrive continuously and should be reviewed without manual
intervention, run a `/loop` in a long-lived dedicated session (convention: session name
`code_reviewer`):

```
/loop 5m <
For each open PR in <owner>/<repo> whose labels do NOT include
  claude/code-review:reviewed or claude/code-review:in-progress:
    run /code-review <PR-number>
>
```

The outer loop discovers NEW PRs and invokes the skill once per PR. When the author pushes
fix commits, the loop's next tick picks up the new HEAD: `/code-review` re-reviews the new
SHA and re-evaluates the gate. Approval is granted automatically when the PR is clean.

The outer loop deliberately does NOT re-invoke on already-reviewed PRs to catch
re-approvals after late thread resolution. The author-side workflow (`/pr-resolve-comments`
or similar) can invoke `/code-review <PR>` directly after resolving threads to nudge the
gate — the skill's softened duplicate-review short-circuit evaluates the gate without
posting a second review.

### Force re-review

To bypass the duplicate-review short-circuit (e.g. the prior review had a bug and you want
to redo it from scratch):

```
/code-review <PR-number> force
```

or

```
/code-review <PR-number> re-review
```

## Overrides and scope

- **GitHub approval event.** The skill does NOT post `event: "APPROVE"` on GitHub reviews.
  GitHub rejects self-approval when the reviewer and author auth as the same GitHub user,
  which is the common case in solo-maintained repos. The `claude/code-review:approved`
  label is the approval signal.
- **Other reviewers' threads.** The approval gate only considers threads opened by this
  skill (identified by the `/code-review` footer in the enclosing review body). Threads
  opened by Copilot, human reviewers, or other bots are the PR author's merge-gate concern
  and do not block `:approved`.
