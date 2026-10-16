"""Build (1) a one-page summary of findings and (2) a study & defence guide, as HTML for PDF printing.

Usage: python3 06_study_materials.py <outdir>
Writes <outdir>/study/summary.html and <outdir>/study/guide.html; print with headless Chromium.
"""
import sys, json, os
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

OUT = sys.argv[1]; ST = f'{OUT}/study'; os.makedirs(ST, exist_ok=True)
d = pd.read_pickle(f'{OUT}/analysed.pkl')
X = pd.read_excel(f'{OUT}/tables/all_results.xlsx', sheet_name=None, index_col=0)
R = json.load(open(f'{OUT}/summary.json'))
FIG = os.path.abspath(f'{OUT}/figures')
n = len(d)

# ---------------- numbers
pc = lambda k: f'{k/n*100:.1f}%'
cnt = lambda c: int(d[c].sum())
sc = R['main_corr']['SHAI_CSS']; part = R['partial_corr']; prev = R['prevalences']; ss = R['sample_size']
rel = X['T4_reliability'].set_index('Scale'); cfa = X['T6_cfa']; hier = X['T13_hierarchical_CSS']
ols = X['T14_OLS_CSS_full']; lg = X['T18_logit_HA_clin']; beh = X['T19_logit_behaviours']
med = X['T21_mediation']; ser = X['T22_serial_mediation']; mod = X['T23_moderation']
sub = {k: R['main_corr'][f'SHAI_{k}'] for k in ['Excessiveness', 'Compulsion', 'Distress', 'Reassurance']}
ib = R['item_by_item']; sens = R['sensitivity']
b_shai = ols.loc['SHAI']; b_ai = ols.loc['ai_user']
def bh(o, p): return beh[(beh.Outcome == o) & (beh.Predictor == p)].iloc[0]
def mr(pre, path): return med[med.Model.str.startswith(pre) & (med.Path == path)].iloc[0]
mA = mr('A:', 'Indirect'); mAd = mr('A:', 'Direct'); mC = mr('C:', 'Indirect'); mCd = mr('C:', 'Direct'); mD = mr('D:', 'Indirect')
_m = smf.ols("CSS ~ C(age_c, Treatment('20–29')) + female + C(occ_c, Treatment('Non-health employed/other')) + chronic + lang_en + tool_ai + tool_search + tool_medplat + tool_social + trust + mot_reassurance + mot_selfdx + mot_cost + mot_triage + SHAI", d).fit(cov_type='HC3')
ai_alt_B, ai_alt_p = _m.params['tool_ai'], _m.pvalues['tool_ai']
N = dict(
 n=n, d0=pd.Timestamp(R['dates'][0]).strftime('%d %B %Y'), d1=pd.Timestamp(R['dates'][1]).strftime('%d %B %Y'),
 age20=pc(int((d.age_group == '20-29').sum())), fem=pc(cnt('female')), med=pc(cnt('medical_student')), hb=pc(cnt('health_background')),
 chron=pc(cnt('chronic')), ar=pc(int((d.language == 'Arabic').sum())),
 ai=pc(cnt('ai_user')), se=pc(cnt('tool_search')), mp=pc(cnt('tool_medplat')), sm=pc(cnt('tool_social')),
 ai_only=pc(int((d.tool_profile == 'AI without search engine').sum())), gpt=pc(int((d.ai_model == 'ChatGPT').sum())),
 conv=pc(cnt('mot_convenience')), tri=pc(cnt('mot_triage')), reas=pc(cnt('mot_reassurance')),
 shai_m=f'{d.SHAI.mean():.1f}', shai_sd=f'{d.SHAI.std():.1f}', css_m=f'{d.CSS.mean():.1f}', css_sd=f'{d.CSS.std():.1f}',
 hac=f'{prev["HA_clin"]:.0f}%', hac_ci=f'{prev["HA_clin_CI"][0]:.1f}–{prev["HA_clin_CI"][1]:.1f}%',
 r=f'{sc["pearson_r"]:.2f}', rci=f'{sc["pearson_CI"][0]:.2f}–{sc["pearson_CI"][1]:.2f}', rho=f'{sc["spearman"]:.2f}',
 r2=f'{sc["r2"]*100:.0f}%', pr=f'{part["r"]:.2f}',
 rE=f'{sub["Excessiveness"]["pearson"]:.2f}', rD=f'{sub["Distress"]["pearson"]:.2f}', rC=f'{sub["Compulsion"]["pearson"]:.2f}', rR=f'{sub["Reassurance"]["pearson"]:.2f}',
 aS=f'{rel.loc["SHAI-14","alpha"]:.2f}', aC=f'{rel.loc["CSS-12","alpha"]:.2f}', oS=f'{rel.loc["SHAI-14","omega"]:.2f}', oC=f'{rel.loc["CSS-12","omega"]:.2f}',
 R2a=f'{hier.R2.iloc[0]:.3f}', R2b=f'{hier.R2.iloc[1]:.3f}', R2c=f'{hier.R2.iloc[2]:.3f}', dR2=f'{hier.dR2.iloc[2]*100:.1f}%',
 B=f'{b_shai.B:.2f}', beta=f'{b_shai.beta_std:.2f}', Bai=f'{b_ai.B:.1f}', Baici=f'{b_ai.CI_low:.1f}–{b_ai.CI_high:.1f}',
 Balt=f'{ai_alt_B:.1f}', palt=f'{ai_alt_p:.2f}',
 orCSS=f'{lg.loc["zCSS","AOR"]:.2f}', orMot=f'{lg.loc["mot_reassurance","AOR"]:.2f}', orAge=f'{lg.loc["age_ord","AOR"]:.2f}', auc=f'{R["logit_HA"]["AUC"]:.2f}',
 mA=f'{mA.coef:.2f}', mAci=f'{mA.CI_low:.2f}–{mA.CI_high:.2f}', mAd=f'{mAd.coef:.2f}', mC=f'{mC.coef:.2f}', mCci=f'{mC.CI_low:.2f}–{mC.CI_high:.2f}',
 mCd=f'{mCd.coef:.2f}', mD=f'{mD.coef:.2f}', ser=f'{ser.iloc[2].coef:.2f}',
 dr=pc(cnt('beh_delay_reassured')), ign=pc(cnt('beh_ignore')), mdoc=pc(cnt('beh_multidoc')), urg=pc(cnt('beh_urgent')), smed=pc(cnt('beh_selfmed')), ter=pc(cnt('beh_delay_terrified')),
 never=pc(cnt('share_never')), always=pc(int((d.share == 'Always').sum())), relneg=pc(cnt('rel_negative')), relsig=pc(int((d.relationship == 'Significantly reduced trust').sum())),
 nsS=f'{bh("Never disclose to physician","zSHAI").AOR:.2f}', nsC=f'{bh("Never disclose to physician","zCSS").AOR:.2f}',
 urC=f'{bh("Urgent visit/ER","zCSS").AOR:.2f}', igC=f'{bh("Ignore symptom","zCSS").AOR:.2f}', mdT=f'{bh("Multiple doctors","trust").AOR:.2f}',
 ibF=ib['sig_fdr'], ibH=ib['sig_holm'], cfaC=f'{cfa.iloc[3].CFI:.2f}', cfaR=f'{cfa.iloc[3].RMSEA:.3f}',
 nreq=ss['n_needed_r_0_20'], pw=f'{ss["power_r_0_20"]*100:.0f}%', mdr=f'{ss["min_detectable_r"]:.2f}', moe=f'{ss["moe_at_n"]:.1f}',
 inc=R['ai_inconsistent'], inc_css=f'{d.loc[d.ai_model_inconsistent==1,"CSS"].mean():.1f}', non_css=f'{d.loc[d.ai_user==0,"CSS"].mean():.1f}',
 ms_r=f'{R["medstud_corr"]["r_med"]:.2f}', ot_r=f'{R["medstud_corr"]["r_other"]:.2f}',
)

# numbers + figure aspect ratios for the slide deck
from PIL import Image as _Im
_asp = {f: _Im.open(f'{FIG}/{f}').size for f in os.listdir(FIG) if f.endswith('.png')}
_extra = dict(tools=[float(d.ai_user.mean()*100), float(d.tool_search.mean()*100), float(d.tool_medplat.mean()*100), float(d.tool_social.mean()*100)],
              motives=[float(d[c].mean()*100) for c in ['mot_convenience', 'mot_triage', 'mot_reassurance', 'mot_selfdx', 'mot_cost']],
              behav=[float(d[c].mean()*100) for c in ['beh_delay_reassured', 'beh_ignore', 'beh_multidoc', 'beh_urgent', 'beh_selfmed', 'beh_delay_terrified']],
              share=[float((d.share == k).mean()*100) for k in ['Always', 'Sometimes', 'Never (fear of judgement)']],
              subr=[float(sub[k]['pearson']) for k in ['Excessiveness', 'Distress', 'Compulsion', 'Reassurance']],
              aspect={k: v[0] / v[1] for k, v in _asp.items()}, figdir=FIG)
json.dump({**{k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in N.items()}, **_extra}, open(f'{ST}/numbers.json', 'w'), indent=1)

CSS_BASE = """
@page { size: A4; margin: 14mm 15mm 14mm 15mm; }
:root { --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --rule:#e1e0d9; --blue:#2a78d6; --blue-l:#eaf2fc; --orange:#eb6834; --orange-l:#fdeee7; --green:#0a7d4f; --green-l:#e6f4ee; }
* { box-sizing: border-box; }
body { font-family: 'Inter', 'Liberation Sans', sans-serif; color: var(--ink); margin: 0; background: #fff; font-size: 10pt; line-height: 1.45; }
h1 { font-size: 18pt; line-height: 1.2; margin: 0 0 4px; letter-spacing: -0.01em; }
h2 { font-size: 13pt; margin: 18px 0 6px; color: var(--ink); border-bottom: 2px solid var(--blue); padding-bottom: 3px; }
h3 { font-size: 11pt; margin: 12px 0 4px; color: var(--blue); }
p { margin: 4px 0 6px; }
.muted { color: var(--ink2); }
.small { font-size: 8.5pt; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 6px 0 10px; }
th, td { border-bottom: 1px solid var(--rule); padding: 4px 6px; text-align: left; vertical-align: top; }
th { background: #f5f5f2; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.box { border-radius: 6px; padding: 8px 11px; margin: 8px 0; }
.say { background: var(--blue-l); border-left: 4px solid var(--blue); }
.warn { background: var(--orange-l); border-left: 4px solid var(--orange); }
.ok { background: var(--green-l); border-left: 4px solid var(--green); }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 7px; margin: 8px 0; }
.tile { border: 1px solid var(--rule); border-radius: 6px; padding: 7px 9px; }
.tile .v { font-size: 17pt; font-weight: 700; color: var(--blue); line-height: 1.1; }
.tile .l { font-size: 8pt; color: var(--ink2); line-height: 1.25; margin-top: 2px; }
img { max-width: 100%; display: block; margin: 6px auto; }
.fig { break-inside: avoid; margin: 8px 0 12px; }
.fig .cap { font-size: 8.5pt; color: var(--ink2); text-align: center; }
.qa { break-inside: avoid; margin: 0 0 9px; }
.qa .q { font-weight: 600; }
.qa .a { margin-left: 14px; }
.page-break { break-before: page; }
ol, ul { margin: 4px 0 6px 26px; padding: 0; }
h2, h3 { break-after: avoid; page-break-after: avoid; }
li { margin: 2px 0; }
.slide { border: 1px solid var(--rule); border-radius: 6px; padding: 7px 10px; margin: 0 0 8px; break-inside: avoid; }
.slide .h { font-weight: 700; color: var(--blue); }
.tag { display: inline-block; font-size: 7.5pt; font-weight: 600; padding: 1px 6px; border-radius: 9px; background: #f0efec; color: var(--ink2); margin-left: 6px; }
"""

def img(name, cap, w='100%'):
    return f'<div class="fig"><img src="file://{FIG}/{name}" style="width:{w}"><div class="cap">{cap}</div></div>'

# ============================================================ ONE-PAGE SUMMARY
summary = f"""<!doctype html><html><head><meta charset="utf-8"><title>Summary of Findings</title><style>{CSS_BASE}
@page {{ margin: 11mm 13mm; }}
body {{ font-size: 9.7pt; line-height: 1.42; }}
h2 {{ font-size: 10.5pt; margin: 9px 0 4px; }}
.find li {{ margin: 3px 0; }}
.two {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 12px; }}
</style></head><body>
<div class="muted small">Graduation research · One-page summary of findings</div>
<h1>Artificial Intelligence, Search Engines, and Cyberchondria: A Study of Patient Pre-Consultation Behavior in Baghdad</h1>
<p class="small muted"><b>Design:</b> analytical cross-sectional online survey (Google Forms), Baghdad, {N['d0']} – {N['d1']} · <b>n = {n}</b> adults · <b>Tools:</b> Short Health Anxiety Inventory (SHAI-14, 0–42) and Cyberchondria Severity Scale short form (CSS-12, 12–60; four subscales) · <b>Analysis:</b> Spearman/Pearson and partial correlation, non-parametric tests with FDR correction, robust hierarchical and logistic regression, bootstrapped mediation and moderation.</p>
<div class="tiles">
 <div class="tile"><div class="v">{N['ai']}</div><div class="l">use AI chatbots for symptoms (search engines {N['se']})</div></div>
 <div class="tile"><div class="v">{N['hac']}</div><div class="l">clinically relevant health anxiety (SHAI ≥ 18; 95% CI {N['hac_ci']})</div></div>
 <div class="tile"><div class="v">r = {N['r']}</div><div class="l">health anxiety ↔ cyberchondria (95% CI {N['rci']}), p &lt; 0.001</div></div>
 <div class="tile"><div class="v">{N['never']}</div><div class="l">never tell their doctor about online/AI searches</div></div>
</div>
<div class="two"><div>
<h2>Key findings</h2>
<ol class="find">
 <li><b>AI is now the main gateway.</b> {N['ai']} use AI chatbots (ChatGPT {N['gpt']} of all), ahead of search engines ({N['se']}); {N['ai_only']} use AI without any search engine. Convenience ({N['conv']}), "do I need a doctor?" ({N['tri']}) and instant reassurance ({N['reas']}) are the main motives.</li>
 <li><b>Health anxiety and cyberchondria travel together.</b> r = {N['r']}; unchanged after adjusting for all covariates (partial r = {N['pr']}). Strongest for <i>excessive searching</i> (r = {N['rE']}) and <i>post-search distress</i> (r = {N['rD']}); weaker for compulsion ({N['rC']}) and reassurance seeking ({N['rR']}).</li>
 <li><b>Health anxiety is the dominant predictor of cyberchondria</b> (β = {N['beta']}); demographics explain almost nothing (R² = {N['R2a']}); adding health anxiety raises R² from {N['R2b']} to {N['R2c']}.</li>
 <li><b>What drives searching is fear, not noticing.</b> Fear of serious illness and interpreting sensations track cyberchondria; mere awareness of aches and sensations does not ({N['ibF']}/168 item pairs significant after FDR).</li>
 <li><b>Pattern consistent with a cycle:</b> health anxiety → excessive searching → post-search distress (indirect effect {N['mA']}) → reassurance-seeking visits (distress almost fully mediates; direct effect {N['mCd']}). The reverse path is also significant: compatible with mutual reinforcement, not proof of it.</li>
 <li><b>Who is most anxious:</b> younger people, those with a chronic condition, social-media searchers, and those searching for instant reassurance (AOR {N['orMot']}).</li>
</ol>
</div><div>
<h2>Pre-consultation behaviour</h2>
<ul>
 <li>{N['dr']} delay or skip care because the search reassured them; {N['ign']} ignore the symptom.</li>
 <li>{N['mdoc']} visit several doctors; {N['urg']} seek urgent care/ER; {N['smed']} self-medicate.</li>
 <li>Higher cyberchondria → more urgent visits (AOR {N['urC']}/SD), less ignoring (AOR {N['igC']}/SD).</li>
 <li><b>Concealment paradox:</b> higher health anxiety → <i>more</i> hiding of searches from the doctor (AOR {N['nsS']}); higher cyberchondria → <i>less</i> (AOR {N['nsC']}).</li>
 <li>{N['relneg']} say searching has complicated or reduced their trust in physicians.</li>
</ul>
<h2>AI chatbots</h2>
<p>AI users had higher cyberchondria (B = +{N['Bai']} points, adjusted), mainly excessiveness and reassurance seeking, <b>but</b> this depends on classifying {N['inc']} inconsistent answers and on only 34 non-users. AI use did not change the strength of the anxiety–cyberchondria link.</p>
<h2>Quality of evidence</h2>
<p>Reliable scales (α {N['aS']} and {N['aC']}); CSS-12 four-factor structure confirmed; Arabic and English responders equivalent; results robust to sensitivity analyses and replicated by an independent analysis (except the AI effect).</p>
</div></div>
<h2>Implications</h2>
<p><b>Clinicians:</b> ask every patient, without judgement, what they searched or asked an AI; treat repeated searching plus distress as a marker of health anxiety. <b>Public health:</b> digital and AI health-literacy campaigns in Arabic; warn about false reassurance. <b>AI developers:</b> anxiety-aware answers that avoid escalating rare diagnoses. <b>Research:</b> longitudinal studies to test the direction of the cycle.</p>
<p class="small muted"><b>Limitations:</b> cross-sectional (no causality); online convenience sample, young and 44% medical students; Arabic wording not formally back-translated; single-item behaviour measures; self-report.</p>
</body></html>"""
open(f'{ST}/summary.html', 'w').write(summary)

# ============================================================ STUDY & DEFENCE GUIDE
def qa(q, a): return f'<div class="qa"><div class="q">Q. {q}</div><div class="a">{a}</div></div>'
glossary = [
 ('Health anxiety', 'Persistent worry about having or developing a serious illness, kept going by misreading normal body sensations and by checking and reassurance-seeking.'),
 ('Cyberchondria', 'Excessive or repeated online health searching that increases (rather than relieves) anxiety or distress.'),
 ('SHAI-14', 'Short Health Anxiety Inventory, 14 items each scored 0–3 (total 0–42). Higher = more health anxiety.'),
 ('CSS-12', 'Cyberchondria Severity Scale short form: 12 items scored 1–5 (total 12–60), four 3-item subscales.'),
 ('Excessiveness', 'CSS subscale: searching a lot (search every sensation, read many pages, repeat the same search).'),
 ('Compulsion', 'CSS subscale: searching interferes with work, leisure and social life.'),
 ('Distress', 'CSS subscale: panic and anxiety caused by what is read online.'),
 ('Reassurance seeking', 'CSS subscale: searching leads to visits to GPs/specialists or requests for tests.'),
 ('Cross-sectional study', 'All data collected at one point in time; shows associations, not cause and effect.'),
 ('Convenience / snowball sampling', 'Non-random recruitment of whoever is reachable, with participants sharing the link onwards.'),
 ('Pearson r / Spearman ρ', 'Correlation coefficients from −1 to +1. Spearman uses ranks and does not assume normality. 0.1 small, 0.3 moderate, 0.5 large.'),
 ('Partial correlation', 'The correlation that remains after statistically removing the effect of other variables (covariates).'),
 ('Mann–Whitney U / Kruskal–Wallis H', 'Non-parametric tests comparing two / three-or-more groups on a score.'),
 ('Chi-square (χ²) / Fisher exact', 'Tests whether two categorical variables are associated; Fisher is used when counts are small.'),
 ('Effect size', 'How big a difference or association is (e.g. r, ε², Cramér\'s V, β, OR), independent of sample size.'),
 ('p-value', 'Probability of a result at least this extreme if there were truly no association. p < 0.05 = "statistically significant".'),
 ('FDR / q-value', 'False discovery rate correction (Benjamini–Hochberg) for running many tests; q < 0.05 means the finding survives the correction.'),
 ('Holm–Bonferroni', 'A stricter multiple-testing correction controlling the chance of any false positive.'),
 ('Linear (OLS) regression, B and β', 'Predicts a score from several variables at once. B = change in outcome per unit of predictor; β = the same in standard-deviation units (comparable across predictors).'),
 ('R² / ΔR²', 'Proportion of variance in the outcome explained by the model / by an added block of variables.'),
 ('HC3 robust standard errors', 'Standard errors that stay valid when the spread of residuals is uneven (heteroskedasticity).'),
 ('Logistic regression, AOR', 'Predicts a yes/no outcome. Adjusted odds ratio > 1 = higher odds, < 1 = lower odds, after accounting for other variables.'),
 ('AUC', 'How well a model separates people with and without the outcome: 0.5 = chance, 0.8+ = good.'),
 ('Mediation', 'Tests whether X is linked to Y through a middle variable M (X → M → Y). Indirect effect = a × b.'),
 ('Bootstrap', 'Re-sampling the data thousands of times to get confidence intervals without strong assumptions.'),
 ('Moderation / interaction', 'Tests whether the strength of an association differs by a third variable (e.g. by gender).'),
 ('Cronbach\'s α / McDonald\'s ω', 'Internal consistency (reliability) of a scale; ≥ 0.70 acceptable, ≥ 0.80 good.'),
 ('CFA (CFI, TLI, RMSEA)', 'Confirmatory factor analysis checks whether items group as the scale claims. Good fit: CFI/TLI ≥ 0.95 (≥ 0.90 acceptable), RMSEA ≤ 0.06–0.08.'),
 ('95% CI', 'Range of values compatible with the data; if it excludes 0 (for B, r) or 1 (for OR), the result is significant.'),
]

guide = f"""<!doctype html><html><head><meta charset="utf-8"><title>Study and Defence Guide</title><style>{CSS_BASE}
.cover {{ height: 255mm; display: flex; flex-direction: column; justify-content: center; }}
.cover h1 {{ font-size: 24pt; }}
.toc li {{ margin: 3px 0; }}
</style></head><body>

<div class="cover">
 <div class="muted">Study &amp; Defence Guide</div>
 <h1>Artificial Intelligence, Search Engines, and Cyberchondria: A Study of Patient Pre-Consultation Behavior in Baghdad</h1>
 <p class="muted" style="font-size:11pt">Everything you need to understand your research, explain every number, present it in 12–15 minutes, and answer the committee's questions.</p>
 <div class="tiles" style="margin-top:20px">
  <div class="tile"><div class="v">{n}</div><div class="l">participants, Baghdad</div></div>
  <div class="tile"><div class="v">r = {N['r']}</div><div class="l">health anxiety ↔ cyberchondria</div></div>
  <div class="tile"><div class="v">{N['ai']}</div><div class="l">use AI chatbots</div></div>
  <div class="tile"><div class="v">{N['hac']}</div><div class="l">clinically relevant health anxiety</div></div>
 </div>
 <h3 style="margin-top:26px">Contents</h3>
 <ol class="toc">
  <li>The study in 60 seconds</li><li>Background concepts</li><li>Methods: what we did and why</li><li>Statistics explained in plain language</li>
  <li>Results walkthrough (with figures and what to say)</li><li>Interpreting the findings</li><li>Limitations and how to defend them</li>
  <li>Numbers to memorise</li><li>Presentation plan: slide by slide</li><li>Anticipated committee questions with model answers</li><li>Glossary</li><li>Final checklist</li>
 </ol>
</div>

<h2 class="page-break">1. The study in 60 seconds</h2>
<div class="box say"><b>Say this if asked "summarise your research":</b><br>
"Many people now look up their symptoms online, and increasingly they ask AI chatbots like ChatGPT before they see a doctor. We wanted to know how this relates to health anxiety and to cyberchondria, which is online searching that makes worry worse instead of better. We surveyed {n} adults in Baghdad using two validated scales, the SHAI-14 and the CSS-12. We found that AI chatbots are now the main source, used by {N['ai']}. About {N['hac']} had clinically relevant health anxiety. Health anxiety and cyberchondria were moderately correlated, r = {N['r']}, and health anxiety was the strongest predictor of cyberchondria, especially of excessive searching and distress after searching. The pattern is consistent with a cycle in which anxiety drives searching, searching drives distress, and distress drives extra doctor visits. Searching also shapes the consultation: about a third delay care because they feel reassured, and a third never tell their doctor about their searches. Because the study is cross-sectional, we cannot prove the direction of the cycle."</div>
<h3>Aim</h3><p>To study the relationship between health anxiety and cyberchondria and their correlates among adults in Baghdad who search for health information online, with attention to AI chatbots and pre-consultation behaviour.</p>
<h3>Objectives (memorise the gist)</h3>
<ol><li>Describe tools, motives and behaviours of online health searching (including AI).</li><li>Measure levels of health anxiety and cyberchondria.</li><li>Measure the strength of their association, overall and by dimension.</li><li>Test every variable's association with both.</li><li>Find independent predictors (multivariable models).</li><li>Test pathways (mediation) and modifiers (moderation).</li><li>Link both to pre-consultation behaviour, disclosure and trust in doctors.</li></ol>
<h3>Hypotheses and verdicts</h3>
<table><tr><th>Hypothesis</th><th>Verdict</th></tr>
<tr><td>H1: Health anxiety is positively associated with cyberchondria, most strongly with distress and excessiveness.</td><td><b>Supported</b> (r = {N['r']}; excessiveness {N['rE']}, distress {N['rD']})</td></tr>
<tr><td>H2: The association is independent of socio-demographic and digital factors.</td><td><b>Supported</b> (partial r = {N['pr']}; β = {N['beta']})</td></tr>
<tr><td>H3: Excessive searching mediates the link between health anxiety and post-search distress.</td><td><b>Supported</b>, partial mediation (indirect {N['mA']}, 95% CI {N['mAci']}). Cross-sectional caveat.</td></tr>
<tr><td>H4: Higher cyberchondria goes with care-seeking and a strained doctor relationship.</td><td><b>Partly supported</b>: urgent visits and strained relationship yes; multiple doctors not independently; most behaviour results exploratory after FDR.</td></tr></table>

<h2 class="page-break">2. Background concepts</h2>
<h3>Health anxiety</h3>
<p>A continuum from normal worry to illness anxiety disorder (DSM-5). The cognitive-behavioural model (Salkovskis &amp; Warwick, 1986) says people misinterpret normal body sensations as signs of serious disease; checking and reassurance-seeking reduce anxiety briefly but keep it going, because the person never learns the feared illness is not there. Lifetime prevalence of health anxiety disorder was 5.7% in an Australian national survey; almost half of Iraqi respondents reported health anxiety during COVID-19 restrictions (Karim et al., 2020).</p>
<h3>Cyberchondria</h3>
<p>Coined by White &amp; Horvitz (2009): searches for common symptoms escalate towards rare, serious diagnoses. Starcevic &amp; Berle (2013) define it as excessive or repeated online searching that <i>increases</i> distress. Searching itself is normal; it becomes cyberchondria when it is excessive, compulsive and distressing. It is seen as a safety behaviour maintained by intermittent reinforcement (sometimes the search reassures, so the habit is reinforced).</p>
<h3>What was known before</h3>
<ul><li>Meta-analyses: health anxiety correlates r ≈ 0.62–0.63 with cyberchondria and r ≈ 0.34 with general online searching (McMullan 2019; Schenkel 2021).</li>
<li>One large longitudinal Dutch study (te Poel 2016) found a reciprocal loop in non-clinical health anxiety but not in clinical health anxiety.</li>
<li>Almost no data from Iraq, and AI chatbots had not been studied alongside search engines.</li></ul>
<h3>The two instruments</h3>
<table><tr><th>Scale</th><th>Items / scoring</th><th>What higher means</th><th>Source</th></tr>
<tr><td>SHAI-14</td><td>14 items, each 4 statements scored 0–3; total 0–42. Cut-off ≥ 18 used for "clinically relevant".</td><td>More health anxiety</td><td>Salkovskis et al., 2002; cut-off Österman et al., 2022</td></tr>
<tr><td>CSS-12</td><td>12 items, Never(1)–Always(5); total 12–60. Excessiveness (items 1–3), Compulsion (4–6), Distress (7–9), Reassurance (10–12).</td><td>More cyberchondria</td><td>McElroy et al., 2019; Arabic version Hallit et al., 2023</td></tr></table>
<div class="box warn"><b>Know this detail:</b> on the Google Form, some SHAI answer options were displayed in a different order from the original scale (e.g. "as much as others" appeared before "less than others"). We scored by the <i>meaning</i> of the chosen statement, following the original key, not by its position. Both our analysis and the independent analysis did this, and both produced identical scores.</div>

<h2 class="page-break">3. Methods: what we did and why</h2>
<table>
<tr><th style="width:24%">Element</th><th>What we did</th><th style="width:30%">Why / how to justify</th></tr>
<tr><td>Design</td><td>Analytical cross-sectional online survey; STROBE and CHERRIES reporting.</td><td>Fast, affordable, appropriate for estimating associations; standard in this field.</td></tr>
<tr><td>Setting &amp; time</td><td>Baghdad, {N['d0']} – {N['d1']}.</td><td>Link shared in Baghdad-based online groups.</td></tr>
<tr><td>Sampling</td><td>Non-probability convenience + snowball; inclusion: ≥ 18 years, consent, Arabic or English.</td><td>No sampling frame of Internet users exists; the target behaviour (online searching) is by definition online.</td></tr>
<tr><td>Sample size</td><td>n = {n}. Minimum {N['nreq']} needed to detect r = 0.20 (α 0.05, power 80%).</td><td>Achieved power {N['pw']} for r = 0.20; smallest detectable r = {N['mdr']}; margin of error ±{N['moe']}% for proportions.</td></tr>
<tr><td>Instrument</td><td>Bilingual Google Form, 41 questions: consent, demographics, tools, motives, trust (1–5), SHAI-14, CSS-12, behaviours, disclosure, relationship, language.</td><td>Validated scales for the main constructs; bilingual to include English-preferring students.</td></tr>
<tr><td>Translation</td><td>Arabic wording by the team; equivalence checked empirically.</td><td>Arabic and English responders: same α, congruent loadings (Tucker φ ≈ 0.99), no mean difference.</td></tr>
<tr><td>Key definitions</td><td>Clinically relevant HA: SHAI ≥ 18. High cyberchondria: CSS &gt; 33 (top third). AI user: ticked AI <i>or</i> named a chatbot ({N['inc']} named one without ticking).</td><td>SHAI cut-off from a diagnostic-accuracy study vs healthy controls; CSS-12 has no clinical cut-off.</td></tr>
<tr><td>Ethics</td><td>Voluntary, anonymous, e-consent required before any question; could withdraw any time.</td><td>[Insert approval committee and number.]</td></tr>
</table>

<h2 class="page-break">4. Statistics explained in plain language</h2>
<p>For each analysis: <b>what it answers</b>, <b>why this test</b>, and <b>how to read the number</b>.</p>
<table>
<tr><th style="width:20%">Analysis</th><th>What it answers</th><th style="width:28%">Why this test</th><th style="width:26%">How to read it</th></tr>
<tr><td>Cronbach's α, McDonald's ω</td><td>Do the items of each scale measure one thing consistently?</td><td>Standard reliability indices; ω is less restrictive than α.</td><td>SHAI α {N['aS']}, CSS α {N['aC']}: good (≥ 0.80).</td></tr>
<tr><td>Confirmatory factor analysis</td><td>Do CSS items group into the 4 subscales?</td><td>Tests the scale's structure in our population.</td><td>CFI {N['cfaC']}, RMSEA {N['cfaR']}: acceptable–good fit.</td></tr>
<tr><td>Shapiro–Wilk</td><td>Are scores normally distributed?</td><td>Decides parametric vs non-parametric tests.</td><td>p &lt; 0.05, mild skew: so we used rank-based tests and robust SEs.</td></tr>
<tr><td>Pearson / Spearman correlation</td><td>How strongly do SHAI and CSS move together?</td><td>Both reported; Spearman robust to non-normality.</td><td>r = {N['r']} = moderate; health anxiety "explains" {N['r2']} of cyberchondria variance.</td></tr>
<tr><td>Partial correlation</td><td>Does the link survive removing age, gender, background, chronic disease, trust, AI use?</td><td>Rules out simple confounding.</td><td>Partial r = {N['pr']}: essentially unchanged.</td></tr>
<tr><td>Williams' t</td><td>Is SHAI more strongly linked to some CSS subscales than others?</td><td>Compares two correlations that share a variable.</td><td>Excessiveness and distress &gt; compulsion and reassurance (p &lt; 0.001).</td></tr>
<tr><td>Mann–Whitney U / Kruskal–Wallis H</td><td>Do scores differ between groups (gender, age, AI use…)?</td><td>Non-parametric group comparisons.</td><td>p &lt; 0.05 = groups differ; effect size r_rb or ε².</td></tr>
<tr><td>χ² / Fisher exact</td><td>Is a category (e.g. social-media use) linked to clinical HA or high cyberchondria?</td><td>Categorical × categorical; Fisher when counts small.</td><td>Cramér's V ~ 0.1 small, 0.3 moderate.</td></tr>
<tr><td>Benjamini–Hochberg FDR</td><td>Which findings survive the many tests we ran?</td><td>162+ tests would produce false positives by chance.</td><td>q &lt; 0.05 = robust; q ≥ 0.05 = exploratory.</td></tr>
<tr><td>Hierarchical OLS regression (HC3)</td><td>What predicts cyberchondria when everything is considered together?</td><td>Adds blocks to see how much each explains; robust SEs.</td><td>R² {N['R2a']} → {N['R2b']} → {N['R2c']}; SHAI β = {N['beta']} (largest).</td></tr>
<tr><td>Logistic regression</td><td>What predicts clinically relevant HA, or each behaviour?</td><td>Yes/no outcomes.</td><td>AOR &gt; 1 = higher odds (e.g. CSS AOR {N['orCSS']} per SD).</td></tr>
<tr><td>Mediation (bootstrap)</td><td>Is HA linked to distress <i>through</i> excessive searching?</td><td>Tests a proposed pathway; 5000 resamples.</td><td>Indirect {N['mA']}, CI excludes 0 = significant indirect path.</td></tr>
<tr><td>Moderation</td><td>Is the HA–CSS link stronger in some groups?</td><td>Interaction terms.</td><td>All p &gt; 0.05: same link everywhere.</td></tr>
<tr><td>Sensitivity analyses</td><td>Are results fragile?</td><td>Remove flagged and careless responses, change cut-offs, bootstrap.</td><td>Main results unchanged.</td></tr>
</table>
<div class="box say"><b>If asked "why non-parametric tests?":</b> "The Shapiro–Wilk test showed the scores were not perfectly normal, and several subscales were skewed, so we used rank-based tests for group comparisons. For regression we used robust (HC3) standard errors and bootstrap intervals, and we also ran Welch's parametric tests as a check; the conclusions were the same."</div>
<div class="box say"><b>If asked "why FDR correction?":</b> "Because we tested every variable against every outcome, more than 160 tests. At p &lt; 0.05 we would expect about 8 false positives by chance, so we controlled the false discovery rate and labelled anything that did not survive as exploratory."</div>

<h2 class="page-break">5. Results walkthrough</h2>
<h3>5.1 Sample</h3>
<p>{n} adults; {N['age20']} aged 20–29; {N['fem']} female; {N['med']} medical students; {N['hb']} health-related background; {N['chron']} chronic condition; {N['ar']} answered mainly in Arabic.</p>
<div class="box warn">The sample is young and dominated by medical students: say so before the committee does.</div>
<h3>5.2 How people search</h3>
{img('fig2_tools_motives.png', 'Figure 1 of the thesis: tools and motivations.')}
<div class="box say"><b>What to say:</b> "AI chatbots have overtaken search engines: {N['ai']} use them versus {N['se']} for search engines, and {N['ai_only']} use AI without any search engine. ChatGPT dominates. People search mainly for convenience, to decide whether they need a doctor, and for instant reassurance."</div>
<h3>5.3 What they do after searching</h3>
{img('fig3_behaviours.png', 'Figure 2 of the thesis: behaviour, disclosure and relationship.')}
<div class="box say"><b>What to say:</b> "The most common response is to delay or skip care because the search reassured them ({N['dr']}). Others go the opposite way: {N['urg']} seek urgent care and {N['mdoc']} see several doctors. Only {N['always']} always tell their doctor what they found; {N['never']} never do, for fear of being judged. And {N['relneg']} feel searching has complicated their relationship with doctors."</div>
<h3>5.4 Levels of health anxiety and cyberchondria</h3>
<p>SHAI mean {N['shai_m']} ± {N['shai_sd']}; {N['hac']} ≥ 18 (95% CI {N['hac_ci']}). CSS mean {N['css_m']} ± {N['css_sd']}. Excessiveness highest, compulsion lowest: people search a lot, but it rarely disrupts their lives.</p>
<h3>5.5 The main result: health anxiety and cyberchondria</h3>
{img('fig1_scatter_shai_css.png', 'Figure 3 of the thesis: SHAI vs CSS.', '78%')}
<div class="box say"><b>What to say:</b> "This is our main finding. Health anxiety and cyberchondria are moderately correlated, r = {N['r']} (95% CI {N['rci']}). The association hardly changes when we adjust for everything else (partial r = {N['pr']}). It is strongest for excessive searching and distress after searching."</div>
{img('fig5_subscales_by_HA.png', 'Figure 8 of the thesis: CSS subscales by health-anxiety status.', '72%')}
<h3>5.6 Which items drive the link</h3>
{img('fig9_item_by_item.png', 'Figure 9 (appendix): item-by-item correlations.', '92%')}
<div class="box say"><b>What to say:</b> "When we looked item by item, {N['ibF']} of 168 pairs were significant after correction. The strongest links involve <i>fear</i> of serious illness and <i>interpreting</i> sensations, for example fear of illness with panic when reading about a rare disease. Simply noticing aches and sensations was not linked. So it is the catastrophic interpretation, not body awareness, that drives searching."</div>
<h3>5.7 Who is affected (bivariate)</h3>
<p>Health anxiety higher in: younger respondents, students, chronic illness, social-media searchers, and reassurance seekers. Gender: no difference. Cyberchondria: almost unrelated to demographics; higher in AI users and in those combining AI + search engines.</p>
{img('fig6_css_by_tool.png', 'Figure 5 of the thesis: cyberchondria by tool profile.', '62%')}
<h3>5.8 Independent predictors</h3>
<p><b>Cyberchondria model:</b> demographics R² {N['R2a']}; + digital use {N['R2b']}; + health anxiety {N['R2c']} (ΔR² {N['dR2']}). SHAI B = {N['B']} per point (β = {N['beta']}). AI use B = +{N['Bai']} (95% CI {N['Baici']}).</p>
<p><b>Clinically relevant health anxiety (logistic):</b> cyberchondria AOR {N['orCSS']} per SD; reassurance motive AOR {N['orMot']}; each older age group AOR {N['orAge']}; AUC {N['auc']}.</p>
{img('fig7_forest_HA.png', 'Figure 6 of the thesis: adjusted odds ratios for SHAI ≥ 18.', '75%')}
<h3>5.9 Pathways (mediation)</h3>
{img('fig8_mediation.png', 'Figure 7 of the thesis: mediation models.')}
<div class="box say"><b>What to say:</b> "We tested your question of whether anxiety and searching feed each other. Excessive searching carries part of the link between health anxiety and distress (indirect effect {N['mA']}). Distress after searching carries almost all of the link between health anxiety and reassurance-seeking visits; the direct effect drops to {N['mCd']}. The reverse ordering is also significant ({N['mD']}). This is what a two-way cycle would look like, but with one-time data we cannot prove which comes first."</div>
<h3>5.10 Behaviour models</h3>
<p>Higher cyberchondria: more urgent visits (AOR {N['urC']}), less ignoring (AOR {N['igC']}). Disclosure paradox: SHAI AOR {N['nsS']} for never disclosing, CSS AOR {N['nsC']}. Higher trust: fewer multiple-doctor visits (AOR {N['mdT']}). Neither score predicts self-medication or reassured delay. Only the disclosure finding survives FDR; the rest are exploratory.</p>
<h3>5.11 Moderation and robustness</h3>
<p>No moderator changed the HA–CSS link (trust, AI use, background, gender, chronic disease, language, age). Medical students r = {N['ms_r']} vs others {N['ot_r']} (not significantly different). Excluding flagged or straight-line responders: r unchanged ({sens['excluding_flagged_r']:.2f} / {sens['excluding_straightliners_r']:.2f}).</p>

<h2 class="page-break">6. Interpreting the findings</h2>
<ul>
<li><b>Why is our r ({N['r']}) lower than meta-analyses (~0.62)?</b> Low-anxiety sample with a narrow range; young, digitally habitual users for whom searching is routine; most earlier studies used the 33-item CSS, which overlaps more with health anxiety.</li>
<li><b>Fear, not vigilance:</b> interpretation and fear items drive cyberchondria, which fits the cognitive model of health anxiety.</li>
<li><b>AI chatbots:</b> a new channel rather than a proven new cause. Conversational, empathetic answers may invite "one more question". The effect is sensitive to classification ({N['inc']} inconsistent answers; only 34 non-users).</li>
<li><b>Two opposite behaviours:</b> searching pushes some people to complacency (delay, ignore) and others to over-use (urgent visits, multiple doctors). The reassured delay happens regardless of anxiety level, which is a safety concern.</li>
<li><b>Concealment paradox:</b> health-anxious people hide searching (fear of being labelled "worried well"), while heavy searchers bring findings to the doctor as reassurance seeking. Clinicians must ask.</li>
<li><b>Medical students:</b> higher health anxiety only before adjustment (an age effect); identical cyberchondria to others, so medical knowledge does not protect.</li>
</ul>

<h2>7. Limitations and how to defend them</h2>
<table><tr><th style="width:26%">Limitation</th><th>How to answer</th></tr>
<tr><td>Cross-sectional: no causality</td><td>"Correct. We use the word association throughout, and we present mediation as consistent with, not proof of, a cycle. We tested the reverse direction too and recommend longitudinal work."</td></tr>
<tr><td>Convenience sample, 44% medical students, young</td><td>"Prevalence and AI-use figures cannot be generalised to all of Baghdad. But associations are less sensitive to sampling than prevalences, the HA–CSS link was the same in every subgroup, and medical students did not differ in cyberchondria."</td></tr>
<tr><td>Arabic not back-translated</td><td>"We tested equivalence empirically: identical reliability, highly congruent factor loadings (≈ 0.99), and no score difference between Arabic and English responders after adjustment. Formal validation is a recommendation."</td></tr>
<tr><td>SHAI cut-off from a Swedish study</td><td>"It is used as an indicator, not a diagnosis; we reported prevalence at 15, 18 and 22, and analysed SHAI as a continuous score."</td></tr>
<tr><td>Behaviour items not validated / multi-select</td><td>"They are descriptive, single items. We treat their associations as exploratory and say so."</td></tr>
<tr><td>Many tests</td><td>"We applied FDR correction and distinguished robust from exploratory findings."</td></tr>
<tr><td>AI effect depends on coding</td><td>"We report it transparently: with the strict definition the effect disappears, so it is a tentative finding."</td></tr>
<tr><td>Self-report, online</td><td>"Anonymous e-survey reduces social-desirability bias; careless responses were checked and excluding them changed nothing."</td></tr></table>

<h2 class="page-break">8. Numbers to memorise</h2>
<table>
<tr><th>Item</th><th class="num">Value</th><th>Item</th><th class="num">Value</th></tr>
<tr><td>Sample size</td><td class="num">{n}</td><td>Data collection</td><td class="num">Jul–Sep 2026</td></tr>
<tr><td>Aged 20–29</td><td class="num">{N['age20']}</td><td>Female</td><td class="num">{N['fem']}</td></tr>
<tr><td>Medical students</td><td class="num">{N['med']}</td><td>Chronic condition</td><td class="num">{N['chron']}</td></tr>
<tr><td>Use AI chatbots</td><td class="num">{N['ai']}</td><td>Use search engines</td><td class="num">{N['se']}</td></tr>
<tr><td>ChatGPT (of all)</td><td class="num">{N['gpt']}</td><td>AI without search engine</td><td class="num">{N['ai_only']}</td></tr>
<tr><td>SHAI mean ± SD</td><td class="num">{N['shai_m']} ± {N['shai_sd']}</td><td>CSS mean ± SD</td><td class="num">{N['css_m']} ± {N['css_sd']}</td></tr>
<tr><td>SHAI ≥ 18</td><td class="num">{N['hac']}</td><td>α SHAI / CSS</td><td class="num">{N['aS']} / {N['aC']}</td></tr>
<tr><td><b>SHAI–CSS r</b></td><td class="num"><b>{N['r']}</b></td><td>Partial r</td><td class="num">{N['pr']}</td></tr>
<tr><td>r with Excessiveness / Distress</td><td class="num">{N['rE']} / {N['rD']}</td><td>r with Compulsion / Reassurance</td><td class="num">{N['rC']} / {N['rR']}</td></tr>
<tr><td>SHAI β in CSS model</td><td class="num">{N['beta']}</td><td>R² final model</td><td class="num">{N['R2c']}</td></tr>
<tr><td>Indirect effect (excess. → distress)</td><td class="num">{N['mA']}</td><td>Direct HA → reassurance after distress</td><td class="num">{N['mCd']} (ns)</td></tr>
<tr><td>Delay care (reassured)</td><td class="num">{N['dr']}</td><td>Never disclose to doctor</td><td class="num">{N['never']}</td></tr>
<tr><td>Urgent care / ER</td><td class="num">{N['urg']}</td><td>Relationship complicated / reduced trust</td><td class="num">{N['relneg']}</td></tr>
<tr><td>Item pairs significant (FDR)</td><td class="num">{N['ibF']}/168</td><td>References</td><td class="num">52 (Vancouver)</td></tr>
</table>

<h2 class="page-break">9. Presentation plan: slide by slide (≈ 12–15 minutes)</h2>
<p class="muted">Keep slides visual: one message per slide, the figure plus a one-line takeaway. Rehearse to time.</p>
""" + ''.join(f'<div class="slide"><span class="h">Slide {i}. {t}</span><span class="tag">{tm}</span><div>{c}</div></div>' for i, (t, tm, c) in enumerate([
 ('Title', '15 s', 'Title, names, supervisor, college. Say the title clearly and introduce the team.'),
 ('Why this matters', '1 min', 'Everyone "Googles" symptoms; now AI chatbots answer them. For some people searching increases worry: cyberchondria. Health anxiety costs patients and services. No data from Iraq; AI not studied.'),
 ('Key concepts', '1 min', 'Define health anxiety and cyberchondria in one line each. Show the cycle: anxiety → search → distress → reassurance-seeking.'),
 ('Aim and objectives', '45 s', 'Aim + 3–4 condensed objectives; state H1–H4 briefly.'),
 ('Methods', '1.5 min', f'Cross-sectional online survey, Baghdad, n = {n}; convenience/snowball; SHAI-14 and CSS-12 (show subscales); bilingual; sample-size justification (needed {N["nreq"]}); ethics.'),
 ('Analysis', '45 s', 'One slide listing analyses: reliability/CFA, correlations, non-parametric tests with FDR, robust regression, logistic, mediation/moderation, sensitivity.'),
 ('Participants', '45 s', f'Key demographics; acknowledge {N["med"]} medical students.'),
 ('How people search', '1 min', f'Figure 1: AI {N["ai"]} vs search engines {N["se"]}; motives.'),
 ('Levels', '45 s', f'SHAI mean {N["shai_m"]}; {N["hac"]} ≥ 18; CSS mean {N["css_m"]}; reliability α {N["aS"]} / {N["aC"]}.'),
 ('Main result', '1.5 min', f'Scatter plot: r = {N["r"]}, partial r = {N["pr"]}; subscale correlations; regression β = {N["beta"]}.'),
 ('What drives it', '1 min', 'Item-by-item heatmap: fear and interpretation, not awareness.'),
 ('Pathways', '1.5 min', 'Mediation figure; say clearly "consistent with a cycle, not proof".'),
 ('Behaviour and the doctor', '1.5 min', f'Delay {N["dr"]}, never disclose {N["never"]}, urgent care; disclosure paradox.'),
 ('AI chatbots', '45 s', 'Higher cyberchondria in AI users, but sensitive to classification; a new channel, not a proven cause.'),
 ('Limitations', '1 min', 'Cross-sectional, sample, translation, single items; how each was mitigated.'),
 ('Conclusions and recommendations', '1 min', 'Three conclusions + recommendations for clinicians, public health, AI developers, research.'),
 ('Thank you / questions', '-', 'Keep the main figure on screen while taking questions.'),
], 1)) + f"""

<h2 class="page-break">10. Anticipated committee questions with model answers</h2>
<h3>About the design and sample</h3>
{qa('Why a cross-sectional design?', 'It is the most feasible design for a graduation project and suitable for measuring associations. We are clear that it cannot establish causality; a longitudinal design is recommended.')}
{qa('How do you know participants were from Baghdad?', 'The link was distributed only through Baghdad-based online groups. We did not include a residence question, which we acknowledge as a limitation.')}
{qa('Your sample is mostly medical students. Is that a problem?', f'It limits generalisability of percentages such as AI use and prevalence. But the main association was the same across all occupational groups, medical students did not differ in cyberchondria, and we adjusted for occupation in all models.')}
{qa('How did you calculate the sample size?', f'For the primary objective, a correlation: detecting r = 0.20 with 80% power and α = 0.05 requires {N["nreq"]}. With {n} we had {N["pw"]} power, and the smallest detectable correlation was {N["mdr"]}. For proportions, the margin of error is ±{N["moe"]}%.')}
{qa('Why did you include participants who answered in English?', 'Many students in Baghdad study in English. Offering both languages improved accessibility. We checked that both language groups responded equivalently.')}
<h3>About the instruments</h3>
{qa('Why the SHAI-14 and the CSS-12?', 'They are the most widely used validated measures of each construct, they are short (good for online surveys), the CSS-12 was validated against the SHAI, and both have Arabic versions in the literature.')}
{qa('Were the scales validated in Arabic?', 'Arabic versions exist (Alshayea 2020 for the SHAI; Hallit 2023 for the CSS-12). We used our own wording, so we tested reliability and structure in our data: α 0.81 and 0.86, four-factor CSS structure confirmed, and equivalent results for Arabic and English responders.')}
{qa('Why a cut-off of 18?', 'It was the optimal SHAI-14 cut-off for distinguishing health anxiety from healthy controls in a 2022 diagnostic-accuracy study. It is an indicator, not a diagnosis, so we also report 15 and 22 and use the continuous score.')}
{qa('What about the answer-order differences on the form?', 'Items were scored by the meaning of the statement chosen, following the original scoring key, so the order did not affect scores.')}
<h3>About the analysis</h3>
{qa('Why both Pearson and Spearman?', 'Pearson is standard and comparable with meta-analyses; Spearman is robust to the mild non-normality. Both gave 0.47.')}
{qa('What does r = 0.47 mean in practice?', f'A moderate positive association: people with more health anxiety tend to have more cyberchondria. Health anxiety accounts for about {N["r2"]} of the differences in cyberchondria.')}
{qa('What is FDR and why use it?', 'False discovery rate correction controls the proportion of false positives when running many tests. We tested every variable, so without it some significant results would be chance findings.')}
{qa('What is mediation and what did you find?', f'It tests whether X is linked to Y through M. Excessive searching partly carries the link from health anxiety to distress (indirect {N["mA"]}). Distress almost fully carries the link from health anxiety to reassurance-seeking visits.')}
{qa('Can mediation in cross-sectional data prove a cycle?', 'No. It tests whether the data are consistent with a proposed ordering. We also tested the reverse ordering, which was also significant, which is consistent with a two-way relationship but cannot prove direction.')}
{qa('Why robust (HC3) standard errors?', 'The residuals showed some heteroskedasticity, and robust standard errors remain valid in that situation.')}
{qa('Did you check multicollinearity?', 'Yes: the highest VIF was 3.9, below the usual threshold of 5–10.')}
{qa('How robust are the results?', 'Excluding the three annotated responses, excluding nine straight-line responders, bootstrapping, and changing the cut-off did not change the main results. An independent analysis of the same data reached the same conclusions.')}
<h3>About the findings</h3>
{qa('Is AI making people more anxious?', f'We cannot say that. AI users scored higher on cyberchondria (+{N["Bai"]} points), but with a strict definition of AI use the effect disappears (B = {N["Balt"]}, p = {N["palt"]}), and the non-user group was small (34). AI is best described as a new channel for the same behaviour.')}
{qa('Why is your correlation lower than in previous studies?', 'Our sample had relatively low health anxiety (narrow range), was young and digitally habitual, and we used the short CSS-12 rather than the 33-item version.')}
{qa('What is the most clinically important finding?', f'That a third of people delay care because they feel reassured, and a third never tell their doctor about their searches; the more health-anxious hide it more. Doctors should ask about online and AI searches routinely.')}
{qa('Why do health-anxious people hide their searches?', 'Probably fear of being labelled as anxious or "worried well", which the answer option itself reflects. Patients with high cyberchondria, in contrast, bring their findings as part of reassurance seeking.')}
{qa('Do medical students have more health anxiety?', 'Only before adjustment; the difference disappeared after accounting for age. Their cyberchondria was identical to others, so medical knowledge did not protect against it.')}
{qa('What would you do differently?', 'Use random sampling, add a residence question, formally back-translate and pilot the Arabic version, measure behaviour frequency rather than tick boxes, and follow participants over time.')}
{qa('What is new in your study?', 'First Iraqi data on health anxiety and cyberchondria; one of the first studies to place AI chatbots alongside search engines; linking both to concrete pre-consultation behaviours and disclosure to doctors.')}
{qa('What are your recommendations?', 'Clinicians: ask about searches non-judgementally and recognise repeated searching with distress as a sign of health anxiety. Public health: Arabic digital/AI health-literacy campaigns. AI developers: anxiety-aware responses. Researchers: longitudinal studies and formal Arabic validation.')}

<h2 class="page-break">11. Glossary</h2>
<table><tr><th style="width:27%">Term</th><th>Meaning</th></tr>
""" + ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in glossary) + f"""</table>

<h2>12. Final checklist before the defence</h2>
<ul>
<li>☐ Fill in the title page, acknowledgment and ethics approval details in the thesis.</li>
<li>☐ Read the full thesis once and the Results and Discussion twice.</li>
<li>☐ Memorise the "60-second summary" and the numbers table (section 8).</li>
<li>☐ Prepare slides following section 9; one message per slide; rehearse to 12–15 minutes.</li>
<li>☐ Practise answering every question in section 10 aloud, ideally with a colleague playing the committee.</li>
<li>☐ Be ready to explain: cross-sectional ≠ causal; what r, p, q, AOR and indirect effect mean.</li>
<li>☐ Bring a printed copy of the one-page summary and the questionnaire.</li>
<li>☐ If you don't know an answer: say so honestly, then say how you would find out. Committees respect that.</li>
</ul>
</body></html>"""
open(f'{ST}/guide.html', 'w').write(guide)
print('written', ST)
