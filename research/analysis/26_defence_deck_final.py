"""Final defence presentation: the Slidesgo template the students chose, with the strongest slides of the earlier
UOBCOM deck rebuilt inside it (logos, search bubbles, cycle, maps), stronger colours, and a three-presenter split.
Input: the template with duplicated slides (4 x4, 6 x2, 8 x2, 9 x2) made with the pptx skill's add_slide.py.
Usage: python3 26_defence_deck_final.py <template_with_duplicates.pptx> <figures dir> <out.pptx>"""
import sys, copy, re, json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.ns import qn
from lxml import etree

SRC, FIG, OUT = sys.argv[1:4]
prs = Presentation(SRC)
C = lambda h: RGBColor.from_string(h)
NAVY, SLATE, STEEL, LIGHT, PALE, INK, WHITE = C('0E2A47'), C('445F73'), C('5E7A90'), C('C2D6E7'), C('F3F3F5'), C('1D2230'), C('FFFFFF')
ORANGE, AMBER, TEAL, WINE = C('C98A2B'), C('A85A12'), C('1E5B4F'), C('7F1D3A')
BODY, HEAD = 'DM Sans', 'Raleway'
slides = {int(re.search(r'(\d+)\.xml$', s.part.partname).group(1)): s for s in prs.slides}
LAYOUT = {l.name: l for l in prs.slide_layouts}
ICON_ID = json.load(open(f'{FIG}/icon_index.json'))
PRESENTER_1, PRESENTER_2, PRESENTER_3 = '[Presenter name]', 'Yaseen Omar Lutfi', '[Presenter name]'

# ================================================================== helpers
def shp(slide, sid):
    for s in slide.shapes:
        if s.shape_id == sid: return s
    raise KeyError(sid)

def runs_of(text):
    return [(p, i % 2 == 1) for i, p in enumerate(text.split('**')) if p]

def _colour(rp, color):
    for f in rp.findall(qn('a:solidFill')): rp.remove(f)
    sf = etree.Element(qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', str(color)); rp.insert(0, sf)

def set_text(shape, items, size=None, align=None, color=None, font=None, bold_color=None):
    """Replace text keeping the template's paragraph/run formatting. '* ' prefix = bullet; **x** = bold."""
    body = shape.text_frame._txBody
    paras = body.findall(qn('a:p'))
    plain = next((p for p in paras if p.find('.//' + qn('a:buChar')) is None), paras[0])
    bullet = next((p for p in paras if p.find('.//' + qn('a:buChar')) is not None), None)
    for p in paras: body.remove(p)
    for it in ([items] if isinstance(items, str) else items):
        is_b = it.startswith('* ') and bullet is not None
        tp = copy.deepcopy(bullet if is_b else plain)
        r0 = tp.find(qn('a:r'))
        rpr = copy.deepcopy(r0.find(qn('a:rPr'))) if r0 is not None and r0.find(qn('a:rPr')) is not None else etree.Element(qn('a:rPr'))
        for el in list(tp):
            if el.tag in (qn('a:r'), qn('a:br'), qn('a:fld')): tp.remove(el)
        end = tp.find(qn('a:endParaRPr'))
        for txt, bold in runs_of(it[2:] if is_b else it):
            r = etree.Element(qn('a:r')); rp = copy.deepcopy(rpr); r.append(rp)
            if bold: rp.set('b', '1')
            if size: rp.set('sz', str(int(size * 100)))
            col = bold_color if (bold and bold_color is not None) else color
            if col is not None: _colour(rp, col)
            if font:
                for t in ('a:latin', 'a:ea', 'a:cs', 'a:sym'):
                    old = rp.find(qn(t))
                    if old is not None: rp.remove(old)
                etree.SubElement(rp, qn('a:latin')).set('typeface', font)
            etree.SubElement(r, qn('a:t')).text = txt
            (tp.insert(list(tp).index(end), r) if end is not None else tp.append(r))
        if align is not None: tp.find(qn('a:pPr')).set('algn', {'l': 'l', 'c': 'ctr', 'r': 'r'}[align])
        body.append(tp)

def move(shape, x=None, y=None, w=None, h=None):
    for attr, v in (('left', x), ('top', y), ('width', w), ('height', h)):
        if v is not None: setattr(shape, attr, Inches(v))

def delete(shape): shape._element.getparent().remove(shape._element)

def swap_picture(slide, shape, path):
    _, rid = slide.part.get_or_add_image_part(path)
    shape._element.find('.//' + qn('a:blip')).set(qn('r:embed'), rid)
    src = shape._element.find('.//' + qn('a:srcRect'))
    if src is not None: src.getparent().remove(src)

def textbox(slide, x, y, w, h, items, size=11, color=INK, bold=False, align='l', font=BODY, fill=None, anchor='t', margin=0.05,
            italic=False, bold_color=NAVY, line=None, space=4, rtl=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, side, Inches(margin))
    if fill is not None: tb.fill.solid(); tb.fill.fore_color.rgb = fill
    if line is not None: tb.line.color.rgb = line; tb.line.width = Pt(1)
    for i, it in enumerate([items] if isinstance(items, str) else items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        if rtl: p._p.get_or_add_pPr().set('rtl', '1')
        if it.startswith('* '):
            it = it[2:]; ppr = p._p.get_or_add_pPr(); ppr.set('marL', str(Inches(0.17))); ppr.set('indent', str(-Inches(0.17)))
            etree.SubElement(ppr, qn('a:buFont')).set('typeface', 'Arial'); etree.SubElement(ppr, qn('a:buChar')).set('char', '•')
        p.space_after = Pt(space)
        for txt, b in runs_of(it):
            r = p.add_run(); r.text = txt; f = r.font; f.size = Pt(size); f.name = font; f.bold = bold or b; f.italic = italic
            f.color.rgb = bold_color if (b and not bold and fill is None and bold_color is not None) else color
    return tb

def rect(slide, x, y, w, h, fill=WHITE, line=None, shape=MSO_SHAPE.RECTANGLE, lw=1.0):
    r = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None: r.line.fill.background()
    else: r.line.color.rgb = line; r.line.width = Pt(lw)
    r.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: r.adjustments[0] = 0.25
    return r

def bar_header(slide, x, y, w, text, fill, h=0.32, size=11):
    return textbox(slide, x, y, w, h, text, size=size, color=WHITE, bold=True, fill=fill, anchor='m', margin=0.08)

def panel(slide, x, y, w, h, title, fill, items, size=10.5):
    bar_header(slide, x, y, w, title, fill)
    rect(slide, x, y + 0.32, w, h - 0.32, WHITE, LIGHT)
    textbox(slide, x + 0.06, y + 0.38, w - 0.12, h - 0.42, items, size=size)

def card(slide, x, y, w, h, title, fill, icon, items, size=11):
    textbox(slide, x, y, w, 0.46, title, size=11.5, color=WHITE, bold=True, fill=fill, anchor='m', margin=0.08).text_frame.margin_left = Inches(0.52)
    rect(slide, x + 0.09, y + 0.06, 0.34, 0.34, WHITE, None, MSO_SHAPE.OVAL); place_icon(slide, icon, x + 0.26, y + 0.23, 0.23)
    rect(slide, x, y + 0.46, w, h - 0.46, WHITE, LIGHT)
    textbox(slide, x + 0.07, y + 0.52, w - 0.14, h - 0.56, items, size=size, space=3)

def picture(slide, path, x, y, w=None, h=None, frame=False):
    kw = {}
    if w: kw['width'] = Inches(w)
    if h: kw['height'] = Inches(h)
    if frame:
        pic = slide.shapes.add_picture(path, Inches(x), Inches(y), **kw); pw, ph = pic.width, pic.height; delete(pic)
        rect(slide, x - 0.05, y - 0.05, pw / 914400 + 0.1, ph / 914400 + 0.1, WHITE, LIGHT)
    return slide.shapes.add_picture(path, Inches(x), Inches(y), **kw)

def bubble(slide, x, y, w, text, dark=False, h=0.42):
    b = rect(slide, x, y, w, h, NAVY if dark else WHITE, None if dark else STEEL, MSO_SHAPE.ROUNDED_RECTANGLE)
    b.adjustments[0] = 0.5
    if dark: textbox(slide, x + 0.1, y, w - 0.2, h, text, size=10.5, color=WHITE, bold=True, anchor='m')
    else:
        place_icon(slide, '34:16', x + 0.24, y + h / 2, 0.22)
        textbox(slide, x + 0.42, y, w - 0.5, h, text, size=10.5, color=INK, anchor='m')

def keybox(slide, text, x, y, w, h=0.42, fill=NAVY, size=11):
    return textbox(slide, x, y, w, h, text, size=size, color=WHITE, bold=True, align='c', fill=fill, anchor='m', margin=0.06)

def place_icon(slide, key, cx, cy, size=0.36, colour=None):
    n, _ = key.split(':'); el = copy.deepcopy(shp(slides[int(n)], ICON_ID[key])._element)
    for clr in el.iter(qn('a:schemeClr')):
        if clr.get('val') in ('dk2', 'dk1', 'accent1', 'accent2'): clr.set('val', 'lt1')
    for clr in el.iter(qn('a:srgbClr')):
        if clr.get('val') == '0E2A47': clr.set('val', 'FFFFFF')
    xf = el.find('.//' + qn('a:xfrm')); ext = xf.find(qn('a:ext')); off = xf.find(qn('a:off'))
    w, h = int(ext.get('cx')), int(ext.get('cy')); k = Inches(size) / max(w, h); nw, nh = int(w * k), int(h * k)
    ext.set('cx', str(nw)); ext.set('cy', str(nh)); off.set('x', str(int(Inches(cx) - nw / 2))); off.set('y', str(int(Inches(cy) - nh / 2)))
    nid = max(int(e.get('id')) for e in slide.shapes._spTree.iter(qn('p:cNvPr'))) + 1
    for e in el.iter(qn('p:cNvPr')): e.set('id', str(nid)); nid += 1
    slide.shapes._spTree.append(el)

def centre(slide, sid):
    c = shp(slide, sid); return (c.left + c.width / 2) / 914400, (c.top + c.height / 2) / 914400

def reicon(slide, old, pairs):
    for g in old: delete(shp(slide, g))
    for circle, key in pairs: place_icon(slide, key, *centre(slide, circle))

def line(slide, x1, y1, x2, y2, color=SLATE, w=1.5, arrow=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(w)
    if arrow:
        ln = c.line._get_or_add_ln(); te = etree.SubElement(ln, qn('a:tailEnd')); te.set('type', 'triangle'); te.set('w', 'med'); te.set('len', 'med')
    return c

def table(slide, header, rows, x, y, w, colw, size=10, hi=(), row_h=0.3):
    gf = slide.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(w), Inches(row_h * (len(rows) + 1)))
    tbl = gf.table; tp = tbl._tbl.tblPr
    for a in ('firstRow', 'bandRow'): tp.set(a, '0')
    sid = tp.find(qn('a:tableStyleId'))
    if sid is not None: sid.text = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
    for j, cw in enumerate(colw): tbl.columns[j].width = Inches(cw)
    for i in range(len(rows) + 1): tbl.rows[i].height = Inches(row_h)
    for i, r in enumerate([header] + rows):
        for j, val in enumerate(r):
            c = tbl.cell(i, j); c.margin_left = c.margin_right = Inches(0.07); c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE; c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else (C('E4ECF3') if (i - 1) in hi else WHITE)
            p = c.text_frame.paragraphs[0]; c.text_frame.word_wrap = True
            for txt, b in runs_of(str(val)):
                run = p.add_run(); run.text = txt; f = run.font; f.size = Pt(size); f.name = BODY
                f.bold = i == 0 or b or j == 0 or (i - 1) in hi; f.color.rgb = WHITE if i == 0 else (NAVY if (j == 0 or b or (i - 1) in hi) else INK)
            tcPr = c._tc.get_or_add_tcPr()
            for k, tag in enumerate(('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB')):
                ln = etree.Element(qn(tag)); ln.set('w', '9525'); sf = etree.SubElement(ln, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', 'A9BCCB'); tcPr.insert(k, ln)
    return gf

def new_slide(title, layout='CUSTOM_8'):
    s = prs.slides.add_slide(LAYOUT[layout])
    if title is None: delete(s.shapes.title)
    else: s.shapes.title.text = title
    return s

def divider(n, num, title, photo, presenter, search=None):
    s = slides[n]; set_text(shp(s, 464), title, color=NAVY); set_text(shp(s, 465), num, font=BODY, color=NAVY)
    swap_picture(s, shp(s, 466), f'{FIG}/{photo}')
    textbox(s, 4.25, 3.95, 4.5, 0.4, f'Presented by **{presenter}**', size=12.5, color=SLATE)
    if search: bubble(s, 0.45, 4.1, 3.35, search)
    return s

order = []

# ================================================================== PART 1 · INTRODUCTION AND METHODS
# 1 title
s = slides[1]
t = shp(s, 432); move(t, x=0.6, y=1.3, w=4.95, h=1.6)
set_text(t, 'HEALTH ANXIETY, AI CHATBOT USE AND CYBERCHONDRIA AMONG ADULTS IN BAGHDAD', size=22, align='l', color=NAVY)
t.text_frame._txBody.find(qn('a:bodyPr')).set('anchor', 't')
sub = shp(s, 433); move(sub, x=0.6, y=2.95, w=4.95, h=2.0)
set_text(sub, ['An online cross-sectional survey', 'Prepared by', '**Abdulrahman Jamal Ghazi  ·  Mustafa Wamedh Mustafa  ·  Yaseen Omar Lutfi**',
               'Supervised by', '**Assist. Prof. Dr. Thikra Hasan Mathkor**'], size=12, align='l', color=INK, bold_color=NAVY)
for i, p in enumerate(sub.text_frame._txBody.findall(qn('a:p'))):
    ppr = p.find(qn('a:pPr')); sb = ppr.find(qn('a:spcBef'))
    if sb is not None: sb.find(qn('a:spcPts')).set('val', '700' if i in (1, 3) else '100')
    if i == 0:
        for r in p.findall(qn('a:r')): _colour(r.find(qn('a:rPr')), AMBER); r.find(qn('a:rPr')).set('i', '1'); r.find(qn('a:rPr')).set('sz', '1400')
    if i in (1, 3):
        for r in p.findall(qn('a:r')): _colour(r.find(qn('a:rPr')), SLATE); r.find(qn('a:rPr')).set('sz', '1050')
picture(s, f'{FIG}/logo_uob.png', 0.6, 0.38, h=0.72); picture(s, f'{FIG}/logo_med.png', 1.42, 0.38, h=0.72)
textbox(s, 2.25, 0.42, 4.6, 0.7, ['Ministry of Higher Education and Scientific Research', 'University of Baghdad  ·  College of Medicine'], size=11, color=NAVY, bold=True, space=2)
picture(s, f'{FIG}/p_title.jpg', 5.75, 1.55, w=3.45, frame=True)
bubble(s, 5.5, 1.22, 3.55, 'headache for 3 days causes brain tumour')
bubble(s, 6.75, 3.25, 2.5, 'Could my headache be serious?', dark=True)
order.append(s)

# 2 outline with the presenter split
s = new_slide('OUTLINE')
for x, fill, part, head, who, items in (
        (0.79, NAVY, 'PART 1', 'INTRODUCTION AND METHODS', PRESENTER_1, ['The question behind the study', 'Health anxiety and cyberchondria', 'The vicious cycle', 'From Dr Google to Dr ChatGPT', 'Aim and hypotheses', 'Design, questionnaire, statistics']),
        (3.67, SLATE, 'PART 2', 'RESULTS', PRESENTER_2, ['Participants and where they search', 'Behaviour after searching', 'Levels of health anxiety', 'Main finding (H1)', 'Predictors of both conditions', 'Medical students (H2)']),
        (6.55, ORANGE, 'PART 3', 'DISCUSSION AND CONCLUSIONS', PRESENTER_3, ['Our finding in Baghdad', 'Worldwide and regional comparison', 'AI chatbots and the consultation', 'Strengths and limitations', 'Conclusions and recommendations'])):
    textbox(s, x, 1.25, 2.67, 0.72, [part, f'**{head}**'], size=10, color=WHITE, fill=fill, anchor='m', margin=0.1, bold_color=WHITE, space=1)
    rect(s, x, 1.97, 2.67, 2.85, WHITE, LIGHT)
    textbox(s, x + 0.08, 2.03, 2.5, 0.32, f'Presented by **{who}**', size=10, color=SLATE, italic=True)
    textbox(s, x + 0.08, 2.4, 2.52, 2.4, ['* ' + i for i in items], size=10.5, space=5)
order.append(s)

# 3 opening: the question behind the study
s = new_slide(None)
rect(s, 0.79, 1.05, 4.35, 1.35, WHITE, LIGHT)
textbox(s, 0.9, 1.1, 4.15, 0.8, 'مَا أَنْزَلَ اللَّهُ دَاءً إِلَّا أَنْزَلَ لَهُ شِفَاءً', size=20, color=NAVY, bold=True, align='c', font='Arial', anchor='m', rtl=True)
textbox(s, 0.9, 1.9, 4.15, 0.4, 'صحيح البخاري', size=11, color=AMBER, align='c', font='Arial', rtl=True)
rect(s, 0.79, 2.6, 4.35, 1.55, WHITE, LIGHT)
textbox(s, 0.95, 2.7, 4.05, 1.0, '“He who fears he shall suffer, already suffers what he fears.”', size=15, color=NAVY, italic=True, bold=True)
textbox(s, 0.95, 3.7, 4.05, 0.35, 'Michel de Montaigne', size=11, color=AMBER)
textbox(s, 0.79, 4.35, 4.35, 0.5, 'Searching can help, or it can feed fear.', size=12, color=SLATE, italic=True)
picture(s, f'{FIG}/p_hook.jpg', 5.5, 1.2, w=3.7, frame=True)
bubble(s, 5.3, 0.95, 3.4, 'is my chest pain a heart attack?')
bubble(s, 6.95, 4.1, 2.2, '…but what if it is?', dark=True)
order.append(s)

# 4 divider 1
order.append(divider(4, '1', 'INTRODUCTION', 'p_intro.jpg', PRESENTER_1, 'rash on arm meaning skin cancer'))

# 5 health anxiety
s = new_slide('HEALTH ANXIETY', 'CUSTOM_8_1')
panel(s, 0.79, 1.2, 2.62, 2.15, 'DEFINITION AND MODEL', NAVY, ['* Persistent worry about **having or getting a serious illness**', '* A **spectrum**: everyday worry → illness anxiety disorder',
      '* Misread sensations → **checking and reassurance** → short relief → worry returns'], size=10)
panel(s, 3.53, 1.2, 2.62, 2.15, 'BURDEN', ORANGE, ['* About **6%** of the population, up to **20%** of outpatients', '* Costly: **unnecessary medical visits**',
      '* Iraq, COVID-19 survey (n = 1591): **49.5%** screened positive'], size=10)
panel(s, 0.79, 3.48, 5.36, 1.3, 'HOW WE MEASURED IT', SLATE, ['* **SHAI-14**: 14 items, each 0–3, total **0–42**; validated in clinical and general samples',
      '* **18 or more** = elevated health anxiety: a screening threshold, **not a diagnosis**'], size=10.5)
picture(s, f'{FIG}/p_ha.jpg', 6.42, 1.25, w=2.75, frame=True)
order.append(s)

# 6 cyberchondria
s = new_slide('CYBERCHONDRIA', 'CUSTOM_8_1')
rect(s, 0.79, 1.18, 5.95, 1.08, WHITE, LIGHT)
textbox(s, 0.87, 1.22, 5.8, 1.0, ['**Definition:** excessive or repeated online health searching that **increases, rather than relieves, distress** (Starcevic and Berle, 2013)',
        'Searches for harmless symptoms often **escalate to rare, serious diagnoses** (White and Horvitz, 2009)'], size=10.5)
picture(s, f'{FIG}/p_cyber.jpg', 6.95, 1.2, w=2.25, frame=True)
textbox(s, 0.79, 2.38, 8.43, 0.32, 'CSS-12 (CYBERCHONDRIA SEVERITY SCALE): FOUR DIMENSIONS, 3 ITEMS EACH, TOTAL 12–60', size=11, color=NAVY, bold=True)
for i, (head, fill, icon, txt) in enumerate((('EXCESSIVENESS', NAVY, '34:16', 'Searching the same symptom again and again'), ('COMPULSION', ORANGE, '34:24', 'Searching interrupts work and social life'),
                                            ('DISTRESS', WINE, '34:67', 'Feeling worse, even panicking, after reading'), ('REASSURANCE', TEAL, '35:70', 'Searching leads to consulting a doctor'))):
    card(s, 0.79 + i * 2.14, 2.75, 2.01, 1.45, head, fill, icon, txt, size=11)
textbox(s, 0.79, 4.3, 8.43, 0.45, 'Searching itself is normal: it becomes cyberchondria when it is **excessive, compulsive and distressing**.', size=11.5, color=SLATE, italic=True)
order.append(s)

# 7 the vicious cycle
s = new_slide('THE VICIOUS CYCLE', 'CUSTOM_8_1')
rect(s, 0.79, 1.2, 3.65, 3.5, WHITE, LIGHT)
textbox(s, 0.88, 1.28, 3.5, 3.4, ['* Two meta-analyses: health anxiety and cyberchondria correlate at **r = 0.62–0.63**', '* Health-anxious people feel **worse** after searching; others feel **relieved**',
        '* Dutch 4-wave panel (n = 5322): the relationship runs **both ways**', '* Reassurance gives **short relief**, so the cycle repeats'], size=11.5, space=8)
boxes = {'top': (6.05, 1.2, 'Health anxiety', NAVY), 'right': (7.55, 2.35, 'Excessive searching', SLATE), 'bottom': (6.05, 3.5, 'Post-search distress', ORANGE), 'left': (4.55, 2.35, 'Reassurance seeking', WINE)}
for x, y, txt, fill in boxes.values(): keybox(s, txt, x, y, 1.62, 0.62, fill=fill, size=11.5)
line(s, 7.67, 1.51, 8.36, 2.33, arrow=True); line(s, 8.36, 2.99, 7.69, 3.8, arrow=True); line(s, 6.03, 3.8, 5.36, 2.99, arrow=True); line(s, 5.36, 2.33, 6.03, 1.51, arrow=True)
textbox(s, 4.55, 4.3, 4.62, 0.35, 'Proposed cycle (cognitive-behavioural model)', size=10.5, color=SLATE, italic=True, align='c')
order.append(s)

# 8 from Dr Google to Dr ChatGPT
s = new_slide('FROM “DR GOOGLE” TO “DR CHATGPT”', 'CUSTOM_8_1')
panel(s, 0.79, 1.2, 4.35, 2.62, 'WHAT CHANGES WITH AI CHATBOTS?', NAVY, ['* **Fluent, personal, conversational** answers', '* Can be asked **again and again**: one more question',
      '* Answers rated **more empathetic** than physicians’ (Ayers, 2023)', '* About **1 in 5** Americans used ChatGPT for health (2024)'], size=11.5)
picture(s, f'{FIG}/p_robot.jpg', 5.45, 1.25, w=3.72, frame=True)
bubble(s, 5.3, 3.55, 3.35, 'I feel tired and my hands shake. Is it serious?')
textbox(s, 0.79, 4.1, 8.43, 0.68, '**The gap:** no cyberchondria data from Baghdad  ·  AI chatbots rarely studied separately from search engines  ·  mixed evidence on medical students',
        size=11.5, color=INK, fill=C('FBF1E3'), line=ORANGE, anchor='m', margin=0.1, bold_color=AMBER)
order.append(s)

# 9 aim and hypotheses
s = new_slide('AIM AND HYPOTHESES', 'CUSTOM_8_1')
card(s, 0.79, 1.15, 4.12, 1.55, 'AIM', NAVY, '34:27', 'To study how health anxiety relates to cyberchondria in adults in Baghdad, with a focus on **AI chatbots** and **medical students**', size=11.5)
card(s, 5.1, 1.15, 4.12, 1.55, 'OBJECTIVES', SLATE, '36:60', ['1. Describe online and AI health searching', '2. Measure both conditions and their link', '3. Compare medical students with others'], size=11)
card(s, 0.79, 2.88, 4.12, 1.9, 'H1: PRIMARY HYPOTHESIS', TEAL, '34:35', ['More health anxiety goes with more cyberchondria, **even after accounting for age, sex, background and digital habits**',
     'Tested by correlation and hierarchical regression'], size=11)
card(s, 5.1, 2.88, 4.12, 1.9, 'H2: SECONDARY HYPOTHESIS', WINE, '35:15', ['Medical students have **higher** health anxiety and cyberchondria (“medical student syndrome”)',
     'Tested before and after adjusting for age'], size=11)
order.append(s)

# 10 divider 2
order.append(divider(42, '2', 'METHODS', 'p_methods.jpg', PRESENTER_1))

# 11 study design
s = new_slide('STUDY DESIGN', 'CUSTOM_8_1')
for i, (head, fill, icon, txt) in enumerate((('DESIGN', NAVY, '36:59', 'Analytical cross-sectional online survey, reported by STROBE and CHERRIES'), ('SETTING', SLATE, '34:1', 'Baghdad · Google Form in Arabic and English'),
                                            ('SAMPLING', ORANGE, '36:98', 'Convenience and snowball, through social-media and messaging groups'), ('PARTICIPANTS', TEAL, '36:82', '**300 adults** aged 18 or older (194 needed) · no missing data'),
                                            ('TOOLS', NAVY, '35:98', '**SHAI-14** for health anxiety · **CSS-12** for cyberchondria · own questions'), ('ETHICS', WINE, '36:52', 'Electronic informed consent · anonymous and voluntary · no names collected'))):
    card(s, 0.79 + (i % 3) * 2.865, 1.15 + (i // 3) * 1.83, 2.7, 1.7, head, fill, icon, txt, size=11)
order.append(s)

# 12 questionnaire
s = new_slide('THE QUESTIONNAIRE', 'CUSTOM_8_1')
table(s, ['Part', 'Content', 'Scoring'], [
    ['1', 'Consent and socio-demographics', 'Age, gender, education, work, chronic condition'],
    ['2', 'Online health-information seeking', 'Tools, main AI chatbot, motives, trust (1–5)'],
    ['3', 'SHAI-14 (health anxiety)', '14 items, each 0–3; total 0–42'],
    ['4', 'CSS-12 (cyberchondria)', '12 items, each 1–5; total 12–60; four dimensions'],
    ['5', 'Behaviour after searching', 'Actions, telling the doctor, the relationship']], 0.79, 1.2, 6.05, [0.5, 2.55, 3.0], size=10.5, hi=(2, 3), row_h=0.4)
textbox(s, 0.79, 4.02, 6.05, 0.85, ['* **Elevated health anxiety:** SHAI-14 of 18 or more (screening, not diagnosis)', '* **High cyberchondria:** CSS-12 above 33 (the upper third)',
                                   '* **Reliability:** alpha 0.81 and 0.86, the same in Arabic and English'], size=10, space=2)
picture(s, f'{FIG}/p_methods.jpg', 7.05, 1.2, h=3.4, frame=True)
order.append(s)

# 13 choosing the statistical tests: decision tree
s = new_slide('CHOOSING THE STATISTICAL TESTS', 'CUSTOM_8_1')
keybox(s, 'WHAT ARE WE TESTING?', 3.6, 1.12, 2.8, 0.36, size=11)
cols = [0.72, 2.92, 5.12, 7.32]; W = 1.95
line(s, 5.0, 1.48, 5.0, 1.6, w=1.25); line(s, cols[0] + W / 2, 1.6, cols[3] + W / 2, 1.6, w=1.25)
L1 = ['A score between groups', 'Two categorical variables', 'Two scores', 'Many factors together']
L2 = ['Normal? Shapiro–Wilk: **No**', 'Expected counts ≥ 5?', 'Link between two scores', 'Type of outcome?']
L3 = [('2 groups', '**Mann–Whitney U**', '3+ groups', '**Kruskal–Wallis H**'), ('Yes', '**Chi-square**', 'No', '**Fisher’s exact**'), (None, '**Pearson r**, confirmed by **Spearman rho**', None, None),
      ('Score', '**Linear regression**', 'Yes / no', '**Logistic regression**')]
L4 = ['SHAI p < 0.001, CSS p = 0.008 · replace the t-test and ANOVA · medians (IQR)', 'Strength of the link: Cramér’s V', 'Adjusted for other factors: partial correlation', 'Hierarchical linear: B, beta, R² · logistic: AOR, AUC']
for x, a, b, c3, d in zip(cols, L1, L2, L3, L4):
    cx = x + W / 2
    line(s, cx, 1.6, cx, 1.72, w=1.25, arrow=True)
    keybox(s, a, x, 1.72, W, 0.42, fill=SLATE, size=10.5)
    line(s, cx, 2.14, cx, 2.3, w=1.25, arrow=True)
    textbox(s, x, 2.3, W, 0.62, b, size=10, color=NAVY, align='c', fill=WHITE, line=SLATE, anchor='m', margin=0.05, italic=True)
    line(s, cx, 2.92, cx, 3.08, w=1.25)
    if c3[0] is None:
        line(s, cx, 3.08, cx, 3.2, w=1.25, arrow=True)
        textbox(s, x, 3.2, W, 0.86, c3[1], size=10.5, color=WHITE, align='c', fill=NAVY, anchor='m', bold_color=WHITE)
    else:
        hw = (W - 0.08) / 2
        line(s, x + hw / 2, 3.08, x + W - hw / 2, 3.08, w=1.25)
        for k, (lab, test) in enumerate(((c3[0], c3[1]), (c3[2], c3[3]))):
            xx = x + k * (hw + 0.08); line(s, xx + hw / 2, 3.08, xx + hw / 2, 3.2, w=1.25, arrow=True)
            textbox(s, xx, 3.2, hw, 0.86, [lab, test], size=9.5, color=C('D6E3EE'), align='c', fill=NAVY, anchor='m', bold_color=WHITE, space=1)
    textbox(s, x, 4.15, W, 0.7, d, size=9.5, color=INK, align='c')
order.append(s)

# ================================================================== PART 2 · RESULTS
order.append(divider(43, '3', 'RESULTS', 'p_results.jpg', PRESENTER_2))

s = new_slide('PARTICIPANTS AND WHERE THEY SEARCH')
for (x, y, num, lab) in ((0.79, 1.25, '300', 'adults, complete data'), (2.47, 1.25, '62.3%', 'aged 20–29'), (0.79, 2.42, '56.3%', 'female'), (2.47, 2.42, '44.0%', 'medical students')):
    rect(s, x, y, 1.58, 1.05, WHITE, LIGHT)
    textbox(s, x, y + 0.08, 1.58, 0.55, num, size=24, color=NAVY, bold=True, align='c', anchor='m')
    textbox(s, x, y + 0.62, 1.58, 0.36, lab, size=10.5, color=INK, align='c')
textbox(s, 0.79, 3.6, 3.26, 0.95, ['* **63.3%** health-related background', '* **21.7%** chronic condition', '* **70.7%** answered in Arabic'], size=11, fill=WHITE, line=LIGHT, margin=0.1)
pic = picture(s, f'{FIG}/sample1_phone_tools.png', 4.4, 1.2, h=3.6)
order.append(s)

s = new_slide('WHAT PEOPLE DID AFTER SEARCHING'); pic = picture(s, f'{FIG}/sample4_path_after_search.png', 0, 1.25, h=3.55); pic.left = int((prs.slide_width - pic.width) / 2); order.append(s)

s = new_slide('LEVELS OF HEALTH ANXIETY')
pic = picture(s, f'{FIG}/sample3_one_in_five.png', 0, 1.25, w=7.2); pic.left = int((prs.slide_width - pic.width) / 2)
table(s, ['Scale', 'Mean ± SD', 'Median (IQR)', 'Cronbach’s alpha'], [['SHAI-14 (0–42)', '12.35 ± 5.83', '12 (8–16)', '0.81'], ['CSS-12 (12–60)', '28.86 ± 8.36', '29 (23–34)', '0.86']],
      1.4, 4.1, 7.2, [2.1, 1.7, 1.7, 1.7], size=10.5, row_h=0.27)
order.append(s)

s = new_slide('MAIN FINDING (H1)')
picture(s, f'{FIG}/scatter_shai_css.png', 0.79, 1.2, h=3.45)
picture(s, f'{FIG}/sample2_cycle_dimensions.png', 5.55, 1.2, w=3.65)
textbox(s, 5.55, 3.6, 3.65, 0.9, ['* Moderate link: **r = 0.47**; **0.48** after adjustment', '* Health anxiety accounts for about **22%**', '* An association, **not proof of cause**'], size=10.5)
keybox(s, 'H1 SUPPORTED', 5.55, 4.45, 3.65, 0.36, size=11.5, fill=TEAL)
order.append(s)

s = new_slide('WHAT PREDICTS CYBERCHONDRIA?')
picture(s, f'{FIG}/r2_blocks.png', 0.79, 1.25, h=3.45)
table(s, ['Predictor (final model)', 'B (95% CI)', 'Beta', 'p'], [
    ['Health anxiety (per point)', '0.68 (0.53–0.84)', '0.48', '< 0.001'], ['AI chatbot user', '5.33 (2.57–8.09)', '0.20', '< 0.001'],
    ['Age 30–39 (vs 20–29)', '6.27 (2.42–10.11)', '0.19', '0.001'], ['Age 40 or older', '3.98 (0.16–7.80)', '0.15', '0.041'],
    ['All other factors', 'not significant', '', '']], 4.95, 1.3, 4.27, [1.75, 1.32, 0.5, 0.7], size=9.5, hi=(0, 1), row_h=0.3)
textbox(s, 4.95, 3.25, 4.27, 1.0, ['* Health anxiety **added 18.4%** after all other factors', '* AI users scored **5.3 points higher**, independently of health anxiety',
                                   '* The model explained **32%** of the differences'], size=10.5)
keybox(s, 'HEALTH ANXIETY IS THE STRONGEST PREDICTOR (BETA = 0.48)', 4.95, 4.3, 4.27, 0.42, size=9.5)
order.append(s)

s = new_slide('WHO HAD ELEVATED HEALTH ANXIETY?')
picture(s, f'{FIG}/forest_HA.png', 0.79, 1.2, w=5.35)
textbox(s, 6.35, 1.3, 2.87, 2.5, ['**Adjusted odds ratios**', '* Cyberchondria: **3.12** per SD', '* Seeking instant reassurance: **3.83**', '* Each older age group: **0.61** (protective)',
                                  '**Model checks**', '* Hosmer–Lemeshow p = **0.50**: good fit', '* AUC = **0.83**: good discrimination'], size=10.5)
textbox(s, 6.35, 3.95, 2.87, 0.8, 'Only 57 cases for 11 factors, so the odds ratios may be overestimated', size=10, color=SLATE, italic=True)
order.append(s)

s = new_slide('MEDICAL STUDENTS VS OTHERS (H2)', 'CUSTOM_8_1')
table(s, ['Measure', 'Medical students (n = 132)', 'Others (n = 168)', 'p', 'Adjusted p'], [
    ['SHAI-14, median (IQR)', '12.5 (10–17)', '11 (7–15)', '0.004', '0.081'], ['Elevated health anxiety', '23.5%', '15.5%', '0.079', '0.238'],
    ['CSS-12, median (IQR)', '29 (23–34)', '29 (23–34)', '0.989', '0.627'], ['High cyberchondria', '28.0%', '29.2%', '0.829', '0.771']],
      0.79, 1.25, 8.43, [2.3, 2.05, 1.75, 1.0, 1.33], size=11, hi=(0,), row_h=0.36)
textbox(s, 0.79, 3.25, 5.1, 1.5, ['* Before adjustment, medical students had **higher health anxiety**', '* After adjusting for **age**, sex, chronic condition and language, the difference was **no longer significant**',
                                  '* Cyberchondria was **identical**'], size=11)
keybox(s, ['H2 NOT SUPPORTED', 'Age, not studying medicine, explained the difference'], 6.1, 3.35, 3.12, 1.1, size=11, fill=WINE)
order.append(s)

# ================================================================== PART 3 · DISCUSSION AND CONCLUSIONS
order.append(divider(47, '4', 'DISCUSSION', 'p_discussion.jpg', PRESENTER_3, 'So, is searching the problem, or the anxiety?'))

s = new_slide('OUR FINDING IN BAGHDAD')
rect(s, 0.79, 1.3, 5.0, 2.9, WHITE, LIGHT)
textbox(s, 0.92, 1.4, 4.75, 2.75, ['To our knowledge, the **first study** to apply the CSS-12 in **Baghdad**, and among the first to examine **AI chatbots separately** from search engines.',
        'Health anxiety and cyberchondria were **moderately associated (r = 0.47)**, independently of all other measured factors.', '**H1 supported  ·  H2 not supported**'], size=13, space=10)
picture(s, f'{FIG}/map_iraq.png', 6.25, 1.05, h=3.25)
textbox(s, 6.0, 4.3, 3.2, 0.5, 'n = 300  ·  r = 0.47', size=18, color=AMBER, bold=True, align='c', font=BODY)
order.append(s)

s = new_slide('COMPARISON WITH WORLDWIDE STUDIES')
mp = picture(s, f'{FIG}/map_world.png', 0.75, 1.3, w=5.6); MW, MH = 5.6, mp.height / 914400
def on_map(fx, fy): return 0.75 + fx * MW, 1.3 + fy * MH
for (fx, fy, bx, by, bw, txt) in ((0.21, 0.36, 0.75, 3.35, 2.2, '**USA:** about 1 in 5 used ChatGPT for health; 21% used AI vs 98% search engines'),
                                  (0.49, 0.22, 1.55, 1.15, 2.6, '**Netherlands** (n = 5322): health anxiety and searching **feed each other**'),
                                  (0.617, 0.32, 3.95, 3.35, 2.35, '**Baghdad (our study):** AI use **88.7%** · r = **0.47**')):
    px, py = on_map(fx, fy); line(s, px, py, bx + bw / 2, by + (0 if by > py else 0.5), color=AMBER, w=1.25)
    rect(s, px - 0.06, py - 0.06, 0.12, 0.12, ORANGE, None, MSO_SHAPE.OVAL)
    textbox(s, bx, by, bw, 0.5, txt, size=9.5, fill=WHITE, line=LIGHT, margin=0.06, anchor='m')
textbox(s, 6.65, 1.2, 2.57, 0.5, 'CORRELATION: HEALTH ANXIETY ↔ CYBERCHONDRIA', size=10, color=NAVY, bold=True)
for i, (lab, v, fill) in enumerate((('Meta-analysis, 2019', 0.62, STEEL), ('Meta-analysis, 2021', 0.63, STEEL), ('Our study', 0.47, ORANGE))):
    y = 1.85 + i * 0.68
    textbox(s, 6.65, y, 2.57, 0.28, lab, size=10, color=INK)
    rect(s, 6.65, y + 0.28, 2.1 * v / 0.63, 0.28, fill); textbox(s, 6.65 + 2.1 * v / 0.63 + 0.04, y + 0.26, 0.5, 0.3, f'{v:.2f}', size=10.5, color=NAVY, bold=True)
textbox(s, 6.65, 3.95, 2.57, 0.9, ['**Why weaker?**', 'Low, narrow health anxiety · confident internet users · the short CSS-12'], size=10, fill=C('FBF1E3'), line=ORANGE, margin=0.07, bold_color=AMBER)
order.append(s)

s = new_slide('COMPARISON WITH REGIONAL STUDIES')
mp = picture(s, f'{FIG}/map_region.png', 0.75, 1.2, h=3.55, frame=True); RW = mp.width / 914400
px, py = 0.75 + 0.318 * RW, 1.2 + 0.245 * 3.55
rect(s, px - 0.05, py - 0.05, 0.1, 0.1, WINE, None, MSO_SHAPE.OVAL); textbox(s, px - 0.95, py - 0.13, 0.88, 0.26, 'Palestine', size=9, color=WINE, bold=True, align='r')
studies = [('IRAQ · COVID-19 survey', '49.5% screened positive for health anxiety (different tool)', ORANGE), ('SAUDI ARABIA · Jeddah', 'Cyberchondria common in adults', SLATE),
           ('SAUDI ARABIA · primary care', '“Dr Google” use linked with health anxiety', SLATE), ('LEBANON', 'Arabic CSS-12 validated: same four dimensions as ours', NAVY),
           ('EGYPT · 1435 medical students', '85.8% had moderate cyberchondria', NAVY), ('PALESTINE', 'Health anxiety least common in medical students', WINE)]
for i, (head, txt, fill) in enumerate(studies):
    y = 1.2 + i * 0.6
    rect(s, 5.55, y, 0.08, 0.52, fill); rect(s, 5.63, y, 3.59, 0.52, WHITE, LIGHT)
    textbox(s, 5.7, y + 0.01, 3.48, 0.5, [f'**{head}**', txt], size=9.5, space=0, bold_color={str(ORANGE): AMBER, str(SLATE): NAVY}.get(str(fill), fill), anchor='m')
order.append(s)

s = new_slide('AI CHATBOTS AND THE CONSULTATION', 'CUSTOM_8_1')
panel(s, 0.79, 1.2, 4.12, 2.35, 'AI CHATBOTS', NAVY, ['* AI use **88.7%**, far above US surveys (about 20%): a young sample', '* AI users had **higher cyberchondria (+5.33 points)**, independently of health anxiety',
      '* A chatbot can be asked **one more question** at any hour', '* Caution: only **34 non-users**; cannot show cause'], size=11)
panel(s, 5.1, 1.2, 4.12, 2.35, 'THE CONSULTATION', ORANGE, ['* **34.7%** delayed care because they felt reassured: fewer visits, but risk of **late diagnosis**',
      '* **31.7%** never tell their doctor, mainly for fear of being judged', '* Open discussion strengthens the relationship; hidden searching strains it'], size=11)
textbox(s, 0.79, 3.8, 8.43, 0.7, '**Clinical message:** ask every patient, without judgement, what they searched or asked an AI', size=12, fill=C('FBF1E3'), line=ORANGE, anchor='m', align='c', bold_color=AMBER)
order.append(s)

s = new_slide('STRENGTHS AND LIMITATIONS', 'CUSTOM_8_1')
card(s, 0.79, 1.2, 4.12, 2.75, 'STRENGTHS', TEAL, '34:84', ['* Validated, reliable scales (alpha **0.81** and **0.86**)', '* Arabic and English versions, equally reliable',
     '* **AI chatbots** studied separately from search engines', '* Complete data: **no missing answers**', '* Results **adjusted** for confounders'], size=12)
card(s, 5.1, 1.2, 4.12, 2.75, 'LIMITATIONS', WINE, '34:79', ['* **Cross-sectional:** association, not cause', '* **Convenience online sample:** percentages cannot be generalised',
     '* No formal back-translation; self-reported answers', '* Small non-AI group (**34**); 57 events in the logistic model'], size=12)
keybox(s, 'Despite these limits: the first Baghdad data on health anxiety, cyberchondria and AI chatbots', 0.79, 4.1, 8.43, 0.6, fill=NAVY, size=12)
order.append(s)

s = new_slide('CONCLUSIONS', 'CUSTOM_8_1')
for i, (head, fill, icon, txt) in enumerate((('AI IS THE MAIN SOURCE', NAVY, '34:19', '**88.7%** used AI chatbots, mainly ChatGPT'), ('ONE IN FIVE', ORANGE, '36:82', '**19.0%** had elevated health anxiety on screening'),
                                            ('H1 SUPPORTED', TEAL, '21:47', 'Health anxiety and cyberchondria are linked (**r = 0.47**), independently of other factors'), ('AI AND CYBERCHONDRIA', SLATE, '35:76', 'AI users had higher cyberchondria (**+5.33 points**)'),
                                            ('H2 NOT SUPPORTED', WINE, '35:15', 'Medical students were not at higher risk once **age** was considered'), ('SEARCHING SHAPES CARE', NAVY, '35:70', '**34.7%** delayed care when reassured; **31.7%** never tell their doctor'))):
    card(s, 0.79 + (i % 3) * 2.865, 1.15 + (i // 3) * 1.83, 2.7, 1.7, head, fill, icon, txt, size=11.5)
order.append(s)

s = new_slide('RECOMMENDATIONS', 'CUSTOM_8_1')
for i, (head, fill, icon, txt) in enumerate((('CLINICIANS', NAVY, '35:70', 'Ask every patient, without judgement, what they searched or asked an AI'), ('MEDICAL EDUCATION', TEAL, '35:15', 'Teach digital and AI health literacy; see repeated searching as a sign of health anxiety'),
                                            ('MINISTRY OF HEALTH', ORANGE, '35:83', 'Arabic health-literacy campaigns and reliable Arabic symptom sources'), ('RESEARCH AND AI', WINE, '35:58', 'Longitudinal studies, random samples; AI answers that avoid escalating to rare diagnoses'))):
    card(s, 0.79 + (i % 2) * 2.9, 1.15 + (i // 2) * 1.83, 2.78, 1.7, head, fill, icon, txt, size=10.5)
picture(s, f'{FIG}/p_rec.jpg', 6.65, 1.2, h=3.55, frame=True)
order.append(s)

s = slides[20]
for sid in (792, 793, 794, 797, 798, 799, 804): delete(shp(s, sid))
textbox(s, 1.5, 0.7, 7.0, 0.9, 'r = 0.47', size=44, color=AMBER, bold=True, align='c', font=BODY)
textbox(s, 1.5, 1.55, 7.0, 0.4, 'Health anxiety and cyberchondria travel together.', size=14, color=INK, align='c', italic=True)
set_text(shp(s, 796), 'THANK YOU', color=NAVY); move(shp(s, 796), x=1.5, y=2.05, w=7.0, h=0.9)
set_text(shp(s, 795), ['Questions are welcome'], size=15, color=SLATE); move(shp(s, 795), y=2.95, h=0.45)
textbox(s, 1.5, 4.6, 7.0, 0.3, 'Template: Slidesgo  ·  photographs: Freepik and free stock images', size=8, color=SLATE, align='c')
order.append(s)

# ================================================================== titles in navy, then keep only these slides, in this order
for sl in order:
    for sh in sl.shapes:
        if sh.is_placeholder and sh.placeholder_format.type in (1, 3) and sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs: r.font.color.rgb = NAVY
lst = prs.slides._sldIdLst
by_id = {e.get('id'): e for e in list(lst)}
keep = [str(s.slide_id) for s in order]
for e in list(lst):
    if e.get('id') not in keep: prs.part.drop_rel(e.get(qn('r:id'))); lst.remove(e)
for sid in keep: lst.append(by_id[sid])
prs.save(OUT); print('wrote', OUT, len(keep), 'slides')
