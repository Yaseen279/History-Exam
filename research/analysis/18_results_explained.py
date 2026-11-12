"""Results, fully explained (PDF, print layout) for Student 2.
Every table of Chapter 3 is reproduced from the final thesis, then explained: the question it answers, the test and why,
how to read each column, a worked walk-through of real rows, what it means, what to say and what you may be asked.
Usage: python3 18_results_explained.py <output dir> <thesis.docx> <out.html>   (then print to PDF)"""
import sys, json, html as H
from docx import Document

OUT, DOCX, HTML = sys.argv[1], sys.argv[2], sys.argv[3]
import os
FIG = os.path.abspath(f'{OUT}/figures')
S = json.load(open(f'{OUT}/simple.json')); L = S['logit_HA']; MS = S['medstud']

# ---------------------------------------------------------------- the thesis tables, exactly as printed
doc = Document(DOCX)
def rows_of(t):
    out = []
    for r in t.rows:
        cells, seen = [], set()
        for c in r.cells:                       # merged cells repeat: keep each cell object once
            if id(c._tc) in seen: continue
            seen.add(id(c._tc)); cells.append(c.text.strip())
        out.append(cells)
    return out
TB = [rows_of(t) for t in doc.tables]
def find(first_header):
    return next(t for t in TB if t and t[0] and t[0][0].startswith(first_header))
T1, T2, T3, T4, T5 = find('Characteristic'), find('Variable'), find('Scale'), find('SHAI-14 score'), find('Cyberchondria measure')
T6 = next(t for t in TB if t[0][:3] == ['Variable', 'n', 'SHAI mean ± SD'])
T7 = next(t for t in TB if len(t[0]) > 1 and t[0][1].startswith('n/N'))
T8 = next(t for t in TB if t[0][:2] == ['Predictor', 'B']); T9 = next(t for t in TB if t[0][:2] == ['Predictor', 'AOR'])
T10 = find('Measure')

def table(rows, hi=(), cols=None, small=False):
    """Render a thesis table. hi = substrings of first-column labels to highlight."""
    head, body = rows[0], rows[1:]
    w = len(head)
    h = f'<table class="t{" sm" if small else ""}"><tr>' + ''.join(f'<th>{H.escape(x)}</th>' for x in head) + '</tr>'
    for r in body:
        if len(r) == 1 or all(not x for x in r[1:]):
            h += f'<tr class="grp"><td colspan="{w}">{H.escape(r[0])}</td></tr>'; continue
        r = (r + [''] * w)[:w]
        cls = ' class="hi"' if any(k in r[0] for k in hi) else ''
        h += f'<tr{cls}>' + ''.join(f'<td>{H.escape(x)}</td>' for x in r) + '</tr>'
    return h + '</table>'

def fig(name, cap, w=100): return f'<figure><img src="file://{FIG}/{name}.png" style="width:{w}%"><figcaption>{cap}</figcaption></figure>'
def box(kind, title, body): return f'<div class="box {kind}"><div class="bt">{title}</div>{body}</div>'
def say(t): return box('say', 'Say it', f'<p>{t}</p>')
def trap(t): return box('trap', 'Trap', f'<p>{t}</p>')
def q(pairs): return box('ask', 'If they ask', ''.join(f'<p class="qq">{a}</p><p class="aa">{b}</p>' for a, b in pairs))
def cols(pairs): return '<dl class="cols">' + ''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in pairs) + '</dl>'
def steps(items): return '<ol class="steps">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'
def card(qn, test, why): return f'<div class="qcard"><div><span>Question</span>{qn}</div><div><span>Test</span>{test}</div><div><span>Why this test</span>{why}</div></div>'

H_ = []; w = H_.append
CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
* { box-sizing: border-box; }
body { font-family: Carlito, Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.6pt; line-height: 1.5; color: #1d2230; margin: 0; }
h1 { font-family: Caladea, Cambria, Georgia, serif; font-size: 27pt; color: #1F3B4D; margin: 0 0 4px; line-height: 1.1; }
h2 { font-family: Caladea, Cambria, Georgia, serif; font-size: 17pt; color: #1F3B4D; margin: 0 0 8px; padding-bottom: 4px; border-bottom: 2.5px solid #1F3B4D; page-break-after: avoid; }
h3 { font-size: 12.5pt; color: #b4541c; margin: 14px 0 5px; page-break-after: avoid; }
h4 { font-size: 11pt; margin: 10px 0 3px; color: #1F3B4D; page-break-after: avoid; }
p { margin: 3px 0 7px; } ul, ol { margin: 3px 0 8px; padding-left: 20px; } li { margin: 2px 0; }
.page { page-break-before: always; }
.lead { font-size: 12pt; color: #46506a; }
table.t { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.3pt; page-break-inside: avoid; }
table.t.sm { font-size: 8.5pt; }
table.t th { background: #1F3B4D; color: #fff; text-align: left; padding: 4px 6px; font-weight: 700; }
table.t td { padding: 3px 6px; border-bottom: 1px solid #dfe5ea; vertical-align: top; }
table.t tr.grp td { background: #e7eef3; font-weight: 700; color: #1F3B4D; }
table.t tr.hi td { background: #fff1c9; }
.mini { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.6pt; page-break-inside: avoid; }
.mini th { background: #e7eef3; text-align: left; padding: 4px 6px; } .mini td { padding: 4px 6px; border-bottom: 1px solid #dfe5ea; vertical-align: top; }
figure { margin: 6px 0 10px; text-align: center; page-break-inside: avoid; } figure img { border: 1px solid #d5dbe1; }
figcaption { font-size: 9pt; color: #555; font-style: italic; margin-top: 3px; }
.box { border-radius: 7px; padding: 7px 11px; margin: 8px 0; page-break-inside: avoid; }
.box .bt { font-weight: 700; font-size: 9pt; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 2px; }
.box p { margin: 2px 0 4px; }
.say { background: #e6f2ec; border-left: 5px solid #1e7a52; } .say .bt { color: #1e7a52; }
.trap { background: #fbecef; border-left: 5px solid #9d1c4a; } .trap .bt { color: #9d1c4a; }
.ask { background: #eef0fb; border-left: 5px solid #3d3a9e; } .ask .bt { color: #3d3a9e; }
.idea { background: #fff6e5; border-left: 5px solid #b4541c; } .idea .bt { color: #b4541c; }
.qq { font-weight: 700; margin-top: 5px !important; } .aa { margin-left: 10px !important; }
dl.cols { display: grid; grid-template-columns: 30% 70%; margin: 4px 0 10px; border-top: 1px solid #dfe5ea; page-break-inside: avoid; }
dl.cols dt { font-weight: 700; padding: 4px 8px 4px 0; border-bottom: 1px solid #dfe5ea; color: #1F3B4D; }
dl.cols dd { margin: 0; padding: 4px 0; border-bottom: 1px solid #dfe5ea; }
ol.steps li { margin: 4px 0; }
.qcard { display: grid; grid-template-columns: 1fr 1fr 1.6fr; gap: 0; border: 1px solid #c9d3dc; border-radius: 7px; margin: 6px 0 10px; overflow: hidden; page-break-inside: avoid; }
.qcard > div { padding: 6px 9px; border-right: 1px solid #c9d3dc; font-size: 10pt; } .qcard > div:last-child { border-right: 0; }
.qcard span { display: block; font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: #b4541c; }
.big { font-size: 20pt; font-weight: 700; color: #1F3B4D; }
.toc li { margin: 4px 0; font-size: 11.5pt; }
.k { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 9.6pt; background: #f2f4f7; padding: 1px 4px; border-radius: 3px; }
.calc { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 9.6pt; background: #f4f6f9; border: 1px solid #e0e5eb; border-radius: 6px; padding: 7px 10px; margin: 6px 0 10px; white-space: pre-wrap; page-break-inside: avoid; }
"""
w(f'<!doctype html><html><head><meta charset="utf-8"><title>Results Fully Explained</title><style>{CSS}</style></head><body>')

# ================================================================ cover
w('''<div style="margin-top:40mm"><p class="lead" style="letter-spacing:.12em;text-transform:uppercase;font-size:10pt;color:#b4541c">Student 2 · Defence preparation</p>
<h1>Your Results, Fully Explained</h1>
<p class="lead">Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad</p>
<p style="margin-top:14mm">This guide takes Chapter 3 of the thesis one table at a time. Every table is reproduced exactly as it appears in the thesis. For each one you get:</p>
<ul><li><b>the question</b> the table answers,</li><li><b>the test</b> that was used and <b>why that test</b>,</li><li><b>how to read every column</b>,</li>
<li><b>a walk-through of real rows</b> with the numbers worked out,</li><li><b>what it means</b> in plain words, <b>what to say</b>, and <b>what you may be asked</b>.</li></ul>
<p>Yellow rows in the tables are the rows you must know.</p>
<h3 style="margin-top:12mm">Contents</h3><ol class="toc">
<li>Part A · Six ideas every result uses</li><li>Part B · Which test, and why (the whole map on one page)</li><li>The test library · every test explained in full (16 pages of tests)</li>
<li>3.1 Participants and online searching (Tables 1–2, Figures 2–3)</li><li>3.2 Levels of health anxiety and cyberchondria (Tables 3–4)</li>
<li>3.3 The main association (Table 5, Figure 4)</li><li>3.4 Which groups differ (Tables 6–7, Figure 5)</li>
<li>3.5 Independent predictors (Tables 8–9, Figure 6)</li><li>3.6 Medical students compared with others (Table 10)</li>
<li>Part C · The hypotheses, with the evidence</li><li>Part D · Practice: read the row yourself (answers at the end)</li></ol></div>''')

# ================================================================ Part A
w('<h2 class="page">Part A · Six ideas every result uses</h2><p>Every number in Chapter 3 is one of these six things. Learn them once and every table becomes readable.</p>')
w('<h3>1. Two kinds of variable decide everything</h3>' + cols([
    ('Categorical', 'Groups or yes/no: gender, uses AI (yes/no), elevated health anxiety (yes/no). Described with <b>n and %</b>.'),
    ('Continuous (a score)', 'A number on a scale: SHAI-14 (0–42), CSS-12 (12–60). Described with <b>mean ± SD</b> or <b>median (IQR)</b>.')]) +
  '<p>Which test you use depends only on <b>what kind of variable you are comparing with what</b> (Part B).</p>')
w('<h3>2. The p-value: “could this be luck?”</h3><p>Imagine there is really no difference or no link. The p-value is the chance of getting a result at least as strong as ours just by luck. If p &lt; 0.05 we call it <b>significant</b>: unlikely to be luck.</p>' +
  box('idea', 'Example', '<p>Health anxiety and cyberchondria: r = 0.47, <b>p &lt; 0.001</b>. If there were no link, a correlation this strong in 300 people would happen less than 1 time in 1000.</p>') +
  trap('p tells you whether an effect exists, not how big or important it is. With 300 people even small effects can be significant. For size, look at r, B, β or the odds ratio.'))
w('<h3>3. The 95% confidence interval: “how sure are we?”</h3><p>Our numbers come from 300 people, not everyone. The 95% CI is the range where the true value probably lies. Narrow = precise.</p>' +
  box('idea', 'Two rules you will use all the time', '<p><b>Odds ratio:</b> if the CI includes <b>1</b> → not significant. Example: chronic condition AOR 1.51 (0.69–3.30) includes 1 → not significant.</p><p><b>Difference or coefficient (B):</b> if the CI includes <b>0</b> → not significant. Example: Female B −0.05 (−1.82 to 1.72) includes 0 → not significant.</p>'))
w('<h3>4. Effect size: “how big?”</h3>' + '<table class="mini"><tr><th>Measure</th><th>Used for</th><th>Small / medium / large</th><th>Ours</th></tr>'
  '<tr><td>r (correlation)</td><td>two scores</td><td>0.1 / 0.3 / 0.5</td><td>0.47: moderate, close to large</td></tr>'
  '<tr><td>Cramér\'s V</td><td>χ² tests</td><td>0.1 / 0.3 / 0.5</td><td>0.12–0.26: small</td></tr>'
  '<tr><td>R²</td><td>regression</td><td>share explained, 0–1</td><td>0.317: 32% of differences in CSS explained</td></tr>'
  '<tr><td>Odds ratio</td><td>yes/no outcomes</td><td>1 = none; further from 1 = bigger</td><td>3.12 per SD of cyberchondria</td></tr></table>')
w('<h3>5. Unadjusted versus adjusted</h3><p><b>Unadjusted</b> (bivariate, Tables 5–7): one variable at a time. <b>Adjusted</b> (multivariable, Tables 8–10): many variables in one model, so each result is “holding the others constant”. A factor that is significant alone can disappear after adjustment if another factor explains it, and the reverse can happen too (you will see both in Table 8).</p>')
w('<h3>6. Normal or not normal</h3><p>Many tests (t-test, ANOVA) assume scores form a bell curve. The <b>Shapiro–Wilk test</b> checks this. Ours were <b>not</b> normal (SHAI p &lt; 0.001; CSS p = 0.008), so groups were compared with <b>non-parametric</b> tests (Mann–Whitney, Kruskal–Wallis), which compare ranks instead of means. Correlation and regression were kept because n = 300 is large, Spearman gave the same answer as Pearson, and the regression residuals were close to normal (checked with a histogram and P-P plot).</p>' +
  box('ask', 'If they ask “why no ANOVA or t-test?”', '<p class="aa">“Shapiro–Wilk showed our scores were not normally distributed and some groups were small, so we used Kruskal–Wallis, the non-parametric version of one-way ANOVA, and Mann–Whitney instead of the t-test. We checked: ANOVA and t-tests give the same conclusions.”</p>'))

# ================================================================ Part B map
w('<h2 class="page">Part B · Which test, and why</h2><p>The whole chapter uses nine tests. The choice follows one rule: <b>what kind of variable is compared with what</b>.</p>')
w('<table class="mini"><tr><th>You want to know…</th><th>Variable types</th><th>Test</th><th>Where</th></tr>' + ''.join(f'<tr><td>{a}</td><td>{b}</td><td><b>{c}</b></td><td>{d}</td></tr>' for a, b, c, d in [
    ('How common is something, and how precise is that?', 'one categorical', '% with 95% CI (Wilson)', 'Tables 1, 2, 4'),
    ('Do the items of a scale measure one thing?', 'items of one scale', "Cronbach's α", 'Table 3'),
    ('Are the scores normal?', 'one score', 'Shapiro–Wilk', 'Methods'),
    ('Do two scores rise together?', 'score × score', 'Pearson r (Spearman ρ to confirm); partial r adjusted', 'Table 5'),
    ('Does a score differ between 2 groups?', 'score × 2 groups', 'Mann–Whitney U', 'Table 6'),
    ('Does a score differ between 3+ groups?', 'score × 3+ groups', 'Kruskal–Wallis H', 'Table 6'),
    ('Is a yes/no outcome related to a group?', 'categorical × categorical', 'χ² (Fisher if cells small), Cramér\'s V', 'Table 7'),
    ('Which factors predict a score, together?', 'score ← many', 'Hierarchical multiple linear regression', 'Table 8'),
    ('Which factors predict a yes/no, together?', 'yes/no ← many', 'Binary logistic regression', 'Tables 9–10'),
    ('Are medical students different, before and after adjustment?', 'score or yes/no × 2 groups, then ← many', 'Mann–Whitney / χ², then linear / logistic regression', 'Table 10')]) + '</table>')
w(box('idea', 'The logic of the chapter', '<p>The chapter moves from simple to complex: <b>describe</b> (3.1–3.2) → <b>one link at a time</b> (3.3–3.4) → <b>all factors together</b> (3.5) → <b>medical students</b> (3.6). Each step answers a question the previous one leaves open.</p>'))
w(say('All analyses were done in SPSS 26 with two-sided p &lt; 0.05. Because our scores were not normally distributed we compared groups with Mann–Whitney and Kruskal–Wallis, used χ² for categories, Pearson and Spearman for the main correlation, and multiple linear and binary logistic regression for independent effects.'))

# ================================================================ test library
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_library import compute, library
_d = pd.read_pickle(f'{OUT}/analysed.pkl')
w('<h2 class="page">The test library · every test, explained in full</h2><p>For each test: what it answers, <b>its other version</b> and when you would use that instead, the assumptions, how it works step by step, a worked example with our own data, how to run and read it in SPSS, and how to report it.</p>' +
  box('idea', 'The pairs to remember', '<p><b>t-test ↔ Mann–Whitney</b> (2 groups) · <b>ANOVA ↔ Kruskal–Wallis</b> (3+ groups) · <b>Pearson ↔ Spearman</b> (two scores) · <b>χ² ↔ Fisher</b> (categories; small counts) · <b>χ² → Cramér’s V</b> (significance → strength) · <b>linear ↔ logistic regression</b> (score ↔ yes/no outcome). The first of each pair needs normal data or large counts; the second does not.</p>'))
for _k, (_t, _h) in enumerate(library(compute(_d), S, box, say, trap, q)):
    w(f'<div style="page-break-inside:avoid"><h3 style="font-size:14pt">{_t}</h3>' + _h + '</div>')

# ================================================================ 3.1
w('<h2 class="page">3.1 Participants and online searching</h2>')
w(card('Who answered, how do they search, and what do they do afterwards?', 'Descriptive statistics only: n and %', 'Every study describes its sample first so the reader knows who the results apply to. No test is needed: we are describing, not comparing.'))
w('<h3>Table 1 · Socio-demographic characteristics</h3>' + table(T1, hi=('20-29', 'Medical student', 'Female', 'Yes')))
w(cols([('n', 'number of people in that row'), ('%', 'n ÷ 300 × 100. Each block adds up to 300 people and 100%.')]))
w('<h4>Walk-through</h4>' + steps(['20–29 years: 187 people → 187 ÷ 300 = <b>62.3%</b>. Add 18–19 (18.7%) and <b>81%</b> are under 30.',
     'Medical students: 132 → <b>44.0%</b>. Health-related background (medical + other health students + health workers): 190 → <b>63.3%</b>.',
     'Female 56.3%; chronic condition 21.7%; answered mostly in Arabic 70.7%.']))
w(say('Our 300 participants were young, 62% aged 20–29, and 44% were medical students, so our percentages describe a young, educated online sample, not all of Baghdad.') +
  q([('Why so many medical students?', 'The form spread through our own networks first (convenience and snowball sampling). We state this as a limitation and do not generalise percentages; associations are still informative.')]))
w('<h3 class="page">Table 2 · Digital health-information seeking</h3>' + table(T2, hi=('AI chatbots', 'ChatGPT', 'Convenience', 'Delay/skip', 'Never'), small=True))
w(cols([('“multiple”', 'people could tick several options, so these blocks add to more than 100%'), ('AI chatbots*', '88.7% = ticked AI <i>or</i> named a chatbot. 78.0% ticked the AI box itself (the asterisk).'),
        ('Tool profile', 'everyone placed in one group: AI + search engine / AI only / no AI. This block does add to 100%.')]))
w('<h4>Walk-through</h4>' + steps(['AI chatbots: 78.0% ticked (88.7% including the 32 who named one) vs search engines <b>56.3%</b> → AI is now first.',
     '41.0% used AI <i>without</i> any search engine. ChatGPT 59.3%, Gemini 23.7%.',
     'Motives: convenience 80.0%, “do I need a doctor?” 57.7%, instant reassurance 51.0%.',
     'After searching: delayed or skipped care because reassured <b>34.7%</b>; ignored the symptom 30.0%; several doctors 25.3%; urgent visit 22.0%.',
     'Told the doctor: always 27.0%, sometimes 41.3%, <b>never 31.7%</b> (fear of judgement).']))
w(fig('fig2_tools_motives', 'Figure 2: the same tools and motives as bars (each bar = % of all 300).', 96) + fig('fig3_behaviours', 'Figure 3: behaviour after searching, disclosure, and effect on the relationship with doctors.', 100))
w(say('AI chatbots are now the main gateway: 78% ticked them against 56% for search engines. After searching, one in three delayed care because they felt reassured, and almost one in three never tells the doctor.') +
  trap('Two AI numbers exist: 78.0% (ticked the box) and 88.7% (ticked or named a chatbot). Always say which one. The difference is the 32 people who named a chatbot in the next question without ticking AI.'))

# ================================================================ 3.2
w('<h2 class="page">3.2 Levels of health anxiety and cyberchondria</h2>')
w(card('How anxious are people, how much do they search, and do the scales work?', 'Mean ± SD, median (IQR), Cronbach\'s α; % with Wilson 95% CI', 'Before using any score you must show it is reliable (α) and describe its level. Prevalence needs a CI because it is an estimate.'))
w('<h3>Table 3 · Scores and reliability</h3>' + table(T3, hi=('SHAI-14 total', 'CSS-12 total')))
w(cols([('Mean ± SD', 'average and spread. About two-thirds of people lie within 1 SD of the mean.'), ('Median (IQR)', 'the middle person, and the range of the middle half. Useful because scores are skewed.'),
        ('Range', 'lowest and highest score anyone actually got (the possible range is in brackets)'), ("Cronbach's α", 'do the items of the scale measure the same thing? ≥ 0.7 acceptable, ≥ 0.8 good, ≥ 0.9 excellent.')]))
w('<h4>Walk-through</h4>' + steps(['SHAI: mean <b>12.35 ± 5.83</b> out of 42 → most people scored about 6.5 to 18. Median 12 (half scored 8–16). Nobody scored above 30.',
     'CSS: mean <b>28.86 ± 8.36</b> out of 12–60 → moderate searching.',
     'Dimensions (each 3–15): excessiveness highest (9.66), compulsion lowest (5.00, median 4: most people are near the minimum of 3) → people search a lot, but it rarely disrupts work or social life.',
     'α = 0.81 (SHAI) and 0.86 (CSS): both <b>good</b>. All four dimensions ≥ 0.76.']))
w('<h3>Table 4 · Prevalence at the published cut-offs</h3>' + table(T4, hi=('≥ 18',)))
w(cols([('Cut-off', 'the three thresholds from the Swedish validation study (Österman 2022). We use ≥ 18.'), ('95% CI', 'Wilson interval: the true prevalence is probably between 15.0% and 23.8%.')]))
w('<div class="calc">57 of 300 scored ≥ 18  →  57 ÷ 300 = 19.0%\n95% CI 15.0% to 23.8%  (Wilson score interval)</div>')
w(say('Both questionnaires were reliable, alpha 0.81 and 0.86. About one in five, 19%, scored in the elevated range of health anxiety, a screening result, not a diagnosis.') +
  trap('Never say “19% have health anxiety disorder”. The SHAI is a screening questionnaire; a diagnosis needs a clinical interview.') +
  q([('Why 18?', 'It best separated people with health anxiety from healthy controls in the Swedish diagnostic study. We also show 22 and 29 so the reader sees how the estimate depends on the threshold.'),
     ('Is α 0.81 good enough?', 'Yes: 0.7 is the usual minimum and 0.8 is good.')]))

# ================================================================ 3.3
w('<h2 class="page">3.3 The main association</h2>')
w(card('Do people with more health anxiety have more cyberchondria (H1), and does it hold after adjustment (H2)?', 'Pearson r with 95% CI; Spearman ρ; partial r; adjusted β', 'Both are continuous scores, so a correlation. Spearman checks the result does not depend on normality; partial r and β check it is not explained by other factors.'))
w('<h3>Table 5 · Correlations</h3>' + table(T5, hi=('CSS-12 total', 'Excessiveness', 'Distress')))
w(cols([('Pearson r (95% CI)', 'strength of the straight-line link, −1 to +1. CI by Fisher\'s z.'), ('Spearman ρ', 'the same idea using ranks; a check that does not need normal data'),
        ('p', 'all &lt; 0.001'), ('Adjusted β', 'the standardised effect of SHAI on that measure from a regression with all other factors (age, gender, occupation, chronic disease, language, tools, trust, motives)')]))
w('<h4>Walk-through</h4>' + steps(['CSS total: r = <b>0.47</b> (0.38–0.55). The whole CI is well above 0 → a real, moderate-to-large link.',
     'r² = 0.47 × 0.47 = <b>0.22</b> → health anxiety accounts for about 22% of the differences in cyberchondria.',
     'Spearman ρ = 0.47 → identical: the result does not depend on the method.',
     'Partial r = 0.48 after removing age, gender, health background, chronic disease, trust and AI use → unchanged, so those are not the explanation (H2).',
     'By dimension: excessiveness 0.46 and distress 0.45 are strongest; compulsion 0.25 and reassurance 0.24 weakest (as H1 predicted).']))
w(fig('fig1_scatter_shai_css', 'Figure 4: each dot is one participant; the orange line is the best fit (CSS = 20.5 + 0.67 × SHAI), the band its 95% CI.', 62))
w('<div class="calc">Reading the line: CSS = 20.5 + 0.67 × SHAI\nSHAI 10  → 20.5 + 6.7  = 27.2\nSHAI 20  → 20.5 + 13.4 = 33.9   (about 7 CSS points higher for 10 SHAI points)</div>')
w(say('This is our main result. Health anxiety and cyberchondria rise together, r = 0.47, and the link is the same after adjusting for everything else, 0.48. It is strongest for excessive searching and for distress after searching. Hypotheses 1 and 2 are supported.') +
  trap('Say “associated with” or “linked to”. Never “health anxiety causes cyberchondria”: one survey at one time cannot show direction.') +
  q([('Why is your r (0.47) lower than the meta-analyses (0.62)?', 'Our health anxiety scores were low and narrowly spread, our participants were confident internet users, and we used the short 12-item scale; all of these weaken correlations.'),
     ('Pearson or Spearman, which is right?', 'Both: Pearson is the standard for two scores, Spearman checks it without assuming normality, and they agree (0.47).')]))

# ================================================================ 3.4
w('<h2 class="page">3.4 Which groups differ</h2>')
w(card('Are scores higher in some groups (age, chronic illness, AI users…)?', 'Mann–Whitney U (2 groups), Kruskal–Wallis H (3+ groups)', 'A score compared across groups, and the scores are not normal → the non-parametric versions of the t-test and one-way ANOVA.'))
w('<h3>Table 6 · Scores by participant characteristics (selected rows)</h3>')
keep = ('Age group', 'Gender', 'Education', 'Study/work', 'Chronic condition', 'Uses AI chatbots', 'Uses social media', 'Tool profile', 'Motive: reassurance')
sel, on = [T6[0]], False
for r in T6[1:]:
    if len(r) >= 2 and r[1] == '' and r[0]:
        on = r[0] in keep
    if on: sel.append(r)
w(table(sel, hi=('Yes', 'AI + search', 'No AI'), small=True))
w(cols([('n', 'people in that group'), ('SHAI / CSS mean ± SD', 'average score of that group'), ('p (on the bold variable row)', 'one p for the whole variable: Mann–Whitney if 2 groups, Kruskal–Wallis if 3 or more. Below 0.05 = the groups differ.')]))
w('<h4>Walk-through</h4>' + steps(['<b>Chronic condition</b>: SHAI 14.2 vs 11.9, Mann–Whitney <b>p = 0.004</b> → people with a chronic illness are more health-anxious. CSS 29.9 vs 28.6, p = 0.435 → but they do not search more.',
     '<b>Reassurance motive</b>: SHAI 13.8 vs 10.9, <b>p &lt; 0.001</b>, the clearest difference in the table.',
     '<b>AI users</b>: CSS 29.5 vs 24.0, <b>p &lt; 0.001</b>. <b>Tool profile</b>: 30.1 (AI + search) vs 28.7 (AI only) vs 24.0 (no AI), Kruskal–Wallis p &lt; 0.001 (Figure 5).',
     '<b>Age</b>: SHAI falls from 14.0 at 18–19 to 10.2 at 30–39, p = 0.008 → younger people are more anxious. Education and occupation also differ for SHAI (students highest).',
     '<b>Gender</b>: p = 0.378 and 0.859 → no difference.']))
w(trap('Kruskal–Wallis tells you that the groups differ somewhere, not which pair. Read the means to see the pattern (e.g. no-AI users clearly lowest). The thesis does not claim specific pairs.'))
w(fig('fig6_css_by_tool', 'Figure 5: box plot of CSS by tool profile. Line = median; box = middle half of people; whiskers = range.', 58))
w('<h3 class="page">Table 7 · Yes/no outcomes (χ²), significant rows only</h3>' + table(T7, hi=('Elevated health anxiety', 'Motive: reassurance', 'Disclose'), small=True))
w(cols([('n/N (%) with outcome', 'in each group: how many had the outcome out of how many in the group'), ("Cramér's V", 'strength of the association: 0.1 small, 0.3 medium'), ('p', 'Pearson χ² or Fisher\'s exact test')]))
w('<h4>Walk-through: the key row</h4><p>High cyberchondria (CSS &gt; 33) by elevated health anxiety:</p>' +
  '<div class="calc">Elevated HA:     30 of 57  = 52.6% high CSS  → odds = 30/27  = 1.11\nNot elevated:    56 of 243 = 23.0% high CSS  → odds = 56/187 = 0.30\nOdds ratio = 1.11 / 0.30 = 3.71   (95% CI 2.04–6.76),  χ² p &lt; 0.001,  V = 0.26</div>' +
  '<p>Also: elevated health anxiety was more common in reassurance seekers (27.5% vs 10.2%) and social-media users (40.6% vs 16.4%); high cyberchondria was more common in people who always tell their doctor (40.7%) than in those who never do (15.8%).</p>')
w(say('Health anxiety was higher in people with a chronic illness and, most clearly, in those searching for instant reassurance. AI users had higher cyberchondria, and people with elevated health anxiety were more than twice as likely to have high cyberchondria, 53% against 23%.') +
  q([('Why is high cyberchondria “> 33”?', 'The CSS-12 has no validated cut-off, so we used the upper third of our sample.'),
     ('Why Fisher sometimes?', 'χ² is unreliable when expected counts in a cell are below 5; Fisher\'s exact test is used then.')]))

# ================================================================ 3.5
w('<h2 class="page">3.5 Independent predictors</h2>')
w(card('Which factors predict cyberchondria when all are considered together (H2)?', 'Hierarchical multiple linear regression (enter method, 3 blocks)', 'The outcome (CSS) is a score and there are many predictors. Entering them in blocks shows how much each group of factors adds.'))
w('<h3>Table 8 · Multiple linear regression of CSS (final model)</h3>' + table(T8, hi=('Health anxiety', 'Uses AI chatbots', 'Age 30–39', 'Age ≥40'), small=True))
w('<table class="mini"><tr><th>Block entered</th><th>R² (share explained)</th><th>Added (ΔR²)</th><th>p for the added block</th></tr>'
  '<tr><td>1 · Socio-demographics</td><td>0.030</td><td>3.0%</td><td>0.53 (not significant)</td></tr><tr><td>2 · + Digital use</td><td>0.133</td><td>+10.3%</td><td>&lt; 0.001</td></tr>'
  '<tr><td>3 · + Health anxiety</td><td><b>0.317</b></td><td><b>+18.4%</b></td><td>&lt; 0.001</td></tr></table><p>Final model: F = 6.48, p &lt; 0.001; adjusted R² 0.268; all VIF low.</p>')
w(cols([('B', 'how many CSS points change for 1 unit of the predictor, with all others held constant. For yes/no predictors: difference between “yes” and the reference group.'),
        ('95% CI', 'if it crosses 0 → not significant'), ('β', 'standardised B: lets you compare predictors measured on different scales. Bigger = stronger.'),
        ('Constant', 'predicted CSS when every predictor is 0. Not meaningful here; ignore it.'), ('ref.', 'the comparison group for categories: age 20–29; non-health employed')]))
w('<h4>Walk-through</h4>' + steps(['<b>Health anxiety</b>: B = 0.68 (0.53–0.84), β = <b>0.48</b>, p &lt; 0.001 → each extra SHAI point adds 0.68 CSS points; 10 points more anxiety ≈ 7 points more cyberchondria. The largest β by far.',
     '<b>AI users</b>: B = 5.33 → 5.3 CSS points higher than non-users, p &lt; 0.001. But with the strict definition (ticked AI only) B = 1.49, p = 0.21 → <b>not robust</b>.',
     '<b>Age 30–39</b> (B 6.27, p = 0.001) and <b>≥ 40</b> (B 3.98, p = 0.041) higher than 20–29. Why, when Table 6 showed no age difference in CSS (p = 0.288)? Because older people have <i>lower</i> health anxiety but the <i>same</i> cyberchondria; once anxiety is held constant, their searching is relatively higher. This is exactly what adjustment does.',
     'Gender, occupation, chronic condition, language, trust and motives: all CIs cross 0 → no independent effect.']))
w(say('Who you are explains only 3% of cyberchondria; digital habits add 10%, and health anxiety adds another 18%, to 32% in total. Health anxiety is by far the strongest predictor, beta 0.48. The AI effect disappears when only people who ticked AI are counted.') +
  q([('What is the difference between B and β?', 'B is in real units (CSS points per SHAI point); β puts every predictor on the same scale so their strength can be compared.'),
     ('Why hierarchical?', 'To show what health anxiety adds after demographics and digital use are already in the model: 18.4%, the biggest block.')]))
w('<h3 class="page">Table 9 · Binary logistic regression of elevated health anxiety</h3>' + table(T9, hi=('Cyberchondria', 'Motive: instant', 'Age group')))
w(cols([('AOR', 'adjusted odds ratio: how many times the odds of elevated health anxiety change, holding the others constant. 1 = no effect; &gt; 1 higher; &lt; 1 lower.'), ('95% CI', 'if it includes 1 → not significant'),
        ('per 1 SD', 'cyberchondria was entered as a z-score; 1 SD = 8.4 CSS points'), ('per step', 'one age group older (e.g. 20–29 → 30–39)')]))
w('<h4>Walk-through</h4>' + steps(['Cyberchondria: AOR <b>3.12</b> (2.11–4.62) → every 8 extra CSS points triple the odds of elevated health anxiety.',
     'Searching for instant reassurance: AOR <b>3.83</b> (1.80–8.18) → almost four times the odds. The CI is wide because only 57 people had elevated anxiety.',
     'Age: AOR <b>0.61</b> per step → each older age group has 39% lower odds (1 − 0.61 = 0.39): <b>protective</b>.',
     'Chronic condition 1.51 (0.69–3.30) includes 1 → not significant here, even though it was significant on the SHAI score in Table 6 (splitting a score into yes/no loses information).']))
w('<h4>How good is the model?</h4><table class="mini"><tr><th>Check</th><th>Ours</th><th>Meaning</th></tr>'
  f'<tr><td>Omnibus χ²</td><td>χ²(11) = {L["omnibus_chi2"]:.1f}, p &lt; 0.001</td><td>the model predicts better than nothing</td></tr>'
  f'<tr><td>Nagelkerke R²</td><td>{L["nagelkerke"]:.2f}</td><td>roughly “31% explained” (a logistic version of R²)</td></tr>'
  f'<tr><td>Hosmer–Lemeshow</td><td>p = {L["HL_p"]:.2f}</td><td>here we <b>want</b> p &gt; 0.05: predicted and observed agree → good fit</td></tr>'
  f'<tr><td>AUC (ROC curve)</td><td>{L["AUC"]:.2f}</td><td>0.5 = coin toss, 0.8–0.9 good: the model separates the two groups well</td></tr>'
  f'<tr><td>Correctly classified</td><td>{L["correct"]:.0f}%</td><td>see the trap below</td></tr></table>')
w(trap('81% correct sounds impressive, but 243 of 300 (81%) did <b>not</b> have elevated anxiety, so a “model” that always guessed “no” would also be 81% correct. That is why the AUC (0.83) is the number to quote for how well the model works.'))
w(fig('fig7_forest_HA_simple', 'Figure 6: forest plot of Table 9. Dot = AOR, line = 95% CI, vertical line at 1 = no effect; orange = significant.', 72))
w(say('Three factors stand out: higher cyberchondria triples the odds of elevated health anxiety, searching for reassurance nearly quadruples them, and older age is protective. The model fits well and its AUC is 0.83.') +
  q([('Why are the odds ratios so large and wide?', 'Only 57 people had elevated anxiety for 11 predictors, about 5 per variable, so the estimates are imprecise and may be overestimated. We say so in the limitations.')]))

# ================================================================ 3.6
A_, C_, E_, H_h = MS['SHAI'], MS['CSS'], MS['HA_clin'], MS['CSS_high']
def pv_(p): return '&lt; 0.001' if p < .001 else f'= {p:.3f}'
w('<h2 class="page">3.6 Medical students compared with other participants</h2>')
w(card('Do medical students have more health anxiety and cyberchondria than the others (H2)?', 'Mann–Whitney U and χ² (unadjusted); then multiple linear and binary logistic regression adjusted for age group, gender, chronic disease and language', 'First a simple comparison of two groups. Then adjustment, because medical students differ from the others in age, and age itself is linked to health anxiety.'))
w('<h3>Table 10 · Medical students vs other participants</h3>' + table(T10, hi=('SHAI-14 score',)))
w(cols([('Medical students / Others', f'mean ± SD for the scores; n (%) for the yes/no outcomes. {MS["n_med"]} medical students, {MS["n_oth"]} others.'),
        ('p', 'unadjusted: Mann–Whitney U (scores) or χ² (yes/no)'),
        ('Adjusted effect', 'B = how many points higher medical students score once age, gender, chronic disease and language are held constant; AOR = adjusted odds ratio for the yes/no outcomes'),
        ('Adj. p', 'the p-value after that adjustment')]))
w('<h4>Walk-through</h4>' + steps([
    f'<b>SHAI, unadjusted:</b> {A_["m_med"]:.1f} vs {A_["m_oth"]:.1f}, Mann–Whitney p {pv_(A_["p_mw"])} → medical students look more health-anxious.',
    f'<b>SHAI, adjusted:</b> B = {A_["B"]:.2f} (95% CI {A_["lo"]:.2f} to {A_["hi"]:.2f}), p {pv_(A_["p_adj"])} → the CI includes 0, so the difference is <b>no longer significant</b>.',
    f'<b>Why it disappears:</b> medical students are younger, and younger participants have higher health anxiety (Table 6: 14.0 at 18–19 vs 10.2 at 30–39). Once age is held constant, being a medical student adds little. Age, not medicine, explained the difference.',
    f'<b>Elevated health anxiety:</b> {E_["pct_med"]:.1f}% vs {E_["pct_oth"]:.1f}%, χ² p {pv_(E_["p_chi"])}; adjusted AOR {E_["AOR"]:.2f} ({E_["lo"]:.2f}–{E_["hi"]:.2f}), p {pv_(E_["p_adj"])} → not significant either way.',
    f'<b>CSS:</b> {C_["m_med"]:.1f} vs {C_["m_oth"]:.1f}, p {pv_(C_["p_mw"])}; adjusted B {C_["B"]:.2f}, p {pv_(C_["p_adj"])} → <b>identical</b>. High cyberchondria {H_h["pct_med"]:.1f}% vs {H_h["pct_oth"]:.1f}%, p {pv_(H_h["p_chi"])}.']))
w('<div class="calc">Is the adjusted SHAI difference significant?\nB = 1.23, 95% CI −0.15 to 2.60  →  the interval includes 0  →  not significant (p = 0.081)</div>')
w(box('idea', 'Unadjusted vs adjusted: the key lesson of this table', '<p>A difference between two groups can be caused by a third variable that differs between them (here, <b>age</b>). Adjustment removes that third variable. If the difference disappears, the group itself was not the cause.</p>'))
w(say(f'Before adjustment, medical students had higher health anxiety, {A_["m_med"]:.1f} against {A_["m_oth"]:.1f}, but after adjusting for age and other factors the difference was no longer significant, because medical students are younger. Their cyberchondria was the same as everyone else\'s. Hypothesis 2 was not supported.') +
  trap('Do not say “medical students are more anxious”. Say “they scored higher only before adjustment; the difference reflected their younger age”.') +
  q([('Is “medical students\' disease” real, then?', 'Not in our sample: knowing more about disease did not make students search more anxiously, but it did not protect them either. A Palestinian study with the same SHAI cut-off agrees; an Egyptian study found high cyberchondria in medical students but had no comparison group.'),
     ('Why adjust for these four variables?', 'Age, gender, chronic disease and language can all affect health anxiety and differ between medical students and the others, so they could create a false difference.'),
     ('Medical students were 44% of the sample. Does that bias the main result?', 'Being a medical student did not change health anxiety or cyberchondria after adjustment, so the high share of medical students is unlikely to explain the main association.')]))

# ================================================================ Part C hypotheses
w('<h2 class="page">Part C · The hypotheses, with the evidence</h2><table class="mini"><tr><th>Hypothesis</th><th>Verdict</th><th>Evidence</th></tr>' + ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in [
    ('H1 · More health anxiety → more cyberchondria, especially distress and excessiveness, independently of other factors', 'Supported', 'r = 0.47 (0.38–0.55); excessiveness 0.46 and distress 0.45 strongest; partial r = 0.48; health anxiety adds 18.4%, β = 0.48 (Tables 5 and 8, Figure 4)'),
    ('H2 · Medical students have higher health anxiety and cyberchondria than other participants', 'Not supported', 'SHAI higher only before adjustment (13.3 vs 11.6, p = 0.004; adjusted p = 0.081); CSS identical (28.9 vs 28.9) (Table 10)')]) + '</table>')
w(say('Hypothesis 1 was supported: health anxiety and cyberchondria are linked, independently of other factors. Hypothesis 2 was not: medical students were not at higher risk once age was taken into account.'))
w('<h3>The never-say list</h3><table class="mini"><tr><th>Never say</th><th>Say instead</th></tr>' + ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in [
    ('Health anxiety causes cyberchondria', 'is associated with / is linked to'), ('19% have health anxiety disorder', '19% scored in the elevated range on a screening tool'),
    ('AI makes people anxious', 'we found no reliable independent effect of AI use'), ('Medical students are more anxious', 'they scored higher only before adjustment for age'),
    ('Our results represent Baghdad', 'a young online convenience sample'), ('81% accuracy shows the model is good', 'the AUC of 0.83 shows good discrimination')]) + '</table>')

# ================================================================ Part D practice
PR = [
 ('Table 6: social-media users SHAI 15.8 vs 11.9, p = 0.001. Interpret.', 'Social-media users have higher health anxiety; Mann–Whitney p = 0.001, so unlikely to be chance.'),
 ('Table 8: “Female B −0.05 (−1.82 to 1.72), p = 0.954.” Interpret.', 'No difference between women and men once other factors are held constant; the CI includes 0.'),
 ('Table 9: “Chronic condition AOR 1.51 (0.69–3.30).” Significant?', 'No: the CI includes 1.'),
 ('Table 10: medical students SHAI B = 1.23 (−0.15 to 2.60), p = 0.081. Interpret.', 'After adjustment, medical students score 1.2 points higher, but the CI includes 0, so the difference is not significant.'),
 ('What does r² = 0.22 mean?', 'Health anxiety accounts for about 22% of the differences in cyberchondria.'),
 ('A Kruskal–Wallis p = 0.008 for SHAI by age. Which age group differs?', 'The test shows only that the groups differ overall; the means show the youngest (18–19, 14.0) highest.'),
 ('Hosmer–Lemeshow p = 0.50. Good or bad?', 'Good: we want p > 0.05; the model fits.'),
 ('Why did the medical-student difference in SHAI disappear after adjustment?', 'Medical students are younger, and younger people had higher health anxiety; age explained the difference.'),
 ('Table 7: V = 0.26. How strong?', 'Small to medium (0.1 small, 0.3 medium).'),
 ('Why is age significant in Table 8 but not for CSS in Table 6?', 'Adjustment: older people have lower anxiety but similar searching; holding anxiety constant reveals their relatively higher cyberchondria.'),
]
w('<h2 class="page">Part D · Practice: read the row yourself</h2><p>Cover the answers (next page). Say each answer out loud in one or two sentences.</p><ol>' + ''.join(f'<li style="margin:7px 0">{a}</li>' for a, _ in PR) + '</ol>')
w('<h3>Answers</h3><ol>' + ''.join(f'<li style="margin:6px 0">{b}</li>' for _, b in PR) + '</ol>')
w('<h3>One-page summary of numbers</h3><table class="mini"><tr><th>What</th><th>Number</th><th>Where</th></tr>' + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in [
    ('Participants', '300; 62.3% aged 20–29; 44.0% medical students', 'Table 1'), ('AI ticked / search engines', '78.0% (88.7% incl. named) / 56.3%', 'Table 2'),
    ('Delay when reassured / never tell', '34.7% / 31.7%', 'Table 2, Fig 3'), ('SHAI / CSS mean', '12.35 ± 5.83 / 28.86 ± 8.36', 'Table 3'), ("Cronbach's α", '0.81 / 0.86', 'Table 3'),
    ('Elevated health anxiety', '19.0% (15.0–23.8); 7.3% at 22; 0.7% at 29', 'Table 4'), ('Main correlation', 'r 0.47 (0.38–0.55); ρ 0.47; partial 0.48; r² 22%', 'Table 5'),
    ('High CSS by elevated HA', '52.6% vs 23.0%; OR 3.71', 'Table 7'), ('Regression', 'R² 0.030 → 0.133 → 0.317; SHAI B 0.68, β 0.48', 'Table 8'),
    ('AI effect', '+5.33 inclusive; +1.49, p 0.21 strict', 'Table 8'), ('Logistic', 'AOR 3.12 / 3.83 / 0.61; AUC 0.83; H–L p 0.50', 'Table 9'),
    ('Medical students vs others', 'SHAI 13.3 vs 11.6 (p 0.004; adjusted 0.081); CSS 28.9 vs 28.9', 'Table 10'), ('Hypotheses', 'H1 supported; H2 not supported', '')]) + '</table>')
w('</body></html>')
open(HTML, 'w').write('\n'.join(H_)); print('wrote', HTML)
