#!/usr/bin/env python3
"""
Generate charts for media coverage analysis — Template.
Adapted from the working Sosa-Celis report to be generalized for any topic.

This template produces five charts:
  1. Timeline of key events
  2. Sentiment scatter (outlets positioned by political leaning and sentiment)
  3. Combined timeline + government narrative alignment
  4. Coverage volume (pie chart)
  5. Framing emphasis (bar chart by category)

INSTRUCTIONS: Fill in the CONFIGURATION section below with your topic-specific data,
then run this script. All chart logic and styling remain unchanged.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import os

# ════════════════════════════════════════════════════════════════════════════
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                        CONFIGURATION SECTION                             ║
# ║  Customize the following values for your topic. Everything else remains  ║
# ║  unchanged and uses the exact logic from the Sosa-Celis working report.  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# ════════════════════════════════════════════════════════════════════════════

# Output directory for charts
OUT = "/path/to/your/output/directory"
os.makedirs(OUT, exist_ok=True)

# Color palette (customize if desired)
LEFT_C = '#2171b5'
CENTER_C = '#6a51a3'
RIGHT_C = '#cb181d'
LIBERT_C = '#f59e0b'
GOV_C = '#525252'
NEUTRAL_C = '#737373'
SHOOTING_C = '#e31a1c'
EVIDENCE_C = '#2ca02c'
INFO_C = '#1f77b4'

# Time axis limits for Chart 1 (timeline overview)
COMMON_XLIM = (datetime(2025, 11, 25), datetime(2026, 2, 20))

# Time axis limits for Chart 3 (combined timeline+alignment, typically narrower)
# Usually starts at the primary topical event
EVENT_XLIM = (datetime(2026, 1, 12), datetime(2026, 2, 16))

# Define key events as a list of tuples:
# (date, label, side, category_key)
# where:
#   - date: datetime object
#   - label: Multi-line text for annotation (use \n)
#   - side: +1 (positive/upper) or -1 (negative/lower) on timeline
#   - category_key: 'gov' | 'shoot' | 'evidence' | 'info'
events = [
    (datetime(2025, 12, 1),  "Operation Metro\nSurge begins",                  -1, 'gov'),
    (datetime(2026, 1, 7),   "Renée Good\nfatally shot",                       1,  'shoot'),
    (datetime(2026, 1, 14),  "Sosa-Celis shot\nby ICE agent",                  -1, 'shoot'),
    (datetime(2026, 1, 15),  "DHS labels victims\n'violent criminals'",         1,  'gov'),
    (datetime(2026, 1, 16),  "Bystander videos\nemerge",                       -1, 'evidence'),
    (datetime(2026, 1, 24),  "Alex Pretti\nfatally shot",                      1,  'shoot'),
    (datetime(2026, 1, 27),  "Conservative outlets\nbreak from narrative",      -1, 'evidence'),
    (datetime(2026, 2, 5),   "Partner Indriany\nspeaks publicly",              1,  'info'),
    (datetime(2026, 2, 13),  "ICE admits agents\n'untruthful'",                -1, 'evidence'),
    (datetime(2026, 2, 14),  "Charges dismissed;\nperjury probe opened",        1,  'evidence'),
]

# Position magnitudes for events alternating vertically on timeline
# These control the vertical spacing of event labels
pos_mags = [2.0, 3.4, 4.5, 1.4, 2.8]
neg_mags = [2.0, 3.4, 4.5, 1.4, 2.8]

# Outlet data: (name, ID, x_political, y_sentiment, category)
# x_political: -3.0 (far left) to +3.0 (far right)
# y_sentiment: -1.0 (hostile) to +1.0 (sympathetic)
# category: 'left' | 'center-left' | 'center' | 'center-right' | 'right' | 'libertarian' | 'gov'
outlets = [
    # Far Left
    ("The Intercept",      "A1",  -2.8, 0.95, 'left'),
    ("Common Dreams",      "A2",  -2.5, 0.9,  'left'),
    ("Jacobin/Salon",      "A3",  -2.2, 0.85, 'left'),
    # Left
    ("The Daily Beast",    "A4",  -1.8, 0.85, 'left'),
    ("Minnesota Reformer", "A5",  -1.5, 0.8,  'left'),
    ("Mother Jones",       "A6",  -1.5, 0.8,  'left'),
    # Center-Left
    ("Slate",              "A7",  -1.2, 0.7,  'center-left'),
    ("NPR",                "A8",  -1.0, 0.6,  'center-left'),
    ("PBS NewsHour",       "A9",  -0.8, 0.55, 'center-left'),
    ("CNN",                "A10", -0.7, 0.5,  'center-left'),
    ("Washington Post",    "A11", -0.5, 0.5,  'center-left'),
    ("Sahan Journal",      "A12", -0.5, 0.85, 'center-left'),
    # Center
    ("NBC News",           "A13", -0.3, 0.45, 'center'),
    ("CBS News",           "A14", -0.2, 0.4,  'center'),
    ("AP / Wire",          "A15",  0.0, 0.35, 'center'),
    ("ABC News",           "A16", -0.2, 0.4,  'center'),
    # Center-Right
    ("The Free Press",     "A17",  0.5, 0.3,  'center-right'),
    ("Reason",             "A18",  1.0, 0.35, 'libertarian'),
    # Right
    ("Fox News",           "A19",  1.8, -0.2, 'right'),
    ("Washington Times",   "A20",  1.0, 0.0,  'right'),
    ("National Review",    "A21",  1.8, -0.5, 'right'),
    ("Daily Caller",       "A22",  2.0, -0.4, 'right'),
    # Far Right
    ("Daily Wire",         "A23",  2.3, -0.7, 'right'),
    ("The Federalist",     "A24",  2.5, -0.8, 'right'),
    ("Newsmax",            "A25",  2.3, -0.3, 'right'),
    ("Breitbart",          "A26",  2.7, -0.5, 'right'),
    ("OANN",               "A27",  2.8, -0.85,'right'),
    # Government
    ("DHS (official)",     "A28",  2.5, -0.9, 'gov'),
]

# Coverage volume pie chart data
# Customize the labels and percentages for your topic
pie_labels = ['Center-Left /\nMainstream', 'Left /\nProgressive', 'Right /\nConservative',
              'Far Right', 'Local MN', 'Wire (AP)', 'Libertarian', 'Govt']
pie_sizes = [30, 18, 10, 8, 18, 8, 4, 4]
pie_colors = ['#4292c6', LEFT_C, RIGHT_C, '#800000', '#78c679', NEUTRAL_C, LIBERT_C, GOV_C]

# Framing emphasis data (Chart 5)
# Each row represents a political category; columns are emphasis levels (0-1)
framing_categories = ['Far Left', 'Left', 'Center-Left', 'Center', 'Center-Right', 'Right', 'Far Right', 'Libertarian']
framing_accountability =     [0.95, 0.90, 0.85, 0.70, 0.55, 0.25, 0.10, 0.70]
framing_immigrant_sympathy = [0.95, 0.85, 0.70, 0.50, 0.30, 0.15, 0.05, 0.45]
framing_govt_credibility =   [0.90, 0.85, 0.80, 0.75, 0.65, 0.40, 0.20, 0.85]
framing_civil_liberties =    [0.85, 0.75, 0.65, 0.50, 0.40, 0.15, 0.05, 0.90]

# ════════════════════════════════════════════════════════════════════════════
# END CONFIGURATION — Below this line, no customization needed
# ════════════════════════════════════════════════════════════════════════════

plt.rcParams.update({
    'figure.facecolor': '#fafafa', 'axes.facecolor': '#fafafa',
    'font.family': 'sans-serif', 'font.size': 11,
    'axes.titlesize': 14, 'axes.titleweight': 'bold',
})

color_map = {'gov': GOV_C, 'shoot': SHOOTING_C, 'evidence': EVIDENCE_C, 'info': INFO_C}
legend_items = [
    mpatches.Patch(color=SHOOTING_C, label='Shooting events'),
    mpatches.Patch(color=GOV_C, label='Government actions'),
    mpatches.Patch(color=EVIDENCE_C, label='Evidence / accountability'),
    mpatches.Patch(color=INFO_C, label='Public / media events'),
]

def draw_timeline(ax, fontsize=8, markersize=9):
    """Draw event timeline on axis. Uses global 'events' and 'pos_mags', 'neg_mags'."""
    pi, ni = 0, 0
    for date, label, side, ckey in events:
        col = color_map[ckey]
        if side > 0:
            lvl = pos_mags[pi % len(pos_mags)]; pi += 1
        else:
            lvl = -neg_mags[ni % len(neg_mags)]; ni += 1
        ax.plot([date, date], [0, lvl], color=col, linewidth=1.8, alpha=0.7)
        ax.plot(date, lvl, 'o', color=col, markersize=markersize, zorder=5,
                markeredgecolor='white', markeredgewidth=1)
        va = 'bottom' if lvl > 0 else 'top'
        y_off = 10 if lvl > 0 else -10
        ax.annotate(label, xy=(date, lvl), xytext=(0, y_off),
                    textcoords='offset points', ha='center', va=va,
                    fontsize=fontsize, fontweight='bold', color=col,
                    bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                              edgecolor=col, alpha=0.92, linewidth=1.2))
    ax.axhline(0, color='#aaaaaa', linewidth=2, zorder=1)


# ═══════════════ CHART 1 — Standalone Timeline ═══════════════
fig, ax = plt.subplots(figsize=(16, 9))
draw_timeline(ax)
ax.legend(handles=legend_items, loc='lower left', fontsize=9, framealpha=0.9, ncol=2)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.set_xlim(*COMMON_XLIM); ax.set_ylim(-5.8, 5.8); ax.set_yticks([])
ax.set_title('Timeline: The Julio Cesar Sosa-Celis Story & Operation Metro Surge', pad=15, fontsize=15)
for sp in ['top', 'right', 'left']: ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(f'{OUT}/chart_timeline.png', dpi=150, bbox_inches='tight')
plt.close(); print("✓ Timeline")


# ═══════════════ CHART 2 — Sentiment Scatter (expanded sources) ═══════════════
fig, ax = plt.subplots(figsize=(14, 9))

cat_style = {
    'left':         (LEFT_C,    's', 'Left / Far Left'),
    'center-left':  ('#4292c6', 'D', 'Center-Left'),
    'center':       (CENTER_C,  'o', 'Center'),
    'center-right': ('#fb6a4a', 'D', 'Center-Right'),
    'right':        (RIGHT_C,   '^', 'Right / Far Right'),
    'libertarian':  (LIBERT_C,  'P', 'Libertarian'),
    'gov':          (GOV_C,     'X', 'Government'),
}

for name, aid, x, y, cat in outlets:
    c, m, _ = cat_style[cat]
    ax.scatter(x, y, c=c, marker=m, s=140, zorder=5, edgecolors='white', linewidth=0.8)
    ax.annotate(f"{name} [{aid}]", (x, y), textcoords="offset points", xytext=(9, -3),
                fontsize=7, color=c, fontweight='bold')

# ── Build marker legend ──
from matplotlib.lines import Line2D
legend_handles = []
seen = set()
for cat_key in ['left', 'center-left', 'center', 'center-right', 'right', 'libertarian', 'gov']:
    c, m, lbl = cat_style[cat_key]
    if lbl not in seen:
        seen.add(lbl)
        legend_handles.append(Line2D([0], [0], marker=m, color='w', markerfacecolor=c,
                                     markeredgecolor='white', markersize=10, label=lbl))
ax.legend(handles=legend_handles, loc='upper left', fontsize=8, framealpha=0.92,
          title='Marker Legend', title_fontsize=9, borderpad=0.8, labelspacing=0.6)

ax.axhline(0, color='#cccccc', linewidth=0.8, linestyle='--')
ax.axvline(0, color='#cccccc', linewidth=0.8, linestyle='--')
ax.set_xlabel('← Left-Leaning                    Political Orientation                    Right-Leaning →', fontsize=11)
ax.set_ylabel('← Hostile to Subject         Sentiment Toward Sosa-Celis         Sympathetic →', fontsize=11)
ax.set_title('Media Outlet Positioning: Political Leaning vs. Sentiment (28 Sources)', pad=15)
ax.set_xlim(-3.5, 3.5); ax.set_ylim(-1.15, 1.15)
ax.text(-3.0, 1.02, 'Left + Sympathetic', fontsize=8, color='#999', style='italic')
ax.text(1.8, 1.02, 'Right + Sympathetic', fontsize=8, color='#999', style='italic')
ax.text(-3.0, -1.08, 'Left + Hostile', fontsize=8, color='#999', style='italic')
ax.text(2.0, -1.08, 'Right + Hostile', fontsize=8, color='#999', style='italic')
ax.text(0.5, -0.015, 'Codes [A1]–[A28] → Appendix A for rubric, scores & article links',
        transform=ax.transAxes, fontsize=8, color='#888888', style='italic', ha='center')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(f'{OUT}/chart_sentiment_scatter.png', dpi=150, bbox_inches='tight')
plt.close(); print("✓ Sentiment scatter (28 sources)")


# ═══════════════ CHART 3 — Combined Timeline + Narrative Alignment ═══════════════
# Note: This chart requires ARTICLES data from article_data.py
# If you have article_data.py in the same directory structure, it will load automatically.
# Otherwise, this chart will be skipped with a message.

try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(OUT)))
    from article_data import ARTICLES, OUTLET_X, OUTLET_CAT
    from collections import defaultdict

    # Government narrative alignment = (1 - y_sentiment) / 2  →  maps [-1,+1] to [1,0]
    def govt_alignment(y_sent):
        return max(0, min(1, (1 - y_sent) / 2))

    def broad_cat(outlet):
        x = OUTLET_X[outlet]
        cat = OUTLET_CAT[outlet]
        if cat == 'gov': return 'Gov'
        if cat == 'libertarian': return 'Libertarian'
        if cat == 'left': return 'Left'
        if cat in ('center-left',): return 'Center-Left'
        if cat in ('center', 'center-right'): return 'Center'
        if cat == 'right' and x >= 2.3: return 'Far-Right'
        if cat == 'right': return 'Right'
        return 'Center'

    EVENT_START = datetime(2026, 1, 14)

    traces = defaultdict(list)
    for outlet, aid, date, y, headline, url, scores in ARTICLES:
        if date < EVENT_START: continue
        bc = broad_cat(outlet)
        if bc == 'Gov': continue
        traces[bc].append((outlet, date, govt_alignment(y)))

    def build_latest_per_outlet_avg(points):
        """Given list of (outlet, date, alignment), return (dates, avgs) bucketed by day."""
        sorted_pts = sorted(points, key=lambda p: p[1])
        from collections import OrderedDict
        by_date = OrderedDict()
        for outlet, d, v in sorted_pts:
            if d not in by_date:
                by_date[d] = []
            by_date[d].append((outlet, v))
        dates_out, avgs_out = [], []
        latest = {}
        for d, articles in by_date.items():
            for outlet, v in articles:
                latest[outlet] = v
            avg = sum(latest.values()) / len(latest)
            dates_out.append(d)
            avgs_out.append(avg)
        return dates_out, avgs_out

    trace_styles = {
        'Far-Right':    ('v-',  '#800000', 2.5, 7),
        'Right':        ('o-',  RIGHT_C,   2.5, 7),
        'Center':       ('s--', CENTER_C,  2.0, 6),
        'Center-Left':  ('D--', '#4292c6', 2.0, 6),
        'Left':         ('D:',  LEFT_C,    2.0, 6),
        'Libertarian':  ('P-.', LIBERT_C,  2.0, 7),
    }
    trace_order = ['Far-Right', 'Right', 'Center', 'Center-Left', 'Left', 'Libertarian']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                    gridspec_kw={'height_ratios': [3, 2], 'hspace': 0.08})
    draw_timeline(ax1, fontsize=7, markersize=7)
    ax1.set_ylim(-5.8, 5.8); ax1.set_yticks([])
    ax1.set_title('Timeline & Alignment with Government Narrative (Article-Based)', pad=12, fontsize=14)
    for sp in ['top', 'right', 'left']: ax1.spines[sp].set_visible(False)
    ax1.legend(handles=legend_items, loc='lower left', fontsize=8, framealpha=0.9, ncol=2)

    for cat_name in trace_order:
        if cat_name not in traces: continue
        dates_t, avgs_t = build_latest_per_outlet_avg(traces[cat_name])
        fmt, col, lw, ms = trace_styles[cat_name]
        ax2.plot(dates_t, avgs_t, fmt, color=col, linewidth=lw, markersize=ms, label=cat_name, alpha=0.85)

    for date, label, side, ckey in events:
        if date >= datetime(2026, 1, 14):
            ax2.axvline(date, color='#dddddd', linewidth=0.8, linestyle=':', zorder=0)

    ax2.set_ylabel('Alignment with\nGovt Narrative', fontsize=10)
    ax2.set_ylim(-0.05, 1.1)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax2.set_xlim(*EVENT_XLIM)
    ax1.set_xlim(*EVENT_XLIM)
    ax2.legend(loc='upper right', fontsize=8, framealpha=0.9, ncol=2)
    ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
    fig.savefig(f'{OUT}/chart_combined_timeline_shift.png', dpi=150, bbox_inches='tight')
    plt.close(); print("✓ Combined timeline+alignment (article-based)")
except Exception as e:
    print(f"⚠ Chart 3 (combined timeline) skipped — article_data.py not found: {e}")


# ═══════════════ CHART 4 — Coverage Volume (round pie) ═══════════════
fig, ax = plt.subplots(figsize=(8, 8))
explode = (0.02,)*len(pie_sizes)
wedges, texts, autotexts = ax.pie(pie_sizes, explode=explode, labels=pie_labels, colors=pie_colors,
                                   autopct='%1.0f%%', startangle=140,
                                   textprops={'fontsize': 9}, pctdistance=0.78)
for t in autotexts:
    t.set_fontsize(9); t.set_fontweight('bold'); t.set_color('white')
ax.set_aspect('equal')
ax.set_title('Estimated Coverage Volume by Source Type\n(See Appendix B for underlying data & article links)',
             pad=15, fontsize=13)
fig.tight_layout()
fig.savefig(f'{OUT}/chart_coverage_volume.png', dpi=150, bbox_inches='tight')
plt.close(); print("✓ Coverage volume")


# ═══════════════ CHART 5 — Framing bar chart ═══════════════
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(framing_categories))
w = 0.2
ax.bar(x-1.5*w, framing_accountability, w, label='LE Accountability', color='#e41a1c', alpha=0.85)
ax.bar(x-0.5*w, framing_immigrant_sympathy, w, label='Sympathy for Subjects', color='#377eb8', alpha=0.85)
ax.bar(x+0.5*w, framing_govt_credibility, w, label='Govt Credibility Concern', color='#4daf4a', alpha=0.85)
ax.bar(x+1.5*w, framing_civil_liberties, w, label='Civil Liberties Emphasis', color='#ff7f00', alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(framing_categories, fontweight='bold', fontsize=9)
ax.set_ylabel('Emphasis Level (0–1)')
ax.set_title('Narrative Framing Emphasis by Political Category', pad=15)
ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
ax.set_ylim(0, 1.1)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig(f'{OUT}/chart_framing.png', dpi=150, bbox_inches='tight')
plt.close(); print("✓ Framing")

print("\n✅ All charts generated.")
