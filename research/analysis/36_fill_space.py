"""Apply the suggested pictures and space fillers to the students' own deck (nothing else touched).
Usage: python3 36_fill_space.py <their.pptx> <figures dir> <out.pptx> [methods_photo]"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
SRC, FIG, OUT = sys.argv[1:4]; METHODS = sys.argv[4] if len(sys.argv) > 4 else 'phone_form.png'
prs = Presentation(SRC); S = prs.slides
NAVY, SLATE, LIGHT, INK, WHITE, PALE = (RGBColor.from_string(c) for c in ('0E2A47', '445F73', 'C2D6E7', '1D2230', 'FFFFFF', 'E4ECF3'))

def tb(s, x, y, w, h, lines, size=11, color=INK, bold=False, fill=None, line=None, align='c', anchor='m'):
    b = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = b.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE if anchor == 'm' else MSO_ANCHOR.TOP
    for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, m, Inches(0.07))
    if fill is not None: b.fill.solid(); b.fill.fore_color.rgb = fill
    if line is not None: b.line.color.rgb = line; b.line.width = Pt(1)
    for i, ln in enumerate([lines] if isinstance(lines, str) else lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = {'c': PP_ALIGN.CENTER, 'l': PP_ALIGN.LEFT}[align]
        for k, part in enumerate(ln.split('**')):
            if not part: continue
            r = p.add_run(); r.text = part; f = r.font; f.size = Pt(size); f.name = 'DM Sans'; f.bold = bold or k % 2 == 1
            f.color.rgb = color if not (k % 2 == 1 and fill is None) else NAVY
    return b
def tiles(s, x, y, w, h, items, gap=0.15):
    tw = (w - gap * (len(items) - 1)) / len(items)
    for i, (num, lab) in enumerate(items):
        xx = x + i * (tw + gap)
        r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(xx), Inches(y), Inches(tw), Inches(h)); r.fill.solid(); r.fill.fore_color.rgb = WHITE
        r.line.color.rgb = LIGHT; r.line.width = Pt(1); r.shadow.inherit = False
        tb(s, xx, y + 0.04, tw, h * 0.55, num, size=20, color=NAVY, bold=True)
        tb(s, xx, y + h * 0.55, tw, h * 0.4, lab, size=10, color=INK)
def swap(s, pic, path):
    _, rid = s.part.get_or_add_image_part(path)
    pic._element.find('.//' + qn('a:blip')).set(qn('r:embed'), rid)
    src = pic._element.find('.//' + qn('a:srcRect'))
    if src is not None: src.getparent().remove(src)

# 4 Health anxiety: cycle diagram instead of the photo
s = S[3]; pic = next(sh for sh in s.shapes if sh.shape_type == 13); swap(s, pic, f'{FIG}/ha_cycle.png')
# 5 Cyberchondria
tb(S[4], 0.79, 4.33, 8.43, 0.5, '**Linked with health anxiety in two meta-analyses (r = 0.62–0.63); the two may feed each other**', size=11.5, color=WHITE, bold=True, fill=NAVY)
# 6 Dr Google -> Dr AI
tiles(S[5], 0.79, 3.0, 4.35, 1.05, [('88.7%', 'used AI chatbots'), ('59.3%', 'ChatGPT'), ('23.7%', 'Gemini')])
tb(S[5], 0.79, 4.3, 8.43, 0.5, '**The gap:** no cyberchondria data from Baghdad · AI chatbots rarely studied separately from search engines', size=11, fill=PALE, line=SLATE)
# 8 Methods divider: picture in the empty frame
s = S[7]; ph = next(sh for sh in s.shapes if sh.is_placeholder and sh.placeholder_format.idx == 3)
ph.insert_picture(f'{FIG}/{METHODS}')
# 10 Questionnaire
tiles(S[9], 7.0, 3.98, 2.22, 0.9, [('41', 'questions'), ('5', 'parts')], gap=0.12)
# 12 Statistical tests
tb(S[11], 0.79, 4.3, 8.43, 0.45, 'All analyses in **IBM SPSS Statistics 26** · two-sided p < 0.05', size=11.5, fill=PALE, line=SLATE)
# 22 Worldwide
tb(S[21], 6.65, 3.95, 2.57, 0.85, ['**Why weaker?**', 'Low, narrow health anxiety · young online sample · short CSS-12'], size=9.5, fill=PALE, line=SLATE, align='l', anchor='t')
# 24 AI and the consultation
tb(S[23], 0.79, 3.8, 8.43, 0.65, '**Clinical message:** ask every patient, without judgement, what they searched or asked an AI', size=12.5, color=WHITE, fill=NAVY)
# 29 Thank you
s = S[28]
tb(s, 1.6, 0.75, 6.8, 0.6, '**r = 0.47**  ·  health anxiety and cyberchondria travel together', size=15, color=SLATE)
sub = next(sh for sh in s.shapes if sh.is_placeholder and sh.placeholder_format.idx == 1)
sub.text_frame.text = 'Questions are welcome'; sub.left, sub.top, sub.width, sub.height = Inches(1.6), Inches(3.0), Inches(6.8), Inches(0.4)
for r in sub.text_frame.paragraphs[0].runs: r.font.size = Pt(15); r.font.color.rgb = SLATE
sub.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
prs.save(OUT); print('saved', OUT)
