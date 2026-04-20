---
name: pr-submit
description: >-
  Submit a pull request with automated Copilot review and comment resolution.
  Use when the user says "submit PR", "create PR", "open PR", "submit pull
  request", "push and create PR", or wants to go through the full PR submission
  workflow including Copilot review. Also trigger when the user says
  "/pr-submit". This skill handles the entire lifecycle — from pre-flight
  checks through review monitoring to final status report.
argument-hint: [optional PR title, e.g. "Add user authentication"]
license: MIT
metadata:
  author: natecostello
  version: "0.1"
---

# Submit Pull Request

End-to-end PR submission workflow: pre-flight checks, PR creation, Copilot review request, review monitoring, comment resolution, description update, and final status summary.

## Workflow

### Step 0: Pre-flight — Copilot Instructions Check

Before anything else, verify that `.github/copilot-instructions.md` exists in the repo:

```bash
git rev-parse --show-toplevel
ls .github/copilot-instructions.md 2>/dev/null
```

**If the file does NOT exist:**
- Warn the user: "This repo doesn't have Copilot review instructions (`.github/copilot-instructions.md`). Copilot reviews will be less effective without project-specific context."
- Suggest: "Run `/copilot-init` first to set that up, then come back to `/pr-submit`."
- **Stop here.** Do not proceed with PR submission until the user either sets up Copilot instructions or explicitly says to continue without them.

**If the file exists:** proceed to Step 1.

### Step 1: Prepare and Submit the PR

1. **Check branch state** — verify there are commits ahead of the base branch and no uncommitted changes:
   ```bash
   git status
   git log --oneline origin/main..HEAD  # adjust base branch as needed
   ```

2. **Push the branch** if it hasn't been pushed or is behind remote:
   ```bash
   git push -u origin HEAD
   ```

3. **Create the PR** using `gh pr create`. If `$ARGUMENTS` was provided, use it as the PR title. Otherwise, draft a title from the commit history.

   Build the PR body with:
   - A `## Summary` section (2-4 bullet points covering what changed and why)
   - A `## Test plan` section (checklist of verification steps — unchecked items signal remaining work)
   - Attribution footer

   ```bash
   gh pr create --title "<title>" --body "$(cat <<'EOF'
   ## Summary
   - <bullet points>

   ## Test plan
   - [ ] <verification step>
   - [ ] <verification step>

   🤖 Generated with [Claude Code](https://claude.ai/code)
   EOF
   )"
   ```

   If the PR already exists for this branch, skip creation and use the existing PR number.

4. **Capture the PR number** from the output for subsequent steps.

### Step 2: Request Copilot Review

Request GitHub Copilot as a reviewer on the PR:

```bash
gh pr edit {pr_number} --add-reviewer "@copilot"
```

Tell the user: "PR #{pr_number} submitted. Copilot review requested — monitoring for completion."

### Step 3: Resolve Review Comments

Invoke the `/pr-resolve-comments` workflow against the PR:

```
/pr-resolve-comments {pr_number}
```

This handles the full lifecycle: waiting for the Copilot review to land, fetching and resolving all unresolved threads, pushing fixes, and re-checking for new review rounds (up to 3 iterations).

If `/pr-resolve-comments` reports skipped threads that need human review, inform the user which threads remain and why.

### Step 4: Complete Test Plan and Update PR Description

After resolving comments, verify and complete all test plan items:

1. **Re-read the PR body:**
   ```bash
   gh pr view {pr_number} --json body --jq '.body'
   ```

2. **Classify each unchecked item.** Parse every `- [ ]` line and classify it as:
   - **Verifiable** — you can run a command or test to confirm it (e.g., "ruff check passes", "pytest passes")
   - **DEFERRED** — items explicitly marked `~~DEFERRED~~` or tagged with a `#issue_number` from `/pr-resolve-comments`. These are NOT blocking — they represent follow-up work tracked in GitHub issues.
   - **Human-required** — requires manual action you can't perform (e.g., UI testing, credential access)

3. **Execute every verifiable test plan item.** For each verifiable `- [ ]` item, actively run the verification command or test described. Do not skip items that you are capable of verifying.

4. **Handle DEFERRED items.** For any `- [ ]` item that was deferred during comment resolution:
   - If a GitHub issue was already created by `/pr-resolve-comments`, note its number
   - If no issue exists yet, create one:
     ```bash
     gh issue create --title "<short description>" --body "$(cat <<'EOF'
     ## Context
     Deferred from PR #{pr_number} test plan.

     ## Task
     {description of the deferred work}

     ---
     *Created from PR #{pr_number} test plan.*
     EOF
     )"
     ```
   - Remove the DEFERRED item from the test plan checkboxes and add it to a `## Deferred` section at the bottom (before the attribution footer):
     ```markdown
     ## Deferred
     - {description} — #{issue_number}
     ```

5. **Update the summary** if the code changed meaningfully during comment resolution. Add or update bullet points describing what was adjusted.

6. **Check off each item** that you verified in step 3. For any item left unchecked, note why it requires human verification.

7. **Apply the update:**
   ```bash
   gh pr edit {pr_number} --body "$(cat <<'EOF'
   <updated body>
   EOF
   )"
   ```

### Step 5: Final Status Summary

Run the `/pr-status` workflow against the PR to generate a complete status report. This gives the user a clear picture of:

- Merge readiness (mergeable, review decision, branch status)
- CI check results
- Remaining unresolved review threads (if any)
- Task item completion
- Blocking issues and suggested next steps

Present the status report to the user as the final output.

### Error Handling

- **PR creation fails:** Check if a PR already exists for this branch (`gh pr list --head {branch}`). If so, use the existing PR.
- **Copilot review times out:** Proceed with status report and note that Copilot review hasn't arrived yet. Suggest the user check back later or re-request review.
- **Comment resolution fails:** Report which comments couldn't be resolved and why. The PR is still submitted — resolution is best-effort.
- **Push fails:** Check for upstream changes, pull and retry once. If still failing, report the error.
