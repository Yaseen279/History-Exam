"""Meeting guide for Student 2: Monday meeting with the supervisor about her corrections, the AI-definition fix
and the completed Tables 3, 6 and 10, plus a recap of the whole study and likely questions.
Usage: python3 19_monday_meeting.py <medians_by_group.json> <out.html>   (then print to PDF)"""
import sys, json, html as H

MED = json.load(open(sys.argv[1])); OUT = sys.argv[2]
e = H.escape
CSS = """
@page { size: A4; margin: 15mm 15mm 15mm 15mm; }
* { box-sizing: border-box; }
body { font-family: Carlito, Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.8pt; line-height: 1.5; color: #1d2230; margin: 0; }
h1 { font-family: Caladea, Cambria, Georgia, serif; font-size: 26pt; color: #1F3B4D; margin: 0 0 4px; line-height: 1.1; }
h2 { font-family: Caladea, Cambria, Georgia, serif; font-size: 16.5pt; color: #1F3B4D; margin: 0 0 8px; padding-bottom: 4px; border-bottom: 2.5px solid #1F3B4D; page-break-after: avoid; }
h3 { font-size: 12.3pt; color: #b4541c; margin: 13px 0 5px; page-break-after: avoid; }
p { margin: 3px 0 7px; } ul, ol { margin: 3px 0 8px; padding-left: 20px; } li { margin: 3px 0; }
.page { page-break-before: always; }
.lead { font-size: 12pt; color: #46506a; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.6pt; page-break-inside: avoid; }
th { background: #1F3B4D; color: #fff; text-align: left; padding: 4px 6px; }
td { padding: 4px 6px; border-bottom: 1px solid #dfe5ea; vertical-align: top; }
tr.grp td { background: #e7eef3; font-weight: 700; color: #1F3B4D; }
.sm { font-size: 9pt; } .sm td, .sm th { padding: 3px 5px; }
.box { border-radius: 7px; padding: 8px 12px; margin: 9px 0; page-break-inside: avoid; }
.box .bt { font-weight: 700; font-size: 9pt; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 3px; }
.box p { margin: 2px 0 4px; }
.say { background: #e6f2ec; border-left: 5px solid #1e7a52; } .say .bt { color: #1e7a52; }
.warn { background: #fbecef; border-left: 5px solid #9d1c4a; } .warn .bt { color: #9d1c4a; }
.idea { background: #fff6e5; border-left: 5px solid #b4541c; } .idea .bt { color: #b4541c; }
.ask { background: #eef0fb; border-left: 5px solid #3d3a9e; } .ask .bt { color: #3d3a9e; }
.qq { font-weight: 700; margin-top: 7px !important; } .aa { margin-left: 10px !important; }
mark { background: #fff07a; padding: 0 2px; }
.ar { direction: rtl; text-align: right; font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 11pt; line-height: 1.9; }
.check li { list-style: none; margin-left: -18px; } .check li::before { content: "☐  "; }
.big { font-size: 15pt; font-weight: 700; color: #1F3B4D; }
"""
def box(kind, title, body): return f'<div class="box {kind}"><div class="bt">{title}</div>{body}</div>'
def say(t): return box('say', 'Say it', f'<p>{t}</p>')
def qa(pairs): return box('ask', 'If she asks', ''.join(f'<p class="qq">{q}</p><p class="aa">{a}</p>' for q, a in pairs))
def tbl(head, rows, cls=''):
    h = f'<table class="{cls}"><tr>' + ''.join(f'<th>{x}</th>' for x in head) + '</tr>'
    for r in rows:
        if len(r) > 1 and all(str(x) == '' for x in r[1:]):
            h += f'<tr class="grp"><td colspan="{len(head)}">{r[0]}</td></tr>'
        else:
            h += '<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>'
    return h + '</table>'

W = []; w = W.append
w(f'<!doctype html><html><head><meta charset="utf-8"><title>Monday Meeting Guide</title><style>{CSS}</style></head><body>')

# ---------------------------------------------------------------- cover
w('''<div style="margin-top:28mm"><p class="lead" style="letter-spacing:.12em;text-transform:uppercase;font-size:10pt;color:#b4541c">Student 2 · Meeting with Dr. Thikra</p>
<h1>Monday Meeting Guide</h1>
<p class="lead">Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad</p>
<p style="margin-top:10mm">The meeting will most likely cover four things. This guide prepares each one, with what to say and the numbers to bring.</p>
<ol><li><b>Her corrections</b> (yellow) and her requests (red): what she changed and what you did.</li>
<li><b>The AI-definition mistake</b> (the 32 participants): what went wrong, how it was fixed, the new result.</li>
<li><b>The completed tables</b>: Table 3 (α by language), Tables 6 and 10 (medians).</li>
<li><b>General questions</b> about the study: a recap of everything, with model answers.</li></ol>
<p>The last page is a checklist of what to bring and a one-page summary of numbers.</p>
<h3 style="margin-top:10mm">Reading time</h3><p>About <b>60–75 minutes</b>. Sections 1–3 are what she will ask about; read them twice. Section 4 is backup.</p></div>''')

# ---------------------------------------------------------------- 1 her corrections
w('<h2 class="page">1 · Her corrections, and what you did with each</h2>')
w('<p>Yellow = she rewrote it herself. Red = she asked you to do something. You keep all her yellow edits.</p>')
w(tbl(['Section', 'What she did', 'Status'], [
    ['1.7 → 1.6', 'Asked to <b>move</b> “Studies of medical students in the region point in different directions…” to section 1.6', 'To do'],
    ['2.3 Questionnaire', 'Rewrote: Arabic wording “prepared by the research team without formal back-translation or full cross-cultural adaptation”', 'Keep'],
    ['2.4 AI-chatbot user', 'Added the full <b>inclusive vs strict</b> definition paragraph', 'Keep; wording depends on the AI fix (section 2)'],
    ['2.5 Statistics', 'Added “Cronbach’s α <b>for the full sample</b>”', 'Keep; α by language ready (section 3)'],
    ['3.1 Behaviour', 'Wording: “the information they had found”, “A total of 34.7%…”', 'Keep'],
    ['3.2 Levels', 'Wrote that language-specific α “were not calculated… cannot be confirmed”', '<b>Numbers ready</b> → replace the sentence (section 3)'],
    ['3.3 Correlation', '“unchanged” → “similar”; “gender” → “six”', 'Keep; fix “six” → “sex”'],
    ['3.5 Predictors', 'Added the AI 95% CI, the sensitivity sentence, and “57 events/11 predictors ≈ 5.2”', 'Keep; AI sentence to update (section 2)'],
    ['3.6 Medical students', '“the same” → “similar”', 'Keep'],
    ['4.3 AI chatbots', 'Rewrote the whole paragraph around the strict definition', 'To update after her approval (section 2)'],
    ['5.2 Recommendations', 'Rewrote the clinicians’ recommendation formally', 'Keep'],
    ['Tables 3, 6, 10', 'Asked for α by language and <b>median (IQR)</b> columns', '<b>Numbers ready</b> (section 3), to insert'],
    ['Objective 1', 'The word “describe” in red, no note', '<b>Ask her</b> what she meant']]))
w(box('idea', 'Three small slips in her edits (fix quietly, no need to point them out)', '<ul><li>2.4: 234 met the strict definition “<b>including</b>” 32 → should be <b>excluding</b> (266 − 32 = 234).</li><li>3.3: “age, <b>six</b>” → “age, <b>sex</b>”.</li><li>3.5: “<b>≥ 40 or older</b>” → “≥ 40” (or “40 or older”), not both.</li></ul>'))
w(box('warn', 'Also fix before Monday: the dates', '<p>The thesis says data were collected until <b>October</b> (Abstract and 2.1). The data file shows the last response on <b>11 September 2026</b>. If she or the department opens the SPSS file, the dates must match. Change both to September.</p>'))

# ---------------------------------------------------------------- 2 the AI fix
w('<h2 class="page">2 · The AI-definition mistake (the 32 participants)</h2>')
w('<h3>What happened, in plain words</h3><ol>'
  '<li>In Q8 people ticked the tools they use. In Q9 they named the chatbot they use.</li>'
  '<li><b>32 people named a chatbot in Q9 (e.g. ChatGPT) but did not tick “AI chatbots” in Q8.</b></li>'
  '<li>Main analysis (inclusive): they were counted as <b>AI users</b>, correctly, because they named one. → 266 users vs 34 non-users.</li>'
  '<li>The check (strict definition) <b>moved them into the non-user group</b>. That was the mistake: people who named ChatGPT are not non-users. And they had high cyberchondria (median 34), so they made the “non-users” look worse and hid the difference.</li>'
  '<li><b>The fix:</b> exclude the 32 from the check instead of moving them. → 234 users vs 34 non-users.</li></ol>')
w(tbl(['', 'AI users / non-users', 'Adjusted effect of AI on cyberchondria', 'Result'], [
    ['<b>Inclusive (main analysis)</b>', '266 / 34', 'B = 5.33 (95% CI 2.57–8.09), p &lt; 0.001', 'Significant'],
    ['Strict (old check, 32 put in non-users)', '234 / 66', 'B = 1.49 (−0.85–3.83), p = 0.21', 'Not significant'],
    ['<b>Corrected check (32 excluded)</b>', '234 / 34', '<mark>B = 4.38 (95% CI 1.68–7.08), p = 0.002</mark>', '<b>Significant</b>']]))
w('<p>Unadjusted with the 32 excluded: cyberchondria 29.2 vs 24.0, Mann–Whitney p &lt; 0.001; high cyberchondria 28.6% vs 8.8%, p = 0.012.</p>')
w(say('We made a mistake in the sensitivity check: 32 people who named a chatbot were counted as non-users. When we excluded them instead, the association between AI use and cyberchondria stayed significant, B = 4.38, p = 0.002. So AI use is associated with higher cyberchondria, independently of health anxiety.'))
w(qa([('Why did you exclude them instead of keeping the strict definition?', 'Because they named a chatbot, so they are not non-users. Putting them in the non-user group was misclassification. Excluding unclear cases is the standard way to check that a result does not depend on them.'),
      ('Isn’t this just changing the analysis to get significance?', 'No: the main analysis was already significant (p &lt; 0.001), and it does not change. Only the check was corrected, for a clear reason (misclassification), and we report it transparently.'),
      ('What changes in the thesis?', '2.4 (the definition paragraph describes exclusion instead of reclassification), 3.5 and 4.3 (the result), and the Abstract and Conclusion: AI use is associated with higher cyberchondria.'),
      ('Why do those 32 have high cyberchondria?', 'Probably chance. Nothing about naming a chatbot without ticking a box should change cyberchondria; it only mattered because the non-user group is small (34).')]))
w(box('idea', 'Your decision before the meeting', '<p>Ask her approval to update 2.4, 3.5, 4.3, the Abstract and Conclusion 4 with the corrected result. She wrote those paragraphs, so she should agree first.</p>'))

# ---------------------------------------------------------------- 3 the tables
w('<h2 class="page">3 · The completed tables</h2>')
a = MED['alpha']
w('<h3>Table 3 · Cronbach’s α by language</h3>' + tbl(['Responders', 'n', 'SHAI-14 α', 'CSS-12 α'], [
    ['Full sample', 300, '0.81', '0.86'], ['Arabic', a['Arabic'][0], f"{a['Arabic'][1]:.2f}", f"{a['Arabic'][2]:.2f}"], ['English', a['English'][0], f"{a['English'][1]:.2f}", f"{a['English'][2]:.2f}"]]))
w(say('Reliability was good and almost identical in both languages: SHAI-14 0.81 in Arabic and 0.81 in English; CSS-12 0.86 and 0.88. So the Arabic wording worked as well as the English.'))
w('<p><b>Replaces her sentence</b> “language-specific Cronbach’s α values were not calculated… cannot be confirmed” with: “Internal consistency was similar in Arabic (n = 212; α = 0.81 and 0.86) and English responders (n = 88; α = 0.81 and 0.88).”</p>')
w('<h3>Why medians (her point, and she is right)</h3><p>Mann–Whitney and Kruskal–Wallis are rank tests, used because the scores are not normally distributed. Rank tests go with the <b>median (IQR)</b>: the middle person and the range of the middle half. The p-values do not change; only how each group is described. Our scores are only mildly skewed, so medians are close to the means.</p>')
w('<h3>Table 6 · Median (IQR) by group</h3>' + tbl(['Group', 'n', 'SHAI-14 median (IQR)', 'CSS-12 median (IQR)'], MED['t6'], 'sm'))
t10 = MED['t10']
w('<h3>Table 10 · Medical students vs others</h3>' + tbl(['', 'Medical students (n = 132)', 'Others (n = 168)', 'p (Mann–Whitney)'], [
    ['SHAI-14 median (IQR)', t10['SHAI'][0], t10['SHAI'][1], '0.004'], ['CSS-12 median (IQR)', t10['CSS'][0], t10['CSS'][1], '0.989']]))
w(box('idea', 'Text in 3.4 and 3.6 too', '<p>The text gives means with Mann–Whitney p-values in two places (reassurance seekers and AI users in 3.4; medical students in 3.6). Medians are added there as well so the thesis is consistent, e.g. medical students SHAI median 12.5 vs 11, p = 0.004.</p>'))
w(qa([('Why did you report means before?', 'We kept the format of the first draft. You were right that rank tests should be described with medians, so we added them.'),
      ('Do the medians change any conclusion?', 'No. The tests and p-values are the same; the medians tell the same story as the means.')]))

# ---------------------------------------------------------------- 4 recap of the whole study
w('<h2 class="page">4 · The whole study in two pages (backup)</h2>')
w(tbl(['Part', 'The essentials'], [
    ['<b>Aim</b>', 'Relationship between health anxiety and cyberchondria among adults in Baghdad, focusing on AI chatbots and medical students.'],
    ['<b>Design</b>', 'Analytical cross-sectional online survey, bilingual Google Form, convenience + snowball sampling, 17 July – 11 September 2026, <b>n = 300</b>, one response per Google account, no missing data.'],
    ['<b>Tools</b>', '<b>SHAI-14</b> (health anxiety, 0–42, ≥ 18 elevated, Swedish cut-off) and <b>CSS-12</b> (cyberchondria, 12–60, four dimensions: excessiveness, compulsion, distress, reassurance seeking).'],
    ['<b>Hypotheses</b>', '<b>H1:</b> more health anxiety → more cyberchondria, independently of other factors. <b>H2:</b> medical students have higher health anxiety and cyberchondria.'],
    ['<b>Statistics</b>', 'SPSS 26, p &lt; 0.05. Shapiro–Wilk (not normal) → Mann–Whitney / Kruskal–Wallis; χ² / Fisher with Cramér’s V; Pearson + Spearman, partial r; hierarchical multiple linear regression; binary logistic regression.'],
    ['<b>Sample</b>', 'Young (62.3% aged 20–29), 56.3% female, 44.0% medical students.'],
    ['<b>Searching</b>', 'AI chatbots 88.7% (78.0% ticked), search engines 56.3%, ChatGPT 59.3%. After searching: 34.7% delayed care because reassured; 31.7% never tell the doctor.'],
    ['<b>Levels</b>', 'SHAI mean 12.35, median 12; <b>19.0%</b> elevated (95% CI 15.0–23.8). CSS mean 28.86, median 29. α 0.81 and 0.86.'],
    ['<b>H1</b>', '<b>Supported.</b> r = 0.47 (0.38–0.55), partial r = 0.48; regression: health anxiety adds 18.4%, β = 0.48 (strongest predictor).'],
    ['<b>H2</b>', '<b>Not supported.</b> Medical students: higher SHAI before adjustment (median 12.5 vs 11, p = 0.004) but not after adjusting for age (p = 0.081); CSS identical.'],
    ['<b>AI</b>', 'AI users: higher cyberchondria, adjusted B = 5.33 (p &lt; 0.001); holds with the 32 unclear cases excluded (B = 4.38, p = 0.002).'],
    ['<b>Logistic</b>', 'Elevated health anxiety: cyberchondria AOR 3.12 per SD, reassurance motive 3.83, older age 0.61 (protective). AUC 0.83.'],
    ['<b>Limits</b>', 'Cross-sectional (no direction), convenience sample (not generalisable), no back-translation, self-report, many tests without correction.']]))
w('<h3>Questions she might ask about the whole study</h3>' + qa([
    ('Why non-parametric tests?', 'Shapiro–Wilk showed the scores were not normally distributed, so Mann–Whitney and Kruskal–Wallis instead of the t-test and ANOVA.'),
    ('Which groups differ in Table 6?', 'Kruskal–Wallis shows only that groups differ overall. Post-hoc (Mann–Whitney with Bonferroni): 18–19 vs 30–39 (p = 0.026), students vs bachelor graduates (p = 0.032), medical students vs non-health employees (p = 0.004): younger students are more health-anxious.'),
    ('Why is H2 not supported if medical students scored higher?', 'Because the difference disappeared after adjusting for age: medical students are younger, and younger people had higher health anxiety.'),
    ('What does r = 0.47 mean?', 'A moderate link: health anxiety explains about 22% of the differences in cyberchondria.'),
    ('Why SHAI ≥ 18?', 'It best separated people with health anxiety from healthy controls in the Swedish validation study.'),
    ('What is the main clinical message?', 'Ask patients, without judgement, what they searched or asked an AI, and what they found.')]))

# ---------------------------------------------------------------- checklist
w('<h2 class="page">Checklist for Monday</h2><ul class="check">'
  '<li>Her version with the medians, α, moved paragraph and slips added (ask me to prepare it before Monday)</li>'
  '<li>Her original version, to show what she marked</li>'
  '<li>The SPSS file (.sav) and, if you have run it, the SPSS output (.spv)</li>'
  '<li>The numbers for the AI fix: B = 4.38, 95% CI 1.68–7.08, p = 0.002 (32 excluded: 234 vs 34)</li>'
  '<li>α by language: Arabic 0.81 / 0.86, English 0.81 / 0.88</li>'
  '<li>Dates fixed to September in the Abstract and 2.1</li>'
  '<li>Question for her: what did she mean by the red “describe” in Objective 1?</li>'
  '<li>Question for her: may we update 2.4, 3.5, 4.3, the Abstract and Conclusion 4 with the corrected AI result?</li></ul>')
w('<h3>If you only remember five things</h3><ol>'
  '<li>The 32 named a chatbot; we wrongly counted them as non-users in the check; excluded instead, AI stays significant (p = 0.002).</li>'
  '<li>The main analysis never changed: AI B = 5.33, p &lt; 0.001.</li>'
  '<li>α is the same in Arabic and English (0.81; 0.86 vs 0.88).</li>'
  '<li>Medians replace/accompany means because the tests are rank-based; no p-value changes.</li>'
  '<li>H1 supported (r = 0.47); H2 not supported (age explains the medical-student difference).</li></ol>')
w('<h3>The Arabic message you sent (for reference)</h3><div class="ar">دكتورة واحنا نكمل التعديلات انتبهنا لغلط سويناه بالتحليل. اكو 32 مشارك كتبوا اسم الـ chatbot اللي يستخدموه بس ما اختاروا خيار AI chatbots بالسؤال الثامن، واحنا بالغلط حسبناهم ضمن مجموعة الي ما يستخدمون AI. صححنا الغلط واستبعدناهم من التحليل، وطلعت العلاقة significant (p = 0.002).</div>')
w('</body></html>')
open(OUT, 'w').write('\n'.join(W)); print('wrote', OUT)
