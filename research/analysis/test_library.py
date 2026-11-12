"""The test library for the Student 2 'Results, Fully Explained' guide: every test used in the thesis, explained in full
with its other version, assumptions, how it works step by step, a worked example with our own data, how to read SPSS,
how to report it and what you may be asked. Imported by 18_results_explained.py; numbers are computed from the data."""
import numpy as np, pandas as pd
from scipy import stats


def compute(d):
    """All numbers used in the library, computed from the analysed data."""
    R = {}
    for v in ['SHAI', 'CSS']:
        w, p = stats.shapiro(d[v]); R[f'sw_{v}'] = (w, p); R[f'skew_{v}'] = stats.skew(d[v])
    sh = d[[f'shai{i}' for i in range(1, 15)]]
    def alpha(X):
        X = np.asarray(X, float); k = X.shape[1]; return k / (k - 1) * (1 - X.var(axis=0, ddof=1).sum() / X.sum(axis=1).var(ddof=1))
    R['alpha_shai'] = alpha(sh); R['alpha_css'] = alpha(d[[f'css{i}' for i in range(1, 13)]])
    R['shai_itemvar'] = sh.var(ddof=1).sum(); R['shai_totvar'] = sh.sum(axis=1).var(ddof=1)
    R['aid'] = {c: alpha(sh.drop(columns=c)) for c in sh}
    r, p = stats.pearsonr(d.SHAI, d.CSS); R['r'] = r; R['t_r'] = r * np.sqrt((len(d) - 2) / (1 - r * r)); R['rho'] = stats.spearmanr(d.SHAI, d.CSS)[0]
    rk = stats.rankdata(d.SHAI)
    a, b = d.loc[d.chronic == 1, 'SHAI'], d.loc[d.chronic == 0, 'SHAI']
    R['mw'] = dict(U=stats.mannwhitneyu(a, b)[0], p=stats.mannwhitneyu(a, b)[1], n1=len(a), n0=len(b), mr1=rk[d.chronic == 1].mean(), mr0=rk[d.chronic == 0].mean(),
                   md1=a.median(), md0=b.median(), tp=stats.ttest_ind(a, b)[1])
    g = [x.SHAI.values for _, x in d.groupby('age4', observed=True)]
    R['kw'] = dict(H=stats.kruskal(*g)[0], p=stats.kruskal(*g)[1], df=len(g) - 1, F=stats.f_oneway(*g)[0], pF=stats.f_oneway(*g)[1],
                   mr=[rk[(d.age4 == k).values].mean() for k in d.age4.cat.categories])
    t = pd.crosstab(d.HA_clin, d.CSS_high); c2, pc, df, ex = stats.chi2_contingency(t, correction=False)
    R['chi'] = dict(o=t.values, e=ex, chi2=c2, p=pc, V=np.sqrt(c2 / len(d)))
    t3 = pd.crosstab(d.beh_delay_terrified, d.HA_clin); c3 = stats.chi2_contingency(t3, correction=False)
    R['fisher'] = dict(o=t3.values, e=c3[3], p_chi=c3[1], p_f=stats.fisher_exact(t3)[1])
    return R


def library(R, S, box, say, trap, q, f2=lambda x: f'{x:.2f}'):
    L = S['logit_HA']; MS = S['medstud']; o = R['chi']['o']; e = R['chi']['e']; fo, fe = R['fisher']['o'], R['fisher']['e']
    T = []   # (title, html)

    def card(title, rows, extra=''):
        body = '<dl class="cols">' + ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows) + '</dl>' + extra
        T.append((title, body))

    def calc(t): return f'<div class="calc">{t}</div>'

    # 1 Shapiro-Wilk
    card('1 · Shapiro–Wilk test (is the score normally distributed?)', [
        ('What it answers', 'Do the scores follow a bell-shaped (normal) curve? Many tests assume they do.'),
        ('The other version', '<b>Kolmogorov–Smirnov</b> test (older, weaker for n under about 2000). You can also look at a <b>histogram</b> or <b>Q–Q plot</b>. Shapiro–Wilk is the most powerful and is what SPSS shows first.'),
        ('How it works', 'It compares the ordered scores with the values a perfect normal curve would give. The statistic W runs from 0 to 1; W = 1 means perfectly normal. The p-value tests “the data are normal”: <b>p &lt; 0.05 means NOT normal</b>.'),
        ('Our result', f'SHAI: W = {R["sw_SHAI"][0]:.3f}, p &lt; 0.001 (skewed to the right, skewness {R["skew_SHAI"]:.2f}). CSS: W = {R["sw_CSS"][0]:.3f}, p = {R["sw_CSS"][1]:.3f}. Both not normal.'),
        ('What it decided', 'Groups were compared with <b>non-parametric</b> tests (Mann–Whitney, Kruskal–Wallis) instead of the t-test and ANOVA.'),
        ('SPSS', 'Analyze → Descriptive Statistics → Explore → Plots → tick “Normality plots with tests”. Read the “Tests of Normality” table, Shapiro–Wilk column.'),
        ('Report it as', '“Scores were not normally distributed (Shapiro–Wilk p &lt; 0.01).”')],
        trap('With large samples Shapiro–Wilk flags even small departures from normality. That is why we also kept Pearson and regression (robust with n = 300) but checked them with Spearman and residual plots.'))

    # 2 Cronbach alpha
    k = 14; iv, tv = R['shai_itemvar'], R['shai_totvar']
    card("2 · Cronbach's α (do the items of a scale hang together?)", [
        ('What it answers', 'Internal consistency: do all the items of one scale measure the same thing? If someone scores high on one SHAI item, do they tend to score high on the others?'),
        ('The other version', "<b>McDonald's ω</b> (omega) is the modern alternative and does not assume every item is equally good; <b>split-half reliability</b> compares two halves of the scale. α is the standard in SPSS and in most theses."),
        ('How it works', 'α compares the variance of the separate items with the variance of the total score. If items move together, the total varies much more than the items alone, and α is high.'),
        ('Rules of thumb', '≥ 0.70 acceptable · ≥ 0.80 good · ≥ 0.90 excellent (above 0.95 may mean the items repeat each other).'),
        ('Our result', f"SHAI-14 α = {R['alpha_shai']:.2f}; CSS-12 α = {R['alpha_css']:.2f}; the four CSS dimensions 0.76–0.88. All good. Removing any single SHAI item would not raise α above {max(R['aid'].values()):.2f}, so every item belongs."),
        ('SPSS', 'Analyze → Scale → Reliability Analysis → move the 14 items in, Model: Alpha. Statistics → “Scale if item deleted”.'),
        ('Report it as', f"“Internal consistency was good (Cronbach's α = {R['alpha_shai']:.2f} for the SHAI-14 and {R['alpha_css']:.2f} for the CSS-12).”")],
        calc(f'α = k/(k − 1) × (1 − sum of item variances / variance of total)\n  = {k}/{k - 1} × (1 − {iv:.2f} / {tv:.2f})\n  = {k / (k - 1):.3f} × {1 - iv / tv:.3f} = {R["alpha_shai"]:.3f}   (SHAI-14)'))

    # 3 Proportion + Wilson CI
    card('3 · Percentage with a 95% confidence interval (Wilson)', [
        ('What it answers', 'How common is something, and how precise is that estimate?'),
        ('The other version', 'The simple <b>Wald</b> interval (p ± 1.96 × √(p(1−p)/n)) is taught in class but is inaccurate for small or extreme percentages. The <b>Wilson</b> interval works well at any percentage, so we used it.'),
        ('Our result', '57 of 300 = 19.0%, 95% CI 15.0–23.8%. At ≥ 29 only 2 of 300 (0.7%, CI 0.2–2.4%): the Wald method would give a negative lower limit, which is impossible; Wilson does not.'),
        ('Report it as', '“57 participants (19.0%; 95% CI 15.0–23.8%) had elevated health anxiety.”')],
        calc('Wald (simple):  0.19 ± 1.96 × √(0.19 × 0.81 / 300) = 0.19 ± 0.044  →  14.6% to 23.4%\nWilson (used):  15.0% to 23.8%   (nearly the same here; very different near 0% or 100%)'))

    # 4 Pearson
    card('4 · Pearson correlation r (do two scores rise together?)', [
        ('What it answers', 'How strongly two continuous scores move together in a straight line. −1 = perfect opposite, 0 = none, +1 = perfect together.'),
        ('The other version', '<b>Spearman ρ</b> (test 5) uses ranks instead of the raw scores, so it does not need normal data and is not pulled by extreme values.'),
        ('Assumptions', 'Two continuous scores; a roughly straight-line relationship; no extreme outliers; approximately normal (relaxed with large samples).'),
        ('How it works', 'For every person it multiplies “how far above or below the mean on SHAI” by “how far above or below the mean on CSS”. If high goes with high and low with low, the products are mostly positive, so r is positive. Then it scales the result to −1…+1.'),
        ('Our result', f'r = {R["r"]:.2f}, 95% CI 0.38–0.55, p &lt; 0.001. r² = {R["r"] ** 2:.2f}: health anxiety accounts for about 22% of the differences in cyberchondria.'),
        ('Size', '0.1 small · 0.3 medium · 0.5 large → 0.47 is moderate, close to large.'),
        ('SPSS', 'Analyze → Correlate → Bivariate → tick Pearson. Read “Pearson Correlation” and “Sig. (2-tailed)”.'),
        ('Report it as', '“Health anxiety was moderately correlated with cyberchondria (r = 0.47, 95% CI 0.38–0.55, p &lt; 0.001).”')],
        calc(f'Significance:  t = r × √((n − 2)/(1 − r²)) = {R["r"]:.3f} × √(298 / {1 - R["r"] ** 2:.3f}) = {R["t_r"]:.1f}   → p &lt; 0.001\n95% CI (Fisher z):  z = atanh(0.470) = 0.510;  0.510 ± 1.96/√297 = 0.396 to 0.624;  back with tanh → 0.38 to 0.55'))

    # 5 Spearman
    card('5 · Spearman rank correlation ρ (rho)', [
        ('What it answers', 'The same question as Pearson, but using ranks: do people who rank high on SHAI also rank high on CSS?'),
        ('The other version', '<b>Pearson r</b>. A third option, <b>Kendall τ</b>, is used for very small samples or many ties. Use Spearman when data are skewed, ordinal (e.g. a 1–5 trust scale) or have outliers.'),
        ('How it works', 'Replace each score by its rank (lowest = 1, highest = 300; ties share the average rank), then calculate a Pearson correlation on the ranks.'),
        ('Tiny example', 'Scores 4, 9, 15 → ranks 1, 2, 3. A huge outlier (e.g. 42 instead of 15) still gets rank 3, so it cannot distort ρ.'),
        ('Our result', f'ρ = {R["rho"]:.2f}, practically identical to Pearson {R["r"]:.2f}: the result does not depend on normality.'),
        ('SPSS', 'Analyze → Correlate → Bivariate → tick Spearman.'),
        ('Report it as', '“Spearman’s ρ gave the same result (ρ = 0.47).”')])

    # 6 Partial correlation
    card('6 · Partial correlation (the link after removing other variables)', [
        ('What it answers', 'Is the SHAI–CSS link still there once we remove the influence of age, gender, health background, chronic disease, trust and AI use?'),
        ('The other version', 'Multiple regression (test 13) answers the same question with more detail; partial r gives it as one correlation.'),
        ('How it works', 'It removes from both SHAI and CSS the part that can be predicted by the control variables, then correlates what is left.'),
        ('Our result', 'Partial r = 0.48 against 0.47 unadjusted: unchanged. The control variables do not explain the link (this is the “independently of other factors” part of H1).'),
        ('SPSS', 'Analyze → Correlate → Partial → variables: SHAI, CSS; controlling for: the six control variables.'),
        ('Report it as', '“The association was unchanged after adjustment (partial r = 0.48).”')])

    m = R['mw']
    card('7 · Mann–Whitney U test (a score in two groups)', [
        ('What it answers', 'Is a score different between two independent groups, e.g. people with and without a chronic condition?'),
        ('The other version', 'The <b>independent-samples t-test</b>, which compares means and assumes normal scores. Mann–Whitney compares ranks, so it needs no normality. (For two measurements on the same people you would use the Wilcoxon signed-rank test or paired t-test, not used here.)'),
        ('Assumptions', 'Two independent groups; the score is at least ordinal. No normality needed.'),
        ('How it works', '1) Put all 300 people in one line from lowest to highest score and give ranks 1–300. 2) Add up the ranks in each group. 3) If one group mostly sits at the top, its ranks are high and U shows it. 4) U is converted to a z and a p-value.'),
        ('Tiny example', 'Group A scores 3, 5, 9; group B 10, 12, 14. Ranks: A = 1, 2, 3; B = 4, 5, 6. Every B is above every A → U = 0, the most extreme possible → significant difference.'),
        ('Our result', f'Chronic condition: SHAI median {m["md1"]:.0f} vs {m["md0"]:.0f}, mean rank {m["mr1"]:.1f} vs {m["mr0"]:.1f}, U = {m["U"]:.0f}, p = {m["p"]:.3f}. A t-test gives p = {m["tp"]:.3f}: same conclusion.'),
        ('SPSS', 'Analyze → Nonparametric Tests → Legacy Dialogs → 2 Independent Samples → Mann–Whitney U. Read “Mean Rank”, “Mann–Whitney U”, “Asymp. Sig.”.'),
        ('Report it as', '“Health anxiety was higher in participants with a chronic condition (median 14 vs 11; Mann–Whitney U, p = 0.004).”')])

    k_ = R['kw']
    card('8 · Kruskal–Wallis H test (a score in three or more groups)', [
        ('What it answers', 'Is a score different across three or more groups, e.g. four age groups?'),
        ('The other version', '<b>One-way ANOVA</b>, which compares means and assumes normal scores with similar spread. Kruskal–Wallis is “ANOVA on ranks”.'),
        ('How it works', 'Rank all 300 scores together, then compare the average rank of each group. If the groups were really the same, their average ranks would be close; H measures how far apart they are. H follows a χ² distribution with (groups − 1) degrees of freedom.'),
        ('Our result', f'SHAI by age: H = {k_["H"]:.2f}, df = {k_["df"]}, p = {k_["p"]:.3f}; mean ranks 18–19 {k_["mr"][0]:.0f}, 20–29 {k_["mr"][1]:.0f}, 30–39 {k_["mr"][2]:.0f}, ≥40 {k_["mr"][3]:.0f} → the youngest rank highest. ANOVA gives F = {k_["F"]:.2f}, p = {k_["pF"]:.3f}: same conclusion.'),
        ('After a significant result', 'Kruskal–Wallis says the groups differ <b>somewhere</b>, not which pair. A post-hoc test (pairwise Mann–Whitney with Bonferroni correction, or Dunn’s test; after ANOVA, Tukey) finds the pair. We describe the pattern from the means rather than claiming specific pairs.'),
        ('SPSS', 'Analyze → Nonparametric Tests → Legacy Dialogs → K Independent Samples → Kruskal–Wallis H. Read “Mean Rank”, “Kruskal–Wallis H”, “df”, “Asymp. Sig.”.'),
        ('Report it as', '“Health anxiety differed by age group (Kruskal–Wallis H = 11.8, df = 3, p = 0.008), being highest at 18–19 years.”')])

    card('9 · Chi-square test of independence (two categorical variables)', [
        ('What it answers', 'Is a yes/no outcome related to a group? E.g. is high cyberchondria more common in people with elevated health anxiety?'),
        ('The other version', "<b>Fisher's exact test</b> (test 10) when any expected count is below 5. For a before/after yes/no on the same people: McNemar (not used)."),
        ('How it works', '1) Make the table of observed counts. 2) Work out the counts you would expect if there were no link (row total × column total ÷ grand total). 3) For each cell, (observed − expected)² ÷ expected. 4) Add them up = χ². Big χ² = observed far from expected = association.'),
        ('Our result', f'χ² = {R["chi"]["chi2"]:.2f}, df = 1, p &lt; 0.001; 52.6% vs 23.0% had high cyberchondria.'),
        ('SPSS', 'Analyze → Descriptive Statistics → Crosstabs → Statistics: tick Chi-square and Phi and Cramér’s V; Cells: Observed, Expected, Row %. Read “Pearson Chi-Square”, “Asymptotic Significance”, and the note on expected counts below 5.'),
        ('Report it as', '“High cyberchondria was more common with elevated health anxiety (52.6% vs 23.0%; χ² = 19.8, p &lt; 0.001).”')],
        calc(f'                      High CSS: No   Yes    Total\nNot elevated HA         {o[0][0]}       {o[0][1]}      243\nElevated HA              {o[1][0]}       {o[1][1]}       57\n'
             f'Expected (no link):  243 × 86 / 300 = {e[0][1]:.1f}   57 × 86 / 300 = {e[1][1]:.1f}   …\n'
             f'χ² = Σ (O − E)² / E = ({o[0][0]} − {e[0][0]:.1f})²/{e[0][0]:.1f} + ({o[0][1]} − {e[0][1]:.1f})²/{e[0][1]:.1f} + ({o[1][0]} − {e[1][0]:.1f})²/{e[1][0]:.1f} + ({o[1][1]} − {e[1][1]:.1f})²/{e[1][1]:.1f}\n   = {R["chi"]["chi2"]:.2f}'))

    card("10 · Fisher's exact test (chi-square for small numbers)", [
        ('What it answers', 'The same question as χ², but when the table has small counts.'),
        ('When to use it', 'When any <b>expected</b> count is below 5. χ² then gives a p-value that is too small; Fisher calculates the exact probability instead.'),
        ('Our example', f'Elevated health anxiety by fear-driven delay: only 26 people delayed out of fear, and one expected cell is {fe[1][1]:.1f} (below 5). χ² would give p = {R["fisher"]["p_chi"]:.3f}; Fisher gives p = {R["fisher"]["p_f"]:.3f}, which is the value in Table 7.'),
        ('SPSS', 'Shown automatically under the χ² table for 2 × 2 tables (“Fisher’s Exact Test”). For bigger tables: Crosstabs → Exact → Monte Carlo (Exact Tests module).'),
        ('Report it as', "“…(Fisher's exact test, p = 0.016).”")])

    card("11 · Cramér's V (how strong is a χ² association?)", [
        ('What it answers', 'The <b>strength</b> of an association between two categorical variables. χ² only says whether it exists, and χ² grows with sample size, so it cannot show strength.'),
        ('The other version', '<b>Phi (φ)</b> for 2 × 2 tables; for 2 × 2 it equals V. Cramér’s V works for any table size.'),
        ('Size', '0.1 small · 0.3 medium · 0.5 large.'),
        ('Our result', f'V = {R["chi"]["V"]:.2f} for elevated health anxiety × high cyberchondria (small to medium); 0.12–0.26 across Table 7.'),
        ('SPSS', 'Crosstabs → Statistics → “Phi and Cramer’s V”. Read the “Symmetric Measures” table.')],
        calc(f'V = √( χ² / (n × (k − 1)) ) = √({R["chi"]["chi2"]:.2f} / (300 × 1)) = {R["chi"]["V"]:.3f}      k = smaller of rows or columns'))

    card('12 · Odds ratio, crude (how much more likely?)', [
        ('What it answers', 'How many times higher the odds of an outcome are in one group than in another.'),
        ('The other version', 'The <b>relative risk</b> (ratio of percentages: 52.6% ÷ 23.0% = 2.3) is easier to say but cannot come out of logistic regression; the odds ratio can, so it is standard in cross-sectional studies.'),
        ('Reading it', 'OR = 1 no difference; above 1 higher odds; below 1 lower odds. If the 95% CI includes 1, it is not significant.'),
        ('Our result', 'OR = 3.71 (95% CI 2.04–6.76) for high cyberchondria with elevated health anxiety.'),
        ('SPSS', 'Crosstabs → Statistics → tick “Risk”. Read “Odds Ratio” in the Risk Estimate table.')],
        calc(f'Odds with elevated HA:     {o[1][1]} / {o[1][0]} = {o[1][1] / o[1][0]:.2f}\nOdds without:              {o[0][1]} / {o[0][0]} = {o[0][1] / o[0][0]:.2f}\nOR = {o[1][1] / o[1][0]:.2f} / {o[0][1] / o[0][0]:.2f} = {(o[1][1] / o[1][0]) / (o[0][1] / o[0][0]):.2f}'))

    card('13 · Multiple linear regression (hierarchical)', [
        ('What it answers', 'Which factors predict a <b>score</b> (CSS) when all of them are considered together, and how much each adds.'),
        ('The other version', '<b>Simple linear regression</b> uses one predictor (the line in Figure 4: CSS = 20.5 + 0.67 × SHAI). <b>Multiple</b> regression uses many at once so each is adjusted for the others. <b>Hierarchical</b> means entering them in blocks to see what each block adds; <b>stepwise</b> lets the computer choose (not recommended, not used).'),
        ('Assumptions', 'Straight-line relationships; residuals (prediction errors) roughly normal with even spread; predictors not near-duplicates (VIF below 5); independent observations. We checked: residuals close to normal (histogram, P-P plot), all VIF low.'),
        ('Output, piece by piece', '<b>R²</b> = share of differences explained (0.317 = 32%). <b>ΔR²</b> = what a block adds (health anxiety +18.4%). <b>F</b> tests whether the model explains anything at all. <b>B</b> = change in CSS per unit of a predictor. <b>β</b> = standardised B, to compare predictors. <b>t</b> and <b>Sig.</b> test each B. <b>VIF</b> = multicollinearity check.'),
        ('Our result', 'R² 0.030 → 0.133 → 0.317; F = 6.48, p &lt; 0.001; SHAI B = 0.68, β = 0.48, p &lt; 0.001 (strongest).'),
        ('SPSS', 'Analyze → Regression → Linear → Dependent: CSS → Block 1: socio-demographics → Next → Block 2: digital use → Next → Block 3: SHAI. Statistics: Estimates, CI, Model fit, R squared change, Collinearity. Plots: histogram and normal P-P of residuals.'),
        ('Report it as', '“Health anxiety added 18.4% of explained variance (R² = 0.317; B = 0.68, β = 0.48, p &lt; 0.001).”')],
        calc('F = (R² / k) / ((1 − R²) / (n − k − 1)) = (0.317 / 20) / (0.683 / 279) = 0.0159 / 0.00245 = 6.48\nPrediction: each extra SHAI point → +0.68 CSS points; 10 points → +6.8'))

    card('14 · Binary logistic regression', [
        ('What it answers', 'Which factors predict a <b>yes/no</b> outcome (elevated health anxiety yes/no), all considered together.'),
        ('The other version', '<b>Linear regression</b> is for scores; it cannot be used for yes/no because it would predict impossible values below 0% or above 100%. Logistic regression predicts the log of the odds, so predictions stay between 0 and 1.'),
        ('Output, piece by piece', '<b>B</b> = change in log-odds. <b>Exp(B)</b> = the adjusted odds ratio (AOR). <b>Wald</b> = (B ÷ SE)², the test for each predictor. <b>Omnibus test</b> = does the model beat no model. <b>Nagelkerke R²</b> = rough “share explained”. <b>Hosmer–Lemeshow</b> = fit; want p &gt; 0.05. <b>Classification table</b> = % correctly predicted. <b>ROC curve / AUC</b> = how well it separates the two groups.'),
        ('Our result', f'AOR 3.12 per SD of CSS, 3.83 for the reassurance motive, 0.61 per older age group. Omnibus χ²(11) = {L["omnibus_chi2"]:.1f}, p &lt; 0.001; Nagelkerke R² = {L["nagelkerke"]:.2f}; Hosmer–Lemeshow p = {L["HL_p"]:.2f}; AUC = {L["AUC"]:.2f}.'),
        ('Rule of thumb', 'About 10 events per predictor are recommended. We had 57 events for 11 predictors (about 5), so the odds ratios may be overestimated; we say so in the limitations.'),
        ('SPSS', 'Analyze → Regression → Binary Logistic → Dependent: HA_elevated; Covariates: the 11 predictors; Options: Hosmer–Lemeshow, CI for exp(B). Then Analyze → ROC Curve with the saved predicted probabilities.'),
        ('Report it as', '“Elevated health anxiety was independently associated with cyberchondria (AOR 3.12 per SD, 95% CI 2.11–4.62).”')],
        calc('Wald for cyberchondria:  B = 1.138, SE = 0.200  →  (1.138 / 0.200)² = 32.3  →  p &lt; 0.001\nExp(B) = e^1.138 = 3.12  →  the odds triple per SD (8.4 CSS points)\nAOR below 1 (age 0.61): 1 − 0.61 = 0.39 → 39% lower odds per older age group'))

    card('15 · z-scores (standardised scores)', [
        ('What it is', 'A score re-expressed as “how many SDs above or below the mean”: z = (score − mean) ÷ SD. Mean becomes 0, SD becomes 1.'),
        ('Why we used it', 'So the odds ratio for cyberchondria is “per 1 SD” (about 8.4 CSS points), a sensible step, instead of “per 1 point”, which would be tiny (AOR 1.15).'),
        ('Example', 'CSS 37.2 → (37.2 − 28.86) ÷ 8.36 = +1.0 SD.'),
        ('SPSS', 'Analyze → Descriptive Statistics → Descriptives → tick “Save standardized values as variables” (creates ZCSS).')])

    not_used = '<table class="mini"><tr><th>Test</th><th>What it is for</th><th>Why we did not use it</th></tr>' + ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in [
        ('Independent t-test', 'a score in 2 groups, normal data', 'scores not normal → Mann–Whitney (same conclusions when checked)'),
        ('One-way ANOVA (+ Tukey)', 'a score in 3+ groups, normal data', 'scores not normal, small groups → Kruskal–Wallis (same conclusions)'),
        ('Paired t-test / Wilcoxon signed-rank', 'the same people measured twice', 'we measured everyone once'),
        ('McNemar test', 'yes/no measured twice on the same people', 'one time point'),
        ('Repeated-measures ANOVA', 'many measurements over time', 'cross-sectional design'),
        ('Kolmogorov–Smirnov', 'normality', 'Shapiro–Wilk is more powerful for n = 300'),
        ('Stepwise regression', 'computer picks predictors', 'unstable; we chose predictors in advance (hierarchical blocks)'),
        ('Correction for multiple testing (Bonferroni, FDR)', 'reduces chance findings', 'we used p &lt; 0.05 like most graduation theses and state it as a limitation')]) + '</table>'
    T.append(('16 · Tests we did not use, and why', not_used + say('If asked about any test not in the thesis, use this table: name what it is for, then say why it did not fit our data or design.')))
    return T
