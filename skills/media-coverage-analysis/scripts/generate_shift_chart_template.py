#!/usr/bin/env python3
"""
Generate article-level sentiment shift chart — Template.
Adapted from the working Sosa-Celis report to be generalized for any topic.

Each article is plotted as a data point. Recent articles are larger and more opaque.
Arrows connect articles from the same outlet chronologically.

INSTRUCTIONS: Update the CONFIGURATION section to point to your article_data.py file
and output directory, then run this script. All visualization logic remains unchanged.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
from collections import defaultdict
import numpy as np
import os, sys

# ════════════════════════════════════════════════════════════════════════════
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                        CONFIGURATION SECTION                             ║
# ║  Customize only these two paths. Everything else is automatic.           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# ════════════════════════════════════════════════════════════════════════════

# Path to directory containing your article_data.py file
ARTICLE_DATA_DIR = "/sessions/bold-trusting-edison"

# Output directory for the chart
OUT = "/sessions/bold-trusting-edison/mnt/2026-02-14 Missy Topics Research"

# ════════════════════════════════════════════════════════════════════════════
# END CONFIGURATION — Below this line, no customization needed
# ════════════════════════════════════════════════════════════════════════════

# Import article data from specified directory
sys.path.insert(0, ARTICLE_DATA_DIR)
try:
    from article_data import ARTICLES, OUTLET_X, OUTLET_CAT
except ImportError as e:
    print(f"ERROR: Could not import article_data from {ARTICLE_DATA_DIR}")
    print(f"Make sure article_data.py exists in that directory.")
    sys.exit(1)

os.makedirs(OUT, exist_ok=True)

# Color scheme
LEFT_C = '#2171b5'
CENTER_C = '#6a51a3'
RIGHT_C = '#cb181d'
LIBERT_C = '#f59e0b'
GOV_C = '#525252'

cat_style = {
    'left':         (LEFT_C,    's'),
    'center-left':  ('#4292c6', 'D'),
    'center':       (CENTER_C,  'o'),
    'center-right': ('#fb6a4a', 'D'),
    'right':        (RIGHT_C,   '^'),
    'libertarian':  (LIBERT_C,  'P'),
    'gov':          (GOV_C,     'X'),
}

plt.rcParams.update({
    'figure.facecolor': '#fafafa', 'axes.facecolor': '#fafafa',
    'font.family': 'sans-serif', 'font.size': 10,
    'axes.titlesize': 13, 'axes.titleweight': 'bold',
})

# ── Compute date range for alpha and size mapping ──
from datetime import datetime
all_dates = [a[2] for a in ARTICLES]
date_min = min(all_dates)
date_max = max(all_dates)
date_range = (date_max - date_min).days or 1

def date_to_alpha(d):
    """More recent articles get higher alpha. Range: 0.2 (oldest) to 1.0 (newest)."""
    frac = (d - date_min).days / date_range
    return 0.20 + 0.80 * frac

def date_to_size(d):
    """More recent articles are larger. Range: 50 (oldest) to 180 (newest)."""
    frac = (d - date_min).days / date_range
    return 50 + 130 * frac

# ── Group articles by outlet (for drawing arrows) ──
by_outlet = defaultdict(list)
for outlet, aid, date, y, headline, url, scores in ARTICLES:
    x = OUTLET_X[outlet]
    cat = OUTLET_CAT[outlet]
    by_outlet[outlet].append((date, x, y, aid, cat, headline))

# Sort each outlet's articles by date
for k in by_outlet:
    by_outlet[k].sort(key=lambda t: t[0])


# ═══════════════ CHART — Article-Level Sentiment Shift ═══════════════
fig, ax = plt.subplots(figsize=(16, 10))
ax.set_title(
    'Sentiment Trajectory by Article\n'
    '(Each point = one article; opacity & size = recency; arrows = chronological shift within outlet)',
    fontsize=13, fontweight='bold', pad=18)

# Draw arrows first (behind points)
for outlet, points in by_outlet.items():
    if len(points) < 2:
        continue
    cat = points[0][4]
    c, _ = cat_style[cat]
    for i in range(len(points) - 1):
        d1, x1, y1 = points[i][0], points[i][1], points[i][2]
        d2, x2, y2 = points[i+1][0], points[i+1][1], points[i+1][2]
        # Arrow from earlier to later
        dy = y2 - y1
        if abs(dy) > 0.02:
            alpha_arr = min(date_to_alpha(d1), date_to_alpha(d2)) * 0.5
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', color=c,
                                        lw=1.5, alpha=alpha_arr,
                                        connectionstyle='arc3,rad=0.0'))

# Plot each article as a point
for outlet, aid, date, y, headline, url, scores in ARTICLES:
    x = OUTLET_X[outlet]
    cat = OUTLET_CAT[outlet]
    c, m = cat_style[cat]
    alpha = date_to_alpha(date)
    size = date_to_size(date)
    ax.scatter(x, y, c=c, marker=m, s=size, zorder=5, alpha=alpha,
               edgecolors='white', linewidth=0.5)

# Label the LATEST article for each outlet (most prominent)
for outlet, points in by_outlet.items():
    latest = points[-1]  # already sorted by date
    d, x, y, aid, cat, headline = latest
    c, _ = cat_style[cat]
    label = f"{outlet} [{aid}]"
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(9, -3),
                fontsize=6, color=c, fontweight='bold', alpha=0.9)

    # If outlet has multiple articles, also faintly label earliest
    if len(points) > 1:
        earliest = points[0]
        d0, x0, y0, aid0, cat0, hl0 = earliest
        ax.annotate(f"[{aid0}]", (x0, y0), textcoords="offset points", xytext=(7, 3),
                    fontsize=5, color=c, alpha=0.45)

ax.axhline(0, color='#cccccc', linewidth=0.8, linestyle='--')
ax.axvline(0, color='#cccccc', linewidth=0.8, linestyle='--')
ax.set_xlim(-3.5, 3.5)
ax.set_ylim(-1.15, 1.15)
ax.set_xlabel('← Left-Leaning                    Political Orientation                    Right-Leaning →', fontsize=11)
ax.set_ylabel('← Hostile to Subject         Sentiment Toward Sosa-Celis         Sympathetic →', fontsize=11)

# Quadrant labels
ax.text(-3.0, 1.02, 'Left + Sympathetic', fontsize=8, color='#999', style='italic')
ax.text(1.8, 1.02, 'Right + Sympathetic', fontsize=8, color='#999', style='italic')
ax.text(-3.0, -1.08, 'Left + Hostile', fontsize=8, color='#999', style='italic')
ax.text(2.0, -1.08, 'Right + Hostile', fontsize=8, color='#999', style='italic')

# Explanation
ax.text(0.5, -0.03,
        f'Each point = 1 article ({len(ARTICLES)} total)  ·  Smaller/faded = earlier  ·  Larger/opaque = more recent  ·  '
        'Arrows = shift within outlet  ·  See Appendix A for full article list',
        transform=ax.transAxes, fontsize=7.5, color='#666', ha='center', style='italic')

# Legend
legend_handles = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='grey',
           markeredgecolor='white', markersize=5, alpha=0.25, label='Earlier article (faded, small)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='grey',
           markeredgecolor='white', markersize=10, alpha=1.0, label='Latest article (bold, large)'),
    Line2D([0], [0], color='grey', linewidth=1.5, alpha=0.4, label='Chronological shift arrow'),
]
for cat_key, lbl in [('left', 'Left/Far Left'), ('center-left', 'Ctr-Left'),
                      ('center', 'Center'), ('center-right', 'Ctr-Right'),
                      ('right', 'Right/Far Right'), ('libertarian', 'Libertarian'), ('gov', 'Govt')]:
    c2, m2 = cat_style[cat_key]
    legend_handles.append(Line2D([0], [0], marker=m2, color='w', markerfacecolor=c2,
                                 markeredgecolor='white', markersize=8, label=lbl))

ax.legend(handles=legend_handles, loc='upper left', fontsize=7, framealpha=0.92,
          title='Legend', title_fontsize=8, borderpad=0.8, labelspacing=0.45, ncol=2)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(f'{OUT}/chart_sentiment_shift.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Article-level sentiment shift chart ({len(ARTICLES)} articles)")
print(f"\n✅ Done. Chart saved to: {OUT}/chart_sentiment_shift.png")
