"""The complete research guide (PDF): every part of the thesis from the title page to the references, explained from
zero for a reader who knows the subject and the data but not research methods or statistics. Every choice is
explained (why this design, why this test, why not the other one), with likely questions and short Arabic notes.
AI use is reported with the inclusive definition (the 32 who named a chatbot counted as AI users).
Usage: python3 20_complete_guide.py <output dir> <out.html>   (then print to PDF)"""
import sys, os, json

OUT, HTML = sys.argv[1], sys.argv[2]
FIG = os.path.abspath(f'{OUT}/figures')
MED = json.load(open(f'{OUT}/medians_by_group.json'))

CSS = """
@page { size: A4; margin: 15mm 15mm 15mm 15mm; }
* { box-sizing: border-box; }
body { font-family: Carlito, Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.6pt; line-height: 1.48; color: #1d2230; margin: 0; }
h1 { font-family: Caladea, Cambria, Georgia, serif; font-size: 28pt; color: #1F3B4D; margin: 0 0 4px; line-height: 1.1; }
h2 { font-family: Caladea, Cambria, Georgia, serif; font-size: 17pt; color: #1F3B4D; margin: 0 0 8px; padding-bottom: 4px; border-bottom: 2.5px solid #1F3B4D; page-break-after: avoid; }
h3 { font-size: 12.4pt; color: #b4541c; margin: 13px 0 4px; page-break-after: avoid; }
h4 { font-size: 11pt; color: #1F3B4D; margin: 9px 0 3px; page-break-after: avoid; }
p { margin: 3px 0 7px; } ul, ol { margin: 3px 0 8px; padding-left: 20px; } li { margin: 2px 0; }
.page { page-break-before: always; }
.part { page-break-before: always; padding-top: 60mm; }
.part h1 { font-size: 34pt; } .part p { font-size: 13pt; color: #46506a; }
.lead { font-size: 12pt; color: #46506a; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.5pt; page-break-inside: avoid; }
th { background: #1F3B4D; color: #fff; text-align: left; padding: 4px 6px; font-weight: 700; }
td { padding: 3.5px 6px; border-bottom: 1px solid #dfe5ea; vertical-align: top; }
tr.grp td { background: #e7eef3; font-weight: 700; color: #1F3B4D; }
tr.hi td { background: #fff4c2; }
.sm { font-size: 8.8pt; } .sm td, .sm th { padding: 2.5px 5px; }
figure { margin: 6px 0 10px; text-align: center; page-break-inside: avoid; } figure img { border: 1px solid #d5dbe1; }
figcaption { font-size: 9pt; color: #555; font-style: italic; margin-top: 3px; }
.box { border-radius: 7px; padding: 7px 11px; margin: 8px 0; page-break-inside: avoid; }
.box .bt { font-weight: 700; font-size: 8.8pt; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 2px; }
.box p { margin: 2px 0 4px; } .box ul { margin: 2px 0 3px; }
.say { background: #e6f2ec; border-left: 5px solid #1e7a52; } .say .bt { color: #1e7a52; }
.trap { background: #fbecef; border-left: 5px solid #9d1c4a; } .trap .bt { color: #9d1c4a; }
.ask { background: #eef0fb; border-left: 5px solid #3d3a9e; } .ask .bt { color: #3d3a9e; }
.idea { background: #fff6e5; border-left: 5px solid #b4541c; } .idea .bt { color: #b4541c; }
.why { background: #eef6fb; border-left: 5px solid #1F6FA0; } .why .bt { color: #1F6FA0; }
.ar { background: #f3f0fa; border-right: 5px solid #6a4c9c; direction: rtl; text-align: right; font-family: 'DejaVu Sans', 'Noto Naskh Arabic', Arial, sans-serif; font-size: 10.4pt; line-height: 1.85; }
.ar .bt { color: #6a4c9c; direction: ltr; text-align: left; }
.qq { font-weight: 700; margin-top: 6px !important; } .aa { margin-left: 10px !important; }
mark { background: #fff07a; padding: 0 1px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
.calc { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 9.2pt; background: #f4f6f9; border: 1px solid #e0e5eb; border-radius: 6px; padding: 7px 10px; margin: 6px 0 10px; white-space: pre-wrap; page-break-inside: avoid; }
dl.cols { display: grid; grid-template-columns: 27% 73%; margin: 4px 0 10px; border-top: 1px solid #dfe5ea; page-break-inside: avoid; }
dl.cols dt { font-weight: 700; padding: 3px 8px 3px 0; border-bottom: 1px solid #dfe5ea; color: #1F3B4D; }
dl.cols dd { margin: 0; padding: 3px 0; border-bottom: 1px solid #dfe5ea; }
.toc li { margin: 3px 0; font-size: 11pt; }
.ref { font-size: 9.3pt; }
"""

W = []; w = W.append
def box(kind, title, body): return f'<div class="box {kind}"><div class="bt">{title}</div>{body}</div>'
def say(t): return box('say', 'Say it', f'<p><mark>{t}</mark></p>')
def trap(t): return box('trap', 'Trap', f'<p>{t}</p>')
def why(t): return box('why', 'Why we did it this way', t if t.startswith('<') else f'<p>{t}</p>')
def idea(title, t): return box('idea', title, t if t.startswith('<') else f'<p>{t}</p>')
def ar(t): return box('ar', 'بالعربي', f'<p>{t}</p>')
def qa(pairs, title='If they ask'): return box('ask', title, ''.join(f'<p class="qq">{q}</p><p class="aa">{a}</p>' for q, a in pairs))
def cols(pairs): return '<dl class="cols">' + ''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in pairs) + '</dl>'
def fig(name, cap, wd=100): return f'<figure><img src="file://{FIG}/{name}.png" style="width:{wd}%"><figcaption>{cap}</figcaption></figure>'
def calc(t): return f'<div class="calc">{t}</div>'
def tbl(head, rows, cls='', hi=()):
    h = f'<table class="{cls}"><tr>' + ''.join(f'<th>{x}</th>' for x in head) + '</tr>'
    for r in rows:
        r = [str(x) for x in r]
        if len(r) > 1 and all(x == '' for x in r[1:]):
            h += f'<tr class="grp"><td colspan="{len(head)}">{r[0]}</td></tr>'; continue
        c = ' class="hi"' if any(k == r[0] or k in r[0] for k in hi) else ''
        h += f'<tr{c}>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>'
    return h + '</table>'

w(f'<!doctype html><html><head><meta charset="utf-8"><title>The Complete Research Guide</title><style>{CSS}</style></head><body>')

# =====================================================================================================  COVER
w('''<div style="margin-top:30mm"><p class="lead" style="letter-spacing:.12em;text-transform:uppercase;font-size:10pt;color:#b4541c">Student 2 · Defence preparation</p>
<h1>The Complete Research Guide</h1>
<p class="lead">Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad: An Online Cross-Sectional Survey</p>
<p style="margin-top:9mm">This guide goes through the whole thesis, from the title page to the last reference. It assumes you know your subject and your data, but <b>nothing about research methods or statistics</b>. For every part it explains <b>what it says, why it is there, and why we did it this way and not another way</b>, because the committee can ask about anything.</p>
<h3>How to read it</h3>
<ul><li><mark>Yellow highlight</mark> = must know. If you only read the yellow, you can answer most questions.</li>
<li><b>Blue “Why”</b> boxes explain each decision. <b>Purple “If they ask”</b> boxes give model answers. <b>Red “Trap”</b> boxes are mistakes to avoid. <b>Green “Say it”</b> boxes are sentences to say.</li>
<li><b>بالعربي</b> boxes explain the hardest ideas in Arabic.</li></ul>
<h3>Contents</h3><ol class="toc">
<li>Part A · Research from zero: the 12 ideas you need first</li>
<li>Part B · The thesis, chapter by chapter (front pages, Abstract, Introduction, Methods, Results, Discussion, Conclusions, References, Appendix)</li>
<li>Part C · Every statistical test: what, why, why not the other one</li>
<li>Part D · 60 questions the committee may ask, with answers</li>
<li>Part E · One-page summary of every number</li></ol>
<p class="lead" style="margin-top:6mm">Reading time: about 4–5 hours in total. Part A first (45 min), then Part B with the thesis open beside you.</p></div>''')

w('<h2 class="page">The study on one page</h2>' + tbl(['', ''], [
    ['<b>Question</b>', 'Is health anxiety linked to cyberchondria in adults in Baghdad, what role do AI chatbots play, and are medical students more affected?'],
    ['<b>Design</b>', 'Analytical cross-sectional online survey (Google Form, Arabic and English), convenience and snowball sampling, <b>n = 300</b>, one response per Google account, no missing data.'],
    ['<b>Tools</b>', '<b>SHAI-14</b> for health anxiety (0–42; ≥ 18 = elevated) · <b>CSS-12</b> for cyberchondria (12–60; four dimensions) · our own questions on tools, motives and behaviour.'],
    ['<b>Hypotheses</b>', '<b>H1</b> more health anxiety → more cyberchondria, independently of other factors · <b>H2</b> medical students have more health anxiety and cyberchondria.'],
    ['<b>Analysis</b>', 'SPSS 26, p &lt; 0.05. Descriptives, Cronbach’s α, Shapiro–Wilk, Mann–Whitney, Kruskal–Wallis, χ²/Fisher, Pearson/Spearman, partial correlation, multiple linear regression, binary logistic regression.'],
    ['<b>Main results</b>', 'AI chatbots used by 88.7% · 19.0% elevated health anxiety · <mark>r = 0.47</mark> between the two scores · health anxiety adds 18.4% in regression (β = 0.48) · AI users higher cyberchondria (B = 5.33, p &lt; 0.001) · 34.7% delay care when reassured · 31.7% never tell the doctor.'],
    ['<b>Verdicts</b>', '<mark><b>H1 supported. H2 not supported</b></mark> (medical students’ higher health anxiety was explained by their younger age).'],
    ['<b>Message</b>', 'Ask every patient, without judgement, what they searched or asked an AI.']]))
w(fig('fig0a_framework_short', 'Figure 1 of the thesis: the conceptual framework. Learn to explain every arrow.', 86))
w(ar('بحثنا يدرس العلاقة بين القلق الصحي (الخوف من المرض) والسايبركوندريا (البحث المفرط والمقلق عن الأعراض في الإنترنت) عند 300 شخص بالغ في بغداد، مع التركيز على روبوتات الذكاء الاصطناعي وطلاب الطب. النتيجة الأساسية: كلما زاد القلق الصحي زادت السايبركوندريا (r = 0.47).'))

# =====================================================================================================  PART A
w('<div class="part"><h1>Part A</h1><p>Research from zero: the 12 ideas you need before anything else.</p></div>')

w('<h2 class="page">A1–A4 · What research is, and how a thesis is built</h2>')
w('<h3>A1. The parts of a research thesis (IMRaD)</h3>' + tbl(['Part', 'The question it answers', 'In our thesis'], [
    ['Introduction', 'Why does this matter, what is known, what is missing?', 'Chapter 1 (1.1–1.8)'],
    ['Methods', 'What exactly did you do, so someone could repeat it?', 'Chapter 2 (2.1–2.6)'],
    ['Results', 'What did you find? Facts and numbers only, no opinions', 'Chapter 3 (3.1–3.6)'],
    ['Discussion', 'What does it mean, how does it compare, what are the weaknesses?', 'Chapter 4 (4.1–4.6)'],
    ['Conclusions', 'The take-home messages and recommendations', 'Chapter 5']]) +
  trap('Results report; the Discussion interprets. Never explain “why” in the Results, and never introduce new numbers in the Discussion.'))
w('<h3>A2. Types of study design</h3>' + tbl(['Design', 'What it does', 'Can it show cause?'], [
    ['<b>Cross-sectional</b> (ours)', 'Measures everything <b>once</b>, at one point in time, in one group', 'No: shows associations only'],
    ['Case–control', 'Starts from people with and without a disease and looks back for causes', 'Weakly'],
    ['Cohort (longitudinal)', 'Follows the same people over time', 'Better: shows what comes first'],
    ['Randomised controlled trial', 'Randomly gives an intervention to some people', 'Yes: the strongest']]) +
  why('<p>A cross-sectional survey was the only realistic design: we wanted to measure how common something is and how two things relate, in a few months, without money or a clinic. “Analytical” means we did not only describe, we also tested relationships (hypotheses).</p>') +
  ar('الدراسة المقطعية (cross-sectional) تقيس كل شيء مرة واحدة. لذلك تُظهر العلاقة بين المتغيرات لكن لا تثبت السبب والنتيجة. هذا أهم قيد في بحثنا.'))
w('<h3>A3. Population, sample and sampling</h3>' + cols([
    ('Population', 'everyone we want to talk about: adults in Baghdad who search for health information online.'),
    ('Sample', 'the 300 people who actually answered.'),
    ('Probability sampling', 'everyone has a known chance of being chosen (random). The results can be generalised. Needs a list of the whole population.'),
    ('<b>Convenience sampling</b> (ours)', 'whoever is easy to reach (our social-media and messaging groups).'),
    ('<b>Snowball sampling</b> (ours)', 'participants pass the link to others.')]) +
  why('There is no list of all Baghdad adults who search online, so random sampling was impossible. Convenience and snowball sampling are standard for online student surveys. The price: <mark>percentages cannot be generalised to all of Baghdad</mark>, although associations (like r = 0.47) are still informative.'))
w('<h3>A4. Variables</h3>' + tbl(['Type', 'Meaning', 'Our examples', 'Described with'], [
    ['<b>Categorical</b>', 'groups or yes/no', 'gender, AI user, medical student, elevated health anxiety', 'n and %'],
    ['<b>Continuous</b>', 'a score or measurement', 'SHAI-14 (0–42), CSS-12 (12–60)', 'mean ± SD or median (IQR)'],
    ['Ordinal', 'ordered categories', 'age group, trust 1–5', 'n and %, median'],
    ['<b>Dependent (outcome)</b>', 'what we explain', 'CSS-12 score; elevated health anxiety', ''],
    ['<b>Independent (predictor)</b>', 'what we use to explain it', 'SHAI-14, AI use, age…', ''],
    ['<b>Confounder</b>', 'a third variable linked to both, which can create a false link', 'age (for medical students)', '']]) +
  idea('Why this matters', '<mark>The type of variable decides the test.</mark> Score vs groups → Mann–Whitney/Kruskal–Wallis; category vs category → χ²; score vs score → correlation; many predictors → regression.'))

w('<h2 class="page">A5–A12 · The statistical ideas behind every number</h2>')
w('<h3>A5. Hypotheses and the null hypothesis</h3><p>A hypothesis is a prediction you test. Statistics always tests the opposite, the <b>null hypothesis (H0)</b>: “there is no link / no difference”. If the data are very unlikely under H0, we reject it and accept our hypothesis.</p>' +
  calc('H1 (ours):  more health anxiety → more cyberchondria\nH0:         no relationship between health anxiety and cyberchondria\nResult:     r = 0.47, p < 0.001 → reject H0 → H1 supported'))
w('<h3>A6. The p-value</h3><p>If there were really no effect, the p-value is the chance of seeing a result at least this strong by luck. <mark>p &lt; 0.05 = significant</mark> (less than 5% chance of luck). It does <b>not</b> tell you how big or important the effect is.</p>')
w('<h3>A7. The 95% confidence interval (CI)</h3><p>The range where the true value probably lies. Narrow = precise. <mark>For a difference or B: if the CI includes 0 → not significant. For an odds ratio: if it includes 1 → not significant.</mark></p>')
w('<h3>A8. Effect size</h3><p>How big the effect is: r (0.1 small, 0.3 medium, 0.5 large), Cramér’s V (same), R² (share explained), odds ratio (1 = none). A good thesis reports both the p-value and the effect size.</p>')
w('<h3>A9. Normal distribution, parametric and non-parametric tests</h3><p>Many tests (t-test, ANOVA) assume scores form a symmetric bell curve. The <b>Shapiro–Wilk test</b> checks this. Ours were <b>not normal</b>, so we used <b>non-parametric</b> tests, which compare ranks instead of means, and describe groups with <b>medians</b>.</p>' +
  ar('التوزيع الطبيعي هو شكل الجرس. درجاتنا لم تكن طبيعية، لذلك استخدمنا اختبارات لا معلمية (Mann–Whitney و Kruskal–Wallis) التي تعتمد على ترتيب القيم بدل المتوسطات.'))
w('<h3>A10. Reliability and validity</h3>' + cols([
    ('Reliability', 'does the scale measure <b>consistently</b>? Checked with <b>Cronbach’s α</b> (≥ 0.7 acceptable, ≥ 0.8 good).'),
    ('Validity', 'does it measure <b>what it claims</b>? We used scales already validated in other studies (SHAI-14, CSS-12).'),
    ('Our values', '<mark>SHAI-14 α = 0.81, CSS-12 α = 0.86; the same in Arabic (0.81, 0.86) and English (0.81, 0.88)</mark>.')]))
w('<h3>A11. Adjusted versus unadjusted, and confounding</h3><p>An <b>unadjusted</b> result looks at one variable alone. An <b>adjusted</b> result (regression) holds other variables constant. A difference can disappear after adjustment if a confounder explains it: <mark>medical students had higher health anxiety only because they were younger</mark> (H2).</p>')
w('<h3>A12. Bias and limitations</h3>' + tbl(['Bias', 'What it means', 'In our study'], [
    ['Selection bias', 'the sample differs from the population', 'online convenience sample, many medical students'],
    ['Self-report / recall bias', 'people misremember or answer as they think they should', 'all answers self-reported'],
    ['Social-desirability bias', 'answering to look good', 'possible for disclosure to the doctor'],
    ['Confounding', 'a third variable creates a false link', 'handled by adjustment (regression)'],
    ['Reverse causation', 'B causes A, not A causes B', 'cross-sectional design cannot exclude it']]))

# =====================================================================================================  PART B
w('<div class="part"><h1>Part B</h1><p>The thesis, chapter by chapter, from the title page to the questionnaire.</p></div>')

w('<h2 class="page">B1 · Front pages and Abstract</h2>')
w(tbl(['Page', 'What it is', 'Why it is there'], [
    ['Title page', 'title, university, students, supervisor, degree', 'identifies the work; the title names the variables (health anxiety, AI chatbot use, cyberchondria), the population (adults in Baghdad) and the design (online cross-sectional survey)'],
    ['Acknowledgment', 'thanks to the supervisor, department and participants', 'courtesy'],
    ['Contents, lists of tables and figures, abbreviations', 'navigation', 'required by the college format'],
    ['Abstract', 'the whole study in about 300 words', 'most readers read only this']]))
w('<h3>The structured Abstract</h3><p>Ours uses the standard medical format: <b>Background · Objectives · Methods · Results · Conclusion · Keywords</b>. Each heading is one or two sentences. Numbers in the Abstract must match the Results exactly.</p>' +
  why('A structured abstract is the format of medical journals and most college guidelines; it lets a reader find the design and main result in seconds. Keywords (cyberchondria; health anxiety; artificial intelligence; chatbots; Iraq) help indexing.') +
  qa([('Why is the title so long?', 'It contains the three variables, the population and the design, which is what a reader needs to judge the study at a glance.')]))

w('<h2 class="page">B2 · Chapter 1: Introduction</h2><p>The Introduction moves from general to specific, like a funnel: the problem → what is known → what is missing (the gap) → what we will do (aim and hypotheses).</p>')
w(tbl(['Section', 'What it says', 'Why it is there', 'Key references'], [
    ['1.1 Background', 'People look up symptoms online and increasingly ask AI chatbots before seeing a doctor; for some, searching makes worry worse (cyberchondria). About 4 in 5 Iraqis are online; no study from Baghdad.', 'sets the problem and the local relevance', 'White & Horvitz 2009 [1]; Starcevic & Berle 2013 [2]; DataReportal 2025 [3]'],
    ['1.2 Health anxiety', 'Definition; a spectrum from mild worry to illness anxiety disorder (DSM-5-TR); the cognitive model (misreading bodily sensations, kept going by checking and reassurance); prevalence ~6% general, up to 20% in outpatients; 49.5% in an Iraqi COVID survey.', 'defines the first variable and shows it is common', 'APA DSM-5-TR [4]; Salkovskis & Warwick 1986 [5]; Tyrer 2018 [6]; Karim 2020 [7]'],
    ['1.3 Cyberchondria', 'Searches escalate from harmless to serious diagnoses; definition (searching that increases distress); the CSS-12 short form and its Arabic version.', 'defines the second variable and the tool', 'White & Horvitz [1]; Starcevic & Berle [2]; McElroy 2019 [8]; Hallit 2023 [9]'],
    ['1.4 Health anxiety and cyberchondria', 'Related but distinct; an experiment showed searching raises anxiety; two meta-analyses r = 0.62–0.63; a Dutch panel found a two-way relationship.', 'shows what is already known about the link (H1)', 'Mathes 2018 [10]; Jungmann 2020 [11]; McMullan 2019 [12]; Schenkel 2021 [13]; te Poel 2016 [14]'],
    ['1.5 Search engines to AI chatbots', 'Chatbots answer fluently and can seem more empathetic than doctors; ~1 in 5 Americans used ChatGPT for health.', 'explains why AI is new and worth studying', 'Ayers 2023 [15]; Ayo-Ajibola 2024 [16]'],
    ['1.6 Searching and the doctor–patient relationship', 'Discussing searches helps the relationship, hiding them strains it; Arab-region data (Jeddah, Saudi, 13 countries); and (moved here by the supervisor) the medical-student studies.', 'links searching to clinical practice and to H2', 'Luo 2022 [17]; El-Zayat 2023 [18]; Pasay-An 2025 [19]; Dahshan 2026 [20]; El-Zoghby 2024 [21]; Fasfoos 2026 [22]'],
    ['1.7 Rationale', 'Three gaps: first estimate in Baghdad; AI separately from search engines; whether medical students are more prone (“medical student syndrome”).', 'justifies why the study was needed', '—'],
    ['1.8 Aim, objectives, hypotheses', 'Aim; 3 objectives; H1 and H2; Figure 1 framework.', 'states exactly what will be tested', '—']], 'sm'))
w(idea('Box 1', '<p>Box 1 separates four terms that overlap: <b>health anxiety</b> (a dimension, screened), <b>illness anxiety disorder</b> (a DSM-5-TR diagnosis, not assessed), <b>cyberchondria</b> (a behavioural pattern, measured with the CSS-12) and <b>ordinary health searching</b> (normal behaviour). It answers the question “is cyberchondria a disease?” (no: it is a pattern, not a diagnosis).</p>'))
w('<h3>Aim, objectives and hypotheses</h3>' + cols([
    ('Aim', 'to study the relationship between health anxiety and cyberchondria among adults in Baghdad who search online, with a focus on AI chatbots and medical students.'),
    ('Objective 1', 'describe where people look for health information and what they do after searching.'),
    ('Objective 2', 'estimate levels of health anxiety and cyberchondria and the strength of their association, independently of other factors (H1).'),
    ('Objective 3', 'compare medical students with other participants (H2).'),
    ('H1 (primary)', '<mark>people with more health anxiety have more cyberchondria, independently of socio-demographic and digital-use factors.</mark>'),
    ('H2 (secondary)', '<mark>medical students have higher health anxiety and cyberchondria than other participants.</mark>')]) +
  why('Aim = the general purpose. Objectives = the concrete steps. Hypotheses = testable predictions. H1 comes from the literature (meta-analyses found a strong link); H2 comes from the idea of “medical student syndrome”. Writing hypotheses makes the study analytical, not just descriptive.') +
  qa([('Why only two hypotheses?', 'They are the two questions our data can test properly. Description (Objective 1) needs no hypothesis.'),
      ('Is cyberchondria a disease?', 'No. It is a behavioural pattern measured on a scale, not a diagnosis. Box 1 explains the difference.'),
      ('What is the gap your study fills?', 'No study from Baghdad, almost none on AI chatbots separately from search engines, and mixed evidence on medical students.')]))

w('<h2 class="page">B3 · Chapter 2: Methods</h2>')
w('<h3>2.1 Design, setting and participants</h3>' + cols([
    ('Design', 'analytical cross-sectional online survey (see A2).'),
    ('Reporting guidelines', '<b>STROBE</b> [23] (for observational studies) and <b>CHERRIES</b> [24] (for internet surveys): checklists of what to report so the study can be judged and repeated.'),
    ('Sampling', 'convenience and snowball through Baghdad-based social-media and messaging groups (see A3).'),
    ('Eligibility', 'adults ≥ 18, able to read Arabic or English, gave consent.'),
    ('Duplicates', 'one response per Google account; no duplicate patterns; all submissions analysed (n = 300).')]) +
  qa([('Why online and not face to face?', 'Faster, cheaper, anonymous (people answer more honestly about anxiety), and the target group is people who search online anyway.'),
      ('Why STROBE and CHERRIES?', 'They are the international checklists for observational and web surveys; following them shows we reported everything needed.')]))
w('<h3>2.2 Sample size</h3>' + calc('To detect r = 0.20 with α = 0.05 (two-sided) and 80% power  →  194 participants (Fisher’s z method)\nWe had 300  →  enough. Margin of error for a percentage with n = 300: about ±5.7%') +
  why('We planned for a small correlation (0.20) to be safe; meta-analyses found 0.62, which needs far fewer people. <b>Power</b> = the chance of detecting a real effect (80% is the standard). <b>α</b> = the chance of a false positive we accept (5%).') +
  ar('حجم العينة المطلوب كان 194 شخصاً لاكتشاف علاقة صغيرة (0.20)، ونحن جمعنا 300، أي أكثر من الكافي.'))
w('<h3>2.3 The questionnaire</h3>' + tbl(['Part', 'Content'], [
    ['1', 'Consent and socio-demographic data (age, gender, education, study/work, chronic condition)'],
    ['2', 'Digital health-information seeking: tools (Q8), main AI chatbot (Q9), motives, trust (1–5)'],
    ['3', '<b>SHAI-14</b>: 14 items, each 0–3, total 0–42 [26]; validated [27,28]'],
    ['4', '<b>CSS-12</b>: 12 items, each 1–5, total 12–60, four 3-item dimensions [8]'],
    ['5', 'Behaviour after searching, telling the doctor, effect on the relationship']]) +
  why('<ul><li><b>Why the SHAI-14?</b> Short, widely used, good reliability, and it has a published cut-off (≥ 18) to identify elevated health anxiety.</li><li><b>Why the CSS-12?</b> The short form of the 33-item CSS: much quicker but keeps all four dimensions (excessiveness, compulsion, distress, reassurance seeking).</li><li><b>Why bilingual?</b> Many young Iraqis, especially medical students, read English; offering both increases participation.</li><li><b>Limitation:</b> the team prepared the Arabic wording without formal back-translation [29]; published Arabic versions were not used [9,30]. α was the same in both languages, which supports the Arabic version.</li></ul>') +
  qa([('What is back-translation?', 'Translating the Arabic version back into English by a second translator and comparing, to check the meaning is the same. We did not do it; that is a limitation.'),
      ('Why not the 33-item CSS?', 'Too long for an online survey (people drop out); the CSS-12 is validated and keeps the four dimensions.')]))
w('<h3>2.4 Definitions</h3>' + tbl(['Term', 'Definition', 'Why'], [
    ['<b>Elevated health anxiety</b>', 'SHAI-14 ≥ 18', 'best cut-off against healthy controls in the Swedish validation study [28]; a screening result, not a diagnosis'],
    ['<b>High cyberchondria</b>', 'CSS-12 &gt; 33 (upper third)', 'the CSS-12 has no validated cut-off, so the upper tertile is used'],
    ['<b>AI-chatbot user</b>', 'ticked “AI chatbots” in Q8 <b>or</b> named a chatbot in Q9 (n = 266)', '<mark>32 people named ChatGPT/Gemini without ticking the box; naming one shows they use it, so they count as users</mark>'],
    ['Health-related background', 'medical, other health-science students and health workers', 'to test whether medical knowledge matters'],
    ['Recoding', '40–49, 50–59, 60+ merged into ≥ 40; free-text “Other” answers put in the closest category', 'groups too small to analyse separately']]) +
  trap('If the thesis text still describes a “strict definition” that moves the 32 into the non-user group, update it to match this guide: all AI analyses count the 32 as AI users.'))
w('<h3>2.5 Statistical analysis</h3><p>Part C explains every test in detail. In one line each:</p>' + tbl(['Purpose', 'Test', 'Why this one'], [
    ['Describe', 'n (%), mean ± SD, median (IQR), 95% CI', 'categorical vs continuous variables'],
    ['Reliability', 'Cronbach’s α (full sample and each language)', 'standard internal-consistency measure in SPSS'],
    ['Normality', 'Shapiro–Wilk', 'most powerful normality test for n = 300'],
    ['Score in 2 groups', 'Mann–Whitney U', 'scores not normal (instead of t-test)'],
    ['Score in 3+ groups', 'Kruskal–Wallis H (+ pairwise post-hoc)', 'scores not normal (instead of ANOVA)'],
    ['Category × category', 'χ² or Fisher’s exact, Cramér’s V', 'Fisher when expected counts &lt; 5'],
    ['Score × score', 'Pearson r (Fisher-z CI), Spearman ρ, partial r', 'Spearman confirms Pearson without normality'],
    ['Many predictors of a score', 'hierarchical multiple linear regression', 'outcome is a score; blocks show what each group adds'],
    ['Many predictors of yes/no', 'binary logistic regression', 'outcome is yes/no'],
    ['Medical students (H2)', 'Mann–Whitney, χ², then regression adjusted for age, gender, chronic disease, language', 'to remove confounding by age']], 'sm') +
  qa([('Which software?', 'IBM SPSS Statistics version 26, two-sided p &lt; 0.05.'),
      ('Why didn’t you correct for multiple testing?', 'Like most graduation theses we used p &lt; 0.05; we state it as a limitation. The main results have p &lt; 0.001.')]))
w('<h3>2.6 Ethical considerations</h3><p>Anonymous online survey of consenting adults, outside any hospital, no intervention, no medical records. The first page explained the study; electronic consent (and age ≥ 18) was required before any question; no names, e-mails or contact details were collected.</p>' +
  qa([('Why didn’t you need ethics committee approval?', 'The supervisor confirmed it was not required for an anonymous, voluntary online survey of adults with no intervention and no patient records.'),
      ('How did you protect participants?', 'Informed consent first, anonymity (no identifying data), voluntary participation, and they could stop at any time.')]))

# ---------------------------------------------------------------------------------------------- RESULTS
w('<h2 class="page">B4 · Chapter 3: Results</h2><p>The Results go from simple to complex: describe the sample → levels of the two scores → the main link → group differences → all factors together → medical students.</p>')
w('<h3>3.1 Participants and online searching (Tables 1–2, Figures 2–3)</h3>' + tbl(['Characteristic', 'Result'], [
    ['Age', '62.3% aged 20–29; 18.7% aged 18–19'], ['Gender', '56.3% female'], ['Study/work', '<mark>44.0% medical students</mark>; 63.3% health-related background'],
    ['Chronic condition', '21.7%'], ['Language', '70.7% Arabic, 29.3% English'],
    ['Tools', '<mark>AI chatbots 88.7%</mark> (78.0% ticked the box), search engines 56.3%, medical platforms 18.3%, social media 10.7%'],
    ['Main chatbot', 'ChatGPT 59.3%, Gemini 23.7%'], ['Motives', 'convenience 80.0%, “do I need a doctor?” 57.7%, instant reassurance 51.0%'],
    ['After searching', '<mark>34.7% delayed/skipped care because reassured</mark>; 30.0% ignored the symptom; 25.3% several doctors; 22.0% urgent care'],
    ['Telling the doctor', 'always 27.0%, sometimes 41.3%, <mark>never 31.7%</mark> (fear of judgement)'], ['Relationship', '34.7% said searching complicated it or reduced trust']]))
w(fig('fig2_tools_motives', 'Figure 2: tools used and motives (multiple answers, so bars add to more than 100%).', 90) + fig('fig3_behaviours', 'Figure 3: behaviour after searching, disclosure, and effect on the relationship.', 96))
w(say('Our sample was young, almost half medical students. AI chatbots were the most used source, 88.7%. After searching, one in three delayed care because they felt reassured, and almost one in three never told their doctor.'))
w('<h3 class="page">3.2 Levels of health anxiety and cyberchondria (Tables 3–4)</h3>' + tbl(['Scale', 'Mean ± SD', 'Median (IQR)', 'Range', 'α (all / Arabic / English)'], [
    ['SHAI-14 (0–42)', '12.35 ± 5.83', '12 (8–16)', '1–30', '0.81 / 0.81 / 0.81'], ['CSS-12 (12–60)', '28.86 ± 8.36', '29 (23–34)', '12–57', '0.86 / 0.86 / 0.88'],
    ['Excessiveness', '9.66 ± 2.94', '10 (8–12)', '3–15', '0.77'], ['Compulsion', '5.00 ± 2.58', '4 (3–6)', '3–15', '0.88'],
    ['Distress', '7.24 ± 2.74', '7 (5–9)', '3–15', '0.76'], ['Reassurance', '6.96 ± 2.81', '7 (5–9)', '3–15', '0.76']], hi=('SHAI-14', 'CSS-12')) +
  tbl(['SHAI-14 cut-off', 'n', '%', '95% CI'], [['≥ 18 (our definition)', 57, '<mark>19.0</mark>', '15.0–23.8'], ['≥ 22', 22, '7.3', '4.9–10.9'], ['≥ 29', 2, '0.7', '0.2–2.4']]) +
  cols([('Excessiveness highest', 'people search a lot'), ('Compulsion lowest', 'but searching rarely disrupts daily life (median 4 of 3–15)'), ('Wilson 95% CI', 'the true prevalence is probably 15–24%')]) +
  say('About one in five, 19.0%, scored in the elevated range of health anxiety, a screening result, not a diagnosis. Both scales were reliable, α 0.81 and 0.86, equally in Arabic and English.') +
  trap('Never say “19% have health anxiety disorder”. The SHAI-14 is a screening questionnaire; a diagnosis needs a clinical interview.'))
w('<h3>3.3 The main association (Table 5, Figure 4): H1</h3>' + tbl(['Measure', 'Pearson r (95% CI)', 'Spearman ρ', 'Adjusted β'], [
    ['<b>CSS-12 total</b>', '<mark>0.47 (0.38–0.55)</mark>', '0.47', '0.48'], ['Excessiveness', '0.46 (0.37–0.55)', '0.45', '0.44'], ['Compulsion', '0.25 (0.14–0.36)', '0.32', '0.29'],
    ['Distress', '0.45 (0.36–0.54)', '0.44', '0.44'], ['Reassurance', '0.24 (0.13–0.35)', '0.23', '0.25']]) +
  calc('r = 0.47  → moderate, close to large\nr² = 0.47 × 0.47 = 0.22  → health anxiety accounts for about 22% of the differences in cyberchondria\nPartial r = 0.48 after removing age, sex, health background, chronic disease, trust and AI use → unchanged (H1: “independently”)') +
  fig('fig1_scatter_shai_css', 'Figure 4: each dot is one participant; the line rises: more health anxiety, more cyberchondria (CSS ≈ 20.5 + 0.67 × SHAI).', 58) +
  say('Health anxiety and cyberchondria rise together, r = 0.47, and the link is the same after adjusting for other factors. It is strongest for excessive searching and distress after searching. H1 is supported.') +
  trap('Say “associated with”, never “causes”. A cross-sectional study cannot show which comes first.'))
w('<h3 class="page">3.4 Which groups differ (Tables 6–7, Figure 5)</h3><p>Each variable was tested with <b>one overall test</b>: Mann–Whitney for 2 groups, Kruskal–Wallis for 3 or more. Groups are described with <b>median (IQR)</b>, which matches these rank tests.</p>')
rows6 = MED['t6']
w(tbl(['Group', 'n', 'SHAI-14 median (IQR)', 'CSS-12 median (IQR)'], rows6, 'sm', hi=('Medical student', 'Yes')))
w(tbl(['Variable', 'SHAI p', 'CSS p', 'Plain meaning'], [
    ['Chronic condition', '<mark>0.004</mark>', '0.435', 'more health anxiety (median 14 vs 11), same searching'],
    ['Motive: instant reassurance', '<mark>&lt; 0.001</mark>', '0.085', 'reassurance seekers more anxious (13 vs 10)'],
    ['Social media', '0.001', '0.021', 'higher on both'],
    ['AI chatbots', '0.008', '<mark>&lt; 0.001</mark>', 'AI users higher cyberchondria (median 30 vs 23.5)'],
    ['Tool profile', '0.006', '&lt; 0.001', 'AI + search highest (31), no AI lowest (23.5)'],
    ['Age / education / study-work', '0.008 / 0.002 / 0.005', 'ns', 'young students more health-anxious'], ['Gender, language', 'ns', 'ns', 'no difference']]))
w(idea('Post-hoc: which groups differ?', '<p>Kruskal–Wallis only says the groups are not all the same. Pairwise Mann–Whitney tests with Bonferroni correction show: <b>18–19 vs 30–39</b> (p = 0.026), <b>current students vs bachelor graduates</b> (p = 0.032), <b>medical students vs non-health employees</b> (p = 0.004). All point to the same thing: <mark>younger students are more health-anxious</mark>.</p>'))
w(fig('fig6_css_by_tool', 'Figure 5: cyberchondria by tool profile (box = middle half of people, line = median).', 50))
w('<h4>Table 7 · Yes/no outcomes (χ² or Fisher)</h4>' + calc('High cyberchondria with elevated health anxiety:  30/57 = 52.6%\nwithout:                                          56/243 = 23.0%\nOdds ratio = (30/27) / (56/187) = 1.11 / 0.30 = 3.71 (95% CI 2.04–6.76), χ² p < 0.001, Cramér’s V = 0.26') +
  '<p>Also significant: elevated health anxiety more common in reassurance seekers (27.5% vs 10.2%) and social-media users (40.6% vs 16.4%); high cyberchondria more common in AI users (31.2% vs 8.8%, p = 0.007) and in people who always tell their doctor (40.7% vs 15.8% of those who never do).</p>')
w('<h3 class="page">3.5 Independent predictors (Tables 8–9, Figure 6)</h3><h4>Table 8 · Hierarchical multiple linear regression of CSS-12</h4>' + tbl(['Block entered', 'R²', 'Added', 'p'], [
    ['1 · Socio-demographics', '0.030', '3%', '0.53'], ['2 · + Digital use (tools, trust, motives)', '0.133', '+10%', '&lt; 0.001'], ['3 · + Health anxiety', '<mark>0.317</mark>', '<mark>+18.4%</mark>', '&lt; 0.001']]) +
  tbl(['Key predictor in the final model', 'B (95% CI)', 'β', 'p'], [
    ['Health anxiety (per SHAI point)', '<mark>0.68 (0.53–0.84)</mark>', '<mark>0.48</mark>', '&lt; 0.001'], ['<b>AI chatbot user</b>', '<mark>5.33 (2.57–8.09)</mark>', '0.20', '<mark>&lt; 0.001</mark>'],
    ['Age 30–39 (vs 20–29)', '6.27 (2.42–10.11)', '0.19', '0.001'], ['Age ≥ 40', '3.98 (0.16–7.80)', '0.15', '0.041'], ['All others (gender, job, chronic, language, trust, motives)', 'CIs include 0', '', 'ns']]) +
  cols([('B', 'change in CSS points per unit: each SHAI point adds 0.68; AI users score 5.3 points higher'), ('β', 'standardised B, to compare predictors: health anxiety (0.48) is by far the strongest'), ('R² 0.317', 'the model explains 32% of the differences in cyberchondria'), ('Hierarchical', 'blocks in order show health anxiety adds 18.4% even after everything else')]) +
  idea('Why age matters here but not in Table 6', '<p>Older people had <b>lower</b> health anxiety but the <b>same</b> cyberchondria. Once health anxiety is held constant, their searching is relatively higher. That is what adjustment does.</p>'))
w('<h4>Table 9 · Binary logistic regression of elevated health anxiety (57 events)</h4>' + tbl(['Predictor', 'AOR (95% CI)', 'p', 'Meaning'], [
    ['Cyberchondria (per 1 SD = 8.4 points)', '<mark>3.12 (2.11–4.62)</mark>', '&lt; 0.001', 'odds triple per SD'], ['Motive: instant reassurance', '<mark>3.83 (1.80–8.18)</mark>', '&lt; 0.001', 'odds almost ×4'],
    ['Age group (per step older)', '<mark>0.61 (0.39–0.93)</mark>', '0.023', 'protective: 39% lower odds per step'], ['All others', 'CIs include 1', 'ns', '']]) +
  calc('Model checks: omnibus χ²(11) = 64.9, p < 0.001 · Nagelkerke R² = 0.31 · Hosmer–Lemeshow p = 0.50 (good fit)\nAUC = 0.83 (good discrimination) · 81% correctly classified (but 81% had no elevated anxiety, so quote the AUC)') +
  fig('fig7_forest_HA_simple', 'Figure 6: forest plot of Table 9. Dot = AOR, line = 95% CI, vertical line at 1 = no effect, orange = significant.', 62) +
  say('Health anxiety is by far the strongest predictor of cyberchondria, adding 18.4%. AI chatbot users scored 5.3 points higher, independently of health anxiety. Elevated health anxiety was linked to higher cyberchondria, searching for reassurance, and younger age.') +
  qa([('Why logistic and not linear regression for Table 9?', 'The outcome (elevated health anxiety) is yes/no; linear regression would predict impossible values below 0 or above 1.'),
      ('Why are the odds ratios wide?', 'Only 57 events for 11 predictors, about 5 per predictor (10 is recommended), so estimates are imprecise and may be overestimated. We say so.'),
      ('The 32 who named a chatbot without ticking it?', 'They were counted as AI users, because naming ChatGPT or Gemini shows they use it. Most ticked a search engine and named a chatbot.')]))
w('<h3 class="page">3.6 Medical students compared with others (Table 10): H2</h3>' + tbl(['Measure', 'Medical students (132)', 'Others (168)', 'p', 'Adjusted', 'Adj. p'], [
    ['SHAI-14 median (IQR)', MED['t10']['SHAI'][0], MED['t10']['SHAI'][1], '<mark>0.004</mark>', 'B 1.23 (−0.15–2.60)', '<mark>0.081</mark>'],
    ['Elevated health anxiety', '23.5%', '15.5%', '0.079', 'AOR 1.44 (0.79–2.65)', '0.238'],
    ['CSS-12 median (IQR)', MED['t10']['CSS'][0], MED['t10']['CSS'][1], '0.989', 'B 0.50 (−1.54–2.54)', '0.627'],
    ['High cyberchondria', '28.0%', '29.2%', '0.829', 'AOR 1.08 (0.63–1.87)', '0.771']]) +
  idea('The key lesson', '<p>Before adjustment medical students looked more anxious. After adjusting for age, gender, chronic disease and language, the difference was <b>no longer significant</b>: medical students are younger, and younger people were more anxious. <mark>Age, not medicine, explained the difference. H2 not supported.</mark></p>') +
  ar('طلاب الطب ظهر عندهم قلق صحي أعلى في البداية، لكن بعد ضبط العمر اختفى الفرق، لأنهم أصغر سناً والأصغر سناً عندهم قلق أعلى. لذلك الفرضية الثانية غير مدعومة.'))

# ---------------------------------------------------------------------------------------------- DISCUSSION
w('<h2 class="page">B5 · Chapter 4: Discussion</h2><p>The Discussion interprets the results, compares them with other studies, and admits the weaknesses.</p>')
w(tbl(['Section', 'What it says', 'What to remember'], [
    ['4.1 Health anxiety and cyberchondria', 'First CSS-12 study in Baghdad; moderate link (r = 0.47) independent of covariates; strongest for excessiveness and distress; 19% elevated is a screening estimate (0.7–19% across published cut-offs).', '<mark>H1 supported</mark>; fits the cognitive model'],
    ['4.2 Worldwide and regional comparison', 'Our r (0.47) is weaker than meta-analyses (0.62–0.63): low and narrow health anxiety, confident internet users, the short CSS-12. AI use (88.7%) far higher than US surveys (~20%, 21%), because our sample is young. Iraq COVID survey (49.5%, different tool). Agrees with Jeddah, Saudi, Lebanon, Egypt.', 'why our numbers differ'],
    ['4.3 AI chatbots', 'AI users had higher cyberchondria independently of health anxiety (B = 5.33). Chatbots can be questioned again and again, which may encourage repeated searching and reassurance seeking; the non-user group was small (34); AI answers may give false reassurance.', '<mark>AI linked to cyberchondria</mark>, needs confirmation'],
    ['4.4 Medical students', 'H2 not supported: higher anxiety only before adjusting for age; cyberchondria identical. Agrees with Palestine (least common in medical students), differs from Egypt (no comparison group).', 'no “medical student syndrome”'],
    ['4.5 Searching and the consultation', 'Reassured delay (34.7%) may save visits but risks late diagnosis; almost a third hide searches, fearing judgement; open discussion strengthens the relationship. Described, not tested.', 'clinical relevance'],
    ['4.6 Strengths and limitations', 'Strengths: validated reliable scales, bilingual, AI studied separately, complete data, adjusted models. Limitations below.', 'know every limitation']], 'sm'))
w('<h3>Limitations: and how to answer each</h3>' + tbl(['Limitation', 'Why it matters', 'Your answer'], [
    ['Cross-sectional design', 'cannot show which comes first', 'we report associations only; longitudinal studies are recommended'],
    ['Convenience online sample, 44% medical students', 'percentages not generalisable', 'associations are still informative; being a medical student did not change scores after adjustment'],
    ['No back-translation of the Arabic wording', 'meaning may differ', 'α was identical in Arabic and English (0.81; 0.86/0.88)'],
    ['Self-report', 'recall and social-desirability bias', 'anonymous survey reduces it'],
    ['Single, non-validated items for behaviour, trust, disclosure', 'less precise', 'reported descriptively'],
    ['Many tests, no correction', 'some results may be chance', 'main results p &lt; 0.001'],
    ['Small non-AI group (34), 57 events in logistic model', 'imprecise estimates', 'stated in the thesis; findings need confirmation']], 'sm'))
w('<h2 class="page">B6 · Chapter 5: Conclusions and Recommendations</h2>' + tbl(['Conclusion', 'Evidence'], [
    ['1. AI chatbots, mainly ChatGPT, are a leading source of health information', '88.7% used them'],
    ['2. About one in five have elevated health anxiety on a screening threshold', '19.0%; younger people and reassurance seekers most affected'],
    ['3. <mark>Health anxiety and cyberchondria are moderately associated, independently of other factors</mark>', 'r = 0.47; partial r = 0.48; regression +18.4%'],
    ['4. AI use is associated with higher cyberchondria', 'B = 5.33, p &lt; 0.001 (update the thesis wording to match)'],
    ['5. Medical students are not at higher risk once age is considered', 'adjusted p = 0.081 and 0.627'],
    ['6. Searching shapes the consultation', '34.7% delay when reassured; 31.7% never tell the doctor']]) +
  tbl(['Recommendation for', 'What'], [
    ['Clinicians', 'ask patients without judgement what they searched or asked an AI and what they found; treat repeated searching and reassurance seeking as possible signs of health anxiety; teach digital and AI health literacy in medical school'],
    ['Ministry of Health', 'Arabic digital and AI health-literacy campaigns; reliable Arabic triage sources'],
    ['AI developers', 'anxiety-aware answers that avoid escalating to rare diagnoses and encourage appropriate consultation'],
    ['Research', 'longitudinal studies, probability samples, formally adapted Arabic scales']]) +
  say('Our main message: health anxiety and cyberchondria travel together, AI chatbots are now the main gateway, and doctors should ask every patient, without judgement, what they searched or asked an AI.'))

# ---------------------------------------------------------------------------------------------- REFERENCES
REFS = [
 ('1', 'White & Horvitz 2009', 'Search logs: searches for harmless symptoms escalate to serious diagnoses', 'background, definition'),
 ('2', 'Starcevic & Berle 2013', 'Defined cyberchondria (searching that increases distress)', 'definition'),
 ('3', 'Kemp, DataReportal 2025', 'About four in five Iraqis online', 'local relevance'),
 ('4', 'APA, DSM-5-TR 2022', 'Illness anxiety disorder, somatic symptom disorder', 'Box 1, definitions'),
 ('5', 'Salkovskis & Warwick 1986', 'Cognitive-behavioural model of health anxiety', 'theory'),
 ('6', 'Tyrer 2018', 'Prevalence ~6% general, up to 20% outpatients', 'burden'),
 ('7', 'Karim 2020', '49.5% health anxiety in an Iraqi COVID online survey', 'Iraq data'),
 ('8', 'McElroy 2019', 'Developed and validated the CSS-12', 'our tool'),
 ('9', 'Hallit 2023', 'Arabic CSS-12 validated in Lebanon', 'Arabic version'),
 ('10', 'Mathes 2018', 'Cyberchondria linked to impairment and healthcare use beyond health anxiety', 'distinct constructs'),
 ('11', 'Jungmann 2020', 'Experiment: searching raised health anxiety', 'causal evidence'),
 ('12', 'McMullan 2019', 'Meta-analysis: r = 0.62', 'comparison for H1'),
 ('13', 'Schenkel 2021', 'Meta-analysis: r = 0.63', 'comparison for H1'),
 ('14', 'te Poel 2016', 'Dutch 4-wave panel (n = 5322): two-way relationship', 'direction'),
 ('15', 'Ayers 2023', 'Chatbot answers rated more empathetic than physicians’', 'AI'),
 ('16', 'Ayo-Ajibola 2024', '~1 in 5 Americans used ChatGPT for health', 'AI comparison'),
 ('17', 'Luo 2022', 'Online information and the doctor–patient relationship', 'consultation'),
 ('18', 'El-Zayat 2023', 'Cyberchondria common in Jeddah', 'Arab region'),
 ('19', 'Pasay-An 2025', 'Health anxiety and “Dr. Google” in Saudi primary care', 'Arab region'),
 ('20', 'Dahshan 2026', '13 Arab countries: trust predicted delayed consultation', 'Arab region'),
 ('21', 'El-Zoghby 2024', '1435 Egyptian medical students, 85.8% moderate cyberchondria', 'H2'),
 ('22', 'Fasfoos 2026', 'Palestine: health anxiety least common in medical students', 'H2'),
 ('23', 'von Elm 2007, STROBE', 'Reporting checklist for observational studies', 'methods'),
 ('24', 'Eysenbach 2004, CHERRIES', 'Reporting checklist for internet surveys', 'methods'),
 ('25', 'Serdar 2021', 'Sample size and power', 'sample size'),
 ('26', 'Salkovskis 2002', 'Developed the Health Anxiety Inventory (SHAI)', 'our tool'),
 ('27', 'Arnáez 2019', 'Spanish validation of the SHAI', 'validity'),
 ('28', 'Österman 2022', 'SHAI-14 cut-offs 18, 22, 29 (Sweden)', 'our cut-off'),
 ('29', 'Cruchinho 2024', 'Translation and cross-cultural adaptation methods', 'limitation'),
 ('30', 'Alshayea 2020', 'Arabic SHAI', 'Arabic version'),
 ('31', 'Yun & Bickmore 2025', '21% used LLMs vs 98% search engines', 'AI comparison')]
w('<h2 class="page">B7 · References and Appendix</h2><h3>How the references work</h3><p>We use the <b>Vancouver style</b>, standard in medicine: references are <b>numbered in the order they first appear</b> in the text, written as [1], [2,3]. The list gives authors, title, journal, year, volume, pages and DOI. <mark>31 references, all cited, mostly from 2018 onwards</mark>; older ones are classics (definitions, the cognitive model, the original scales, the reporting checklists).</p>' +
  tbl(['#', 'Source', 'What it showed', 'Used for'], REFS, 'sm') +
  qa([('Why are some references old (1986, 2004, 2007, 2009)?', 'They are the original sources: the cognitive model, the first definition, the reporting checklists. You always cite the original.'),
      ('Why Vancouver style?', 'It is the standard in medical journals and in our college.')]))
w('<h3>The Appendix: the questionnaire</h3><p>The full questionnaire in five parts, as shown to participants (both languages; only English printed). All items were required except a few optional ones (e.g. naming the chatbot), so there was no missing data. Including it lets anyone see exactly what was asked.</p>')

# =====================================================================================================  PART C
w('<div class="part"><h1>Part C</h1><p>Every statistical test: what it does, why we used it, and why not the other one.</p></div>')
TESTS = [
 ('Shapiro–Wilk', 'Are the scores normally distributed?', 'Kolmogorov–Smirnov (weaker); histogram or Q–Q plot', 'Most powerful normality test for our sample size; shown by SPSS first.', 'SHAI W = 0.976, p &lt; 0.001; CSS W = 0.987, p = 0.008 → not normal', 'Analyze → Descriptive Statistics → Explore → Plots → Normality plots with tests'),
 ('Cronbach’s α', 'Do the items of a scale measure the same thing?', 'McDonald’s ω; split-half', 'The standard internal-consistency measure in SPSS and theses.', 'SHAI 0.81, CSS 0.86; Arabic 0.81/0.86, English 0.81/0.88', 'Analyze → Scale → Reliability Analysis (Alpha)'),
 ('Wilson 95% CI', 'How precise is a percentage?', 'Wald interval (inaccurate near 0% or 100%)', 'Accurate for any percentage; the Wald CI for 0.7% would go below zero.', '19.0% (15.0–23.8%)', 'by hand or an online calculator'),
 ('Pearson r', 'Do two scores rise together in a straight line?', 'Spearman ρ', 'The standard correlation for two scores; with n = 300 it is robust.', 'r = 0.47 (0.38–0.55), p &lt; 0.001', 'Analyze → Correlate → Bivariate (Pearson)'),
 ('Spearman ρ', 'Same question, using ranks', 'Pearson r; Kendall τ', 'Does not need normal data; confirms Pearson.', 'ρ = 0.47 (same as Pearson)', 'Analyze → Correlate → Bivariate (Spearman)'),
 ('Partial correlation', 'Is the link still there after removing other variables?', 'Multiple regression', 'Gives the adjusted link as one easy number.', 'partial r = 0.48', 'Analyze → Correlate → Partial'),
 ('Mann–Whitney U', 'Is a score different between 2 groups?', 'Independent t-test', 'Scores not normal; compares ranks.', 'chronic condition SHAI 14 vs 11, p = 0.004 (t-test p = 0.005, same conclusion)', 'Nonparametric Tests → Legacy Dialogs → 2 Independent Samples'),
 ('Kruskal–Wallis H', 'Is a score different across 3+ groups?', 'One-way ANOVA (+ Tukey)', 'Scores not normal, small groups; “ANOVA on ranks”.', 'SHAI by age H = 11.8, df = 3, p = 0.008 (ANOVA p = 0.026, same conclusion)', 'Nonparametric Tests → Legacy Dialogs → K Independent Samples'),
 ('Post-hoc (Bonferroni)', 'Which pairs differ after a significant Kruskal–Wallis?', 'Tukey (after ANOVA); Dunn’s test', 'Multiplies each p by the number of pairs, so chance findings don’t count.', '18–19 vs 30–39 p = 0.026; students vs graduates p = 0.032; medical students vs non-health employees p = 0.004', 'pairwise Mann–Whitney, p × number of pairs'),
 ('χ² test', 'Is a yes/no outcome related to a group?', 'Fisher’s exact (small counts)', 'Compares observed with expected counts.', 'high CSS 52.6% vs 23.0%, χ² = 19.8, p &lt; 0.001', 'Crosstabs → Statistics → Chi-square'),
 ('Fisher’s exact', 'Same as χ² when counts are small', 'χ²', 'χ² is unreliable if an expected count is below 5.', 'fear-driven delay × elevated HA: expected 4.9 → Fisher p = 0.016', 'shown automatically for 2×2 tables'),
 ('Cramér’s V', 'How strong is a χ² association?', 'Phi (2×2 only)', 'χ² depends on sample size; V is 0–1.', 'V = 0.26 (small–medium)', 'Crosstabs → Statistics → Phi and Cramér’s V'),
 ('Odds ratio', 'How many times higher are the odds?', 'Relative risk', 'Comes out of logistic regression; standard in cross-sectional studies.', 'OR = 3.71 (2.04–6.76)', 'Crosstabs → Statistics → Risk'),
 ('Multiple linear regression (hierarchical)', 'Which factors predict a score, together?', 'Simple regression (one predictor); stepwise (unstable)', 'Outcome is a score; blocks show what health anxiety adds after the rest.', 'R² 0.030 → 0.133 → 0.317; SHAI β = 0.48; AI B = 5.33', 'Regression → Linear, Block 1/2/3 (Next)'),
 ('Binary logistic regression', 'Which factors predict a yes/no outcome?', 'Linear regression (wrong for yes/no)', 'Keeps predictions between 0 and 1; gives adjusted odds ratios.', 'AOR 3.12 / 3.83 / 0.61; AUC 0.83; H–L p = 0.50', 'Regression → Binary Logistic'),
 ('Hosmer–Lemeshow', 'Does the logistic model fit?', '—', 'Standard SPSS fit check; we want p &gt; 0.05.', 'p = 0.50 → good fit', 'Binary Logistic → Options'),
 ('ROC curve / AUC', 'How well does the model separate the two groups?', '% correctly classified (misleading here)', '0.5 = chance, 0.8–0.9 good.', 'AUC = 0.83', 'Analyze → ROC Curve'),
 ('VIF', 'Are predictors near-duplicates?', '—', 'Checks multicollinearity; below 5 is fine.', 'all low', 'Linear → Statistics → Collinearity'),
 ('z-score', 'Score in SD units', '—', 'So odds ratios are “per 1 SD” (8.4 CSS points), a meaningful step.', 'AOR 3.12 per SD', 'Descriptives → Save standardized values')]
w('<h2 class="page">C1 · The test library</h2><p>' + idea('The pairs to remember', '<p><mark><b>t-test ↔ Mann–Whitney</b> (2 groups) · <b>ANOVA ↔ Kruskal–Wallis</b> (3+ groups) · <b>Pearson ↔ Spearman</b> (two scores) · <b>χ² ↔ Fisher</b> (small counts) · <b>χ² → Cramér’s V</b> (significance → strength) · <b>linear ↔ logistic regression</b> (score ↔ yes/no)</mark>. The first of each pair needs normal data or large counts; the second does not.</p>') + '</p>')
for t, q, other, whyt, ours, spss in TESTS:
    w(f'<div style="page-break-inside:avoid"><h4>{t}</h4>' + cols([('Question', f'<mark>{q}</mark>'), ('The other version', other), ('Why we used it', whyt), ('Our result', f'<mark>{ours}</mark>'), ('SPSS', spss)]) + '</div>')
w(tbl(['Test we did NOT use', 'Why not'], [
    ['Independent t-test / one-way ANOVA', 'scores not normal; Mann–Whitney / Kruskal–Wallis give the same conclusions'],
    ['Paired t-test, Wilcoxon signed-rank, McNemar, repeated-measures ANOVA', 'they compare the same people twice; we measured everyone once'],
    ['Stepwise regression', 'unstable; we chose predictors in advance (blocks)'],
    ['Bonferroni/FDR correction for all tests', 'we used p &lt; 0.05 like most graduation theses and state it as a limitation'],
    ['Factor analysis (CFA)', 'beyond a graduation thesis; we used already validated scales']]) +
  ar('القاعدة: نوع المتغير يحدد الاختبار. درجات غير طبيعية بين مجموعتين ← Mann–Whitney، بين ثلاث مجموعات أو أكثر ← Kruskal–Wallis، متغيران فئويان ← Chi-square، درجتان ← Pearson و Spearman، عدة عوامل معاً ← الانحدار.'))

# =====================================================================================================  PART D
QA = [
 ('Design and sampling', [
  ('Why a cross-sectional design?', 'It measures prevalence and associations at one time point, quickly and cheaply. It cannot show cause, which we state as a limitation.'),
  ('Why not a cohort study?', 'It needs following people over months or years, beyond a graduation project. We recommend it for future research.'),
  ('Why convenience and snowball sampling?', 'No list of all Baghdad adults who search online exists, so random sampling was impossible.'),
  ('Can you generalise your results?', 'Percentages, no: the sample is young and online. Associations, yes, with caution.'),
  ('Why so many medical students?', 'The link spread through our own networks first. After adjustment, being a medical student did not change scores.'),
  ('How did you prevent duplicate answers?', 'One response per Google account, and no duplicate patterns were found.'),
  ('Why is the sample 300?', '194 were needed to detect r = 0.20; 300 gives more power and a ±5.7% margin for percentages.')]),
 ('Questionnaire and variables', [
  ('Why the SHAI-14?', 'Short, validated, reliable, with a published cut-off (≥ 18).'),
  ('Why ≥ 18?', 'It best separated people with health anxiety from healthy controls in the Swedish validation study.'),
  ('Why the CSS-12?', 'Validated short form of the 33-item CSS keeping all four dimensions.'),
  ('What are the four CSS dimensions?', 'Excessiveness (searching a lot), compulsion (it disrupts life), distress (worse after searching), reassurance seeking (consulting doctors because of it).'),
  ('Did you translate the scales formally?', 'No back-translation; a limitation. Reliability was the same in Arabic and English.'),
  ('How did you define an AI user?', 'Ticked “AI chatbots” or named a chatbot; the 32 who named one without ticking were counted as users because they use it.'),
  ('Why is high cyberchondria > 33?', 'No validated cut-off exists for the CSS-12, so we used the upper third.'),
  ('Why merge ages 40+?', 'Each of the oldest groups was too small to analyse alone.')]),
 ('Statistics', [
  ('Why non-parametric tests?', 'Shapiro–Wilk showed the scores were not normal.'),
  ('Why no ANOVA or t-test?', 'Same reason; Kruskal–Wallis and Mann–Whitney are their non-parametric versions. We checked: the conclusions are the same.'),
  ('Why medians?', 'Rank-based tests go with medians; for skewed data the median describes a typical person better.'),
  ('Which groups differ in Table 6?', 'Post-hoc: 18–19 vs 30–39, students vs graduates, medical students vs non-health employees; younger students are more anxious.'),
  ('Why both Pearson and Spearman?', 'Pearson is standard; Spearman confirms it without assuming normality; both were 0.47.'),
  ('What does partial r mean?', 'The correlation after removing the effect of other variables: 0.48, unchanged.'),
  ('Why hierarchical regression?', 'To show how much health anxiety adds after demographics and digital use: 18.4%.'),
  ('Difference between B and β?', 'B is in real units (CSS points per unit); β is standardised so predictors can be compared.'),
  ('Why logistic regression?', 'The outcome (elevated health anxiety) is yes/no.'),
  ('What is an AOR?', 'Adjusted odds ratio: how many times the odds change with other factors held constant.'),
  ('What is Cramér’s V?', 'The strength of a χ² association (0.1 small, 0.3 medium).'),
  ('Why Fisher’s exact test?', 'χ² is unreliable when an expected count is below 5.'),
  ('What is the AUC?', 'How well the model separates the two groups; 0.83 is good.'),
  ('What does Hosmer–Lemeshow p = 0.50 mean?', 'The model fits well (we want p > 0.05).'),
  ('Why not correct for multiple testing?', 'Standard p < 0.05; stated as a limitation; main results p < 0.001.'),
  ('Which software?', 'IBM SPSS Statistics 26.')]),
 ('Results and interpretation', [
  ('What is your main finding?', 'Health anxiety and cyberchondria are moderately associated, r = 0.47, independently of other factors.'),
  ('What does r = 0.47 mean in plain words?', 'People who worry more about illness search more and more anxiously; worry explains about 22% of the differences.'),
  ('Does health anxiety cause cyberchondria?', 'We cannot say; one survey cannot show direction. A Dutch study suggests they feed each other.'),
  ('Why is your r lower than the meta-analyses (0.62)?', 'Low, narrow health anxiety in our sample, confident internet users, and the short CSS-12.'),
  ('Is 19% a lot?', 'It is a screening estimate; at stricter cut-offs it is 7.3% (≥ 22) and 0.7% (≥ 29). It shows a substantial minority with elevated worry.'),
  ('What about AI users?', 'They had higher cyberchondria, 5.3 points, independently of health anxiety (p < 0.001). The non-user group was small, so it needs confirmation.'),
  ('Why might AI increase cyberchondria?', 'Chatbots can be asked again and again, encouraging repeated searching and reassurance seeking.'),
  ('Why was H2 not supported?', 'Medical students’ higher health anxiety disappeared after adjusting for age; their cyberchondria was identical.'),
  ('Is “medical student syndrome” real?', 'Not in our sample: medical knowledge neither increased nor protected against cyberchondria.'),
  ('Why does age matter in the regression but not in Table 6?', 'Older people had lower anxiety but similar searching; holding anxiety constant reveals their relatively higher searching.'),
  ('Why do 34.7% delay care?', 'Reassuring information online; it may save visits for minor symptoms but risks late diagnosis.'),
  ('Why do people hide searches from the doctor?', 'Mainly fear of being judged; hidden information can strain the relationship.')]),
 ('Ethics, limitations and impact', [
  ('Was ethics approval needed?', 'The supervisor confirmed not, for an anonymous voluntary online survey of adults with no intervention.'),
  ('How was consent obtained?', 'Electronic consent, with age ≥ 18 confirmed, before any question.'),
  ('What is the most important limitation?', 'The cross-sectional design: no direction can be shown.'),
  ('What would you do differently?', 'A probability sample, a formally translated Arabic version, and a longitudinal design.'),
  ('What is new in your study?', 'First CSS-12 study in Baghdad; AI chatbots separate from search engines; medical students compared with adjustment.'),
  ('What should doctors do?', 'Ask without judgement what patients searched or asked an AI, and clear up misunderstandings.'),
  ('Who benefits from your study?', 'Clinicians, medical educators, the Ministry of Health (health-literacy campaigns) and AI developers.')])]
w('<div class="part"><h1>Part D</h1><p>60 questions the committee may ask, with short model answers. Cover the answers and say yours out loud.</p></div>')
first = True
for grp, items in QA:
    w(('<h2 class="page">' if first else '<h2>') + f'D · {grp}</h2>' + ''.join(f'<p class="qq">{q}</p><p class="aa">{a}</p>' for q, a in items)); first = False
w(ar('نصيحة للمناقشة: إذا لم تعرف الجواب، قل بهدوء: "هذه نقطة مهمة، ونعتبرها من حدود الدراسة ونوصي بدراستها مستقبلاً". لا تخمّن أرقاماً.'))

# =====================================================================================================  PART E
w('<h2 class="page">E · Every number on one page</h2>' + tbl(['What', 'Number', 'Where'], [
    ['Participants', '300; 62.3% aged 20–29; 56.3% female; 44.0% medical students', 'Table 1'],
    ['Tools', 'AI chatbots 88.7% (78.0% ticked); search engines 56.3%; ChatGPT 59.3%', 'Table 2, Fig 2'],
    ['After searching', 'delay when reassured 34.7%; never tell doctor 31.7%; relationship strained 34.7%', 'Table 2, Fig 3'],
    ['SHAI-14', 'mean 12.35 ± 5.83; median 12 (8–16); α 0.81 (Arabic 0.81, English 0.81)', 'Table 3'],
    ['CSS-12', 'mean 28.86 ± 8.36; median 29 (23–34); α 0.86 (Arabic 0.86, English 0.88)', 'Table 3'],
    ['Elevated health anxiety', '19.0% (15.0–23.8); 7.3% at ≥ 22; 0.7% at ≥ 29', 'Table 4'],
    ['Main correlation', 'r 0.47 (0.38–0.55); ρ 0.47; partial r 0.48; r² 22%', 'Table 5, Fig 4'],
    ['By dimension', 'excessiveness 0.46; distress 0.45; compulsion 0.25; reassurance 0.24', 'Table 5'],
    ['Group differences', 'chronic SHAI 14 vs 11 (p 0.004); reassurance 13 vs 10 (p &lt; 0.001); AI CSS 30 vs 23.5 (p &lt; 0.001)', 'Table 6'],
    ['Post-hoc', '18–19 vs 30–39 p 0.026; students vs graduates p 0.032; medical students vs non-health employees p 0.004', 'text'],
    ['χ²', 'high CSS 52.6% vs 23.0%, OR 3.71, V 0.26', 'Table 7'],
    ['Regression', 'R² 0.030 → 0.133 → 0.317; SHAI B 0.68, β 0.48; AI B 5.33 (2.57–8.09), p &lt; 0.001', 'Table 8'],
    ['Logistic', 'AOR CSS 3.12, reassurance 3.83, age 0.61; AUC 0.83; H–L p 0.50; Nagelkerke 0.31', 'Table 9, Fig 6'],
    ['Medical students', 'SHAI median 12.5 vs 11 (p 0.004; adjusted p 0.081); CSS 29 vs 29 (p 0.989)', 'Table 10'],
    ['Hypotheses', '<mark>H1 supported; H2 not supported</mark>', '']], 'sm'))
w('</body></html>')
open(HTML, 'w').write('\n'.join(W)); print('wrote', HTML)
