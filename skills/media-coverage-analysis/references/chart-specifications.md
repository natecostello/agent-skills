# Chart Specifications

This document defines the data structures, visual specifications, and computation methods
for all 6 charts in the report.

**STANDARDIZATION RULE:** The color palette (Section 2) and marker shapes (Section 3) are
canonical. Every chart in every report must use these exact colors and markers for the
corresponding political categories. Do not invent ad-hoc colors or markers. If a new
category is needed, define it here first.

## 1. Article Dataset (`article_data.py`)

This file is the single source of truth. All charts and both appendices draw from it.

### Structure

```python
from datetime import datetime

# Each article: (outlet, article_id, date, y_sentiment, headline, url, score_breakdown)
ARTICLES = [
    ("The Intercept", "A1a", datetime(2026, 1, 7), 0.90,
     "This Isn't the First Killing by ICE",
     "https://theintercept.com/...",
     "+.25/+.25/+.25/+.15"),
    # ... one entry per article
]

# Political x-position for each outlet (from scoring-rubric.md)
OUTLET_X = {
    "The Intercept": -2.8,
    "Fox News": 1.8,
    # ... one entry per outlet
}

# Category for marker shapes
OUTLET_CAT = {
    "The Intercept": "left",
    "Fox News": "right",
    # ... one entry per outlet
}
```

### Article ID Convention

Use `[Outlet Abbreviation][Letter][Sequence]`:
- `A1a` = first outlet, first article
- `A1b` = first outlet, second article
- Number outlets roughly left-to-right
- Letter suffix `a`, `b`, `c` for chronological articles within an outlet

### Completeness Check

Every outlet in ARTICLES must have an entry in both OUTLET_X and OUTLET_CAT.
Every article must have all 7 fields populated (url can be empty string for unavailable links).

## 2. Color Palette

```python
LEFT_C    = '#2171b5'  # Blue
CENTER_C  = '#6a51a3'  # Purple
RIGHT_C   = '#cb181d'  # Red
LIBERT_C  = '#f59e0b'  # Amber
GOV_C     = '#525252'  # Dark gray
NEUTRAL_C = '#737373'  # Gray

# Event marker colors
SHOOTING_C = '#e31a1c'  # Red (shooting events)
EVIDENCE_C = '#2ca02c'  # Green (evidence/accountability events)
INFO_C     = '#1f77b4'  # Blue (government/public/media events)
```

## 3. Marker Shapes by Category

```python
cat_style = {
    'left':         (LEFT_C,    's'),    # Square
    'center-left':  ('#4292c6', 'D'),    # Diamond
    'center':       (CENTER_C,  'o'),    # Circle
    'center-right': ('#fb6a4a', 'D'),    # Diamond
    'right':        (RIGHT_C,   '^'),    # Triangle up
    'libertarian':  (LIBERT_C,  'P'),    # Plus (filled)
    'gov':          (GOV_C,     'X'),    # X
}
```

## 4. Chart 1: Timeline (`chart_timeline.png`)

A horizontal timeline showing key events with colored markers.

- **Figure size**: 16×5 inches
- **Layout**: Events placed at alternating y-positions above and below the axis
- **Markers**: Colored circles (red for shootings, green for evidence/accountability, blue for govt/public)
- **Labels**: Event text with date, connected to marker by vertical line
- **X-axis**: Date range covering the full topic window
- **Legend**: Marker color meanings

Events are defined as tuples: `(date, label, side, category)` where:
- `side`: 'up' or 'down' for alternating placement
- `category`: 'shooting', 'evidence', 'govt', 'public' → determines color

**CRITICAL: Text box collision avoidance.** Timeline labels MUST NOT overlap each other.
Use a greedy slot-based stagger algorithm:

1. For each event, check ALL prior same-side events within a **computed** proximity window.
2. Starting at the base y-position, check if any nearby label occupies that slot.
3. If occupied, increment y (for 'up') or decrement y (for 'down') by the step size.
4. Repeat until a clear slot is found.
5. The same collision avoidance applies to the top panel of Chart 4 (combined timeline).

**CRITICAL: Computing `proximity_days`.** The proximity window must reflect the actual width
of rendered text boxes in date-axis units, NOT a small fixed number of days. A label rendered
at 6pt font is approximately 1.5 inches wide on a typical chart. To convert this to days:

```
proximity_days = (date_range_days / usable_figure_width_inches) * label_width_inches * 1.2
```

For example:
- Chart 1 (standalone timeline): 380-day range on a 20-inch figure ≈ 19 days/inch.
  A 1.5-inch label spans ~28 days. With 1.2x safety margin → **proximity_days ≈ 55**.
- Chart 4 (combined timeline): 230-day range on a 14-inch usable width ≈ 16 days/inch.
  A 1.2-inch label at 5pt spans ~20 days. With 1.2x safety margin → **proximity_days ≈ 35**.

**Never use `proximity_days=3`.** That value only catches events on literally the same day and
guarantees overlapping labels for any real-world timeline. Always compute the value from the
date range and figure dimensions. When in doubt, use a larger value — extra vertical stagger
is always preferable to overlapping text.

Implementation pattern:
```python
def _stagger_y_positions(events, base_up=1.0, base_down=-1.0, step=0.8, proximity_days=55):
    y_positions = []
    up_placed, down_placed = [], []
    for i, (d, label, side, cat) in enumerate(events):
        if side == 'up':
            nearby_ys = [py for pd, py in up_placed if abs((d - pd).days) <= proximity_days]
            y = base_up
            while any(abs(y - ny) < step for ny in nearby_ys):
                y += step
            up_placed.append((d, y))
        else:
            nearby_ys = [py for pd, py in down_placed if abs((d - pd).days) <= proximity_days]
            y = base_down
            while any(abs(y - ny) < step for ny in nearby_ys):
                y -= step
            down_placed.append((d, y))
        y_positions.append(y)
    return y_positions
```

**Figure height must accommodate stagger depth.** Dense event clusters require 3+ stagger
levels. Use `figsize=(22, 10)` for standalone timelines and `set_ylim(-6.5, 6.5)` to provide
room. For Chart 4's top panel, use `set_ylim(-5.5, 5.5)`. Reduce font size to 6pt for
standalone timelines and 5pt for Chart 4's top panel.

Labels should be concise — aim for ≤25 characters per line, 2 lines maximum. If a label
requires 3+ lines or exceeds 25 chars/line, shorten it. Shorter labels reduce the required
proximity_days and produce cleaner charts.

## 5. Chart 2: Sentiment Scatter (`chart_sentiment_scatter.png`)

Static outlet-level scatter plot (one point per outlet, not per article).

- **Figure size**: 16×10 inches
- **X-axis**: Political orientation (–3.5 to +3.5)
- **Y-axis**: Average sentiment (–1.15 to +1.15)
- **Points**: Marker shape and color by category
- **Labels**: Outlet name next to each point
- **Reference lines**: Dashed gray lines at x=0 and y=0
- **Quadrant labels**: "Left + Sympathetic", "Right + Hostile", etc.
- **Legend**: Marker shapes explained

For outlets with multiple articles, use the average sentiment as the y-position.

**CRITICAL: Label collision avoidance.** With 20+ outlets, labels will overlap unless
actively repelled. Use an iterative repulsion algorithm:

1. Collect initial label positions (offset slightly from the data point).
2. Estimate each label's bounding box in data coordinates (character width ≈ x_range/110,
   label height ≈ y_range/35).
3. For each pair of labels, check if bounding boxes overlap.
4. If overlapping, push apart — primarily vertically, with slight horizontal displacement
   when labels are nearly co-located.
5. Iterate 50 times or until no labels move.
6. Draw thin leader lines from data points to displaced labels.

Implementation pattern:
```python
def _repel_labels(labels_data, x_range=7.0, y_range=2.3, iterations=50):
    """labels_data: list of [x, y, name] — positions updated in-place."""
    char_w = x_range / 110
    label_h = y_range / 35
    for _ in range(iterations):
        moved = False
        for i in range(len(labels_data)):
            for j in range(i + 1, len(labels_data)):
                xi, yi = labels_data[i][0], labels_data[i][1]
                xj, yj = labels_data[j][0], labels_data[j][1]
                wi = len(labels_data[i][2]) * char_w
                wj = len(labels_data[j][2]) * char_w
                dx = abs(xi - xj)
                dy = abs(yi - yj)
                min_dx = (wi + wj) / 2
                min_dy = label_h
                if dx < min_dx and dy < min_dy:
                    push_y = (min_dy - dy) / 2 + 0.02
                    push_x = (min_dx - dx) * 0.15 if dx < min_dx * 0.5 else 0
                    if yi >= yj:
                        labels_data[i][1] += push_y; labels_data[j][1] -= push_y
                    else:
                        labels_data[i][1] -= push_y; labels_data[j][1] += push_y
                    if xi >= xj:
                        labels_data[i][0] += push_x; labels_data[j][0] -= push_x
                    else:
                        labels_data[i][0] -= push_x; labels_data[j][0] += push_x
                    moved = True
        if not moved:
            break
```

After repulsion, draw leader lines from each data point to its displaced label position
when the displacement exceeds a threshold (e.g., distance > 0.15 in data coordinates).
Use thin, semi-transparent lines (`'-', color='#999', alpha=0.3, lw=0.5`).

The same repulsion approach applies to both Chart 2 (outlet-level) and Chart 3
(article-level, labeling each outlet's latest article).

## 6. Chart 3: Article-Level Shift (`chart_sentiment_shift.png`)

Every article as an individual point, with recency encoding and chronological arrows.

- **Figure size**: 16×10 inches
- **X-axis**: Political orientation (–3.5 to +3.5)
- **Y-axis**: Sentiment (–1.15 to +1.15)
- **Point size**: Recency-encoded: `size = 50 + 130 * frac` where frac = normalized date position
- **Point opacity**: Recency-encoded: `alpha = 0.20 + 0.80 * frac`
- **Arrows**: Connect articles from the same outlet chronologically (earlier → later)
  - Arrow alpha = `min(alpha_start, alpha_end) * 0.5`
  - Only draw if |dy| > 0.02 (skip trivial shifts)
- **Labels**: Latest article for each outlet labeled in bold; earliest labeled faintly
- **Legend**: Explains faded/small = earlier, bold/large = later, plus marker shapes
- **Footer text**: Article count, explanation of encoding

## 7. Chart 4: Timeline + Alignment (`chart_combined_timeline_shift.png`)

Two-panel chart with shared x-axis. Timeline events on top, alignment traces below.

- **Figure size**: 16×10 inches
- **Layout**: 2 subplots, height ratio 3:2, shared x-axis
- **Top panel**: Same as Chart 1 timeline but abbreviated to start at the topical event
- **Bottom panel**: Government narrative alignment traces by category

### Alignment Computation (Bottom Panel)

**Formula:** `alignment = (1 - sentiment) / 2`

**Trace method (latest-per-outlet):**
1. Sort all articles in a category by date
2. Group by date (bucket to the day)
3. For each date group, update the "latest" dict with each outlet's newest score
4. Compute the group average = mean of all outlets' latest scores
5. Emit one point per unique date

```python
def build_latest_per_outlet_avg(points):
    """points = [(outlet, date, alignment), ...]"""
    sorted_pts = sorted(points, key=lambda p: p[1])
    latest = {}  # outlet -> latest alignment
    by_date = OrderedDict()
    for outlet, d, v in sorted_pts:
        if d not in by_date:
            by_date[d] = []
        by_date[d].append((outlet, v))
    dates_out, avgs_out = [], []
    for d, articles in by_date.items():
        for outlet, v in articles:
            latest[outlet] = v
        avg = sum(latest.values()) / len(latest)
        dates_out.append(d)
        avgs_out.append(avg)
    return dates_out, avgs_out
```

**Broad categories for traces:**
- Far-Right: `cat == 'right'` and `x >= 2.3`
- Right: `cat == 'right'` and `x < 2.3`
- Center: `cat in ('center', 'center-right')`
- Center-Left: `cat == 'center-left'`
- Left: `cat == 'left'`
- Libertarian: `cat == 'libertarian'`
- Government/official: **excluded** from traces

**Trace styles:**
```python
trace_styles = {
    'Far-Right':    ('v-',  '#800000', 2.5, 7),  # Triangle down, maroon
    'Right':        ('o-',  RIGHT_C,   2.5, 7),  # Circle, red
    'Center':       ('s--', CENTER_C,  2.0, 6),  # Square dashed, purple
    'Center-Left':  ('D--', '#4292c6', 2.0, 6),  # Diamond dashed, blue
    'Left':         ('D:',  LEFT_C,    2.0, 6),  # Diamond dotted, blue
    'Libertarian':  ('P-.', LIBERT_C,  2.0, 7),  # Plus dash-dot, amber
}
```

**X-axis limits:** Start at topical event date minus 2 days, end at report date plus 2 days.
(Not the full topic window — only the portion with article data.)

**Y-axis:** 0 to 1.1 (alignment scale)

**Filtering:** Only include articles on or after the topical event date. Pre-event articles
are excluded from the alignment chart even if they exist in the dataset.

## 8. Chart 5: Coverage Volume (`chart_coverage_volume.png`)

Pie chart showing estimated coverage volume by source type.

- **Figure size**: 8×8 inches
- **CRITICAL: The pie chart must be perfectly circular.** Use `ax.set_aspect('equal')` to
  enforce a 1:1 aspect ratio. The `figsize` alone is not sufficient — matplotlib may still
  produce an oblong chart without the explicit aspect setting. Always call:
  ```python
  ax.set_aspect('equal')
  ```
- **Categories**: Center-Left/Mainstream, Left/Progressive, Right/Conservative, Far Right,
  Local, Wire (AP/Reuters), Libertarian, Govt
- **Colors**: Match the color palette above
- **Labels**: Category name + percentage

Coverage volume is estimated from search-result frequency, not counted precisely. This is
an approximate visualization — note this in the methodology.

## 9. Chart 6: Framing (`chart_framing.png`)

Grouped bar chart showing narrative framing emphasis by political category.

- **Figure size**: 12×7 inches
- **Categories (x-axis groups) — STANDARD ORDER:** Far Left, Left, Center-Left, Center,
  Center-Right, Right, Far Right, Libertarian. This left-to-right ordering with Libertarian
  last (as a cross-spectrum outlier) is fixed across all reports. Not every category needs
  data — omit categories with no articles — but the order of those present must follow this
  sequence.
- **Framing dimensions** (bars within each group): Sympathy for subject, Govt credibility
  concern, Civil liberties emphasis, Immigration-status emphasis (or equivalent topic-specific
  dimension)
- **Y-axis**: 0 to 1.0 (emphasis level)
- **Colors**: One color per framing dimension

The framing values are qualitative judgments based on the scored articles — they represent
the analyst's assessment of how much emphasis each category placed on each framing dimension,
not a mechanical computation.

## 10. Global Matplotlib Settings

```python
plt.rcParams.update({
    'figure.facecolor': '#fafafa',
    'axes.facecolor': '#fafafa',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
})
```

All charts saved at 150 DPI with `bbox_inches='tight'`.
