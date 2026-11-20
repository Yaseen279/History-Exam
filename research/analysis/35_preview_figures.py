"""Two candidate pictures: the health-anxiety cycle (slide 4) and a phone showing the online form (Methods divider).
Usage: python3 35_preview_figures.py <out dir>"""
import sys, glob, os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, Polygon, Rectangle
from matplotlib import font_manager as fm
for f in glob.glob(os.path.expanduser('~/.fonts/static/*.ttf')): fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'DMSansStatic'
NAVY, SLATE, STEEL, LIGHT, INK = '#0E2A47', '#445F73', '#7D95A8', '#C2D6E7', '#1D2230'
OUT = sys.argv[1]

# health-anxiety cycle (cognitive-behavioural model), portrait to fit the 2.75 x 3.55 in frame
f, a = plt.subplots(figsize=(2.75, 3.55), dpi=300); a.set_xlim(0, 2.75); a.set_ylim(0, 3.55); a.axis('off')
a.add_patch(Rectangle((0, 0), 2.75, 3.55, fc='white', ec='none'))
a.text(1.375, 3.36, 'THE HEALTH-ANXIETY CYCLE', ha='center', fontsize=8.2, fontweight='bold', color=NAVY)
cx, cy, R = 1.375, 1.7, 0.92
steps = ['Body\nsensation', 'Misread as\nserious illness', 'Worry\n(health anxiety)', 'Checking,\nsearching,\nreassurance', 'Short relief']
ang = [90, 18, -54, -126, 162]
for k, (t, g) in enumerate(zip(steps, ang)):
    t0 = np.deg2rad(g); x, y = cx + R * np.cos(t0), cy + R * np.sin(t0)
    a.add_patch(FancyBboxPatch((x - 0.42, y - 0.2), 0.84, 0.4, boxstyle='round,pad=0,rounding_size=0.07', fc=NAVY if k in (2, 3) else SLATE, ec='none', zorder=3))
    a.text(x, y, t, ha='center', va='center', fontsize=5.6, color='white', fontweight='bold', zorder=4, linespacing=1.05)
    # arrow to the next step, along the circle
    g2 = ang[(k + 1) % 5]
    while g2 >= g: g2 -= 360
    th = np.deg2rad(np.linspace(g - 20, g2 + 20, 24)); xs, ys = cx + R * np.cos(th), cy + R * np.sin(th)
    a.plot(xs, ys, color=STEEL, lw=1.4, zorder=1)
    a.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-3], ys[-3]), arrowprops=dict(arrowstyle='-|>', color=STEEL, lw=1.4, mutation_scale=7), zorder=2)
a.text(cx, cy + 0.05, 'worry\nreturns', ha='center', va='center', fontsize=6.4, color=SLATE, style='italic')
a.text(1.375, 0.13, 'Cognitive-behavioural model (Salkovskis)', ha='center', fontsize=5.2, color=SLATE, style='italic')
f.savefig(f'{OUT}/ha_cycle.png', dpi=300, facecolor='white'); plt.close(f)

# phone showing the online questionnaire, portrait 2.89 x 4.16 in
f, a = plt.subplots(figsize=(2.89, 4.16), dpi=300); a.set_xlim(0, 2.89); a.set_ylim(0, 4.16); a.axis('off')
a.add_patch(Rectangle((0, 0), 2.89, 4.16, fc='#EEF2F6', ec='none'))
a.add_patch(FancyBboxPatch((0.47, 0.22), 1.95, 3.72, boxstyle='round,pad=0,rounding_size=0.25', fc=SLATE, ec='none'))
a.add_patch(FancyBboxPatch((0.58, 0.48), 1.73, 3.22, boxstyle='round,pad=0,rounding_size=0.06', fc='white', ec='none'))
a.add_patch(FancyBboxPatch((1.25, 3.79), 0.4, 0.05, boxstyle='round,pad=0,rounding_size=0.02', fc=LIGHT, ec='none'))
a.add_patch(Circle((1.445, 0.34), 0.07, fc=LIGHT, ec='none'))
a.add_patch(Rectangle((0.58, 3.28), 1.73, 0.42, fc=NAVY, ec='none'))
a.text(0.68, 3.49, 'Health searching survey', fontsize=6.6, color='white', fontweight='bold', va='center')
a.text(0.68, 3.14, 'Arabic · English', fontsize=5.4, color=SLATE, va='center')
y = 2.86
for lab, kind in (('Consent (aged 18 or older)', 'check'), ('Which tools do you use?', 'opts'), ('SHAI-14 · 14 items', 'scale'), ('CSS-12 · 12 items', 'scale')):
    a.text(0.68, y, lab, fontsize=5.0, color=INK, va='center')
    if kind == 'check':
        a.add_patch(Rectangle((2.08, y - 0.06), 0.12, 0.12, fc=NAVY, ec='none')); a.plot([2.105, 2.135, 2.18], [y, y - 0.03, y + 0.04], color='white', lw=1.1)
    elif kind == 'opts':
        for k in range(3): a.add_patch(Circle((0.74 + k * 0.32, y - 0.17), 0.04, fc='white', ec=STEEL, lw=0.8)); a.add_patch(Rectangle((0.8 + k * 0.32, y - 0.19), 0.17, 0.04, fc=LIGHT, ec='none'))
        a.add_patch(Circle((0.74, y - 0.17), 0.02, fc=NAVY, ec='none'))
    else:
        for k in range(5): a.add_patch(Circle((0.74 + k * 0.2, y - 0.17), 0.04, fc=NAVY if k == 2 else 'white', ec=STEEL, lw=0.8))
    y -= 0.5
a.add_patch(FancyBboxPatch((1.62, 0.62), 0.6, 0.2, boxstyle='round,pad=0,rounding_size=0.05', fc=NAVY, ec='none'))
a.text(1.92, 0.72, 'Submit', fontsize=5.6, color='white', ha='center', va='center', fontweight='bold')
a.text(0.68, 0.72, 'n = 300', fontsize=6, color=NAVY, va='center', fontweight='bold')
f.savefig(f'{OUT}/phone_form.png', dpi=300, facecolor='#EEF2F6'); plt.close(f)
print('figures written')
