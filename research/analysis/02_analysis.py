"""Full statistical analysis. Usage: python3 02_analysis.py <clean.pkl> <outdir>"""
import sys, json, warnings, itertools
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm, statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor
import pingouin as pg
warnings.filterwarnings('ignore')
rng = np.random.default_rng(2026)

d = pd.read_pickle(sys.argv[1]); OUT = sys.argv[2]
SHAI = [f'shai{k}' for k in range(1, 15)]; CSS = [f'css{k}' for k in range(1, 13)]
SUBS = {'Excessiveness': ['css1', 'css2', 'css3'], 'Compulsion': ['css4', 'css5', 'css6'],
        'Distress': ['css7', 'css8', 'css9'], 'Reassurance': ['css10', 'css11', 'css12']}
SUBCOL = {'Excessiveness': 'CSS_excess', 'Compulsion': 'CSS_compul', 'Distress': 'CSS_distress', 'Reassurance': 'CSS_reassur'}
R = {}            # json summary
T = {}            # tables -> excel
n = len(d)

def fmt_p(p):
    return '<0.001' if p < 0.001 else f'{p:.3f}'

# ======================= 1. Sample size / power =======================
z = stats.norm.ppf
def n_corr(r, alpha=0.05, power=0.80):
    return int(np.ceil(((z(1-alpha/2) + z(power)) / np.arctanh(r))**2 + 3))
def power_corr(r, n, alpha=0.05):
    return float(stats.norm.cdf(np.arctanh(r)*np.sqrt(n-3) - z(1-alpha/2)))
def min_r(n, alpha=0.05, power=0.80):
    return float(np.tanh((z(1-alpha/2)+z(power))/np.sqrt(n-3)))
# Cochran (infinite population, Baghdad ~9 million)
moe = 1.96*np.sqrt(0.25/n)
# regression power: f2 for k predictors (noncentral F)
def power_reg(f2, k, n, alpha=0.05):
    df1, df2 = k, n-k-1; lam = f2*n
    crit = stats.f.ppf(1-alpha, df1, df2)
    return float(1-stats.ncf.cdf(crit, df1, df2, lam))
R['sample_size'] = dict(n=n, cochran_n_for_5pct=int(np.ceil(1.96**2*0.25/0.05**2)), moe_at_n=round(moe*100, 2),
    n_needed_r_0_20=n_corr(0.20), n_needed_r_0_30=n_corr(0.30), min_detectable_r=round(min_r(n), 3),
    power_r_0_20=round(power_corr(0.20, n), 3), power_reg_f2_0_05_k15=round(power_reg(0.05, 15, n), 3),
    power_reg_f2_0_02_1pred_in_15=None)
# power to detect a single predictor adding f2=0.03 in a 15-predictor model
df2 = n-15-1; crit = stats.f.ppf(0.95, 1, df2)
R['sample_size']['power_single_predictor_f2_0_03'] = round(float(1-stats.ncf.cdf(crit, 1, df2, 0.03*n)), 3)
# events per variable for logistic
R['sample_size']['HA_clin_events'] = int(d.HA_clin.sum())

# ======================= 2. Descriptives =======================
def freq(col, order=None, label=None):
    vc = d[col].value_counts()
    if order is not None: vc = vc.reindex(order).fillna(0).astype(int)
    return pd.DataFrame({'Variable': label or col, 'Category': vc.index.astype(str), 'n': vc.values,
                         '%': (vc.values/n*100).round(1)})
tab1 = pd.concat([
    freq('age_group', ['18-19', '20-29', '30-39', '40-49', '50-59', '60+'], 'Age group (years)'),
    freq('gender', ['Female', 'Male'], 'Gender'),
    freq('education', ['Currently a student', 'High school or below', 'Diploma/Vocational', 'Bachelor', 'Postgraduate'], 'Highest education'),
    freq('occupation', ['Medical student', 'Other health-science student', 'Healthcare worker', 'Non-health student', 'Non-health employee/other'], 'Study/work'),
    freq('health_background', [1, 0], 'Health-related background (1=yes)'),
    freq('chronic', [1, 0], 'Diagnosed chronic condition (1=yes)'),
    freq('language', ['Arabic', 'English'], 'Language relied on')])
T['T1_demographics'] = tab1

def multi(cols, labels, title):
    return pd.DataFrame({'Variable': title, 'Category': labels, 'n': [int(d[c].sum()) for c in cols],
                         '%': [round(d[c].mean()*100, 1) for c in cols]})
tab2 = pd.concat([
    multi(['ai_user', 'tool_search', 'tool_medplat', 'tool_social'], ['AI chatbots*', 'Search engines', 'Dedicated medical platforms', 'Social media'], 'Tools used (multiple)'),
    freq('ai_model', ['ChatGPT', 'Gemini', 'Claude', 'Other AI', 'None reported'], 'Main AI chatbot'),
    freq('tool_profile', ['AI + search engine', 'AI without search engine', 'No AI (search/other only)'], 'Tool profile'),
    multi(['mot_convenience', 'mot_triage', 'mot_reassurance', 'mot_selfdx', 'mot_cost'],
          ['Convenience/accessibility', 'Check if doctor visit is needed', 'Instant reassurance', 'Self-diagnose / double-check prescription', 'Cost/logistic barriers'], 'Motivation (multiple)'),
    freq('trust', [1, 2, 3, 4, 5], 'Trust in online/AI medical data (1-5)'),
    multi(['beh_delay_reassured', 'beh_ignore', 'beh_multidoc', 'beh_urgent', 'beh_selfmed', 'beh_delay_terrified'],
          ['Delay/skip care (reassured)', 'Ignore symptom', 'Visit multiple doctors', 'Urgent visit/ER/fast diagnosis', 'Self-medication', 'Delay care (terrified/overwhelmed)'], 'Behaviour after searching (multiple)'),
    freq('share', ['Always', 'Sometimes', 'Never (fear of judgement)'], 'Disclose search to physician'),
    freq('relationship', ['No negative impact', 'Somewhat complicated', 'Significantly reduced trust'], 'Effect on doctor relationship')])
T['T2_digital_behaviour'] = tab2
R['n_tools_dist'] = d.n_tools.value_counts().sort_index().to_dict()
R['ai_inconsistent'] = int(d.ai_model_inconsistent.sum())

# scale descriptives + normality
def desc(x):
    x = pd.Series(x)
    sw = stats.shapiro(x)
    return dict(mean=x.mean(), sd=x.std(), median=x.median(), q1=x.quantile(.25), q3=x.quantile(.75),
                min=x.min(), max=x.max(), skew=stats.skew(x), kurt=stats.kurtosis(x), SW_W=sw.statistic, SW_p=sw.pvalue)
scales = {'SHAI-14 total (0-42)': 'SHAI', 'CSS-12 total (12-60)': 'CSS', 'Excessiveness (3-15)': 'CSS_excess',
          'Compulsion (3-15)': 'CSS_compul', 'Distress (3-15)': 'CSS_distress', 'Reassurance (3-15)': 'CSS_reassur',
          'Trust in online/AI data (1-5)': 'trust'}
T['T3_scale_desc'] = pd.DataFrame({k: desc(d[v]) for k, v in scales.items()}).T.round(3)

# ======================= 3. Reliability & structure =======================
def omega_total(df):
    # one-factor omega from minres EFA loadings
    from factor_analyzer import FactorAnalyzer
    fa = FactorAnalyzer(n_factors=1, rotation=None, method='minres'); fa.fit(df)
    l = fa.loadings_.ravel(); u = fa.get_uniquenesses()
    return float(l.sum()**2/(l.sum()**2+u.sum()))
def alpha_ci(df):
    a, ci = pg.cronbach_alpha(data=df, ci=.95)
    return a, ci
rel = []
for name, items in [('SHAI-14', SHAI), ('CSS-12', CSS)] + [(f'CSS {k}', v) for k, v in SUBS.items()]:
    a, ci = alpha_ci(d[items]); om = omega_total(d[items])
    rel.append(dict(Scale=name, items=len(items), alpha=round(a, 3), alpha_CI=f'{ci[0]:.2f}–{ci[1]:.2f}', omega=round(om, 3),
                    mean_inter_item_r=round(d[items].corr().values[np.triu_indices(len(items), 1)].mean(), 3)))
for lang in ['Arabic', 'English']:
    s = d[d.language == lang]
    for name, items in [('SHAI-14', SHAI), ('CSS-12', CSS)]:
        a, ci = alpha_ci(s[items])
        rel.append(dict(Scale=f'{name} ({lang} responders, n={len(s)})', items=len(items), alpha=round(a, 3),
                        alpha_CI=f'{ci[0]:.2f}–{ci[1]:.2f}', omega=round(omega_total(s[items]), 3), mean_inter_item_r=None))
T['T4_reliability'] = pd.DataFrame(rel)
# Feldt test of equal alphas across language groups
def feldt(a1, n1, a2, n2):
    W = (1-a1)/(1-a2); df1, df2 = n1-1, n2-1
    p = 2*min(stats.f.cdf(W, df1, df2), 1-stats.f.cdf(W, df1, df2)); return W, p
R['feldt'] = {}
for name, items in [('SHAI', SHAI), ('CSS', CSS)]:
    A = d[d.language == 'Arabic']; E = d[d.language == 'English']
    a1 = pg.cronbach_alpha(A[items])[0]; a2 = pg.cronbach_alpha(E[items])[0]
    W, p = feldt(a1, len(A), a2, len(E)); R['feldt'][name] = dict(alpha_ar=a1, alpha_en=a2, W=W, p=p)

# item statistics (corrected item-total r, alpha if deleted)
items_tab = []
shai_names = ['Worry about health', 'Noticing aches/pains', 'Awareness of bodily sensations', 'Resisting thoughts of illness',
              'Fear of serious illness', 'Images of being ill', 'Distraction from health thoughts', 'Relief after medical reassurance',
              'Hearing about an illness', 'Interpreting bodily sensations', 'Perceived risk', 'Thinking you are ill',
              'Unexplained sensations', 'Family/friends view']
css_names = ['Search unexplained sensation online', 'Read different pages on same condition', 'Enter same symptoms repeatedly',
             'Distracts from news/sports/entertainment', 'Interrupts work', 'Interrupts offline social activities',
             'Panic on reading of rare/serious condition', 'Feel fine until reading online', 'More anxious after searching',
             'Leads to consulting GP', 'Suggest diagnostic procedure to doctor', 'Leads to consulting other specialists']
for scale, items, names in [('SHAI-14', SHAI, shai_names), ('CSS-12', CSS, css_names)]:
    tot = d[items].sum(axis=1); a_full = pg.cronbach_alpha(d[items])[0]
    for it, nm in zip(items, names):
        rest = tot - d[it]
        items_tab.append(dict(Scale=scale, Item=it.upper(), Content=nm, Mean=round(d[it].mean(), 2), SD=round(d[it].std(), 2),
                              r_item_rest=round(stats.pearsonr(d[it], rest)[0], 3),
                              alpha_if_deleted=round(pg.cronbach_alpha(d[[i for i in items if i != it]])[0], 3)))
T['T5_item_stats'] = pd.DataFrame(items_tab)

# Sampling adequacy + CFA
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
R['kmo'] = {}
for name, items in [('SHAI', SHAI), ('CSS', CSS)]:
    chi, p = calculate_bartlett_sphericity(d[items]); kmo = calculate_kmo(d[items])[1]
    R['kmo'][name] = dict(KMO=kmo, bartlett_chi2=chi, bartlett_p=p)
import semopy
cfa_rows = []
def run_cfa(desc_, spec, data):
    # DWLS suits ordinal items; ML reported alongside as a stricter check
    out = None
    for method in ['DWLS', 'MLW']:
        m = semopy.Model(spec); m.fit(data, obj=method)
        st = semopy.calc_stats(m).T.iloc[:, 0]
        cfa_rows.append(dict(Model=desc_, Estimator='DWLS' if method == 'DWLS' else 'ML', chi2=round(st['chi2'], 2), df=int(st['DoF']),
                             CFI=round(st['CFI'], 3), TLI=round(st['TLI'], 3), RMSEA=round(st['RMSEA'], 3)))
        if out is None: out = m
    return out
cssd = d[CSS].astype(float); shaid = d[SHAI].astype(float)
run_cfa('CSS-12: one factor', 'G =~ ' + ' + '.join(CSS), cssd)
spec4 = '\n'.join(f'{k} =~ ' + ' + '.join(v) for k, v in SUBS.items())
m4 = run_cfa('CSS-12: four correlated factors', spec4, cssd)
run_cfa('SHAI-14: one factor', 'HA =~ ' + ' + '.join(SHAI), shaid)
# Abramowitz et al. 2007 two-factor (illness likelihood vs body vigilance): body vigilance = items 2,3,10
bv = ['shai2', 'shai3', 'shai10']; il = [i for i in SHAI if i not in bv]
run_cfa('SHAI-14: two factors (illness likelihood + body vigilance)', 'IL =~ ' + ' + '.join(il) + '\nBV =~ ' + ' + '.join(bv), shaid)
T['T6_cfa'] = pd.DataFrame(cfa_rows)
ins = m4.inspect(std_est=True)
T['T6b_cfa_css4_loadings'] = ins[ins.op == '~'][['lval', 'rval', 'Est. Std', 'p-value']].round(3) if (ins.op == '~').any() else ins[ins.op == '=~']
lo = ins[ins['op'] == '~'] if (ins['op'] == '~').any() else ins[ins['op'] == '=~']
R['css4_std_loadings_range'] = [float(lo['Est. Std'].min()), float(lo['Est. Std'].max())]
fc = ins[(ins.op == '~~') & ins.lval.isin(SUBS) & ins.rval.isin(SUBS) & (ins.lval != ins.rval)]
T['T6c_css_factor_corr'] = fc[['lval', 'rval', 'Est. Std']].round(3)

# ======================= 4. Correlations =======================
def spearman_ci(x, y, B=5000):
    rho = stats.spearmanr(x, y)[0]
    idx = rng.integers(0, len(x), (B, len(x)))
    xb, yb = np.asarray(x)[idx], np.asarray(y)[idx]
    rb = np.array([stats.spearmanr(a, b)[0] for a, b in zip(xb[:2000], yb[:2000])])
    return rho, np.percentile(rb, [2.5, 97.5])
main = {}
r_p, p_p = stats.pearsonr(d.SHAI, d.CSS); rho, p_s = stats.spearmanr(d.SHAI, d.CSS)
rho_, ci = spearman_ci(d.SHAI.values, d.CSS.values)
pc = pg.corr(d.SHAI, d.CSS, method='pearson')
main['SHAI_CSS'] = dict(pearson_r=r_p, pearson_p=p_p, pearson_CI=list(pc['CI95'].iloc[0]), spearman=rho, spearman_p=p_s,
                        spearman_boot_CI=list(ci), r2=r_p**2)
for k, c in SUBCOL.items():
    rr, pp = stats.spearmanr(d.SHAI, d[c]); rp, ppp = stats.pearsonr(d.SHAI, d[c])
    main[f'SHAI_{k}'] = dict(spearman=rr, p=pp, pearson=rp, pearson_CI=list(pg.corr(d.SHAI, d[c])['CI95'].iloc[0]))
# Steiger-type comparison of dependent correlations: is SHAI-Distress > SHAI-Excessiveness, etc. (pingouin compare not avail) -> Williams' t
def williams_t(r12, r13, r23, n_):
    det = 1 - r12**2 - r13**2 - r23**2 + 2*r12*r13*r23
    rbar = (r12 + r13)/2
    t = (r12 - r13)*np.sqrt((n_-1)*(1+r23)/(2*((n_-1)/(n_-3))*det + rbar**2*(1-r23)**3))
    return t, 2*(1-stats.t.cdf(abs(t), n_-3))
cmp = []
for a, b in itertools.combinations(SUBCOL, 2):
    r12 = stats.pearsonr(d.SHAI, d[SUBCOL[a]])[0]; r13 = stats.pearsonr(d.SHAI, d[SUBCOL[b]])[0]
    r23 = stats.pearsonr(d[SUBCOL[a]], d[SUBCOL[b]])[0]
    t, p = williams_t(r12, r13, r23, n)
    cmp.append(dict(A=a, B=b, r_SHAI_A=round(r12, 3), r_SHAI_B=round(r13, 3), t=round(t, 2), p=p))
T['T7b_compare_corr'] = pd.DataFrame(cmp)
R['main_corr'] = main
# partial correlation SHAI-CSS controlling for covariates
pcor = pg.partial_corr(d.assign(gender_f=d.female), x='SHAI', y='CSS',
                       covar=['age_ord', 'female', 'health_background', 'chronic', 'trust', 'ai_user'], method='pearson')
R['partial_corr'] = dict(r=float(pcor['r'].iloc[0]), CI=list(pcor['CI95'].iloc[0]), p=float(pcor['p_val'].iloc[0]))

cvars = ['SHAI', 'CSS', 'CSS_excess', 'CSS_compul', 'CSS_distress', 'CSS_reassur', 'trust', 'n_tools', 'n_motives', 'age_ord']
clabels = ['Health anxiety (SHAI)', 'Cyberchondria (CSS)', 'Excessiveness', 'Compulsion', 'Distress', 'Reassurance',
           'Trust in online/AI', 'No. of tools', 'No. of motives', 'Age group']
rho_m = d[cvars].corr(method='spearman'); p_m = pd.DataFrame(np.ones((len(cvars),)*2), index=cvars, columns=cvars).copy()
for a, b in itertools.combinations(cvars, 2):
    p_m.loc[a, b] = p_m.loc[b, a] = stats.spearmanr(d[a], d[b])[1]
iu = np.triu_indices(len(cvars), 1)
q = multipletests(p_m.values[iu], method='fdr_bh')[1]
qa = np.zeros((len(cvars),)*2); qa[iu] = q; qa = qa + qa.T; q_m = pd.DataFrame(qa, index=cvars, columns=cvars)
rho_m.index = rho_m.columns = clabels; q_m.index = q_m.columns = clabels
T['T7_corr_matrix_rho'] = rho_m.round(3); T['T7_corr_matrix_q'] = q_m.round(4)
# item-level: SHAI total vs each CSS item, CSS total vs each SHAI item
il_rows = []
for it, nm in zip(CSS, css_names):
    r_, p_ = stats.spearmanr(d.SHAI, d[it]); il_rows.append(dict(Pair='SHAI total × CSS item', Item=it.upper(), Content=nm, rho=r_, p=p_))
for it, nm in zip(SHAI, shai_names):
    r_, p_ = stats.spearmanr(d.CSS, d[it]); il_rows.append(dict(Pair='CSS total × SHAI item', Item=it.upper(), Content=nm, rho=r_, p=p_))
il = pd.DataFrame(il_rows); il['q_FDR'] = multipletests(il.p, method='fdr_bh')[1]
T['T8_item_level_corr'] = il.round(4)

# ======================= 5. Group comparisons (every variable) =======================
groupvars = {
 'Age group': 'age4', 'Gender': 'gender', 'Education': 'education', 'Study/work': 'occupation',
 'Health-related background': 'health_background', 'Chronic condition': 'chronic', 'Uses AI chatbots': 'ai_user',
 'Uses search engines': 'tool_search', 'Uses medical platforms': 'tool_medplat', 'Uses social media': 'tool_social',
 'Tool profile': 'tool_profile', 'Main AI chatbot': 'ai_model', 'Motive: convenience': 'mot_convenience',
 'Motive: cost/logistics': 'mot_cost', 'Motive: reassurance': 'mot_reassurance', 'Motive: self-diagnosis': 'mot_selfdx',
 'Motive: triage (need a doctor?)': 'mot_triage', 'Trust in online/AI (1-5)': 'trust',
 'Delay care (reassured)': 'beh_delay_reassured', 'Delay care (terrified)': 'beh_delay_terrified', 'Self-medication': 'beh_selfmed',
 'Urgent visit/ER': 'beh_urgent', 'Multiple doctors': 'beh_multidoc', 'Ignore symptom': 'beh_ignore',
 'Disclose to physician': 'share', 'Effect on doctor relationship': 'relationship', 'Language': 'language'}
outcomes = {'SHAI': 'SHAI', 'CSS': 'CSS', 'Excessiveness': 'CSS_excess', 'Compulsion': 'CSS_compul',
            'Distress': 'CSS_distress', 'Reassurance': 'CSS_reassur'}
rows = []; posthoc_rows = []
for gl, g in groupvars.items():
    levels = [lv for lv in d[g].dropna().unique()]
    try: levels = sorted(levels)
    except Exception: pass
    gsz = d[g].value_counts()
    for ol, o in outcomes.items():
        groups = [d.loc[d[g] == lv, o].values for lv in levels]
        desc_s = '; '.join(f'{lv}: {np.median(x):.0f} ({np.percentile(x,25):.0f}–{np.percentile(x,75):.0f}) [{np.mean(x):.1f}±{np.std(x,ddof=1):.1f}], n={len(x)}' for lv, x in zip(levels, groups))
        if len(levels) == 2:
            U, p = stats.mannwhitneyu(groups[0], groups[1], alternative='two-sided')
            rrb = 1 - 2*U/(len(groups[0])*len(groups[1]))   # rank-biserial (positive = second level higher)
            tt = stats.ttest_ind(groups[1], groups[0], equal_var=False)
            dcoh = (groups[1].mean()-groups[0].mean())/np.sqrt((groups[0].var(ddof=1)+groups[1].var(ddof=1))/2)
            rows.append(dict(Variable=gl, Outcome=ol, Test='Mann–Whitney U', Stat=U, p=p, Effect='r_rb (+ = 2nd level higher)', ES=rrb,
                             Welch_t=tt.statistic, Welch_p=tt.pvalue, Cohen_d=dcoh, Groups=desc_s))
        else:
            H, p = stats.kruskal(*groups); k = len(groups)
            eps2 = (H - k + 1)/(n - k)
            F = pg.welch_anova(data=d, dv=o, between=g)
            rows.append(dict(Variable=gl, Outcome=ol, Test='Kruskal–Wallis H', Stat=H, p=p, Effect='epsilon²', ES=max(eps2, 0),
                             Welch_t=F['F'].iloc[0], Welch_p=F['p_unc'].iloc[0], Cohen_d=F['np2'].iloc[0], Groups=desc_s))
            if p < 0.05 and ol in ('SHAI', 'CSS'):
                dt = pg.pairwise_tests(data=d, dv=o, between=g, parametric=False, padjust='holm')
                for _, r in dt.iterrows():
                    posthoc_rows.append(dict(Variable=gl, Outcome=ol, A=r['A'], B=r['B'], U=r['U_val'], p_holm=r['p_corr']))
G = pd.DataFrame(rows)
G['q_FDR'] = multipletests(G.p, method='fdr_bh')[1]
T['T9_group_comparisons'] = G.round(4)
T['T9b_posthoc'] = pd.DataFrame(posthoc_rows).round(4)

# ======================= 6. Chi-square: clinical HA & high cyberchondria vs every categorical =======================
css_cut = d.CSS.quantile(2/3)
d['CSS_high'] = (d.CSS > css_cut).astype(int)      # upper tertile
R['css_high_cut'] = float(css_cut); R['css_high_n'] = int(d.CSS_high.sum())
chi_rows = []
def chi_test(g, y):
    ct = pd.crosstab(d[g], d[y])
    if ct.shape == (2, 2):
        ex = stats.contingency.expected_freq(ct.values)
        if (ex < 5).any():
            OR, p = stats.fisher_exact(ct.values); test = 'Fisher exact'; chi = np.nan
        else:
            chi, p, _, _ = stats.chi2_contingency(ct, correction=False); test = 'Pearson χ²'
    else:
        chi, p, _, ex = stats.chi2_contingency(ct, correction=False); test = 'Pearson χ²'
        if (ex < 5).mean() > 0.2:
            # Monte-Carlo exact p
            obs = chi; cnt = 0; x = d[g].values; yy = d[y].values
            for _ in range(5000):
                c2 = stats.chi2_contingency(pd.crosstab(x, rng.permutation(yy)), correction=False)[0]; cnt += c2 >= obs
            p = (cnt+1)/5001; test = 'χ² (Monte-Carlo exact p)'
    chi_v = stats.chi2_contingency(ct, correction=False)[0]
    V = np.sqrt(chi_v/(ct.values.sum()*(min(ct.shape)-1)))
    pct = (ct.div(ct.sum(axis=1), axis=0)[1]*100).round(1)
    return test, chi, p, V, '; '.join(f'{i}: {ct.loc[i,1]}/{ct.loc[i].sum()} ({pct[i]}%)' for i in ct.index)
for y, yl in [('HA_clin', 'Clinically relevant HA (SHAI≥18)'), ('CSS_high', 'High cyberchondria (CSS upper tertile)')]:
    for gl, g in groupvars.items():
        test, chi, p, V, s = chi_test(g, y)
        chi_rows.append(dict(Outcome=yl, Variable=gl, Test=test, chi2=chi, p=p, CramersV=V, Distribution=s))
# HA_clin × CSS_high
test, chi, p, V, s = chi_test('HA_clin', 'CSS_high')
chi_rows.append(dict(Outcome='High cyberchondria (CSS upper tertile)', Variable='Clinically relevant HA', Test=test, chi2=chi, p=p, CramersV=V, Distribution=s))
CH = pd.DataFrame(chi_rows); CH['q_FDR'] = multipletests(CH.p, method='fdr_bh')[1]
T['T10_chi_square'] = CH.round(4)
ct = pd.crosstab(d.HA_clin, d.CSS_high); OR = (ct.loc[1,1]*ct.loc[0,0])/(ct.loc[1,0]*ct.loc[0,1])
se = np.sqrt((1/ct.values).sum()); R['HA_CSShigh_OR'] = dict(OR=OR, CI=[np.exp(np.log(OR)-1.96*se), np.exp(np.log(OR)+1.96*se)], table=ct.values.tolist())

# Associations between behavioural/categorical digital variables themselves (trust, tools, share, relationship)
pair_rows = []
catvars = ['ai_user', 'tool_search', 'health_background', 'medical_student', 'chronic', 'female', 'language', 'share', 'relationship',
           'beh_delay_reassured', 'beh_selfmed', 'beh_urgent', 'beh_multidoc', 'beh_ignore', 'mot_reassurance', 'mot_selfdx', 'mot_cost', 'age4']
for a, b in itertools.combinations(catvars, 2):
    ctab = pd.crosstab(d[a], d[b]); chi, p, _, ex = stats.chi2_contingency(ctab, correction=False)
    V = np.sqrt(chi/(n*(min(ctab.shape)-1)))
    pair_rows.append(dict(A=a, B=b, chi2=chi, df=(ctab.shape[0]-1)*(ctab.shape[1]-1), p=p, CramersV=V, low_expected=bool((ex < 5).any())))
PR = pd.DataFrame(pair_rows); PR['q_FDR'] = multipletests(PR.p, method='fdr_bh')[1]
T['T11_pairwise_categorical'] = PR.sort_values('p').round(4)
# trust (ordinal) vs categorical: Kruskal
tr_rows = []
for gl, g in groupvars.items():
    if g == 'trust': continue
    lv = d[g].unique(); grp = [d.loc[d[g] == l, 'trust'] for l in lv]
    if len(lv) == 2: s, p = stats.mannwhitneyu(*grp); t = 'MWU'
    else: s, p = stats.kruskal(*grp); t = 'KW'
    tr_rows.append(dict(Variable=gl, Test=t, Stat=s, p=p, means='; '.join(f'{l}: {x.mean():.2f}' for l, x in zip(lv, grp))))
TR = pd.DataFrame(tr_rows); TR['q_FDR'] = multipletests(TR.p, method='fdr_bh')[1]
T['T12_trust_by_group'] = TR.round(4)

# ======================= 7. Multivariable models =======================
d['age_c'] = d.age4.astype(str).replace({'18-19': '18–19', '20-29': '20–29', '30-39': '30–39'})
d['occ_c'] = d.occupation.replace({'Other health-science student': 'Other health student', 'Non-health employee/other': 'Non-health employed/other'})
d['lang_en'] = (d.language == 'English').astype(int)
d['zSHAI'] = (d.SHAI - d.SHAI.mean())/d.SHAI.std(); d['zCSS'] = (d.CSS - d.CSS.mean())/d.CSS.std()
d['trust_c'] = d.trust - d.trust.mean(); d['SHAI_c'] = d.SHAI - d.SHAI.mean()
covs = "C(age_c, Treatment('20–29')) + female + C(occ_c, Treatment('Non-health employed/other')) + chronic + lang_en"
digital = "ai_user + tool_search + tool_medplat + tool_social + trust + mot_reassurance + mot_selfdx + mot_cost + mot_triage"
def ols(formula, data=d):
    return smf.ols(formula, data).fit(cov_type='HC3')
m1 = ols(f'CSS ~ {covs}'); m2 = ols(f'CSS ~ {covs} + {digital}'); m3 = ols(f'CSS ~ {covs} + {digital} + SHAI')
hier = []
for i, (lab, m) in enumerate([('Block 1: socio-demographics', m1), ('Block 2: + digital-use variables', m2), ('Block 3: + health anxiety (SHAI)', m3)]):
    prev = [None, m1, m2][i]
    if prev is not None:
        # F-change using classical (non-robust) fits
        fo = smf.ols(m.model.formula, d).fit(); fp = smf.ols(prev.model.formula, d).fit()
        Fch, pch, dfd = fo.compare_f_test(fp)
    else:
        Fch = pch = np.nan
    hier.append(dict(Model=lab, R2=m.rsquared, adjR2=m.rsquared_adj, dR2=(m.rsquared - (prev.rsquared if prev is not None else 0)), F_change=Fch, p_change=pch))
T['T13_hierarchical_CSS'] = pd.DataFrame(hier).round(4)
def coef_table(m, std_from=None):
    ci = m.conf_int(); tb = pd.DataFrame({'B': m.params, 'CI_low': ci[0], 'CI_high': ci[1], 'SE_HC3': m.bse, 't': m.tvalues, 'p': m.pvalues})
    # standardized beta for continuous predictors
    y = m.model.endog; X = pd.DataFrame(m.model.exog, columns=m.model.exog_names)
    tb['beta_std'] = [m.params[c]*X[c].std()/y.std() if c != 'Intercept' else np.nan for c in tb.index]
    return tb
T['T14_OLS_CSS_full'] = coef_table(m3).round(4)
X = pd.DataFrame(m3.model.exog, columns=m3.model.exog_names).drop(columns='Intercept')
T['T14b_VIF'] = pd.DataFrame({'VIF': [variance_inflation_factor(X.assign(c=1).values, i) for i in range(X.shape[1])]}, index=X.columns).round(2)
R['ols_css'] = dict(R2=m3.rsquared, adjR2=m3.rsquared_adj, F=m3.fvalue, Fp=m3.f_pvalue, n=int(m3.nobs),
                    resid_shapiro_p=stats.shapiro(m3.resid)[1], bp_p=sm.stats.het_breuschpagan(m3.resid, m3.model.exog)[1])
# reverse direction: SHAI ~ CSS + covariates
m4r = ols(f'SHAI ~ {covs} + {digital} + CSS')
T['T15_OLS_SHAI_full'] = coef_table(m4r).round(4)
R['ols_shai'] = dict(R2=m4r.rsquared, adjR2=m4r.rsquared_adj, F=m4r.fvalue, Fp=m4r.f_pvalue)
m4r0 = ols(f'SHAI ~ {covs} + {digital}'); R['ols_shai']['dR2_CSS'] = m4r.rsquared - m4r0.rsquared
# Each CSS subscale ~ SHAI + covariates (standardized)
sub_rows = []
for k, c in SUBCOL.items():
    m = ols(f'{c} ~ {covs} + {digital} + SHAI')
    b = m.params['SHAI']; beta = b*d.SHAI.std()/d[c].std(); ci = m.conf_int().loc['SHAI']
    sub_rows.append(dict(Outcome=k, B=b, CI=f'{ci[0]:.3f} to {ci[1]:.3f}', beta=beta, p=m.pvalues['SHAI'], R2=m.rsquared))
T['T16_subscales_on_SHAI'] = pd.DataFrame(sub_rows).round(4)
# quantile regression: is SHAI effect stronger at high cyberchondria?
qr = []
for qq in [0.25, 0.5, 0.75, 0.9]:
    mq = smf.quantreg(f'CSS ~ SHAI + age_ord + female + health_background + chronic + trust + ai_user', d).fit(q=qq)
    ci = mq.conf_int().loc['SHAI']; qr.append(dict(quantile=qq, B_SHAI=mq.params['SHAI'], CI=f'{ci[0]:.2f} to {ci[1]:.2f}', p=mq.pvalues['SHAI']))
T['T17_quantile_reg'] = pd.DataFrame(qr).round(4)
# Nonlinearity: quadratic SHAI
mq2 = ols('CSS ~ SHAI + I(SHAI**2) + age_ord + female + health_background + chronic + trust + ai_user')
R['quadratic'] = dict(b2=mq2.params['I(SHAI ** 2)'], p=mq2.pvalues['I(SHAI ** 2)'])

# ======================= 8. Logistic regressions =======================
def logit(formula, data=d):
    m = smf.logit(formula, data).fit(disp=0, cov_type='HC1')
    ci = np.exp(m.conf_int()); tb = pd.DataFrame({'AOR': np.exp(m.params), 'CI_low': ci[0], 'CI_high': ci[1], 'p': m.pvalues})
    return m, tb
lcov = "age_ord + female + health_background + chronic + lang_en"
mL, tL = logit(f'HA_clin ~ {lcov} + ai_user + tool_search + trust + mot_reassurance + mot_selfdx + zCSS')
T['T18_logit_HA_clin'] = tL.round(4)
R['logit_HA'] = dict(pseudoR2=mL.prsquared, n=int(mL.nobs), events=int(d.HA_clin.sum()), llr_p=mL.llr_pvalue)
from sklearn.metrics import roc_auc_score
R['logit_HA']['AUC'] = roc_auc_score(d.HA_clin, mL.predict())
# outcomes: behaviours as dependent variables
beh_out = {'Delay/skip care (reassured)': 'beh_delay_reassured', 'Self-medication': 'beh_selfmed', 'Urgent visit/ER': 'beh_urgent',
           'Multiple doctors': 'beh_multidoc', 'Ignore symptom': 'beh_ignore', 'Delay care (terrified)': 'beh_delay_terrified',
           'Never disclose to physician': 'share_never', 'Negative effect on doctor relationship': 'rel_negative'}
br = []
for lab, y in beh_out.items():
    try:
        m, tb = logit(f'{y} ~ zSHAI + zCSS + trust + ai_user + {lcov}')
        for v in ['zSHAI', 'zCSS', 'trust', 'ai_user', 'health_background']:
            br.append(dict(Outcome=lab, events=int(d[y].sum()), Predictor=v, AOR=tb.loc[v, 'AOR'], CI_low=tb.loc[v, 'CI_low'], CI_high=tb.loc[v, 'CI_high'], p=tb.loc[v, 'p']))
    except Exception as e:
        br.append(dict(Outcome=lab, Predictor='model failed', AOR=np.nan, p=np.nan))
BR = pd.DataFrame(br); BR['q_FDR'] = multipletests(BR.p.fillna(1), method='fdr_bh')[1]
T['T19_logit_behaviours'] = BR.round(4)
# Ordinal logistic: relationship (ordered) and trust
from statsmodels.miscmodels.ordinal_model import OrderedModel
d['rel_ord'] = d.relationship.map({'No negative impact': 0, 'Somewhat complicated': 1, 'Significantly reduced trust': 2})
d['share_ord'] = d.share.map({'Always': 0, 'Sometimes': 1, 'Never (fear of judgement)': 2})
ordr = []
for y, lab in [('rel_ord', 'Damage to doctor relationship (ordinal)'), ('share_ord', 'Non-disclosure to physician (ordinal)')]:
    om = OrderedModel(d[y], d[['zSHAI', 'zCSS', 'trust', 'ai_user', 'age_ord', 'female', 'health_background', 'chronic']], distr='logit').fit(method='bfgs', disp=0)
    ci = om.conf_int()
    for v in ['zSHAI', 'zCSS', 'trust', 'ai_user', 'health_background']:
        ordr.append(dict(Outcome=lab, Predictor=v, OR=np.exp(om.params[v]), CI_low=np.exp(ci.loc[v, 0]), CI_high=np.exp(ci.loc[v, 1]), p=om.pvalues[v]))
T['T20_ordinal_logit'] = pd.DataFrame(ordr).round(4)

# ======================= 9. Mediation & moderation =======================
def boot_mediation(x, m, y, covars, data, B=5000):
    res = pg.mediation_analysis(data=data, x=x, m=m, y=y, covar=covars, n_boot=B, seed=2026)
    return res
med_rows = []
cov_med = ['age_ord', 'female', 'health_background', 'chronic', 'trust', 'ai_user']
zs = d.copy()
for c in ['SHAI', 'CSS', 'CSS_excess', 'CSS_compul', 'CSS_distress', 'CSS_reassur']:
    zs[c] = (d[c]-d[c].mean())/d[c].std()
# Model A: SHAI -> Excessiveness (searching) -> Distress (post-search anxiety)  ["search fuels anxiety"]
for lab, x, m_, y in [('A: HA → Excessive searching → Post-search distress', 'SHAI', 'CSS_excess', 'CSS_distress'),
                      ('B: HA → Excessive searching → Compulsion', 'SHAI', 'CSS_excess', 'CSS_compul'),
                      ('C: HA → Post-search distress → Reassurance-seeking (doctor visits)', 'SHAI', 'CSS_distress', 'CSS_reassur'),
                      ('D: Excessive searching → Post-search distress → HA (reverse path)', 'CSS_excess', 'CSS_distress', 'SHAI')]:
    res = boot_mediation(x, m_, y, cov_med, zs)
    for _, r in res.iterrows():
        med_rows.append(dict(Model=lab, Path=r['path'], coef=r['coef'], CI_low=r['CI2.5'], CI_high=r['CI97.5'], p=r['pval']))
MED = pd.DataFrame(med_rows); T['T21_mediation'] = MED.round(4)
# proportion mediated
pm = {}
for lab in MED.Model.unique():
    s = MED[MED.Model == lab].set_index('Path')
    pm[lab] = float(s.loc['Indirect', 'coef']/s.loc['Total', 'coef'])
R['prop_mediated'] = pm
# Serial: HA -> excess -> distress -> reassurance (manual bootstrap)
def serial(df, B=5000):
    Xc = df[cov_med].values
    def fit(D):
        def b(yv, xs):
            Xm = np.column_stack([np.ones(len(D))] + xs + [D[cov_med].values])
            return np.linalg.lstsq(Xm, D[yv].values, rcond=None)[0]
        a1 = b('CSS_excess', [D.SHAI.values])[1]
        bb = b('CSS_distress', [D.SHAI.values, D.CSS_excess.values]); a2, d21 = bb[1], bb[2]
        cc = b('CSS_reassur', [D.SHAI.values, D.CSS_excess.values, D.CSS_distress.values]); cprime, b1, b2 = cc[1], cc[2], cc[3]
        return np.array([a1*b1, a2*b2, a1*d21*b2, cprime])
    est = fit(df); boots = np.array([fit(df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)) for _ in range(B)])
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    return pd.DataFrame({'Path': ['HA→Excess→Reassurance', 'HA→Distress→Reassurance', 'HA→Excess→Distress→Reassurance', 'Direct HA→Reassurance'],
                         'coef': est, 'CI_low': lo, 'CI_high': hi})
T['T22_serial_mediation'] = serial(zs.reset_index(drop=True)).round(4)
# Moderation: does trust / AI use / health background / gender / chronic moderate SHAI->CSS?
mod_rows = []
for mod, lab in [('trust_c', 'Trust in online/AI data'), ('ai_user', 'AI chatbot use'), ('health_background', 'Health-related background'),
                 ('female', 'Female gender'), ('chronic', 'Chronic condition'), ('lang_en', 'English-language responder'), ('age_ord', 'Age group (ordinal)')]:
    m = ols(f'CSS ~ SHAI_c * {mod} + age_ord + female + health_background + chronic + trust + ai_user')
    term = f'SHAI_c:{mod}'
    ci = m.conf_int().loc[term]
    mod_rows.append(dict(Moderator=lab, B_interaction=m.params[term], CI=f'{ci[0]:.3f} to {ci[1]:.3f}', p=m.pvalues[term], R2=m.rsquared))
MOD = pd.DataFrame(mod_rows); MOD['q_FDR'] = multipletests(MOD.p, method='fdr_bh')[1]; T['T23_moderation'] = MOD.round(4)
# simple slopes for trust
mt = ols('CSS ~ SHAI_c * trust_c + age_ord + female + health_background + chronic + ai_user')
ss = []
for lv, val in [('Low trust (−1 SD)', -d.trust.std()), ('Mean trust', 0), ('High trust (+1 SD)', d.trust.std())]:
    g = np.zeros(len(mt.params)); names = list(mt.params.index)
    g[names.index('SHAI_c')] = 1; g[names.index('SHAI_c:trust_c')] = val
    est = g @ mt.params.values; se = np.sqrt(g @ mt.cov_params().values @ g)
    ss.append(dict(Level=lv, slope=est, CI_low=est-1.96*se, CI_high=est+1.96*se, p=2*(1-stats.norm.cdf(abs(est/se)))))
T['T23b_simple_slopes_trust'] = pd.DataFrame(ss).round(4)

# ======================= 10. Language equivalence =======================
le = []
for c in ['SHAI', 'CSS']:
    a = d.loc[d.language == 'Arabic', c]; e = d.loc[d.language == 'English', c]
    U, p = stats.mannwhitneyu(a, e)
    m = ols(f'{c} ~ lang_en + age_ord + female + health_background + chronic')
    le.append(dict(Scale=c, Arabic=f'{a.mean():.2f}±{a.std():.2f}', English=f'{e.mean():.2f}±{e.std():.2f}', MWU_p=p,
                   adj_B_English=m.params['lang_en'], adj_p=m.pvalues['lang_en']))
r_ar = stats.pearsonr(d.loc[d.language == 'Arabic', 'SHAI'], d.loc[d.language == 'Arabic', 'CSS'])[0]
r_en = stats.pearsonr(d.loc[d.language == 'English', 'SHAI'], d.loc[d.language == 'English', 'CSS'])[0]
zdiff = (np.arctanh(r_ar)-np.arctanh(r_en))/np.sqrt(1/(212-3)+1/(88-3))
R['lang_corr'] = dict(r_ar=r_ar, r_en=r_en, z=zdiff, p=2*(1-stats.norm.cdf(abs(zdiff))))
T['T24_language'] = pd.DataFrame(le).round(4)
# Multi-group CFA (configural) for CSS by language — loading similarity (Tucker congruence)
from factor_analyzer import FactorAnalyzer
def loads(df):
    fa = FactorAnalyzer(n_factors=1, rotation=None); fa.fit(df); return fa.loadings_.ravel()
cong = {}
for name, items in [('SHAI', SHAI), ('CSS', CSS)]:
    la = loads(d.loc[d.language == 'Arabic', items]); lb = loads(d.loc[d.language == 'English', items])
    cong[name] = abs(float(np.dot(la, lb)/np.sqrt(np.dot(la, la)*np.dot(lb, lb))))  # sign of a factor is arbitrary
R['tucker_congruence'] = cong

# ======================= 11. Medical students vs others: does medical knowledge buffer? =======================
ms = []
for c in ['SHAI', 'CSS', 'CSS_excess', 'CSS_compul', 'CSS_distress', 'CSS_reassur', 'trust']:
    a = d.loc[d.medical_student == 1, c]; b = d.loc[d.medical_student == 0, c]
    U, p = stats.mannwhitneyu(a, b); ms.append(dict(Var=c, Med=f'{a.mean():.2f}±{a.std():.2f}', Other=f'{b.mean():.2f}±{b.std():.2f}', p=p))
T['T25_medstudents'] = pd.DataFrame(ms).round(4)
r_ms = stats.pearsonr(d.loc[d.medical_student == 1, 'SHAI'], d.loc[d.medical_student == 1, 'CSS'])[0]
r_ot = stats.pearsonr(d.loc[d.medical_student == 0, 'SHAI'], d.loc[d.medical_student == 0, 'CSS'])[0]
zz = (np.arctanh(r_ms)-np.arctanh(r_ot))/np.sqrt(1/(132-3)+1/(168-3))
R['medstud_corr'] = dict(r_med=r_ms, r_other=r_ot, z=zz, p=2*(1-stats.norm.cdf(abs(zz))))
# correlations within each subgroup
sg = []
for gl, g in [('Gender', 'gender'), ('Study/work', 'occupation'), ('Age group', 'age4'), ('Chronic', 'chronic'), ('Tool profile', 'tool_profile'), ('Language', 'language')]:
    for lv in d[g].unique():
        s = d[d[g] == lv]
        if len(s) >= 15:
            r_, p_ = stats.pearsonr(s.SHAI, s.CSS); ci_ = pg.corr(s.SHAI, s.CSS)['CI95'].iloc[0]
            sg.append(dict(Grouping=gl, Level=str(lv), n=len(s), r=r_, CI=f'{ci_[0]:.2f}–{ci_[1]:.2f}', p=p_))
T['T26_subgroup_corr'] = pd.DataFrame(sg).round(4)

# ======================= 12. Sensitivity =======================
sens = {}
nf = d[d.flag_note == '']
sens['excluding_flagged_r'] = stats.pearsonr(nf.SHAI, nf.CSS)[0]
# straight-lining check on CSS (all same answer)
sl = (d[CSS].nunique(axis=1) == 1) | (d[SHAI].nunique(axis=1) == 1)
sens['straightliners'] = int(sl.sum())
s2 = d[~sl]; sens['excluding_straightliners_r'] = stats.pearsonr(s2.SHAI, s2.CSS)[0]; sens['n_after'] = len(s2)
# Spearman robust; alternative cut-off
for cut in [15, 18, 22]:
    sens[f'prev_SHAI_ge_{cut}'] = float((d.SHAI >= cut).mean()*100)
# bootstrap OLS coefficient of SHAI on CSS
bs = []
for _ in range(2000):
    s = d.iloc[rng.integers(0, n, n)]
    try: bs.append(smf.ols(m3.model.formula, s).fit().params['SHAI'])
    except Exception: pass
sens['boot_B_SHAI_CI'] = list(np.percentile(bs, [2.5, 97.5]))
# timing: early vs late responders
med_t = d.timestamp.median(); early = d.timestamp <= med_t
sens['early_late_SHAI_p'] = stats.mannwhitneyu(d.loc[early, 'SHAI'], d.loc[~early, 'SHAI'])[1]
sens['early_late_CSS_p'] = stats.mannwhitneyu(d.loc[early, 'CSS'], d.loc[~early, 'CSS'])[1]
R['sensitivity'] = sens
R['prevalences'] = dict(HA_clin=float(d.HA_clin.mean()*100), HA_clin_CI=[float(x*100) for x in sm.stats.proportion_confint(d.HA_clin.sum(), n, method='wilson')])
R['dates'] = [str(d.timestamp.min().date()), str(d.timestamp.max().date())]
# item endorsement (Often/Always) for CSS items and SHAI item level 2-3
end = []
for it, nm in zip(CSS, css_names):
    end.append(dict(Scale='CSS-12', Item=nm, pct_often_always=round((d[it] >= 4).mean()*100, 1), mean=round(d[it].mean(), 2)))
for it, nm in zip(SHAI, shai_names):
    end.append(dict(Scale='SHAI-14', Item=nm, pct_often_always=round((d[it] >= 2).mean()*100, 1), mean=round(d[it].mean(), 2)))
T['T27_item_endorsement'] = pd.DataFrame(end)

# item x item: every SHAI item with every CSS item (14 x 12 = 168 Spearman tests, FDR within the family)
ii = []
for si, sn in zip(SHAI, shai_names):
    for ci_, cn in zip(CSS, css_names):
        r_, p_ = stats.spearmanr(d[si], d[ci_]); ii.append(dict(SHAI_item=si.upper(), SHAI_content=sn, CSS_item=ci_.upper(), CSS_content=cn, rho=r_, p=p_))
II = pd.DataFrame(ii); II['q_FDR'] = multipletests(II.p, method='fdr_bh')[1]; II['p_Holm'] = multipletests(II.p, method='holm')[1]
T['T28_item_by_item'] = II.round(4)
R['item_by_item'] = dict(n=len(II), sig_fdr=int((II.q_FDR < .05).sum()), sig_holm=int((II.p_Holm < .05).sum()),
                         top=II.sort_values('rho', ascending=False).head(5)[['SHAI_content', 'CSS_content', 'rho']].values.tolist())
d.to_pickle(f'{OUT}/analysed.pkl')
with pd.ExcelWriter(f'{OUT}/tables/all_results.xlsx') as xw:
    for k, v in T.items(): v.to_excel(xw, sheet_name=k[:31])
json.dump(R, open(f'{OUT}/summary.json', 'w'), indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
print(json.dumps(R, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
