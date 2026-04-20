#!/usr/bin/env python3
"""
Generate PDF report — Template.
Adapted from the working Sosa-Celis report to be generalized for any topic.

This PDF includes:
  - Title page with topic and date
  - Timeline of key events
  - Narrative framing analysis by political category
  - Charts (sentiment scatter, combined timeline+alignment, coverage volume, framing)
  - Public sentiment indicators
  - Methodology
  - Fact-check section with claim/evidence/verdict format
  - Appendix A: Sentiment scoring rubric and article-level data
  - Appendix B: Government narrative alignment data

INSTRUCTIONS: Update the CONFIGURATION section below with your topic-specific data,
then run this script. All PDF logic, styling, and structure remain unchanged.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
import os
import sys

# ════════════════════════════════════════════════════════════════════════════
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                        CONFIGURATION SECTION                             ║
# ║  Customize these values for your topic. Everything else is automatic.    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# ════════════════════════════════════════════════════════════════════════════

# Path to directory containing your article_data.py file
ARTICLE_DATA_DIR = "/sessions/bold-trusting-edison"

# Output directory for the PDF and supporting charts
OUT = "/sessions/bold-trusting-edison/mnt/2026-02-14 Missy Topics Research"

# PDF filename and title
TOPIC_TITLE = "The Story of Julio Cesar Sosa-Celis"
REPORT_DATE = "February 14, 2026"
TOPIC_WINDOW = "December 2025 – February 2026"
PDF_FILENAME = "Sosa-Celis_Media_Coverage_Report.pdf"

# Executive Summary — brief overview of the topic and its significance
EXECUTIVE_SUMMARY = """
The story of Julio Cesar Sosa-Celis — a 24-year-old Venezuelan man shot in the leg by an ICE agent
in Minneapolis on January 14, 2026 — became a flashpoint in the national debate over immigration
enforcement after video evidence contradicted sworn officer testimony, leading to dismissed charges
and a federal perjury investigation. The case is embedded in the larger context of Operation Metro Surge,
which also produced two fatal shootings of U.S. citizens (Renée Good and Alex Pretti), sparking
nationwide protests and a rare fracture in conservative media's alignment with the government narrative.
"""

# Timeline events: (date_str, event_description)
TIMELINE_EVENTS = [
    ['Dec 1, 2025', 'Operation Metro Surge launched; thousands of agents deployed'],
    ['Jan 7, 2026',  'Renée Good, 37, U.S. citizen, fatally shot by ICE agent'],
    ['Jan 14, 2026', 'Sosa-Celis shot in the thigh during ICE traffic stop'],
    ['Jan 15, 2026', 'DHS labels all three men "violent criminal illegal aliens"'],
    ['Jan 16, 2026', 'Bystander videos emerge contradicting official account'],
    ['Jan 24, 2026', 'Alex Pretti, 37, VA nurse, U.S. citizen, fatally shot'],
    ['Jan 27, 2026', 'Conservative outlets (WSJ, NY Post, Free Press) break from govt narrative'],
    ['Feb 5, 2026',  'Sosa-Celis\'s partner speaks publicly'],
    ['Feb 13, 2026', 'ICE Director acknowledges "untruthful statements" under oath'],
    ['Feb 14, 2026', 'All charges dismissed with prejudice; perjury probe opened'],
]

# Narrative framing sections: (title, body_text)
NARRATIVE_SECTIONS = [
    ("The Right / Conservative",
     "<b>Initial (Jan 14–23):</b> Sosa-Celis presented as illegal alien who attacked officer. DHS language adopted "
     "uncritically by Daily Wire, Federalist, National Review, OANN. Sentimental register: <i>indignation on behalf "
     "of law enforcement</i>. <b>Far-right</b> (OANN, DW, Federalist) maintained this longer. "
     "<b>Shift (Jan 24+):</b> Pretti killing fractured frame. WSJ/NY Post editorials broke. Fox reported perjury "
     "probe without defending officers. NR/DW still foregrounded immigration status."),
    ("The Left / Progressive",
     "Sosa-Celis framed as victim of state violence from day one. Daily Beast: "How a Solitary Bullet Hole Blew "
     "Apart ICE's Web of Lies." Salon ran three pieces. Common Dreams called for ICE abolition. "
     "Register: <i>moral outrage and solidarity</i>. Third man's TX transfer framed as witness tampering."),
    ("The Center / Mainstream",
     "AP, CBS, NBC, ABC presented competing accounts. Shifted toward skepticism as evidence mounted. "
     "Register: <i>institutional concern</i> — procedural, detached, focused on credibility of institutions."),
    ("The Libertarian",
     "Reason analyzed use-of-force policy. Cato: only 5% of detainees have violent convictions. "
     "Register: <i>alarm about government overreach</i>. Gun-rights angle created common cause with progressives."),
    ("The Localist / Minnesota",
     "Sahan Journal centered community impact. MPR interviewed partner Indriany. "
     "Register: <i>community under siege</i>. MN chief judge excoriating ICE for ignoring 90+ court orders."),
]

# Public sentiment indicators: (indicator, finding, source)
PUBLIC_SENTIMENT_DATA = [
    ['Video awareness', '82% of voters saw Good shooting video', 'Quinnipiac'],
    ['Social media reach', '70% of Americans saw videos on social media', 'YouGov'],
    ['ICE approval', 'Deeply divided; majority disapprove; Rs support expanded role', 'Multiple'],
    ['Celebrity activism', 'Springsteen, Billie Eilish, Pedro Pascal, Jamie Lee Curtis', 'Multiple'],
    ['Protest spread', 'Chicago, NYC, LA, SF, Seattle, DC + Minneapolis', 'NBC/CBS/AP'],
    ['Sports crossover', 'NBA\'s Anthony Edwards criticized for weak response', 'Yahoo Sports'],
]

# Fact-check claims: (title, claim_text, evidence_text, verdict_text, source_aids_list)
# source_aids_list should contain article IDs as they appear in article_data.py
FACT_CHECKS = [
    ("'Sosa-Celis was armed'",
     "DHS described men who "violently beat a law enforcement officer with weapons." Multiple right-leaning "
     "outlets reported men wielded a snow shovel and broom handle as weapons.",
     "No evidence indicates Sosa-Celis carried a firearm or weapon. The "weapons" were household items at "
     "the residence. Photographic evidence showed the officer fired <i>through the front door</i> — "
     "inconsistent with a close-quarters street attack. Surveillance video did not corroborate the assault narrative.",
     "✘ FALSE — Sosa-Celis was unarmed. Household items retroactively characterized as weapons.",
     ['A34a', 'A15a', 'A22a', 'A31a', 'A27a']),
    ("'He attacked / ambushed ICE agents'",
     "Sec. Noem: "an attempted murder of federal law enforcement." Federalist: "Propaganda Press Glosses Over "
     "Attack On ICE Agent." Officers claimed they were beaten while on the ground.",
     "Contradicted by: (1) city surveillance video; (2) two eyewitnesses within 10 feet; (3) neighbor testimony; "
     "(4) bullet hole through front door showing officer fired at retreating person. Prosecutors cited evidence "
     ""materially inconsistent" with sworn testimony. All charges dismissed with prejudice. Two ICE officers "
     "now under federal perjury investigation.",
     "✘ FALSE — Assault narrative contradicted by video, physical evidence, and multiple witnesses.",
     ['A15b', 'A13a', 'A4b', 'A5a', 'A5b', 'A31a', 'A31b']),
    ("'He was a violent criminal'",
     "DHS headline: "Three Violent Criminal Illegal Aliens." National Review: "brutal shovel beating." "
     "Adopted by Daily Wire, Federalist, OANN.",
     "Actual criminal record: <b>one conviction for driving without a license</b> and two arrests for giving "
     "a false name. Both minor, non-violent offenses. No violent criminal history in any court filing or investigation.",
     "✘ FALSE — Only conviction was a traffic offense.",
     ['A15a', 'A34a', 'A27a', 'A30a', 'A31a', 'A33a']),
    ("'He was an illegal alien subject to deportation'",
     "DHS consistently used "illegal alien" and characterized the encounter as lawful enforcement.",
     "Entered US illegally Aug 2022 but subsequently <b>granted Temporary Protected Status (TPS)</b>, providing "
     "legal protection from deportation. Not under active deportation order at time of shooting. Working as "
     "DoorDash driver with a young son.",
     "⚠ MISLEADING — Original entry unlawful but held legal TPS status at time of encounter.",
     ['A22a', 'A34a', 'A18a']),
    ("'Venezuelan gang member / Tren de Aragua'",
     "Operation framed as targeting TdA gang members. Some outlets grouped Sosa-Celis with gang-connected individuals.",
     "No evidence in any filing links Sosa-Celis to TdA or any gang. Working as delivery driver, no violent history, "
     "had family. FBI revealed operation was based on <b>mistaken identity</b> — agents sought a different "
     "individual (Joffre Stalin Paucar Barrera).",
     "✘ UNSUBSTANTIATED — No evidence of gang affiliation. Bystander in mistaken-identity operation.",
     ['A22a', 'A8b', 'A34a']),
    ("'The shooting was justified self-defense'",
     "Officer claimed he fired in self-defense while being ambushed, fearing for his life.",
     "FBI/DOJ investigation: (1) officer fired through closed door; (2) Sosa-Celis retreating into home when shot; "
     "(3) video shows no active assault; (4) two officers provided "untruthful statements" under oath; "
     "(5) evidence "materially inconsistent" with assault allegations. Non-fatal thigh wound. No body cameras deployed.",
     "⚠ EVIDENCE CONTRADICTS — Physical evidence, video, and witnesses inconsistent with self-defense. "
     "Perjury probe opened.",
     ['A9b', 'A10a', 'A8b', 'A20b']),
]

# Fact-check summary table: (number, claim, verdict, key_evidence)
FACT_CHECK_SUMMARY = [
    ['1', 'Sosa-Celis was armed', '✘ False', 'No weapon found; bullet hole through door'],
    ['2', 'He attacked/ambushed agents', '✘ False', 'Video, witnesses, physical evidence contradict'],
    ['3', 'He was a violent criminal', '✘ False', 'Only conviction: driving without license'],
    ['4', 'He was an illegal alien', '⚠ Misleading', 'Held Temporary Protected Status'],
    ['5', 'Gang member / TdA', '✘ Unsubstantiated', 'No evidence; mistaken identity operation'],
    ['6', 'Shooting justified', '⚠ Contradicted', 'Fired through door; perjury probe opened'],
]

# Sentiment scoring rubric explanations
RUBRIC_CRITERIA = [
    ['Subject description', '"illegal alien," "criminal" in headline',
     'Name + nationality neutrally', 'Name only, "resident," humanizing detail'],
    ['Account primacy', 'Govt account leads, defense buried', 'Both accounts equal',
     'Defense/victim leads, govt challenged'],
    ['Emotional register', 'Indignation toward subject', 'Procedural, detached',
     'Outrage on behalf of subject'],
    ['Immigration status', 'Foregrounded in headline as framing', 'Mentioned in body only',
     'Omitted or de-emphasized'],
]

# Alignment formula interpretation table
ALIGNMENT_FORMULA = [
    ['+1.00 (max sympathetic)', '0.00', 'Fully opposed to govt narrative'],
    ['+0.50', '0.25', 'Mostly opposed'],
    ['0.00 (neutral)', '0.50', 'Neutral / balanced'],
    ['-0.50', '0.75', 'Mostly aligned'],
    ['-1.00 (max hostile)', '1.00', 'Fully aligned with govt narrative'],
]

# ════════════════════════════════════════════════════════════════════════════
# END CONFIGURATION — Below this line, no customization needed
# ════════════════════════════════════════════════════════════════════════════

# Import article data
sys.path.insert(0, ARTICLE_DATA_DIR)
try:
    from article_data import ARTICLES, OUTLET_X, OUTLET_CAT
except ImportError as e:
    print(f"ERROR: Could not import article_data from {ARTICLE_DATA_DIR}")
    print(f"Make sure article_data.py exists in that directory.")
    sys.exit(1)

PDF_PATH = f"{OUT}/{PDF_FILENAME}"

doc = SimpleDocTemplate(PDF_PATH, pagesize=letter,
    topMargin=0.6*inch, bottomMargin=0.6*inch, leftMargin=0.7*inch, rightMargin=0.7*inch)

styles = getSampleStyleSheet()
S = styles.add
S(ParagraphStyle('RT', parent=styles['Title'], fontSize=22, spaceAfter=6,
    textColor=HexColor('#1a1a2e'), fontName='Helvetica-Bold'))
S(ParagraphStyle('RS', parent=styles['Normal'], fontSize=12, spaceAfter=20,
    textColor=HexColor('#666'), alignment=TA_CENTER, fontName='Helvetica'))
S(ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, spaceBefore=18, spaceAfter=10,
    textColor=HexColor('#1a1a2e'), fontName='Helvetica-Bold', borderWidth=0))
S(ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceBefore=14, spaceAfter=6,
    textColor=HexColor('#333366'), fontName='Helvetica-Bold'))
S(ParagraphStyle('H3', parent=styles['Heading3'], fontSize=11, spaceBefore=10, spaceAfter=4,
    textColor=HexColor('#444488'), fontName='Helvetica-Bold'))
S(ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8,
    alignment=TA_JUSTIFY, fontName='Helvetica'))
S(ParagraphStyle('SN', parent=styles['Normal'], fontSize=8, leading=10,
    textColor=HexColor('#888'), fontName='Helvetica-Oblique'))
S(ParagraphStyle('TC', parent=styles['Normal'], fontSize=8.5, leading=11, fontName='Helvetica'))
S(ParagraphStyle('TH', parent=styles['Normal'], fontSize=9, leading=11,
    fontName='Helvetica-Bold', textColor=colors.white))
S(ParagraphStyle('AE', parent=styles['Normal'], fontSize=9, leading=12, spaceAfter=3, fontName='Helvetica'))

TS = TableStyle([
    ('BACKGROUND', (0,0), (-1,0), HexColor('#1a1a2e')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.5, HexColor('#ccc')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, HexColor('#f5f5ff')]),
    ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
])

def tbl(hdrs, rows, cw):
    """Build a styled table."""
    d = [[Paragraph(h, styles['TH']) for h in hdrs]]
    for r in rows: d.append([Paragraph(str(c), styles['TC']) for c in r])
    t = Table(d, colWidths=cw); t.setStyle(TS); return t

def img(n, w, h):
    """Load image if it exists, else return spacer."""
    p = f"{OUT}/{n}"
    return Image(p, width=w, height=h) if os.path.exists(p) else Spacer(1, 12)

st = []

# ── Title Page ──
st.append(Spacer(1, 1.2*inch))
st.append(Paragraph("Media Coverage &amp; Sentiment Analysis", styles['RT']))
st.append(Paragraph(TOPIC_TITLE, styles['RT']))
st.append(Spacer(1, 10))
st.append(Paragraph(f"Report Date: {REPORT_DATE} | Topic Window: {TOPIC_WINDOW}", styles['RS']))
st.append(Spacer(1, 20))
st.append(Paragraph("Executive Summary", styles['H1']))
st.append(Paragraph(EXECUTIVE_SUMMARY, styles['B']))
st.append(PageBreak())

# ── Timeline ──
st.append(Paragraph("Timeline of Key Events", styles['H1']))
st.append(img('chart_timeline.png', 6.8*inch, 3.8*inch))
st.append(Spacer(1, 4))
st.append(tbl(['Date', 'Event'], TIMELINE_EVENTS, [1*inch, 5.6*inch]))
st.append(PageBreak())

# ── Sentiment & Narrative ──
st.append(Paragraph("Sentiment &amp; Narrative Framing", styles['H1']))
for title, body in NARRATIVE_SECTIONS:
    st.append(Paragraph(title, styles['H2']))
    st.append(Paragraph(body, styles['B']))
st.append(PageBreak())

# ── Sentiment Map & Shift Over Time ──
st.append(Paragraph("Sentiment Map &amp; Shift Over Time", styles['H1']))
st.append(img('chart_sentiment_shift.png', 6.5*inch, 4.0*inch))
st.append(Paragraph(
    "Each point = one article (52 total). <b>Size and opacity encode recency</b> — smaller/faded = earlier, "
    "larger/bold = more recent. Arrows trace chronological shift within each outlet. "
    "<b>Marker shapes:</b> ■ squares = Left/Far Left, ◆ diamonds = Center-Left &amp; Center-Right, "
    "● circles = Center, ▲ triangles = Right/Far Right, ✙ plus = Libertarian, ✕ X = Government. "
    "All 52 articles with dates, scores, and links in <b>Appendix A</b>.", styles['B']))
st.append(Paragraph(
    "Key findings: strong diagonal (left = sympathetic, right = hostile), but arrows show every multi-article outlet "
    "shifted upward over time. Fox News moved -0.50 → -0.05. Daily Beast +0.75 → +0.95. "
    "Far-right outlets shifted up but stayed hostile. Left barely moved (skeptical from day one). "
    "DHS (single point, bottom-right) never shifted.", styles['B']))
st.append(PageBreak())

# ── Combined Timeline + Govt Narrative Alignment ──
st.append(Paragraph("Timeline &amp; Alignment with Government Narrative", styles['H1']))
st.append(img('chart_combined_timeline_shift.png', 6.8*inch, 4.2*inch))
st.append(Paragraph(
    "Bottom panel: each point marks an article publication date. At each point, the y-value is the average "
    "alignment across all outlets in that category, using <b>only each outlet's most recent article</b> "
    "(computed as (1 – sentiment) / 2, where hostile-to-subject = high alignment). "
    "When an outlet publishes a new article, it replaces the old one in the group average. "
    "Right dropped from ~0.81 to ~0.55 as Fox News and Washington Times softened. "
    "Far-Right fell from ~0.95 to ~0.77 but remained above all other categories. "
    "See <b>Appendix B</b> for the per-article alignment scores underlying these traces.", styles['B']))

# ── Coverage Volume ──
st.append(Paragraph("Coverage Volume by Source Type", styles['H1']))
st.append(img('chart_coverage_volume.png', 4.5*inch, 4.5*inch))
st.append(Paragraph("See <b>Appendix B</b> for underlying data and article links.", styles['B']))
st.append(PageBreak())

# ── Framing ──
st.append(Paragraph("Narrative Framing by Political Category", styles['H1']))
st.append(img('chart_framing.png', 6.5*inch, 3.5*inch))
st.append(Paragraph(
    "Now includes <b>Far Right</b> as separate category. Far-right scored near zero on sympathy and civil "
    "liberties but maintained some govt-credibility concern after the perjury probe.", styles['B']))

# ── Public Sentiment ──
st.append(Paragraph("Public Sentiment Indicators", styles['H1']))
st.append(tbl(['Indicator', 'Finding', 'Source'], PUBLIC_SENTIMENT_DATA, [1.2*inch, 3.5*inch, 1.6*inch]))
st.append(PageBreak())

# ── Methodology ──
st.append(Paragraph("Methodology", styles['H1']))
st.append(Paragraph(
    "Compiled Feb 14, 2026 via web search across 28 outlets. Political-leaning baselines from AllSides and "
    "Ad Fontes Media, adjusted ±0.3 for story-specific framing. Sentiment follows explicit rubric in Appendix A. "
    "Coverage volume approximate. All scores are documented qualitative judgment, not algorithmic.", styles['SN']))
st.append(PageBreak())

# ── Fact-Check Section ──
st.append(Paragraph("Fact-Check: Key Claims in Media Coverage", styles['H1']))
st.append(Paragraph(
    "A significant feature of this story is the gap between assertions made in early coverage (often parroting "
    "DHS press releases) and what subsequent evidence revealed. Below, key claims are evaluated against the "
    "evidentiary record.", styles['B']))

# Build URL lookup from article data
article_url = {}
for _o, _aid, _d, _y, _hl, _url, _s in ARTICLES:
    article_url[_aid] = _url

def aid_link(aid):
    """Return a clickable article ID link."""
    url = article_url.get(aid, '')
    if url:
        return f'<a href="{url}" color="#1a0dab">{aid}</a>'
    return aid

def aid_links(aids):
    """Return comma-separated clickable article ID links."""
    return ', '.join(aid_link(a) for a in aids)

# Render fact-checks
for title, claim_text, evidence_text, verdict_text, source_aids in FACT_CHECKS:
    st.append(Paragraph(f"Claim: {title}", styles['H2']))
    st.append(Paragraph(f"<b>As stated:</b> {claim_text}", styles['B']))
    st.append(Paragraph(f"<b>Evidence:</b> {evidence_text}", styles['B']))
    st.append(Paragraph(f"<b>Verdict:</b> {verdict_text}", styles['B']))
    st.append(Paragraph(f"<i>Sources: {aid_links(source_aids)}</i>", styles['SN']))
    st.append(Spacer(1, 6))

# Summary table
st.append(Paragraph("Fact-Check Summary", styles['H2']))
st.append(tbl(
    ['#', 'Claim', 'Verdict', 'Key Evidence'],
    FACT_CHECK_SUMMARY,
    [0.3*inch, 1.6*inch, 1.1*inch, 3.3*inch]
))
st.append(PageBreak())

# ══════════ APPENDIX A — Article-Level ══════════
st.append(Paragraph("Appendix A: Sentiment Scoring Rubric &amp; Source Articles", styles['H1']))
st.append(Paragraph("Scoring Rubric", styles['H2']))
st.append(Paragraph(
    "<b>Political Orientation (x-axis, -3 to +3):</b> AllSides/Ad Fontes baseline ±0.3 for story framing.", styles['B']))
st.append(Paragraph(
    "<b>Sentiment (y-axis, -1 to +1):</b> Sum of four criteria scored -0.25 to +0.25 each:", styles['B']))
st.append(tbl(
    ['Criterion', '-0.25 (hostile)', '0 (neutral)', '+0.25 (sympathetic)'],
    RUBRIC_CRITERIA,
    [1.1*inch, 1.6*inch, 1.5*inch, 1.9*inch]
))
st.append(Spacer(1, 8))

# Article-level table from dataset
sorted_articles = sorted(ARTICLES, key=lambda a: (OUTLET_X[a[0]], a[2]))

st.append(Paragraph("Article-Level Scoring (52 Articles)", styles['H2']))
st.append(Paragraph(
    "Each row = one data point on the sentiment map. Sorted by political orientation (left to right), then date.", styles['B']))

# Split into chunks of ~13 articles per page
chunk_size = 13
for i in range(0, len(sorted_articles), chunk_size):
    chunk = sorted_articles[i:i+chunk_size]
    rows = []
    for outlet, aid, date, y, headline, url, scores in chunk:
        x = OUTLET_X[outlet]
        date_str = date.strftime("%b %d")
        hl = headline if len(headline) <= 50 else headline[:47] + "..."
        if url:
            hl_linked = f'<a href="{url}" color="#1a0dab">{hl}</a>'
        else:
            hl_linked = hl
        rows.append([aid, date_str, outlet, f"{x:+.1f}", f"{y:+.2f}", scores, hl_linked])
    st.append(tbl(
        ['ID', 'Date', 'Outlet', 'x', 'y', 'Scores', 'Headline'],
        rows,
        [0.4*inch, 0.5*inch, 1.0*inch, 0.35*inch, 0.4*inch, 1.3*inch, 2.4*inch]
    ))
    st.append(Spacer(1, 4))

st.append(PageBreak())

# ══════════ APPENDIX B — Government Narrative Alignment Basis ══════════
st.append(Paragraph("Appendix B: Government Narrative Alignment — Basis Data", styles['H1']))
st.append(Paragraph(
    "This appendix provides the per-article data underlying the "Alignment with Government Narrative" "
    "chart. Alignment is calculated as <b>(1 – sentiment) / 2</b>, mapping the -1 to +1 sentiment "
    "scale onto a 0–1 alignment scale where 1.0 = fully aligned with the DHS official account and "
    "0.0 = fully opposed. Each trace on the chart uses <b>only each outlet's most recent article</b> to "
    "compute the group average — when an outlet publishes a new article, it replaces the old one. "
    "A new point is plotted each time any article in the category is published.", styles['B']))

st.append(Paragraph("Formula &amp; Interpretation", styles['H2']))
st.append(tbl(
    ['Sentiment (y)', 'Alignment', 'Interpretation'],
    ALIGNMENT_FORMULA,
    [1.8*inch, 0.8*inch, 3.0*inch]
))
st.append(Spacer(1, 8))

# Build alignment data
def govt_align_pdf(y_sent):
    return max(0, min(1, (1 - y_sent) / 2))

def broad_cat_pdf(outlet):
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

from datetime import datetime
EVENT_START = datetime(2026, 1, 14)

align_rows = []
for outlet, aid, date, y, headline, url, scores in ARTICLES:
    if date < EVENT_START: continue
    bc = broad_cat_pdf(outlet)
    if bc == 'Gov': continue
    align_rows.append((date, aid, outlet, bc, y, govt_align_pdf(y), headline))
align_rows.sort(key=lambda r: (r[0], r[3]))

st.append(Paragraph("Per-Article Alignment Scores (Sorted by Date)", styles['H2']))

chunk_size = 18
for i in range(0, len(align_rows), chunk_size):
    chunk = align_rows[i:i+chunk_size]
    rows = []
    for date, aid, outlet, bc, y, alignment, headline in chunk:
        url = article_url.get(aid, '')
        aid_cell = f'<a href="{url}" color="#1a0dab">{aid}</a>' if url else aid
        rows.append([
            aid_cell,
            date.strftime("%b %d"),
            outlet,
            bc,
            f"{y:+.2f}",
            f"{alignment:.2f}",
        ])
    st.append(tbl(
        ['ID', 'Date', 'Outlet', 'Category', 'Sent.', 'Align.'],
        rows,
        [0.4*inch, 0.5*inch, 1.1*inch, 1.0*inch, 0.5*inch, 0.5*inch]
    ))
    st.append(Spacer(1, 4))

st.append(Spacer(1, 15))
st.append(Paragraph("Report generated for research purposes. All links accessible as of Feb 14, 2026.", styles['SN']))

doc.build(st)
print(f"✅ PDF saved: {PDF_PATH}")
