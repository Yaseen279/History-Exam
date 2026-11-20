"""Fix the 'sinc' limitation and the strengths sentence (no highlight), and start every table on its own page.
Usage: python3 32_final_touches.py <in.docx> <out.docx>"""
import sys, re
from docx import Document
from docx.oxml.ns import qn
d = Document(sys.argv[1]); P = d.paragraphs

def rewrite(p, text):
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]: r._r.getparent().remove(r._r)

for p in P:
    t = p.text
    if t.startswith('Strengths include'):
        rewrite(p, 'Strengths include two established, reliable scales, a bilingual questionnaire, separate assessment of AI chatbots, complete data and adjustment for confounders in multivariable models.')
    elif t.strip() == 'The main limitations are:' and t != 'The main limitations are:':
        rewrite(p, 'The main limitations are:')
    elif t.startswith('Sample: an online convenience sample') and 'sinc' in t:
        # keep the bold "Sample:" label if the first run is the label
        lab = p.runs[0].text if p.runs[0].text.strip().startswith('Sample') and len(p.runs) > 1 else None
        body = 'an online convenience sample, young and with many medical students (44.0%), so percentages cannot be generalised to the whole population of Baghdad; in addition, only 34 participants did not use AI chatbots.'
        if lab is not None:
            first, rest = p.runs[0], p.runs[1:]
            rest[0].text = ' ' + body if not lab.endswith(' ') else body
            for r in rest[1:]: r._r.getparent().remove(r._r)
        else:
            rewrite(p, 'Sample: ' + body)

# every table starts on a new page; tables short enough stay whole, Table 6 may continue onto the next page
for t in d.tables[3:]:
    cap = t._tbl.getprevious()
    while cap is not None and cap.tag == qn('w:p') and not ''.join(x.text or '' for x in cap.iter(qn('w:t'))).strip(): cap = cap.getprevious()
    txt = ''.join(x.text or '' for x in cap.iter(qn('w:t')))
    if not re.match(r'Table \d+\.', txt): continue
    from docx.text.paragraph import Paragraph
    Paragraph(cap, None).paragraph_format.page_break_before = True
    Paragraph(cap, None).paragraph_format.keep_with_next = True
    long_table = txt.startswith('Table 6.')
    rows = t._tbl.findall(qn('w:tr'))
    for k, tr in enumerate(rows):
        for p in tr.iter(qn('w:p')):
            pf = Paragraph(p, None).paragraph_format
            pf.keep_with_next = (k == 0) or (not long_table and k < len(rows) - 1)
    print('own page:', txt[:40])
for p in d.paragraphs:
    if 'sinc ' in p.text: print('STILL:', p.text)
d.save(sys.argv[2])
