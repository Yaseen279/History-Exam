"""Measurement invariance of SHAI-14 and CSS-12 across Arabic vs English responders.
(1) Multi-group CFA (ML with mean structure): configural -> metric -> scalar, chi2/CFI/RMSEA, delta criteria.
(2) Item-level DIF: ordinal logistic regression (Zumbo): item ~ total; + language; + total x language.
Usage: python3 02c_invariance.py <analysed.pkl> <out dir>
"""
import sys, numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel

d = pd.read_pickle(sys.argv[1])
SHAI = [f'shai{k}' for k in range(1, 15)]; CSS = [f'css{k}' for k in range(1, 13)]
grp = d.language.values; G = ['Arabic', 'English']

def group_stats(items):
    out = []
    for g in G:
        X = d.loc[d.language == g, items].values.astype(float)
        n = len(X); m = X.mean(0); S = np.cov(X, rowvar=False, bias=True)
        out.append((n, m, S))
    return out

def fit_mgcfa(items, pattern, level):
    """pattern: p x k 0/1 loading pattern. level: 'configural' | 'metric' | 'scalar'."""
    gs = group_stats(items); p, k = pattern.shape; idx = np.argwhere(pattern == 1)
    nl = len(idx); ncorr = k * (k - 1) // 2
    # parameter blocks
    blocks = []
    def add(name, size, g=None): blocks.append((name, size, g))
    for gi in range(2):
        if level == 'configural' or gi == 0: add('lam', nl, gi if level == 'configural' else 'shared')
        add('theta', p, gi)
        add('corr', ncorr, gi)
        if gi == 1 and level != 'configural': add('fsd', k, gi)          # factor SDs free in group 2
        if level == 'scalar':
            if gi == 0: add('nu', p, 'shared')
            if gi == 1: add('alpha', k, gi)                                # latent means free in group 2
        else:
            add('nu', p, gi)                                               # intercepts free (saturated means)
    sizes = [b[1] for b in blocks]; offs = np.cumsum([0] + sizes)
    def unpack(theta_vec, gi):
        par = {}
        for (name, size, g), o in zip(blocks, offs[:-1]):
            if g == gi or g == 'shared': par[name] = theta_vec[o:o + size]
        return par
    def implied(theta_vec, gi):
        par = unpack(theta_vec, gi)
        L = np.zeros((p, k)); L[idx[:, 0], idx[:, 1]] = par['lam']
        # correlation matrix via normalised Cholesky rows
        C = np.eye(k); C[np.tril_indices(k, -1)] = par['corr'] if ncorr else []
        C = C / np.linalg.norm(C, axis=1, keepdims=True); R = C @ C.T
        sd = np.exp(par['fsd']) if 'fsd' in par else np.ones(k)
        Phi = np.outer(sd, sd) * R
        Th = np.diag(np.exp(par['theta']))
        Sig = L @ Phi @ L.T + Th
        al = par['alpha'] if 'alpha' in par else np.zeros(k)
        mu = par['nu'] + L @ al
        return Sig, mu
    def F(theta_vec):
        tot = 0.0
        for gi, (n, m, S) in enumerate(gs):
            Sig, mu = implied(theta_vec, gi)
            sign, logdet = np.linalg.slogdet(Sig)
            if sign <= 0: return 1e10
            Si = np.linalg.inv(Sig); dm = m - mu
            tot += n * (logdet + np.trace(S @ Si) + dm @ Si @ dm - np.linalg.slogdet(S)[1] - p)
        return tot
    x0 = []
    for name, size, g in blocks:
        x0 += {'lam': [0.6] * size, 'theta': [np.log(0.6)] * size, 'corr': [0.5] * size, 'fsd': [0.0] * size,
               'nu': list(gs[0][1]) if size == p else [0] * size, 'alpha': [0.0] * size}[name]
    res = minimize(F, np.array(x0, float), method='L-BFGS-B', options={'maxiter': 20000, 'maxfun': 200000})
    chi2 = res.fun; npar = len(x0)
    nmom = 2 * (p * (p + 1) // 2 + p)
    df = nmom - npar
    return chi2, df, res.success

def baseline(items):
    gs = group_stats(items); p = len(items); chi2 = 0
    for n, m, S in gs:   # independence model: diagonal Sigma, saturated means
        chi2 += n * (np.sum(np.log(np.diag(S))) - np.linalg.slogdet(S)[1])
    return chi2, 2 * (p * (p - 1) // 2)

def fit_indices(chi2, df, b_chi2, b_df, N):
    cfi = 1 - max(chi2 - df, 0) / max(b_chi2 - b_df, chi2 - df, 1e-9)
    tli = ((b_chi2 / b_df) - (chi2 / df)) / ((b_chi2 / b_df) - 1)
    rmsea = np.sqrt(2) * np.sqrt(max(chi2 - df, 0) / (df * (N - 1)))   # multi-group adjustment (sqrt(G))
    return cfi, tli, rmsea

N = len(d); rows = []
pat_shai = np.ones((14, 1), int)
pat_css = np.zeros((12, 4), int)
for f in range(4): pat_css[3 * f:3 * f + 3, f] = 1
for name, items, pat in [('SHAI-14 (one factor)', SHAI, pat_shai), ('CSS-12 (four factors)', CSS, pat_css)]:
    bchi, bdf = baseline(items); prev = None
    for level in ['configural', 'metric', 'scalar']:
        chi2, df, ok = fit_mgcfa(items, pat, level)
        cfi, tli, rmsea = fit_indices(chi2, df, bchi, bdf, N)
        row = dict(Scale=name, Model=level, chi2=round(chi2, 2), df=df, CFI=round(cfi, 3), TLI=round(tli, 3), RMSEA=round(rmsea, 3), converged=ok)
        if prev is not None:
            dchi, ddf = chi2 - prev['chi2'], df - prev['df']
            row.update(d_chi2=round(dchi, 2), d_df=ddf, p_diff=round(1 - stats.chi2.cdf(dchi, ddf), 3),
                       d_CFI=round(cfi - prev['CFI'], 3), d_RMSEA=round(rmsea - prev['RMSEA'], 3))
        rows.append(row); prev = dict(chi2=chi2, df=df, CFI=cfi, RMSEA=rmsea)
MG = pd.DataFrame(rows)

# ---- item-level DIF (ordinal logistic, Zumbo 1999): McFadden R2 change, Jodoin & Gierl thresholds
dif = []
d['lang_en'] = (d.language == 'English').astype(int)
for scale, items in [('SHAI-14', SHAI), ('CSS-12', CSS)]:
    tot = d[items].sum(axis=1)
    for it in items:
        rest = (tot - d[it]); z = (rest - rest.mean()) / rest.std()
        y = d[it].astype(int)
        y = pd.Series(pd.Categorical(y, ordered=True))
        def fit(X):
            m = OrderedModel(y, X, distr='logit').fit(method='bfgs', disp=0, maxiter=2000)
            return m.llf, m
        X1 = pd.DataFrame({'z': z.values}); X2 = X1.assign(lang=d.lang_en.values); X3 = X2.assign(inter=X2.z * X2.lang)
        ll0 = OrderedModel(y, pd.DataFrame({'c': np.zeros(len(y))}), distr='logit') if False else None
        l1, _ = fit(X1); l2, m2 = fit(X2); l3, _ = fit(X3)
        # null log-likelihood (thresholds only) for McFadden R2
        cats = y.value_counts(normalize=True); lnull = float((y.value_counts() * np.log(cats)).sum())
        r1, r2, r3 = 1 - l1 / lnull, 1 - l2 / lnull, 1 - l3 / lnull
        p_uni = 1 - stats.chi2.cdf(2 * (l2 - l1), 1); p_non = 1 - stats.chi2.cdf(2 * (l3 - l2), 1); p_any = 1 - stats.chi2.cdf(2 * (l3 - l1), 2)
        dif.append(dict(Scale=scale, Item=it.upper(), p_uniform=p_uni, p_nonuniform=p_non, p_any=p_any,
                        dR2_any=r3 - r1, OR_English=float(np.exp(m2.params['lang']))))
DIF = pd.DataFrame(dif)
from statsmodels.stats.multitest import multipletests
DIF['q_any'] = multipletests(DIF.p_any, method='fdr_bh')[1]
DIF['flag'] = np.where((DIF.q_any < 0.05) & (DIF.dR2_any >= 0.035), 'DIF', '')
pd.set_option('display.width', 220)
print(MG.to_string(index=False)); print()
print(DIF.round(3).to_string(index=False))
MG.to_csv(sys.argv[2] + '/invariance_mgcfa.csv', index=False); DIF.round(4).to_csv(sys.argv[2] + '/invariance_dif.csv', index=False)
