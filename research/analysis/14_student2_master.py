"""Student 2 master file: everything in one document.
Merges the Student 2 guide and the 'Results from zero' guide (both generated first) and adds the whole study
(aim, objectives, hypotheses and verdicts, methods, statistical analysis, conclusions, recommendations, limitations)
taken word for word from the thesis.
Usage: python3 14_student2_master.py <output dir> <student guides dir>"""
import sys, re, json, html
from docx import Document

OUT, GD = sys.argv[1], sys.argv[2]
N = json.load(open(f'{OUT}/study/numbers.json')); FIG = N['figdir']
e = html.escape

def parts(path):
    """Split a generated guide into {h2 title: html} plus its CSS."""
    t = open(path).read()
    css = re.search(r'<style>(.*?)</style>', t, re.S).group(1)
    body = re.search(r'<body>(.*)</body>', t, re.S).group(1)
    chunks = re.split(r'(<h2[^>]*>.*?</h2>)', body)
    out = {'_cover': chunks[0]}
    for i in range(1, len(chunks), 2):
        title = re.sub(r'<[^>]+>', '', chunks[i])
        out[title] = chunks[i + 1]
    return out, css

G, css1 = parts(f'{GD}/Student2_Guide.html')
Z, css2 = parts(f'{GD}/Student2_Results_From_Zero.html')
def g(prefix, src):
    k = [k for k in src if k.startswith(prefix)]; assert len(k) == 1, (prefix, list(src)); return src[k[0]]

# ---------------------------------------------------------------- thesis text, word for word
ps = [p.text for p in Document(f'{OUT}/Cyberchondria_Research_Baghdad.docx').paragraphs]
def between(a, b):
    i, j = ps.index(a), ps.index(b)
    return [p for p in ps[i + 1:j] if p.strip() and not re.match(r'^(Table|Figure) \d+\. ', p)]
def paras(lst): return ''.join((f'<h4>{e(p)}</h4>' if re.match(r'^\d\.\d+ ', p) else f'<p>{e(p)}</p>') for p in lst)
aim = between('1.8 Aim and objectives', '2. Method')
design = between('2.1 Study design and setting', '2.6 Statistical analysis')
stats = between('2.6 Statistical analysis', '2.7 Ethical considerations')
ethics = between('2.7 Ethical considerations', '3. Results')
concl = between('5.1 Conclusions', '5.2 Recommendations')
recs = between('5.2 Recommendations', '6. References')
lims = between('4.8 Strengths and limitations', '5. Conclusions and Recommendations')
rationale = between('1.7 Rationale', '1.8 Aim and objectives')
abstract = between('Summary / Abstract', '1. Introduction')

# ---------------------------------------------------------------- assemble
CSS = css1 + '\n' + css2 + """
.toc li { margin: 3px 0; } .sec { font-size: 11pt; color: #555; }
.verdict td:first-child { font-weight: bold; width: 45%; } .verdict td:nth-child(2) { width: 17%; }
h2 { color: #0B5394; border-bottom-color: #0B5394; }
"""
H = [f'<!doctype html><html><head><meta charset="utf-8"><title>Student 2 Master File</title><style>{CSS}</style></head><body>']
w = H.append
SECTIONS = [
    ('1', 'The study in full (aim, hypotheses, methods, conclusions)'),
    ('2', 'Whole-study essentials: two-minute script, core facts, terms'),
    ('3', 'The Results as one story'),
    ('4', 'Statistics from zero (with our numbers)'),
    ('5', 'Every table and figure: why it is there and how to read it'),
    ('6', 'Your chapter, section by section'),
    ('7', 'Statistical analysis (Section 2.6, word for word)'),
    ('8', 'Your slides: what to point at, and the full scripts'),
    ('9', 'Questions and model answers, plus drills'),
    ('10', 'Your key sources'),
    ('11', 'Editing your chapter'),
    ('12', 'Your 14-day plan, self-test and day-before checklist'),
    ('13', 'Cheat sheet'),
]
w(f'''<h1>Student 2 · Master File</h1>
<p style="font-size:12.5pt;color:#555">Everything you need in one place: the study, your Results part from zero, your slides, your questions.<br>
Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad</p>
<div class="box"><b>Your role.</b> You present slides 13–23 (Results, about 6 minutes) and you are the team's statistics person.
You own Chapter 3 (Results), Tables 1–13, Figures 3–11 and Appendix A, and you must understand Section 2.6 (Statistical analysis).
Handover line at the end of your part: “Those are our results. My colleague will now discuss what they mean.”</div>
<h3>Contents</h3><ol class="toc">''' + ''.join(f'<li><b>{t}</b></li>' for _, t in SECTIONS) + '''</ol>
<h3>How to study this file</h3>
<table><tr><th>Day</th><th>Read</th></tr>
<tr><td>1</td><td>Section 1 (the study) and Section 2 (essentials). Say the two-minute script out loud three times.</td></tr>
<tr><td>2</td><td>Section 3 (the story) and Section 4, lessons 1–12.</td></tr>
<tr><td>3</td><td>Section 4, lessons 13–25. Explain each lesson out loud using our numbers.</td></tr>
<tr><td>4–5</td><td>Section 5 (every table and figure), with the thesis open beside you.</td></tr>
<tr><td>6</td><td>Sections 6 and 7 (your chapter and the methods).</td></tr>
<tr><td>7–8</td><td>Section 8: practise your slides alone, three times, with a timer.</td></tr>
<tr><td>9–10</td><td>Section 9: answer every question out loud; record yourself once.</td></tr>
<tr><td>11–14</td><td>Sections 10–12; rehearsals with the team; self-test until 100%; Section 13 in your pocket.</td></tr></table>''')

# 1 the study in full
w('<h2 class="page">1 · The study in full</h2>')
w('<h3>Title</h3><p><b>Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad: An Online Cross-Sectional Survey</b></p>')
w('<h3>Abstract (as in the thesis)</h3>' + paras(abstract))
w('<h3>Why the study was done (Rationale, 1.7)</h3>' + paras(rationale))
w('<h3>Aim, objectives and hypotheses (1.8, word for word)</h3>' + paras(aim))
w('<h3>Were the hypotheses supported? (memorise this table)</h3><table class="verdict"><tr><th>Hypothesis</th><th>Verdict</th><th>Evidence (where)</th></tr>' + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in [
    ('H1: health anxiety is positively associated with cyberchondria, most with distress and excessiveness', 'Supported', f'r = {N["r"]} ({N["rci"]}); excessiveness {N["rE"]} and distress {N["rD"]} strongest (Table 6, Figure 5)'),
    ('H2: independent of socio-demographic and digital-use factors', 'Supported', f'partial r = {N["pr"]}; health anxiety adds {N["dR2"]}, β {N["beta"]} (Table 9)'),
    ('H3: excessive searching mediates health anxiety → post-search distress', 'Supported statistically, not causally', f'indirect {N["mA"]} ({N["mAci"]}), but reverse path also {N["mD"]} (Table 12, Figure 9)'),
    ('H4: cyberchondria ↔ care-seeking and strained relationship', 'Partially supported', f'only more disclosure survived FDR (AOR {N["nsC"]}, q {N["nsCq"]}); urgent visits, strained relationship exploratory (Table 11)'),
]) + '</table>')
w('<div class="say">H1 and H2 were supported; H3 was supported statistically but not causally; H4 was only partially supported.</div>')
w(f'<img class="fig" src="file://{FIG}/fig0a_framework.png"><p class="small" style="text-align:center">Figure 1: conceptual framework (where each hypothesis sits).</p>')
w('<h3>Methods (2.1–2.5, word for word; 2.6 is in Section 7)</h3>' + paras(design))
w(f'<img class="fig" src="file://{FIG}/fig0b_flowchart.png"><p class="small" style="text-align:center">Figure 2: study flowchart.</p>')
w('<h3>Ethics (2.7)</h3>' + paras(ethics))
w('<h3>Conclusions (5.1, word for word)</h3>' + paras(concl))
w('<h3>Recommendations (5.2, word for word)</h3>' + paras(recs))
w('<h3>Strengths and limitations (4.8, word for word)</h3>' + paras(lims))

# 2 essentials (from the Student 2 guide Part 1)
w('<h2 class="page">2 · Whole-study essentials</h2>' + g('Part 1', G))
# 3, 4, 5 from the from-zero guide
w('<h2 class="page">3 · The Results as one story</h2>' + g('Part A', Z))
w('<h2 class="page">4 · Statistics from zero (with our numbers)</h2>' + g('Part B', Z))
w('<h2 class="page">5 · Every table and figure: why it is there and how to read it</h2>' + g('Part C', Z))
# 6 chapter walkthrough (drop its duplicate figure gallery, covered in section 5)
ch = g('Part 2', G); ch = ch.split('<h3>How to read your figures</h3>')[0]
w('<h2 class="page">6 · Your chapter, section by section</h2>' + ch)
# 7 statistical analysis verbatim
w('<h2 class="page">7 · Statistical analysis (Section 2.6, word for word)</h2><p>You are the team\'s statistics person. Read this until you can explain each method in one sentence (Section 4 gives the plain-language version of each).</p>' + paras(stats))
# 8 slides
w('<h2 class="page">8 · Your slides</h2><h3>A. What to point at and what to say (short version)</h3>' + g('Part D', Z) + '<h3>B. Full scripts (speaker notes)</h3>' + g('Part 4', G))
# 9 questions + drills
w('<h2 class="page">9 · Questions and model answers</h2>' + g('Part 5', G) + '<h3>E. Drills: explain it simply</h3>' + g('Part E', Z))
# 10 sources, 11 editing
w('<h2 class="page">10 · Your key sources</h2>' + g('Part 3', G))
w('<h2 class="page">11 · Editing your chapter</h2>' + g('Part 6', G))
# 12 plan + self-test + checklist
w('<h2 class="page">12 · Plan, self-test and checklist</h2><h3>14-day plan</h3>' + g('Part 7', G) + '<h3>Self-test</h3>' + g('Part 8', G) + '<h3>Day-before checklist</h3>' + g('Part 9', G))
# 13 cheat sheet
w('<h2 class="page">13 · Cheat sheet</h2>' + g('Cheat sheet', Z))
w('</body></html>')
path = f'{GD}/Student2_Master_File.html'
open(path, 'w').write('\n'.join(H)); print('wrote', path)
