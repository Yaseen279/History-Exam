"""Apply the agreed changes to the students' deck: new health-anxiety photo, "Dr AI" title, phone with the real
questionnaire on the Methods divider, slightly larger questionnaire and statistics slides, and a short "Why weaker?" box.
Usage: python3 37_apply_choices.py <their.pptx> <figures dir> <out.pptx>"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
SRC, FIG, OUT = sys.argv[1:4]
prs = Presentation(SRC); S = prs.slides
NAVY, SLATE, INK, PALE = (RGBColor.from_string(c) for c in ('0E2A47', '445F73', '1D2230', 'E4ECF3'))

def swap(s, pic, path):
    _, rid = s.part.get_or_add_image_part(path)
    pic._element.find('.//' + qn('a:blip')).set(qn('r:embed'), rid)
    src = pic._element.find('.//' + qn('a:srcRect'))
    if src is not None: src.getparent().remove(src)
def bump(shape, d):
    for r in shape._element.iter(qn('a:rPr')):
        if r.get('sz'): r.set('sz', str(int(int(r.get('sz')) + d * 100)))
    for r in shape._element.iter(qn('a:endParaRPr')):
        if r.get('sz'): r.set('sz', str(int(int(r.get('sz')) + d * 100)))

# slide 4: worried woman at her laptop instead of the neck-pain photo
s = S[3]; swap(s, next(sh for sh in s.shapes if sh.shape_type == 13), f'{FIG}/ha_opt1.jpg')

# slide 6: "Dr ChatGPT" -> "Dr AI" in the title only
for sh in S[5].shapes:
    if sh.has_text_frame:
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if 'CHATGPT' in r.text and 'DR' in r.text.upper(): r.text = r.text.replace('“DR CHATGPT”', '“DR AI”').replace('"DR CHATGPT"', '"DR AI"').replace('DR CHATGPT', 'DR AI')
print('slide 6 title:', S[5].shapes.title.text_frame.text)

# slide 8: phone with the real questionnaire in the empty picture frame
s = S[7]; ph = next(sh for sh in s.shapes if sh.is_placeholder and sh.placeholder_format.idx == 3)
ph.insert_picture(f'{FIG}/phone_questionnaire.png')

# slide 10: questionnaire table and definition lines one size up
s = S[9]
for sh in s.shapes:
    if sh.has_table or (sh.has_text_frame and sh.text_frame.text.startswith('Elevated')): bump(sh, 1)
for sh in s.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith('Elevated'): sh.top = Inches(4.05); sh.width = Inches(8.43)

# slide 12: statistics tree stretched to fill the slide and text one size up
s = S[11]; TOP = Inches(1.12); K = 1.25
for sh in s.shapes:
    if sh.is_placeholder: continue
    sh.top = int(TOP + (sh.top - TOP) * K); sh.height = int(sh.height * K)
    if sh.has_text_frame: bump(sh, 1)

# slide 22: short "Why weaker?" box under the bars
s = S[21]
b = s.shapes.add_textbox(Inches(6.65), Inches(3.92), Inches(2.57), Inches(0.95)); tf = b.text_frame; tf.word_wrap = True
for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, m, Inches(0.07))
b.fill.solid(); b.fill.fore_color.rgb = PALE; b.line.color.rgb = SLATE; b.line.width = Pt(1)
for i, (t, bold) in enumerate((('Why weaker?', True), ('• Narrow range of health anxiety (mean SHAI 12.3)', False), ('• Young, confident internet users', False),
                               ('• Short CSS-12 (most studies used the 33-item scale)', False))):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); r = p.add_run(); r.text = t
    r.font.size = Pt(9.5); r.font.name = 'DM Sans'; r.font.bold = bold; r.font.color.rgb = NAVY if bold else INK
prs.save(OUT); print('saved', OUT)
