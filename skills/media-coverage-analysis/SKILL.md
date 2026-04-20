---
name: media-coverage-analysis
description: >-
  Generate comprehensive media coverage and sentiment analysis reports for any news topic.
  Produces a defensible, data-driven report with political spectrum analysis, article-level
  sentiment scoring, government narrative alignment tracking, fact-checking, and visualizations.
  Outputs both Markdown and PDF with clickable source links. Use this skill whenever the user
  asks to analyze media coverage, sentiment, bias, or narrative framing around any news event
  or topic — even if they don't use the exact phrase "media coverage analysis." Also trigger
  when users ask for political spectrum analysis, media bias reports, or fact-check summaries.
  MANDATORY TRIGGERS: media coverage, sentiment analysis, media bias, narrative framing,
  political spectrum, fact-check, how media covered, news analysis.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
---

# Media Coverage & Sentiment Analysis

This skill produces a complete, defensible media coverage analysis report for any news topic.
Every data point on every chart traces back to a specific article scored on a transparent rubric,
so the reader can disagree with any individual score and see exactly how it was derived.

## Setup

The chart and PDF generator scripts require a Python environment with `matplotlib`, `numpy`,
and `reportlab`. Bootstrap once with [`uv`](https://docs.astral.sh/uv/):

```bash
cd skills/media-coverage-analysis
uv venv
uv pip install -r requirements.txt
```

Run the scripts through the venv interpreter (adapt paths if you copy the templates into a
working directory):

```bash
cd skills/media-coverage-analysis
.venv/bin/python scripts/generate_charts_template.py
.venv/bin/python scripts/generate_shift_chart_template.py
.venv/bin/python scripts/generate_pdf_template.py
```

The NLP experimentation deps referenced in "TODO: Future Exploration" below (`torch`,
`transformers`, `sentence-transformers`, `scikit-learn`) are **not** in `requirements.txt` —
install them on demand if you pursue that work.

## Why This Design

Media analysis is inherently subjective. The skill addresses this by making every judgment
explicit: each article gets four independent subscores on named criteria. Political orientation
uses AllSides/Ad Fontes baselines with documented adjustments. Fact-check verdicts cite specific
evidence. Government narrative alignment is a mathematical transform of sentiment, not a separate
subjective judgment. This makes the report useful even to readers who disagree with individual
scores — they can see where to push back.

## Hard Rules

These apply to every report, no exceptions:

1. **PDF is a first-class citizen.** The PDF must look as good as the Markdown. If a feature
   (emoji, Unicode symbol, etc.) does not render correctly in ReportLab, do not use it. Use
   text-only verdicts (e.g., "[FALSE]", "[MISLEADING]") rather than emoji symbols.
2. **Section structure is required.** The numbered sections and appendices defined in
   `references/report-structure.md` are the minimum required structure. All 12 sections must
   appear in the specified order. Sections may be expanded but never removed or reordered.
3. **Multiple articles per outlet are required for shift analysis.** The shift over time within
   outlets is a core analytical finding. For every outlet in the dataset, actively search for
   2+ articles across different time periods. A dataset with mostly single-article outlets
   produces flat, uninteresting shift arrows and misses the story. Target 3+ articles for
   major outlets (NPR, Fox News, CNN, etc.).
4. **Searches must be exhaustive.** For every outlet in the search matrix, run at least 2–3
   different query formulations (different keywords, date ranges, topic angles). A single
   failed search does not mean absence of coverage — it means the search was insufficient.
   Only declare "no coverage found" after 3+ distinct search attempts with varied terms.
5. **Government social media is part of the timeline.** Presidential tweets/truths, cabinet
   members' social media posts, and official government social media are events that belong
   in the Section 2 timeline. A presidential truth posted before the topical event (e.g.,
   foreshadowing rhetoric) is timeline-relevant even though it predates the event. These do
   NOT appear in the sentiment analysis (Sections 4–5), which is limited to published articles
   after the topical event date.
6. **No overlapping text.** Timeline charts (Sections 2 and 5) must implement collision
   avoidance for text boxes. Labels must be size-aware and repositioned or staggered to avoid
   obscuring each other. See `references/chart-specifications.md` for implementation.
7. **Standard category ordering.** Wherever political categories appear in charts or narrative
   sections, use the standard order defined in `references/chart-specifications.md`.
8. **Colors and markers are standardized.** The color palette and marker shapes in
   `references/chart-specifications.md` are canonical. Every chart must use them consistently.
   Do not invent ad-hoc colors.
9. **Primary-source legal and policy research is required.** For any topic involving government
   action, enforcement, or policy disputes, search for court filings, judicial rulings, executive
   orders, agency directives, and internal policy memos. These are the strongest evidence
   available and must be cited with specific case numbers, judge names, and ruling dates.
   Media descriptions of legal developments are secondary — the filings themselves are primary.
   See Step 2 for the detailed research protocol.

## Workflow

Follow these steps in order. The reference files contain the detailed specifications; this
section provides the high-level flow and the reasoning behind each step.

### Step 1: Understand the Topic

Before any research, establish four things:

- **The core event**: What happened, when, who was involved
- **The topic window**: Date range for coverage (typically the event date through the present)
- **The key tension**: What makes coverage diverge? (competing accounts, political fault lines, evolving evidence)
- **The official/government narrative**: If one exists, this becomes the alignment baseline

Write these down — they inform every subsequent step. The "topical event date" is especially
important because the alignment chart must not include data points before it.

### Step 2: Research Systematically

Read `references/scoring-rubric.md` Section 2 for the outlet spectrum before starting research.

Search for 40–80 articles from 20+ outlets spanning far-left through far-right, plus
libertarian, local, and government/official sources. Use outlet-specific searches
(e.g., `site:foxnews.com [topic]`) and general date-filtered searches. **Prioritize
depth over breadth:** 3 articles from one outlet showing a shift over time are more
valuable than 3 articles from 3 outlets showing a single snapshot each.

**MANDATORY: Search every political category explicitly.** Do not assume absence — verify it.
Run dedicated searches for outlets in each of these categories. If an outlet has no coverage,
record that as a finding (absence is data). Search at minimum:

| Category | Minimum Outlets to Search | Search Method |
|----------|--------------------------|---------------|
| Far Left | The Intercept, Common Dreams, Jacobin | `site:` searches + general |
| Left | Salon, Daily Beast, Mother Jones, HuffPost, Raw Story | `site:` searches |
| Center-Left | NPR, PBS, CNN, WaPo, MSNBC | `site:` searches |
| Center | AP, Reuters, ABC, CBS, NBC | `site:` searches |
| Center-Right | WSJ, NY Post, Fox local affiliates | `site:` searches |
| Right | Fox News, Washington Times, Washington Examiner, National Review | `site:` searches |
| Far Right | Daily Wire, Breitbart, Newsmax, OANN, Daily Caller, Townhall, The Federalist, Epoch Times, RedState, The Blaze | **Must search each individually** |
| Libertarian | Reason, Cato Institute | `site:` searches |
| Government | DHS, DOJ, White House, relevant agencies | `site:` searches |
| Local | 3+ outlets local to the event | general + `site:` searches |

The far-right category requires individual `site:` searches for each outlet because these
outlets often cover initial government narratives but not subsequent contradictions — and
documenting that asymmetry is a core analytical finding. A general search like
`"[topic]" breitbart OR newsmax` will miss articles that don't use the exact search terms.

**MANDATORY: Search each time period separately.** For stories that evolve over time, run
separate searches for each major phase (e.g., initial incident, charges/legal developments,
evidence release). Right-leaning outlets frequently cover Phase 1 (government narrative
intact) but not Phase 2 (narrative contradicted). Left-leaning outlets may do the reverse.
Searching only the most recent period will systematically miss early coverage from outlets
that later went silent, and vice versa.

For each article, record: outlet, date, headline, URL, and enough content to score it. Aim
for temporal coverage too — articles from both the initial reporting period and later
developments, because the shift over time is where the interesting story lives.

The research phase is the most time-consuming step and the one most likely to need multiple
search rounds. Be thorough — a thin dataset produces unconvincing charts.

**MANDATORY: Search government social media.** Search for presidential tweets/truths,
cabinet-level social media posts, and official agency social media related to the topic.
These are timeline events (Section 2) and provide context for the narrative environment
even when they predate the topical event. Example: a presidential truth posted the day
before an operation begins is a timeline event.

**MANDATORY: Run multiple query formulations per outlet.** For each outlet in the search
matrix, use at least 2–3 different search queries (different keywords, name variants,
topic angles). A single `site:motherjones.com "renee good"` returning zero results does
NOT establish absence — try `site:motherjones.com ICE shooting Minneapolis`, try without
`site:` using `motherjones "ice shooting"`, etc. Only declare "no coverage found" after
3+ genuinely distinct attempts. Coverage absence from outlets like Mother Jones, ProPublica,
BBC, Guardian, NY Post, or WSJ for a major national story is improbable and warrants
extra search effort before accepting.

**After research, create a coverage gap audit:** List every outlet searched, the specific
queries used, and whether coverage was found. This becomes part of the Methodology section
and prevents silent omissions from weakening the analysis. The audit should document the
search effort, not just the result.

**MANDATORY: Search for primary-source legal and policy documents.** For any topic involving
government action, enforcement, civil liberties, or policy disputes, media articles alone are
insufficient. The strongest evidence for the timeline, fact-checks, and narrative analysis
comes from primary legal and policy sources. Search for ALL of the following that apply:

| Source Type | What to Search For | Where to Search |
|------------|-------------------|-----------------|
| **Court filings** | Lawsuits, complaints, motions for TRO/PI, amicus briefs | PACER, CourtListener, `site:courtlistener.com`, news reports citing case numbers |
| **Judicial rulings** | Temporary restraining orders, preliminary injunctions, opinions | Same as above, plus `site:law.justia.com`, legal news outlets |
| **Executive orders** | Presidential EOs, national security memoranda, presidential directives | `site:whitehouse.gov`, Federal Register, media coverage |
| **Agency directives** | DHS/DOJ/ICE policy memos, operational guidance, internal directives | Agency websites, FOIA releases, investigative reporting |
| **AG memoranda** | Attorney General memos to federal prosecutors, policy guidance | `site:justice.gov`, legal news |
| **State legal actions** | State AG lawsuits, state court filings, governor executive orders | State AG websites, local legal news |
| **Legislative actions** | Bills, committee hearings, floor statements, testimony transcripts | `site:congress.gov`, C-SPAN, committee websites |

**Search strategy for legal sources:**
1. Start with case names mentioned in media coverage — articles often reference lawsuits
   by name (e.g., "ACLU v. DHS") without providing full case details
2. Search for the full case number, presiding judge, and specific rulings
3. Search for related cases — one lawsuit often spawns related filings in other jurisdictions
4. Search for the specific legal theories cited (e.g., First Amendment, APA violations,
   42 U.S.C. § 1983) to find additional cases
5. Check legal news outlets (Law360, Reuters Legal, SCOTUSblog, Lawfare) for analysis

**What to record for each primary source:**
- Full case name and number (e.g., *LA Press Club v. Noem*, No. 2:25-cv-01494)
- Presiding judge
- Date of filing and date of ruling (if applicable)
- Specific holding or key language from the ruling
- Which media outlets reported on it and which did not (this is an analytical finding)

**Why this matters:** Court filings and judicial rulings are the strongest possible evidence
for fact-checks. A judge's finding that "X is not supported by the evidence" carries more
weight than any number of media articles arguing the same point. When a judge issues a
preliminary injunction, they have made a legal determination that the plaintiff is likely
to succeed on the merits — this is a factual finding, not editorial opinion. Legal primary
sources also reveal asymmetric coverage patterns: outlets that covered the initial government
claim but not the subsequent judicial rejection of that claim are exhibiting a documentable
information gap.

These primary sources should be integrated into:
- **Section 2 (Timeline):** Court filings, rulings, and executive orders are timeline events
- **Section 10 (Fact-Checks):** Judicial findings are top-tier evidence for verdicts
- **Section 3 (Narrative Analysis):** Which outlets covered legal developments and which didn't
- **Section 9 (Methodology):** Document the primary sources consulted

### Step 3: Score Each Article

**Read `references/scoring-rubric.md` before scoring any articles.** This is the most critical
step for consistency and defensibility.

The rubric has four criteria, each scored –0.25 to +0.25:
1. Subject description (how the subject is named/characterized)
2. Account primacy (whose version leads the article)
3. Emotional register (the article's affective tone)
4. Immigration/identity status foregrounding (for topics where this applies; otherwise substitute
   an equivalent framing criterion relevant to the topic)

Score what you observe in the text, not what you infer about intent. When uncertain, score
toward 0. Document the breakdown as `"+.25/+.20/+.15/+.10"`.

### Step 4: Identify and Fact-Check Claims

**Read `references/fact-checking-guide.md`** before writing this section.

Identify 4–8 key assertions made in coverage — especially claims from official sources that
were widely repeated and later challenged by evidence. For each claim, document: how it was
stated, by whom, what the evidence shows, a verdict, and article IDs as citations.

### Step 5: Build the Article Dataset

Create `article_data.py` in the working directory. This single file is the source of truth for
all charts and both appendices. Read `references/chart-specifications.md` Section 1 for the
exact data structure.

### Step 6: Generate Charts

**Read `references/chart-specifications.md`** for full specs. There are 6 charts:

1. **Timeline** — key events with color-coded markers
2. **Sentiment Scatter** — outlet-level static positioning
3. **Article-Level Shift** — every article as a recency-encoded point with chronological arrows
4. **Timeline + Alignment** — events above, government narrative alignment traces below
5. **Coverage Volume** — pie chart by source type
6. **Framing** — bar chart of narrative emphasis by political category

Adapt the template scripts in `scripts/` for the specific topic. The chart specs contain the
exact color palette, marker shapes, axis labels, and computation methods.

### Step 7: Assemble the Report

**Read `references/report-structure.md`** for the exact section ordering. The report includes:

- Executive Summary
- Timeline of Key Events (chart + table)
- Sentiment & Narrative Analysis (by political category)
- Sentiment Map & Shift Over Time (article-level chart)
- Timeline & Government Narrative Alignment (combined chart)
- Coverage Volume
- Narrative Framing
- Public Sentiment Indicators
- Methodology Note
- Fact-Check Section (claims + summary table)
- Appendix A: Scoring Rubric & All Articles (with links)
- Appendix B: Government Narrative Alignment Basis Data (with links)

Output both Markdown (.md) and PDF formats. The PDF must have clickable links throughout.

### Step 8: Verify

Read every page of the generated PDF. Check that:
- All charts render and are readable
- Tables don't overflow margins
- Links are blue and present in appendices and fact-check sources
- Article counts match between the dataset, charts, and appendix
- Fact-check verdicts match the summary table
- **No emoji or broken Unicode characters anywhere** — look for black squares, question marks,
  or tofu (□) that indicate failed rendering
- **Pie chart is perfectly circular**, not oblong
- **Timeline text boxes do not overlap** — all labels must be readable
- **Multiple articles per outlet** — verify the shift chart shows arrows for major outlets,
  indicating temporal coverage depth (not just single snapshots)
- **All 12 sections present** in the correct order

## Key Formulas

**Government Narrative Alignment:**
```
alignment = (1 - sentiment) / 2
```
Maps sentiment [–1, +1] to alignment [0, 1]. The "government narrative" is whatever the official
institutional position is — in many stories this means hostile-to-subject = high alignment.

**Alignment Trace (latest-per-outlet):** At each date, the group average uses only each
outlet's most recent article. When an outlet publishes again, the old score drops out.
One point per unique date per category. This means the trace responds to editorial shifts
rather than being dragged by early coverage.

**Recency Encoding (shift chart):**
```
alpha = 0.20 + 0.80 * (days_since_earliest / total_days)
size  = 50  + 130  * (days_since_earliest / total_days)
```

## TODO: Future Exploration

- **NLP-based sentiment scoring (Sections 4A/5A):** Explore automated sentiment analysis as
  a complement to the manual rubric. Initial testing with zero-shot NLI (BART-MNLI) on headlines
  showed r=0.066 correlation with manual scores — the model confuses lexical violence with
  editorial hostility. SBERT embedding alignment showed r=0.044 — topical similarity dominates
  stance signal. Three improvements to try:
  1. **Scrape article ledes** (first 500 words) instead of headline-only input
  2. **Multi-axis NLI hypotheses** mirroring the 4 rubric criteria (subject description, account
     primacy, emotional register, status foregrounding) instead of a single sympathetic/hostile
     dimension
  3. **Contrastive SBERT** measuring difference between similarity to government-narrative and
     counter-narrative reference texts, canceling out shared topical vocabulary
  - Venv with torch/transformers/sentence-transformers is at `.venv/` in the skill directory
  - See the Renee Good report working directory for the initial `compute_nlp_sentiment.py` script
    and comparison charts

## Reference Files

Read these at the points indicated in the workflow:

| File | When to Read | Contents |
|------|-------------|----------|
| `references/scoring-rubric.md` | Before Step 3 | 4-criterion rubric, political orientation method, calibration |
| `references/fact-checking-guide.md` | Before Step 4 | Claim identification, evidence evaluation, verdict assignment |
| `references/report-structure.md` | Before Step 7 | Exact sections, ordering, formatting for Markdown and PDF |
| `references/chart-specifications.md` | Before Steps 5–6 | Data structures, chart specs, colors, alignment computation |
