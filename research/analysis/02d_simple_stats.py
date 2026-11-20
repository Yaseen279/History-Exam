"""Plain, SPSS-style versions of the multivariable analyses (for the short thesis).
Classical OLS standard errors, standard binary logistic regression (Wald p, Nagelkerke R2, apparent AUC,
Hosmer-Lemeshow), Sobel-test mediation, and the two figures that depend on these numbers.
Every number here can be reproduced with output/spss/Cyberchondria_Simple_Analysis.sps.
Usage: python3 02d_simple_stats.py <output dir>"""
import sys, json, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.metrics import roc_auc_score

OUT = sys.argv[1]
d = pd.read_pickle(f'{OUT}/analysed.pkl')
S = {}

# ------------------------------------------------------------------ 1. hierarchical linear regression of CSS
covs = "C(age_c, Treatment('20–29')) + female + C(occ_c, Treatment('Non-health employed/other')) + chronic + lang_en"
digital = "ai_user + tool_search + tool_medplat + tool_social + trust + mot_reassurance + mot_selfdx + mot_cost + mot_triage"
m1 = smf.ols(f'CSS ~ {covs}', d).fit(); m2 = smf.ols(f'CSS ~ {covs} + {digital}', d).fit(); m3 = smf.ols(f'CSS ~ {covs} + {digital} + SHAI', d).fit()
blocks = []
for prev, m in [(None, m1), (m1, m2), (m2, m3)]:
    if prev is None:
        Fch, pch = m.fvalue, m.f_pvalue
    else:
        Fch, pch, _ = m.compare_f_test(prev)
    blocks.append(dict(R2=m.rsquared, adjR2=m.rsquared_adj, dR2=m.rsquared - (prev.rsquared if prev is not None else 0), F_change=Fch, p_change=pch))
S['hier'] = blocks
S['ols_final'] = dict(F=m3.fvalue, df1=int(m3.df_model), df2=int(m3.df_resid), p=m3.f_pvalue, R2=m3.rsquared, adjR2=m3.rsquared_adj)
y_sd = d.CSS.std(); Xf = pd.DataFrame(m3.model.exog, columns=m3.model.exog_names)
coef = pd.DataFrame({'B': m3.params, 'SE': m3.bse, 't': m3.tvalues, 'p': m3.pvalues})
coef['beta'] = [None if c == 'Intercept' else m3.params[c] * Xf[c].std() / y_sd for c in coef.index]
S['ols_coef'] = coef.reset_index().rename(columns={'index': 'term'}).to_dict('records')
# strict AI definition (ticked only)
m3s = smf.ols(f'CSS ~ {covs} + {digital.replace("ai_user", "tool_ai")} + SHAI', d).fit()
S['ai_strict'] = dict(B=m3s.params['tool_ai'], p=m3s.pvalues['tool_ai'])

# ------------------------------------------------------------------ 2. binary logistic regression of elevated health anxiety
def nagelkerke(m):
    n = m.nobs; cs = 1 - np.exp(2 * (m.llnull - m.llf) / n); return cs, cs / (1 - np.exp(2 * m.llnull / n))
def hosmer_lemeshow(y, p, g=10):
    q = pd.qcut(pd.Series(p).rank(method='first'), g, labels=False)
    t = pd.DataFrame({'y': y, 'p': p, 'g': q}).groupby('g').agg(o=('y', 'sum'), e=('p', 'sum'), n=('y', 'size'))
    chi = (((t.o - t.e) ** 2) / (t.e * (1 - t.e / t.n))).sum(); return chi, 1 - stats.chi2.cdf(chi, g - 2)
def logit(formula):
    m = smf.logit(formula, d).fit(disp=0); ci = np.exp(m.conf_int())
    return m, pd.DataFrame({'AOR': np.exp(m.params), 'CI_low': ci[0], 'CI_high': ci[1], 'B': m.params, 'SE': m.bse, 'Wald': (m.params / m.bse) ** 2, 'p': m.pvalues})
lcov = "age_ord + female + health_background + chronic + lang_en"
mL, tL = logit(f'HA_clin ~ {lcov} + ai_user + tool_search + trust + mot_reassurance + mot_selfdx + zCSS')
cs, nk = nagelkerke(mL); hl, hlp = hosmer_lemeshow(d.HA_clin.values, np.asarray(mL.predict()))
S['logit_HA'] = dict(n=int(mL.nobs), events=int(d.HA_clin.sum()), omnibus_chi2=float(mL.llr), omnibus_df=int(mL.df_model), omnibus_p=float(mL.llr_pvalue),
                     cox_snell=cs, nagelkerke=nk, HL_chi2=hl, HL_p=hlp, AUC=roc_auc_score(d.HA_clin, mL.predict()),
                     correct=float(((mL.predict() >= .5).astype(int) == d.HA_clin).mean() * 100))
S['logit_HA_coef'] = tL.reset_index().rename(columns={'index': 'term'}).to_dict('records')

# ------------------------------------------------------------------ 3. behaviours (both scores in the same model)
beh_out = {'Urgent visit/ER': 'beh_urgent', 'Multiple doctors': 'beh_multidoc', 'Delay/skip care (reassured)': 'beh_delay_reassured',
           'Delay care (terrified)': 'beh_delay_terrified', 'Self-medication': 'beh_selfmed', 'Ignore symptom': 'beh_ignore',
           'Never disclose to physician': 'share_never', 'Negative effect on doctor relationship': 'rel_negative'}
br = []
for lab, y in beh_out.items():
    m, tb = logit(f'{y} ~ zSHAI + zCSS + trust + ai_user + {lcov}')
    for v in ['zSHAI', 'zCSS', 'trust', 'ai_user', 'health_background']:
        r = tb.loc[v]; br.append(dict(Outcome=lab, var=y, events=int(d[y].sum()), Predictor=v, AOR=r.AOR, CI_low=r.CI_low, CI_high=r.CI_high, p=r.p))
S['behaviour'] = br

# ------------------------------------------------------------------ 4. mediation with the Sobel test (standardised scores)
z = d.copy()
for c in ['SHAI', 'CSS_excess', 'CSS_compul', 'CSS_distress', 'CSS_reassur']:
    z[c] = (d[c] - d[c].mean()) / d[c].std()
cm = 'age_ord + female + health_background + chronic + trust + ai_user'
med = []
for key, lab, x, mv, y in [('A', 'HA → excessive searching → post-search distress', 'SHAI', 'CSS_excess', 'CSS_distress'),
                           ('C', 'HA → post-search distress → reassurance seeking', 'SHAI', 'CSS_distress', 'CSS_reassur'),
                           ('D', 'Excessive searching → post-search distress → HA (reverse order)', 'CSS_excess', 'CSS_distress', 'SHAI')]:
    ma = smf.ols(f'{mv} ~ {x} + {cm}', z).fit(); mb = smf.ols(f'{y} ~ {x} + {mv} + {cm}', z).fit(); mc = smf.ols(f'{y} ~ {x} + {cm}', z).fit()
    a, sa, b, sb = ma.params[x], ma.bse[x], mb.params[mv], mb.bse[mv]
    se = np.sqrt(b ** 2 * sa ** 2 + a ** 2 * sb ** 2); zs = a * b / se
    med.append(dict(key=key, Model=lab, a=a, SE_a=sa, p_a=ma.pvalues[x], b=b, SE_b=sb, p_b=mb.pvalues[mv], c=mc.params[x], p_c=mc.pvalues[x],
                    c_prime=mb.params[x], p_c_prime=mb.pvalues[x], indirect=a * b, SE_ind=se, sobel_z=zs, sobel_p=2 * (1 - stats.norm.cdf(abs(zs))),
                    prop=a * b / mc.params[x]))
S['mediation'] = med

# ------------------------------------------------------------------ 4b. medical students vs other participants (H3)
ms = d.medical_student == 1; adj = 'age_ord + female + chronic + lang_en'
mst = {'n_med': int(ms.sum()), 'n_oth': int((~ms).sum())}
for v in ['SHAI', 'CSS']:
    f = smf.ols(f'{v} ~ medical_student + {adj}', d).fit(); ci = f.conf_int().loc['medical_student']
    mst[v] = dict(m_med=d.loc[ms, v].mean(), sd_med=d.loc[ms, v].std(), m_oth=d.loc[~ms, v].mean(), sd_oth=d.loc[~ms, v].std(),
                  p_mw=stats.mannwhitneyu(d.loc[ms, v], d.loc[~ms, v])[1], B=f.params['medical_student'], lo=ci[0], hi=ci[1], p_adj=f.pvalues['medical_student'])
for y in ['HA_clin', 'CSS_high']:
    a_, b_ = int(d.loc[ms, y].sum()), int(d.loc[~ms, y].sum())
    tab = np.array([[a_, ms.sum() - a_], [b_, (~ms).sum() - b_]])
    f = smf.logit(f'{y} ~ medical_student + {adj}', d).fit(disp=0); ci = np.exp(f.conf_int().loc['medical_student'])
    mst[y] = dict(k_med=a_, k_oth=b_, pct_med=a_ / ms.sum() * 100, pct_oth=b_ / (~ms).sum() * 100, p_chi=stats.chi2_contingency(tab, correction=False)[1],
                  OR=(tab[0, 0] * tab[1, 1]) / (tab[0, 1] * tab[1, 0]), AOR=float(np.exp(f.params['medical_student'])), lo=float(ci[0]), hi=float(ci[1]), p_adj=float(f.pvalues['medical_student']))
S['medstud'] = mst

# ------------------------------------------------------------------ 5. simple correlations (SPSS CORRELATIONS / PARTIAL CORR)
r, p = stats.pearsonr(d.SHAI, d.CSS); zf = np.arctanh(r); h = 1.96 / np.sqrt(len(d) - 3)
S['pearson'] = dict(r=r, p=p, CI=[np.tanh(zf - h), np.tanh(zf + h)], rho=stats.spearmanr(d.SHAI, d.CSS)[0])
def _clean(o):
    if isinstance(o, dict): return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list): return [_clean(v) for v in o]
    if isinstance(o, float) and np.isnan(o): return None
    return o
S = _clean(json.loads(json.dumps(S, default=float)))
json.dump(S, open(f'{OUT}/simple.json', 'w'), indent=1, ensure_ascii=False, default=float)
print('wrote', f'{OUT}/simple.json')

# ------------------------------------------------------------------ 6. figures that show these numbers
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
FIG = f'{OUT}/figures'
BLUE, ORANGE, INK, INK2, MUTED, GRID, AXIS = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': AXIS, 'axes.labelcolor': INK2, 'xtick.color': INK2,
                     'ytick.color': INK2, 'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 300, 'savefig.bbox': 'tight'})
lab = {'age_ord': 'Age group (per step)', 'female': 'Female', 'health_background': 'Health-related background', 'chronic': 'Chronic condition',
       'lang_en': 'Answered mainly in English', 'ai_user': 'Uses AI chatbots', 'tool_search': 'Uses search engines', 'trust': 'Trust in online/AI (per point)',
       'mot_reassurance': 'Motive: instant reassurance', 'mot_selfdx': 'Motive: self-diagnosis', 'zCSS': 'Cyberchondria (per 1 SD)'}
t = tL.drop(index='Intercept').iloc[::-1]
fig, ax = plt.subplots(figsize=(6.6, 4.6)); ys = np.arange(len(t)); sig = t.p < .05
ax.hlines(ys, t.CI_low, t.CI_high, color=np.where(sig, ORANGE, MUTED), lw=2)
ax.scatter(t.AOR, ys, s=50, color=np.where(sig, ORANGE, BLUE), zorder=3, edgecolor='white', linewidth=1)
ax.axvline(1, color=INK2, lw=1); ax.set_xscale('log'); ax.set_yticks(ys); ax.set_yticklabels([lab[i] for i in t.index])
for y_, (_, r_) in zip(ys, t.iterrows()):
    ax.text(14, y_, f'{r_.AOR:.2f} ({r_.CI_low:.2f}–{r_.CI_high:.2f})', va='center', fontsize=8, color=INK)
ax.set_xlim(.1, 40); ax.set_xticks([.2, .5, 1, 2, 5, 10]); ax.set_xticklabels(['0.2', '0.5', '1', '2', '5', '10'])
ax.set_xlabel('Adjusted odds ratio (log scale) for SHAI ≥ 18'); ax.grid(axis='x', color=GRID, lw=.6); ax.set_axisbelow(True)
fig.savefig(f'{FIG}/fig7_forest_HA_simple.png'); plt.close(fig)

star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ' (ns)'
def diagram(ax, s, xl, ml, yl, title):
    for (cx, cy), txt in zip([(0.12, 0.25), (0.5, 0.78), (0.88, 0.25)], [xl, ml, yl]):
        ax.add_patch(FancyBboxPatch((cx - .15, cy - .1), .30, .20, boxstyle='round,pad=0.01,rounding_size=0.02', fc='#cde2fb', ec=BLUE, lw=1.2))
        ax.text(cx, cy, txt, ha='center', va='center', fontsize=8.5, color=INK)
    kw = dict(arrowstyle='-|>', color=INK2, lw=1.4, mutation_scale=14)
    ax.annotate('', xy=(0.42, 0.70), xytext=(0.20, 0.34), arrowprops=kw); ax.annotate('', xy=(0.80, 0.34), xytext=(0.58, 0.70), arrowprops=kw)
    ax.annotate('', xy=(0.73, 0.25), xytext=(0.27, 0.25), arrowprops=kw)
    ax.text(0.22, 0.55, f'a = {s["a"]:.2f}{star(s["p_a"])}', fontsize=9, color=INK, ha='right')
    ax.text(0.78, 0.55, f'b = {s["b"]:.2f}{star(s["p_b"])}', fontsize=9, color=INK)
    ax.text(0.5, 0.09, f'c = {s["c"]:.2f}{star(s["p_c"])};  c′ = {s["c_prime"]:.2f}{star(s["p_c_prime"])}', ha='center', fontsize=9, color=INK)
    pz = '< 0.001' if s['sobel_p'] < .001 else f'= {s["sobel_p"]:.3f}'
    ax.text(0.5, -0.03, f'Indirect a×b = {s["indirect"]:.2f} (Sobel z = {s["sobel_z"]:.2f}, p {pz})', ha='center', fontsize=9, color=ORANGE, fontweight='bold')
    ax.set_title(title, loc='left', fontsize=11); ax.set_xlim(-0.05, 1.05); ax.set_ylim(-.05, 1); ax.axis('off')
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
diagram(axs[0], med[0], 'Health anxiety\n(SHAI)', 'Excessive searching\n(CSS-Excessiveness)', 'Post-search distress\n(CSS-Distress)', 'A. Searching as a pathway to distress')
diagram(axs[1], med[1], 'Health anxiety\n(SHAI)', 'Post-search distress\n(CSS-Distress)', 'Reassurance-seeking\n(CSS-Reassurance)', 'B. Distress as a pathway to doctor visits')
fig.text(0.01, -0.03, 'Standardised coefficients from linear regressions adjusted for age, gender, health background, chronic illness, trust and AI use; Sobel test for the indirect effect. * p<0.05, ** p<0.01, *** p<0.001.', fontsize=8, color=INK2)
fig.savefig(f'{FIG}/fig8_mediation_sobel.png'); plt.close(fig)
print('figures written')
