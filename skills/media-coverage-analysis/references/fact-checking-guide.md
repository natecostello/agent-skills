# Fact-Checking Guide

This document describes how to identify claims, evaluate evidence, and assign verdicts for
the fact-check section of the report.

## 1. Identifying Claims

Look for assertions that meet ALL of these criteria:

- **Widely repeated**: The claim appeared in multiple outlets, not just one
- **Consequential**: The claim shaped how readers understood the event
- **Verifiable**: There exists (or should exist) evidence that can confirm or contradict it
- **Contested**: At least some outlets or sources challenged the claim

Good fact-check subjects are often official claims that were initially taken at face value
and later contradicted by evidence. Government press releases, official statements, and
sworn testimony are prime candidates because they carry institutional authority and their
inaccuracy is especially newsworthy.

Aim for 4–8 claims per report. Too few and the section feels thin; too many and it becomes
a laundry list.

## 2. Evaluating Evidence

For each claim, gather:

- **Primary sources**: Court filings, official press releases, video evidence, physical
  evidence, sworn testimony, government databases
- **Secondary sources**: Reporting from outlets that did original investigation (not wire
  rewrites)
- **Witness accounts**: Named witnesses, on-record interviews
- **Expert analysis**: Legal experts, policy analysts, subject-matter specialists

Hierarchy of evidence (strongest to weakest):
1. Physical evidence (bullet holes, video, forensic results)
2. Multiple independent witnesses with consistent accounts
3. **Court filings and judicial findings** — these are exceptionally strong because judges
   evaluate evidence under legal standards. A preliminary injunction requires a finding that
   the plaintiff is "likely to succeed on the merits." A judicial opinion stating "the
   government's claim is not supported by the record" is a factual determination, not editorial
   opinion. Always cite the specific case number, judge name, and ruling date.
4. Government records and databases
5. Single-source witness accounts
6. Expert opinion
7. Unnamed/anonymous sources

**MANDATORY: Search for judicial findings before finalizing verdicts.** For any claim involving
government action or policy, check whether courts have ruled on the claim's validity. A judge's
finding supersedes competing media narratives because it reflects adversarial testing of evidence.
If a court has issued a ruling relevant to a claim under review, that ruling MUST be cited in the
evidence section — regardless of whether media outlets reported on it. See the skill workflow
Step 2 for the full primary-source research protocol.

## 3. Assigning Verdicts

Use these verdict categories:

| Verdict | When to Use | Tag |
|---------|------------|-----|
| **FALSE** | Evidence clearly and directly contradicts the claim | [FALSE] |
| **MISLEADING** | Claim contains a kernel of truth but omits critical context that changes the meaning | [MISLEADING] |
| **UNSUBSTANTIATED** | No credible evidence supports the claim, but also no evidence directly disproves it | [UNSUBSTANTIATED] |
| **EVIDENCE CONTRADICTS** | Multiple lines of evidence are inconsistent with the claim, but not a clean falsification | [EVIDENCE CONTRADICTS] |
| **TRUE** | Evidence clearly supports the claim | [TRUE] |
| **MOSTLY TRUE** | Claim is substantially accurate but contains minor errors or omissions | [MOSTLY TRUE] |
| **DISPUTED** | Credible evidence exists on both sides; reasonable people disagree | [DISPUTED] |

**No emoji.** Use the bracketed text tags above, not emoji symbols. The PDF is a first-class
output and emoji do not render correctly in ReportLab.

Be precise about which verdict applies. "FALSE" means the evidence directly contradicts the
claim — don't use it when "MISLEADING" or "EVIDENCE CONTRADICTS" is more accurate. Overstating
verdicts undermines the report's credibility.

## 4. Claim Extraction (Before Writing Any Verdict)

**This step is mandatory and must be completed before writing any fact-check entry.**

For each claim under review, extract every discrete factual assertion made about the event
from every article in the dataset that discusses it — regardless of outlet political orientation.
Record these as a flat list of assertions with article IDs.

Example: If reviewing a claim about a confrontation, the extraction might yield:
- "Subject kicked the vehicle, breaking the tail light" (A28b, A34b, A39a)
- "Agents tackled the subject" (A11b, A42a)
- "Subject suffered a broken rib" (A11b, A37a)
- "Subject yelled profanity at agents" (A28b, A34b, A37b)
- "Subject spat toward agents" (A28b, A39a)

This prevents inheriting the omissions of whichever cluster of outlets you happen to
synthesize from first. The fact-check for a [MISLEADING] verdict should reflect ALL
assertions, not just the ones surfaced by the sources you instinctively trust more.

### Adversarial completeness check

After extraction, explicitly answer these two questions:

1. **What does the right-leaning coverage include that the left-leaning coverage omits?**
2. **What does the left-leaning coverage include that the right-leaning coverage omits?**

If either answer is non-trivial, the fact-check MUST address both omissions. A fact-check
that only calls out one side's omission while silently reproducing the other side's omission
is itself misleading — and undermines the report's credibility as a neutral analysis.

### Primary source limitation flag

When a fact-check hinges on video, audio, or other non-textual evidence that cannot be
directly reviewed (because the analyst is working from textual descriptions, not viewing
the media directly):

1. Reconcile descriptions of the evidence from at least 3 outlets across different political
   orientations before writing the verdict
2. Note any details that appear in some outlets' descriptions but not others — these are
   the most likely sites of selective framing
3. If competing descriptions are irreconcilable without viewing the primary source, flag
   this explicitly in the evidence section

## 5. Structuring Each Claim

Each fact-check entry should follow this structure:

### Claim: "[The claim as stated]"

**As stated:** How the claim was articulated, by whom, in what outlets. Include direct quotes
where possible. Cite specific article IDs.

**What the evidence shows:** Present the evidence that bears on the claim. Lead with the
strongest evidence. Be specific — "video evidence" is weaker than "city surveillance video
from the 600 block of 24th Ave N, timestamped 6:47 PM." Include assertions from across
the political spectrum identified during claim extraction (Section 4).

**Verdict: [TAG] [VERDICT]** — One-sentence summary of why this verdict applies. Use bracketed
text tags (e.g., `[FALSE]`, `[MISLEADING]`) — no emoji.

**Sources:** List the article IDs that contain the evidence, as clickable links.

## 6. The Summary Table

After all individual fact-checks, include a summary table:

| # | Claim | Verdict | Key Evidence |
|---|-------|---------|-------------|
| 1 | [Short version] | [Symbol + word] | [One-line evidence summary] |

This gives readers a quick overview before diving into details.

## 7. Principles

- **Cite article IDs** from the dataset, not just outlet names. This lets readers click through
  to the actual source articles and cross-reference with the sentiment data.
- **Don't editorialize.** The evidence should speak for itself. "Verdict: ❌ FALSE — no weapon
  found" is better than "Verdict: ❌ FALSE — this was an outrageous lie."
- **Include claims that turn out TRUE.** If a contested claim is actually supported by evidence,
  say so. This demonstrates the analysis is evenhanded, not advocacy.
- **Distinguish between the claim and the claimer.** A claim can be false even if the person
  who made it believed it. Focus on the claim's accuracy, not the claimer's intent.
- **Acknowledge uncertainty.** If the evidence is incomplete or ambiguous, say so. "DISPUTED"
  is a legitimate verdict.
