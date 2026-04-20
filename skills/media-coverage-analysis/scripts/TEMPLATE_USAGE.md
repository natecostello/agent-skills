# Media Coverage Analysis Template Scripts

This directory contains three generalized template scripts adapted from the working Sosa-Celis media coverage analysis report. Each script has been refactored to isolate topic-specific configuration at the top, while preserving the exact working logic from the original implementations.

## Scripts Overview

### 1. `generate_charts_template.py` (19 KB)

**Purpose:** Generate the five core charts for media coverage analysis.

**Produces:**
- `chart_timeline.png` - Event timeline with vertical positioning
- `chart_sentiment_scatter.png` - Outlet positioning by political leaning vs. sentiment
- `chart_combined_timeline_shift.png` - Timeline + government narrative alignment trace
- `chart_coverage_volume.png` - Pie chart of coverage distribution
- `chart_framing.png` - Bar chart of framing emphasis by political category

**Configuration Section:**
- Output directory path
- Color palette (optional customization)
- Time axis limits (COMMON_XLIM for overview, EVENT_XLIM for detail)
- Event list: `(date, label, side, category_key)` tuples
- Position magnitudes for timeline labels
- Outlet data: `(name, ID, x_political, y_sentiment, category)` tuples
- Coverage volume pie chart: labels and sizes
- Framing emphasis data: 4 dimensions across 8 political categories

**Working Logic Preserved:**
- Timeline drawing with alternating event positioning
- Sentiment scatter with category-specific markers and colors
- Article-based government narrative alignment calculation (reads from `article_data.py`)
- Pie chart rendering with auto-percentages
- Multi-series bar chart with proper spacing and labeling
- All matplotlib styling (colors, fonts, sizes, spines)

**Dependencies:**
- `matplotlib`
- `numpy`
- `article_data.py` (optional; Chart 3 gracefully skips if missing)

---

### 2. `generate_shift_chart_template.py` (9.0 KB)

**Purpose:** Generate the article-level sentiment shift chart showing trajectory over time.

**Produces:**
- `chart_sentiment_shift.png` - Article positions with opacity/size encoding recency, arrows showing shifts

**Configuration Section:**
- `ARTICLE_DATA_DIR` - Path to directory containing `article_data.py`
- `OUT` - Output directory for the chart

**Working Logic Preserved:**
- Date-to-alpha mapping (older = faded, newer = opaque)
- Date-to-size mapping (older = small, newer = large)
- Arrow drawing between consecutive articles from same outlet
- Chronological shift visualization with color coding per outlet category
- Latest-article labeling (prominent) + earliest-article labeling (faint)
- Quadrant labels and explanation text
- Full legend with marker shapes

**Dependencies:**
- `matplotlib`
- `article_data.py` (required; contains ARTICLES, OUTLET_X, OUTLET_CAT)

---

### 3. `generate_pdf_template.py` (26 KB)

**Purpose:** Generate comprehensive PDF report with all charts, fact-checks, and appendices.

**Produces:**
- PDF report with the following sections:
  1. Title page + Executive Summary
  2. Timeline of key events (table + chart)
  3. Narrative framing by political category (5 sections)
  4. Sentiment map and shift analysis
  5. Combined timeline + alignment chart
  6. Coverage volume and framing charts
  7. Public sentiment indicators table
  8. Methodology section
  9. Fact-check section (claims, evidence, verdicts with clickable article links)
  10. Appendix A: Scoring rubric and article-level data table
  11. Appendix B: Alignment formula and per-article alignment scores

**Configuration Section:**
- `ARTICLE_DATA_DIR` - Path to `article_data.py`
- `OUT` - Output directory for PDF
- `TOPIC_TITLE` - Main title for the report
- `REPORT_DATE` - Publication date
- `TOPIC_WINDOW` - Time period covered
- `PDF_FILENAME` - Output filename
- `EXECUTIVE_SUMMARY` - Brief overview (with HTML formatting support)
- `TIMELINE_EVENTS` - List of `[date_str, description]` pairs
- `NARRATIVE_SECTIONS` - List of `(section_title, body_html)` tuples (5 sections)
- `PUBLIC_SENTIMENT_DATA` - Table data: `[indicator, finding, source]` rows
- `FACT_CHECKS` - List of `(title, claim_text, evidence_text, verdict_text, source_aids)` tuples
- `FACT_CHECK_SUMMARY` - Summary table data
- `RUBRIC_CRITERIA` - Scoring rubric rows
- `ALIGNMENT_FORMULA` - Formula interpretation table

**Working Logic Preserved:**
- ReportLab document structure and styling
- Table generation with alternating row colors
- Image embedding (graceful fallback to spacer if missing)
- Hyperlink generation from article ID to URL (via `article_data.py`)
- Government alignment calculation: `(1 - sentiment) / 2`
- Broad category classification logic
- Page breaks for proper section separation
- Font styling, colors, and spacing exactly as in original

**Dependencies:**
- `reportlab`
- `article_data.py` (required)

---

## How to Use These Templates

### Step 1: Prepare Your Article Data
Create an `article_data.py` file with your topic data:

```python
# article_data.py
from datetime import datetime

# List of all articles as tuples:
# (outlet, article_id, date, sentiment_y, headline, url, scores_description)
ARTICLES = [
    ("Outlet Name", "A1", datetime(2026, 1, 15), 0.75, "Article Headline", "https://...", "0.25+0.25+0.25+0.00"),
    # ... more articles
]

# Dict mapping outlet name to x-axis political position
OUTLET_X = {
    "Outlet Name": -1.5,
    # ... more outlets
}

# Dict mapping outlet name to category
OUTLET_CAT = {
    "Outlet Name": "center-left",
    # ... more outlets
}
```

### Step 2: Configure Each Template
Fill in the CONFIGURATION section at the top of each script:

**For `generate_charts_template.py`:**
- Set `OUT` to your output directory
- Define your `events` list
- Set `COMMON_XLIM` and `EVENT_XLIM`
- Provide `outlets` list with all sources
- Update pie chart data and framing emphasis arrays

**For `generate_shift_chart_template.py`:**
- Set `ARTICLE_DATA_DIR` and `OUT`

**For `generate_pdf_template.py`:**
- Set `ARTICLE_DATA_DIR`, `OUT`, and metadata fields
- Write `EXECUTIVE_SUMMARY`, `NARRATIVE_SECTIONS`, fact-checks, etc.
- Optionally customize rubric and formula interpretation tables

### Step 3: Run the Scripts
```bash
python generate_charts_template.py
python generate_shift_chart_template.py
python generate_pdf_template.py
```

Charts are generated first (required for PDF). Then PDF can embed them.

---

## Key Design Decisions

### Configuration Isolation
All topic-specific values are clustered at the top of each script, clearly marked with decorative section headers. The rest of the code remains untouched from the Sosa-Celis originals.

### Preserved Logic
Every chart algorithm, color scheme, font setting, and layout decision has been preserved exactly:
- Matplotlib figure sizes, DPI, styling
- Color hex values and category mappings
- Event positioning magnitudes
- Alpha/size date-encoding functions
- ReportLab styling, spacing, font choices
- Table borders, backgrounds, padding
- Hyperlink generation from article data

### Graceful Fallbacks
- `generate_charts_template.py` gracefully skips Chart 3 if `article_data.py` is not found
- `generate_pdf_template.py` exits cleanly with an error message if article data is missing
- Images are embedded only if they exist; otherwise, spacers are used

### Extensibility
The templates can be easily extended:
- Add more events to the timeline
- Add more outlets to the sentiment scatter
- Add more narrative sections to the PDF
- Adjust color palettes and font sizes in the configuration
- Modify rubric criteria or fact-check claims

---

## File Sizes
- `generate_charts_template.py` - 19 KB (5 charts)
- `generate_shift_chart_template.py` - 9.0 KB (1 chart)
- `generate_pdf_template.py` - 26 KB (comprehensive report)

**Total:** ~54 KB of template code for a complete media coverage analysis pipeline.

---

## Example Workflow

```bash
# 1. Create article_data.py in your working directory
# 2. Customize and run the chart generator
python generate_charts_template.py

# 3. Run the shift chart generator
python generate_shift_chart_template.py

# 4. Run the PDF generator (it will embed the charts)
python generate_pdf_template.py

# 5. Output files:
#    - chart_timeline.png
#    - chart_sentiment_scatter.png
#    - chart_combined_timeline_shift.png
#    - chart_coverage_volume.png
#    - chart_framing.png
#    - chart_sentiment_shift.png
#    - YourTopic_Media_Coverage_Report.pdf
```

---

## Notes

- All sentiment/alignment calculations assume y-axis ranges from -1 (hostile) to +1 (sympathetic)
- Political orientation (x-axis) ranges from -3 (far left) to +3 (far right)
- Dates must be Python `datetime` objects
- URLs in article_data.py become clickable links in the PDF (via `aid_link()` function)
- All configuration uses clear variable names; no magic numbers outside the config section

---

**Generated from:** `/sessions/bold-trusting-edison/generate_charts.py`, `generate_shift_charts.py`, `generate_pdf_v3.py`

**Template created:** February 15, 2026
