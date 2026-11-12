"""Short version of the thesis (~35 pages): same setup, tables and figures as 04_build_docx.py, condensed text
(based on the humanized wording), extra analyses summarised in one sentence each, no appendices, fewer references.
Usage: python3 04s_build_short.py <output dir> <out.docx> [pages.json]"""
import sys, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, '04_build_docx.py')).read().split('\n')

def idx(prefix, after=0):
    hits = [i for i, L in enumerate(SRC) if i >= after and L.startswith(prefix)]
    assert hits, prefix
    return hits[0]
def block(start, end_prefix, after=0, edits=()):
    """Source lines from the line starting with `start` to the first later line starting with `end_prefix` (inclusive)."""
    i = idx(start, after); j = idx(end_prefix, i)
    txt = '\n'.join(SRC[i:j + 1])
    for a, b in edits:
        assert a in txt, (start, a[:60]); txt = txt.replace(a, b)
    return txt

HEAD = '\n'.join(SRC[:idx('# ================================================================== ABSTRACT')])
REFS_PART = '\n'.join(SRC[idx('# ------------------------------------------------------------------ REFERENCES'):idx('# ------------------------------------------------------------------ APPENDIX')])
TAIL = '\n'.join(SRC[idx('# ------------------------------------------------------------------ fill lists'):])
_ab = "t = doc.add_table(rows=0, cols=2)\nfor a, b in abbr:"
assert _ab in HEAD
assert "P('[Academic year]', align='center', indent=False)" in HEAD
HEAD = HEAD.replace("P('[Academic year]', align='center', indent=False)", "P('2026          1448', align='center', indent=False)")
HEAD = HEAD.replace('in partial fulfilment of the requirements for the degree of [Degree]', 'in partial fulfilment of the requirements for the degree of Bachelor of Medicine and Bachelor of Surgery (M.B.Ch.B.)')
_ack_old = "P('[To be completed by the authors.]', indent=False)\nP('We thank all the participants who gave their time to complete this survey, and [names of supervisor, department and any others to be acknowledged].')"
assert _ack_old in HEAD
HEAD = HEAD.replace(_ack_old, "P('First and foremost, praise and thanks to Allah for His blessings throughout this work.', indent=False)\nP('We express our deepest gratitude to our supervisor, Assist. Prof. Dr. Thikra Hasan Mathkor (Department of Biochemistry), for guidance, encouragement and constructive feedback at every stage of this study.')\nP('We also thank the Department of Biochemistry and the College of Medicine, University of Baghdad, and all the participants who gave their time to complete our online questionnaire and made this study possible.')")
HEAD = HEAD.replace(_ab, "abbr = [x for x in abbr if x[0] not in ('CFA', 'CFI', 'DWLS', 'FDR', 'HC3', 'KMO', 'ML', 'RMSEA', 'TLI', 'OLS')]\n" + _ab, 1)
R0 = idx("H('3. Results')")

TAB1 = block("T1 = X['T1_demographics']", "table(['Characteristic'", R0)
TAB2 = block("T2 = X['T2_digital_behaviour']", "      note='Tools, motivations", R0).replace("table(['Variable', 'n', '%'], rows, widths=[10.5, 2, 2],", "table(['Variable', 'n', '%'], rows, widths=[10.5, 2, 2], size=9.5, compact=True,")
TAB3 = block("T3 = X['T3_scale_desc']", "T3 = X['T3_scale_desc']", R0) + '\n' + block("rows = []", "      note=f'Language equivalence", idx("for lab, col, rk in", R0) - 1, edits=[
    ("(SHAI-14 means are not strictly comparable across languages because its scalar invariance was not supported; Table 5)", "(SHAI-14 means are not strictly comparable across languages because its scalar invariance was not supported)"),
    (" Measurement invariance across languages: Table 5.", " Measurement invariance (multi-group CFA): CSS-12 scalar invariant; SHAI-14 metric but not scalar invariant; no item DIF after FDR correction.")])
TAB4 = block("from statsmodels.stats.proportion import", "      note=f'Cut-offs of 18", R0)
TABC = block("rows = []", "      note='Adjusted β", idx("for k, col in [('CSS-12 total'", R0) - 1)
GVARS = block("gA = gp('Age group'", "gTPc = gp(", R0)
TAB7 = block("sel = [('Age group'", "      note='SHAI-14 comparisons by language", R0, edits=[
    ("SHAI-14 comparisons by language should be read cautiously because SHAI-14 scalar invariance was not supported (Table 5). ", "SHAI-14 comparisons by language should be read cautiously because SHAI-14 scalar invariance was not supported. ")])
TAB8 = block("rows = []", "      bold_rows=[i for i, r in enumerate(rows) if r[1] == ''], note='Pearson", idx("for out_lab, out in", R0) - 1)
TAB9 = block("rows = []", "      note=f'Block 1", idx("lab = {'Intercept'", R0) - 1)
TAB10 = block("rows = []", "      note=f'AUC =", idx("lab2 = {'age_ord'", R0) - 1)
BVARS = block("bU = bh('Urgent visit/ER'", "bM = bh('Multiple doctors'", R0)
TAB11 = block("rows = []", "      note='AOR per 1 SD", idx("for outc in ['Urgent visit/ER'", R0) - 1)
TAB12 = block("rows = []", "      '; '.join([f'{r.Moderator.lower()}", idx("for lab_, pre in", R0) - 1)

# ---- simplification to SPSS-level analyses (classical SEs, no FDR, Sobel mediation): post-process the extracted blocks
def sub1(txt, a, b):
    assert a in txt, a[:70]; return txt.replace(a, b)
TAB3 = sub1(TAB3, "f'{rr.alpha:.2f} ({rr.alpha_CI})', f'{rr.omega:.2f}'])", "f'{rr.alpha:.2f}'])")
TAB3 = sub1(TAB3, "['Scale', 'Mean ± SD', 'Median (IQR)', 'Range', 'α (95% CI)', 'ω'], rows, widths=[4.6, 2.6, 2.6, 1.6, 2.7, 1.1]", "['Scale', 'Mean ± SD', 'Median (IQR)', 'Range', 'Cronbach\\'s α'], rows, widths=[4.8, 3.0, 3.0, 2.0, 2.4]")
TAB3 = sub1(TAB3, 'Descriptive statistics, reliability and language equivalence of', 'Descriptive statistics and reliability of')
TAB3 = re.sub(r"note=f'Language equivalence.*$", "note='Cronbach\\'s α ≥ 0.70 indicates acceptable internal consistency. Higher scores indicate more health anxiety (SHAI-14) and more cyberchondria (CSS-12).')", TAB3, flags=re.M)
TABC = TABC.replace('ci(*rr["pearson_CI"])', 'ci(*fisher_ci(rr["pearson"]))').replace('ci(*sc["pearson_CI"])', 'ci(*fisher_ci(sc["pearson_r"]))')
TABC = "def fisher_ci(r, n=300):\n    z = np.arctanh(r); h = 1.959964 / np.sqrt(n - 3)\n    return np.tanh(z - h), np.tanh(z + h)\n" + TABC
TABC = re.sub(r"note='Adjusted β.*$", "note='Pearson r with 95% CI calculated by Fisher\\'s z transformation; all p < 0.001. Adjusted β: standardised coefficient of SHAI from multiple linear regression models adjusted for age, gender, occupation, chronic disease, language, tools, trust and motives.')", TABC, flags=re.M)
TAB7 = sub1(TAB7, "f'{pnum(g1.p)} ({g1.q_FDR:.3f})', '', f'{pnum(g2.p)} ({g2.q_FDR:.3f})'", "pnum(g1.p), '', pnum(g2.p)")
TAB7 = sub1(TAB7, "'SHAI mean ± SD', 'p (q)', 'CSS mean ± SD', 'p (q)'", "'SHAI mean ± SD', 'p', 'CSS mean ± SD', 'p'")
TAB7 = re.sub(r"note='SHAI-14 comparisons.*$", "note='p: Mann–Whitney U test (two groups) or Kruskal–Wallis H test (three or more groups); p < 0.05 was considered significant.')", TAB7, flags=re.M)
TAB7 = sub1(TAB7, "('Gender', 'gender', ['Female', 'Male']),", "('Gender', 'gender', ['Female', 'Male']), ('Education', 'education', ['Currently a student', 'High school or below', 'Diploma/Vocational', 'Bachelor', 'Postgraduate']),")
TAB8 = sub1(TAB8, "rows.append([out_lab, '', '', '', ''])", "rows.append([out_lab, '', '', ''])")
TAB8 = sub1(TAB8, "pnum(r.p), f'{r.q_FDR:.3f}'])", "pnum(r.p)])")
TAB8 = sub1(TAB8, "'Cramér\\'s V', 'p', 'q (FDR)'], rows, widths=[4.6, 7.4, 1.6, 1.4, 1.6]", "'Cramér\\'s V', 'p'], rows, widths=[5.0, 8.2, 1.7, 1.6]")
TAB8 = sub1(TAB8, " Associations with q ≥ 0.05 are exploratory.", "")
TAB9 = sub1(TAB9, 'Hierarchical robust linear regression', 'Hierarchical multiple linear regression')
TAB9 = sub1(TAB9, ' HC3 robust standard errors.', '')
TAB10 = re.sub(r"note=f'AUC =.*$", "note=f'Enter method. Omnibus χ²({SL[\"omnibus_df\"]}) = {SL[\"omnibus_chi2\"]:.1f}, p < 0.001; Nagelkerke R² = {SL[\"nagelkerke\"]:.2f}; Hosmer–Lemeshow χ²(8) = {SL[\"HL_chi2\"]:.2f}, p = {SL[\"HL_p\"]:.2f}; {SL[\"correct\"]:.0f}% correctly classified; area under the ROC curve = {SL[\"AUC\"]:.2f}. Cyberchondria entered as a z-score.')", TAB10, flags=re.M)
TAB11 = sub1(TAB11, " FDR-adjusted q-values are given in the supplementary workbook.", " p < 0.05 was considered significant.")
TAB12 = r"""
rows = []
for m in SM:
    rows.append([m['Model'], f"{m['a']:.2f} ({m['SE_a']:.2f})", f"{m['b']:.2f} ({m['SE_b']:.2f})", f"{m['c']:.2f}", f"{m['c_prime']:.2f}" + ('' if m['p_c_prime'] < .05 else ' (ns)'),
                 f"{m['indirect']:.2f}", f"{m['sobel_z']:.2f}", pnum(m['sobel_p'])])
caption('Table', 'Mediation models of the association between health anxiety (HA) and the dimensions of cyberchondria (standardised coefficients, Sobel test, n = 300)')
table(['Model', 'a (SE)', 'b (SE)', 'Total c', 'Direct c′', 'Indirect a×b', 'Sobel z', 'p'], rows, widths=[4.9, 1.7, 1.7, 1.3, 1.6, 1.6, 1.3, 1.7], size=9.5,
      note='All variables were converted to z-scores before the regressions, so the coefficients (B) and their SEs are on a standardised scale. a: predictor → mediator; b: mediator → outcome, adjusted for the predictor; c: total effect; c′: direct effect. Linear regressions adjusted for age, gender, health background, chronic disease, trust and AI use. All a, b and c paths p < 0.001; ns: not significant. Sobel z = a×b / √(b²SEa² + a²SEb²).')
"""
OVR = r"""
# ---- SPSS-level results (from 02d_simple_stats.py) replace the robust/bootstrap/FDR versions
S2 = json.load(open(f'{OUT}/simple.json'))
hier = pd.DataFrame(S2['hier']); SL = S2['logit_HA']; SM = S2['mediation']
_c = pd.DataFrame(S2['ols_coef']).set_index('term'); _t = stats.t.ppf(.975, S2['ols_final']['df2'])
ols = pd.DataFrame({'B': _c.B, 'CI_low': _c.B - _t * _c.SE, 'CI_high': _c.B + _t * _c.SE, 'SE': _c.SE, 'beta_std': _c.beta, 'p': _c.p})
R['ols_css']['F'] = S2['ols_final']['F']
lg = pd.DataFrame(S2['logit_HA_coef']).set_index('term')
beh = pd.DataFrame(S2['behaviour'])
b_shai = ols.loc['SHAI']; b_ai = ols.loc['ai_user']; b_a30 = ols.loc["C(age_c, Treatment('20–29'))[T.30–39]"]; b_a40 = ols.loc["C(age_c, Treatment('20–29'))[T.≥40]"]
lg_css = lg.loc['zCSS']; lg_mot = lg.loc['mot_reassurance']; lg_age = lg.loc['age_ord']
ai_alt_B, ai_alt_p = S2['ai_strict']['B'], S2['ai_strict']['p']
"""

MAIN = r'''
# ================================================================== ABSTRACT (short)
H('Summary / Abstract')
for a in [
 f'**Background:** Many adults look up symptoms online before seeing a doctor, increasingly with artificial-intelligence (AI) chatbots. Health anxiety and cyberchondria (excessive, distressing online health searching) are thought to feed each other, but evidence from Iraq, and on AI chatbots, is scarce.',
 f'**Objectives:** To measure the association between health anxiety and cyberchondria among adults in Baghdad, and to describe online and AI health-information seeking and behaviour before consulting a doctor.',
 f'**Methods:** Cross-sectional online survey of {n} adults in Baghdad (July–September 2026) using the Short Health Anxiety Inventory (SHAI-14) and the Cyberchondria Severity Scale (CSS-12), analysed with non-parametric group comparisons, χ² tests, correlation, multiple linear and binary logistic regression, and mediation analysis (Sobel test).',
 f'**Results:** Participants were mostly young ({pct(age20)} aged 20–29). AI chatbots were ticked by {E["ai_profile"]["ticked_ai_pct"]:.1f}% ({pct(ai_n)} including those who named a chatbot), more than search engines ({pct(se_n)}). Health anxiety correlated with cyberchondria (r = {sc["pearson_r"]:.2f}, 95% CI {ci(*sc["pearson_CI"])}) and remained its strongest predictor after adjustment (β = {b_shai.beta_std:.2f}), most strongly with excessive searching and post-search distress. Elevated health anxiety (SHAI-14 ≥ 18, a screening threshold, not a diagnosis) was found in {prev["HA_clin"]:.1f}%. After searching, {pct(cnt("beh_delay_reassured"))} delayed or skipped care because they felt reassured and {pct(cnt("share_never"))} never told their doctor, citing fear of judgement. The association between AI use and cyberchondria was not robust to how AI use was defined.',
 f'**Conclusion:** In this young, health-oriented convenience sample, health anxiety and cyberchondria were linked and AI chatbots were a major source of health information, without reliable evidence that they add to cyberchondria beyond health anxiety. Clinicians should ask patients, without judgement, what they have searched or asked an AI.',
 '**Keywords:** cyberchondria; health anxiety; artificial intelligence; chatbots; Iraq.']:
    P(a, space_after=3, size=13)

new = doc.add_section(WD_SECTION.NEW_PAGE)

# ================================================================== 1 INTRODUCTION
H('1. Introduction')
H('1.1 Background', 2)
P(f'Many people now look a symptom up online before they see a doctor. Often it goes into a search engine, or is described to an AI chatbot, well before a physician hears about it. The information is immediate, free and available at any hour, and it can help people decide whether a symptom needs medical attention. For a sizeable minority, however, searching makes the worry worse, a pattern known as cyberchondria {cite("white2009","starcevic2013")}. About four in five Iraqis were online by 2025 {cite("datareportal2025")}, yet we found no study from Baghdad on how this habit interacts with health anxiety or affects the consultation that follows.')
H('1.2 Health anxiety', 2)
P(f'Health anxiety is a persistent preoccupation with having, or getting, a serious illness, kept going by misreading normal bodily sensations. It runs on a continuum from passing worry to illness anxiety disorder and somatic symptom disorder in the DSM-5-TR {cite("apa2013")}. In the cognitive-behavioural model, sensations are read as signs of serious disease, and the resulting anxiety is maintained by safety behaviours such as body checking and reassurance seeking, which relieve it briefly but stop the person learning that the feared outcome does not happen {cite("salk1986")}.')
P(f'Health anxiety is common and costly: its lifetime prevalence is about 6% in the general population and up to 20% in hospital outpatients, and it generates unnecessary medical contacts {cite("tyrer2018")}. In Iraq, 49.5% of 1591 respondents to an online survey during the COVID-19 restrictions screened positive for health anxiety on the Health Anxiety Questionnaire {cite("karim2020")}.')
H('1.3 Cyberchondria', 2)
P(f'White and Horvitz showed in large-scale search logs that searches for common, harmless symptoms often escalated towards rare and serious diagnoses {cite("white2009")}. Starcevic and Berle defined cyberchondria as excessive or repeated online health searching that increases, rather than relieves, distress {cite("starcevic2013")}; searching itself is not pathological, but becomes cyberchondria when it is excessive, compulsive and distressing. The 33-item Cyberchondria Severity Scale has a 12-item short form (CSS-12) that keeps four subscales (excessiveness, compulsion, distress and reassurance seeking) {cite("mcelroy2019")}, and an Arabic version has shown acceptable structure in Lebanon {cite("hallit2023")}.')
H('1.4 Health anxiety and cyberchondria', 2)
P(f'The two are closely related but not identical: beyond its overlap with health anxiety, cyberchondria is linked with more functional impairment and healthcare use {cite("mathes2018")}, and in a randomised experiment searching the causes of provoked bodily symptoms raised health anxiety and the wish to see a physician {cite("jungmann2020")}. Two meta-analyses found that health anxiety correlates strongly with cyberchondria (r = 0.62 and 0.63), with subscale correlations from 0.24 to 0.66 {cite("mcmullan2019","schenkel2021")}. Whether the two fuel each other is unsettled. A four-wave Dutch panel of 5322 adults found early evidence of a two-way relationship, though only in people with non-clinical health anxiety {cite("tepoel2016")}.')
P('The terms used in this thesis overlap, so Box 1 sets out how they differ and how each was measured.')
caption_box = doc.add_paragraph(); caption_box.paragraph_format.keep_with_next = True; caption_box.paragraph_format.space_before = Pt(6); caption_box.paragraph_format.space_after = Pt(3)
_r = caption_box.add_run('Box 1. '); _r.bold = True; _r.font.name = FONT; _r.font.size = Pt(12)
_r = caption_box.add_run('Health anxiety, illness anxiety disorder, cyberchondria and ordinary online health searching'); _r.font.name = FONT; _r.font.size = Pt(12)
table(['', 'Health anxiety', 'Illness anxiety disorder', 'Cyberchondria', 'Ordinary online health searching'], [
    ['What it is', 'Worry about having or getting a serious illness, on a continuum from mild to severe', 'The DSM-5-TR diagnosis at the severe end: preoccupation for at least 6 months', 'Excessive or repeated online health searching that increases rather than relieves distress', 'Looking up information about a symptom, condition or treatment'],
    ['Key features', 'Misreading bodily sensations; checking; reassurance seeking', 'No or mild somatic symptoms; high health anxiety; excessive checking or avoidance', 'Excessiveness, compulsion, distress and reassurance seeking', 'Occasional, goal-directed; usually reduces uncertainty'],
    ['Status', 'Dimension (screened, not diagnosed)', 'Clinical diagnosis by a clinician', 'Behavioural pattern, not a diagnosis', 'Normal behaviour'],
    ['In this study', 'SHAI-14 (0–42; ≥ 18 elevated)', 'Not assessed', 'CSS-12 (12–60; four subscales)', 'Tools, motives and behaviour items'],
], widths=[2.6, 3.4, 3.4, 3.4, 3.2], size=9.5, compact=True, bold_rows=(),
   note=f'Sources: DSM-5-TR {cite("apa2013")}; cognitive model {cite("salk1986")}; cyberchondria {cite("starcevic2013","mcelroy2019")}.')
H('1.5 From search engines to AI chatbots', 2)
P(f'Most of this evidence predates large language model chatbots such as ChatGPT and Gemini, which answer in fluent, personal language, can be questioned again and again, and can seem more empathetic than physicians {cite("ayers2023")}. In a large US survey about one in five respondents had used ChatGPT for health information, and about a third of them changed medications or asked for referrals based on its answers {cite("ayo2024")}. It remains unclear whether chatbots relieve worry with calm answers or feed it by always being available for another round of reassurance.')
H('1.6 Searching and the doctor–patient relationship', 2)
P(f'Online information can help the relationship when patients discuss it with their physician, and strain it when they hide it {cite("luo2022")}. Reassurance seeking may lead to extra consultations, while false reassurance may delay care. In the Arab region, cyberchondria was common in Jeddah {cite("elzayat2023")} and linked with health anxiety in Saudi primary care {cite("pasayan2025")}, and across 13 Arabic-speaking countries trust in online information predicted delayed consultation {cite("dahshan2026")}. No comparable study exists from Iraq.')
H('1.7 Rationale', 2)
P('This study addresses three gaps: it gives, to our knowledge, the first estimate of the association between health anxiety and cyberchondria (CSS-12) in Baghdad; it examines AI chatbots separately from search engines; and it links both constructs to what clinicians see before and during a consultation.')
H('1.8 Aim, objectives and hypotheses', 2)
P('**Aim:** To study the relationship between health anxiety and cyberchondria among adults in Baghdad who search for health information online, with a focus on AI chatbots and pre-consultation behaviour.', indent=False)
P('**Objectives:**', indent=False)
for b in ['To describe where adults in Baghdad look for health information (online and through AI) and what they do before seeing a doctor.',
          'To estimate levels of health anxiety and cyberchondria and the strength of their association, independently of socio-demographic and digital-use factors (H1, H2).',
          'To examine statistical pathways consistent with a mutually reinforcing cycle (H3).',
          'To examine how health anxiety and cyberchondria relate to pre-consultation behaviour, disclosure of searches and trust in physicians (H4).']:
    numbered(b)
P('**Hypotheses:** (H1) People with more health anxiety have more cyberchondria, especially on the distress and excessiveness dimensions. (H2) This holds after adjustment for socio-demographic and digital-use factors. (H3) Part of the link between health anxiety and post-search distress runs, statistically, through excessive searching. (H4) People with more cyberchondria make more urgent visits and multiple consultations and report a more strained doctor–patient relationship. H1 and H2 were primary and H3 and H4 secondary; all other analyses were exploratory (Figure 1).')
figure(f'{FIG}/fig0a_framework.png', 'Conceptual framework of the study: health anxiety is associated with cyberchondria (H1) independently of covariates (H2), partly through excessive searching and post-search distress (H3), and cyberchondria with pre-consultation behaviour (H4).', width=14)

# ================================================================== 2 METHOD
H('2. Method')
H('2.1 Design, setting and participants', 2)
P(f'This analytical cross-sectional study follows the STROBE {cite("strobe2007")} and CHERRIES {cite("eysenbach2004")} reporting guidelines. Data were collected online in Baghdad between {pd.Timestamp(dates[0]):%d %B %Y} and {pd.Timestamp(dates[1]):%d %B %Y} by convenience and snowball sampling through Baghdad-based social-media and messaging groups. Adults aged 18 or over who could read Arabic or English and gave informed consent were eligible. The form accepted only one response per Google account, and no duplicate response patterns were found; all completed submissions were analysed.')
H('2.2 Sample size', 2)
P(f'Using Fisher\'s z with two-sided α = 0.05 and 80% power, {ss["n_needed_r_0_20"]} participants are needed to detect a correlation of r = 0.20 {cite("serdar2021")}; meta-analytic estimates are far larger (r ≈ 0.62), so the target is conservative. For proportions, {n} participants give a margin of error of ±{ss["moe_at_n"]:.1f}%.')
H('2.3 Questionnaire', 2)
P(f'A bilingual (Arabic–English) Google Form had five parts: (1) consent and socio-demographic data; (2) digital health-information seeking (tools, main AI chatbot, motives and trust in online/AI information); (3) the 14-item Short Health Anxiety Inventory (SHAI-14; items scored 0–3, total 0–42) {cite("salk2002")}, which has good reliability and validity {cite("arnaez2019","osterman2022")}; (4) the CSS-12 (items scored 1–5, total 12–60; four 3-item subscales) {cite("mcelroy2019")}; and (5) behaviour after searching, disclosure of searches to the physician and the effect on the relationship with physicians. The Arabic wording was written by the team without formal cross-cultural adaptation {cite("cruchinho2024")}; published Arabic versions {cite("hallit2023","alshayea2020")} were not used. The response options of one SHAI item (item 2) were displayed in a different order from the original and were scored by meaning.')
H('2.4 Definitions', 2)
for b in [f'**Elevated health anxiety:** SHAI-14 ≥ 18, the cut-off that best separated people with health anxiety from healthy controls in a Swedish diagnostic study {cite("osterman2022")}; it is a screening threshold, not a diagnosis, so prevalence at 15, 22 and 29 is also reported.',
          '**High cyberchondria:** CSS-12 > 33 (upper tertile), as the CSS-12 has no validated cut-off.',
          f'**AI-chatbot user:** ticked "AI chatbots" or named a chatbot; because {int(d.ai_model_inconsistent.sum())} respondents named one without ticking it, all AI analyses were repeated with the strict (ticked-only) definition.',
          '**Health-related background:** medical students, other health-science students and healthcare workers.',
          '**Recoding for analysis:** the three oldest age groups (40–49, 50–59 and ≥ 60 years; n = 36) were merged into one group (≥ 40) because each was small, and free-text “Other” answers to the education and occupation questions were assigned to the closest existing category (for example, “PhD” to postgraduate, a secondary-school student to non-health student, and an engineer or homemaker to non-health employed/other).']:
    bullet(b)
H('2.5 Statistical analysis', 2)
P(f'Data were analysed with IBM SPSS Statistics version 26 (IBM Corp., Armonk, NY); two-sided p < 0.05 was considered significant. Categorical variables are presented as frequencies and percentages, with 95% confidence intervals for prevalence, and continuous variables as mean ± SD and median (IQR). Internal consistency was assessed with Cronbach\'s α. Because scale scores were not normally distributed (Shapiro–Wilk test), scores were compared between two groups with the Mann–Whitney U test and between three or more groups with the Kruskal–Wallis H test. Associations between categorical variables were tested with Pearson\'s χ² test or Fisher\'s exact test, with Cramér\'s V as the effect size. The association between SHAI-14 and CSS-12 scores was measured with Pearson\'s (95% CI by Fisher\'s z transformation) and Spearman\'s correlation coefficients and with partial correlation controlling for covariates; Spearman\'s ρ was used to confirm the Pearson correlations because the scores were not normally distributed.')
P(f'Independent predictors of the CSS-12 score were identified by hierarchical multiple linear regression (enter method) with socio-demographic variables in block 1, digital-use variables in block 2 and the SHAI-14 score in block 3; multicollinearity was checked with the variance inflation factor, and the normality of the residuals with a histogram and a normal P-P plot. Binary logistic regression (enter method) was used for elevated health anxiety and for each behaviour, with results given as adjusted odds ratios (AOR) and 95% CI and model fit assessed with the Hosmer–Lemeshow test and the area under the ROC curve. Mediation was tested with the regression approach of Baron and Kenny {cite("baron1986")} on z-scores of all variables, and the significance of each indirect effect with the Sobel test {cite("sobel1982")}. As a sensitivity check, the main correlation was repeated after excluding straight-line responses and without SHAI item 2.')
H('2.6 Ethical considerations', 2)
P('The study was an anonymous online survey of consenting adults, carried out outside any hospital or health facility, with no intervention and no access to medical records; it was conducted under the supervision of the College of Medicine, University of Baghdad. Participation was voluntary: the first page of the form explained the purpose of the study, electronic informed consent (with confirmation of age ≥ 18) was required before any question, and participants could withdraw at any time by closing the form. No names, e-mail addresses or contact details were collected, and the data were used only for this research.')

# ================================================================== 3 RESULTS
''' + OVR + r'''
H('3. Results')
H('3.1 Participants and online health-information seeking', 2)
P(f'All {n} participants completed the questionnaire with no missing data. The sample was young ({pct(age20)} aged 20–29), {pct(fem)} were female, {pct(medst)} were medical students and {pct(hb)} had a health-related background (Table 1). AI chatbots were the most used tool ({E["ai_profile"]["ticked_ai_pct"]:.1f}% ticked; {pct(ai_n)} including those who named one), ahead of search engines ({pct(se_n)}); {pct(int((d.tool_profile=="AI without search engine").sum()))} used AI without any search engine and ChatGPT was used by {pct(int((d.ai_model=="ChatGPT").sum()))}. AI use fell from {d.loc[d.age4=="18-19","ai_user"].mean()*100:.0f}% at 18–19 years to {d.loc[d.age4=="≥40","ai_user"].mean()*100:.0f}% at 40 or older. The leading motives were convenience, deciding whether a doctor was needed and instant reassurance (Table 2, Figure 2).')
''' + TAB1 + '\n' + TAB2 + r'''
figure(f'{FIG}/fig2_tools_motives.png', 'Tools used and motivations for searching for health information online (n = 300).', width=15)
P(f'After searching, {pct(cnt("beh_delay_reassured"))} delayed or skipped care because the information was reassuring, {pct(cnt("beh_ignore"))} ignored the symptom, {pct(cnt("beh_multidoc"))} consulted several doctors and {pct(cnt("beh_urgent"))} sought urgent care. Only {pct(int((d.share=="Always").sum()))} always told their physician about their searches, whereas {pct(cnt("share_never"))} never did, citing fear of judgement, and {pct(int((d.relationship!="No negative impact").sum()))} said searching had complicated their relationship with, or trust in, their doctor (Figure 3).')
figure(f'{FIG}/fig3_behaviours.png', 'Behaviour after searching, disclosure of searches to physicians and perceived effect on the doctor–patient relationship (n = 300).', width=16)

H('3.2 Levels of health anxiety and cyberchondria', 2)
''' + TAB3.split('\n')[0] + r'''
P(f'Scale scores and reliability are shown in Table 3. The mean SHAI-14 score was {msd(shai)}; {npct(cnt("HA_clin"))} (95% CI {ci(*prev["HA_clin_CI"], k=1)}%) had elevated health anxiety, an estimate that ranged from {sens["prev_SHAI_ge_15"]:.1f}% at a cut-off of 15 to {sens["prev_SHAI_ge_29"]:.1f}% at 29 (Table 4). The mean CSS-12 score was {msd(css)}; participants searched frequently (excessiveness was the highest dimension) but searching rarely interfered with daily life (compulsion was the lowest). Both scales had good internal consistency (Cronbach\'s α = {rel.loc["SHAI-14","alpha"]:.2f} for the SHAI-14 and {rel.loc["CSS-12","alpha"]:.2f} for the CSS-12), and scores did not differ between participants who answered in Arabic and in English.')
''' + '\n'.join(TAB3.split('\n')[1:]) + '\n' + TAB4 + r'''

H('3.3 Association between health anxiety and cyberchondria', 2)
P(f'Health anxiety and cyberchondria were moderately correlated (r = {sc["pearson_r"]:.2f}, 95% CI {ci(*sc["pearson_CI"])}; Spearman ρ = {sc["spearman"]:.2f}; p < 0.001), and the correlation was unchanged after adjustment for age, gender, health background, chronic disease, trust and AI use (partial r = {part["r"]:.2f}) (Table 5, Figure 4). Health anxiety correlated with all four dimensions, most strongly with excessiveness (r = {r_sub["Excessiveness"]["pearson"]:.2f}) and distress (r = {r_sub["Distress"]["pearson"]:.2f}) and least with compulsion (r = {r_sub["Compulsion"]["pearson"]:.2f}) and reassurance seeking (r = {r_sub["Reassurance"]["pearson"]:.2f}).')
''' + TABC + r'''
figure(f'{FIG}/fig1_scatter_shai_css.png', 'Health anxiety (SHAI-14) against cyberchondria (CSS-12) with the least-squares line and 95% confidence band (n = 300).', width=11.5)

H('3.4 Factors associated with health anxiety and cyberchondria', 2)
''' + GVARS + r'''
P(f'Health anxiety (Table 6) was higher in participants with a chronic condition ({pv(gC.p)}), in those searching for instant reassurance ({msd(d.loc[d.mot_reassurance==1,"SHAI"])} vs {msd(d.loc[d.mot_reassurance==0,"SHAI"])}; {pv(gMR.p)}), in social-media users ({pv(gSMs.p)}) and AI users ({pv(gAIs.p)}), and differed by age ({pv(gA.p)}), education ({pv(gE.p)}) and occupation ({pv(gO.p)}); gender and language made no difference. Cyberchondria was higher in AI users than in non-users ({msd(d.loc[d.ai_user==1,"CSS"])} vs {msd(d.loc[d.ai_user==0,"CSS"])}; {pv(gAIc.p)}), highest in those combining AI with search engines ({pv(gTPc.p)}; Figure 5), and was also higher in social-media users ({pv(gSMc.p)}). Participants with elevated health anxiety more often had high cyberchondria (52.6% vs 23.0%; OR = {R["HA_CSShigh_OR"]["OR"]:.2f}, 95% CI {ci(*R["HA_CSShigh_OR"]["CI"])}) (Table 7).')
''' + TAB7.replace("widths=[5.2, 1.2, 2.8, 2.4, 2.8, 2.4], size=10", "widths=[5.2, 1.2, 2.8, 2.4, 2.8, 2.4], size=8.5, compact=True") + r'''
figure(f'{FIG}/fig6_css_by_tool.png', 'Cyberchondria (CSS-12) by online tool profile.', width=10.5)
''' + TAB8 + r'''

H('3.5 Independent predictors', 2)
P(f'In hierarchical regression (Table 8), socio-demographics explained {hier.R2.iloc[0]*100:.0f}% of the variance in cyberchondria (p = {hier.p_change.iloc[0]:.2f}), digital use raised this to {hier.R2.iloc[1]*100:.0f}% (p < 0.001), and health anxiety added a further {hier.dR2.iloc[2]*100:.1f}% (R² = {hier.R2.iloc[2]:.3f}, p < 0.001). Health anxiety was by far the strongest predictor (B = {b_shai.B:.2f}, β = {b_shai.beta_std:.2f}, p < 0.001); participants aged 30–39 (B = {b_a30.B:.1f}) and 40 or older (B = {b_a40.B:.1f}) also had higher adjusted scores than those aged 20–29. AI use was associated with a {b_ai.B:.1f}-point higher CSS score under the inclusive definition (p < 0.001), but not under the strict definition (B = {ai_alt_B:.2f}, {pv(ai_alt_p)}), so there was no reliable evidence of an independent AI effect. In logistic regression, elevated health anxiety was independently associated with higher cyberchondria (AOR = {lg_css.AOR:.2f} per SD, 95% CI {ci(lg_css.CI_low, lg_css.CI_high)}), searching for instant reassurance (AOR = {lg_mot.AOR:.2f}, 95% CI {ci(lg_mot.CI_low, lg_mot.CI_high)}) and younger age (AOR = {lg_age.AOR:.2f} per age-group step); the model fitted well (Hosmer–Lemeshow p = {SL["HL_p"]:.2f}) and discriminated well (AUC = {SL["AUC"]:.2f}), although with about five events per predictor the odds ratios may be overestimated (Table 9, Figure 6). In the sensitivity analyses the correlation was unchanged (r = 0.47–0.48).')
''' + TAB9 + '\n' + TAB10 + r'''
figure(f'{FIG}/fig7_forest_HA_simple.png', 'Adjusted odds ratios for elevated health anxiety (SHAI ≥ 18); orange: p < 0.05.', width=13)

H('3.6 Behaviour and pathways', 2)
''' + BVARS + r'''
P(f'With both scores in the same models (Table 10), behaviour was related more to cyberchondria than to health anxiety. Higher CSS scores went with urgent visits (AOR = {bU.AOR:.2f}, {pv(bU.p)}), less ignoring of symptoms (AOR = {bI.AOR:.2f}, {pv(bI.p)}), a negative effect on the relationship with physicians (AOR = {bR.AOR:.2f}, {pv(bR.p)}) and lower odds of never telling the physician about searches, that is, more disclosure (AOR = {bNC.AOR:.2f}, {pv(bNC.p)}). Health anxiety pointed the other way, towards concealment (AOR = {bNS.AOR:.2f}, {pv(bNS.p)}). Greater trust in online/AI information went with fewer multiple-doctor consultations (AOR = {bM.AOR:.2f}, {pv(bM.p)}) and, not significantly, with more delay of care when reassured (AOR = {bh("Delay/skip care (reassured)", "trust").AOR:.2f}, {pv(bh("Delay/skip care (reassured)", "trust").p)}). Neither score was associated with multiple consultations, self-medication or delaying care, and fear-driven delay was of borderline significance ({pv(bT.p)}).')
''' + TAB11 + r'''
P(f'In mediation models (Table 11, Figure 7), excessive searching accounted, statistically, for about a third of the link between health anxiety and post-search distress (indirect effect = {SM[0]["indirect"]:.2f}, Sobel z = {SM[0]["sobel_z"]:.2f}, p < 0.001), and post-search distress for almost all of the link with reassurance-seeking consultations (indirect = {SM[1]["indirect"]:.2f}, Sobel z = {SM[1]["sobel_z"]:.2f}, p < 0.001; direct c′ = {SM[1]["c_prime"]:.2f}, not significant). The reverse ordering was also significant (indirect = {SM[2]["indirect"]:.2f}, Sobel z = {SM[2]["sobel_z"]:.2f}), so direction cannot be established. Participants with elevated health anxiety scored higher on all four dimensions (Figure 8).')
''' + TAB12 + r'''
figure(f'{FIG}/fig8_mediation_sobel.png', 'Mediation models: (A) excessive searching between health anxiety and post-search distress; (B) post-search distress between health anxiety and reassurance seeking.', width=15.5)
figure(f'{FIG}/fig5_subscales_by_HA.png', 'Cyberchondria dimensions by health-anxiety status (mean ± 95% CI).', width=11)

# ================================================================== 4 DISCUSSION
H('4. Discussion')
H('4.1 Health anxiety and cyberchondria', 2)
P(f'To our knowledge, this is the first study to use the CSS-12 in Baghdad and one of the first to examine AI chatbots alongside search engines before a medical visit. Health anxiety and cyberchondria were moderately associated (r = {sc["pearson_r"]:.2f}), independently of the covariates, supporting H1 and H2. The association was concentrated in excessiveness and distress, the dimensions closest to fearful searching and its emotional aftermath, as the cognitive model predicts {cite("salk1986")}. The 19% with elevated health anxiety is a screening estimate that varied from 0.7% to 33% across the four published cut-offs (15 to 29), but it suggests that a substantial minority of digitally active adults in Baghdad report elevated health worry.')
H('4.2 Comparison with worldwide and regional results', 2)
P(f'**Worldwide.** Our correlation was weaker than the meta-analytic estimates of 0.62–0.63 {cite("mcmullan2019","schenkel2021")}. Low and narrowly spread health anxiety (mean SHAI 12.3), recruitment of confident Internet users and the short CSS-12, where most earlier studies used the 33-item scale, may all have weakened it. AI use here ({E["ai_profile"]["ticked_ai_pct"]:.0f}–{ai_n/n*100:.1f}%) was far higher than in a 2024 US survey (about one in five) {cite("ayo2024")} or a 2025 survey (21%, against 98% for search engines) {cite("yun2025")}, partly because the sample was young.')
P(f'**Iraq and the Arab region.** During the COVID-19 restrictions, 49.5% of Iraqi respondents screened positive for health anxiety {cite("karim2020")}; that survey used a different questionnaire during a pandemic, so it is not directly comparable with our 19%, but both point to a substantial minority with elevated health worry. Our results agree with Arab-region data from Jeddah, Saudi primary care, Lebanon and 1435 Egyptian medical students, of whom 85.8% showed moderate cyberchondria {cite("elzayat2023","pasayan2025","hallit2023","elzoghby2024")}, and across 13 Arabic-speaking countries trust in online information predicted delayed consultation {cite("dahshan2026")}. A Palestinian study using the same SHAI threshold found elevated health anxiety least common among medical students {cite("fasfoos2026")}, and in our sample medical students did not differ from others after adjustment for age.')
H('4.3 Do health anxiety and cyberchondria fuel each other?', 2)
P(f'The mediation results fit the reinforcing cycle proposed by the cognitive model and the Dutch longitudinal study {cite("tepoel2016")}: more health anxiety goes with more searching, more searching with more distress, and distress with reassurance seeking. They must not be over-interpreted. Cross-sectional mediation can be seriously biased for longitudinal processes {cite("olaughlin2018")}, a significant indirect effect cannot identify the causal order {cite("rohrer2022")}, the reverse model was equally significant, and the mediators and outcomes are subscales of one instrument {cite("podsakoff2024")}. The data are compatible with a cycle but cannot demonstrate it; H3 is supported statistically, not causally.')
H('4.4 AI chatbots', 2)
P(f'The higher cyberchondria of AI users vanished under the strict definition and rested on a small, older comparison group: an absence of evidence, not evidence of no effect. Higher trust in online/AI information went with fewer multiple-doctor consultations, suggesting that trusted AI answers may replace some "doctor shopping", but also offering a route for false reassurance; a non-significant trend towards reassured delay (AOR = {bh("Delay/skip care (reassured)", "trust").AOR:.2f}, {pv(bh("Delay/skip care (reassured)", "trust").p)}) echoes the regional finding that trust predicts delayed consultation.')
H('4.5 The consultation and medical students', 2)
P(f'Delaying care because of reassurance ({pct(cnt("beh_delay_reassured"))}) may save visits for minor symptoms but risks late diagnosis for serious ones, and it was unrelated to either score, so it is not limited to anxious users. Almost a third never told their doctor about their searches. Higher cyberchondria went with more disclosure, whereas higher health anxiety may go with concealment (p = 0.017, uncorrected), perhaps from fear of being labelled the "worried well"; information discussed openly strengthens the relationship, whereas hidden information undermines it {cite("luo2022")}. H4 is partly supported: higher cyberchondria went with urgent visits and a strained relationship (both p < 0.05, uncorrected for multiple testing), but not with multiple consultations. Medical students\' higher unadjusted health anxiety disappeared after adjustment for age, and their cyberchondria equalled that of others, so medical knowledge did not appear to protect against cyberchondria.')
H('4.6 Strengths and limitations', 2)
P('Strengths include two established, reliable scales, a bilingual questionnaire, separate assessment of AI chatbots, complete data, adjustment for confounders in multivariable models and sensitivity analyses. The main limitations are:', indent=True)
for b in ['**Design:** cross-sectional data cannot establish direction; mediation describes statistical pathways only.',
          f'**Sample:** an online convenience sample, young and with many medical students ({pct(medst)}), so percentages cannot be generalised to Baghdad; residence was not verified by a question.',
          '**Measurement:** Arabic wording without formal back-translation or a confirmatory factor analysis; one SHAI item with reordered options; CSS item 3 mentions only search engines and may miss repeated chatbot use; behaviour, trust and disclosure measured with single, non-validated items; all data self-reported.',
          '**Analysis:** many statistical tests were run without correction for multiple comparisons, so some significant results may be due to chance; small subgroups (34 AI non-users); about five events per predictor in the logistic model; the AI result depends on how 32 respondents were classified.']:
    bullet(b)

# ================================================================== 5 CONCLUSIONS
H('5. Conclusions and Recommendations')
H('5.1 Conclusions', 2)
for b in [f'AI chatbots, mainly ChatGPT, are a leading source of health information before consulting a doctor among digitally active adults in Baghdad ({E["ai_profile"]["ticked_ai_pct"]:.1f}% ticked; {pct(ai_n)} including those who named one).',
          f'About one in five ({prev["HA_clin"]:.0f}%) had elevated health anxiety on a screening threshold; younger people and reassurance seekers were most affected.',
          f'Health anxiety and cyberchondria are moderately associated (r = {sc["pearson_r"]:.2f}), compatible with a reinforcing cycle that this design cannot prove.',
          'There is no reliable evidence that AI use adds to cyberchondria beyond health anxiety.',
          'Searching shapes the consultation: about a third delay care when reassured and about a third never disclose their searches; higher cyberchondria may go with more disclosure of searches to the doctor.']:
    numbered(b)
H('5.2 Recommendations', 2)
for b in ['**Clinicians:** ask every patient, without judgement, what they have searched or asked an AI; treat repeated searching and reassurance seeking as possible signs of health anxiety; teach digital and AI health literacy in medical school.',
          '**Ministry of Health:** the Ministry may consider Arabic digital and AI health-literacy campaigns that warn about false reassurance, and reliable Arabic triage sources.',
          '**AI developers:** developers may consider anxiety-aware health answers that avoid escalating rare diagnoses and encourage appropriate consultation.',
          f'**Research:** longitudinal studies, probability samples and formally adapted Arabic scales; intervention trials are needed, as ClinicalTrials.gov lists only nine cyberchondria studies and none in Iraq {cite("ctgov2026")}.']:
    bullet(b)
'''

APPX = r"""
page_break()
H('Appendix. Study questionnaire')
def QP(text, size=10.5, after=1, bold=False, indent=0.0, italic=False):
    qp = doc.add_paragraph(); qp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    qp.paragraph_format.line_spacing = 1.0; qp.paragraph_format.space_after = Pt(after); qp.paragraph_format.space_before = Pt(0)
    if indent: qp.paragraph_format.left_indent = Cm(indent)
    add_runs(qp, f'**{text}**' if bold else (f'*{text}*' if italic else text), size); return qp
def Q(num, text, opts=None):
    qp = QP(f'**{num}.** {text}', after=0 if opts else 3)
    qp.paragraph_format.keep_with_next = bool(opts)
    if opts: QP(' · '.join(opts), size=9.5, after=3, indent=0.6, italic=True)
QP('Administered online through Google Forms in English and Arabic (every item shown in both languages; the Arabic text is not reproduced here). All items were required except Q7 and Q9. ○ = one answer; ☐ = all that apply.', size=10, after=6, italic=True)
QP('Part 1. Consent and socio-demographic data', bold=True, size=11, after=2)
Q(1, 'I confirm that I am at least 18 years of age, have read the description of this study and voluntarily agree to participate; I can withdraw at any point without penalty.', ['○ I explicitly agree and consent to participate'])
Q(2, 'Age group', ['○ 18–19', '20–29', '30–39', '40–49', '50–59', '60+'])
Q(3, 'Gender', ['○ Male', 'Female'])
Q(4, 'Highest level of education completed', ['○ Currently a student', 'Postgraduate (Master\'s or PhD)', 'Bachelor\'s', 'Diploma/vocational', 'High school or below', 'Other'])
Q(5, 'Nature of current study or work', ['○ Medical student', 'Student in another healthcare field', 'Medical doctor', 'Other healthcare professional', 'Student in a non-healthcare field', 'Employed in a non-healthcare field', 'Other'])
Q(6, 'Do you have a diagnosed chronic medical condition?', ['○ Yes', 'No'])
Q(7, 'If yes, please specify (optional, free text).')
QP('Part 2. Digital health information seeking', bold=True, size=11, after=2)
Q(8, 'Which tools do you use most frequently to look up symptoms online?', ['☐ Search engine (e.g. Google)', 'AI chatbots', 'Dedicated medical platforms (e.g. WebMD, Mayo Clinic)', 'Social media (e.g. Facebook, Reddit, Instagram)'])
Q(9, 'If you use AI, which one most of the time?', ['○ ChatGPT', 'Gemini', 'Claude', 'Other'])
Q(10, 'Primary motivation for searching medical information online', ['☐ Convenience and easy access', 'High cost or difficulty of doctor visits', 'Instant reassurance about an unexplained symptom', 'Self-diagnosis or double-checking a prescription', 'To see if a symptom is serious enough to need a doctor', 'Other'])
Q(11, 'How much do you trust medical information generated by online tools/AI (1–5)?', ['○ 1 Not at all', '2 Slightly', '3 Moderately', '4 Very much', '5 Completely'])
QP('Part 3. Short Health Anxiety Inventory (SHAI-14): choose the statement that best describes you (scored 0–3)', bold=True, size=11, after=2)
SHAI = [('Worrying about health', 'I do not worry about my health / occasionally worry / spend much of my time worrying / spend most of my time worrying'),
 ('Body awareness*', 'I notice aches/pains as much as most people (of my age) / less than most people / more than most people / I am aware of aches/pains all the time'),
 ('Bodily sensations', 'As a rule I am not aware of bodily sensations or changes / sometimes aware / often aware / constantly aware'),
 ('Thoughts of illness', 'Resisting thoughts of illness is never a problem / most of the time I can resist them / I try but am often unable to / they are so strong I no longer try'),
 ('Fear of serious illness', 'As a rule I am not afraid I have a serious illness / sometimes afraid / often afraid / always afraid'),
 ('Images of illness', 'I do not have images of myself being ill / occasionally / frequently / constantly'),
 ('Distraction from health thoughts', 'No difficulty taking my mind off my health / sometimes difficult / often difficult / nothing can take my mind off it'),
 ('Medical reassurance', 'Lastingly relieved if my doctor says nothing is wrong / relieved but worries sometimes return / relieved but worries always return / not relieved'),
 ('Hearing about illness', 'If I hear about an illness I never think I have it / sometimes / often / always'),
 ('Interpretation of sensations', 'If I have a bodily sensation I rarely wonder what it means / often wonder / always wonder / must know what it means'),
 ('Perceived risk', 'I usually feel at very low / fairly low / moderate / high risk of developing a serious illness'),
 ('Thinking you are ill', 'I never / sometimes / often think I have a serious illness / I usually think I am seriously ill'),
 ('Unexplained sensations', 'If I notice an unexplained sensation I do not find it difficult / sometimes / often / always find it difficult to think about other things'),
 ('Family and friends', 'My family/friends would say I do not worry enough / have a normal attitude / worry too much about my health / am a hypochondriac')]
for k, (h, o) in enumerate(SHAI, 12):
    Q(k, h, [o])
QP('*Options for Q13 were displayed in the order shown (the original scale lists "less than" before "as much as"); scoring followed the meaning of each statement.', size=9, after=4, italic=True)
QP('Part 4. Cyberchondria Severity Scale (CSS-12): ○ Never (1) · Rarely (2) · Sometimes (3) · Often (4) · Always (5)', bold=True, size=11, after=2)
CSS = ['If I notice an unexplained bodily sensation, I search for it on the Internet.', 'I read different web pages about the same health condition.', 'I enter the same symptoms into a search engine on more than one occasion.',
 'Researching symptoms online distracts me from reading news, sports or entertainment.', 'Researching symptoms online interrupts my work (e.g. emails, documents).', 'Researching symptoms online interrupts my offline social activities.',
 'I panic when I read online that a symptom I have could be a sign of a rare or serious condition.', 'I feel fine until I read about a serious medical condition online.', 'I feel more anxious or distressed after researching symptoms online.',
 'Researching symptoms online leads me to consult my general practitioner.', 'I suggest to my doctor a specific diagnostic procedure I have read about online (e.g. a biopsy, a blood test).', 'Researching symptoms online leads me to consult other medical specialists.']
for k, s in enumerate(CSS, 26):
    Q(k, s)
QP('Part 5. Pre-consultation behaviour and the doctor–patient relationship', bold=True, size=11, after=2)
Q(38, 'After searching your symptoms online, what are your most frequent responses?', ['☐ Buy self-prescribed medication without a doctor', 'Delay or skip medical help because the information reassured me', 'Delay help because the information frightened or overwhelmed me', 'Seek an urgent appointment or the emergency room', 'Visit several doctors to double-check', 'Ignore the symptom'])
Q(39, 'During a consultation, do you share your online or AI findings with your physician?', ['○ Yes, always', 'Sometimes, depending on how the doctor responds', 'No, never, for fear of being judged or dismissed'])
Q(40, 'How has digital health information-seeking affected your relationship with and trust in healthcare providers?', ['○ Significantly reduced my trust', 'Somewhat complicated the relationship, but I still follow advice', 'No negative impact; it supplements my doctor\'s care'])
Q(41, 'Which language did you rely on most while completing this questionnaire?', ['○ Mostly English', 'Mostly Arabic'])
"""
MAIN = MAIN.replace('are provided in the supplementary workbook', 'are available from the authors').replace('are listed in the supplementary workbook', 'are available from the authors').replace('are given in the supplementary workbook', 'are available from the authors')
code = HEAD + '\n' + MAIN + '\n' + REFS_PART + '\n' + APPX + '\n' + TAIL
assert "f'{OUT}/toc_entries.json'" in code
code = code.replace("f'{OUT}/toc_entries.json'", "f'{OUT}/toc_entries_short.json'")
_HDR = """
for _s in doc.sections:
    _s.header.is_linked_to_previous = False
    _hp = _s.header.paragraphs[0]; _hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _hr = _hp.add_run('Health Anxiety, AI Chatbot Use and Cyberchondria in Baghdad'); _hr.italic = True; _hr.font.name = FONT; _hr.font.size = Pt(10); _hr.font.color.rgb = RGBColor(0x1F, 0x3B, 0x4D)
    _pPr = _hp._p.get_or_add_pPr(); _bd = OxmlElement('w:pBdr'); _b = OxmlElement('w:bottom')
    _b.set(qn('w:val'), 'single'); _b.set(qn('w:sz'), '4'); _b.set(qn('w:space'), '4'); _b.set(qn('w:color'), '1F3B4D'); _bd.append(_b); _pPr.append(_bd)
"""
_anc = "for s in doc.sections:\n    s.page_height"
assert _anc in code
code = code.replace(_anc, _HDR + _anc, 1)
exec(compile(code, '04s_build_short (assembled)', 'exec'), {'__name__': '__main__'})
