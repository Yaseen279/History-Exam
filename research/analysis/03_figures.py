"""Figures for the thesis (300 dpi PNG). Usage: python3 03_figures.py <outdir>"""
import sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import statsmodels.formula.api as smf
OUT = sys.argv[1]; FIG = f'{OUT}/figures'
d = pd.read_pickle(f'{OUT}/analysed.pkl')
x = pd.read_excel(f'{OUT}/tables/all_results.xlsx', sheet_name=None, index_col=0)
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, MUTED, GRID, AXIS = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': AXIS, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'axes.titlesize': 11,
                     'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 300, 'savefig.bbox': 'tight',
                     'figure.facecolor': 'white', 'axes.facecolor': 'white'})
def grid(ax, axis='y'):
    ax.grid(axis=axis, color=GRID, lw=0.6); ax.set_axisbelow(True)
def save(fig, name):
    fig.savefig(f'{FIG}/{name}.png'); plt.close(fig)

# Fig 1: scatter SHAI vs CSS
fig, ax = plt.subplots(figsize=(6.4, 4.4))
jit = np.random.default_rng(1)
ax.scatter(d.SHAI + jit.uniform(-.25, .25, len(d)), d.CSS + jit.uniform(-.25, .25, len(d)), s=22, color=BLUE, alpha=.55,
           edgecolor='white', linewidth=.6)
m = smf.ols('CSS ~ SHAI', d).fit(); xs = np.linspace(d.SHAI.min(), d.SHAI.max(), 100)
pr = m.get_prediction(pd.DataFrame({'SHAI': xs})).summary_frame()
ax.fill_between(xs, pr.mean_ci_lower, pr.mean_ci_upper, color=ORANGE, alpha=.18, lw=0)
ax.plot(xs, pr['mean'], color=ORANGE, lw=2)
ax.axvline(18, color=MUTED, lw=1, ls='--'); ax.text(18.3, 13, 'SHAI ≥ 18', color=INK2, fontsize=8.5)
r = x['T7_corr_matrix_rho'].iloc[0, 1]
ax.text(0.02, 0.97, f'Pearson r = 0.47 (95% CI 0.38–0.55)\nSpearman ρ = {r:.2f}, p < 0.001\nCSS = {m.params.iloc[0]:.1f} + {m.params.iloc[1]:.2f} × SHAI',
        transform=ax.transAxes, va='top', fontsize=9, color=INK, bbox=dict(fc='white', ec=GRID, pad=4))
ax.set_xlabel('Health anxiety (SHAI-14 total, 0–42)'); ax.set_ylabel('Cyberchondria (CSS-12 total, 12–60)')
grid(ax, 'both'); save(fig, 'fig1_scatter_shai_css')

# Fig 2: tools & motivations (two panels, single series each)
def hbar(ax, labels, vals, title, color=BLUE):
    o = np.argsort(vals); labels = np.array(labels)[o]; vals = np.array(vals)[o]
    ax.barh(labels, vals, color=color, height=.6)
    for i, v in enumerate(vals): ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=8.5, color=INK)
    ax.set_xlim(0, max(vals)*1.18); ax.set_title(title, loc='left'); grid(ax, 'x'); ax.set_xlabel('% of respondents (n = 300)')
fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))
hbar(axs[0], ['AI chatbots*', 'Search engines', 'Medical platforms', 'Social media'],
     [d.ai_user.mean()*100, d.tool_search.mean()*100, d.tool_medplat.mean()*100, d.tool_social.mean()*100], 'A. Tools used to look up symptoms')
hbar(axs[1], ['Convenience/accessibility', 'Check if a doctor is needed', 'Instant reassurance', 'Self-diagnose/double-check', 'Cost/logistic barriers'],
     [d[c].mean()*100 for c in ['mot_convenience', 'mot_triage', 'mot_reassurance', 'mot_selfdx', 'mot_cost']], 'B. Motivations for searching')
fig.text(0.01, -0.04, '*Includes 32 respondents who named an AI chatbot without ticking the AI option. Multiple answers allowed.', fontsize=8, color=INK2)
fig.tight_layout(); save(fig, 'fig2_tools_motives')

# Fig 3: behaviours + disclosure + relationship
fig, axs = plt.subplots(1, 3, figsize=(13, 3.6), gridspec_kw={'width_ratios': [1.6, 1, 1]})
hbar(axs[0], ['Delay/skip care (reassured)', 'Ignore the symptom', 'Visit multiple doctors', 'Urgent visit/ER', 'Self-medication', 'Delay care (terrified)'],
     [d[c].mean()*100 for c in ['beh_delay_reassured', 'beh_ignore', 'beh_multidoc', 'beh_urgent', 'beh_selfmed', 'beh_delay_terrified']], 'A. Behaviour after searching')
hbar(axs[1], ['Always', 'Sometimes', 'Never (fear of judgement)'], [(d.share == k).mean()*100 for k in ['Always', 'Sometimes', 'Never (fear of judgement)']], 'B. Disclose search to doctor')
hbar(axs[2], ['No negative impact', 'Somewhat complicated', 'Significantly reduced trust'], [(d.relationship == k).mean()*100 for k in ['No negative impact', 'Somewhat complicated', 'Significantly reduced trust']], 'C. Effect on doctor relationship')
fig.tight_layout(); save(fig, 'fig3_behaviours')

# Fig 4: correlation heatmap (diverging blue-gray-red)
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('div', ['#184f95', '#6da7ec', '#f0efec', '#ef8a89', '#b42e2e'])
rho = x['T7_corr_matrix_rho']; q = x['T7_corr_matrix_q']
fig, ax = plt.subplots(figsize=(8.2, 6.8))
mask = np.triu(np.ones_like(rho, bool), 0)
im = ax.imshow(np.where(mask, np.nan, rho.values), cmap=cmap, vmin=-1, vmax=1)
for i in range(len(rho)):
    for j in range(i+1):
        if i == j: continue
        v = rho.values[i, j]; star = '***' if q.values[i, j] < .001 else '**' if q.values[i, j] < .01 else '*' if q.values[i, j] < .05 else ''
        ax.text(j, i, f'{v:.2f}{star}', ha='center', va='center', fontsize=7.5, color='white' if abs(v) > .55 else INK)
ax.set_xticks(range(len(rho))); ax.set_xticklabels(rho.columns, rotation=45, ha='right', fontsize=8.5)
ax.set_yticks(range(len(rho))); ax.set_yticklabels(rho.index, fontsize=8.5)
for s in ax.spines.values(): s.set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=.7); cb.set_label('Spearman ρ'); cb.outline.set_visible(False)
ax.text(0, -0.36, 'FDR-adjusted (Benjamini–Hochberg): * q<0.05, ** q<0.01, *** q<0.001', transform=ax.transAxes, fontsize=8, color=INK2)
save(fig, 'fig4_corr_heatmap')

# Fig 5: CSS subscales by health-anxiety status (2 series)
subs = [('Excessiveness', 'CSS_excess'), ('Compulsion', 'CSS_compul'), ('Distress', 'CSS_distress'), ('Reassurance', 'CSS_reassur')]
fig, ax = plt.subplots(figsize=(7, 4))
w = .36; xs_ = np.arange(4)
for k, (grp, col, lab) in enumerate([(0, BLUE, f'SHAI < 18 (n={int((d.HA_clin==0).sum())})'), (1, ORANGE, f'SHAI ≥ 18 (n={int(d.HA_clin.sum())})')]):
    s = d[d.HA_clin == grp]; mu = [s[c].mean() for _, c in subs]; se = [s[c].std()/np.sqrt(len(s))*1.96 for _, c in subs]
    ax.bar(xs_ + (k-.5)*w*1.06, mu, w, color=col, label=lab, yerr=se, error_kw=dict(ecolor=INK2, lw=1, capsize=3))
    for xi, v in zip(xs_ + (k-.5)*w*1.06, mu): ax.text(xi, .3, f'{v:.1f}', ha='center', color='white', fontsize=8.5, fontweight='bold')
ax.set_xticks(xs_); ax.set_xticklabels([s for s, _ in subs]); ax.set_ylabel('Mean subscale score (3–15) ± 95% CI')
ax.legend(frameon=False, loc='upper right'); grid(ax); ax.set_ylim(0, 15)
save(fig, 'fig5_subscales_by_HA')

# Fig 6: CSS by tool profile (box)
fig, ax = plt.subplots(figsize=(6.4, 4))
order = ['No AI (search/other only)', 'AI without search engine', 'AI + search engine']
data = [d.loc[d.tool_profile == o, 'CSS'] for o in order]
bp = ax.boxplot(data, widths=.5, patch_artist=True, medianprops=dict(color=ORANGE, lw=2), whiskerprops=dict(color=INK2),
                capprops=dict(color=INK2), flierprops=dict(marker='o', ms=4, mfc=BLUE, mec='white'))
for b in bp['boxes']: b.set(facecolor='#cde2fb', edgecolor=BLUE)
ax.set_xticks([1, 2, 3]); ax.set_xticklabels([f'{o}\n(n={len(v)})' for o, v in zip(['No AI', 'AI, no search engine', 'AI + search engine'], data)])
ax.set_ylabel('Cyberchondria (CSS-12 total)'); grid(ax)
ax.text(.02, .97, 'Kruskal–Wallis p < 0.001', transform=ax.transAxes, va='top', fontsize=9)
save(fig, 'fig6_css_by_tool')

# Fig 7: forest plot logistic HA_clin
t = x['T18_logit_HA_clin'].drop(index='Intercept')
lab = {'age_ord': 'Age group (per step)', 'female': 'Female', 'health_background': 'Health-related background', 'chronic': 'Chronic condition',
       'lang_en': 'Answered mainly in English', 'ai_user': 'Uses AI chatbots', 'tool_search': 'Uses search engines', 'trust': 'Trust in online/AI (per point)',
       'mot_reassurance': 'Motive: instant reassurance', 'mot_selfdx': 'Motive: self-diagnosis', 'zCSS': 'Cyberchondria (per 1 SD)'}
t = t.iloc[::-1]
fig, ax = plt.subplots(figsize=(6.6, 4.6))
ys = np.arange(len(t))
sig = t.p < .05
ax.hlines(ys, t.CI_low, t.CI_high, color=np.where(sig, ORANGE, MUTED), lw=2)
ax.scatter(t.AOR, ys, s=50, color=np.where(sig, ORANGE, BLUE), zorder=3, edgecolor='white', linewidth=1)
ax.axvline(1, color=INK2, lw=1); ax.set_xscale('log')
ax.set_yticks(ys); ax.set_yticklabels([lab[i] for i in t.index])
for y_, (_, r_) in zip(ys, t.iterrows()):
    ax.text(14, y_, f'{r_.AOR:.2f} ({r_.CI_low:.2f}–{r_.CI_high:.2f})', va='center', fontsize=8, color=INK)
ax.set_xlim(.1, 40); ax.set_xticks([.2, .5, 1, 2, 5, 10]); ax.set_xticklabels(['0.2', '0.5', '1', '2', '5', '10'])
ax.set_xlabel('Adjusted odds ratio (log scale) for SHAI ≥ 18'); grid(ax, 'x')
save(fig, 'fig7_forest_HA')

# Fig 8: mediation path diagrams (models A and C)
med = x['T21_mediation']
def diagram(ax, model, xl, ml, yl, title):
    s = med[med.Model == model].set_index('Path')
    a = s.iloc[0]; b = s.iloc[1]; tot = s.loc['Total']; dr = s.loc['Direct']; ind = s.loc['Indirect']
    boxes = {'X': (0.12, 0.25), 'M': (0.5, 0.78), 'Y': (0.88, 0.25)}
    for key, txt in zip(['X', 'M', 'Y'], [xl, ml, yl]):
        cx, cy = boxes[key]
        ax.add_patch(FancyBboxPatch((cx-.15, cy-.1), .30, .20, boxstyle='round,pad=0.01,rounding_size=0.02', fc='#cde2fb', ec=BLUE, lw=1.2))
        ax.text(cx, cy, txt, ha='center', va='center', fontsize=8.5, color=INK)
    kw = dict(arrowstyle='-|>', color=INK2, lw=1.4, mutation_scale=14)
    ax.annotate('', xy=(0.42, 0.70), xytext=(0.20, 0.34), arrowprops=kw)
    ax.annotate('', xy=(0.80, 0.34), xytext=(0.58, 0.70), arrowprops=kw)
    ax.annotate('', xy=(0.73, 0.25), xytext=(0.27, 0.25), arrowprops=kw)
    star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ' (ns)'
    ax.text(0.22, 0.55, f'a = {a.coef:.2f}{star(a.p)}', fontsize=9, color=INK, ha='right')
    ax.text(0.78, 0.55, f'b = {b.coef:.2f}{star(b.p)}', fontsize=9, color=INK)
    ax.text(0.5, 0.09, f"c = {tot.coef:.2f}{star(tot.p)};  c′ = {dr.coef:.2f}{star(dr.p)}", ha='center', fontsize=9, color=INK)
    ax.text(0.5, -0.03, f'Indirect a×b = {ind.coef:.2f} (95% boot CI {ind.CI_low:.2f}–{ind.CI_high:.2f})', ha='center', fontsize=9, color=ORANGE, fontweight='bold')
    ax.set_title(title, loc='left'); ax.set_xlim(-0.05, 1.05); ax.set_ylim(-.05, 1); ax.axis('off')
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
models = list(med.Model.unique())
diagram(axs[0], models[0], 'Health anxiety\n(SHAI)', 'Excessive searching\n(CSS-Excessiveness)', 'Post-search distress\n(CSS-Distress)', 'A. Searching as a pathway to distress')
diagram(axs[1], models[2], 'Health anxiety\n(SHAI)', 'Post-search distress\n(CSS-Distress)', 'Reassurance-seeking\n(CSS-Reassurance)', 'B. Distress as a pathway to doctor visits')
fig.text(0.01, -0.03, 'Standardised coefficients adjusted for age, gender, health background, chronic illness, trust and AI use; 5,000 bootstrap resamples. * p<0.05, ** p<0.01, *** p<0.001.', fontsize=8, color=INK2)
save(fig, 'fig8_mediation')
print('figures done')
