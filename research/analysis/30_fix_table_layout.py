"""Tables 3, 6 and 10: fit the page width, same line spacing in every cell, text vertically centred.
Usage: python3 30_fix_table_layout.py <in.docx> <out.docx>"""
import sys
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
d = Document(sys.argv[1])
s = d.sections[0]; TEXT_W = int((s.page_width - s.left_margin - s.right_margin) / 635)   # twips
WIDTHS = {5: [2150, 1300, 1300, 900, 1050, 1438],                         # Table 3
          8: [1750, 560, 1000, 720, 1000, 720, 1519, 1519],                 # Table 6
          12: [1350, 920, 920, 720, 1250, 720, 1454, 1454]}                 # Table 10
for ti, cols in WIDTHS.items():
    t = d.tables[ti]; grid = t._tbl.find(qn('w:tblGrid')).findall(qn('w:gridCol'))
    assert len(grid) == len(cols), (ti, len(grid))
    k = TEXT_W / sum(cols); cols = [int(c * k) for c in cols]
    for g, w in zip(grid, cols): g.set(qn('w:w'), str(w))
    tw = t._tbl.tblPr.find(qn('w:tblW'))
    if tw is None: tw = t._tbl.tblPr.makeelement(qn('w:tblW'), {}); t._tbl.tblPr.append(tw)
    tw.set(qn('w:w'), str(sum(cols))); tw.set(qn('w:type'), 'dxa')
    for row in t.rows:
        for tc, w in zip(row._tr.findall(qn('w:tc')), cols):
            pr = tc.get_or_add_tcPr()
            cw = pr.find(qn('w:tcW'))
            if cw is None: cw = pr.makeelement(qn('w:tcW'), {}); pr.insert(0, cw)
            cw.set(qn('w:w'), str(w)); cw.set(qn('w:type'), 'dxa')
            va = pr.find(qn('w:vAlign'))
            if va is None: va = pr.makeelement(qn('w:vAlign'), {}); pr.append(va)
            va.set(qn('w:val'), 'center')
            for p in tc.iter(qn('w:p')):
                from docx.text.paragraph import Paragraph
                pf = Paragraph(p, None).paragraph_format
                pf.line_spacing = 1.0; pf.space_before = Pt(0); pf.space_after = Pt(0)
d.save(sys.argv[2]); print('fitted tables to', TEXT_W, 'twips')
