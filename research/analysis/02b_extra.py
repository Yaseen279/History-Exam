"""Additional analyses requested in the defence critique.

Usage: python3 02b_extra.py <outdir>     (reads <outdir>/analysed.pkl, writes <outdir>/extra.json)
- bootstrap optimism-corrected AUC for the elevated-health-anxiety logistic model (Harrell)
- SRMR for the ML confirmatory factor models
- Cohen's f2 for each block of the hierarchical regression
- sensitivity of the main correlation to dropping the one reordered SHAI item (item 2)
- profile of AI non-users vs users
"""
import sys, json, warnings
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score
import semopy
warnings.filterwarnings('ignore')
OUT = sys.argv[1]; d = pd.read_pickle(f'{OUT}/analysed.pkl'); n = len(d)
rng = np.random.default_rng(2026); E = {}

# --- optimism-corrected AUC (500 bootstrap refits, same predictors as Table 8)
f = 'HA_clin ~ age_ord + female + health_background + chronic + lang_en + ai_user + tool_search + trust + mot_reassurance + mot_selfdx + zCSS'
m = smf.logit(f, d).fit(disp=0); auc_app = roc_auc_score(d.HA_clin, m.predict(d))
opt = []
for _ in range(500):
    b = d.iloc[rng.integers(0, n, n)]
    try:
        mb = smf.logit(f, b).fit(disp=0)
        opt.append(roc_auc_score(b.HA_clin, mb.predict(b)) - roc_auc_score(d.HA_clin, mb.predict(d)))
    except Exception:
        pass
E['auc'] = dict(apparent=auc_app, optimism=float(np.mean(opt)), corrected=auc_app - float(np.mean(opt)), n_boot=len(opt))

# --- SRMR for ML CFA models
def srmr(spec, items):
    X = d[items].astype(float); mdl = semopy.Model(spec); mdl.fit(X, obj='MLW')
    obs = mdl.vars['observed']                       # model's own variable order
    S = np.cov(X[obs].values, rowvar=False, bias=True); Sig = mdl.calc_sigma()[0]
    sd = np.sqrt(np.diag(S)); R = (S - Sig) / np.outer(sd, sd)
    return float(np.sqrt(np.mean(R[np.tril_indices(len(items))] ** 2)))
CSS = [f'css{k}' for k in range(1, 13)]; SHAI = [f'shai{k}' for k in range(1, 15)]
spec4 = '\n'.join(f'F{j} =~ ' + ' + '.join(CSS[3 * j:3 * j + 3]) for j in range(4))
E['srmr'] = dict(css4=srmr(spec4, CSS), css1=srmr('G =~ ' + ' + '.join(CSS), CSS), shai1=srmr('H =~ ' + ' + '.join(SHAI), SHAI))

# --- f2 for hierarchical blocks
H = pd.read_excel(f'{OUT}/tables/all_results.xlsx', sheet_name='T13_hierarchical_CSS', index_col=0)
r2 = list(H.R2); E['f2'] = dict(block1=r2[0] / (1 - r2[0]), block2=(r2[1] - r2[0]) / (1 - r2[1]), block3=(r2[2] - r2[1]) / (1 - r2[2]))

# --- reordered SHAI item (item 2) sensitivity
s13 = d[[f'shai{k}' for k in range(1, 15) if k != 2]].sum(axis=1)
r13, p13 = stats.pearsonr(s13, d.CSS); rpro = stats.pearsonr(s13 * 14 / 13, d.CSS)[0]
E['item2'] = dict(r_full=float(stats.pearsonr(d.SHAI, d.CSS)[0]), r_13item_raw=float(r13), r_13item_prorated=float(rpro),
                  rho_13item=float(stats.spearmanr(s13, d.CSS)[0]), p=float(p13))

# --- disattenuated correlation (Spearman-Brown style correction for unreliability)
rel = pd.read_excel(f'{OUT}/tables/all_results.xlsx', sheet_name='T4_reliability', index_col=0).set_index('Scale')
aS, aC = rel.loc['SHAI-14', 'alpha'], rel.loc['CSS-12', 'alpha']
E['disattenuated_r'] = E['item2']['r_full'] / np.sqrt(aS * aC)

# --- AI non-users vs users
prof = {}
for g, lab in [(0, 'non_users'), (1, 'users')]:
    s = d[d.ai_user == g]
    prof[lab] = dict(n=len(s), age_ge40_pct=float((s.age4 == '≥40').mean() * 100), age_le29_pct=float(s.age4.isin(['18-19', '20-29']).mean() * 100),
                     health_bg_pct=float(s.health_background.mean() * 100), medstud_pct=float(s.medical_student.mean() * 100),
                     female_pct=float(s.female.mean() * 100), SHAI_mean=float(s.SHAI.mean()))
ct = pd.crosstab(d.ai_user, d.age4); prof['p_age'] = float(stats.chi2_contingency(ct)[1])
prof['p_health_bg'] = float(stats.fisher_exact(pd.crosstab(d.ai_user, d.health_background))[1])
prof['ticked_ai_pct'] = float(d.tool_ai.mean() * 100); prof['ai_user_pct'] = float(d.ai_user.mean() * 100)
prof['named_model_pct_of_all'] = float((d.ai_model != 'None reported').mean() * 100)
E['ai_profile'] = prof

json.dump(E, open(f'{OUT}/extra.json', 'w'), indent=1)
print(json.dumps(E, indent=1))
