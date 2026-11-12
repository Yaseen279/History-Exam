"""Three individual, comprehensive defence guides (one per presenting student).
Each guide stands alone: shared core knowledge, a section-by-section walkthrough of the student's own chapter,
their key sources, a slide-by-slide script (taken from the presentation's speaker notes), a question bank with
model answers, editing instructions, a 14-day plan, a self-test with answers and a day-before checklist.
Usage: python3 12_student_guides.py <numbers.json> <thesis.docx> <deck.pptx> <out dir>"""
import sys, json, re, html, os
from docx import Document
from pptx import Presentation

NUMS, DOCX, PPTX, OUT = sys.argv[1:5]
SHORT = os.environ.get('THESIS') == 'short'
N = json.load(open(NUMS)); FIG = N['figdir']
e = html.escape

# ---------------------------------------------------------------- reference numbers straight from the thesis
_ps = [p.text for p in Document(DOCX).paragraphs]
_i = _ps.index('6. References')
REFS = {int(m.group(1)): m.group(2) for p in _ps[_i + 1:] for m in [re.match(r'^(\d+)\.\t(.*)', p)] if m}
def R(start):
    hits = [k for k, v in REFS.items() if v.startswith(start)]
    if SHORT and len(hits) != 1: return 0          # reference not cited in the short thesis
    assert len(hits) == 1, (start, hits)
    return hits[0]
def ref(start): return f'[{R(start)}]'

# ---------------------------------------------------------------- slides and speaker notes from the deck
SLIDES = []
for i, s in enumerate(Presentation(PPTX).slides, 1):
    texts = [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    title = next((t for t in texts if len(t) < 60 and '\n' not in t), texts[0] if texts else '')
    notes = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ''
    notes = re.sub(r'^\[[^\]]+\]\s*', '', notes)
    if SHORT:   # the deck already uses short numbers: non-breaking space keeps remap() from renumbering them again
        notes = re.sub(r'\b(Tables?|Figures?) (\d)', '\\1\u00a0\\2', notes); title = re.sub(r'\b(Tables?|Figures?) (\d)', '\\1\u00a0\\2', title)
    SLIDES.append((i, title, notes))

CSS = """
@page { size: A4; margin: 15mm 14mm 15mm 14mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, Carlito, Arial, sans-serif; font-size: 10.5pt; color: #222; line-height: 1.42; margin: 0; }
h1 { font-family: Cambria, Caladea, Georgia, serif; color: #1E5B4F; font-size: 26pt; margin: 0 0 4px; }
h2 { font-family: Cambria, Caladea, Georgia, serif; color: #1E5B4F; font-size: 16pt; margin: 16px 0 6px; padding-bottom: 3px; border-bottom: 2px solid #1E5B4F; page-break-after: avoid; }
h3 { color: #B45F06; font-size: 12pt; margin: 12px 0 4px; page-break-after: avoid; }
h4 { color: #1E5B4F; font-size: 11pt; margin: 9px 0 3px; page-break-after: avoid; }
p { margin: 3px 0 6px; } ul, ol { margin: 3px 0 7px; padding-left: 20px; } li { margin: 2px 0; }
.sub { color: #555; font-size: 11.5pt; margin-bottom: 10px; }
.box { border: 1px solid #c9d3d1; border-left: 5px solid #1E5B4F; background: #F4F8F7; padding: 7px 10px; margin: 7px 0; page-break-inside: avoid; }
.warn { border-left-color: #B45F06; background: #FFF7ED; } .red { border-left-color: #7F1D3A; background: #FBF1F4; }
table { border-collapse: collapse; width: 100%; margin: 5px 0 9px; font-size: 9.6pt; }
tr { page-break-inside: avoid; }
th { background: #DCE6E4; text-align: left; } th, td { border: 1px solid #c8cfcd; padding: 3px 6px; vertical-align: top; }
.page { page-break-before: always; }
.q { font-weight: bold; color: #1E5B4F; margin-top: 7px; } .a { margin: 0 0 4px 12px; }
.tip { margin: 0 0 6px 12px; color: #7F1D3A; font-size: 9.8pt; }
.num { font-weight: bold; color: #B45F06; }
.small { font-size: 9.2pt; color: #555; }
.slide { border: 1px solid #c9d3d1; border-radius: 6px; padding: 6px 10px; margin: 7px 0; page-break-inside: avoid; }
.slide .hd { font-weight: bold; color: #fff; background: #1E5B4F; margin: -6px -10px 5px; padding: 3px 10px; border-radius: 6px 6px 0 0; }
.script { font-style: italic; }
img.fig { display: block; max-width: 100%; max-height: 330px; margin: 6px auto; border: 1px solid #ddd; }
.tag { display: inline-block; padding: 1px 9px; border-radius: 9px; font-weight: bold; color: #fff; }
.s1 { background: #1E5B4F; } .s2 { background: #0B5394; } .s3 { background: #7F1D3A; }
.cols { display: flex; gap: 12px; } .cols > div { flex: 1; }
"""

def ul(items): return '<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
def ol(items): return '<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'
def table(head, rows, widths=None):
    h = ''.join(f'<th{" style=\"width:" + widths[i] + "\"" if widths else ""}>{c}</th>' for i, c in enumerate(head))
    return f'<table><tr>{h}</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table>'
def qa(items):
    out = ''
    for it in items:
        q, a = it[0], it[1]
        out += f'<p class="q">Q: {e(q)}</p><p class="a">{a}</p>'
        if len(it) > 2: out += f'<p class="tip">Watch out: {it[2]}</p>'
    return out
def img(file, cap):
    return f'<img class="fig" src="file://{FIG}/{file}"><p class="small" style="text-align:center">{cap}</p>'

# ================================================================ SHARED CORE (in every guide)
def shared_core():
    s = '<h2 class="page">Part 1 · The whole study (everyone must know this)</h2>'
    s += '''<div class="box warn"><b>The committee can ask any of you about any part.</b> You split the presentation, not the knowledge.
Learn this part so well that you can explain the whole study without slides.</div>'''
    s += '<h3>The study in two minutes (practise saying this out loud)</h3>'
    s += f'''<p class="script">“Many people now look up their symptoms online before seeing a doctor, and more and more of them ask AI chatbots like ChatGPT.
For some people this searching makes them more worried, not less. That is called cyberchondria, and it is closely linked to health anxiety.
No one had studied this in Baghdad, and AI chatbots had hardly been studied next to search engines.
We ran an online survey of {N["n"]} adults in Baghdad between {N["d0"]} and {N["d1"]}, using two established scales: the SHAI-14 for health anxiety and the CSS-12 for cyberchondria.
We found that AI chatbots are now the main source of health information: {N["ai_tick"]} ticked them, more than search engines ({N["se"]}).
About one in five ({N["hac"]}) had elevated health anxiety. Health anxiety and cyberchondria were moderately linked, r = {N["r"]}, and this held after adjusting for everything else.
The link ran mainly through excessive searching and post-search distress, which fits a vicious cycle, although one survey cannot prove direction.
We found no reliable evidence that AI itself adds to cyberchondria beyond health anxiety.
And searching shapes the consultation: about a third delay care because they feel reassured, and about a third never tell their doctor what they searched.
So our main message for clinicians is simple: ask patients, without judgement, what they searched or asked an AI.”</p>'''
    core = [
        ('Design', f'Analytical cross-sectional online survey; STROBE and CHERRIES checklists'),
        ('Who and when', f'<span class="num">{N["n"]}</span> adults, Baghdad, {N["d0"]} – {N["d1"]}; convenience + snowball sampling'),
        ('Sample size', f'<span class="num">{N["nreq"]}</span> needed for r = 0.20 (α 0.05, 80% power); margin of error ±{N["moe"]}%'),
        ('Sample profile', f'{N["age20"]} aged 20–29 · {N["fem"]} female · <span class="num">{N["med"]}</span> medical students · {N["hb"]} health background · {N["chron"]} chronic condition · {N["ar"]} answered in Arabic'),
        ('Tools used', f'AI chatbots <span class="num">{N["ai_tick"]}</span> ticked ({N["ai"]} incl. named) · search engines {N["se"]} · medical platforms {N["mp"]} · social media {N["sm"]} · ChatGPT {N["gpt"]} · AI without any search engine {N["ai_only"]}'),
        ('Motives', f'convenience {N["conv"]} · “do I need a doctor?” {N["tri"]} · instant reassurance {N["reas"]}'),
        ('Health anxiety', f'SHAI mean {N["shai_m"]} ± {N["shai_sd"]} (0–42) · <span class="num">{N["hac"]}</span> elevated (≥ 18; 95% CI {N["hac_ci"]}) · {N["ge29"]} at ≥ 29'),
        ('Cyberchondria', f'CSS mean {N["css_m"]} ± {N["css_sd"]} (12–60) · excessiveness highest, compulsion lowest'),
        ('Reliability', f'α {N["aS"]} (SHAI), {N["aC"]} (CSS); ω {N["oS"]}, {N["oC"]} · CSS-12 4-factor CFA: CFI {N["cfaC"]}, RMSEA {N["cfaR"]}, SRMR {N["srmr"]}'),
        ('Arabic vs English', 'CSS-12 fully (scalar) invariant; SHAI-14 metric invariant; no item DIF after FDR'),
        ('Main result', f'<span class="num">r = {N["r"]}</span> (95% CI {N["rci"]}); explains {N["r2"]} of the variance · partial r = {N["pr"]}'),
        ('By facet', f'excessiveness {N["rE"]} · distress {N["rD"]} · compulsion {N["rC"]} · reassurance {N["rR"]}'),
        ('Regression', f'R² {N["R2a"]} (demographics) → {N["R2b"]} (+ digital use) → {N["R2c"]} (+ health anxiety, ΔR² {N["dR2"]}); β = {N["beta"]}'),
        ('Who is anxious', f'AOR <span class="num">{N["orCSS"]}</span> per SD of cyberchondria · {N["orMot"]} reassurance motive · {N["orAge"]} per older age group · AUC {N["auc"]} → {N["aucc"]}'),
        ('Pathways', f'via excessive searching {N["mA"]} (CI {N["mAci"]}) · via distress {N["mC"]} (direct → {N["mCd"]}) · reverse {N["mD"]}'),
        ('Behaviour', f'delay care when reassured <span class="num">{N["dr"]}</span> · ignore symptom {N["ign"]} · several doctors {N["mdoc"]} · urgent care {N["urg"]} · self-medication {N["smed"]}'),
        ('Doctor relationship', f'never tell the doctor <span class="num">{N["never"]}</span> · always tell {N["always"]} · trust strained {N["relneg"]} · higher cyberchondria → more disclosure (OR {N["nsC"]}, q {N["nsCq"]})'),
        ('AI effect', f'+{N["Bai"]} CSS points (inclusive) but +{N["Balt"]}, p = {N["palt"]} (strict) → no reliable independent effect · {N["inc"]} named-not-ticked · 34 non-users'),
        ('Robustness', 'every sensitivity analysis left the main result unchanged (Table 13)'),
    ]
    s += '<h3>Core facts (memorise; examiners test these)</h3>' + table(['Topic', 'Fact'], [[f'<b>{a}</b>', b] for a, b in core], ['20%', '80%'])
    s += '<h3>Terms you must be able to explain in one sentence</h3>' + table(['Term', 'Plain explanation'], [
        ['Health anxiety', 'Persistent worry about having or developing a serious illness, kept going by misreading normal body sensations and by reassurance seeking.'],
        ['Illness anxiety disorder', 'The DSM-5 diagnosis at the severe end of health anxiety. We did <b>not</b> diagnose it; we measured symptoms.'],
        ['Cyberchondria', 'Excessive or repeated online health searching that increases rather than relieves distress.'],
        ['SHAI-14', '14 items, each scored 0–3 (total 0–42); higher = more health anxiety. ≥ 18 = elevated (screening threshold).'],
        ['CSS-12', '12 items scored 1–5 (total 12–60) with four 3-item facets: excessiveness, compulsion, distress, reassurance seeking.'],
        ['Cross-sectional', 'Everything measured once, at one time point: shows associations, not cause and effect.'],
        ['Convenience / snowball sampling', 'People who were easy to reach, who then shared the link with others. Quick, but not representative.'],
        ['Mean ± SD', 'The average score and how spread out the scores are.'],
        ['Median (IQR)', 'The middle score and the range of the middle half; used when data are skewed.'],
        ['p-value', 'How surprising the result would be if there were truly no effect; p < 0.05 is called significant.'],
        ['95% CI', 'The range in which the true value probably lies; narrower = more precise.'],
        ['Correlation r', 'How closely two scores move together (0 = none, 1 = perfect). 0.47 is moderate.'],
        ['Partial correlation', 'The same link after removing the effect of other variables.'],
        ['Mann–Whitney / Kruskal–Wallis', 'Non-parametric tests comparing two / three or more groups, used because scores were not normally distributed.'],
        ['χ² test', 'Tests whether two categorical variables are related (e.g., social-media use and elevated health anxiety).'],
        ['FDR (q-value)', 'Correction for running many tests; a result is “robust” if q < 0.05, otherwise exploratory.'],
        ['Linear regression, B and β', 'Predicts a score from several factors at once. B = change in CSS points per unit; β = the same on a standardised scale (to compare factors).'],
        ['R² and ΔR²', 'Share of variation explained by the model; ΔR² = extra share explained by adding a block of variables.'],
        ['Logistic regression, AOR', 'Predicts a yes/no outcome. Adjusted odds ratio: how many times the odds change, holding other factors constant.'],
        ['AUC', 'How well a model separates two groups (0.5 = chance, 1 = perfect).'],
        ['Mediation', 'Splitting a link into a part that runs through a third variable (indirect) and the rest (direct). Statistical, not causal.'],
        ['Moderation', 'Whether a third variable changes the strength of a link (e.g., does AI use make the link stronger? No).'],
        ['Cronbach α / McDonald ω', 'Internal consistency: do the items of a scale hang together? ≥ 0.7 is acceptable, ≥ 0.8 good.'],
        ['CFA (CFI, RMSEA, SRMR)', 'Checks the items group into the intended factors. Good: CFI ≈ 0.95+, RMSEA ≤ 0.08, SRMR ≤ 0.08.'],
        ['Measurement invariance', 'Checks the scale measures the same thing in two groups (here Arabic vs English) before comparing them.'],
        ['Sensitivity analysis', 'Re-running the main analysis in a different way to see if the result holds.'],
    ], ['24%', '76%'])
    s += '''<div class="box red"><b>Never say</b> (overclaims the committee will catch):
<ul><li>“Health anxiety <i>causes</i> cyberchondria” → say “is associated with”, “is compatible with a cycle”.</li>
<li>“19% <i>have</i> health anxiety disorder” → “19% scored in the elevated range on a screening tool”.</li>
<li>“AI makes people anxious” → “we found no reliable independent effect of AI use”.</li>
<li>“Our results represent Baghdad” → “a young, online, convenience sample; associations were consistent across subgroups”.</li>
<li>“The Arabic version is validated” → “we tested it: equal reliability and formal invariance, but no formal back-translation”.</li></ul></div>'''
    s += img('fig0a_framework.png', 'Figure 1 of the thesis: the conceptual framework. Learn to explain every arrow.')
    return s

# ================================================================ PER-STUDENT CONTENT
STUDENTS = {}

# ---------------------------------------------------------------- STUDENT 1
STUDENTS[1] = dict(
    tag='s1', title='Introduction & Methods', slides=range(1, 13), minutes='≈ 5 minutes',
    chapters='Chapter 1 Introduction (1.1–1.8), Chapter 2 Method (2.1–2.7), Figures 1–2, Acknowledgment',
    opener='You open the defence. Your first minute sets the committee\'s impression of the whole team: slow, clear, confident.',
    handover='“That was our methodology. Now my colleague will present what we found.”',
    walkthrough=[
        ('1.1 Background', 'Why the topic matters.',
         ['Searching before seeing a doctor is now ordinary; it helps, but for some people it amplifies worry: <b>cyberchondria</b> ' + ref('White RW') + ref('Starcevic V, Berle D. Cyberchondria: towards') + '.',
          f'Iraq is highly connected: about <b>four in five</b> Iraqis online by 2025 {ref("Kemp S")}, yet nothing had been studied in Baghdad.'],
         'Why Baghdad? Why now? Your answer: high Internet use, rising AI use, no local data.'),
        ('1.2 Health anxiety', 'What health anxiety is and why it matters.',
         [f'A continuum from normal worry to illness anxiety disorder / somatic symptom disorder (DSM-5) {ref("American Psychiatric")}.',
          f'Cognitive-behavioural model {ref("Salkovskis PM, Warwick")}: sensations misread → anxiety → checking and reassurance → short relief → worry returns.',
          f'Common and costly: ≈ 6% lifetime, up to 20% in hospital outpatients, unnecessary contacts {ref("Tyrer P. Recent")}{ref("Tyrer P. Why")}; rising over three decades {ref("Kosic A")}.',
          f'Iraq: about half of 1591 online respondents reported health anxiety during COVID-19 {ref("Karim SK")}; home quarantine raised it in 1578 adults {ref("Taha PH")}.'],
         'Be able to draw the cognitive cycle on a whiteboard.'),
        ('1.3 Cyberchondria', 'Definition and measurement.',
         [f'White & Horvitz {ref("White RW")}: benign searches escalate to rare, serious diagnoses. Starcevic & Berle {ref("Starcevic V, Berle D. Cyberchondria: towards")}: searching that <i>increases</i> distress.',
          f'Not pathological in itself; becomes cyberchondria when excessive, compulsive, distressing {ref("Starcevic V, Berle D, Arnáez")}; possible transdiagnostic compulsive syndrome {ref("Vismara M")}.',
          f'CSS-33 had five factors incl. mistrust of doctors {ref("McElroy E, Shevlin")}; CSS-12 keeps four {ref("McElroy E, Kearney")}; Arabic CSS-12 validated in Lebanon {ref("Hallit S")}.'],
         'Know why we used CSS-12 (short, four facets, Arabic version exists) and that it drops “mistrust”.'),
        ('1.4 Health anxiety and cyberchondria', 'Why the two are studied together.',
         [f'Related but distinct; cyberchondria adds impairment and healthcare use {ref("Mathes BM")}. Searching raises anxiety in an experiment {ref("Jungmann SM, Brand")}.',
          f'Meta-analyses: r = 0.34 with general online searching but <b>0.62</b> with cyberchondria {ref("McMullan RD")}; <b>0.63</b>, facets 0.24–0.66 {ref("Schenkel SK")}.',
          f'Intolerance of uncertainty linked to cyberchondria (r = 0.55) {ref("Jungmann SM, Dessauer")}.',
          f'Longitudinal: Dutch 4-wave panel of 5322 adults, reciprocal link {ref("te Poel F")}; pregnancy study, health anxiety as risk factor {ref("Šoštarić M")}.',
          f'COVID-19 studies in Croatia and Turkey {ref("Jokic-Begic N")}{ref("Kurcer MA")}; scoping review prevalence 30.7–55.6% {ref("Miezah D")}.'],
         'The meta-analytic 0.62 will come back in the Discussion: our 0.47 is lower. Know that Student 3 explains why.'),
        ('1.5 From search engines to AI chatbots', 'What is new about AI.',
         [f'LLM chatbots are fluent, personal, repeatable; answers can seem more empathetic than doctors\' {ref("Thirunavukarasu AJ")}{ref("Ayers JW")}.',
          f'US survey: ≈ 1 in 5 used ChatGPT for health; ≈ a third changed medication or asked for referrals {ref("Ayo-Ajibola O")}.',
          f'Health anxiety predicts symptom-checker use {ref("Wetzel AJ")}; Czech sample: link via trust in AI {ref("Svestkova A")}; Turkish dermatology: 61% used AI before the visit {ref("Dığış M")}.'],
         'Open question you can state: does AI relieve worry (calm answers) or feed it (endless reassurance)?'),
        ('1.6 Searching and the doctor–patient relationship', 'Why behaviour matters clinically.',
         [f'Discussing searches can help the relationship; hiding them strains it {ref("Wang J")}{ref("Luo A")}.',
          f'Arab region: Jeddah {ref("El-Zayat A")}, Saudi primary care {ref("Pasay-An E")}, 13 MENA countries: trust in online information predicted delayed consultation {ref("Dahshan A")}.'],
         ''),
        ('1.7 Rationale', 'Three gaps.',
         ['First CSS-12 data from Baghdad.', 'AI chatbots studied separately from search engines.', 'Psychology linked to real pre-consultation behaviour.'],
         'Practise saying the three gaps in one breath.'),
        ('1.8 Aim, objectives, hypotheses, Figure 1', 'What the study set out to do.',
         ['Aim: relationship between health anxiety and cyberchondria and their correlates among adults in Baghdad, with attention to AI chatbots and pre-consultation behaviour.',
          'H1: health anxiety ↔ cyberchondria (mainly distress, excessiveness). H2: independent of other factors. H3: excessive searching mediates HA → distress. H4: cyberchondria ↔ care-seeking and strained relationship.',
          'H1–H2 primary; H3–H4 secondary; AI comparisons, item-level, moderation and sensitivity analyses exploratory.',
          'Figure 1 shows these on the cycle.'],
         'Know which hypotheses were supported: H1 yes, H2 yes, H3 statistically (not causally), H4 partially.'),
        ('2.1 Design and setting', '', [f'Analytical cross-sectional; STROBE {ref("von Elm E")} and CHERRIES {ref("Eysenbach G")}; online, Baghdad, {N["d0"]} – {N["d1"]}.'], ''),
        ('2.2 Participants and sampling', '', ['Convenience + snowball via Baghdad-based social-media and messaging groups.', 'Inclusion: ≥ 18 years, reads Arabic or English, informed consent.', 'All submissions retained; no duplicates; response rate cannot be calculated (snowball).', 'Three responses had been annotated by the team: kept, and excluded in a sensitivity analysis.'],
         'Residence in Baghdad was not asked directly: say so honestly.'),
        ('2.3 Sample size', '', [f'Fisher\'s z: r = 0.20, α 0.05, 80% power → {N["nreq"]} (85 for r = 0.30) {ref("Serdar CC")}. 300 collected; ±{N["moe"]}% margin for percentages (vs ±5% for 385).', 'Logistic model for elevated health anxiety: 57 events / 11 predictors ≈ 5 per variable (limitation).'], ''),
        ('2.4 Instrument', '', [f'Bilingual Google Form, five parts (Figure 2). SHAI-14 {ref("Salkovskis PM, Rimes")}, validated widely {ref("Arnáez S")}{ref("Österman S")}{ref("Poshtan MM")}, Arabic version in Saudi Arabia {ref("Alshayea AK")}.',
          f'CSS-12 {ref("McElroy E, Kearney")}: 1–5 scale, four subscales.', f'Arabic wording by the team, not formal cross-cultural adaptation {ref("Cruchinho P")}; published Arabic versions {ref("Hallit S")}{ref("Alshaibani M")}{ref("Alshayea AK")} not used.',
          'SHAI item 2 options displayed in a different order; scored by meaning; dropping it changed nothing.'],
         'This is the most attacked section. Prepare the Arabic-version answer (Part 5).'),
        ('2.5 Variables', '', ['Elevated health anxiety: SHAI ≥ 18 (vs healthy controls, Swedish study) ' + ref('Österman S') + '; also 15, 22, 29.', 'High cyberchondria: CSS > 33 (upper tertile; no validated cut-off).',
          f'AI user: ticked AI or named a chatbot ({N["inc"]} named without ticking); analyses repeated with the strict definition.', 'Health background = medical, other health-science students and healthcare workers.'], ''),
        ('2.6 Statistical analysis', 'You name the methods; Student 2 explains them in depth.',
         ['Python 3 (pandas, SciPy, statsmodels, pingouin, factor_analyzer, semopy), fully scripted; SPSS file provided.',
          f'Psychometrics: α, ω {ref("Hayes AF, Coutts")}, CFA by ML (criteria {ref("McNeish D")}), invariance by multi-group CFA {ref("Leitgöb H")} and DIF by ordinal logistic regression {ref("Ćosić Pilepić A")}.',
          f'Correlations; Mann–Whitney/Kruskal–Wallis; χ²; FDR {ref("Benjamini Y")}; hierarchical robust regression; logistic and ordinal; bootstrap mediation {ref("Hayes AF. Introduction")}; moderation; sensitivity analyses.', 'Figure 2 summarises the study flow.'],
         ''),
        ('2.7 Ethics', '', ['Voluntary, anonymous, e-consent with age confirmation before any question; no names or contacts.', '[Ethics approval: committee, number, date: fill in before the defence.]'], 'You must know the approval details by heart.'),
    ],
    sources_chap=['intro', 'method'],
    qa_own=[
        ('Why did you choose this topic?', 'Give your <b>real</b> reason (e.g., patients or relatives using ChatGPT before seeing a doctor). Then: no data from Iraq, and AI chatbots had not been studied next to search engines.'),
        ('What is the difference between health anxiety and cyberchondria?', 'Health anxiety is the underlying worry about illness; cyberchondria is a behaviour pattern, excessive searching that makes the worry worse. They overlap strongly but are distinct.'),
        ('Why is your study design cross-sectional?', 'Feasible for a student project and appropriate for associations. We say clearly it cannot show direction, and we recommend longitudinal studies.'),
        ('Your sample is not representative. Why convenience sampling?', 'There is no sampling frame for online adults in Baghdad. We describe the sample honestly, do not generalise percentages, and show associations were consistent across subgroups.'),
        ('Explain your sample size calculation.', f'Our primary outcome is a correlation. Fisher\'s z with α 0.05 and 80% power needs {N["nreq"]} participants to detect r = 0.20. We had 300; meta-analytic r is ≈ 0.62, so the calculation is conservative.'),
        ('Why not use Cochran\'s formula (385)?', f'That is for estimating a proportion with ±5% precision. Our primary aim was a correlation. For percentages, 300 gives ±{N["moe"]}%, close to ±5%.'),
        ('Why SHAI-14 and CSS-12?', 'Both are widely used, short, reliable and have Arabic versions in the literature. CSS-12 has four facets, which let us test the cycle.'),
        ('Why SHAI ≥ 18?', f'It best separated people with health anxiety from healthy controls in the Swedish diagnostic study {ref("Österman S")}. It is a screening threshold, so we say “elevated”, and Table 4 shows other cut-offs.', 'Never call it a diagnosis.'),
        ('Did you translate the questionnaire properly?', 'No formal forward–backward translation, which is a limitation. But we tested equivalence: equal reliability, equal means, full scalar invariance of the CSS-12, metric invariance of the SHAI-14 and no item DIF.'),
        ('Why didn\'t you use the published Arabic versions?', 'We were not aware of them when the form was built [or give your real reason]. We cite them and recommend them for future work.', 'Do not invent a reason; if unsure, say it was an oversight in planning.'),
        ('How do you know participants lived in Baghdad?', 'Through Baghdad-based distribution channels; there was no residence question. This is listed as a limitation.'),
        ('Could one person answer twice?', '[Fill in: did Google Forms limit one response per account?] We found no duplicate response patterns.'),
        ('Why is it called “analytical” cross-sectional?', 'Because we tested associations and hypotheses, not just described prevalence.'),
        ('What are STROBE and CHERRIES?', 'Reporting checklists: STROBE for observational studies, CHERRIES for online surveys. They make sure we report everything a reader needs.'),
        ('What ethical issues did you consider?', 'Voluntary participation, anonymity, informed consent before any question, right to withdraw, secure data. [Approval number.]'),
        ('What are your hypotheses and were they supported?', 'H1 and H2 supported; H3 supported statistically but not causally; H4 only partially (only disclosure survived FDR).'),
        ('Why include AI chatbots?', f'Because they are new and now dominant: {N["ai_tick"]} ticked them. Earlier studies treated “the Internet” as one thing.'),
        ('What does Figure 1 show?', 'The conceptual framework: health anxiety, the four facets of cyberchondria on a cycle, the tools that feed searching, covariates, and behaviour as the outcome, with H1–H4 marked.'),
    ],
    qa_hard=[
        ('“This is just a student survey; why should we trust it?”', 'Calmly: established scales, good reliability, pre-specified hypotheses, correction for multiple testing, robust methods and sensitivity analyses; and we state our limitations openly.'),
        ('“You found what everyone already knows.”', 'The link itself is known; what is new is Baghdad data, AI chatbots studied separately, and the link to concrete behaviour before the consultation.'),
        ('“Why should a doctor care about this?”', 'Because a third of patients delay care when reassured online and a third hide their searches: both affect diagnosis and trust.'),
    ],
    edit=[
        'Chapter 1 is the most “human” place to write in your own voice: explain each idea as you would to a classmate, keeping every reference number with its claim.',
        'Add your genuine reason for choosing the topic (one or two sentences in 1.1 or 1.7) only if it is true.',
        'In Chapter 2, change wording but never the facts: dates, criteria, sample size numbers, cut-offs, test names, software.',
        'Write the Acknowledgment yourselves: supervisor, participants, anyone who shared the link, family.',
        'Fill in 2.7 (ethics approval) and the Google Forms question in 2.2.',
        'Keep Figures 1 and 2 and their captions; do not type caption numbers by hand.',
    ],
    self_test=[
        ('How many participants, and when was data collected?', f'{N["n"]}; {N["d0"]} – {N["d1"]}'),
        ('Required sample size and for what effect?', f'{N["nreq"]} for r = 0.20 (α 0.05, 80% power)'),
        ('Range of the SHAI-14 and CSS-12?', '0–42 and 12–60'),
        ('The four CSS-12 facets?', 'Excessiveness, compulsion, distress, reassurance seeking'),
        ('Cut-off for elevated health anxiety and its source?', 'SHAI ≥ 18; Swedish diagnostic-accuracy study (Österman 2022)'),
        ('Meta-analytic correlation between health anxiety and cyberchondria?', '≈ 0.62 (McMullan 2019) and 0.63 (Schenkel 2021)'),
        ('Who coined “cyberchondria” in search-log research?', 'White and Horvitz (2009)'),
        ('Inclusion criteria?', '≥ 18 years, reads Arabic or English, informed consent'),
        ('Sampling method?', 'Convenience + snowball through Baghdad-based online groups'),
        ('Which checklists guided reporting?', 'STROBE and CHERRIES'),
        ('Name the four hypotheses briefly.', 'H1 HA ↔ CSS; H2 independent; H3 mediation via excessive searching; H4 behaviour/relationship'),
        ('Percentage of Iraqis online?', 'About four in five (≈ 80%) by 2025'),
        ('How was AI use defined, and why two definitions?', f'Ticked AI or named a chatbot; {N["inc"]} named without ticking, so results were repeated with the strict definition'),
        ('Software used?', 'Python 3 (fully scripted); SPSS file also provided'),
        ('What does the cognitive model say keeps health anxiety going?', 'Misinterpretation of sensations plus safety behaviours (checking, reassurance) that give short relief'),
    ],
)

# ---------------------------------------------------------------- STUDENT 2
STUDENTS[2] = dict(
    tag='s2', title='Results', slides=range(13, 24), minutes='≈ 6 minutes',
    chapters='Chapter 3 Results (3.1–3.10), Tables 1–13, Figures 3–11, Appendix A; and Section 2.6 (you are the team\'s statistics person)',
    opener='You carry the heaviest numbers. Your job is to make them simple: one message per slide, then the “In summary” line.',
    handover='“Those are our results. My colleague will now discuss what they mean.”',
    walkthrough=[
        ('3.1 Participants (Table 1)', 'Who answered.', [f'{N["n"]} adults, no missing data; {N["age20"]} aged 20–29; {N["fem"]} female; most current students; medical students {N["med"]}; health background {N["hb"]}; chronic condition {N["chron"]} (migraine, hypertension, asthma…); Arabic {N["ar"]}.'], 'Message: a young, educated, digitally active sample.'),
        ('3.2 Online health-information seeking (Table 2, Figure 3)', 'How people search.', [f'AI ticked {N["ai_tick"]} ({N["ai"]} incl. named) vs search engines {N["se"]}; AI without any search engine {N["ai_only"]}; ChatGPT {N["gpt"]}.', 'AI use 96% at 18–19 y, 72% at ≥ 40 y; the 34 non-users are older.', f'Motives: convenience {N["conv"]}, “do I need a doctor?” {N["tri"]}, reassurance {N["reas"]}; trust mostly moderate.'], 'Message: for this sample, the first “doctor” is often an AI.'),
        ('3.3 Behaviour and the doctor relationship (Figure 4)', '', [f'Delay/skip care when reassured {N["dr"]}; ignore {N["ign"]}; several doctors {N["mdoc"]}; urgent care {N["urg"]}.', f'Always tell the doctor {N["always"]}; never (fear of judgement) {N["never"]}; relationship complicated or trust reduced {N["relneg"]}.'], 'The “never” option combined frequency and a reason: say “never tell, citing fear of judgement”.'),
        ('3.4 Levels and psychometrics (Tables 3, 4, 5)', '', [f'SHAI {N["shai_m"]} ± {N["shai_sd"]}; elevated {N["hac"]} (CI {N["hac_ci"]}); Table 4: 32.7% at ≥ 15, 19.0% at ≥ 18, 7.3% at ≥ 22, 0.7% at ≥ 29.', f'CSS {N["css_m"]} ± {N["css_sd"]}; excessiveness 9.66 (highest), compulsion 5.00 (lowest).',
          f'Reliability α {N["aS"]} / {N["aC"]}; ω {N["oS"]} / {N["oC"]}. CSS-12 four-factor CFA (ML) CFI {N["cfaC"]}, RMSEA {N["cfaR"]}, SRMR {N["srmr"]}; SHAI one-factor poor (CFI 0.83): not strictly unidimensional.',
          'Table 5: CSS-12 configural → metric (Δχ² 5.52, p 0.70, ΔCFI +0.002) → scalar (Δχ² 8.41, p 0.40, ΔCFI −0.001): fully invariant. Both baselines are imperfect (configural CFI 0.937 CSS, 0.808 SHAI), so the SHAI result is hard to interpret. SHAI-14 metric supported (p 0.73), scalar not (p 0.007, ΔCFI −0.018). No item DIF after FDR.'],
         'Explain why prevalence depends on the cut-off and why that is not a weakness: it is honest reporting.'),
        ('3.5 Main association (Table 6, Figures 5, 6)', 'The central result.', [f'r = {N["r"]} (95% CI {N["rci"]}), ρ = {N["rho"]}, explains {N["r2"]}; partial r = {N["pr"]}.', f'Facets: excessiveness {N["rE"]}, distress {N["rD"]} (stronger, Williams\' t p < 0.001) vs compulsion {N["rC"]}, reassurance {N["rR"]}.',
          f'Item level: fear of serious illness and interpretation of sensations matter, mere awareness does not; {N["ibF"]}/168 pairs survive FDR ({N["ibH"]} Holm); strongest ρ 0.43 (Figure 11, Appendix A).'],
         'H1 and H2 are answered here.'),
        ('3.6 Bivariate factors (Tables 7, 8, Figure 7)', '162 tests.', ['Health anxiety higher with chronic condition (p 0.004, q 0.028) and reassurance motive; age/education/occupation borderline (exploratory); gender no difference.', 'AI users higher CSS (inclusive), mainly excessiveness and reassurance; highest in AI + search engine users; chatbot brand no difference.', 'χ²: elevated HA → 52.6% vs 23.0% high cyberchondria (OR ≈ 3.7).'],
         'Remember q-values: “survives correction” vs “exploratory”.'),
        ('3.7 Multivariable models (Tables 9, 10, Figure 8)', '', [f'Hierarchical regression: R² {N["R2a"]} → {N["R2b"]} → {N["R2c"]}; health anxiety adds {N["dR2"]} (f² medium); B = {N["B"]}, β = {N["beta"]}.', f'AI: +{N["Bai"]} (CI {N["Baici"]}) inclusive vs +{N["Balt"]}, p {N["palt"]} strict; the {N["inc"]} reclassified had the highest CSS ({N["inc_css"]} vs {N["non_css"]} in non-users).',
          'Reverse model: CSS strongest predictor of SHAI; chronic disease B +1.7 (p 0.029); medical students no longer differ after adjustment.', f'Logistic (57 events): AOR {N["orCSS"]} cyberchondria per SD, {N["orMot"]} reassurance motive, {N["orAge"]} age; AUC {N["auc"]} → {N["aucc"]}; ≈ 5 events per variable → exploratory.'],
         'You will be asked to explain AOR, AUC and why it was corrected.'),
        ('3.8 Behaviour models (Table 11)', '', [f'Cyberchondria (not health anxiety) goes with urgent visits (AOR {N["urC"]}), less ignoring ({N["igC"]}), strained relationship (ordinal OR 1.34).', f'Only robust behavioural result: higher CSS → lower odds of never disclosing (AOR {N["nsC"]}, q {N["nsCq"]}). Health anxiety → concealment AOR {N["nsS"]}, q {N["nsSq"]} (exploratory).', f'Trust → fewer multiple-doctor visits (AOR {N["mdT"]}).'], 'H4 only partially supported.'),
        ('3.9 Pathways (Table 12, Figures 9, 10)', '', [f'HA → excessive searching → distress: indirect {N["mA"]} (CI {N["mAci"]}), direct {N["mAd"]}.', f'HA → distress → reassurance seeking: indirect {N["mC"]} (CI {N["mCci"]}), direct {N["mCd"]} (ns).', f'Reverse path also significant ({N["mD"]}); serial path {N["ser"]}. No moderator significant after FDR; age trend p 0.07.'], 'Always end with: “compatible with a cycle, not proof of direction”.'),
        ('3.10 Sensitivity (Table 13)', '', ['Excluding annotated (r 0.46) or straight-liners (r 0.47), dropping SHAI item 2 (r 0.48), bootstrap CI for B 0.54–0.83, quantile B 0.55–0.85, no quadratic effect (p 0.25), VIF ≤ 3.9, early vs late responders no difference; residuals non-normal → robust SEs.', 'Only the AI effect depended on a decision (definition).'], ''),
    ],
    sources_chap=['method', 'results'],
    figs=[('fig2_tools_motives.png', 'Figure 3: tools and motives. Read: bars = % of participants; multiple answers allowed, so they add to more than 100%.'),
          ('fig1_scatter_shai_css.png', 'Figure 5: each dot is a participant; the line is the best fit, the band its 95% CI. The upward slope is r = 0.47.'),
          ('fig4_corr_heatmap.png', 'Figure 6: darker = stronger correlation; stars = significant after FDR.'),
          ('fig7_forest_HA.png', 'Figure 8: each dot is an AOR with its 95% CI; the vertical line at 1 = no effect; lines that cross 1 are not significant.'),
          ('fig8_mediation.png', 'Figure 9: a = predictor → mediator, b = mediator → outcome, c′ = direct effect; the indirect effect is a × b.'),
          ('fig3_behaviours.png', 'Figure 4: behaviour after searching, disclosure, and effect on the relationship.')],
    qa_own=[
        ('Why non-parametric tests?', 'Shapiro–Wilk showed the scores were not normally distributed; Mann–Whitney and Kruskal–Wallis do not assume normality. Welch tests confirmed the same conclusions.'),
        ('What is FDR and why did you use it?', 'With 162 comparisons, about 8 would be “significant” by chance at p < 0.05. Benjamini–Hochberg controls the proportion of false discoveries; results with q ≥ 0.05 are labelled exploratory.'),
        ('Explain r = 0.47 to a non-statistician.', 'People with more health anxiety clearly tend to have more cyberchondria; anxiety accounts for about a fifth (22%) of the differences.'),
        ('Why both Pearson and Spearman?', 'Pearson for the linear correlation, Spearman as a check that does not depend on normality; both were 0.47.'),
        ('What does partial r = 0.48 tell us?', 'The link is not explained by age, gender, background, chronic disease, trust or AI use: it survives adjustment (H2).'),
        ('Why hierarchical regression?', 'To see what health anxiety adds after demographics and digital use: 18.4% extra variance, by far the biggest block.'),
        ('What do B and β mean in Table 9?', f'B = {N["B"]}: each SHAI point adds about 0.7 CSS points. β = {N["beta"]}: the standardised effect, used to compare predictors.'),
        ('Why robust (HC3) standard errors?', 'The residuals were heteroskedastic (Breusch–Pagan p = 0.004); HC3 gives valid standard errors anyway.'),
        ('What is an adjusted odds ratio of 3.12?', 'For each standard deviation higher cyberchondria, the odds of elevated health anxiety are about three times higher, holding other factors constant.'),
        ('Why is the reassurance-motive AOR so wide?', 'Only 57 events for 11 predictors (≈ 5 per variable), so estimates are imprecise and probably optimistic; we label them exploratory.'),
        ('What is the AUC and why corrected?', 'How well the model separates elevated from non-elevated anxiety. Models look better on their own data, so 500 bootstrap refits corrected 0.83 to 0.79.'),
        ('Does the mediation prove a vicious cycle?', 'No. One time point, the reverse order fits too, and the facets come from one questionnaire. It is compatible with a cycle; only longitudinal data can show direction.'),
        ('Why does the AI effect disappear?', f'It depends on {N["inc"]} people who named a chatbot without ticking it; they had the highest scores. Under the strict definition p = {N["palt"]}. Only 34 non-users made a small comparison group.'),
        ('Chronic illness was not significant in the logistic model. Why?', 'Dichotomising SHAI at 18 loses information and power. On the continuous score chronic illness is significant: p = 0.004 unadjusted and p = 0.029 adjusted (B +1.7).'),
        ('What do CFI, RMSEA and SRMR mean?', f'Fit indices for CFA. CSS-12 four factors: CFI {N["cfaC"]}, RMSEA {N["cfaR"]}, SRMR {N["srmr"]}: acceptable. SHAI one-factor fitted poorly.'),
        ('Why does the SHAI fit poorly?', 'It is not strictly unidimensional; recent validations find two factors (illness likelihood and consequences). Reliability was still good (α 0.81).'),
        ('What is measurement invariance (Table 5)?', 'Testing in steps whether the scale works the same in Arabic and English: same structure, then same loadings, then same intercepts. CSS-12 passed all three; SHAI-14 passed the first two.'),
        ('Why is high cyberchondria defined as > 33?', 'There is no validated clinical cut-off for the CSS-12, so we used the upper tertile of our sample, as is common.'),
        ('Why is the prevalence so dependent on the cut-off (Table 4)?', 'Because most scores cluster just below the thresholds; that is why we report several cut-offs and say “elevated”, not “disorder”.'),
        ('What does Table 13 show?', 'That the main correlation stays 0.46–0.48 whatever we exclude, and the regression is stable. Only the AI effect depended on a decision.'),
    ],
    qa_hard=[
        ('“Your p-values are tiny because your sample is large.”', 'The effect sizes are meaningful too: r = 0.47 is moderate and ΔR² 18.4% is a medium effect (f² ≈ 0.27).'),
        ('“You ran so many tests; something will be significant.”', 'Exactly why we used FDR correction and separated robust from exploratory findings.'),
        ('“The mediators are subscales of the same scale. Isn\'t that circular?”', 'Partly, yes: shared method variance inflates the paths. That is why we call it an exploratory decomposition, not a mechanism.'),
    ],
    edit=[
        'Results is mostly numbers: <b>do not change any number</b>, p, q, CI, test name or table reference.',
        'You may reword the connecting sentences in your own words; keep one main message per paragraph.',
        'Never type table or figure numbers by hand in captions; in text, keep “Table n / Figure n” exactly.',
        'If a number or sentence looks wrong, add a comment and ask; do not “fix” statistics yourself.',
        'Read 2.6 Statistical analysis until you can explain each method in one sentence; you will be asked.',
    ],
    self_test=[
        ('Main correlation with 95% CI?', f'r = {N["r"]} ({N["rci"]})'),
        ('Partial correlation?', N['pr']),
        ('Which two facets correlate most with health anxiety?', f'Excessiveness ({N["rE"]}) and distress ({N["rD"]})'),
        ('R² of the three regression blocks?', f'{N["R2a"]} → {N["R2b"]} → {N["R2c"]}'),
        ('β and B for health anxiety in the final model?', f'β {N["beta"]}, B {N["B"]}'),
        ('Three independent predictors of elevated health anxiety and their AORs?', f'Cyberchondria {N["orCSS"]}, reassurance motive {N["orMot"]}, age {N["orAge"]}'),
        ('AUC apparent and corrected?', f'{N["auc"]} → {N["aucc"]}'),
        ('Indirect effect via excessive searching?', f'{N["mA"]} (CI {N["mAci"]})'),
        ('Direct effect of HA on reassurance seeking after distress?', f'{N["mCd"]} (not significant)'),
        ('The only behavioural association that survived FDR?', f'Higher cyberchondria → less never-disclosure (AOR {N["nsC"]}, q {N["nsCq"]})'),
        ('AI effect inclusive vs strict?', f'+{N["Bai"]} vs +{N["Balt"]} (p {N["palt"]})'),
        ('Prevalence at cut-offs 15/18/22/29?', '32.7% / 19.0% / 7.3% / 0.7%'),
        ('Which scale is fully invariant across languages?', 'CSS-12 (scalar); SHAI-14 metric only'),
        ('How many of 168 item pairs survived FDR?', N['ibF']),
        ('Reliability α of both scales?', f'{N["aS"]} and {N["aC"]}'),
    ],
)

# ---------------------------------------------------------------- STUDENT 3
STUDENTS[3] = dict(
    tag='s3', title='Discussion & Conclusions', slides=range(24, 34), minutes='≈ 4 minutes',
    chapters='Chapter 4 Discussion (4.1–4.8), Chapter 5 Conclusions & Recommendations',
    opener='You close the defence. The committee\'s last impression is yours: finish calmly on the conclusion and the clinical message.',
    handover='“Thank you for listening; we welcome your questions.” (leave the r = 0.47 slide on screen)',
    walkthrough=[
        ('4.1 Principal findings', 'The four headline findings.', [f'First CSS-12 study in Baghdad; among the first to put AI chatbots next to search engines.', f'(1) AI used by {N["ai_tick"]}–{N["ai"]}; (2) r = {N["r"]}, independent; (3) concentrated in excessiveness and distress; (4) searching shapes the consultation.'], 'This is your opening slide content (slide 25).'),
        ('4.2 Health anxiety and cyberchondria', 'Why our r is weaker than meta-analyses.', [f'Ours 0.47 vs 0.62–0.63 {ref("McMullan RD")}{ref("Schenkel SK")}.', f'Reasons: measurement error (corrected ≈ {N["disr"]}); low, narrow health anxiety (mean {N["shai_m"]}); online recruitment of confident users; CSS-12 instead of the 33-item CSS.', f'19% elevated is a screening estimate; 7%–33% across cut-offs; consistent with high pandemic health anxiety in Iraq {ref("Karim SK")}.'], 'Learn the four reasons as a numbered list.'),
        ('4.3 Do they fuel each other?', '', [f'Consistent with the cognitive model and the Dutch longitudinal study {ref("Salkovskis PM, Warwick")}{ref("te Poel F")}.', f'But cross-sectional mediation is biased for longitudinal processes {ref("O\'Laughlin KD")}; an indirect effect cannot identify the true order {ref("Rohrer JM")}; shared method variance {ref("Podsakoff PM")}.', 'H3 supported statistically, not causally.'], 'If you remember one sentence: “compatible with a cycle, not proof of direction”.'),
        ('4.4 AI chatbots', '', [f'Our 78–89% vs ≈ 20% in a 2024 US survey {ref("Ayo-Ajibola O")} and 21% vs 98% search engines in 2025 {ref("Yun HS")}.', 'Young sample: 96% at 18–19 y vs 72% at ≥ 40 y.', 'Inclusive AI effect not robust; no moderation; absence of evidence, not evidence of absence.', f'Trust → fewer multiple-doctor visits but a trend to reassured delay (OR 1.33, p 0.088), echoing MENA data {ref("Dahshan A")}.'], ''),
        ('4.5 The consultation', '', [f'Reassured delay ({N["dr"]}): saves visits for minor symptoms, risks delayed diagnosis; occurs at all anxiety levels.', f'Cyberchondria with urgent care (exploratory), mirroring healthcare use {ref("Tyrer P. Recent")}{ref("Mathes BM")}.', f'Non-disclosure {N["never"]}; higher cyberchondria → more disclosure (robust); health anxiety → concealment (exploratory); discussed searches strengthen the relationship {ref("Luo A")}.', 'H4 partially supported.'], ''),
        ('4.6 Medical students', '', [f'Higher unadjusted health anxiety disappeared after adjustment (age). SHAI–CSS r {N["ms_r"]} in medical students vs {N["ot_r"]} others.', f'“Medical student syndrome”: weak evidence; a Palestinian study with the same SHAI ≥ 18 found medical students lowest {ref("Fasfoos A")}.', 'Medical knowledge did not protect against cyberchondria.'], 'Expect a question here: you are medical students yourselves.'),
        ('4.7 Regional comparison', '', [f'Jeddah: common, linked with smartphone addiction {ref("El-Zayat A")}; Saudi primary care: linked with health anxiety {ref("Pasay-An E")}; Lebanon: Arabic CSS-12 structure similar {ref("Hallit S")}.', f'Egypt: 1435 medical students, 85.8% moderate cyberchondria {ref("El-Zoghby SM")}; Saudi CSS-12 validation {ref("Alshaibani M")}.'], ''),
        ('4.8 Strengths and limitations', '', ['Strengths: established scales, bilingual with invariance testing, AI separate, complete data, FDR, robust and bootstrap methods, sensitivity analyses, links to behaviour.', 'Limitations: cross-sectional; convenience sample (young, 44% medical students); Arabic wording without back-translation; single-item behaviour measures; self-report; many tests and small subgroups; AI classification; careless responding.'], 'For each limitation, know what was done about it (Part 5).'),
        ('5.1 Conclusions (six)', '', [f'AI chatbots a leading source ({N["ai_tick"]} / {N["ai"]}).', f'{N["hac"]} elevated (screening; {N["ge29"]} at 29).', f'r = {N["r"]}, strongest predictor.', 'Compatible with a cycle, direction unproven.', 'No reliable independent AI effect.', f'Searching shapes the consultation: delay {N["dr"]}, non-disclosure {N["never"]}, strained trust {N["relneg"]}.'], ''),
        ('5.2 Recommendations', '', ['Clinicians: ask non-judgementally; recognise repeated searching as a sign; screen with SHAI; CBT strategies; teach digital/AI literacy in medical school.', 'Ministry of Health: Arabic digital and AI health-literacy campaigns; reliable Arabic triage sources.', 'AI developers: anxiety-aware answers, no escalation to rare diagnoses, Arabic.', f'Research: interventions (only 9 registered cyberchondria studies, none in Iraq {ref("ClinicalTrials")}); longitudinal and experimental designs; probability sampling; adapted Arabic scales.'], 'Recommendations must follow from results: be ready to link each to a finding.'),
    ],
    sources_chap=['disc'],
    qa_own=[
        ('Why is your correlation weaker than other studies?', f'Four reasons: measurement error (corrected r ≈ {N["disr"]}), low and narrow health anxiety, online recruitment of confident users, and the short CSS-12.'),
        ('Is your sample representative of Baghdad?', 'No: young, educated, many medical students. We do not generalise percentages; the associations were consistent across subgroups.'),
        ('What is new in your study?', 'First CSS-12 data from Baghdad; AI chatbots separated from search engines; psychology linked to behaviour before the consultation.'),
        ('Why is AI use so high compared with the US?', 'A young, educated, health-oriented sample; AI use fell clearly with age (96% → 72%). It is not an estimate for all adults.'),
        ('So does AI make cyberchondria worse?', 'We found no reliable independent effect beyond health anxiety. That is absence of evidence, not evidence of absence; experiments are needed.'),
        ('Is delaying care because of reassurance good or bad?', 'Both: it may prevent unnecessary visits for minor symptoms but risks missing serious ones. It occurred at all anxiety levels.'),
        ('Why do people with more cyberchondria disclose more?', 'Searching is central to their behaviour and they bring findings as part of reassurance seeking; health-anxious patients may hide searches for fear of being seen as “worried well” (exploratory).'),
        ('Are medical students more anxious?', f'Unadjusted yes, but it disappeared after adjustment (younger age). Their cyberchondria was the same as others\'. A Palestinian study {ref("Fasfoos A")} found medical students lowest.'),
        ('What is your biggest limitation?', 'Cross-sectional design: no causal direction. Second, the convenience sample.'),
        ('If you repeated the study, what would you change?', 'Probability sampling across ages, formal Arabic adaptation (or the published versions), a clearer AI-use question, and follow-up over time.'),
        ('How do your findings compare with the Arab region?', 'Consistent: Jeddah, Saudi primary care and Lebanon all link cyberchondria with health anxiety; Egyptian medical students show high cyberchondria.'),
        ('What should a doctor do differently on Monday?', 'Ask every patient, without judgement, what they searched or asked an AI; treat repeated searching and reassurance seeking as signs of health anxiety; avoid endless reassurance.'),
        ('What should the Ministry do?', 'Support Arabic digital and AI health-literacy campaigns and reliable Arabic triage sources, warning especially about false reassurance.'),
        ('Why recommend intervention trials?', 'ClinicalTrials.gov lists only nine cyberchondria studies, none in Iraq; brief Arabic digital or CBT interventions are a clear gap.'),
        ('Was H4 supported?', 'Partially: only higher cyberchondria → more disclosure survived FDR; urgent care and strained relationship were exploratory.'),
        ('How do you know the results are not due to careless responders?', 'We excluded straight-liners and annotated responses in sensitivity analyses; the correlation did not change (Table 13).'),
        ('What does “absence of evidence is not evidence of absence” mean here?', 'Not finding a robust AI effect does not prove AI has no effect; our design and the small non-user group could miss it.'),
        ('Why is the Discussion careful with words like “cycle”?', 'Because one survey cannot show direction; we use “compatible with” to stay within what the data show.'),
    ],
    qa_hard=[
        ('“Your recommendations go beyond your data.”', 'Each one is tied to a finding (e.g., ask about searches ← 31.7% never disclose); policy recommendations are phrased as “may consider”.'),
        ('“Why should we believe a self-report survey?”', 'Self-report is standard for these constructs; the scales are validated, reliable and invariant; we acknowledge recall and social-desirability bias.'),
        ('“Isn\'t the AI finding just a coding decision?”', 'Yes, and we say so openly; that is why we conclude there is no reliable evidence of an independent AI effect.'),
    ],
    edit=[
        'Discussion is where your own interpretation belongs: rewrite each paragraph in your voice, keeping every [n] with its claim.',
        'Add genuine local insight (how patients in Baghdad use ChatGPT, pharmacies, cost of visits) only if it is true.',
        'Do not strengthen claims: keep “compatible with”, “exploratory”, “may consider”.',
        'Recommendations can be personal and practical, but each must follow from a result.',
        'Keep the limitations complete: removing one makes the thesis look less honest, not stronger.',
    ],
    self_test=[
        ('Our r vs meta-analytic r?', f'{N["r"]} vs 0.62–0.63'),
        ('Four reasons our r is weaker?', 'Measurement error, low/narrow health anxiety, online recruitment, short CSS-12'),
        ('Disattenuated correlation?', f'≈ {N["disr"]}'),
        ('AI use in our study vs US 2024?', f'{N["ai_tick"]}–{N["ai"]} vs ≈ 20%'),
        ('AI use by age?', '96% at 18–19 y vs 72% at ≥ 40 y'),
        ('Percentage delaying care when reassured?', N['dr']),
        ('Percentage never telling the doctor?', N['never']),
        ('Was H3 supported?', 'Statistically, not causally'),
        ('Was H4 supported?', 'Partially (only disclosure survived FDR)'),
        ('SHAI–CSS r in medical students vs others?', f'{N["ms_r"]} vs {N["ot_r"]}'),
        ('Egyptian study size and finding?', '1435 medical students; 85.8% moderate cyberchondria'),
        ('Number of registered cyberchondria trials, and in Iraq?', 'Nine; none in Iraq'),
        ('Biggest limitation?', 'Cross-sectional design'),
        ('Prevalence range across cut-offs?', 'About 7% to 33% (0.7% at 29)'),
        ('The clinical message in one sentence?', 'Ask every patient, without judgement, what they searched or asked an AI'),
    ],
)

LIMITS = [
    ['Cross-sectional design', 'Reverse-direction models; wording “compatible with”; longitudinal studies recommended'],
    ['Convenience/snowball sample', 'Percentages not generalised; associations consistent across subgroups'],
    ['Arabic wording (no back-translation)', 'Equal reliability and means; CSS-12 fully invariant, SHAI-14 metric; no item DIF'],
    ['Single-item behaviour measures', 'Reported descriptively; associations labelled exploratory'],
    ['Many tests', 'FDR correction; robust vs exploratory separated'],
    ['Small subgroups (34 non-users)', 'Acknowledged; AI effect called “not robust”'],
    ['Self-report and careless responding', 'Anonymous; straight-liners and annotated responses excluded in sensitivity analyses (no change)'],
]

# ================================================================ BUILD ONE GUIDE
def build(k):
    S = STUDENTS[k]; other = [j for j in (1, 2, 3) if j != k]
    h = [f'<!doctype html><html><head><meta charset="utf-8"><title>Student {k} Guide</title><style>{CSS}</style></head><body>']
    w = h.append
    # cover
    w(f'''<h1>Defence Guide · Student {k}</h1>
<div class="sub"><span class="tag {S["tag"]}">Student {k}: {S["title"]}</span> &nbsp; Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad</div>
<div class="box"><b>Your role.</b> {S["opener"]}</div>''')
    w(table(['', ''], [
        ['<b>You present</b>', f'Slides {S["slides"].start}–{S["slides"].stop - 1} ({S["minutes"]})'],
        ['<b>You own in the thesis</b>', S['chapters']],
        ['<b>Your handover line</b>', S['handover']],
        ['<b>Your teammates</b>', ' · '.join(f'Student {j}: {STUDENTS[j]["title"]} (slides {STUDENTS[j]["slides"].start}–{STUDENTS[j]["slides"].stop - 1})' for j in other)],
    ], ['26%', '74%']))
    w('<h3>What is in this guide</h3>' + ol([
        'The whole study: two-minute script, core facts, terms, “never say” list (same in all three guides)',
        'Your chapter, section by section: what it says, the numbers, the sources, what to watch',
        'Your key sources: each reference number in your chapter and what it found',
        'Your slides, one by one: what is on screen, your script, timing and traps',
        'Questions: on your part, on the whole study, and difficult ones, with model answers',
        'Editing your chapter safely and in your own words',
        'Your 14-day plan', 'Self-test with answers', 'Checklist for the day before']))
    w(shared_core())
    # Part 2 walkthrough
    w(f'<h2 class="page">Part 2 · Your chapter, section by section</h2>')
    w('<p>For each section: its <b>purpose</b>, the <b>key points and numbers</b> (with the reference numbers used in the thesis), and what to <b>watch</b>.</p>')
    for sec, purpose, pts, watch in S['walkthrough']:
        w(f'<h4>{sec}</h4>' + (f'<p><i>{purpose}</i></p>' if purpose else '') + ul(pts) + (f'<p class="tip">Watch: {watch}</p>' if watch else ''))
    if 'figs' in S:
        w('<h3>How to read your figures</h3>')
        for f, c in S['figs']: w(img(f, c))
    if k == 1:
        w(img('fig0b_flowchart.png', 'Figure 2: the study flowchart. You present this on the methodology slides.'))
    # Part 3 sources
    w('<h2 class="page">Part 3 · Your key sources</h2><p>Every reference cited in your chapter, with its number in the thesis. Know the bold ones well: examiners often ask “who found that?”.</p>')
    chap_nums = sorted(set().union(*[CHAP[c] for c in S['sources_chap']]))
    w(table(['No.', 'Reference (as listed in Chapter 6)'], [[f'[{n_}]', e(REFS[n_][:230]) + ('…' if len(REFS[n_]) > 230 else '')] for n_ in chap_nums], ['7%', '93%']))
    # Part 4 slides
    w(f'<h2 class="page">Part 4 · Your slides, one by one</h2><p>The script below is the speaker-notes text of your slides in the presentation. Practise until you can say it in your own words without reading.</p>')
    for i, title, notes in SLIDES:
        if i in S['slides']:
            w(f'<div class="slide"><div class="hd">Slide {i} · {e(title)}</div><p class="script">{e(notes)}</p></div>')
    w(f'<div class="box warn"><b>Delivery for your part:</b> {S["minutes"]}; about 25–35 seconds per content slide and 10 seconds per divider. Point at the number you are saying. Pause after each key number. End with: {S["handover"]}</div>')
    # Part 5 questions
    w('<h2 class="page">Part 5 · Questions and model answers</h2><h3>A. Questions on your part</h3>' + qa(S['qa_own']))
    w('<h3>B. Questions anyone can be asked (know the answer even if it is not your part)</h3>' + qa([
        ('Summarise your study in one minute.', 'Use the two-minute script in Part 1, shortened: design, sample, two scales, r = 0.47, AI result, behaviour, clinical message.'),
        ('What is your main finding?', f'Health anxiety and cyberchondria are moderately and robustly associated (r = {N["r"]}), independent of other factors.'),
        ('What did you find about AI chatbots?', f'They are the main source ({N["ai_tick"]} ticked), but there was no reliable independent effect on cyberchondria beyond health anxiety.'),
        ('What percentage had elevated health anxiety?', f'{N["hac"]} at SHAI ≥ 18, a screening threshold, not a diagnosis.'),
        ('What is your biggest limitation?', 'The cross-sectional design: no direction of cause.'),
        ('What is the clinical message?', 'Ask patients, without judgement, what they searched or asked an AI.'),
        ('Why did you split the presentation this way?', 'By chapter, but each of us studied the whole thesis.'),
        ('Were your hypotheses written before you collected the data?', 'Answer truthfully. A safe true answer: they follow from our objectives and previous research, and the questionnaire was designed to measure these things; we tested all of them and report every result, including those not supported.', 'Never claim they were pre-registered.'),
        ('Who did the statistical analysis?', 'Answer honestly according to what you did. If AI tools helped with code or drafting, say so in line with your college policy and the declaration in the thesis.'),
    ]))
    w('<h3>C. Difficult or hostile questions</h3>' + qa(S['qa_hard']))
    w('<h3>D. Limitations and what was done about each (all students)</h3>' + table(['Limitation', 'What we did / how to answer'], LIMITS, ['34%', '66%']))
    w('''<div class="box"><b>How to answer any question:</b> pause → repeat the question briefly → answer in two or three sentences → stop.
If you do not know: “We did not examine that directly; based on our data we would expect…, and it is a good question for future research.” Never invent a number.
If a teammate struggles: “If I may add…”.</div>''')
    # Part 6 editing
    w('<h2 class="page">Part 6 · Editing your chapter</h2>')
    w('''<div class="box warn"><b>The Word file is the master copy.</b> Edit only the .docx, in one shared OneDrive / Word Online file with
<b>Review → Track Changes</b> on. Keep an untouched copy (Thesis_ORIGINAL.docx). Avoid Google Docs: it breaks the automatic numbering.</div>''')
    w('<h3>For your chapter</h3>' + ul(S['edit']))
    w('<h3>Never touch</h3>' + ul(['Numbers, %, p, q, CI, r, OR, β, n', 'Reference numbers like [18] (move them with their sentence)', 'The reference list', 'Table/figure captions, table of contents and lists (automatic fields)', 'Heading numbers and styles', 'Times New Roman 14 and page numbering']))
    w('<h3>The rewrite method (paragraph by paragraph)</h3>' + ol(['Read until you understand it; look up anything unclear.', 'Close it and explain it out loud.', 'Write your version from that explanation.', 'Compare: same facts, numbers and [n]; nothing claimed more strongly.', 'Read aloud; change any phrase you would never say.']))
    w('<h3>After editing</h3>' + ol(['Ctrl + A, then F9, to update the table of contents, the lists and the captions.', 'Search for “[” to find placeholders left.', 'Swap chapters with a teammate for checking.', 'Export to PDF and look at every page.']))
    w('''<div class="box red"><b>About AI use, honestly.</b> Check your college's AI policy with your supervisor and declare AI assistance if required. A sentence you can adapt:
<i>“The statistical analysis code and an initial draft of this report were prepared with the assistance of an AI tool (Claude, Anthropic). All analyses were checked, and the text was reviewed and rewritten by the authors, who take full responsibility for its content.”</i>
Do not use paraphrasing tools or tricks to fool detectors: they make the text worse and can count as misconduct. Real ownership (your words, your understanding, your edit history) is the best protection.</div>''')
    # Part 7 plan
    plan = [
        ('1', 'Read the Abstract, 1.8 and Chapter 5. Learn the two-minute script (Part 1).'),
        ('2', 'Read the whole thesis once, marking what you cannot explain.'),
        ('3', 'Core facts and terms (Part 1). Self-test on core facts.'),
        ('4', 'Your chapter, sections in Part 2 (first half).'),
        ('5', 'Your chapter, second half; your key sources (Part 3).'),
        ('6', 'Start rewriting your chapter (Part 6).'),
        ('7', 'Finish rewriting. Self-test (Part 8).'),
        ('8', 'Swap chapters with a teammate; check accuracy and voice.'),
        ('9', 'Your slides: read the scripts (Part 4), then present them alone 3 times.'),
        ('10', 'Questions A–D out loud (Part 5). Record yourself once.'),
        ('11', 'Team: full rehearsal with timing and handovers.'),
        ('12', 'Team: mock committee; each student asks the others their Part 5 questions.'),
        ('13', 'Fix weak answers; second full rehearsal; final Word checks.'),
        ('14', 'Day before: checklist (last page); one calm run-through; sleep.'),
    ]
    w('<h2 class="page">Part 7 · Your 14-day plan</h2>' + table(['Day', 'Task'], plan, ['8%', '92%']))
    # Part 8 self-test
    w('<h2>Part 8 · Self-test</h2><p>Cover the answers, answer out loud, then check. Repeat until all are correct.</p>')
    w(table(['#', 'Question', 'Answer'], [[str(i + 1), e(q), a] for i, (q, a) in enumerate(S['self_test'] + [
        ('Main correlation (everyone)?', f'r = {N["r"]}'), ('Elevated health anxiety (everyone)?', N['hac']), ('AI chatbots ticked (everyone)?', N['ai_tick']),
        ('Never tell the doctor (everyone)?', N['never']), ('Sample size (everyone)?', str(N['n']))])], ['5%', '55%', '40%']))
    # checklist
    w('<h2>Part 9 · Day-before checklist</h2>' + table(['✓', 'Item'], [['☐', x] for x in [
        'All placeholders filled (names, supervisor, college, logo, degree, year, ethics, Google Forms question, Acknowledgment)',
        'Fields updated (Ctrl + A, F9); PDF checked page by page', 'AI declaration added if required',
        'Presentation: names on slide 1, ethics number on slide 10; USB + PDF + email copies; clicker tested',
        f'I can give the two-minute summary and my slides ({S["slides"].start}–{S["slides"].stop - 1}) without notes',
        'I have answered every question in Part 5 out loud', 'I scored 100% on the self-test',
        'Printed thesis copy if required; arrive early; agree who stands where']], ['6%', '94%']))
    w('<p class="small">Generated from the study outputs and the presentation, so every number and slide script here matches the thesis and the deck.</p></body></html>')
    return '\n'.join(h)

# chapter citation sets from the thesis
_ps_all = _ps
def _chap(a, b):
    s_, e_ = _ps_all.index(a), _ps_all.index(b); nums = set()
    for p_ in _ps_all[s_:e_]:
        for g in re.findall(r'\[([\d,–\- ]+)\]', p_):
            for part in g.split(','):
                part = part.strip()
                if re.match(r'^\d+[–-]\d+$', part):
                    x, y = re.split('[–-]', part); nums.update(range(int(x), int(y) + 1))
                elif part.isdigit(): nums.add(int(part))
    return nums
CHAP = {'intro': _chap('1. Introduction', '2. Method'), 'method': _chap('2. Method', '3. Results'),
        'results': _chap('3. Results', '4. Discussion'), 'disc': _chap('4. Discussion', '6. References')}

if SHORT:   # Student 2 for the short (submitted) thesis
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from numbering import remap
    S2 = STUDENTS[2]
    S2['chapters'] = 'Chapter 3 Results (3.1–3.6), Tables 1–11, Figures 2–8; and Section 2.5 Statistical analysis (you are the team\'s statistics person)'
    S2['figs'] = [f for f in S2['figs'] if 'corr_heatmap' not in f[0]]
    SS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(NUMS)), '..', 'simple.json')))
    _ai = [r for r in SS['ols_coef'] if r['term'] == 'ai_user'][0]
    N['palt'] = f"{SS['ai_strict']['p']:.2f}"; N['Baici'] = f"{_ai['B'] - 1.9685 * _ai['SE']:.1f}–{_ai['B'] + 1.9685 * _ai['SE']:.1f}"; N['auc'] = f"{SS['logit_HA']['AUC']:.2f}"
    _sm, _sl = SS['mediation'], SS['logit_HA']
    _b = {(r['Outcome'], r['Predictor']): r for r in SS['behaviour']}
    _rel = _b[('Negative effect on doctor relationship', 'zCSS')]; _nsS = _b[('Never disclose to physician', 'zSHAI')]; _nsC = _b[('Never disclose to physician', 'zCSS')]
    _oc = {r['term']: r for r in SS['ols_coef']}; _a30 = _oc["C(age_c, Treatment('20–29'))[T.30–39]"]; _a40 = _oc["C(age_c, Treatment('20–29'))[T.≥40]"]
    T_ = lambda k, n: f'{k} {n}'          # short-numbered reference that remap() must not touch
    S2['walkthrough'] = [
        (f'3.1 Participants and online health-information seeking ({T_("Tables", "1–2")}, {T_("Figures", "2–3")})', 'Who answered, how they search, and what they do after searching.',
         [f'{N["n"]} adults, no missing data; {N["age20"]} aged 20–29; {N["fem"]} female; medical students {N["med"]}; health background {N["hb"]}; chronic condition {N["chron"]}; Arabic {N["ar"]}.',
          f'AI ticked {N["ai_tick"]} ({N["ai"]} incl. named) vs search engines {N["se"]}; AI without any search engine {N["ai_only"]}; ChatGPT {N["gpt"]}. AI use 96% at 18–19 y vs 72% at ≥ 40 y.',
          f'Motives: convenience {N["conv"]}, “do I need a doctor?” {N["tri"]}, reassurance {N["reas"]}.',
          f'After searching: delay/skip care when reassured {N["dr"]}; ignore {N["ign"]}; several doctors {N["mdoc"]}; urgent care {N["urg"]}. Always tell the doctor {N["always"]}; never (fear of judgement) {N["never"]}; relationship strained {N["relneg"]}.'],
         'Message: a young, digitally active sample whose first “doctor” is often an AI; searching changes the consultation.'),
        (f'3.2 Levels of health anxiety and cyberchondria ({T_("Tables", "3–4")})', '', [
          f'SHAI {N["shai_m"]} ± {N["shai_sd"]}; elevated {N["hac"]} (CI {N["hac_ci"]}); {T_("Table", "4")}: 32.7% at ≥ 15, 19.0% at ≥ 18, 7.3% at ≥ 22, 0.7% at ≥ 29.',
          f'CSS {N["css_m"]} ± {N["css_sd"]}; excessiveness highest, compulsion lowest.',
          f'Cronbach α {N["aS"]} (SHAI) and {N["aC"]} (CSS): good. Arabic and English responders did not differ (Mann–Whitney p 0.86 and 0.65).'],
         'Why several cut-offs? Because prevalence depends on the threshold; reporting all four is honest.'),
        (f'3.3 Main association ({T_("Table", "5")}, {T_("Figure", "4")})', 'The central result (H1, H2).', [
          f'Pearson r = {N["r"]} (95% CI {N["rci"]}), Spearman ρ = {N["rho"]}, p < 0.001; explains {N["r2"]}; partial r = {N["pr"]}.',
          f'Facets: strongest with excessiveness {N["rE"]} and distress {N["rD"]}, weakest with compulsion {N["rC"]} and reassurance {N["rR"]}.'],
         'H1 and H2 are answered here.'),
        (f'3.4 Factors associated ({T_("Tables", "6–7")}, {T_("Figure", "5")})', 'Mann–Whitney / Kruskal–Wallis and χ² tests (p < 0.05).', [
          'Health anxiety higher with a chronic condition (p 0.004), in reassurance seekers (p < 0.001), social-media users (p 0.001) and AI users (p 0.008); differs by age (p 0.008), education (p 0.002) and occupation (p 0.005); gender and language no difference.',
          'Cyberchondria higher in AI users (p < 0.001), highest in AI + search engine users (p < 0.001), and in social-media users (p 0.021).',
          f'Elevated health anxiety → 52.6% vs 23.0% high cyberchondria (OR 3.71) ({T_("Table", "7")}).'],
         'Many tests at p < 0.05: a few weaker results could be chance (we say so in the limitations).'),
        (f'3.5 Independent predictors ({T_("Tables", "8–9")}, {T_("Figure", "6")})', '', [
          f'Hierarchical linear regression: R² {N["R2a"]} → {N["R2b"]} → {N["R2c"]}; health anxiety adds {N["dR2"]}; B = {N["B"]}, β = {N["beta"]}, p < 0.001. Ages 30–39 (B {_a30["B"]:.1f}) and ≥ 40 (B {_a40["B"]:.1f}) also higher than 20–29.',
          f'AI: +{N["Bai"]} inclusive vs +{N["Balt"]}, p {N["palt"]} strict → no reliable independent effect.',
          f'Binary logistic (57 events): AOR {N["orCSS"]} cyberchondria per SD, {N["orMot"]} reassurance motive, {N["orAge"]} age; Nagelkerke R² {_sl["nagelkerke"]:.2f}; Hosmer–Lemeshow p {_sl["HL_p"]:.2f} (good fit); AUC {_sl["AUC"]:.2f}; ≈ 5 events per variable → estimates may be overestimated.',
          'Sensitivity (one sentence): r stayed 0.47–0.48 in every check.'],
         'You will be asked about AOR, AUC and Hosmer–Lemeshow.'),
        (f'3.6 Behaviour and pathways ({T_("Tables", "10–11")}, {T_("Figures", "7–8")})', '', [
          f'Higher CSS → urgent visits (AOR {N["urC"]}, p 0.013), less ignoring ({N["igC"]}, p 0.009), strained relationship ({_rel["AOR"]:.2f}, p {_rel["p"]:.3f}) and more disclosure (never-disclose AOR {_nsC["AOR"]:.2f}, p 0.001).',
          f'Higher SHAI → concealment (never-disclose AOR {_nsS["AOR"]:.2f}, p {_nsS["p"]:.3f}). Trust → fewer multiple doctors (AOR 0.59, p 0.004).',
          f'Mediation (Sobel test): via excessive searching {_sm[0]["indirect"]:.2f} (z {_sm[0]["sobel_z"]:.2f}, p < 0.001; about a third); via distress {_sm[1]["indirect"]:.2f} (z {_sm[1]["sobel_z"]:.2f}), direct {_sm[1]["c_prime"]:.2f} (ns); reverse {_sm[2]["indirect"]:.2f} (z {_sm[2]["sobel_z"]:.2f}).'],
         'Always end with: “compatible with a cycle, not proof of direction”.'),
    ]
    S2['figs'] = [('fig2_tools_motives.png', 'Figure 3: tools and motives. Read: bars = % of participants; multiple answers allowed, so they add to more than 100%.'),
          ('fig1_scatter_shai_css.png', 'Figure 5: each dot is a participant; the line is the best fit, the band its 95% CI. The upward slope is r = 0.47.'),
          ('fig7_forest_HA_simple.png', 'Figure 8: each dot is an AOR with its 95% CI; the vertical line at 1 = no effect; lines that cross 1 are not significant.'),
          ('fig8_mediation_sobel.png', 'Figure 9: a = predictor → mediator, b = mediator → outcome, c′ = direct effect; the indirect effect is a × b, tested with the Sobel test.'),
          ('fig3_behaviours.png', 'Figure 4: behaviour after searching, disclosure, and effect on the relationship.')]
    _drop = ('What is FDR', 'Why robust (HC3)', 'What is the AUC and why corrected', 'What do CFI, RMSEA', 'Why does the SHAI fit poorly', 'What is measurement invariance', 'What does Table 13 show')
    S2['qa_own'] = [q for q in S2['qa_own'] if not q[0].startswith(_drop)] + [
        ('Which software did you use?', 'IBM SPSS Statistics [version]; the syntax file reproduces every table (say this only after the team has run it and checked the numbers).'),
        ('Why didn\'t you correct for multiple testing?', 'We used the standard p < 0.05, as most graduation theses do, and we say in the limitations that with many tests some weaker results may be chance. Our main results are p < 0.001.'),
        ('What is the AUC?', f'The area under the ROC curve: how well the model separates elevated from non-elevated anxiety. {_sl["AUC"]:.2f} is good.'),
        ('What does the Hosmer–Lemeshow test tell you?', f'Whether the logistic model fits the data. We want it non-significant: p = {_sl["HL_p"]:.2f}, so the fit is good.'),
        ('How did you test mediation?', 'Three linear regressions per model (paths a, b, c and c′) and the Sobel test for the indirect effect a × b.'),
        ('What does Sobel z = 5.14 mean?', 'The indirect effect is about five standard errors above zero, so p < 0.001: part of the link runs through excessive searching, statistically.'),
        ('Why Mann–Whitney and not the t-test?', 'Shapiro–Wilk showed the scores were not normal (p < 0.01), so we used non-parametric tests that compare ranks.')]
    S2['qa_own'] = [((a.replace('Welch tests confirmed the same conclusions.', '').strip()), b) if False else (a, b.replace(' Welch tests confirmed the same conclusions.', '').replace('we label them exploratory', 'we interpret them cautiously')) for a, b in S2['qa_own']]
    S2['qa_hard'] = [
        ('“Your p-values are tiny because your sample is large.”', 'The effect sizes are meaningful too: r = 0.47 is moderate and ΔR² 18.4% is a medium effect.'),
        ('“You ran so many tests; something will be significant.”', 'Yes, that is possible for the weaker results, and we say so in the limitations. The main findings (r = 0.47, health anxiety in the regression, the mediation paths) have p < 0.001 and would survive any correction.'),
        ('“The mediators are subscales of the same scale. Isn\'t that circular?”', 'Partly, yes: shared method variance inflates the paths. That is why we call it a statistical decomposition, not a mechanism.'),
    ]
    S2['edit'] = [x.replace(', p, q, CI', ', p, CI').replace('Read 2.6', 'Read 2.5') for x in S2['edit']]
    S2['self_test'] = [q for q in S2['self_test'] if not q[0].startswith(('AUC apparent', 'Indirect effect via', 'The only behavioural', 'Which scale is fully', 'How many of 168'))] + [
        ('AUC and Hosmer–Lemeshow p?', f'{_sl["AUC"]:.2f}; p {_sl["HL_p"]:.2f}'),
        ('Indirect effect via excessive searching and its Sobel z?', f'{_sm[0]["indirect"]:.2f}; z {_sm[0]["sobel_z"]:.2f}'),
        ('Behaviours linked to higher cyberchondria?', 'Urgent visits, less ignoring, strained relationship, more disclosure'),
        ('Which significance level did you use?', 'p < 0.05, two-sided, no correction for multiple tests')]
    html_ = build(2).replace('2.6 Statistical analysis', '2.5 Statistical analysis').replace('Read 2.6 Statistical analysis', 'Read 2.5 Statistical analysis')
    for a, b in [(f'; ω {N["oS"]}, {N["oC"]} · CSS-12 4-factor CFA: CFI {N["cfaC"]}, RMSEA {N["cfaR"]}, SRMR {N["srmr"]}', ' (Cronbach α ≥ 0.8 = good)'),
                 ('CSS-12 fully (scalar) invariant; SHAI-14 metric invariant; no item DIF after FDR', 'no difference in SHAI or CSS scores (Mann–Whitney p 0.86 and 0.65)'),
                 (f'AUC {N["auc"]} → {N["aucc"]}', f'AUC {_sl["AUC"]:.2f}'),
                 (f'via excessive searching {N["mA"]} (CI {N["mAci"]})', f'via excessive searching {N["mA"]} (Sobel z {_sm[0]["sobel_z"]:.2f})'),
                 (f'higher cyberchondria → more disclosure (OR {N["nsC"]}, q {N["nsCq"]})', f'higher cyberchondria → more disclosure (AOR {N["nsC"]}, p 0.001)'),
                 ('every sensitivity analysis left the main result unchanged (Table 13)', 'every sensitivity analysis left the main result unchanged (r 0.47–0.48)'),
                 ("<tr><td>FDR (q-value)</td><td>Correction for running many tests; a result is “robust” if q &lt; 0.05, otherwise exploratory.</td></tr>", "<tr><td>Sobel test</td><td>Tests whether an indirect (mediated) effect a × b is different from zero.</td></tr>"),
                 ("<tr><td>FDR (q-value)</td><td>Correction for running many tests; a result is “robust” if q < 0.05, otherwise exploratory.</td></tr>", "<tr><td>Sobel test</td><td>Tests whether an indirect (mediated) effect a × b is different from zero.</td></tr>"),
                 ("<tr><td>Moderation</td><td>Whether a third variable changes the strength of a link (e.g., does AI use make the link stronger? No).</td></tr>", "<tr><td>Hosmer–Lemeshow test</td><td>Checks the fit of a logistic model; p &gt; 0.05 = good fit.</td></tr>"),
                 ('Cronbach α / McDonald ω', 'Cronbach α'),
                 ("<tr><td>CFA (CFI, RMSEA, SRMR)</td><td>Checks the items group into the intended factors. Good: CFI ≈ 0.95+, RMSEA ≤ 0.08, SRMR ≤ 0.08.</td></tr>", "<tr><td>Cramér's V</td><td>Strength of a χ² association: 0.1 small, 0.3 medium, 0.5 large.</td></tr>"),
                 ("<tr><td>Measurement invariance</td><td>Checks the scale measures the same thing in two groups (here Arabic vs English) before comparing them.</td></tr>", "<tr><td>VIF</td><td>Checks that regression predictors are not near-duplicates; below 5 is fine.</td></tr>"),
                 ('“we tested it: equal reliability and formal invariance, but no formal back-translation”', '“the team wrote the Arabic wording; reliability was good and Arabic and English scores did not differ, but there was no formal back-translation”'),
                 ('Health anxiety and cyberchondria are moderately and robustly associated', 'Health anxiety and cyberchondria are moderately associated'),
                 ('Equal reliability and means; CSS-12 fully invariant, SHAI-14 metric; no item DIF', 'Good reliability; Arabic and English scores did not differ'),
                 ('Reported descriptively; associations labelled exploratory', 'Reported descriptively; interpreted cautiously'),
                 ('FDR correction; robust vs exploratory separated', 'Stated in the limitations; main results p < 0.001'),
                 ('Acknowledged; AI effect called “not robust”', 'Acknowledged; AI effect depends on the definition')]:
        html_ = html_.replace(a, b)
    html_ = html_.replace('is it robust?', 'does it hold?')
    html_ = html_.replace('straight-liners and annotated responses excluded in sensitivity analyses', 'straight-line responders excluded in a sensitivity analysis').replace('We excluded straight-liners and annotated responses in sensitivity analyses', 'We excluded straight-line responders in a sensitivity analysis').replace('0.46–0.48', '0.47–0.48')
    html_ = html_.replace('Under the strict definition p = 0.31', f'Under the strict definition p = {N["palt"]}').replace('(p 0.31)', f'(p {N["palt"]})')
    open(f'{OUT}/Student2_Guide.html', 'w').write(remap(html_))
else:
    os.makedirs(OUT, exist_ok=True)
    for k in (1, 2, 3):
        open(f'{OUT}/Student{k}_Guide.html', 'w').write(build(k))
    print('wrote', f'{OUT}/Student{k}_Guide.html')
