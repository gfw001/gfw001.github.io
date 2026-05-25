#!/usr/bin/env python3
"""
Generate innovation-cycles.svg for /blog/2026/mlsys.html

Two panels share a year-based x-axis (y-axis intentionally unlabeled):

  Pattern 1 - Hype waves (interest-over-time, peaks & troughs):
      1) NLP / Conversational AI Understanding   peak ~2019-2020
      2) Cloud Native                            peak ~2021-2022
      3) LLM / AI Native                          take-off late 2022, still climbing

  Pattern 2 - Adoption eras (flat, parallel segments, rising by time):
      1) 2019-2020  NLP                       (lowest)
      2) 2020-2022  Container & Serverless    (middle)
      3) 2023-now   LLM (ongoing)             (highest)

Pure stdlib, no third-party deps. Run:  python3 innovation_cycles.py
"""
import math

# ---- canvas -------------------------------------------------------------
W, H = 960, 640
L, R = 78, 720           # plot x range (leaves room for right-side labels)
Y0, Y1 = 2016.0, 2026.5  # year span on x-axis

def xpix(year):
    return L + (year - Y0) / (Y1 - Y0) * (R - L)

# panel vertical bands
TOP_T, TOP_B = 78, 300     # top panel (waves)
BOT_T, BOT_B = 372, 560    # bottom panel (flat eras)

def ytop(v):   # v in 0..1 -> pixel (0 at panel bottom)
    return TOP_B - v * (TOP_B - TOP_T)

def ybot(v):
    return BOT_B - v * (BOT_B - BOT_T)

# ---- curve models -------------------------------------------------------
def gauss(x, mu, sig, amp):
    return amp * math.exp(-((x - mu) ** 2) / (2 * sig ** 2))

def logistic(x, x0, k, amp):
    return amp / (1.0 + math.exp(-(x - x0) / k))

# NLP / Conversational AI: rises mid-2010s, peaks ~2019.3, long decline as it is
# absorbed into LLMs (small residual tail kept).
def nlp(x):
    return gauss(x, 2019.3, 1.7, 0.82) + 0.10 * math.exp(-((x - 2024) ** 2) / 8)

# Cloud Native (Kubernetes / containers / serverless): rises to ~2021.5, then
# plateaus -- it became the default substrate, so it stays level rather than
# declining on the right.
def cloud(x):
    if x <= 2021.5:
        return gauss(x, 2021.5, 1.8, 0.92)
    return 0.92

# LLM / AI Native: near-zero until late 2022, S-curve still climbing in 2026
def llm(x):
    return logistic(x, 2023.5, 0.55, 1.0)

def polyline_points(fn, step=0.05):
    pts = []
    x = Y0
    while x <= Y1 + 1e-9:
        pts.append((xpix(x), ytop(fn(x))))
        x += step
    return pts

def path_d(pts):
    d = "M {:.1f} {:.1f}".format(*pts[0])
    for p in pts[1:]:
        d += " L {:.1f} {:.1f}".format(*p)
    return d

# ---- colors -------------------------------------------------------------
C_NLP   = "#e8923c"   # warm orange
C_CLOUD = "#2f9e8f"   # teal
C_LLM   = "#5b6ee1"   # indigo
INK     = "#333333"
GRID    = "#e6e6e6"
AXIS    = "#999999"

svg = []
svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'font-family="Roboto, Helvetica, Arial, sans-serif" '
    f'role="img" aria-label="Three innovation cycles of the past decade">'
)
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')

# ---- title --------------------------------------------------------------
svg.append(f'<text x="{L}" y="40" font-size="20" font-weight="700" fill="{INK}">'
           f'Three innovation cycles of the past decade</text>')
svg.append(f'<text x="{L}" y="60" font-size="12.5" fill="#777">'
           f'x-axis: year &#183; y-axis: relative intensity (unlabeled)</text>')

# ---- shared x grid (year ticks) for both panels -------------------------
ticks = [2016, 2018, 2020, 2022, 2024, 2026]
for yr in ticks:
    x = xpix(yr)
    svg.append(f'<line x1="{x:.1f}" y1="{TOP_T}" x2="{x:.1f}" y2="{TOP_B}" stroke="{GRID}" stroke-width="1"/>')
    svg.append(f'<line x1="{x:.1f}" y1="{BOT_T}" x2="{x:.1f}" y2="{BOT_B}" stroke="{GRID}" stroke-width="1"/>')

# ======================= PANEL 1 : WAVES =================================
svg.append(f'<text x="{L}" y="{TOP_T-8}" font-size="13.5" font-weight="700" fill="{INK}">'
           f'Pattern 1 &#8212; Hype waves (interest over time, peaks &amp; troughs)</text>')
# baseline + y-axis (no ticks/numbers)
svg.append(f'<line x1="{L}" y1="{TOP_B}" x2="{R}" y2="{TOP_B}" stroke="{AXIS}" stroke-width="1.4"/>')
svg.append(f'<line x1="{L}" y1="{TOP_T-2}" x2="{L}" y2="{TOP_B}" stroke="{AXIS}" stroke-width="1.4"/>')

for fn, color, label in [(nlp, C_NLP, "NLP / Conversational AI"),
                         (cloud, C_CLOUD, "Cloud Native"),
                         (llm, C_LLM, "LLM / AI Native")]:
    pts = polyline_points(fn)
    svg.append(f'<path d="{path_d(pts)}" fill="none" stroke="{color}" stroke-width="2.6" '
               f'stroke-linejoin="round" stroke-linecap="round"/>')

# peak markers (evidence: approximate peak years)
peaks = [(2019.3, nlp(2019.3), C_NLP, "~2019–20"),
         (2021.5, cloud(2021.5), C_CLOUD, "~2021–22"),
         (2026.2, llm(2026.2), C_LLM, "rising")]
for yr, v, color, note in peaks:
    cx, cy = xpix(yr), ytop(v)
    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.4" fill="{color}"/>')
    svg.append(f'<text x="{cx:.1f}" y="{cy-8:.1f}" font-size="10.5" fill="{color}" '
               f'text-anchor="middle">{note}</text>')

# right-side legend for panel 1
ly = TOP_T + 14
for color, label in [(C_NLP, "NLP / Conversational AI"),
                     (C_CLOUD, "Cloud Native"),
                     (C_LLM, "LLM / AI Native")]:
    svg.append(f'<line x1="{R+14}" y1="{ly}" x2="{R+34}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
    svg.append(f'<text x="{R+40}" y="{ly+4}" font-size="11.5" fill="{INK}">{label}</text>')
    ly += 20

# ======================= PANEL 2 : FLAT ERAS =============================
svg.append(f'<text x="{L}" y="{BOT_T-8}" font-size="13.5" font-weight="700" fill="{INK}">'
           f'Pattern 2 &#8212; Adoption eras (flat, parallel, rising by time)</text>')
svg.append(f'<line x1="{L}" y1="{BOT_B}" x2="{R}" y2="{BOT_B}" stroke="{AXIS}" stroke-width="1.4"/>')
svg.append(f'<line x1="{L}" y1="{BOT_T-2}" x2="{L}" y2="{BOT_B}" stroke="{AXIS}" stroke-width="1.4"/>')

# (start, end, height0..1, color, label, ongoing?)
eras = [
    (2019.0, 2020.0, 0.26, C_NLP,   "NLP", False),
    (2020.0, 2022.0, 0.55, C_CLOUD, "Container &amp; Serverless", False),
    (2023.0, 2026.2, 0.88, C_LLM,   "LLM (ongoing)", True),
]
for x0, x1, h, color, label, ongoing in eras:
    y = ybot(h)
    xa, xb = xpix(x0), xpix(x1)
    # drop guides to baseline
    svg.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xa:.1f}" y2="{BOT_B}" stroke="{color}" '
               f'stroke-width="1" stroke-dasharray="3 3" opacity="0.5"/>')
    # the flat era line
    svg.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{color}" '
               f'stroke-width="5" stroke-linecap="round"/>')
    if ongoing:  # dashed continuation + arrow head
        svg.append(f'<line x1="{xb:.1f}" y1="{y:.1f}" x2="{xb+26:.1f}" y2="{y:.1f}" stroke="{color}" '
                   f'stroke-width="3" stroke-dasharray="5 4"/>')
        ah = xb + 26
        svg.append(f'<polygon points="{ah:.1f},{y-5:.1f} {ah+9:.1f},{y:.1f} {ah:.1f},{y+5:.1f}" fill="{color}"/>')
        lx = ah + 14
    else:
        lx = xb + 10
    # year range under the segment
    yr_txt = f"{int(x0)}–{int(x1)}" if not ongoing else f"{int(x0)}–now"
    svg.append(f'<text x="{(xa+xb)/2:.1f}" y="{y-9:.1f}" font-size="11" font-weight="600" '
               f'fill="{color}" text-anchor="middle">{label}</text>')
    svg.append(f'<text x="{lx:.1f}" y="{y+4:.1f}" font-size="10.5" fill="#777">{yr_txt}</text>')

# ---- year tick labels (shared, drawn under bottom panel) ----------------
for yr in ticks:
    x = xpix(yr)
    svg.append(f'<text x="{x:.1f}" y="{BOT_B+18}" font-size="11" fill="#666" '
               f'text-anchor="middle">{yr}</text>')

svg.append('</svg>')

out = "innovation-cycles.svg"
with open(out, "w") as f:
    f.write("\n".join(svg))
print("wrote", out)
