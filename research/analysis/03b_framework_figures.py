"""Conceptual framework (Introduction) and study flowchart (Method).
Usage: python3 03b_framework_figures.py <output dir>"""
import sys, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = sys.argv[1]; FIG = f'{OUT}/figures'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
BLUE, ORANGE, NAVY, GREY, PALE = '#2A78D6', '#EB6834', '#0B2545', '#6B6B6B', '#EEF3FA'

def box(ax, x, y, w, h, text, fc=PALE, ec=BLUE, tc=NAVY, bold=True, fs=10, ls='-'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.06', fc=fc, ec=ec, lw=1.6, ls=ls))
    ax.text(x, y, text, ha='center', va='center', color=tc, fontsize=fs, fontweight='bold' if bold else 'normal', wrap=True)

def arrow(ax, p1, p2, color=NAVY, ls='-', rad=0.0, lw=1.6, label=None, lpos=0.5, loff=(0, 0), lc=None):
    a = FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=14, color=color, lw=lw, ls=ls, connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(a)
    if label:
        x = p1[0] + (p2[0] - p1[0]) * lpos + loff[0]; y = p1[1] + (p2[1] - p1[1]) * lpos + loff[1]
        ax.text(x, y, label, ha='center', va='center', fontsize=9, color=lc or color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none'))

# ---------------------------------------------------------------- Figure: conceptual framework
fig, ax = plt.subplots(figsize=(10, 6.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis('off')
box(ax, 2.0, 4.6, 2.6, 0.9, 'Health anxiety\n(SHAI-14)', fc=BLUE, ec=BLUE, tc='white')
box(ax, 5.4, 4.6, 2.6, 0.9, 'Excessive searching\n(CSS Excessiveness)')
box(ax, 5.4, 2.6, 2.6, 0.9, 'Post-search distress\n(CSS Distress)')
box(ax, 2.0, 2.6, 2.6, 0.9, 'Reassurance seeking\n(CSS Reassurance)')
box(ax, 8.6, 3.6, 2.3, 1.5, 'Pre-consultation\nbehaviour and the\ndoctor–patient\nrelationship', fc='#FDEEE7', ec=ORANGE, tc=NAVY)
box(ax, 7.4, 5.85, 4.0, 0.55, 'Online tools: search engines · AI chatbots', fc='white', ec=GREY, tc=GREY, bold=False, fs=9.5, ls='--')
box(ax, 5.0, 0.75, 9.4, 0.75, 'Adjusted for: age · gender · occupation and health background · chronic disease · trust in online/AI · language',
    fc='white', ec=GREY, tc=GREY, bold=False, fs=9, ls='--')
arrow(ax, (3.3, 4.6), (4.1, 4.6), label='H3 (a)', loff=(0, 0.28))
arrow(ax, (5.4, 4.15), (5.4, 3.05), label='H3 (b)', loff=(0.45, 0))
arrow(ax, (4.1, 2.6), (3.3, 2.6))
arrow(ax, (2.0, 3.05), (2.0, 4.15), ls='--', color=GREY, label='short-lived relief', loff=(-0.05, 0), lc=GREY)
arrow(ax, (2.6, 4.15), (4.6, 3.0), color=BLUE, rad=0.0, label='H1 · H2', lpos=0.42, loff=(-0.15, -0.05), lc=BLUE)
arrow(ax, (6.7, 3.0), (7.45, 3.35), color=ORANGE, label='H4', loff=(0, 0.22), lc=ORANGE)
arrow(ax, (6.7, 4.4), (7.45, 3.95), color=ORANGE)
arrow(ax, (6.4, 5.57), (5.9, 5.07), color=GREY, ls='--')
ax.text(5.4, 5.33, '', fontsize=8)
arrow(ax, (3.7, 1.13), (3.7, 2.15), color=GREY, ls='--')
ax.text(3.65, 5.42, 'Cyberchondria (CSS-12)', rotation=0, ha='center', va='center', color=NAVY, fontsize=9.5, fontweight='bold')
ax.add_patch(FancyBboxPatch((0.45, 2.0), 6.4, 3.25, boxstyle='round,pad=0.02,rounding_size=0.1', fc='none', ec=NAVY, lw=0.8, ls=':'))
plt.tight_layout(); fig.savefig(f'{FIG}/fig0a_framework.png', dpi=300, bbox_inches='tight'); plt.close(fig)

# ---------------------------------------------------------------- Figure: study flowchart
N = json.load(open(f'{OUT}/study/numbers.json')) if __import__('os').path.exists(f'{OUT}/study/numbers.json') else {'n': 300, 'd0': '17 July 2026', 'd1': '11 September 2026'}
fig, ax = plt.subplots(figsize=(10, 7.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 7.4); ax.axis('off')
steps = [
    (6.55, 'Questionnaire development', 'Bilingual (Arabic–English) Google Form · five parts: consent & demographics · digital health seeking · SHAI-14 · CSS-12 · pre-consultation behaviour'),
    (5.25, 'Online distribution in Baghdad', f'{N["d0"]} – {N["d1"]} · convenience and snowball sampling via Baghdad-based social-media and messaging groups'),
    (3.95, f'Responses analysed: n = {N["n"]}', 'Electronic consent and age ≥ 18 required · all items mandatory (no missing data) · no duplicates · all responses retained; annotated and straight-line responses examined in sensitivity analyses'),
    (2.65, 'Data cleaning and scoring', 'Recoding of free-text answers · SHAI-14 (0–42), CSS-12 (12–60) and four subscales · elevated health anxiety (SHAI ≥ 18)'),
]
for y, h, t in steps:
    box(ax, 1.75, y, 3.0, 0.95, h, fc=BLUE, ec=BLUE, tc='white', fs=10)
    ax.add_patch(FancyBboxPatch((3.45, y - 0.475), 6.3, 0.95, boxstyle='round,pad=0.02,rounding_size=0.06', fc=PALE, ec=BLUE, lw=1.2))
    ax.text(3.6, y, __import__('textwrap').fill(t, 80), ha='left', va='center', fontsize=9, color=NAVY)
for y1, y2 in [(6.55, 5.25), (5.25, 3.95), (3.95, 2.65)]:
    arrow(ax, (1.75, y1 - 0.48), (1.75, y2 + 0.48))
arrow(ax, (1.75, 2.17), (1.75, 1.6))
ax.text(5.0, 1.35, 'Statistical analysis', ha='center', va='center', fontsize=10.5, color=NAVY, fontweight='bold')
stages = ['Descriptive\nstatistics', 'Psychometrics\nα, ω, CFA,\ninvariance', 'Bivariate tests\n(FDR-corrected)', 'Multivariable\nlinear & logistic\nregression', 'Pathways\nmediation &\nmoderation', 'Sensitivity\nanalyses']
for i, s in enumerate(stages):
    x = 0.85 + i * 1.66
    box(ax, x, 0.55, 1.5, 0.95, s, fc='#FDEEE7', ec=ORANGE, tc=NAVY, fs=8.5)
    if i < len(stages) - 1:
        arrow(ax, (x + 0.76, 0.55), (x + 0.9, 0.55), color=ORANGE, lw=1.2)
plt.tight_layout(); fig.savefig(f'{FIG}/fig0b_flowchart.png', dpi=300, bbox_inches='tight'); plt.close(fig)
print('wrote fig0a_framework.png, fig0b_flowchart.png')
