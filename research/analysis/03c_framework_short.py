"""Conceptual framework for the short thesis (H1, H2 and the medical-student hypothesis H3).
Usage: python3 03c_framework_short.py <output dir>"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = sys.argv[1]; FIG = f'{OUT}/figures'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
BLUE, ORANGE, NAVY, GREY, PALE = '#2A78D6', '#EB6834', '#0B2545', '#6B6B6B', '#EEF3FA'

def box(ax, x, y, w, h, text, fc=PALE, ec=BLUE, tc=NAVY, bold=True, fs=10.5, ls='-'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec=ec, lw=1.6, ls=ls))
    ax.text(x, y, text, ha='center', va='center', color=tc, fontsize=fs, fontweight='bold' if bold else 'normal')

def arrow(ax, p1, p2, color=NAVY, ls='-', label=None, lpos=0.5, loff=(0, 0), lw=1.8):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=15, color=color, lw=lw, ls=ls))
    if label:
        x = p1[0] + (p2[0] - p1[0]) * lpos + loff[0]; y = p1[1] + (p2[1] - p1[1]) * lpos + loff[1]
        ax.text(x, y, label, ha='center', va='center', fontsize=9.5, color=color, fontweight='bold', bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none'))

fig, ax = plt.subplots(figsize=(10, 5.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 5.6); ax.axis('off')
box(ax, 2.0, 3.3, 2.8, 1.0, 'Health anxiety\n(SHAI-14)', fc=BLUE, ec=BLUE, tc='white')
box(ax, 8.0, 3.3, 3.0, 1.55, 'Cyberchondria (CSS-12)\nexcessiveness · compulsion\ndistress · reassurance seeking', fs=10)
box(ax, 5.0, 5.05, 3.4, 0.7, 'Being a medical student', fc='#FDEEE7', ec=ORANGE)
box(ax, 5.0, 1.75, 4.2, 0.6, 'Online tools: search engines · AI chatbots', fc='white', ec=GREY, tc=GREY, bold=False, fs=9.5, ls='--')
box(ax, 5.0, 0.45, 9.4, 0.6, 'H1: adjusted for age, gender, occupation, chronic disease, language, digital use and motives',
    fc='white', ec=GREY, tc=GREY, bold=False, fs=9, ls='--')
arrow(ax, (3.45, 3.3), (6.45, 3.3), color=BLUE, label='H1', loff=(0, 0.28))
arrow(ax, (4.1, 4.75), (2.9, 3.85), color=ORANGE, label='H2', lpos=0.5, loff=(-0.35, 0.05))
arrow(ax, (5.9, 4.75), (7.1, 4.12), color=ORANGE, label='H2', lpos=0.5, loff=(0.35, 0.05))
arrow(ax, (6.4, 2.05), (7.2, 2.5), color=GREY, ls='--')
plt.tight_layout(); fig.savefig(f'{FIG}/fig0a_framework_short.png', dpi=300, bbox_inches='tight'); plt.close(fig)
print('wrote', f'{FIG}/fig0a_framework_short.png')
