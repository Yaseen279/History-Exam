"""From v4: fix the strengths/limitation sentences (no highlight), give the added columns of Tables 3, 6 and 10 the same
look as the rest of each table, and keep each short table on one page without forcing page breaks.
Usage: python3 33_layout_final.py <v4.docx> <out.docx>"""
import sys, copy
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
d = Document(sys.argv[1])

def rewrite_runs(runs, text):
    runs[0].text = text
    for r in runs[1:]: r._r.getparent().remove(r._r)
for p in d.paragraphs:
    if p.text.startswith('Strengths include'):
        rewrite_runs(p.runs, 'Strengths include two established, reliable scales, a bilingual questionnaire, separate assessment of AI chatbots, complete data and adjustment for confounders in multivariable models.')
    elif p.text.strip() == 'The main limitations are:': rewrite_runs(p.runs, 'The main limitations are:')
    elif p.text.startswith('Sample: an online convenience sample') and 'sinc' in p.text:
        rest = p.runs[1:] if p.runs[0].text.strip() == 'Sample:' else p.runs
        rewrite_runs(rest, (' ' if rest is not p.runs else 'Sample: ') + 'an online convenience sample, young and with many medical students (44.0%), so percentages cannot be generalised to the whole population of Baghdad; in addition, only 34 participants did not use AI chatbots.')
    for r in p.runs:
        if p.text.startswith(('Strengths include', 'Sample: an online', 'The main limitations')):
            for h in r._r.findall('.//' + qn('w:highlight')): h.getparent().remove(h)

# added columns copy the formatting of the last original column, row by row
for ti, new in ((5, [5]), (8, [6, 7]), (12, [6, 7])):
    t = d.tables[ti]
    for tr in t._tbl.findall(qn('w:tr')):
        tcs = tr.findall(qn('w:tc')); ref = tcs[new[0] - 1]
        ref_pr = ref.find(qn('w:tcPr')); ref_p = ref.find(qn('w:p')); ref_ppr = ref_p.find(qn('w:pPr'))
        # text formatting from the nearest column on the left that has text in this row
        txt_cells = [c for c in tcs[:new[0]] if ''.join(x.text or '' for x in c.iter(qn('w:t'))).strip()]
        ref_r = next((r for r in txt_cells[-1].iter(qn('w:r')) if ''.join(x.text or '' for x in r.iter(qn('w:t'))).strip()), None) if txt_cells else None
        ref_rpr = ref_r.find(qn('w:rPr')) if ref_r is not None else None
        for i in new:
            tc = tcs[i]; pr = tc.find(qn('w:tcPr'))
            for tag in ('w:tcBorders', 'w:shd', 'w:vAlign'):
                for old in pr.findall(qn(tag)): pr.remove(old)
                src = ref_pr.find(qn(tag))
                if src is not None: pr.append(copy.deepcopy(src))
            for p in tc.findall(qn('w:p')):
                old = p.find(qn('w:pPr'))
                if old is not None: p.remove(old)
                if ref_ppr is not None: p.insert(0, copy.deepcopy(ref_ppr))
                for r in p.findall(qn('w:r')):
                    for o in r.findall(qn('w:rPr')): r.remove(o)
                    if ref_rpr is not None: r.insert(0, copy.deepcopy(ref_rpr))
                    else:
                        r.insert(0, r.makeelement(qn('w:rPr'), {}))
                    rp = r.find(qn('w:rPr'))
                    for h in rp.findall(qn('w:highlight')) + rp.findall(qn('w:shd')): rp.remove(h)
        # the header row of the new columns must read like the other headers
    print('styled added columns of docx table', ti + 1)

# no forced page breaks; short tables are kept on one page, long ones (Tables 1, 2, 6) may continue
LONG = {'Table 1.', 'Table 2.', 'Table 6.'}
for t in d.tables[3:]:
    cap = t._tbl.getprevious()
    while cap is not None and cap.tag == qn('w:p') and not ''.join(x.text or '' for x in cap.iter(qn('w:t'))).strip(): cap = cap.getprevious()
    txt = ''.join(x.text or '' for x in cap.iter(qn('w:t'))) if cap is not None else ''
    if not txt.startswith('Table '): continue
    cp = Paragraph(cap, None).paragraph_format; cp.page_break_before = False; cp.keep_with_next = True
    rows = t._tbl.findall(qn('w:tr')); long_t = any(txt.startswith(L) for L in LONG)
    for k, tr in enumerate(rows):
        for p in tr.iter(qn('w:p')):
            Paragraph(p, None).paragraph_format.keep_with_next = (k == 0) or (not long_t and k < len(rows) - 1)
d.save(sys.argv[2]); print('saved')
