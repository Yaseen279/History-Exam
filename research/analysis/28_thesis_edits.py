"""Apply the agreed corrections to the supervisor's version of the thesis:
- AI-chatbot users defined once (ticked or named a chatbot, n = 266): the strict definition and its sensitivity analysis are removed
- Tables 3, 6 and 10 completed (Cronbach's alpha by language; medians and IQR by group)
- small slips fixed (six -> sex, "≥ 40 or older")
Every change is highlighted in green in the marked copy; the clean copy has no highlights at all.
Usage: python3 28_thesis_edits.py <supervisor.docx> <data.sav> <out_marked.docx> <out_clean.docx>"""
import sys, copy
import numpy as np, pyreadstat
from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml.ns import qn

SRC, SAV, OUT_MARKED, OUT_CLEAN = sys.argv[1:5]
doc = Document(SRC)
P = doc.paragraphs
MARK = WD_COLOR_INDEX.BRIGHT_GREEN
log = []

def set_hl(run_el, on=True):
    rpr = run_el.find(qn('w:rPr'))
    if rpr is None: rpr = run_el.makeelement(qn('w:rPr'), {}); run_el.insert(0, rpr)
    for h in rpr.findall(qn('w:highlight')): rpr.remove(h)
    if on:
        h = rpr.makeelement(qn('w:highlight'), {qn('w:val'): 'green'}); rpr.append(h)

def replace(par, old, new, label):
    """Replace `old` (which may span several runs) with `new`, keeping the formatting of the run where `old` starts."""
    runs = par.runs; text = ''.join(r.text for r in runs)
    i = text.find(old)
    if i < 0: raise ValueError(f'{label}: text not found: {old[:60]}')
    j = i + len(old); pos = 0; first = None
    for r in runs:
        a, b = pos, pos + len(r.text); pos = b
        if b <= i or a >= j: continue
        keep_before = r.text[:max(0, i - a)]; keep_after = r.text[max(0, j - a):] if b > j else ''
        if first is None:
            first = r
            r.text = keep_before
            if new:
                nr = copy.deepcopy(r._r); r._r.addnext(nr)
                for t in nr.findall(qn('w:t')) + nr.findall(qn('w:tab')) + nr.findall(qn('w:br')): nr.remove(t)
                t = nr.makeelement(qn('w:t'), {}); t.text = new; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); nr.append(t)
                set_hl(nr)
                if keep_after:
                    ar = copy.deepcopy(r._r); nr.addnext(ar)
                    for t in ar.findall(qn('w:t')) + ar.findall(qn('w:tab')) + ar.findall(qn('w:br')): ar.remove(t)
                    t = ar.makeelement(qn('w:t'), {}); t.text = keep_after; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); ar.append(t)
        else:
            r.text = keep_after
    log.append(label)

def para(n, must):
    assert must in P[n].text, (n, must, P[n].text[:120]); return P[n]

# ---------------------------------------------------------------- text: one AI definition, no strict/sensitivity analysis
replace(para(37, 'not robust'), 'The association between AI use and cyberchondria was not robust to the definition of AI use.',
        'AI-chatbot users had higher cyberchondria than non-users, independently of health anxiety (B = 5.33, p < 0.001).', 'Abstract, results')
replace(para(38, 'without reliable evidence'), ', without reliable evidence that they add to cyberchondria beyond health anxiety',
        ', and their use was associated with higher cyberchondria', 'Abstract, conclusion')
p78 = para(78, 'two definitions'); start = p78.text.index('AI-chatbot use was operationalised')
replace(p78, p78.text[start:], 'a participant who reported using an AI chatbot (for example, ChatGPT or Gemini) to look for health information (n = 266, 88.7%); '
        'the remaining 34 participants were classified as non-users.', '2.4 Definitions, AI-chatbot user')
replace(para(82, "for the full sample"), 'for the full sample.', 'for the full sample and for each language version.', '2.5 Statistical analysis, alpha by language')
p99 = para(99, 'language-specific'); s99 = p99.text.index('However, language-specific')
replace(p99, p99.text[s99:], 'Internal consistency was similar in the two language versions (SHAI-14: α = 0.81 in both Arabic and English; '
        'CSS-12: α = 0.86 in Arabic and 0.88 in English).', '3.2 Reliability by language')
replace(para(107, 'age, six,'), 'age, six,', 'age, sex,', '3.3 slip: six -> sex')
p123 = para(123, 'strict definition')
replace(p123, '≥ 40 or older', '≥ 40', '3.5 slip: ≥ 40 or older')
s123 = p123.text.index('AI use was associated with a 5.33'); e123 = p123.text.index('AI-chatbot effect.') + len('AI-chatbot effect.')
replace(p123, p123.text[s123:e123], 'AI-chatbot users scored 5.33 points higher on the CSS-12 than non-users, independently of health anxiety and the other factors (95% CI 2.57–8.09; p < 0.001).',
        '3.5 AI result, strict-definition sentences removed')
replace(p123, ' In the sensitivity analyses the correlation was unchanged (r = 0.47–0.48).', '', '3.5 sensitivity sentence removed')
p142 = para(142, 'strict definition'); s142 = p142.text.index('The higher CSS-12 scores'); e142 = p142.text.index('Most participants trusted')
replace(p142, p142.text[s142:e142], 'AI-chatbot users had higher cyberchondria than non-users, and the association remained after adjustment for health anxiety and the other factors '
        '(B = 5.33, p < 0.001). Unlike a search engine, a chatbot can be questioned again and again at any hour, which may encourage repeated searching and reassurance seeking. '
        'However, the non-user group was small (n = 34), so this finding needs confirmation in larger studies. ', '4.3 AI chatbots')
replace(para(148, 'sensitivity analyses'), 'complete data, adjustment for confounders in multivariable models and sensitivity analyses',
        'complete data and adjustment for confounders in multivariable models', '4.6 strengths: sensitivity analyses removed')
p150 = para(150, 'Sample:'); replace(p150, 'cannot be generalised to Baghdad.', 'cannot be generalised to Baghdad; only 34 participants did not use AI chatbots.', '4.6 limitation: small non-user group')
replace(para(159, 'no reliable evidence'), 'There is no reliable evidence that AI use adds to cyberchondria beyond health anxiety.',
        'AI-chatbot use was associated with higher cyberchondria, independently of health anxiety.', 'Conclusion 5')

# the supervisor's placeholder instructions under Tables 3, 6 and 10 are now answered: remove them (Table 6 keeps a normal note)
replace(para(115, 'rank-based'), P[115].text, 'Note. Mann–Whitney U and Kruskal–Wallis H tests are rank-based, so median (IQR) is reported alongside mean ± SD.', 'Table 6 note')
for n, must in ((133, 'placeholders'), (102, 'not available in the analyses')):
    el = para(n, must)._p; el.getparent().remove(el); log.append(f'removed supervisor placeholder note ({must})')

for k, p in enumerate(doc.paragraphs):
    if any(w in p.text for w in ('strict definition', 'inclusive definition', 'sensitivity anal', 'not robust')): print('STILL MENTIONS IT: paragraph', k, p.text[:120])

# ---------------------------------------------------------------- tables
d, meta = pyreadstat.read_sav(SAV)
def med(x):
    q = np.percentile(np.asarray(x, float), [25, 50, 75], method='weibull'); f = lambda v: '%g' % round(v, 1)
    return f'{f(q[1])} ({f(q[0])}–{f(q[2])})'
def alpha(df):
    k = df.shape[1]; return k / (k - 1) * (1 - df.var(ddof=1).sum() / df.sum(axis=1).var(ddof=1))
def set_cell(cell, text):
    p = cell.paragraphs[0]; runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]: r._r.getparent().remove(r._r)
    else: p.add_run(text)
    set_hl(p.runs[0]._r)

# Table 3 (docx table 6): add a column with alpha in each language
t3 = doc.tables[5]
S = ['shai%d' % i for i in range(1, 15)]; C = ['css%d' % i for i in range(1, 13)]
items = [S, C, C[0:3], C[3:6], C[6:9], C[9:12]]
grid = t3._tbl.find(qn('w:tblGrid')); grid.append(copy.deepcopy(grid.findall(qn('w:gridCol'))[-1]))
for ri, row in enumerate(t3.rows):
    tc = copy.deepcopy(row._tr.findall(qn('w:tc'))[-1]); row._tr.append(tc)
for ri, row in enumerate(t3.rows):
    cell = row.cells[-1]
    if ri == 0: set_cell(cell, 'α Arabic / English')
    else:
        a_ar = alpha(d[d.language == 1][items[ri - 1]]); a_en = alpha(d[d.language == 2][items[ri - 1]])
        set_cell(cell, f'{a_ar:.2f} / {a_en:.2f}')
log.append('Table 3: alpha by language column')

# Table 6 (docx table 9): medians (IQR) by group
GROUPS = {'Age group': ('age4', None), 'Gender': ('gender', None), 'Education': ('education', None), 'Study/work': ('occupation', None), 'Chronic condition': ('chronic', None),
          'Uses AI chatbots': ('ai_user', None), 'Uses search engines': ('tool_search', None), 'Uses social media': ('tool_social', None), 'Tool profile': ('tool_profile', None),
          'Motive: reassurance': ('mot_reassurance', None), 'Motive: self-diagnosis': ('mot_selfdx', None), 'Trust in online/AI': ('trust', None), 'Language': ('language', None)}
t6 = doc.tables[8]; var = None; filled = 0
for row in t6.rows[1:]:
    label = row.cells[0].text.strip()
    if label in GROUPS: var = GROUPS[label][0]; continue
    labels = meta.variable_value_labels[var]
    code = next((k for k, v in labels.items() if v.lower() == label.lower()), None)
    if code is None and label.isdigit(): code = float(label)
    if code is None: raise ValueError(f'Table 6: no group for {label!r} in {var}')
    g = d[d[var] == code]; assert len(g) == int(row.cells[1].text), (label, len(g), row.cells[1].text)
    set_cell(row.cells[6], med(g.SHAI)); set_cell(row.cells[7], med(g.CSS)); filled += 1
log.append(f'Table 6: medians (IQR) for {filled} groups')

# Table 10 (docx table 13): medians for medical students vs others
t10 = doc.tables[12]; ms, ot = d[d.medical_student == 1], d[d.medical_student == 0]
set_cell(t10.rows[1].cells[6], f'{med(ms.SHAI)} vs {med(ot.SHAI)}'); set_cell(t10.rows[1].cells[7], '—')
set_cell(t10.rows[3].cells[6], '—'); set_cell(t10.rows[3].cells[7], f'{med(ms.CSS)} vs {med(ot.CSS)}')
log.append('Table 10: medians (IQR) for medical students vs others')

# Table 6: the CSS columns had no font size set and printed larger than the rest of the table
from docx.shared import Pt, Emu
for row in t6.rows:
    for c in (4, 5):
        for p_ in row.cells[c].paragraphs:
            for r in p_.runs: r.font.size = Emu(107950)
# Table 10: share the page width between its eight columns so p-values do not break
from docx.shared import Inches
W10 = [1.15, 0.75, 0.75, 0.45, 1.05, 0.45, 0.75, 0.75]
gc = t10._tbl.find(qn('w:tblGrid')).findall(qn('w:gridCol'))
for g, w in zip(gc, W10): g.set(qn('w:w'), str(int(w * 1440)))
for row in t10.rows:
    for c, w in zip(row.cells, W10): c.width = Inches(w)

# Table 6 note: plain small black text like the thesis's other table notes
from docx.shared import RGBColor
for p_ in doc.paragraphs:
    if p_.text.startswith('Note. Mann–Whitney U and Kruskal–Wallis H'):
        for r in p_.runs: r.font.color.rgb = RGBColor(0, 0, 0); r.font.italic = False; r.font.size = Pt(9)
# Table 10: the two median columns get the same dark header shading as the rest of the header row
def copy_shading(src_cell, dst_cell):
    sp = src_cell._tc.get_or_add_tcPr().find(qn('w:shd'))
    if sp is None: return
    dp = dst_cell._tc.get_or_add_tcPr()
    for old in dp.findall(qn('w:shd')): dp.remove(old)
    dp.append(copy.deepcopy(sp))
    for p_ in dst_cell.paragraphs:
        for r in p_.runs: r.font.color.rgb = RGBColor(255, 255, 255); r.font.bold = True
for c in (6, 7): copy_shading(t10.rows[0].cells[0], t10.rows[0].cells[c]); copy_shading(t6.rows[0].cells[0], t6.rows[0].cells[c])
# Table 6: keep the caption and note on the same page as the table (they were stranded on a page of their own)
for p_ in doc.paragraphs:
    if p_.text.startswith('Table 6. ') or p_.text.startswith('Note. Mann–Whitney U and Kruskal–Wallis H'): p_.paragraph_format.keep_with_next = True

for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            assert '[Calculate' not in c.text, 'placeholder left in a table'
doc.save(OUT_MARKED)

# clean copy: same document, every highlight removed (the supervisor's yellow and our green)
clean = Document(OUT_MARKED)
for el in clean.element.body.iter(qn('w:highlight')): el.getparent().remove(el)
clean.save(OUT_CLEAN)
print('\n'.join('changed: ' + x for x in log)); print('wrote', OUT_MARKED, 'and', OUT_CLEAN)
