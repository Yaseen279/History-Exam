"""Defence presentation built in the Slidesgo template the student chose.
Input: the template with duplicated slides (4 x3, 6 x2, 8 x2, 9 x2) made with the pptx skill's add_slide.py.
Usage: python3 25_slidesgo_deck.py <template_with_duplicates.pptx> <figures dir> <out.pptx>"""
import sys, copy, re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree

SRC, FIG, OUT = sys.argv[1:4]
prs = Presentation(SRC)
NAVY, SLATE, STEEL, LIGHT, PALE, GREY = (RGBColor.from_string(c) for c in ('0E2A47', '445F73', '7D95A8', 'C2D6E7', 'F3F3F5', '505050'))
BODY, HEAD = 'DM Sans', 'Raleway'
slides = {int(re.search(r'(\d+)\.xml$', s.part.partname).group(1)): s for s in prs.slides}   # by template slide file number
LAYOUT = {l.name: l for l in prs.slide_layouts}

# ------------------------------------------------------------------ helpers
def shp(slide, sid):
    for s in slide.shapes:
        if s.shape_id == sid: return s
    raise KeyError(sid)

def runs_of(text):
    parts = text.split('**'); return [(p, i % 2 == 1) for i, p in enumerate(parts) if p]

def set_text(shape, items, size=None, align=None, color=None):
    """Replace the text, keeping the template's paragraph and run formatting. items: list of str; '* ' prefix = bullet."""
    body = shape.text_frame._txBody
    paras = body.findall(qn('a:p'))
    plain = next((p for p in paras if p.find('.//' + qn('a:buChar')) is None), paras[0])
    bullet = next((p for p in paras if p.find('.//' + qn('a:buChar')) is not None), None)
    for p in paras: body.remove(p)
    if isinstance(items, str): items = [items]
    for it in items:
        is_b = it.startswith('* ') and bullet is not None
        tp = copy.deepcopy(bullet if is_b else plain)
        r0 = tp.find(qn('a:r')); rpr = copy.deepcopy(r0.find(qn('a:rPr'))) if r0 is not None and r0.find(qn('a:rPr')) is not None else etree.SubElement(etree.Element('x'), qn('a:rPr'))
        for el in list(tp):
            if el.tag in (qn('a:r'), qn('a:br'), qn('a:fld')): tp.remove(el)
        end = tp.find(qn('a:endParaRPr'))
        for txt, bold in runs_of(it[2:] if is_b else it):
            r = etree.Element(qn('a:r')); rp = copy.deepcopy(rpr); r.append(rp)
            if bold: rp.set('b', '1')
            if size: rp.set('sz', str(int(size * 100)))
            if color is not None:
                for f in rp.findall(qn('a:solidFill')): rp.remove(f)
                sf = etree.SubElement(rp, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', str(color)); rp.insert(0, sf)
            t = etree.SubElement(r, qn('a:t')); t.text = txt
            (tp.insert(list(tp).index(end), r) if end is not None else tp.append(r))
        if align is not None:
            ppr = tp.find(qn('a:pPr')); ppr.set('algn', {'l': 'l', 'c': 'ctr', 'r': 'r'}[align])
        body.append(tp)

def move(shape, x=None, y=None, w=None, h=None):
    if x is not None: shape.left = Inches(x)
    if y is not None: shape.top = Inches(y)
    if w is not None: shape.width = Inches(w)
    if h is not None: shape.height = Inches(h)

def delete(shape): shape._element.getparent().remove(shape._element)

def swap_picture(slide, shape, path):
    _, rid = slide.part.get_or_add_image_part(path)
    blip = shape._element.find('.//' + qn('a:blip')); blip.set(qn('r:embed'), rid)
    src = shape._element.find('.//' + qn('a:srcRect'))
    if src is not None: src.getparent().remove(src)

def textbox(slide, x, y, w, h, items, size=11, color=GREY, bold=False, align='l', font=BODY, fill=None, anchor='t', margin=0.04):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE}[anchor]
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, side, Inches(margin))
    if fill is not None: tb.fill.solid(); tb.fill.fore_color.rgb = fill
    if isinstance(items, str): items = [items]
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        bul = it.startswith('* ')
        if bul:
            it = it[2:]; ppr = p._p.get_or_add_pPr(); ppr.set('marL', str(Inches(0.17))); ppr.set('indent', str(-Inches(0.17)))
            bf = etree.SubElement(ppr, qn('a:buFont')); bf.set('typeface', 'Arial'); etree.SubElement(ppr, qn('a:buChar')).set('char', '•')
        p.space_after = Pt(4)
        for txt, b in runs_of(it):
            r = p.add_run(); r.text = txt; f = r.font; f.size = Pt(size); f.name = font; f.bold = bold or b
            f.color.rgb = NAVY if (b and not bold and fill is None) else color
    return tb

def picture(slide, path, x, y, w=None, h=None):
    kw = {}
    if w: kw['width'] = Inches(w)
    if h: kw['height'] = Inches(h)
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), **kw)
    if w and h is None and pic.height > Inches(3.7):   # keep inside the frame
        r = Inches(3.7) / pic.height; pic.height = Inches(3.7); pic.width = int(pic.width * r)
    return pic

def cell_border(cell, color='B7C7D5', w=9525):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
        old = tcPr.find(qn(tag))
        if old is not None: tcPr.remove(old)
    fill = tcPr.find(qn('a:solidFill'))
    for i, tag in enumerate(('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB')):
        ln = etree.Element(qn(tag)); ln.set('w', str(w)); sf = etree.SubElement(ln, qn('a:solidFill')); etree.SubElement(sf, qn('a:srgbClr')).set('val', color)
        tcPr.insert(i, ln)

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
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid(); c.fill.fore_color.rgb = LIGHT if i == 0 else (RGBColor.from_string('E8EFF5') if (i - 1) in hi else RGBColor.from_string('FFFFFF'))
            tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
            for txt, b in runs_of(str(val)):
                run = p.add_run(); run.text = txt; f = run.font; f.size = Pt(size); f.name = BODY
                f.bold = i == 0 or b or (j == 0) or ((i - 1) in hi); f.color.rgb = NAVY if (i == 0 or (i - 1) in hi or j == 0 or b) else GREY
            cell_border(c)
    return gf

def new_slide(title, layout='CUSTOM_8'):
    s = prs.slides.add_slide(LAYOUT[layout]); s.shapes.title.text = title
    return s

def keybox(slide, text, x, y, w, h=0.42, fill=NAVY, size=11):
    return textbox(slide, x, y, w, h, text, size=size, color=RGBColor.from_string('FFFFFF'), bold=True, align='c', fill=fill, anchor='m', margin=0.06)

order = []

# ------------------------------------------------------------------ 1 title
s = slides[1]
t = shp(s, 432); move(t, y=0.72, h=2.45)
body = t.text_frame._txBody; p = body.find(qn('a:p')); rs = p.findall(qn('a:r'))
rs[0].find(qn('a:t')).text = 'HEALTH ANXIETY, AI CHATBOT USE AND '; rs[1].find(qn('a:t')).text = 'CYBERCHONDRIA'; rs[2].find(qn('a:t')).text = ''
tail = copy.deepcopy(rs[0]); tail.find(qn('a:t')).text = ' AMONG ADULTS IN BAGHDAD'; rs[2].addnext(tail)
for r in p.findall(qn('a:r')): r.find(qn('a:rPr')).set('sz', '3000')
sub = shp(s, 433); move(sub, y=3.22, h=1.45)
set_text(sub, ['An online cross-sectional survey', '**Abdulrahman Jamal Ghazi  ·  Mustafa Wamedh Mustafa  ·  Yaseen Omar Lutfi**',
               'Supervised by Assist. Prof. Dr. Thikra Hasan Mathkor', 'College of Medicine  ·  University of Baghdad  ·  2026'], size=10.5)
order.append(s)

# ------------------------------------------------------------------ 2 contents
s = slides[3]
for sid, txt in zip((454, 455, 456, 457, 458, 459), ('INTRODUCTION', 'METHODS', 'RESULTS', 'DISCUSSION', 'CONCLUSIONS', 'RECOMMENDATIONS')): set_text(shp(s, sid), txt, size=13)
move(shp(s, 459), w=2.75)
order.append(s)

def divider(n, num, title, photo):
    s = slides[n]; set_text(shp(s, 464), title); set_text(shp(s, 465), num); swap_picture(s, shp(s, 466), f'{FIG}/{photo}'); return s

# ------------------------------------------------------------------ 3-7 introduction
order.append(divider(4, '01', 'INTRODUCTION', 'p_intro.jpg'))
s = slides[5]
set_text(shp(s, 471), 'BACKGROUND')
set_text(shp(s, 472), ['Many people now search their symptoms online, or **ask an AI chatbot**, before they see a doctor.',
                       '* About **4 in 5** Iraqis are online', '* For some, searching **increases worry** instead of relieving it', '* AI chatbots answer fluently, personally and at any hour'], size=11)
swap_picture(s, shp(s, 473), f'{FIG}/p_background.jpg'); order.append(s)

s = slides[6]
set_text(shp(s, 481), 'HEALTH ANXIETY AND CYBERCHONDRIA')
set_text(shp(s, 484), 'HEALTH ANXIETY'); set_text(shp(s, 480), 'CYBERCHONDRIA')
set_text(shp(s, 483), 'Persistent worry about having or getting a serious illness, kept going by misreading normal body sensations', size=11)
set_text(shp(s, 482), 'Excessive, repeated online health searching that increases distress instead of relieving it: a pattern, not a diagnosis', size=11)
for sid in (483, 482): move(shp(s, sid), h=1.3)
keybox(s, 'Two meta-analyses: strongly linked (r = 0.62–0.63), and they may feed each other', 1.15, 4.2, 7.7, 0.42, fill=SLATE, size=10.5)
order.append(s)

s = slides[7]
set_text(shp(s, 502), 'WHY THIS STUDY?')
for h, b, ht, bt in ((503, 505, 'NO LOCAL DATA', 'No study of cyberchondria from Baghdad, although about four in five Iraqis are online'),
                     (504, 506, 'AI CHATBOTS', 'A new way to search: almost no studies separate chatbots from ordinary search engines'),
                     (508, 507, 'MEDICAL STUDENTS', 'Does learning about diseases make students more anxious? The evidence is mixed')):
    set_text(shp(s, h), ht, size=13); set_text(shp(s, b), bt, size=11)
order.append(s)

s = slides[8]
set_text(shp(s, 538), 'AIM AND HYPOTHESES')
for h, b, ht, bt in ((539, 534, 'AIM', 'To study the link between health anxiety and cyberchondria in adults in Baghdad, with a focus on AI chatbots and medical students'),
                     (541, 535, 'OBJECTIVES', 'Describe online searching · measure both conditions and their link · compare medical students with others'),
                     (540, 536, 'H1: PRIMARY', 'More health anxiety goes with more cyberchondria, **independently of other factors**'),
                     (542, 537, 'H2: SECONDARY', 'Medical students have **higher** health anxiety and cyberchondria than other participants')):
    set_text(shp(s, h), ht); set_text(shp(s, b), bt, size=10.5)
order.append(s)

# ------------------------------------------------------------------ 8-11 methods
order.append(divider(42, '02', 'METHODS', 'p_methods.jpg'))
s = slides[9]
set_text(shp(s, 580), 'STUDY DESIGN')
for h, b, ht, bt in ((585, 581, 'DESIGN', 'Analytical cross-sectional online survey (STROBE, CHERRIES)'), (586, 582, 'SETTING', 'Baghdad · Google Form in Arabic and English'),
                     (587, 588, 'SAMPLING', 'Convenience and snowball, through social-media groups'), (590, 583, 'PARTICIPANTS', '300 adults aged 18 or older (194 needed) · no missing data'),
                     (591, 584, 'TOOLS', 'SHAI-14 for health anxiety · CSS-12 for cyberchondria'), (592, 589, 'ETHICS', 'Electronic informed consent · anonymous and voluntary')):
    set_text(shp(s, h), ht); set_text(shp(s, b), bt, size=10)
order.append(s)

s = new_slide('THE QUESTIONNAIRE', 'CUSTOM_8_1')
table(s, ['Part', 'Content', 'Scoring'], [
    ['1', 'Consent and socio-demographic data', 'Age, gender, education, study or work, chronic condition'],
    ['2', 'Online health-information seeking', 'Tools used, main AI chatbot, motives, trust (1–5)'],
    ['3', 'Short Health Anxiety Inventory (SHAI-14)', '14 items, each 0–3; total 0–42'],
    ['4', 'Cyberchondria Severity Scale (CSS-12)', '12 items, each 1–5; total 12–60; four dimensions'],
    ['5', 'Behaviour after searching', 'Actions taken, telling the doctor, effect on the relationship']], 0.79, 1.3, 8.43, [0.6, 3.5, 4.33], size=10.5, hi=(2, 3), row_h=0.36)
textbox(s, 0.79, 3.72, 8.43, 1.05, ['* **Elevated health anxiety:** SHAI-14 of 18 or more (a screening cut-off, not a diagnosis)',
                                    '* **High cyberchondria:** CSS-12 above 33 (the upper third)',
                                    '* **Reliability:** Cronbach’s alpha 0.81 (SHAI-14) and 0.86 (CSS-12), the same in Arabic and English'], size=10.5)
order.append(s)

s = slides[16]
set_text(shp(s, 726), 'CHOOSING THE STATISTICAL TESTS')
set_text(shp(s, 727), 'SCORES CHECKED WITH SHAPIRO–WILK: NOT NORMAL → NON-PARAMETRIC TESTS', size=9.5)
for h, b, ht, bt in ((729, 731, 'SCORE: 2 GROUPS', ['Mann–Whitney U', '(instead of the t-test)', 'Groups shown as medians (IQR)']),
                     (728, 735, 'SCORE: 3+ GROUPS', ['Kruskal–Wallis H', '(instead of ANOVA)']),
                     (730, 742, 'YES/NO × GROUP', ['Chi-square', 'Fisher’s exact test if an expected count is below 5', 'Cramér’s V for strength']),
                     (736, 738, 'SCORE × SCORE', ['Pearson r', 'confirmed by Spearman rho', 'Partial correlation (adjusted)'])):
    set_text(shp(s, h), ht, size=9.5); set_text(shp(s, b), bt, size=10)
set_text(shp(s, 739), 'ALL FACTORS TOGETHER: LINEAR REGRESSION (SCORE) · LOGISTIC REGRESSION (YES/NO)', size=9.5)
order.append(s)

# ------------------------------------------------------------------ 12-20 results
order.append(divider(43, '03', 'RESULTS', 'p_results.jpg'))
s = slides[10]
set_text(shp(s, 649), '300'); set_text(shp(s, 646), 'adults in Baghdad, complete data')
set_text(shp(s, 647), '62.3%'); set_text(shp(s, 648), 'aged 20–29 years')
set_text(shp(s, 650), '44.0%'); set_text(shp(s, 651), 'medical students')
textbox(s, 0.79, 0.52, 5, 0.55, 'THE PARTICIPANTS', size=24, color=GREY, font='Raleway Black')
order.append(s)

s = new_slide('WHERE PEOPLE SEARCH'); pic = picture(s, f'{FIG}/sample1_phone_tools.png', 0, 1.22, h=3.6); pic.left = int((prs.slide_width - pic.width) / 2); order.append(s)
s = new_slide('WHAT PEOPLE DID AFTER SEARCHING'); pic = picture(s, f'{FIG}/sample4_path_after_search.png', 0, 1.25, h=3.55); pic.left = int((prs.slide_width - pic.width) / 2); order.append(s)

s = new_slide('LEVELS OF HEALTH ANXIETY')
pic = picture(s, f'{FIG}/sample3_one_in_five.png', 0, 1.3, w=7.2); pic.left = int((prs.slide_width - pic.width) / 2)
table(s, ['Scale', 'Mean ± SD', 'Median (IQR)', 'Cronbach’s alpha'], [['SHAI-14 (0–42)', '12.35 ± 5.83', '12 (8–16)', '0.81'], ['CSS-12 (12–60)', '28.86 ± 8.36', '29 (23–34)', '0.86']],
      1.4, 4.15, 7.2, [2.1, 1.7, 1.7, 1.7], size=10, row_h=0.26)
order.append(s)

s = new_slide('MAIN FINDING (H1)')
picture(s, f'{FIG}/scatter_shai_css.png', 0.79, 1.2, h=3.45)
picture(s, f'{FIG}/sample2_cycle_dimensions.png', 5.55, 1.2, w=3.65)
textbox(s, 5.55, 3.62, 3.65, 0.9, ['* Moderate link: **r = 0.47**; **0.48** after adjustment', '* Health anxiety accounts for about **22%**', '* An association, **not proof of cause**'], size=10)
keybox(s, 'H1 SUPPORTED', 5.55, 4.45, 3.65, 0.36, size=11)
order.append(s)

s = new_slide('WHAT PREDICTS CYBERCHONDRIA?')
cd = CategoryChartData(); cd.categories = ['1. Who you are', '2. + How you search', '3. + Health anxiety']; cd.add_series('R² (%)', (3.0, 13.3, 31.7))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.79), Inches(1.2), Inches(3.9), Inches(3.55), cd); ch = gf.chart
ch.has_legend = False; ch.has_title = True; ch.chart_title.text_frame.text = 'Variance explained (R², %)'
tr = ch.chart_title.text_frame.paragraphs[0].runs[0].font; tr.size = Pt(11); tr.name = BODY; tr.color.rgb = NAVY; tr.bold = True
pl = ch.plots[0]; pl.gap_width = 70; pl.has_data_labels = True; dl = pl.data_labels; dl.number_format = '0.0"%"'; dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END; dl.font.size = Pt(11); dl.font.bold = True; dl.font.color.rgb = NAVY; dl.font.name = BODY
for i, pt in enumerate(pl.series[0].points):
    pt.format.fill.solid(); pt.format.fill.fore_color.rgb = NAVY if i == 2 else STEEL
va = ch.value_axis; va.maximum_scale = 40; va.minimum_scale = 0; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGBColor.from_string('E3EAF0')
va.tick_labels.font.size = Pt(9); va.tick_labels.font.color.rgb = GREY; va.tick_labels.font.name = BODY; va.format.line.fill.background()
ca = ch.category_axis; ca.tick_labels.font.size = Pt(9); ca.tick_labels.font.color.rgb = GREY; ca.tick_labels.font.name = BODY
table(s, ['Predictor (final model)', 'B (95% CI)', 'Beta', 'p'], [
    ['Health anxiety (per point)', '0.68 (0.53–0.84)', '0.48', '< 0.001'], ['AI chatbot user', '5.33 (2.57–8.09)', '0.20', '< 0.001'],
    ['Age 30–39 (vs 20–29)', '6.27 (2.42–10.11)', '0.19', '0.001'], ['Age 40 or older', '3.98 (0.16–7.80)', '0.15', '0.041'],
    ['All other factors', 'not significant', '', '']], 4.95, 1.3, 4.27, [1.75, 1.32, 0.5, 0.7], size=9.5, hi=(0, 1), row_h=0.3)
textbox(s, 4.95, 3.25, 4.27, 1.0, ['* Health anxiety **added 18.4%** after all other factors', '* AI users scored **5.3 points higher**, independently of health anxiety',
                                   '* The model explained **32%** of the differences'], size=10)
keybox(s, 'HEALTH ANXIETY IS THE STRONGEST PREDICTOR (BETA = 0.48)', 4.95, 4.3, 4.27, 0.42, size=9.5)
order.append(s)

s = new_slide('WHO HAD ELEVATED HEALTH ANXIETY?')
picture(s, f'{FIG}/forest_HA.png', 0.79, 1.25, w=5.35)
textbox(s, 6.35, 1.3, 2.87, 2.4, ['**Adjusted odds ratios**', '* Cyberchondria: **3.12** per SD', '* Seeking instant reassurance: **3.83**', '* Each older age group: **0.61** (protective)',
                                  '**Model checks**', '* Hosmer–Lemeshow p = **0.50**: good fit', '* AUC = **0.83**: good discrimination'], size=10)
textbox(s, 6.35, 3.85, 2.87, 0.85, 'Only 57 cases for 11 factors, so the odds ratios may be overestimated', size=9.5, color=SLATE)
order.append(s)

s = new_slide('MEDICAL STUDENTS VS OTHERS (H2)', 'CUSTOM_8_1')
table(s, ['Measure', 'Medical students (n = 132)', 'Others (n = 168)', 'p', 'Adjusted p'], [
    ['SHAI-14, median (IQR)', '12.5 (10–17)', '11 (7–15)', '0.004', '0.081'], ['Elevated health anxiety', '23.5%', '15.5%', '0.079', '0.238'],
    ['CSS-12, median (IQR)', '29 (23–34)', '29 (23–34)', '0.989', '0.627'], ['High cyberchondria', '28.0%', '29.2%', '0.829', '0.771']],
      0.79, 1.3, 8.43, [2.3, 2.05, 1.75, 1.0, 1.33], size=10.5, hi=(0,), row_h=0.34)
textbox(s, 0.79, 3.25, 5.0, 1.5, ['* Before adjustment, medical students had **higher health anxiety**', '* After adjusting for **age**, sex, chronic condition and language, the difference was **no longer significant**',
                                  '* Cyberchondria was **identical**'], size=10.5)
keybox(s, ['H2 NOT SUPPORTED', 'Age, not studying medicine, explained the difference'], 6.1, 3.35, 3.12, 1.1, size=11)
order.append(s)

# ------------------------------------------------------------------ 21-25 discussion and close
s = new_slide('COMPARISON WITH OTHER STUDIES', 'CUSTOM_8_1')
table(s, ['Finding', 'Our study', 'Other studies', 'Likely explanation'], [
    ['Health anxiety–cyberchondria link', 'r = 0.47', 'r = 0.62–0.63 (two meta-analyses)', 'Low, narrow health anxiety; the short CSS-12'],
    ['AI chatbot use for health', '88.7%', 'About 1 in 5 in US surveys', 'A young, educated, online sample'],
    ['AI use and cyberchondria', '+5.33 points', 'Very few studies', 'Chatbots can be asked again and again'],
    ['Medical students', 'No difference after adjustment', 'Palestine: least common · Egypt: high levels', 'Age explained the difference']],
      0.79, 1.3, 8.43, [2.3, 1.75, 2.2, 2.18], size=10, row_h=0.42)
keybox(s, 'The first study of cyberchondria in Baghdad, and one of few to examine AI chatbots separately', 0.79, 4.3, 8.43, 0.4, fill=SLATE, size=10.5)
order.append(s)

s = slides[44]
set_text(shp(s, 481), 'STRENGTHS AND LIMITATIONS'); set_text(shp(s, 484), 'STRENGTHS'); set_text(shp(s, 480), 'LIMITATIONS')
set_text(shp(s, 483), ['Validated, reliable scales (alpha 0.81 and 0.86)', 'Arabic and English versions', 'AI chatbots studied separately', 'Complete data; adjusted models'], size=10.5)
set_text(shp(s, 482), ['Cross-sectional: association, not cause', 'Convenience online sample: cannot generalise', 'No formal back-translation; self-report', 'Small non-AI group (34)'], size=10.5)
for sid in (483, 482): move(shp(s, sid), h=1.9)
order.append(s)

s = slides[46]
set_text(shp(s, 580), 'CONCLUSIONS')
for g in (596, 604, 612, 615, 630, 637): delete(shp(s, g))
for circ, n in zip((603, 602, 601, 595, 594, 593), '123456'):
    c = shp(s, circ); tf = c.text_frame; tf.text = n; r = tf.paragraphs[0].runs[0]; r.font.size = Pt(16); r.font.bold = True; r.font.color.rgb = NAVY; r.font.name = HEAD
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
for h, b, ht, bt in ((585, 581, 'AI IS THE MAIN SOURCE', '88.7% used AI chatbots, mainly ChatGPT'), (586, 582, 'ONE IN FIVE', '19.0% had elevated health anxiety on screening'),
                     (587, 588, 'H1 SUPPORTED', 'Health anxiety and cyberchondria are linked (r = 0.47), independently'), (590, 583, 'AI AND CYBERCHONDRIA', 'AI users had higher cyberchondria (+5.33 points)'),
                     (591, 584, 'H2 NOT SUPPORTED', 'Medical students were not at higher risk once age was considered'), (592, 589, 'SEARCHING SHAPES CARE', '34.7% delayed care when reassured; 31.7% never tell their doctor')):
    set_text(shp(s, h), ht, size=12); set_text(shp(s, b), bt, size=10)
order.append(s)

s = slides[45]
set_text(shp(s, 538), 'RECOMMENDATIONS')
for h, b, ht, bt in ((539, 534, 'CLINICIANS', 'Ask every patient, without judgement, what they searched or asked an AI, and what they found'),
                     (541, 535, 'MEDICAL EDUCATION', 'Teach digital and AI health literacy; treat repeated searching as a sign of health anxiety'),
                     (540, 536, 'MINISTRY OF HEALTH', 'Arabic health-literacy campaigns and reliable Arabic sources for symptom advice'),
                     (542, 537, 'RESEARCH AND AI DEVELOPERS', 'Longitudinal studies with random samples; AI answers that avoid escalating to rare diagnoses')):
    set_text(shp(s, h), ht, size=13); set_text(shp(s, b), bt, size=10.5)
order.append(s)

s = slides[20]
set_text(shp(s, 796), 'THANK YOU'); move(shp(s, 796), x=1.5, w=7.0); set_text(shp(s, 795), ['Questions and discussion'], size=16); move(shp(s, 795), y=2.15)
for sid in (792, 793, 794, 797, 798, 799, 804): delete(shp(s, sid))
textbox(s, 1.5, 4.55, 7.0, 0.4, 'Photographs: Wikimedia Commons (ChatGPT phone: Jernej Furman, CC BY 2.0; person with phone: Japanexperterna.se, CC BY-SA 2.0; '
        'University of Baghdad: alameedy, CC0; medical students: Binil Zack, CC BY-SA 4.0; doctor and patient: National Cancer Institute, public domain)', size=7, color=SLATE, align='c')
order.append(s)

# ------------------------------------------------------------------ keep only these slides, in this order
lst = prs.slides._sldIdLst; ids = {s.slide_id: e for e in lst for s in [None] if False}
by_id = {e.get('id'): e for e in list(lst)}
keep = [str(s.slide_id) for s in order]
for e in list(lst):
    if e.get('id') not in keep:
        prs.part.drop_rel(e.get(qn('r:id'))); lst.remove(e)
for sid in keep: lst.append(by_id[sid])
prs.save(OUT); print('wrote', OUT, len(keep), 'slides')
