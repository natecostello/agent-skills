# Report Structure

This document defines the exact section ordering, content expectations, and formatting
for both the Markdown and PDF versions of the report.

## Report Title and Header

```markdown
# Media Coverage & Sentiment Analysis Report

## [Topic Title]

**Report Date:** [Date] | **Topic Window:** [Start] – [End]
```

## Section Order — Required Minimum Structure

The following 12 sections and 2 appendices are the **required minimum**. They must appear in
this exact order and with these exact numbering/titles. Sections may be expanded with
additional subsections but never removed, renamed, or reordered.

### 1. Executive Summary

2–3 paragraphs covering:
- What happened (the core event)
- Why it matters for media analysis (the divergence, the shift, the pattern)
- The key finding (what the data shows about how coverage evolved)

Keep it tight. The reader should understand the story and the report's value in under 60 seconds.

### 2. Timeline of Key Events

- Embed `chart_timeline.png`
- Follow with a Markdown table: Date | Event
- Include 8–15 key events spanning the topic window
- Events should include: the triggering event, government responses, evidence emergence,
  media inflection points, legal developments (court filings, judicial rulings, executive
  orders, agency directives — with case numbers and judge names where applicable)
- **Include government social media:** Presidential tweets/truths, cabinet-level social media
  posts, and official government rhetoric that shaped the narrative environment — even if
  they predate the topical event (e.g., inflammatory rhetoric posted the day before an
  operation begins). These provide context for how coverage was primed.
- Note: Government social media appears in the timeline (Section 2) but does NOT appear in
  the sentiment analysis (Sections 4–5), which is limited to published articles after the
  topical event date.

### 3. Sentiment & Sentimental Narrative

Analysis by political category. Use these subsections:

- **The Right / Conservative Narrative** — initial framing, far-right vs. mainstream-right
  divergence, shifts over time
- **The Left / Progressive Narrative** — initial framing, consistency or evolution
- **The Center / Mainstream Narrative** — initial framing, how it shifted as evidence emerged
- **The Libertarian Narrative** — framing through the lens of government overreach / civil
  liberties (if applicable)
- **The Localist / Regional Narrative** — local outlets' unique perspective (if applicable)

For each category, describe: the initial framing, the sentimental register (what emotion the
article evokes), specific outlets and their approaches, and any shifts over time. Use specific
article examples and quote headlines.

### 4. Sentiment Map & Shift Over Time

- Embed `chart_sentiment_shift.png`
- Explain the chart: axes, what points represent, what size/opacity encode, what arrows mean
- Describe marker shapes and colors
- List 4–6 key observations from the chart
- Reference Appendix A for the full article list

### 5. Timeline & Alignment with Government Narrative

- Embed `chart_combined_timeline_shift.png`
- Explain the methodology: latest-per-outlet averaging, one point per date per category
- Note the alignment formula: (1 − sentiment) / 2
- Highlight key drops or sustained alignment
- Reference Appendix B for per-article scores

### 6. Coverage Volume by Source Type

- Embed `chart_coverage_volume.png`
- Brief description of the distribution

### 7. Narrative Framing by Political Category

- Embed `chart_framing.png`
- Describe what the framing dimensions measure and key differences between categories
- **Standard category order (left-to-right on x-axis):** Far Left, Left, Center-Left, Center,
  Center-Right, Right, Far Right, Libertarian. Libertarian appears last as a cross-spectrum
  outlier. This order is fixed across all reports for consistency.

### 8. Public Sentiment Indicators

Bullet points of available public opinion data:
- Polls (with source and date)
- Social media indicators
- Protest/public action data
- Celebrity/cultural involvement
- Any other public sentiment signals

This section uses whatever data is available; it's inherently less structured than the
article-level analysis.

### 9. Methodology Note

Brief paragraph covering:
- Report compilation date
- Number of outlets and articles
- Source of political-leaning baselines
- Nature of the scoring (qualitative with explicit rubric, not algorithmic)
- Primary legal/policy sources consulted (court filings, judicial rulings, executive orders,
  agency directives — with case counts and specific case names)
- Any caveats

### 10. Fact-Check Section

Follow the structure in `fact-checking-guide.md`:
- Section header: "Fact-Check: Key Claims in Media Coverage"
- Introductory paragraph explaining the purpose
- 4–8 individual claim entries (each with Claim → As stated → Evidence → Verdict → Sources)
- Sources should use article IDs with clickable links
- Summary table at the end

### 11. Appendix A: Sentiment Scoring Rubric & Source Articles

- Scoring rubric (the 4-criterion table from `scoring-rubric.md`)
- Full article table with columns: ID | Date | Outlet | x (pol) | y (sent) | Scores | Headline | Link
- Sorted by political orientation (left to right), then by date
- Headlines should be clickable links to the source URL
- Every article in the dataset must appear here

### 12. Appendix B: Government Narrative Alignment — Basis Data

- Explanation of the alignment formula and methodology
- Interpretation table (sentiment → alignment → interpretation)
- Full article table with columns: ID | Date | Outlet | Category | Sent. | Align.
- Article IDs should be clickable links
- Sorted by date
- Only includes articles on or after the topical event date
- Government/official sources excluded (they define the narrative)

## PDF-Specific Requirements

**The PDF is a first-class output.** It is not a secondary artifact of the Markdown — it must
be independently complete, professional, and correctly formatted. Every feature in the report
must render correctly in the PDF. If a feature does not render in ReportLab (e.g., emoji
characters), **do not use it** — find a text-only alternative. Specifically:

- **No emoji in any output.** Use text labels like `[FALSE]`, `[MISLEADING]`, `[TRUE]` instead
  of `❌`, `⚠️`, `✅`. This applies to both the Markdown and the PDF to keep them consistent.
- Use `--` or `[X]` style markers instead of Unicode symbols that may not render.

The PDF is generated using ReportLab's SimpleDocTemplate with Platypus flowables.

### Links

All of these must be clickable in the PDF:
- Headlines in Appendix A → link to source URL
- Article IDs in Appendix B → link to source URL
- Article IDs in fact-check sources → link to source URL

Use ReportLab's `<a href="url" color="#1a0dab">text</a>` syntax within Paragraph objects
for links. The color `#1a0dab` is Google's link blue.

### Page Breaks

Insert page breaks:
- Before the timeline + alignment chart section
- Before the framing section
- Before the fact-check section
- Before Appendix A
- Before Appendix B

### Table Chunking

For large tables (Appendix A with 50+ rows), split into chunks of ~13 rows per table
to prevent overflow. For Appendix B, use chunks of ~18 rows.

### Chart Sizing

| Chart | Width | Height |
|-------|-------|--------|
| Timeline | 6.8in | 3.5in |
| Sentiment shift | 6.8in | 4.5in |
| Combined timeline+alignment | 6.8in | 4.2in |
| Coverage volume pie | 4.5in | 4.5in |
| Framing bar | 6.5in | 4.0in |

### Styles

Use a consistent style set:
- Title: Helvetica-Bold 22pt
- H1: Helvetica-Bold 16pt, #1a237e (dark blue)
- H2: Helvetica-Bold 12pt, #333333
- Body: Helvetica 9pt, leading 13, #333333
- Small/source note: Helvetica 7pt, #666666, italic
