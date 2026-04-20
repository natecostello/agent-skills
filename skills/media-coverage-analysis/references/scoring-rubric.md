# Scoring Rubric

This document defines how to score articles for sentiment and political orientation. Consistency
depends on applying these rules the same way across every article, regardless of whether you
agree with the article's perspective.

## 1. Sentiment Toward Subject (y-axis): –1.0 to +1.0

Score each article on four observable criteria, each –0.25 to +0.25. Sum all four for the
overall sentiment score. This produces a range of –1.0 to +1.0.

### Criterion 1: Subject Description

How the primary subject of the story is named and characterized in the headline and lede.

| Score | Indicator |
|-------|-----------|
| –0.25 | Dehumanizing or criminalizing language in headline/lede: "illegal alien," "criminal," "violent," "gang member" without qualification |
| –0.15 | Criminalizing language in body but not headline; headline neutral but lede foregrounds status |
| –0.10 | Mild negative framing: "undocumented immigrant" with "charged with" or "accused of" leading |
| 0.00 | Neutral: name + nationality stated factually, no characterization |
| +0.10 | Mild positive context: mentions occupation, family, community ties |
| +0.15 | Humanizing detail prominent: "father of two," "resident," "delivery driver" |
| +0.20 | Victim framing in headline: "man shot by" rather than "man involved in" |
| +0.25 | Strongly sympathetic framing: "victim," humanizing headline, no criminalizing language |

### Criterion 2: Account Primacy

Whose version of events leads the article and structures the narrative.

| Score | Indicator |
|-------|-----------|
| –0.25 | Government/official account leads and structures article; defense/victim account buried or absent |
| –0.15 | Government account leads but defense mentioned by paragraph 3–5 |
| –0.10 | Government account in headline; both accounts in body with slight govt emphasis |
| 0.00 | Both accounts presented with roughly equal prominence and space |
| +0.10 | Defense/victim account in headline; government account in body |
| +0.15 | Defense/victim account leads; government account mentioned but challenged |
| +0.20 | Defense/victim account structures the article; government account presented as contested |
| +0.25 | Defense/victim account leads; government account explicitly challenged or debunked |

### Criterion 3: Emotional Register

The affective tone and moral framing of the article.

| Score | Indicator |
|-------|-----------|
| –0.25 | Indignation toward subject; sympathy exclusively for officers/officials; outrage framing |
| –0.15 | Officers presented as victims; subject's situation minimized |
| –0.10 | Slight rhetorical sympathy for official position; subject treated as problem |
| 0.00 | Procedural, detached, wire-service tone |
| +0.10 | Slight rhetorical concern for subject's situation |
| +0.15 | Empathy for subject visible; concern about overreach |
| +0.20 | Outrage on behalf of subject; strong empathy framing |
| +0.25 | Moral condemnation of official actions; full solidarity framing |

### Criterion 4: Identity/Status Foregrounding

How prominently the subject's identity characteristics (immigration status, race, nationality,
criminal record, etc.) are used as a framing device versus contextual detail.

This criterion adapts to the topic. For immigration stories, it's about immigration status
foregrounding. For police use-of-force stories involving race, it might be about how race
is foregrounded. For corporate scandals, it might be about how the executive's wealth is
framed. The principle is the same: does the article use identity as a framing device to
shape the reader's reaction?

| Score | Indicator |
|-------|-----------|
| –0.25 | Identity/status foregrounded in headline as primary framing device |
| –0.15 | Identity/status in headline but not sole framing device |
| –0.10 | Identity/status mentioned in lede as relevant context |
| 0.00 | Identity/status mentioned in body, neutral context |
| +0.05 | Identity/status mentioned but de-emphasized |
| +0.10 | Identity/status present but buried; irrelevant to framing |
| +0.15 | Identity/status omitted from framing; other details emphasized |
| +0.20 | Identity/status explicitly challenged as irrelevant framing |
| +0.25 | Identity/status omitted entirely or actively de-emphasized |

### Score Breakdown Format

Record scores as a slash-separated string: `"+.25/+.20/+.15/+.10"` representing
subj/prim/reg/stat. This makes it auditable — anyone can check which criteria drove the score.

### Calibration Guide

| Overall Score Range | Interpretation | Example |
|---------------------|----------------|---------|
| +0.75 to +1.00 | Strongly sympathetic | Full solidarity framing, subject is victim, officials condemned |
| +0.25 to +0.75 | Moderately sympathetic | Subject humanized, defense account leads, concern for subject |
| –0.25 to +0.25 | Neutral / balanced | Wire-service tone, both accounts presented, minimal framing |
| –0.75 to –0.25 | Moderately hostile | Official account leads, criminalizing language, subject as problem |
| –1.00 to –0.75 | Strongly hostile | Full government narrative, criminalizing headline, subject dehumanized |

## 2. Political Orientation (x-axis): –3.0 to +3.0

Use AllSides and Ad Fontes Media ratings as baselines for each outlet's general editorial
positioning. Then adjust ±0.3 maximum based on this specific story's framing.

### Baseline Spectrum

| x Range | Category | Example Outlets |
|---------|----------|----------------|
| –3.0 to –2.0 | Far Left | The Intercept, Common Dreams, Jacobin |
| –2.0 to –1.5 | Left | Salon, Daily Beast, Mother Jones, MN Reformer |
| –1.5 to –0.5 | Center-Left | NPR, PBS, CNN, WaPo, Slate, MPR, Sahan Journal |
| –0.5 to +0.5 | Center | AP, CBS, NBC, ABC, Reuters, KARE 11, KTTC, Fox 9 |
| +0.5 to +1.0 | Center-Right | Free Press, WSJ editorial |
| +1.0 to +2.0 | Right | Fox News, Nat'l Review, Wash Times, Daily Caller |
| +2.0 to +2.5 | Far Right | Daily Wire, Newsmax, Federalist |
| +2.5 to +3.0 | Extreme Right | Breitbart, OANN |
| +1.0 (approx) | Libertarian | Reason, Cato Institute |
| +2.5 (for govt) | Government | DHS, DOJ, White House press releases |

### Story-Specific Adjustments (±0.3 max)

- If an outlet's coverage of this specific story is notably more partisan than their baseline,
  adjust up to ±0.3
- Document the adjustment rationale
- Never adjust more than ±0.3 from baseline — if coverage seems wildly off-baseline, double-check
  that you have the outlet identified correctly

### Outlet Categories for Charting

Assign each outlet a category string for marker shape/color grouping:
`left`, `center-left`, `center`, `center-right`, `right`, `libertarian`, `gov`

### Broad Categories for Alignment Chart

For the government narrative alignment traces, group outlets into 6 categories:

| Broad Category | Rule |
|---------------|------|
| Far-Right | `cat == 'right'` and `x >= 2.3` |
| Right | `cat == 'right'` and `x < 2.3` |
| Center | `cat in ('center', 'center-right')` |
| Center-Left | `cat == 'center-left'` |
| Left | `cat == 'left'` |
| Libertarian | `cat == 'libertarian'` |

Government/official sources are excluded from the alignment traces (they define the narrative,
they don't align with it).

## 3. Consistency Principles

- **Score what you observe**, not what you infer. If an article uses neutral language but you
  know the outlet is partisan, score the language, not the outlet.
- **Score each criterion independently.** An article can have hostile subject description but
  neutral account primacy (e.g., if it uses "illegal alien" in the headline but quotes both
  sides equally).
- **When uncertain, score toward 0.** A score of 0.00 means "I couldn't determine a clear lean"
  — this is better than guessing.
- **Re-score if needed.** If after scoring 20 articles you realize your calibration drifted,
  go back and adjust. Internal consistency matters more than getting every score perfect on
  first pass.
- **The subscores must sum to the overall score.** This is a hard constraint. If you want an
  overall score of +0.55, you need subscores that add to +0.55.
