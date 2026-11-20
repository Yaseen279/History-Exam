"""Scatter plot (Figure 4) and forest plot (Figure 6) redrawn in the Slidesgo template colours.
Usage: python3 24_slidesgo_figures.py <data .sav> <out dir>"""
import sys, glob, os, numpy as np, pyreadstat, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in glob.glob(os.path.expanduser('~/.fonts/static/*.ttf')): fm.fontManager.addfont(f)
plt.rcParams.update({'font.family': 'DMSansStatic', 'axes.edgecolor': '#7D95A8', 'axes.labelcolor': '#505050', 'xtick.color': '#505050', 'ytick.color': '#505050'})
NAVY, SLATE, STEEL, LIGHT, INK = '#0E2A47', '#445F73', '#7D95A8', '#D6E3EE', '#505050'
d, _ = pyreadstat.read_sav(sys.argv[1]); OUT = sys.argv[2]
x, y = d.SHAI.astype(float).values, d.CSS.astype(float).values

# ---- scatter with regression line and 95% confidence band
f, a = plt.subplots(figsize=(6.4, 4.6), dpi=220)
rng = np.random.default_rng(1)
a.scatter(x + rng.uniform(-.25, .25, len(x)), y + rng.uniform(-.25, .25, len(y)), s=16, color=STEEL, alpha=.55, lw=0)
b1, b0 = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 100); n = len(x)
res = y - (b0 + b1 * x); s = np.sqrt((res ** 2).sum() / (n - 2)); se = s * np.sqrt(1 / n + (xs - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
a.fill_between(xs, b0 + b1 * xs - 1.97 * se, b0 + b1 * xs + 1.97 * se, color=LIGHT, alpha=.9, lw=0)
a.plot(xs, b0 + b1 * xs, color=NAVY, lw=2.6)
a.axvline(18, color=SLATE, ls=(0, (4, 3)), lw=1.2); a.text(18.4, 13, 'SHAI ≥ 18', color=SLATE, fontsize=9)
a.text(0.6, 56, f'r = 0.47 (95% CI 0.38–0.55)\nSpearman rho = 0.47 · p < 0.001\nCSS ≈ {b0:.1f} + {b1:.2f} × SHAI', fontsize=10, color=NAVY, va='top', fontweight='bold', linespacing=1.5)
a.set_xlabel('Health anxiety (SHAI-14, 0–42)', fontsize=11); a.set_ylabel('Cyberchondria (CSS-12, 12–60)', fontsize=11)
a.set_xlim(-0.5, 31); a.set_ylim(10, 58); a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#E6ECF1', lw=.8); a.set_axisbelow(True)
f.savefig(f'{OUT}/scatter_shai_css.png', bbox_inches='tight', facecolor=(1, 1, 1, 0.82)); plt.close(f); print('scatter', round(b0, 2), round(b1, 3))

# ---- forest plot of Table 9 (values as published in the thesis)
rows = [('Cyberchondria (per 1 SD)', 3.12, 2.11, 4.62, 1), ('Motive: instant reassurance', 3.83, 1.80, 8.18, 1), ('Age group (per step older)', 0.61, 0.39, 0.93, 1),
        ('Female', 1.23, 0.62, 2.43, 0), ('Health-related background', 1.05, 0.48, 2.27, 0), ('Chronic condition', 1.51, 0.69, 3.30, 0), ('Answered mainly in English', 0.94, 0.45, 1.96, 0),
        ('Uses AI chatbots', 0.61, 0.18, 2.13, 0), ('Uses search engines', 1.43, 0.69, 3.00, 0), ('Trust in online/AI (per point)', 0.74, 0.46, 1.19, 0), ('Motive: self-diagnosis', 0.93, 0.43, 2.03, 0)]
f, a = plt.subplots(figsize=(6.0, 4.3), dpi=220)
for i, (lab, o, lo, hi, sig) in enumerate(rows):
    yy = len(rows) - 1 - i; c = NAVY if sig else '#6F8496'
    a.plot([lo, hi], [yy, yy], color=c, lw=2.4 if sig else 1.6, solid_capstyle='round'); a.plot(o, yy, 'o', color=c, ms=8 if sig else 6)
    a.text(13.5, yy, f'{o:.2f} ({lo:.2f}–{hi:.2f})', va='center', fontsize=11, color=NAVY if sig else INK, fontweight='bold' if sig else 'normal')
a.axvline(1, color=SLATE, lw=1.2, ls=(0, (4, 3))); a.set_xscale('log'); a.set_xlim(0.15, 11)
a.set_xticks([0.2, 0.5, 1, 2, 5, 10]); a.set_xticklabels(['0.2', '0.5', '1', '2', '5', '10'])
a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows][::-1], fontsize=11, color=INK)
for t, r in zip(a.get_yticklabels(), rows[::-1]):
    if r[4]: t.set_color(NAVY); t.set_fontweight('bold')
a.set_xlabel('Adjusted odds ratio (log scale) for elevated health anxiety', fontsize=11)
a.text(0.16, len(rows) - 0.35, '← lower odds', fontsize=10, color=SLATE); a.text(1.08, len(rows) - 0.35, 'higher odds →', fontsize=10, color=SLATE)
a.spines[['top', 'right', 'left']].set_visible(False); a.tick_params(axis='y', length=0); a.set_ylim(-0.7, len(rows) - 0.1)
f.savefig(f'{OUT}/forest_HA.png', bbox_inches='tight', facecolor=(1, 1, 1, 0.82)); plt.close(f); print('forest')

# ---- variance explained by each block of the hierarchical regression (Table 8)
f, a = plt.subplots(figsize=(4.6, 4.0), dpi=220)
labs = ['1. Who you are', '2. + How you\nsearch', '3. + Health\nanxiety']; vals = [3.0, 13.3, 31.7]
bars = a.bar(labs, vals, color=[STEEL, STEEL, NAVY], width=0.6)
for b_, v in zip(bars, vals): a.text(b_.get_x() + b_.get_width() / 2, v + 0.8, f'{v:.1f}%', ha='center', fontsize=12, fontweight='bold', color=NAVY)
a.text(2, 22.5, 'health\nanxiety\nadds\n+18.4%', color='white', fontsize=10.5, fontweight='bold', va='center', ha='center', linespacing=1.3)
a.set_ylim(0, 38); a.set_ylabel('Variance explained, R² (%)', fontsize=10.5)
a.spines[['top', 'right']].set_visible(False); a.grid(axis='y', color='#E3EAF0', lw=.8); a.set_axisbelow(True); a.tick_params(axis='x', labelsize=9.5)
f.savefig(f'{OUT}/r2_blocks.png', bbox_inches='tight', facecolor=(1, 1, 1, 0.82)); plt.close(f); print('r2')
