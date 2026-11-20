"""Remove the blank page before Table 6 (and any other long table): every paragraph inside the tables had 'keep with next',
which forces Word to move a whole table to a new page. Keep it only on the header row so headers stay with the first data row.
Then write a clean copy without highlights. Usage: python3 31_fix_blank_page.py <in_marked.docx> <out_marked.docx> <out_clean.docx>"""
import sys
from docx import Document
from docx.oxml.ns import qn
d = Document(sys.argv[1]); n = 0
for t in d.tables:
    for k, tr in enumerate(t._tbl.findall(qn('w:tr'))):
        if k == 0: continue
        for kn in list(tr.iter(qn('w:keepNext'))): kn.getparent().remove(kn); n += 1
d.save(sys.argv[2])
for rpr in list(d.element.body.iter(qn('w:rPr'))):
    for tag in ('w:highlight', 'w:shd'):
        for el in rpr.findall(qn(tag)): rpr.remove(el)
d.save(sys.argv[3]); print('removed keep-with-next from', n, 'table paragraphs')
