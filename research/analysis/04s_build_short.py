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
R0 = idx("H('3. Results')")

TAB1 = block("T1 = X['T1_demographics']", "table(['Characteristic'", R0)
TAB2 = block("T2 = X['T2_digital_behaviour']", "      note='Tools, motivations", R0)
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

MAIN = r'''
# ================================================================== ABSTRACT (short)
H('Summary / Abstract')
for a in [
 f'**Background:** Many adults look up symptoms online before seeing a doctor, increasingly with artificial-intelligence (AI) chatbots. Health anxiety and cyberchondria (excessive, distressing online health searching) are thought to feed each other, but evidence from Iraq, and on AI chatbots, is scarce.',
 f'**Objectives:** To measure the association between health anxiety and cyberchondria among adults in Baghdad, and to describe online and AI health-information seeking and behaviour before consulting a doctor.',
 f'**Methods:** Cross-sectional online survey of {n} adults in Baghdad (July–September 2026) using the Short Health Anxiety Inventory (SHAI-14) and the Cyberchondria Severity Scale (CSS-12), analysed with FDR-corrected group comparisons, robust regression and bootstrapped mediation.',
 f'**Results:** Participants were mostly young ({pct(age20)} aged 20–29). AI chatbots were ticked by {E["ai_profile"]["ticked_ai_pct"]:.1f}% ({pct(ai_n)} including those who named a chatbot), more than search engines ({pct(se_n)}). Health anxiety correlated with cyberchondria (r = {sc["pearson_r"]:.2f}, 95% CI {ci(*sc["pearson_CI"])}) and remained its strongest predictor after adjustment (β = {b_shai.beta_std:.2f}), most strongly with excessive searching and post-search distress. Elevated health anxiety (SHAI-14 ≥ 18, a screening threshold, not a diagnosis) was found in {prev["HA_clin"]:.1f}%. After searching, {pct(cnt("beh_delay_reassured"))} delayed care because they felt reassured and {pct(cnt("share_never"))} never told their doctor, citing fear of judgement. The association between AI use and cyberchondria was not robust to how AI use was defined.',
 f'**Conclusion:** In this young, health-oriented convenience sample, health anxiety and cyberchondria were linked and AI chatbots were a major source of health information, without reliable evidence that they add to cyberchondria beyond health anxiety. Clinicians should ask patients, without judgement, what they have searched or asked an AI.',
 '**Keywords:** cyberchondria; health anxiety; artificial intelligence; chatbots; Iraq.']:
    P(a, space_after=4)

new = doc.add_section(WD_SECTION.NEW_PAGE)

# ================================================================== 1 INTRODUCTION
H('1. Introduction')
H('1.1 Background', 2)
P(f'Many people now look a symptom up online before they see a doctor. Often it goes into a search engine, or is described to an AI chatbot, well before a physician hears about it. The information is immediate, free and available at any hour, and it can help people decide whether a symptom needs medical attention. For a sizeable minority, however, searching makes the worry worse, a pattern known as cyberchondria {cite("white2009","starcevic2013")}. About four in five Iraqis were online by 2025 {cite("datareportal2025")}, yet we found no study from Baghdad on how this habit interacts with health anxiety or affects the consultation that follows.')
H('1.2 Health anxiety', 2)
P(f'Health anxiety is a persistent preoccupation with having, or getting, a serious illness, kept going by misreading normal bodily sensations. It runs on a continuum from passing worry to illness anxiety disorder and somatic symptom disorder in the DSM-5 {cite("apa2013")}. In the cognitive-behavioural model, sensations are read as signs of serious disease, and the resulting anxiety is maintained by safety behaviours such as body checking and reassurance seeking, which relieve it briefly but stop the person learning that the feared outcome does not happen {cite("salk1986")}.')
P(f'Health anxiety is common and costly: its lifetime prevalence is about 6% in the general population and up to 20% in hospital outpatients, and it generates unnecessary medical contacts {cite("tyrer2018")}. In Iraq, 49.5% of 1591 respondents to an online survey during the COVID-19 restrictions screened positive for health anxiety on the Health Anxiety Questionnaire {cite("karim2020")}.')
H('1.3 Cyberchondria', 2)
P(f'White and Horvitz showed in large-scale search logs that searches for common, harmless symptoms often escalated towards rare and serious diagnoses {cite("white2009")}. Starcevic and Berle defined cyberchondria as excessive or repeated online health searching that increases, rather than relieves, distress {cite("starcevic2013")}; searching itself is not pathological, but becomes cyberchondria when it is excessive, compulsive and distressing. The 33-item Cyberchondria Severity Scale has a 12-item short form (CSS-12) keeps four subscales (excessiveness, compulsion, distress and reassurance seeking) {cite("mcelroy2019")}, and an Arabic version has shown acceptable structure in Lebanon {cite("hallit2023")}.')
H('1.4 Health anxiety and cyberchondria', 2)
P(f'The two are closely related but not identical: beyond its overlap with health anxiety, cyberchondria is linked with more functional impairment and healthcare use {cite("mathes2018")}, and in a randomised experiment searching the causes of provoked bodily symptoms raised health anxiety and the wish to see a physician {cite("jungmann2020")}. Two meta-analyses found that health anxiety correlates strongly with cyberchondria (r = 0.62 and 0.63), with subscale correlations from 0.24 to 0.66 {cite("mcmullan2019","schenkel2021")}. Whether the two fuel each other is unsettled. A four-wave Dutch panel of 5322 adults found early evidence of a two-way relationship, though only in people with non-clinical health anxiety {cite("tepoel2016")}.')
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
P(f'This analytical cross-sectional study follows the STROBE {cite("strobe2007")} and CHERRIES {cite("eysenbach2004")} reporting guidelines. Data were collected online in Baghdad between {pd.Timestamp(dates[0]):%d %B %Y} and {pd.Timestamp(dates[1]):%d %B %Y} by convenience and snowball sampling through Baghdad-based social-media and messaging groups. Adults aged 18 or over who could read Arabic or English and gave informed consent were eligible. All completed submissions were analysed; no duplicate response patterns were found [Authors to state whether Google Forms limited submissions to one per account]. Three responses annotated by the team during data collection [authors to state the reason] were kept and tested in a sensitivity analysis.')
H('2.2 Sample size', 2)
P(f'Using Fisher\'s z with two-sided α = 0.05 and 80% power, {ss["n_needed_r_0_20"]} participants are needed to detect a correlation of r = 0.20 {cite("serdar2021")}; meta-analytic estimates are far larger (r ≈ 0.62), so the target is conservative. For proportions, {n} participants give a margin of error of ±{ss["moe_at_n"]:.1f}%.')
H('2.3 Questionnaire', 2)
P(f'A bilingual (Arabic–English) Google Form had five parts: (1) consent and socio-demographic data; (2) digital health-information seeking (tools, main AI chatbot, motives and trust in online/AI information); (3) the 14-item Short Health Anxiety Inventory (SHAI-14; items scored 0–3, total 0–42) {cite("salk2002")}, which has good reliability and validity {cite("osterman2022")}; (4) the CSS-12 (items 1–5, total 12–60; four 3-item subscales) {cite("mcelroy2019")}; and (5) behaviour after searching, disclosure of searches to the physician and the effect on the relationship with physicians. The Arabic wording was written by the team without formal cross-cultural adaptation {cite("cruchinho2024")}; published Arabic versions {cite("hallit2023","alshayea2020")} were not used. The response options of one SHAI item (item 2) were displayed in a different order from the original and were scored by meaning.')
H('2.4 Definitions', 2)
for b in [f'**Elevated health anxiety:** SHAI-14 ≥ 18, the cut-off that best separated people with health anxiety from healthy controls in a Swedish diagnostic study {cite("osterman2022")}; it is a screening threshold, not a diagnosis, so prevalence at 15, 22 and 29 is also reported.',
          '**High cyberchondria:** CSS-12 > 33 (upper tertile), as the CSS-12 has no validated cut-off.',
          f'**AI-chatbot user:** ticked "AI chatbots" or named a chatbot; because {int(d.ai_model_inconsistent.sum())} respondents named one without ticking it, all AI analyses were repeated with the strict (ticked-only) definition.',
          '**Health-related background:** medical students, other health-science students and healthcare workers.']:
    bullet(b)
H('2.5 Statistical analysis', 2)
P(f'Analyses were scripted in Python 3 (two-sided α = 0.05). Reliability was assessed with Cronbach\'s α and McDonald\'s ω {cite("hayescoutts2020")}, structure with confirmatory factor analysis (maximum likelihood), and equivalence of Arabic and English responders with multi-group measurement invariance {cite("leitgob2023")} and item-level differential item functioning {cite("cosic2026")}. Associations were tested with Pearson and Spearman correlations (bootstrap CIs) and partial correlations; dependent correlations were compared with Williams\' T2 test {cite("steiger1980")}. Scores were compared between groups with Mann–Whitney U or Kruskal–Wallis tests and categorical variables with χ² or Fisher\'s exact tests. Because many tests were run, p-values within each family were adjusted by the Benjamini–Hochberg false discovery rate (q-values) {cite("bh1995")}, and associations that did not survive correction are called exploratory.')
P(f'Multivariable analyses comprised hierarchical robust (HC3) linear regression of CSS on socio-demographics, digital use and SHAI; logistic regression of elevated health anxiety (AUC corrected for optimism by bootstrap) and of each behaviour; and exploratory mediation models with 5000 bootstrap resamples {cite("hayes2022")}, plus moderation by interaction terms. Sensitivity analyses excluded annotated and straight-line responses, removed SHAI item 2 and compared early with late responders.')
H('2.6 Ethical considerations', 2)
P('Participation was voluntary and anonymous; electronic informed consent (with confirmation of age ≥ 18) was required before any question, and no names or contact details were collected. [Ethical approval: committee name, approval number and date to be inserted.]')

# ================================================================== 3 RESULTS
H('3. Results')
H('3.1 Participants and online health-information seeking', 2)
P(f'All {n} participants completed the questionnaire with no missing data. The sample was young ({pct(age20)} aged 20–29), {pct(fem)} were female, {pct(medst)} were medical students and {pct(hb)} had a health-related background (Table 1). AI chatbots were the most used tool ({E["ai_profile"]["ticked_ai_pct"]:.1f}% ticked; {pct(ai_n)} including those who named one), ahead of search engines ({pct(se_n)}); {pct(int((d.tool_profile=="AI without search engine").sum()))} used AI without any search engine and ChatGPT was used by {pct(int((d.ai_model=="ChatGPT").sum()))}. AI use fell from {d.loc[d.age4=="18-19","ai_user"].mean()*100:.0f}% at 18–19 years to {d.loc[d.age4=="≥40","ai_user"].mean()*100:.0f}% at 40 or older. The leading motives were convenience, deciding whether a doctor was needed and instant reassurance (Table 2, Figure 2).')
''' + TAB1 + '\n' + TAB2 + r'''
figure(f'{FIG}/fig2_tools_motives.png', 'Tools used and motivations for searching for health information online (n = 300).', width=15)
P(f'After searching, {pct(cnt("beh_delay_reassured"))} delayed or skipped care because the information was reassuring, {pct(cnt("beh_ignore"))} ignored the symptom, {pct(cnt("beh_multidoc"))} consulted several doctors and {pct(cnt("beh_urgent"))} sought urgent care. Only {pct(int((d.share=="Always").sum()))} always told their physician about their searches, whereas {pct(cnt("share_never"))} never did, citing fear of judgement, and {pct(int((d.relationship!="No negative impact").sum()))} said searching had complicated their relationship with, or trust in, their doctor (Figure 3).')
figure(f'{FIG}/fig3_behaviours.png', 'Behaviour after searching, disclosure of searches to physicians and perceived effect on the doctor–patient relationship (n = 300).', width=16)

H('3.2 Levels of health anxiety and cyberchondria', 2)
''' + TAB3.split('\n')[0] + r'''
P(f'The mean SHAI-14 score was {msd(shai)}; {npct(cnt("HA_clin"))} (95% CI {ci(*prev["HA_clin_CI"], k=1)}%) had elevated health anxiety, an estimate that ranged from {sens["prev_SHAI_ge_15"]:.1f}% at a cut-off of 15 to {sens["prev_SHAI_ge_29"]:.1f}% at 29 (Table 4). The mean CSS-12 score was {msd(css)}; participants searched frequently (excessiveness was the highest dimension) but searching rarely interfered with daily life (compulsion was the lowest). Both scales were reliable (α = {rel.loc["SHAI-14","alpha"]:.2f} and {rel.loc["CSS-12","alpha"]:.2f}), the four-factor CSS-12 structure fitted acceptably (CFI = {cfa.iloc[3].CFI:.3f}, RMSEA = {cfa.iloc[3].RMSEA:.3f}), and the CSS-12 was fully invariant across Arabic and English responders; the SHAI-14 reached metric but not scalar invariance from a weak baseline, so its language comparisons need caution (Table 3).')
''' + '\n'.join(TAB3.split('\n')[1:]) + '\n' + TAB4 + r'''

H('3.3 Association between health anxiety and cyberchondria', 2)
P(f'Health anxiety and cyberchondria were moderately correlated (r = {sc["pearson_r"]:.2f}, 95% CI {ci(*sc["pearson_CI"])}; Spearman ρ = {sc["spearman"]:.2f}; p < 0.001), and the correlation was unchanged after adjustment for age, gender, health background, chronic disease, trust and AI use (partial r = {part["r"]:.2f}) (Table 5, Figure 4). Correlations with excessiveness (r = {r_sub["Excessiveness"]["pearson"]:.2f}) and distress (r = {r_sub["Distress"]["pearson"]:.2f}) were significantly stronger than with compulsion and reassurance seeking (Williams\' T2, p < 0.001). Item by item, cyberchondria followed fear of serious illness and the interpretation of bodily sensations, not mere awareness of sensations; {ib["sig_fdr"]} of 168 item pairs remained significant after FDR correction.')
''' + TABC + r'''
figure(f'{FIG}/fig1_scatter_shai_css.png', 'Health anxiety (SHAI-14) against cyberchondria (CSS-12) with the least-squares line and 95% confidence band (n = 300).', width=11.5)

H('3.4 Factors associated with health anxiety and cyberchondria', 2)
''' + GVARS + r'''
P(f'Across 162 group comparisons (Table 6), health anxiety was higher with a chronic condition (q = {gC.q_FDR:.3f}) and, most clearly, in those searching for instant reassurance (q = {gMR.q_FDR:.3f}); differences by age, education and occupation were borderline and exploratory, and gender made no difference. Under the inclusive definition, AI users had higher cyberchondria (q = {gAIc.q_FDR:.3f}), highest in those combining AI with search engines (Figure 5). Participants with elevated health anxiety more often had high cyberchondria (52.6% vs 23.0%; OR = {R["HA_CSShigh_OR"]["OR"]:.2f}) (Table 7).')
''' + TAB7.replace("widths=[5.2, 1.2, 2.8, 2.4, 2.8, 2.4], size=10", "widths=[5.2, 1.2, 2.8, 2.4, 2.8, 2.4], size=9.5") + r'''
figure(f'{FIG}/fig6_css_by_tool.png', 'Cyberchondria (CSS-12) by online tool profile.', width=10.5)
''' + TAB8 + r'''

H('3.5 Independent predictors', 2)
P(f'In hierarchical regression (Table 8), socio-demographics explained {hier.R2.iloc[0]*100:.0f}% of the variance in cyberchondria, digital use raised this to {hier.R2.iloc[1]*100:.0f}%, and health anxiety added a further {hier.dR2.iloc[2]*100:.1f}% (R² = {hier.R2.iloc[2]:.3f}). Health anxiety was by far the strongest predictor (B = {b_shai.B:.2f}, β = {b_shai.beta_std:.2f}, p < 0.001). AI use was associated with a {b_ai.B:.1f}-point higher CSS score under the inclusive definition, but not under the strict definition (B = {ai_alt_B:.2f}, {pv(ai_alt_p)}), so there was no reliable evidence of an independent AI effect. Elevated health anxiety was independently associated with higher cyberchondria (AOR = {lg_css.AOR:.2f} per SD), searching for instant reassurance (AOR = {lg_mot.AOR:.2f}) and younger age (AOR = {lg_age.AOR:.2f}); the model discriminated well (AUC {E["auc"]["corrected"]:.2f} after optimism correction), although with about five events per predictor the odds ratios are exploratory (Table 9, Figure 6). All sensitivity analyses left these results unchanged (r = 0.46–0.48).')
''' + TAB9 + '\n' + TAB10 + r'''
figure(f'{FIG}/fig7_forest_HA.png', 'Adjusted odds ratios for elevated health anxiety (SHAI ≥ 18); orange: p < 0.05.', width=13)

H('3.6 Behaviour and pathways', 2)
''' + BVARS + r'''
P(f'With both scores in the same models (Table 10), behaviour was related more to cyberchondria than to health anxiety: higher CSS went with urgent visits (AOR = {bU.AOR:.2f}), fear-driven delay (AOR = {bT.AOR:.2f}), less ignoring of symptoms (AOR = {bI.AOR:.2f}) and a more strained relationship (ordinal OR = {oR.OR:.2f}). Only one of 40 tests survived FDR correction: participants with higher cyberchondria were less likely to report never telling their physician about their searches, that is, more likely to disclose them (AOR = {bNC.AOR:.2f}, q = {bNC.q_FDR:.3f}). Higher health anxiety pointed towards concealment (AOR = {bNS.AOR:.2f}, q = {bNS.q_FDR:.3f}; exploratory).')
''' + TAB11 + r'''
P(f'In exploratory mediation models (Table 11, Figure 7), excessive searching statistically accounted for part of the link between health anxiety and post-search distress (indirect = {mA_ind.coef:.2f}, 95% CI {ci(mA_ind.CI_low, mA_ind.CI_high)}), and distress for almost all of the link with reassurance-seeking consultations (direct c′ = {mC_dir.coef:.2f}). The reverse ordering was equally significant (indirect = {mD_ind.coef:.2f}), so direction cannot be established. No moderator altered the association after FDR correction, and participants with elevated health anxiety scored higher on all four dimensions (Figure 8).')
''' + TAB12 + r'''
figure(f'{FIG}/fig8_mediation.png', 'Mediation models: (A) excessive searching between health anxiety and post-search distress; (B) post-search distress between health anxiety and reassurance seeking.', width=15.5)
figure(f'{FIG}/fig5_subscales_by_HA.png', 'Cyberchondria dimensions by health-anxiety status (mean ± 95% CI).', width=11)

# ================================================================== 4 DISCUSSION
H('4. Discussion')
H('4.1 Health anxiety and cyberchondria', 2)
P(f'To our knowledge, this is the first study to use the CSS-12 in Baghdad and one of the first to examine AI chatbots alongside search engines before a medical visit. Health anxiety and cyberchondria were moderately and robustly associated (r = {sc["pearson_r"]:.2f}), supporting H1 and H2, although the link was weaker than the meta-analytic estimates of 0.62–0.63 {cite("mcmullan2019","schenkel2021")}. Corrected for the reliability of both scales it would be about {E["disattenuated_r"]:.2f}, although the observed estimate remains {sc["pearson_r"]:.2f}. Low and narrowly spread health anxiety (mean SHAI 12.3), recruitment of confident Internet users and the short CSS-12 may also have weakened it. The association was concentrated in excessiveness and distress, and at item level in fear and catastrophic interpretation rather than bodily vigilance, as the cognitive model predicts {cite("salk1986")}. The 19% with elevated health anxiety is a screening estimate that varied from 7% to 33% across plausible cut-offs, but it suggests that a substantial minority of digitally active adults in Baghdad report elevated health worry, in keeping with pandemic data from Iraq {cite("karim2020")}.')
H('4.2 Do health anxiety and cyberchondria fuel each other?', 2)
P(f'The mediation results fit the reinforcing cycle proposed by the cognitive model and the Dutch longitudinal study {cite("tepoel2016")}: more health anxiety goes with more searching, more searching with more distress, and distress with reassurance seeking. They must not be over-interpreted. Cross-sectional mediation can be seriously biased for longitudinal processes {cite("olaughlin2018")}, a significant indirect effect cannot identify the causal order {cite("rohrer2022")}, the reverse model was equally significant, and the mediators and outcomes are subscales of one instrument {cite("podsakoff2024")}. The data are compatible with a cycle but cannot demonstrate it; H3 is supported statistically, not causally.')
H('4.3 AI chatbots', 2)
P(f'AI use here ({E["ai_profile"]["ticked_ai_pct"]:.0f}–{ai_n/n*100:.1f}%) was far higher than in a 2024 US survey (about one in five) {cite("ayo2024")} or a 2025 survey (21%, against 98% for search engines) {cite("yun2025")}, partly because the sample was young. The higher cyberchondria of AI users vanished under the strict definition and rested on a small, older comparison group, and AI use did not change the strength of the anxiety–cyberchondria link: an absence of evidence, not evidence of no effect. Higher trust in online/AI information went with fewer multiple-doctor consultations, suggesting that trusted AI answers may replace some "doctor shopping", but also offering a route for false reassurance; a non-significant trend towards reassured delay (AOR = 1.33, p = 0.088) echoes regional data in which trust predicted delayed consultation {cite("dahshan2026")}.')
H('4.4 The consultation and medical students', 2)
P(f'Delaying care because of reassurance ({pct(cnt("beh_delay_reassured"))}) may save visits for minor symptoms but risks late diagnosis for serious ones, and it was unrelated to either score, so it is not limited to anxious users. Almost a third never told their doctor about their searches. Higher cyberchondria robustly went with more disclosure, whereas health anxiety tended towards concealment (exploratory), perhaps from fear of being labelled the "worried well"; information discussed openly strengthens the relationship, whereas hidden information undermines it {cite("luo2022")}. H4 is only partly supported. Medical students\' higher health anxiety disappeared after adjustment for age, and their cyberchondria equalled that of others; a Palestinian study using the same SHAI threshold even found elevated health anxiety least common among medical students {cite("fasfoos2026")}. These results agree with Arab-region data from Jeddah, Saudi primary care, Lebanon and 1435 Egyptian medical students, of whom 85.8% showed moderate cyberchondria {cite("elzayat2023","pasayan2025","hallit2023","elzoghby2024")}.')
H('4.5 Strengths and limitations', 2)
P('Strengths include two established, reliable scales, formal Arabic–English invariance testing, separate assessment of AI chatbots, complete data, correction for multiple testing, robust and bootstrap methods, and sensitivity analyses. The main limitations are:', indent=True)
for b in ['**Design:** cross-sectional data cannot establish direction; mediation describes statistical pathways only.',
          f'**Sample:** an online convenience sample, young and with many medical students ({pct(medst)}), so percentages cannot be generalised to Baghdad; residence was not verified by a question.',
          '**Measurement:** Arabic wording without formal back-translation (although the CSS-12 was fully invariant); one SHAI item with reordered options; behaviour, trust and disclosure measured with single, non-validated items; all data self-reported.',
          '**Analysis:** many exploratory tests despite FDR correction; small subgroups (34 AI non-users); about five events per predictor in the logistic model; the AI result depends on how 32 respondents were classified.']:
    bullet(b)

# ================================================================== 5 CONCLUSIONS
H('5. Conclusions and Recommendations')
H('5.1 Conclusions', 2)
for b in [f'AI chatbots, mainly ChatGPT, are a leading source of health information before consulting a doctor among digitally active adults in Baghdad ({E["ai_profile"]["ticked_ai_pct"]:.1f}% ticked; {pct(ai_n)} including those who named one).',
          f'About one in five ({prev["HA_clin"]:.0f}%) had elevated health anxiety on a screening threshold; younger people and reassurance seekers were most affected.',
          f'Health anxiety and cyberchondria are moderately and robustly associated (r = {sc["pearson_r"]:.2f}), compatible with a reinforcing cycle that this design cannot prove.',
          'There is no reliable evidence that AI use adds to cyberchondria beyond health anxiety.',
          'Searching shapes the consultation: about a third delay care when reassured and about a third never disclose their searches; higher cyberchondria goes with more disclosure.']:
    numbered(b)
H('5.2 Recommendations', 2)
for b in ['**Clinicians:** ask every patient, without judgement, what they have searched or asked an AI; treat repeated searching and reassurance seeking as possible signs of health anxiety; teach digital and AI health literacy in medical school.',
          '**Ministry of Health:** the Ministry may consider Arabic digital and AI health-literacy campaigns that warn about false reassurance, and reliable Arabic triage sources.',
          '**AI developers:** developers may consider anxiety-aware health answers that avoid escalating rare diagnoses and encourage appropriate consultation.',
          f'**Research:** longitudinal studies, probability samples and formally adapted Arabic scales; intervention trials are needed, as ClinicalTrials.gov lists only nine cyberchondria studies and none in Iraq {cite("ctgov2026")}.']:
    bullet(b)
'''

code = HEAD + '\n' + MAIN + '\n' + REFS_PART + '\n' + TAIL
assert "f'{OUT}/toc_entries.json'" in code
code = code.replace("f'{OUT}/toc_entries.json'", "f'{OUT}/toc_entries_short.json'")
exec(compile(code, '04s_build_short (assembled)', 'exec'), {'__name__': '__main__'})
