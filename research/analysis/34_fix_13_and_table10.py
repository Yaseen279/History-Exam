"""Section 1.3 body text was in the Heading 2 style (crammed); give it normal body formatting.
Table 10: drop the two side columns and show median (IQR) under the mean in the group columns; add a note.
Usage: python3 34_fix_13_and_table10.py <in.docx> <out.docx>"""
import sys, copy
from docx import Document
from docx.oxml.ns import qn
d = Document(sys.argv[1]); P = d.paragraphs

# 1. body paragraphs that carry a heading style
ref = next(p for p in P if p.text.startswith('Health anxiety is a persistent preoccupation'))
for p in P:
    if p.style.name.startswith('Heading') and len(p.text) > 120:
        p.style = ref.style
        old = p._p.pPr
        if old is not None: p._p.remove(old)
        p._p.insert(0, copy.deepcopy(ref._p.pPr))
        rr = ref.runs[0]._r.find(qn('w:rPr'))
        for r in p._p.findall(qn('w:r')):
            for o in r.findall(qn('w:rPr')): r.remove(o)
            if rr is not None: r.insert(0, copy.deepcopy(rr))
        print('body text restored:', p.text[:50])

# 2. Table 10
t = d.tables[12]; tbl = t._tbl
assert t.rows[0].cells[6].text.startswith('SHAI-14 median')
grid = tbl.find(qn('w:tblGrid')); cols = grid.findall(qn('w:gridCol'))
for g in cols[6:]: grid.remove(g)
for tr in tbl.findall(qn('w:tr')):
    for tc in tr.findall(qn('w:tc'))[6:]: tr.remove(tc)
W = [2250, 1400, 1400, 650, 1950, 1050]
s = d.sections[0]; TW = int((s.page_width - s.left_margin - s.right_margin) / 635); W = [int(w * TW / sum(W)) for w in W]
for g, w in zip(grid.findall(qn('w:gridCol')), W): g.set(qn('w:w'), str(w))
tw = tbl.tblPr.find(qn('w:tblW')); tw.set(qn('w:w'), str(sum(W))); tw.set(qn('w:type'), 'dxa')
for row in t.rows:
    for tc, w in zip(row._tr.findall(qn('w:tc')), W):
        cw = tc.get_or_add_tcPr().find(qn('w:tcW')); cw.set(qn('w:w'), str(w)); cw.set(qn('w:type'), 'dxa')

def set_text(cell, lines):
    p0 = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]: extra._p.getparent().remove(extra._p)
    run0 = copy.deepcopy(p0.runs[0]._r)
    for r in p0._p.findall(qn('w:r')): p0._p.remove(r)
    for k, line in enumerate(lines):
        par = p0._p if k == 0 else copy.deepcopy(p0._p)
        if k: cell._tc.append(par)
        for r in par.findall(qn('w:r')): par.remove(r)
        r = copy.deepcopy(run0)
        for x in r.findall(qn('w:t')) + r.findall(qn('w:br')) + r.findall(qn('w:tab')): r.remove(x)
        tx = r.makeelement(qn('w:t'), {}); tx.text = line; tx.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); r.append(tx)
        par.append(r)
hdr = t.rows[0].cells
set_text(hdr[1], ['Medical students (n = 132)']); set_text(hdr[2], ['Others (n = 168)'])
set_text(hdr[3], ['p']); set_text(hdr[5], ['Adjusted p'])
set_text(t.rows[1].cells[0], ['SHAI-14 score', 'mean ± SD', 'median (IQR)'])
set_text(t.rows[1].cells[1], ['', '13.3 ± 5.8', '12.5 (10–17)']); set_text(t.rows[1].cells[2], ['', '11.6 ± 5.7', '11 (7–15)'])
set_text(t.rows[3].cells[0], ['CSS-12 score', 'mean ± SD', 'median (IQR)'])
set_text(t.rows[3].cells[1], ['', '28.9 ± 8.1', '29 (23–34)']); set_text(t.rows[3].cells[2], ['', '28.9 ± 8.6', '29 (23–34)'])
# indent the "mean ± SD" / "median (IQR)" sub-labels slightly
for ri in (1, 3):
    for p in t.rows[ri].cells[0].paragraphs[1:]: p.paragraph_format.left_indent = 114300

# note under the table, in the style of the other table notes
note_ref = next(p for p in P if p.text.startswith('Note. p: Mann–Whitney U test'))
note = copy.deepcopy(note_ref._p)
rs = note.findall(qn('w:r'))
for r in rs[2:]: note.remove(r)
rs[1].find(qn('w:t')).text = ('p: Mann–Whitney U test for scores and χ² test for proportions. Adjusted: linear regression (B) or logistic regression (AOR) '
                              'adjusted for age group, gender, chronic condition and language.')
tbl.addnext(note)
d.save(sys.argv[2]); print('Table 10 rebuilt')
