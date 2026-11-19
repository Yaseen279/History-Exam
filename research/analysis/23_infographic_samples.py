"""Sample infographics (shape-based charts) in the Green template colours. Usage: python3 23_infographic_samples.py <out dir>"""
import sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, FancyArrowPatch, Polygon, Rectangle
from matplotlib import font_manager as fm
OUT = sys.argv[1]
PALETTE = sys.argv[2] if len(sys.argv) > 2 else 'green'
import glob, os
for f in glob.glob(os.path.expanduser('~/.fonts/static/*.ttf')): fm.fontManager.addfont(f)
if PALETTE == 'slate':   # Slidesgo template: navy highlight on blue-grey, DM Sans
    FONT = 'DMSansStatic'
    MAIN, ACC, P1, P2, P3, INK = '#445F73', '#0E2A47', '#7D95A8', '#A9BED0', '#D6E3EE', '#505050'
else:
    FONT = 'Carlito' if any('Carlito' in f.name for f in fm.fontManager.ttflist) else 'DejaVu Sans'
    MAIN, ACC, P1, P2, P3, INK = '#1E4D3A', '#C8921B', '#4F7F69', '#8DB3A0', '#C9DDD2', '#1D2230'
plt.rcParams['font.family'] = FONT

def canvas(w=10, h=6.2):
    f, a = plt.subplots(figsize=(w, h), dpi=200); a.set_xlim(0, w); a.set_ylim(0, h); a.axis('off'); a.set_aspect('equal'); return f, a
def save(f, n): f.savefig(f'{OUT}/{n}.png', dpi=200, bbox_inches='tight', facecolor='white', pad_inches=0.15); plt.close(f); print('wrote', n)

# ---------------------------------------------------------------- 1. phone with app tiles
f, a = canvas(10, 6.4)
a.add_patch(FancyBboxPatch((3.3, 0.25), 3.4, 5.9, boxstyle='round,pad=0,rounding_size=0.45', fc=MAIN, ec='none'))
a.add_patch(FancyBboxPatch((3.5, 0.75), 3.0, 5.0, boxstyle='round,pad=0,rounding_size=0.12', fc='#F4F8F5', ec='none'))
a.add_patch(FancyBboxPatch((4.55, 5.88), 0.9, 0.1, boxstyle='round,pad=0,rounding_size=0.05', fc=P2, ec='none'))
a.add_patch(Circle((5, 0.48), 0.14, fc=P2, ec='none'))
tiles = [('AI chatbots', 88.7, ACC, 'ai'), ('Search engines', 56.3, P1, 'search'), ('Medical platforms', 18.3, P2, 'med'), ('Social media', 10.7, P3, 'social')]
pos = [(3.72, 3.3), (5.12, 3.3), (3.72, 1.0), (5.12, 1.0)]
for (lab, v, c, ic), (x, y) in zip(tiles, pos):
    a.add_patch(FancyBboxPatch((x, y + 0.75), 1.16, 1.16, boxstyle='round,pad=0,rounding_size=0.22', fc=c, ec='none'))
    cx, cy = x + 0.58, y + 1.33
    if ic == 'ai':
        a.add_patch(FancyBboxPatch((cx - .34, cy - .18), .68, .45, boxstyle='round,pad=0,rounding_size=0.1', fc='white', ec='none'))
        a.add_patch(Polygon([(cx - .2, cy - .18), (cx - .3, cy - .36), (cx - .02, cy - .18)], fc='white', ec='none'))
        for dx in (-.16, 0, .16): a.add_patch(Circle((cx + dx, cy + .05), .045, fc=c, ec='none'))
    elif ic == 'search':
        a.add_patch(Circle((cx - .06, cy + .07), .22, fc='none', ec='white', lw=4)); a.plot([cx + .09, cx + .3], [cy - .09, cy - .3], color='white', lw=5, solid_capstyle='round')
    elif ic == 'med':
        a.add_patch(Rectangle((cx - .09, cy - .3), .18, .6, fc='white', ec='none')); a.add_patch(Rectangle((cx - .3, cy - .09), .6, .18, fc='white', ec='none'))
    else:
        for dx, s in ((-.17, .8), (.17, .8), (0, 1)):
            a.add_patch(Circle((cx + dx, cy + .12 * s), .09 * s, fc='white', ec='none')); a.add_patch(Wedge((cx + dx, cy - .22), .2 * s, 0, 180, fc='white', ec='none'))
    a.text(x + 0.58, y + 0.5, f'{v}%', ha='center', va='center', fontsize=17, fontweight='bold', color=ACC if c == ACC else MAIN)
    a.text(x + 0.58, y + 0.18, lab, ha='center', va='center', fontsize=9.5, color=INK)
a.text(0.1, 4.9, 'AI chatbots', fontsize=26, fontweight='bold', color=ACC)
a.text(0.1, 4.35, 'were the most used', fontsize=17, color=MAIN)
a.text(0.1, 3.9, 'source of health', fontsize=17, color=MAIN)
a.text(0.1, 3.45, 'information', fontsize=17, color=MAIN)
a.text(0.1, 2.4, 'ChatGPT 59.3%\nGemini 23.7%', fontsize=14, color=INK, linespacing=1.6)
a.text(7.0, 4.6, '88.7%', fontsize=40, fontweight='bold', color=ACC)
a.text(7.05, 4.1, 'used AI chatbots', fontsize=14, color=INK)
a.text(7.05, 3.1, 'vs 56.3%', fontsize=22, fontweight='bold', color=P1)
a.text(7.05, 2.7, 'used search engines', fontsize=14, color=INK)
save(f, 'sample1_phone_tools')

# ---------------------------------------------------------------- 2. vicious circle of the CSS-12 dimensions
f, a = canvas(10, 6.4)
cx, cy, R = 5, 3.15, 2.05
segs = [('Excessiveness', 'searching a lot', 0.46, 98, ACC), ('Distress', 'feeling worse after', 0.45, 8, ACC), ('Reassurance seeking', 'going to the doctor', 0.24, 278, P2), ('Compulsion', 'disrupts daily life', 0.25, 188, P2)]
import numpy as np
for (n, d, r, st, c) in segs:   # each arc covers its own quadrant; travel is clockwise, so the head sits at the start angle
    a.add_patch(Wedge((cx, cy), R, st + 6, st + 74, width=0.42, fc=c, ec='none'))
    t = np.deg2rad(st + 6); rm = R - .21; x1, y1 = cx + rm * np.cos(t), cy + rm * np.sin(t)
    nx, ny = np.cos(t), np.sin(t); tx, ty = np.sin(t), -np.cos(t)
    a.add_patch(Polygon([(x1 + .36 * nx, y1 + .36 * ny), (x1 - .36 * nx, y1 - .36 * ny), (x1 + .4 * tx, y1 + .4 * ty)], fc=c, ec='none'))
lab = {98: (cx - R - 0.2, cy + R - .25, 'right'), 8: (cx + R + 0.2, cy + R - .25, 'left'), 278: (cx + R + 0.2, cy - R + .55, 'left'), 188: (cx - R - 0.2, cy - R + .55, 'right')}
for (n, d, r, ang, c) in segs:
    x, y, ha = lab[ang]; hi = c == ACC
    a.text(x, y, n, ha=ha, fontsize=16, fontweight='bold', color=MAIN)
    a.text(x, y - .38, d, ha=ha, fontsize=12, color=INK)
    a.text(x, y - .95, f'r = {r:.2f}', ha=ha, fontsize=24 if hi else 18, fontweight='bold', color=ACC if hi else P1)
a.text(cx, cy + .3, 'Health', ha='center', fontsize=17, fontweight='bold', color=MAIN)
a.text(cx, cy - .12, 'anxiety', ha='center', fontsize=17, fontweight='bold', color=MAIN)
a.text(cx, cy - .6, 'overall r = 0.47', ha='center', fontsize=12, color=INK)
save(f, 'sample2_cycle_dimensions')

# ---------------------------------------------------------------- 3. one in five (ten people)
f, a = canvas(10, 4.4)
def person(x, y, c, s=1):
    a.add_patch(Circle((x, y + 1.55 * s), .3 * s, fc=c, ec='none'))
    a.add_patch(FancyBboxPatch((x - .38 * s, y), .76 * s, 1.1 * s, boxstyle=f'round,pad=0,rounding_size={.3*s}', fc=c, ec='none'))
for i in range(10): person(0.55 + i * 0.95, 1.05, ACC if i < 2 else P3, 0.95)
a.text(0.1, 3.75, '19.0%', fontsize=40, fontweight='bold', color=ACC)
a.text(2.55, 3.95, 'about 1 in 5 participants had elevated health anxiety', fontsize=17, color=MAIN)
a.text(2.55, 3.55, 'SHAI-14 ≥ 18 · a screening result, not a diagnosis · 95% CI 15.0–23.8%', fontsize=12, color=INK)
a.text(0.1, 0.35, '7.3% at a cut-off of 22   ·   0.7% at 29', fontsize=12, color=P1)
save(f, 'sample3_one_in_five')

# ---------------------------------------------------------------- 4. the patient's path after searching
f, a = canvas(11.5, 6.2)
def box(x, y, w, h, t, c, tc='white', fs=15):
    a.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.2', fc=c, ec='none')); a.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, fontweight='bold', color=tc)
box(0.1, 2.7, 1.7, 0.85, 'Symptom', MAIN)
box(2.3, 2.7, 1.9, 0.85, 'Search online\nor ask an AI', MAIN, fs=13)
a.add_patch(FancyArrowPatch((1.8, 3.12), (2.3, 3.12), arrowstyle='-|>', mutation_scale=22, color=MAIN, lw=3))
outs = [('Delayed care: felt reassured', 34.7, ACC), ('Ignored the symptom', 30.0, P2), ('Visited several doctors', 25.3, P2), ('Sought urgent care', 22.0, P2)]
ys = [5.0, 3.75, 2.5, 1.25]
for (t, v, c), y in zip(outs, ys):
    a.add_patch(FancyArrowPatch((4.2, 3.12), (5.2, y + .35), connectionstyle='arc3,rad=0', arrowstyle='-', color=c, lw=2 + v / 4, capstyle='round'))
    a.add_patch(FancyBboxPatch((5.2, y), 3.65, 0.7, boxstyle='round,pad=0,rounding_size=0.15', fc=c, ec='none'))
    a.text(5.35, y + .35, t, va='center', fontsize=12.5, fontweight='bold', color='white' if c == ACC else MAIN)
    a.text(9.0, y + .35, f'{v}%', va='center', fontsize=22 if c == ACC else 17, fontweight='bold', color=ACC if c == ACC else P1)
a.add_patch(FancyBboxPatch((9.15, 0.1), 2.25, 1.05, boxstyle='round,pad=0,rounding_size=0.15', fc='#F4F8F5', ec=MAIN, lw=1.5))
a.text(10.27, 0.8, 'At the doctor', ha='center', fontsize=11, color=INK)
a.text(10.27, 0.33, 'never told: 31.7%', ha='center', fontsize=13, fontweight='bold', color=ACC)
save(f, 'sample4_path_after_search')
