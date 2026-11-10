"""Build the graduation research paper (.docx) from the analysis outputs.

Usage: python3 04_build_docx.py <outdir> <docx path>
College format: Times New Roman 14; Abstract (<=1.5 pages); Introduction (>=4 pages);
Method; Results; Discussion; Conclusions and Recommendations; References (Vancouver).
Preliminary pages (Title, Acknowledgment, Abbreviations, Tables, Figures, Abstract) use
roman numerals; arabic numbering starts at 1 on the Introduction.
"""
import os, sys, json, re
import numpy as np, pandas as pd
from scipy import stats
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from refs import REFS

OUT, DOCX = sys.argv[1], sys.argv[2]
d = pd.read_pickle(f'{OUT}/analysed.pkl')
X = pd.read_excel(f'{OUT}/tables/all_results.xlsx', sheet_name=None, index_col=0)
R = json.load(open(f'{OUT}/summary.json'))
E = json.load(open(f'{OUT}/extra.json'))
INV = pd.read_csv(f'{OUT}/tables/invariance_mgcfa.csv').set_index(['Scale', 'Model'])   # from 02c_invariance.py
DIF = pd.read_csv(f'{OUT}/tables/invariance_dif.csv')
def inv(scale, model, col): return INV.loc[(scale, model), col]
_prev = {'metric': 'configural', 'scalar': 'metric'}
def dcfi(scale, model): return round(INV.loc[(scale, model), 'CFI'], 3) - round(INV.loc[(scale, _prev[model]), 'CFI'], 3)
IS, IC = 'SHAI-14 (one factor)', 'CSS-12 (four factors)'
n = len(d)
FONT = 'Times New Roman'

# ------------------------------------------------------------------ helpers
def f2(x): return f'{x:.2f}'
def f1(x): return f'{x:.1f}'
def f3(x): return f'{x:.3f}'
def pv(p):
    return 'p < 0.001' if p < 0.001 else f'p = {p:.3f}'
def pnum(p):
    return '<0.001' if p < 0.001 else f'{p:.3f}'
def pct(k, tot=n): return f'{k/tot*100:.1f}%'
def npct(k, tot=n): return f'{k} ({k/tot*100:.1f}%)'
def msd(s): return f'{s.mean():.2f} ± {s.std():.2f}'

order = []
def cite(*keys):
    nums = []
    for k in keys:
        assert k in REFS, k
        if k not in order: order.append(k)
        nums.append(order.index(k) + 1)
    nums = sorted(set(nums))
    # compress ranges: 1,2,3 -> 1-3
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j+1] == nums[j] + 1: j += 1
        out.append(f'{nums[i]}–{nums[j]}' if j - i >= 2 else (f'{nums[i]},{nums[j]}' if j == i + 1 else f'{nums[i]}'))
        i = j + 1
    return '[' + ','.join(out) + ']'

doc = Document()
st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(14)
st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT); st.element.rPr.rFonts.set(qn('w:cs'), FONT)
pf = st.paragraph_format; pf.line_spacing = 1.5; pf.space_after = Pt(6)
for lvl, size in [(1, 16), (2, 14), (3, 14)]:
    h = doc.styles[f'Heading {lvl}']; h.font.name = FONT; h.font.size = Pt(size); h.font.bold = True
    h.font.italic = (lvl == 3); h.font.color.rgb = RGBColor(0, 0, 0)
    rpr = h.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in list(rf.attrib):
        if a.endswith('Theme'): del rf.attrib[a]   # theme fonts would override Times New Roman
    for a in ['w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs']: rf.set(qn(a), FONT)
    h.paragraph_format.space_before = Pt(12 if lvl > 1 else 0); h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.line_spacing = 1.5; h.paragraph_format.keep_with_next = True
sec = doc.sections[0]
for s in [sec]:
    s.page_height, s.page_width = Cm(29.7), Cm(21.0)
    s.left_margin = Cm(3.0); s.right_margin = Cm(2.5); s.top_margin = Cm(2.5); s.bottom_margin = Cm(2.5)

def add_runs(p, text, size=None):
    # **bold**, *italic*
    parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)
    for part in parts:
        if not part: continue
        if part.startswith('**'): r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith('*'): r = p.add_run(part[1:-1]); r.italic = True
        else: r = p.add_run(part)
        r.font.name = FONT
        if size: r.font.size = Pt(size)
    return p
def P(text, align='justify', size=None, indent=True, space_after=6, bold=False):
    p = doc.add_paragraph()
    p.alignment = {'justify': WD_ALIGN_PARAGRAPH.JUSTIFY, 'center': WD_ALIGN_PARAGRAPH.CENTER, 'left': WD_ALIGN_PARAGRAPH.LEFT}[align]
    if indent and align == 'justify': p.paragraph_format.first_line_indent = Cm(1.0)
    p.paragraph_format.space_after = Pt(space_after)
    add_runs(p, f'**{text}**' if bold else text, size)
    return p
def bullet(text):
    p = doc.add_paragraph(style='List Bullet'); add_runs(p, text); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(3); return p
NUM = [0]
def numbered(text):
    # numbering restarts after every heading (Word's List Number style would run on across lists)
    NUM[0] += 1
    p = doc.add_paragraph(); add_runs(p, f'{NUM[0]}.\t' + text); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(0.9); p.paragraph_format.first_line_indent = Cm(-0.9)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(0.9)); p.paragraph_format.space_after = Pt(3); return p
HEADS = []
def H(text, lvl=1):
    HEADS.append((lvl, text)); NUM[0] = 0; h = doc.add_heading(text, level=lvl)
    if lvl == 1:
        pPr = h._p.get_or_add_pPr(); pb = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
        b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '8'); b.set(qn('w:space'), '4'); b.set(qn('w:color'), '1F3B4D'); pb.append(b); pPr.append(pb)
    return h
def page_break(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def add_field(run, instr, cached='1'):
    f1_ = OxmlElement('w:fldChar'); f1_.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr
    f2_ = OxmlElement('w:fldChar'); f2_.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t'); t.text = cached
    f3_ = OxmlElement('w:fldChar'); f3_.set(qn('w:fldCharType'), 'end')
    for e in (f1_, it, f2_, t, f3_): run._r.append(e)

tables_list, figures_list = [], []
def caption(kind, text):
    lst = tables_list if kind == 'Table' else figures_list
    lst.append(text); num = len(lst)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(4); p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.keep_with_next = (kind == 'Table')
    r = p.add_run(f'{kind} '); r.bold = True; r.font.size = Pt(12)
    # field split over separate runs so the cached number keeps the caption formatting
    for part in ['begin', 'instr', 'separate', 'text', 'end']:
        r = p.add_run(); r.bold = True; r.font.size = Pt(12)
        if part == 'instr':
            it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = f' SEQ {kind} \\* ARABIC '; r._r.append(it)
        elif part == 'text':
            r.text = str(num)
        else:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), part); r._r.append(e)
    r = p.add_run('. '); r.bold = True; r.font.size = Pt(12)
    r2 = p.add_run(text); r2.font.size = Pt(12); r2.italic = (kind == 'Figure')
    return num

def set_cell_border(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr(); b = tcPr.find(qn('w:tcBorders'))
    if b is None: b = OxmlElement('w:tcBorders'); tcPr.append(b)
    for edge, val in kw.items():
        el = OxmlElement(f'w:{edge}'); el.set(qn('w:val'), val); el.set(qn('w:sz'), '8'); el.set(qn('w:color'), '000000'); b.append(el)

NAVY_T, GROUP_T, ZEBRA_T, RULE_T = '1F3B4D', 'E3EBF0', 'F6F8FA', 'C9D2DA'
def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill); tcPr.append(shd)
def table(header, rows, widths=None, size=10.5, note=None, bold_rows=(), compact=False):
    t = doc.add_table(rows=1, cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = doc.styles['Table Grid']
    tblPr = t._tbl.tblPr; bd = tblPr.find(qn('w:tblBorders'))
    if bd is not None: tblPr.remove(bd)
    bd = OxmlElement('w:tblBorders')          # heavy top/bottom rules, fine horizontal lines, no vertical lines
    for edge, val, sz, col in [('top', 'single', 12, NAVY_T), ('bottom', 'single', 12, NAVY_T), ('left', 'nil', 0, 'auto'), ('right', 'nil', 0, 'auto'),
                               ('insideH', 'single', 4, RULE_T), ('insideV', 'nil', 0, 'auto')]:
        el = OxmlElement(f'w:{edge}'); el.set(qn('w:val'), val)
        if val != 'nil': el.set(qn('w:sz'), str(sz)); el.set(qn('w:color'), col); el.set(qn('w:space'), '0')
        bd.append(el)
    tblPr.append(bd)
    mar = OxmlElement('w:tblCellMar')
    for edge, v in [('top', 8 if compact else 35), ('bottom', 8 if compact else 35), ('left', 90), ('right', 90)]:
        el = OxmlElement(f'w:{edge}'); el.set(qn('w:w'), str(v)); el.set(qn('w:type'), 'dxa'); mar.append(el)
    tblPr.append(mar)
    def fill(cells, vals, bold=False, color=None):
        for c, v in zip(cells, vals):
            c.text = ''; p = c.paragraphs[0]; p.paragraph_format.line_spacing = (Pt(size + 2) if compact else 1.0); p.paragraph_format.space_after = Pt(0)
            v = '0.00' if str(v) == '-0.00' else v
            r = p.add_run(str(v)); r.font.size = Pt(size); r.bold = bold; r.font.name = FONT
            if color: r.font.color.rgb = RGBColor.from_string(color)
    fill(t.rows[0].cells, header, bold=True, color='FFFFFF')
    for c in t.rows[0].cells: shade(c, NAVY_T)
    trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); trPr.append(th)   # repeat header on new page
    k = 0
    for i, row in enumerate(rows):
        cells = t.add_row().cells; grp = i in bold_rows
        fill(cells, row, bold=grp)
        if grp: [shade(c, GROUP_T) for c in cells]; k = 0
        else:
            if k % 2 == 1: [shade(c, ZEBRA_T) for c in cells]
            k += 1
    for ri, row in enumerate(t.rows):
        tr = row._tr; trPr = tr.get_or_add_trPr(); cs = OxmlElement('w:cantSplit'); trPr.append(cs)
        if ri < len(t.rows) - 1:                       # keep the whole table on one page
            for c in row.cells:
                for cp in c.paragraphs: cp.paragraph_format.keep_with_next = True
    if widths:
        t.autofit = False
        lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
        for col, w in zip(t.columns, widths): col.width = Cm(w)
        for row in t.rows:
            for c, w in zip(row.cells, widths): c.width = Cm(w)
    if note:
        p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(12)
        r0 = p.add_run('Note. '); r0.italic = True; r0.font.size = Pt(9.5); r0.font.name = FONT
        add_runs(p, note, size=9.5)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t

def figure(path, text, width=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    run = p.add_run(); run.add_picture(path, width=Cm(width))
    spPr = run._r.xpath('.//pic:spPr')[0]                     # thin grey frame around the figure
    ln = OxmlElement('a:ln'); ln.set('w', '9525'); sf = OxmlElement('a:solidFill'); cl = OxmlElement('a:srgbClr'); cl.set('val', 'B8C2CC')
    sf.append(cl); ln.append(sf); spPr.append(ln)
    caption('Figure', text)

FIG = f'{OUT}/figures'

# ------------------------------------------------------------------ numbers used in text
dates = R['dates']
mc = R['main_corr']; sc = mc['SHAI_CSS']
part = R['partial_corr']
prev = R['prevalences']; ss = R['sample_size']
rel = X['T4_reliability'].set_index('Scale')
cfa = X['T6_cfa']
hier = X['T13_hierarchical_CSS']
ols = X['T14_OLS_CSS_full']; olsS = X['T15_OLS_SHAI_full']
lg = X['T18_logit_HA_clin']; beh = X['T19_logit_behaviours']; ordl = X['T20_ordinal_logit']
med = X['T21_mediation']; ser = X['T22_serial_mediation']; mod = X['T23_moderation']
sg = X['T26_subgroup_corr']; lang = X['T24_language']; ms = X['T25_medstudents']
G = X['T9_group_comparisons']; CH = X['T10_chi_square']; cmpc = X['T7b_compare_corr']
sens = R['sensitivity']; quant = X['T17_quantile_reg']; subq = X['T16_subscales_on_SHAI']
def gp(var, out): return G[(G.Variable == var) & (G.Outcome == out)].iloc[0]
def chi(out, var): return CH[(CH.Outcome.str.startswith(out)) & (CH.Variable == var)].iloc[0]
def bh(outcome, pred): return beh[(beh.Outcome == outcome) & (beh.Predictor == pred)].iloc[0]
def medrow(model_prefix, path): return med[med.Model.str.startswith(model_prefix) & (med.Path == path)].iloc[0]
def ci(lo, hi, k=2): return f'{lo:.{k}f}–{hi:.{k}f}'

shai, css = d.SHAI, d.CSS
_ph = X['T9b_posthoc']; ph_ms = float(_ph[(_ph.Variable == 'Study/work') & (_ph.Outcome == 'SHAI') & (_ph.A == 'Medical student') & (_ph.B == 'Non-health employee/other')].p_holm.iloc[0])
ib = R['item_by_item']
import statsmodels.formula.api as smf
_m = smf.ols("CSS ~ C(age_c, Treatment('20–29')) + female + C(occ_c, Treatment('Non-health employed/other')) + chronic + lang_en + tool_ai + tool_search + tool_medplat + tool_social + trust + mot_reassurance + mot_selfdx + mot_cost + mot_triage + SHAI", d).fit(cov_type='HC3')
ai_alt_B, ai_alt_p = _m.params['tool_ai'], _m.pvalues['tool_ai']
kw_bot = stats.kruskal(*[d.loc[d.ai_model == m, 'CSS'] for m in ['ChatGPT', 'Gemini', 'Claude']]).pvalue
_df2 = n - 20 - 1; pow20 = float(1 - stats.ncf.cdf(stats.f.ppf(0.95, 1, _df2), 1, _df2, 0.03 * n))
cnt = lambda c: int(d[c].sum())
age20 = int((d.age_group == '20-29').sum()); fem = cnt('female'); medst = cnt('medical_student')
ai_n = cnt('ai_user'); se_n = cnt('tool_search'); hb = cnt('health_background')
r_sub = {k: mc[f'SHAI_{k}'] for k in ['Excessiveness', 'Compulsion', 'Distress', 'Reassurance']}
mA_ind = medrow('A:', 'Indirect'); mA_dir = medrow('A:', 'Direct'); mA_tot = medrow('A:', 'Total')
mC_ind = medrow('C:', 'Indirect'); mC_dir = medrow('C:', 'Direct'); mC_tot = medrow('C:', 'Total')
mD_ind = medrow('D:', 'Indirect'); mB_ind = medrow('B:', 'Indirect')
pmed = R['prop_mediated']
b_shai = ols.loc['SHAI']; b_ai = ols.loc['ai_user']
lg_css = lg.loc['zCSS']; lg_mot = lg.loc['mot_reassurance']; lg_age = lg.loc['age_ord']
hiS = olsS.loc['CSS']; hiChron = olsS.loc['chronic']; hiMot = olsS.loc['mot_reassurance']

# ================================================================== TITLE PAGE (section 1: roman)
LOGO = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'assets', 'uobcom')
hdr = doc.add_table(rows=1, cols=3); hdr.alignment = WD_TABLE_ALIGNMENT.CENTER; hdr.autofit = False
_lay = OxmlElement('w:tblLayout'); _lay.set(qn('w:type'), 'fixed'); hdr._tbl.tblPr.append(_lay)
_tw = hdr._tbl.tblPr.find(qn('w:tblW'))
if _tw is None: _tw = OxmlElement('w:tblW'); hdr._tbl.tblPr.append(_tw)
_tw.set(qn('w:w'), str(int(16.0 * 567))); _tw.set(qn('w:type'), 'dxa')
for col, w in zip(hdr.columns, [3.0, 10.0, 3.0]): col.width = Cm(w)
for c, w in zip(hdr.rows[0].cells, [3.0, 10.0, 3.0]): c.width = Cm(w)
c0, c1, c2 = hdr.rows[0].cells
for c, f, wd in [(c0, 'logo_uob.png', 2.9), (c2, 'logo_med.png', 2.45)]:
    pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER; pp.add_run().add_picture(os.path.join(LOGO, f), width=Cm(wd))
    c.vertical_alignment = 1
c1.vertical_alignment = 1
for k, (txt_, sz) in enumerate([('Republic of Iraq', 11), ('Ministry of Higher Education and Scientific Research', 10.5), ('University of Baghdad', 14), ('College of Medicine', 14)]):
    pp = c1.paragraphs[0] if k == 0 else c1.add_paragraph()
    pp.alignment = WD_ALIGN_PARAGRAPH.CENTER; pp.paragraph_format.space_after = Pt(0); pp.paragraph_format.line_spacing = 1.15
    r = pp.add_run(txt_); r.bold = True; r.font.size = Pt(sz); r.font.name = FONT; r.font.color.rgb = RGBColor.from_string('1F3B4D')
rule = doc.add_paragraph(); rpPr = rule._p.get_or_add_pPr(); pb = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
b.set(qn('w:val'), 'double'); b.set(qn('w:sz'), '6'); b.set(qn('w:space'), '1'); b.set(qn('w:color'), '1F3B4D'); pb.append(b); rpPr.append(pb)
P('', indent=False)
p = P('Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad: An Online Cross-Sectional Survey',
      align='center', indent=False, size=20, bold=True)
for r in p.runs: r.font.color.rgb = RGBColor.from_string('1F3B4D')
P('', indent=False)
P('A graduation research project submitted to the College of Medicine, University of Baghdad, in partial fulfilment of the requirements for the degree of [Degree]', align='center', indent=False, size=13)
P('', indent=False)
P('**A research project presented by**', align='center', indent=False)
P('Abdulrahman Jamal Ghazi', align='center', indent=False, space_after=0)
P('Mustafa Wamedh Mustafa', align='center', indent=False, space_after=0)
P('Yaseen Omar Lutfi', align='center', indent=False)
P('', indent=False)
P('**Supervised by**', align='center', indent=False)
P('Assist. Prof. Dr. Thikra Hasan Mathkor', align='center', indent=False)
P('', indent=False)
P('[Academic year]', align='center', indent=False)
rule2 = doc.add_paragraph(); r2pPr = rule2._p.get_or_add_pPr(); pb2 = OxmlElement('w:pBdr'); b2 = OxmlElement('w:bottom')
b2.set(qn('w:val'), 'double'); b2.set(qn('w:sz'), '6'); b2.set(qn('w:space'), '1'); b2.set(qn('w:color'), '1F3B4D'); pb2.append(b2); r2pPr.append(pb2)
page_break()

# ACKNOWLEDGMENT
H('Acknowledgment')
P('[To be completed by the authors.]', indent=False)
P('We thank all the participants who gave their time to complete this survey, and [names of supervisor, department and any others to be acknowledged].')
page_break()

# TABLE OF CONTENTS (filled at the end)
H('Table of Contents'); TOC_anchor = doc.add_paragraph(); page_break()

# LIST OF ABBREVIATIONS
H('List of Abbreviations')
abbr = [('AI', 'Artificial intelligence'), ('AOR', 'Adjusted odds ratio'), ('AUC', 'Area under the receiver operating characteristic curve'),
        ('CFA', 'Confirmatory factor analysis'), ('CFI', 'Comparative fit index'), ('CI', 'Confidence interval'),
        ('CSS-12', 'Cyberchondria Severity Scale, 12-item short form'), ('DWLS', 'Diagonally weighted least squares'),
        ('ER', 'Emergency room'), ('FDR', 'False discovery rate'), ('GP', 'General practitioner'), ('HA', 'Health anxiety'),
        ('HC3', 'Heteroskedasticity-consistent standard errors, type 3'), ('IQR', 'Interquartile range'),
        ('KMO', 'Kaiser–Meyer–Olkin measure of sampling adequacy'), ('LLM', 'Large language model'), ('ML', 'Maximum likelihood'),
        ('OLS', 'Ordinary least squares'), ('OR', 'Odds ratio'), ('RMSEA', 'Root mean square error of approximation'),
        ('SD', 'Standard deviation'), ('SHAI-14', 'Short Health Anxiety Inventory, 14-item version'),
        ('STROBE', 'Strengthening the Reporting of Observational Studies in Epidemiology'), ('TLI', 'Tucker–Lewis index'),
        ('VIF', 'Variance inflation factor')]
t = doc.add_table(rows=0, cols=2)
for a, b in abbr:
    c = t.add_row().cells; c[0].text = a; c[1].text = b
    for cc in c:
        for r in cc.paragraphs[0].runs: r.font.size = Pt(13)
        cc.paragraphs[0].paragraph_format.space_after = Pt(1); cc.paragraphs[0].paragraph_format.line_spacing = 1.15
    c[0].paragraphs[0].runs[0].bold = True
for row in t.rows: row.cells[0].width = Cm(3.5); row.cells[1].width = Cm(12)
page_break()

# placeholders for lists of tables / figures (filled at the end)
H('List of Tables'); LT_anchor = doc.add_paragraph(); page_break()
H('List of Figures'); LF_anchor = doc.add_paragraph(); page_break()

# ================================================================== ABSTRACT
H('Summary / Abstract')
sd_ = lambda s: f'{s.mean():.1f} ± {s.std():.1f}'
abstract = [
 f'**Background:** Adults increasingly consult search engines and, more recently, artificial-intelligence (AI) chatbots before seeing a doctor. Health anxiety and cyberchondria (excessive, distressing online health searching) are thought to reinforce each other, but evidence from Iraq, and on AI chatbots, is scarce.',
 f'**Objectives:** To measure the association between health anxiety and cyberchondria among adults in Baghdad, and to describe online and AI health-information seeking and pre-consultation behaviour.',
 f'**Methods:** Cross-sectional online survey of {n} adults in Baghdad ({pd.Timestamp(dates[0]):%B}–{pd.Timestamp(dates[1]):%B %Y}) using the Short Health Anxiety Inventory (SHAI-14) and the Cyberchondria Severity Scale (CSS-12). Analyses included measurement-invariance testing across Arabic and English responders, FDR-corrected group comparisons, robust regression and bootstrapped mediation.',
 f'**Results:** Participants were mostly young ({pct(age20)} aged 20–29) and {pct(hb)} had a health-related background; the CSS-12 was invariant across Arabic and English responders. AI chatbots were ticked by {E["ai_profile"]["ticked_ai_pct"]:.1f}% ({pct(ai_n)} including respondents who named a chatbot), against {pct(se_n)} for search engines. Health anxiety correlated with cyberchondria (r = {sc["pearson_r"]:.2f}, 95% CI {ci(*sc["pearson_CI"])}) and remained its strongest predictor after adjustment (β = {b_shai.beta_std:.2f}), most strongly with excessive searching and post-search distress. Elevated health anxiety (SHAI-14 ≥ 18, a screening threshold rather than a diagnosis) was found in {prev["HA_clin"]:.1f}%; only {sens["prev_SHAI_ge_29"]:.1f}% reached the stricter low-prevalence cut-off of 29. After searching, {pct(cnt("beh_delay_reassured"))} delayed or skipped care because they felt reassured and {pct(cnt("share_never"))} never told their doctor, citing fear of judgement; higher cyberchondria was associated with more disclosure. The association between AI use and cyberchondria was not robust to how AI use was defined.',
 f'**Conclusion:** In this convenience sample of mostly young, health-oriented adults, health anxiety and cyberchondria were linked, and AI chatbots were a major channel for online health information, without reliable evidence that their use adds to cyberchondria beyond health anxiety. The cross-sectional design cannot establish direction. Clinicians should ask about online and AI searches without judgement.',
 '**Keywords:** cyberchondria; health anxiety; artificial intelligence; chatbots; online health information seeking; Iraq.']
for a in abstract: P(a, space_after=4)

# ================================================================== MAIN TEXT (section 2: arabic from 1)
new = doc.add_section(WD_SECTION.NEW_PAGE)

H('1. Introduction')
H('1.1 Background', 2)
P(f'Searching the Internet before seeing a doctor has become an ordinary part of being ill. A symptom is now often typed into a search engine, or described to an AI chatbot, long before it is described to a physician. This shift has clear benefits: information is immediate, free and available at any hour, and it can help people judge whether a symptom needs medical attention. It also has a well-documented downside. For a sizeable minority of people, online searching does not settle a worry but amplifies it, a phenomenon that has come to be called *cyberchondria* {cite("white2009","starcevic2013")}.')
P(f'Iraq offers a useful and under-studied setting in which to examine this. Internet access in the country has expanded rapidly, with roughly four in five Iraqis online by the start of 2025 {cite("datareportal2025")}, and in such a highly connected population the Internet and, increasingly, AI chatbots may function as a first point of contact for health concerns. How this behaviour interacts with health anxiety, and what it means for the consultation that follows, has not been examined in Baghdad.')

H('1.2 Health anxiety', 2)
P(f'Health anxiety refers to a persistent preoccupation with having, or acquiring, a serious illness, maintained by misinterpretation of normal bodily sensations. It lies on a continuum, from transient worry that most people experience to clinically significant illness anxiety disorder and somatic symptom disorder in the DSM-5 {cite("apa2013")}. The cognitive-behavioural model proposes that bodily sensations are interpreted as signs of serious disease and that the resulting anxiety is maintained by safety behaviours such as body checking and reassurance seeking: these behaviours relieve anxiety briefly but prevent the person from learning that the feared outcome does not occur, so the worry returns {cite("salk1986")}.')
P(f'Health anxiety is not rare: its lifetime prevalence is estimated at about 6% in the general population and up to 20% among hospital outpatients, and it generates substantial costs through unnecessary medical contacts {cite("tyrer2018","tyrer2020")}. A meta-analysis of university student samples found that health anxiety scores rose steadily between 1985 and 2017 {cite("kosic2020")}. In Iraq, 49.5% of 1591 respondents to an online survey during the COVID-19 restrictions screened positive for health anxiety on the Health Anxiety Questionnaire {cite("karim2020")}, and a second national online survey of 1578 Iraqi adults found that home quarantine was accompanied by greater health anxiety and increased reassurance-seeking behaviour {cite("taha2021")}, suggesting that the population is far from immune to illness worry.')

H('1.3 Cyberchondria', 2)
P(f'The term cyberchondria was popularised by White and Horvitz, whose analysis of large-scale search logs showed that searches for common, benign symptoms frequently escalated towards rare and serious diagnoses, and that this escalation was driven by the amount and wording of medical content viewed and by the user\'s own predisposition to escalate {cite("white2009")}. Starcevic and Berle later defined cyberchondria as excessive or repeated online searching for health information that is associated with increasing, rather than relieving, distress or anxiety {cite("starcevic2013")}. Crucially, searching for health information is not itself pathological; it becomes cyberchondria when it is excessive, compulsive and distressing, and when it drives further reassurance seeking {cite("starcevic2020")}. A systematic review described cyberchondria as a possible transdiagnostic, compulsive digital syndrome closely linked to health anxiety and obsessive-compulsive symptoms, while noting that the evidence base was almost entirely cross-sectional and based on online student samples {cite("vismara2020")}.')
P(f'The most widely used instrument is the Cyberchondria Severity Scale (CSS), originally a 33-item measure with five factors: compulsion, distress, excessiveness, reassurance seeking and mistrust of medical professionals {cite("mcelroy2014")}. Its 12-item short form (CSS-12) drops the mistrust dimension and retains four three-item subscales that load substantially on a general cyberchondria factor, supporting both a total and subscale scores {cite("mcelroy2019")}. An Arabic version of the CSS-12 has shown acceptable structure and validity among Lebanese adults {cite("hallit2023")}.')

H('1.4 The relationship between health anxiety and cyberchondria', 2)
P(f'Cyberchondria and health anxiety are closely related yet distinct: in a community sample, cyberchondria overlapped strongly with health anxiety but, beyond that overlap, was associated with greater functional impairment and healthcare utilisation {cite("mathes2018")}. Searching can also raise anxiety directly: in a randomised experiment, participants who searched Google or a medical app for the causes of experimentally provoked bodily symptoms reported more negative affect, more health anxiety and a stronger wish to consult a physician than controls who waited {cite("jungmann2020")}. Two meta-analyses have quantified the association: health anxiety correlates moderately with general online health information seeking (r = 0.34) but strongly with cyberchondria (r = 0.62) {cite("mcmullan2019")}, and a later meta-analysis reported a similar pooled correlation (r = 0.63), with subscale correlations ranging from 0.24 to 0.66 {cite("schenkel2021")}. The same work frames health-related Internet use in anxious individuals as a safety behaviour maintained by intermittent reinforcement {cite("schenkel2021")}. Intolerance of uncertainty is also strongly associated with cyberchondria, already in adolescence (r = 0.55), presumably because search results rarely deliver a single, certain answer {cite("jungmann2025")}.')
P(f'Whether the two conditions "fuel each other" is the central question. The only large longitudinal study, a four-wave Dutch panel of 5322 adults, found initial evidence of a reciprocal relationship in which health-anxious people search more and searching in turn raises health anxiety; however, this loop appeared among people with non-clinical health anxiety and not in the clinically anxious subsample, in whom searching seemed to maintain rather than worsen anxiety {cite("tepoel2016")}. A more recent three-wave study of pregnant women likewise identified health anxiety as a prospective risk factor for cyberchondria {cite("sostaric2023")}. The COVID-19 pandemic offered a natural test of the cycle: cyberchondria tracked rising concern and safety behaviours in Croatia {cite("jokic2020")}, and was linked with health anxiety among university students in Turkey {cite("kurcer2022")}. A recent scoping review reported cyberchondria prevalence estimates between 30.7% and 55.6% across studies and consistent associations with health anxiety {cite("miezah2026")}.')

H('1.5 From search engines to AI chatbots', 2)
P(f'Most of this evidence was gathered when "searching online" meant using a search engine. Large language model (LLM) chatbots such as ChatGPT and Gemini change the experience in important ways: they answer in fluent, personalised, conversational language; they can be questioned repeatedly; and their responses can appear more empathetic than those of physicians {cite("thiru2023","ayers2023")}. In a large US survey, about one in five respondents had used ChatGPT for health information; two-thirds of these users reported scepticism about its output and two-thirds turned to their physicians, yet about a third changed medications or requested referrals based on its answers {cite("ayo2024")}. Health anxiety has also been identified as a stable predictor of symptom-checker app use, with over half of users meeting a hypochondria classification {cite("wetzel2024")}. In a representative Czech sample of 4775 Internet users, health anxiety was associated with willingness to use generative AI for health information only indirectly, through greater trust in AI {cite("svestkova2025")}, and among young dermatology outpatients in Turkey 61% had consulted an AI chatbot (mostly ChatGPT) before their visit, without a detectable increase in anxiety {cite("digis2026")}. Whether AI chatbots relieve worry, by offering calm and contextualised answers, or amplify it, by being endlessly available for another round of reassurance, is an open empirical question.')

H('1.6 Online searching and the doctor–patient relationship', 2)
P(f'What patients do after searching matters for clinical care. Online information can improve the doctor–patient relationship when patients discuss it with their physician, but can strain it when it is withheld or used to challenge the physician {cite("wang2018","luo2022")}. Reassurance seeking may translate into additional consultations, requests for investigations or "doctor shopping", while false reassurance may lead to delayed care. Studies in the Arab region have begun to describe these patterns: cyberchondria was common among adults in Jeddah and associated with smartphone addiction {cite("elzayat2023")}, and among Saudi primary-care patients cyberchondria was linked with health anxiety {cite("pasayan2025")}. Across 13 Arabic-speaking countries of the Middle East and North Africa, about a third of 4276 migraine patients had delayed consultation or modified treatment because of online information, and higher trust in online information strongly predicted delayed consultation {cite("dahshan2026")}. No comparable study has been reported from Iraq, and none, to our knowledge, has placed AI chatbots alongside search engines in this population.')

H('1.7 Rationale', 2)
P('This study addresses three gaps. First, it provides, to our knowledge, the first estimate of the association between health anxiety and cyberchondria (using the CSS-12) in a Baghdad-based sample. Second, it examines AI chatbots as a distinct, and now dominant, source of online health information, rather than treating "the Internet" as one entity. Third, it links these psychological constructs to concrete pre-consultation behaviours, namely delaying care, self-medication, urgent visits, multiple consultations, disclosure of searches and trust in physicians, that matter directly to clinicians.')

H('1.8 Aim and objectives', 2)
P('**Aim:** To study the relationship between health anxiety and cyberchondria and their correlates among adults in Baghdad who search for health information online, with particular attention to AI chatbots and pre-consultation behaviour.', indent=False)
P('**Specific objectives:**', indent=False)
for o in ['To describe online and AI-based health-information seeking and pre-consultation behaviour among adults in Baghdad.',
          'To estimate levels of health anxiety and cyberchondria and the strength of their association, overall and by cyberchondria dimension, independently of socio-demographic and digital-use factors (H1, H2); correlates of each construct were examined as secondary analyses.',
          'To examine statistical pathways consistent with a mutually reinforcing cycle, and factors that might modify the association (H3).',
          'To examine how health anxiety and cyberchondria relate to pre-consultation behaviour, disclosure of searches to physicians and trust in physicians (H4).']:
    numbered(o)
P('**Hypotheses:** (H1) Health anxiety is positively associated with cyberchondria, most strongly with its distress and excessiveness dimensions. (H2) The association is independent of socio-demographic and digital-use factors. (H3) Excessive searching statistically mediates the link between health anxiety and post-search distress. (H4) Higher cyberchondria is associated with care-seeking behaviours (urgent visits, multiple consultations) and with a more strained doctor–patient relationship. H1 and H2 were the primary hypotheses and H3 and H4 secondary; all other analyses, including the AI-use comparisons, item-level, moderation and sensitivity analyses, were exploratory.', indent=False)
P('The conceptual framework of the study, linking these hypotheses to the proposed cycle between health anxiety and the facets of cyberchondria, is shown in Figure 1.')
figure(f'{FIG}/fig0a_framework.png', 'Conceptual framework of the study. Health anxiety is hypothesised to be associated with cyberchondria (H1) independently of covariates (H2), partly through excessive searching and post-search distress (H3), and cyberchondria with pre-consultation behaviour and the doctor–patient relationship (H4). The dashed arrow shows the short-lived relief that maintains the cycle.', width=15.5)

# ------------------------------------------------------------------ METHOD
H('2. Method')
H('2.1 Study design and setting', 2)
P(f'This was an analytical cross-sectional study reported in line with the STROBE statement for observational studies {cite("strobe2007")} and the CHERRIES checklist for web-based surveys {cite("eysenbach2004")}. Data were collected online in Baghdad, Iraq, between {pd.Timestamp(dates[0]):%d %B %Y} and {pd.Timestamp(dates[1]):%d %B %Y}.')
H('2.2 Participants and sampling', 2)
P('A non-probability (convenience and snowball) sampling approach was used. The survey link was distributed through online channels (social media and messaging groups) whose members were based in Baghdad. Inclusion criteria were: age 18 years or older, ability to read Arabic or English, and provision of informed consent. Every completed submission was retained for analysis. No duplicate response patterns were found. [Authors to state whether Google Forms limited submissions to one per account.] Because the link spread by snowball sampling, the number of people who saw the invitation is unknown, so view and participation rates could not be computed. Three responses had been annotated by the team during data collection [authors to state the reason for each annotation]; they were kept, and their exclusion was tested in a sensitivity analysis. The resulting sample was predominantly young and from health-related fields (Section 3.1).')
H('2.3 Sample size', 2)
P(f'The study was powered for its primary objective, the correlation between health anxiety and cyberchondria. Using Fisher\'s z approximation with two-sided α = 0.05 and 80% power, a minimum of {ss["n_needed_r_0_20"]} participants is required to detect a small-to-moderate correlation (r = 0.20), and {ss["n_needed_r_0_30"]} to detect r = 0.30 {cite("serdar2021")}. Meta-analytic estimates of this association are far larger (r ≈ 0.62) {cite("mcmullan2019","schenkel2021")}, so these targets are conservative. For descriptive proportions, {n} participants give a margin of error of ±{ss["moe_at_n"]:.1f}% at 95% confidence (worst case, p = 0.5), compared with ±5% for the {ss["cochran_n_for_5pct"]} participants of a Cochran-based calculation. The logistic model for elevated health anxiety had {ss["HA_clin_events"]} events for 11 predictors (≈5 events per variable), which is acknowledged as a limitation of that model.')
H('2.4 Data collection instrument', 2)
P('A bilingual (Arabic–English) self-administered questionnaire was built in Google Forms. All items were required, except the free-text description of chronic disease and the name of the AI chatbot used, which were conditional. The questionnaire had five parts:')
numbered('**Consent and socio-demographic data:** confirmation of age ≥18 and consent; age group; gender; highest education; nature of study or work; diagnosed chronic medical condition (and its type).')
numbered('**Digital health information seeking:** tools used (search engines, AI chatbots, dedicated medical platforms, social media; multiple answers); main AI chatbot; motivation for searching (multiple answers); and trust in medical information generated by online tools/AI (5-point scale).')
numbered(f'**Health anxiety:** the 14-item Short Health Anxiety Inventory (SHAI-14) {cite("salk2002")}. Each item offers four statements scored 0–3, giving a total of 0–42; higher scores indicate greater health anxiety. The SHAI has good reliability and validity in clinical and non-clinical samples, including recent validations in Spain, Sweden and Iran {cite("arnaez2019","osterman2022","poshtan2024")}, and an Arabic version has been validated in Saudi Arabia {cite("alshayea2020")}.')
numbered(f'**Cyberchondria:** the CSS-12 {cite("mcelroy2019")}, with items rated on a 5-point frequency scale (1 = never to 5 = always), giving a total of 12–60 and four subscales (3–15 each): Excessiveness (items 1–3), Compulsion (4–6), Distress (7–9) and Reassurance seeking (10–12).')
numbered('**Pre-consultation behaviour and relationship with physicians:** behavioural responses after searching (multiple answers), whether search or AI results are disclosed to the physician, the perceived effect of digital information seeking on the relationship with and trust in physicians, and the language mainly relied upon while answering.')
P(f'Each item was presented in English and Arabic. The research team produced the Arabic wording; its equivalence was examined empirically by comparing the psychometric behaviour of the scales between participants who relied mainly on Arabic and those who relied mainly on English (Section 2.6). For one SHAI item (item 2, noticing aches and pains) the four statements were displayed in a different order from the original scale ("as much as most people" before "less than most people"); all other SHAI and CSS items appeared in their original order. Items were scored according to the meaning of the chosen statement, following the original scoring key. The Arabic wording was produced by the research team rather than through formal cross-cultural adaptation {cite("cruchinho2024")}, and the published Arabic versions of the CSS-12 and SHAI {cite("hallit2023","alshaibani2023","alshayea2020")} were not used. As in the original scale, CSS item 3 refers to entering symptoms into a search engine.')
H('2.5 Variables and operational definitions', 2)
for b in [f'**Elevated health anxiety:** SHAI-14 ≥ 18, the optimal cut-off for distinguishing people with health anxiety from healthy controls in a Swedish diagnostic-accuracy study {cite("osterman2022")}. Because the same study recommends higher cut-offs in psychiatric (22) and low-prevalence (29) settings, the term "elevated" rather than "clinically relevant" is used, it is not a diagnosis, and prevalence at 15, 22 and 29 is also reported.',
          '**High cyberchondria:** CSS-12 total in the upper tertile of the sample (> 33), since the CSS-12 has no validated clinical cut-off.',
          '**AI-chatbot user:** ticked "AI chatbots" as a tool or named an AI chatbot in the follow-up question. Thirty-two respondents named a chatbot without ticking the tool option; they were classified as users (the follow-up question was optional and specifically addressed to chatbot users). Because this decision affects the results, AI use is reported both ways (ticked only, and ticked or named), and all analyses involving AI use were repeated with the stricter definition.',
          '**Health-related background:** medical students, students in other health fields and healthcare workers.',
          '**Occupation:** free-text "Other" answers were recoded into the closest category (e.g. secondary-school students and school leavers as non-health students; housewives, engineers and business owners as non-health employed/other). Age groups 40–49, 50–59 and 60+ were merged (≥40) for inferential analysis because of small cell sizes.']:
    bullet(b)
H('2.6 Statistical analysis', 2)
P('Analyses were carried out in Python 3 (pandas, SciPy, statsmodels, pingouin, factor_analyzer and semopy). The analysis code is fully scripted and reproducible. All tests were two-sided with α = 0.05.')
for b in [
 f'**Descriptive statistics:** frequencies and percentages for categorical variables; mean ± SD and median (IQR) for scores. Normality was assessed with the Shapiro–Wilk test, skewness and kurtosis.',
 f'**Psychometrics:** internal consistency by Cronbach\'s α (with 95% CI) and McDonald\'s ω {cite("hayescoutts2020")}; corrected item–rest correlations; sampling adequacy (KMO, Bartlett\'s test); and confirmatory factor analysis by maximum likelihood (ML), with fit judged by CFI, TLI, RMSEA and SRMR against conventional criteria (CFI/TLI ≥ 0.95, RMSEA ≤ 0.06–0.08, SRMR ≤ 0.08), recognising that fixed cut-offs do not transfer exactly to every model {cite("mcneish2023")}. Diagonally weighted least squares (DWLS) estimates on Pearson covariances are reported for comparison only, because their fit indices are not comparable with these cut-offs. Equivalence of the Arabic and English responders was tested by comparing α values with Feldt\'s test, and adjusted mean differences. Formal measurement invariance was then tested by multi-group CFA (ML with a mean structure), fitting configural, metric (equal loadings) and scalar (equal loadings and intercepts) models in sequence; each step was judged by the χ² difference test and by a change in CFI of no more than −0.01 and in RMSEA of no more than 0.015 {cite("leitgob2023")}. Differential item functioning (DIF) was examined for every item by ordinal logistic regression of the item on the scale total, language and their interaction, a regression-based approach that performs well for ordinal items {cite("cosic2026")}, with FDR correction across the 26 items.',
 f'**Correlation analysis:** Pearson and Spearman correlations (bootstrapped 95% CIs) and partial correlations adjusted for covariates. Differences between dependent correlations (health anxiety with each CSS subscale) were tested with Williams\' T2 test for dependent correlations, as recommended by Steiger {cite("steiger1980")}. Item-level correlations were computed for every SHAI item with the CSS total and every CSS item with the SHAI total.',
 f'**Group comparisons for every variable:** Mann–Whitney U (rank-biserial r as effect size) or Kruskal–Wallis H (ε² as effect size) for SHAI, CSS and each CSS subscale, with Welch\'s t-test/ANOVA as parametric confirmation and pairwise Mann–Whitney post-hoc comparisons with Holm adjustment. Associations of all categorical variables with elevated health anxiety and high cyberchondria were tested with Pearson χ² or Fisher\'s exact test (Monte-Carlo exact p when expected counts were small), with Cramér\'s V. Pairwise associations among all categorical variables were also screened.',
 f'**Multiple testing:** because many associations were tested, p-values within each family of tests were adjusted with the Benjamini–Hochberg false discovery rate procedure (q-values) {cite("bh1995")}. The families were: the 162 group comparisons; the chi-square tests; the pairwise associations among categorical variables; the 40 coefficients of the behaviour models; the moderation terms; and the 168 item-level correlations. Unadjusted p-values are reported, and associations that do not survive correction are labelled as exploratory.',
 f'**Multivariable models:** hierarchical OLS regression of CSS on socio-demographics (block 1), digital-use variables (block 2) and SHAI (block 3), with HC3 robust standard errors, standardised coefficients and VIF checks; the reverse model (SHAI on CSS); models for each CSS subscale; quantile regression (25th–90th percentiles) and a quadratic term to examine non-linearity. Logistic regression identified predictors of elevated health anxiety (AORs; apparent AUC and AUC corrected for optimism by 500 bootstrap refits) and of each pre-consultation behaviour; ordinal logistic regression was used for the ordered disclosure and relationship outcomes.',
 f'**Mediation and moderation:** as an exploratory decomposition of the association into CSS facets, mediation models with bootstrap confidence intervals (5000 resamples) estimated how much of the link between health anxiety and post-search distress ran through excessive searching, and related pathways, including a reverse-direction model and a serial model {cite("hayes2022")}. Moderation of the SHAI–CSS association by trust, AI use, health background, gender, chronic disease, language and age was tested with interaction terms and simple slopes.',
 '**Sensitivity analyses:** exclusion of annotated responses; exclusion of straight-line responders (identical answers to all items of a scale); alternative SHAI cut-offs; bootstrap of the main regression coefficient; and comparison of early versus late responders as a proxy for non-response bias.']:
    bullet(b)
P('The flow of the study, from questionnaire development to the stages of analysis, is summarised in Figure 2.')
figure(f'{FIG}/fig0b_flowchart.png', 'Study flowchart: questionnaire development, data collection, data preparation and stages of statistical analysis.', width=15.5)
H('2.7 Ethical considerations', 2)
P('Participation was voluntary and anonymous. The first page of the form explained the purpose of the study, and electronic informed consent (with confirmation of age ≥18) was required before any question was shown; participants could withdraw at any time by closing the form. No names or contact details were collected, and data were stored securely and used only for research purposes. [Ethical approval: committee name, approval number and date to be inserted.]')

# ------------------------------------------------------------------ RESULTS
H('3. Results')
H('3.1 Characteristics of participants', 2)
occ = d.occupation.value_counts()
P(f'A total of {n} adults completed the questionnaire; all gave consent and no item had missing data. The sample was young, with {npct(age20)} aged 20–29 and {npct(int((d.age_group=="18-19").sum()))} aged 18–19; {npct(fem)} were female. Most were currently students ({npct(int((d.education=="Currently a student").sum()))}); medical students were the largest occupational group ({npct(medst)}), and {npct(hb)} had a health-related background. A diagnosed chronic condition was reported by {npct(cnt("chronic"))}, most commonly migraine, hypertension, asthma, anaemia, psoriasis and diabetes. Most participants relied mainly on Arabic when answering ({npct(int((d.language=="Arabic").sum()))}) (Table 1).')
T1 = X['T1_demographics']
rows = []
for var in T1.Variable.unique():
    rows.append([var, '', ''])
    for _, r in T1[T1.Variable == var].iterrows():
        cat = {'1': 'Yes', '0': 'No'}.get(str(r.Category), str(r.Category))
        rows.append(['    ' + cat, int(r.n), f'{r["%"]:.1f}'])
caption('Table', f'Socio-demographic characteristics of the participants (n = {n})')
table(['Characteristic', 'n', '%'], rows, widths=[10.5, 2, 2], bold_rows=[i for i, r in enumerate(rows) if r[1] == ''])

H('3.2 Patterns of online health information seeking', 2)
P(f'AI chatbots were the most frequently used tool for looking up symptoms: {npct(cnt("tool_ai"))} ticked them, or {npct(ai_n)} when the 32 respondents who named a chatbot without ticking the option are included, ahead of search engines ({npct(se_n)}). Notably, {npct(int((d.tool_profile=="AI without search engine").sum()))} used AI chatbots without any search engine, and ChatGPT was the dominant chatbot ({npct(int((d.ai_model=="ChatGPT").sum()))}). AI use fell with age, from {d.loc[d.age4=="18-19","ai_user"].mean()*100:.0f}% at 18–19 years to {d.loc[d.age4=="≥40","ai_user"].mean()*100:.0f}% at 40 years or older, so the 34 non-users were an older group. The leading motives were convenience ({pct(cnt("mot_convenience"))}), deciding whether a doctor visit was needed ({pct(cnt("mot_triage"))}) and instant reassurance ({pct(cnt("mot_reassurance"))}), and trust in online/AI medical information was mostly moderate (Table 2, Figure 3).')
T2 = X['T2_digital_behaviour']
rows = []
for var in T2.Variable.unique():
    rows.append([var, '', '']);
    for _, r in T2[T2.Variable == var].iterrows():
        cat = str(r.Category)
        if var.startswith('Trust'): cat = {'1': '1 – Do not trust at all', '2': '2 – Slightly', '3': '3 – Moderately', '4': '4 – Very much', '5': '5 – Completely'}[cat]
        rows.append(['    ' + cat, int(r.n), f'{r["%"]:.1f}'])
caption('Table', 'Online health information seeking, pre-consultation behaviour and relationship with physicians (n = 300)')
table(['Variable', 'n', '%'], rows, widths=[10.5, 2, 2], bold_rows=[i for i, r in enumerate(rows) if r[1] == ''],
      note='Tools, motivations and behaviours allowed multiple answers, so percentages do not sum to 100. AI users include 32 respondents who named a chatbot without ticking the AI option.')
figure(f'{FIG}/fig2_tools_motives.png', 'Tools used and motivations for searching for health information online (n = 300).')

H('3.3 Pre-consultation behaviour and the doctor–patient relationship', 2)
P(f'After searching, the most frequent response was to delay or skip care because the information was reassuring ({pct(cnt("beh_delay_reassured"))}), followed by ignoring the symptom ({pct(cnt("beh_ignore"))}); others escalated, consulting several doctors ({pct(cnt("beh_multidoc"))}) or seeking urgent care ({pct(cnt("beh_urgent"))}). Only {pct(int((d.share=="Always").sum()))} always told their physician about their searches, whereas {pct(cnt("share_never"))} never did so, citing fear of being judged, and {pct(int((d.relationship!="No negative impact").sum()))} said searching had complicated their relationship with, or reduced their trust in, their doctor (Figure 4).')
figure(f'{FIG}/fig3_behaviours.png', 'Behavioural responses after searching, disclosure of searches to physicians and perceived effect on the doctor–patient relationship (n = 300).', width=16)

H('3.4 Levels of health anxiety and cyberchondria, and psychometric properties', 2)
T3 = X['T3_scale_desc']
P(f'The mean SHAI-14 score was {msd(shai)} and {npct(cnt("HA_clin"))} (95% CI {ci(*prev["HA_clin_CI"], k=1)}%) scored at or above 18, indicating elevated health anxiety; the estimate depended strongly on the threshold, from {sens["prev_SHAI_ge_15"]:.1f}% at 15 to {sens["prev_SHAI_ge_29"]:.1f}% at 29 (Table 4). The mean CSS-12 score was {msd(css)}: participants searched a great deal (excessiveness was the highest-scoring dimension, {msd(d.CSS_excess)}) but searching rarely disrupted daily life (compulsion was the lowest, {msd(d.CSS_compul)}). Because scores deviated modestly from normality (Shapiro–Wilk p < 0.01), non-parametric bivariate tests and robust regression standard errors were used.')
P(f'Both scales were reliable (SHAI-14 α = {rel.loc["SHAI-14","alpha"]:.2f}, ω = {rel.loc["SHAI-14","omega"]:.2f}; CSS-12 α = {rel.loc["CSS-12","alpha"]:.2f}, ω = {rel.loc["CSS-12","omega"]:.2f}; Table 3). Under ML, the four-factor structure of the CSS-12 fitted acceptably (CFI = {cfa.iloc[3].CFI:.3f}, RMSEA = {cfa.iloc[3].RMSEA:.3f}, SRMR = {E["srmr"]["css4"]:.3f}) and clearly better than a single factor, whereas the one-factor SHAI-14 model fitted poorly (CFI = {cfa.iloc[5].CFI:.3f}), so the SHAI-14 should not be regarded as strictly unidimensional, consistent with the two-factor solutions reported in recent validations {cite("arnaez2019","poshtan2024")}.')
_mod_lang = X["T23_moderation"].set_index("Moderator").loc["English-language responder"]
_nomS = ", ".join(DIF[(DIF.Scale == "SHAI-14") & (DIF.p_uniform < 0.05)].Item.str.replace("SHAI", ""))
P(f'Measurement invariance across Arabic and English responders is summarised in Table 5. The CSS-12 reached full scalar invariance, so its scores can be compared directly across the two languages; the SHAI-14 reached metric but not scalar invariance (scalar ΔCFI = {dcfi(IS,"scalar"):.3f}). Both tests start from imperfect baselines (configural CFI = {inv(IC,"configural","CFI"):.3f} for the CSS-12 and {inv(IS,"configural","CFI"):.3f} for the SHAI-14), so the SHAI-14 results in particular are hard to interpret and should be read cautiously. No item showed differential item functioning after FDR correction (smallest q = {DIF.q_any.min():.2f}), and language did not modify the association between health anxiety and cyberchondria (interaction {pv(_mod_lang.p)}).')
rows = []
for lab, col, rk in [('SHAI-14 total (0–42)', 'SHAI', 'SHAI-14'), ('CSS-12 total (12–60)', 'CSS', 'CSS-12'), ('  Excessiveness (3–15)', 'CSS_excess', 'CSS Excessiveness'),
                     ('  Compulsion (3–15)', 'CSS_compul', 'CSS Compulsion'), ('  Distress (3–15)', 'CSS_distress', 'CSS Distress'), ('  Reassurance (3–15)', 'CSS_reassur', 'CSS Reassurance')]:
    s = d[col]; rr = rel.loc[rk]
    rows.append([lab, f'{s.mean():.2f} ± {s.std():.2f}', f'{s.median():.0f} ({s.quantile(.25):.0f}–{s.quantile(.75):.0f})', f'{s.min():.0f}–{s.max():.0f}', f'{rr.alpha:.2f} ({rr.alpha_CI})', f'{rr.omega:.2f}'])
lr = lang.set_index('Scale')
caption('Table', 'Descriptive statistics, reliability and language equivalence of the SHAI-14 and CSS-12 (n = 300)')
table(['Scale', 'Mean ± SD', 'Median (IQR)', 'Range', 'α (95% CI)', 'ω'], rows, widths=[4.6, 2.6, 2.6, 1.6, 2.7, 1.1],
      note=f'Language equivalence (SHAI-14 means are not strictly comparable across languages because its scalar invariance was not supported; Table 5): SHAI mean {lr.loc["SHAI","Arabic"]} (Arabic) vs {lr.loc["SHAI","English"]} (English), adjusted p = {lr.loc["SHAI","adj_p"]:.2f}; CSS mean {lr.loc["CSS","Arabic"]} vs {lr.loc["CSS","English"]}, adjusted p = {lr.loc["CSS","adj_p"]:.2f}. CFA fit, ML (primary): CSS-12 four factors CFI {cfa.iloc[3].CFI:.3f}, TLI {cfa.iloc[3].TLI:.3f}, RMSEA {cfa.iloc[3].RMSEA:.3f}, SRMR {E["srmr"]["css4"]:.3f}; SHAI-14 one factor CFI {cfa.iloc[5].CFI:.3f}, RMSEA {cfa.iloc[5].RMSEA:.3f}, SRMR {E["srmr"]["shai1"]:.3f}. DWLS on Pearson covariances (comparison only, not comparable with ML cut-offs): CSS-12 CFI {cfa.iloc[2].CFI:.3f}, RMSEA {cfa.iloc[2].RMSEA:.3f}; SHAI-14 CFI {cfa.iloc[4].CFI:.3f}, RMSEA {cfa.iloc[4].RMSEA:.3f}. Measurement invariance across languages: Table 5.')
from statsmodels.stats.proportion import proportion_confint as _pci
rows = []
for cut, basis in [(15, 'Lower threshold (sensitivity)'), (18, 'Optimal versus healthy controls (primary definition)'), (22, 'Optimal in a psychiatric setting'), (29, 'Optimal in a low-prevalence setting')]:
    k = int((d.SHAI >= cut).sum()); lo, hi = _pci(k, n, method='wilson')
    rows.append([f'≥ {cut}', basis, k, f'{k / n * 100:.1f}', f'{lo * 100:.1f}–{hi * 100:.1f}'])
caption('Table', 'Prevalence of elevated health anxiety at different SHAI-14 cut-offs (n = 300)')
table(['SHAI-14 score', 'Basis of the cut-off', 'n', '%', '95% CI'], rows, widths=[2.6, 7.4, 1.4, 1.6, 2.6], bold_rows=[1],
      note=f'Cut-offs of 18, 22 and 29 from the Swedish diagnostic-accuracy study of the SHAI-14 {cite("osterman2022")}; ≥ 18 is used throughout this thesis. 95% CI: Wilson score interval. An elevated score is a screening result, not a diagnosis.')
rows = []
_z = lambda v: 0.0 if abs(v) < 5e-4 else v
for sc_lab, sc_key in [('CSS-12 (four factors)', IC), ('SHAI-14 (one factor)', IS)]:
    rows.append([sc_lab, '', '', '', '', '', '', ''])
    for m, mlab in [('configural', 'Configural'), ('metric', 'Metric (equal loadings)'), ('scalar', 'Scalar (+ intercepts)')]:
        r = INV.loc[(sc_key, m)]
        if m == 'configural':
            dd = ['—', '—', '—']; dec = 'Baseline'
        else:
            dd = [f'{r.d_chi2:.2f} ({r.d_df:.0f})', pnum(r.p_diff), f'{_z(dcfi(sc_key, m)):+.3f}']
            dec = 'Supported' if (r.d_CFI >= -0.01 and r.p_diff >= 0.05) else ('Supported (ΔCFI)' if r.d_CFI >= -0.01 else 'Not supported')
        rows.append(['    ' + mlab, f'{r.chi2:.1f} ({r.df:.0f})', f'{r.CFI:.3f}', f'{r.RMSEA:.3f}', *dd, dec])
caption('Table', 'Measurement invariance of the CSS-12 and SHAI-14 across Arabic and English responders (multi-group CFA)')
table(['Model', 'χ² (df)', 'CFI', 'RMSEA', 'Δχ² (Δdf)', 'p', 'ΔCFI', 'Decision'], rows, widths=[4.3, 2.0, 1.2, 1.7, 2.0, 1.2, 1.4, 2.0], size=9,
      bold_rows=[0, 4], note=f'Maximum likelihood with a mean structure; Arabic n = {int((d.language=="Arabic").sum())}, English n = {int((d.language=="English").sum())}. A step is supported when CFI does not fall by more than 0.01 and Δχ² is non-significant {cite("leitgob2023")}. Item-level DIF (ordinal logistic regression): no item significant after FDR correction (smallest q = {DIF.q_any.min():.2f}).')

H('3.5 Association between health anxiety and cyberchondria', 2)
P(f'Health anxiety was positively and moderately correlated with cyberchondria (Pearson r = {sc["pearson_r"]:.2f}, 95% CI {ci(*sc["pearson_CI"])}; Spearman ρ = {sc["spearman"]:.2f}, bootstrap 95% CI {ci(*sc["spearman_boot_CI"])}; {pv(sc["pearson_p"])}), with health anxiety accounting for {sc["r2"]*100:.0f}% of the variance in cyberchondria (Figure 5). The association was essentially unchanged after adjustment for age, gender, health background, chronic disease, trust in online information and AI use (partial r = {part["r"]:.2f}, 95% CI {ci(*part["CI"])}). Health anxiety was correlated with all four cyberchondria dimensions, but not equally: correlations with excessiveness (r = {r_sub["Excessiveness"]["pearson"]:.2f}) and distress (r = {r_sub["Distress"]["pearson"]:.2f}) were similar to each other and significantly stronger than those with compulsion (r = {r_sub["Compulsion"]["pearson"]:.2f}) and reassurance seeking (r = {r_sub["Reassurance"]["pearson"]:.2f}) (Williams\' T2, all p < 0.001) (Table 6, Figure 6).')
P(f'At item level, fear of serious illness and the interpretation of bodily sensations were most closely linked to cyberchondria, whereas simple awareness of bodily sensations and of aches and pains was not (q > 0.10); {ib["sig_fdr"]} of the 168 SHAI × CSS item pairs remained significant after FDR correction, the strongest being fear of serious illness with panic on reading about a rare or serious condition (ρ = {ib["top"][0][2]:.2f}; Appendix A, Figure 11). Trust in online/AI information was associated only with excessiveness (ρ = {X["T7_corr_matrix_rho"].loc["Trust in online/AI","Excessiveness"]:.2f}; Figure 6).')
rows = []
for k, col in [('CSS-12 total', None), ('Excessiveness', 'Excessiveness'), ('Compulsion', 'Compulsion'), ('Distress', 'Distress'), ('Reassurance', 'Reassurance')]:
    if col is None:
        rows.append([k, f'{sc["pearson_r"]:.2f} ({ci(*sc["pearson_CI"])})', f'{sc["spearman"]:.2f}', pnum(sc["pearson_p"]), f'{b_shai.beta_std:.2f}'])
    else:
        rr = r_sub[col]; sq = subq.set_index('Outcome').loc[col]
        rows.append([k, f'{rr["pearson"]:.2f} ({ci(*rr["pearson_CI"])})', f'{rr["spearman"]:.2f}', pnum(rr["p"]), f'{sq.beta:.2f}'])
caption('Table', 'Correlation between health anxiety (SHAI-14) and cyberchondria (CSS-12) and its dimensions (n = 300)')
table(['Cyberchondria measure', 'Pearson r (95% CI)', 'Spearman ρ', 'p', 'Adjusted β'], rows, widths=[4.5, 4, 2.4, 2, 2.4],
      note='Adjusted β: standardised coefficient of SHAI from robust OLS models adjusted for age, gender, occupation, chronic disease, language, tools, trust and motives. Excessiveness and Distress correlations were each significantly stronger than Compulsion and Reassurance (Williams\' T2, p < 0.001); they did not differ from each other (p = ' + f'{cmpc.iloc[1].p:.2f}).')
figure(f'{FIG}/fig1_scatter_shai_css.png', 'Scatter plot of health anxiety (SHAI-14) against cyberchondria (CSS-12) with the least-squares line and 95% confidence band (n = 300; points slightly jittered).', width=13)
figure(f'{FIG}/fig4_corr_heatmap.png', 'Spearman correlation matrix of health anxiety, cyberchondria and its dimensions, trust in online/AI information, number of tools, number of motives and age group (FDR-adjusted significance).', width=14)

H('3.6 Factors associated with health anxiety and cyberchondria (bivariate analysis)', 2)
gA = gp('Age group', 'SHAI'); gE = gp('Education', 'SHAI'); gO = gp('Study/work', 'SHAI'); gC = gp('Chronic condition', 'SHAI')
gAIc = gp('Uses AI chatbots', 'CSS'); gAIs = gp('Uses AI chatbots', 'SHAI'); gSMs = gp('Uses social media', 'SHAI'); gSMc = gp('Uses social media', 'CSS')
gTPc = gp('Tool profile', 'CSS'); gMR = gp('Motive: reassurance', 'SHAI'); gGs = gp('Gender', 'SHAI'); gGc = gp('Gender', 'CSS')
P(f'Every variable was tested against SHAI, CSS and each CSS dimension (162 tests; Table 7). Health anxiety was higher in participants with a chronic condition ({pv(gC.p)}, q = {gC.q_FDR:.3f}) and, most clearly, in those searching for instant reassurance ({msd(d.loc[d.mot_reassurance==1,"SHAI"])} vs {msd(d.loc[d.mot_reassurance==0,"SHAI"])}; q = {gMR.q_FDR:.3f}). Differences by age, education and occupation were smaller and borderline after correction (age q = {gA.q_FDR:.3f}) and are treated as exploratory. Gender was unrelated to either score.')
P(f'Under the inclusive definition, cyberchondria was higher among AI-chatbot users than non-users ({msd(d.loc[d.ai_user==1,"CSS"])} vs {msd(d.loc[d.ai_user==0,"CSS"])}; q = {gAIc.q_FDR:.3f}), mainly in excessiveness and reassurance seeking, and was highest in those who combined AI with search engines (Figure 7); the specific chatbot made no difference ({pv(kw_bot)}).')
# Table 7: selected comparisons
sel = [('Age group', 'age4', ['18-19', '20-29', '30-39', '≥40']), ('Gender', 'gender', ['Female', 'Male']),
       ('Study/work', 'occupation', ['Medical student', 'Other health-science student', 'Healthcare worker', 'Non-health student', 'Non-health employee/other']),
       ('Chronic condition', 'chronic', [1, 0]), ('Uses AI chatbots', 'ai_user', [1, 0]), ('Uses search engines', 'tool_search', [1, 0]),
       ('Uses social media', 'tool_social', [1, 0]), ('Tool profile', 'tool_profile', ['AI + search engine', 'AI without search engine', 'No AI (search/other only)']),
       ('Motive: reassurance', 'mot_reassurance', [1, 0]), ('Motive: self-diagnosis', 'mot_selfdx', [1, 0]),
       ('Trust in online/AI (1-5)', 'trust', [1, 2, 3, 4, 5]), ('Language', 'language', ['Arabic', 'English'])]
rows = []; bolds = []
for lab, col, levels in sel:
    g1 = gp(lab, 'SHAI'); g2 = gp(lab, 'CSS')
    bolds.append(len(rows))
    rows.append([lab.replace(' (1-5)', ''), '', '', f'{pnum(g1.p)} ({g1.q_FDR:.3f})', '', f'{pnum(g2.p)} ({g2.q_FDR:.3f})'])
    for lv in levels:
        s = d[d[col] == lv]
        name = {1: 'Yes', 0: 'No'}.get(lv, lv) if col not in ('trust',) else str(lv)
        rows.append(['    ' + str(name), len(s), f'{s.SHAI.mean():.1f} ± {s.SHAI.std():.1f}', '', f'{s.CSS.mean():.1f} ± {s.CSS.std():.1f}', ''])
caption('Table', 'Health anxiety (SHAI-14) and cyberchondria (CSS-12) scores by participant characteristics (n = 300)')
table(['Variable', 'n', 'SHAI mean ± SD', 'p (q)', 'CSS mean ± SD', 'p (q)'], rows, widths=[5.2, 1.2, 2.8, 2.4, 2.8, 2.4], size=10, bold_rows=bolds,
      note='SHAI-14 comparisons by language should be read cautiously because SHAI-14 scalar invariance was not supported (Table 5). p: Mann–Whitney U (two groups) or Kruskal–Wallis H (three or more groups); q: Benjamini–Hochberg false-discovery-rate adjusted p across all 162 group comparisons. Effect sizes, medians (IQR), Welch tests and post-hoc comparisons are provided in the supplementary workbook.')
figure(f'{FIG}/fig6_css_by_tool.png', 'Cyberchondria (CSS-12) by online tool profile.', width=12)

P(f'In categorical analysis (Table 8), elevated health anxiety was more common among social-media users and among those seeking instant reassurance, and participants with elevated health anxiety had higher odds of high cyberchondria (52.6% vs 23.0%; OR = {R["HA_CSShigh_OR"]["OR"]:.2f}, 95% CI {ci(*R["HA_CSShigh_OR"]["CI"])}). High cyberchondria was most frequent among participants who always disclosed their searches to their physician (q = {chi("High","Disclose to physician").q_FDR:.3f}).')
rows = []
for out_lab, out in [('Elevated health anxiety (SHAI ≥ 18)', 'Clinically'), ('High cyberchondria (CSS > 33)', 'High')]:
    sub = CH[CH.Outcome.str.startswith(out) & (CH.p < 0.05)].sort_values('p')
    rows.append([out_lab, '', '', '', ''])
    for _, r in sub.iterrows():
        dist = r.Distribution.replace('Clinically relevant HA', '').replace('(fear of judgement)', '')
        dist = re.sub(r'\b0:', 'No:', dist); dist = re.sub(r'\b1:', 'Yes:', dist)
        rows.append(['    ' + r.Variable.replace('Clinically relevant HA', 'Elevated health anxiety'), dist, f'{r.CramersV:.2f}', pnum(r.p), f'{r.q_FDR:.3f}'])
caption('Table', 'Variables significantly associated (p < 0.05) with elevated health anxiety and with high cyberchondria')
table(['Variable', 'n/N (%) with outcome, by group', 'Cramér\'s V', 'p', 'q (FDR)'], rows, widths=[4.6, 7.4, 1.6, 1.4, 1.6], size=9.5,
      bold_rows=[i for i, r in enumerate(rows) if r[1] == ''], note='Pearson χ² or Fisher\'s exact test (Monte-Carlo exact p where expected counts were < 5). Associations with q ≥ 0.05 are exploratory. Non-significant associations are listed in the supplementary workbook.')

H('3.7 Independent predictors (multivariable analysis)', 2)
P(f'In the hierarchical regression (Table 9), socio-demographic variables explained little of the variance in cyberchondria (R² = {hier.R2.iloc[0]:.3f}); digital-use variables raised R² to {hier.R2.iloc[1]:.3f}, and health anxiety added a further {hier.dR2.iloc[2]*100:.1f}% (R² = {hier.R2.iloc[2]:.3f}; f² = {E["f2"]["block3"]:.2f}, a medium effect). Health anxiety was by far the strongest predictor (B = {b_shai.B:.2f}, 95% CI {ci(b_shai.CI_low, b_shai.CI_high)}, β = {b_shai.beta_std:.2f}, {pv(b_shai.p)}). AI-chatbot use was associated with a {b_ai.B:.1f}-point higher CSS score under the inclusive definition ({pv(b_ai.p)}), but not when only respondents who ticked "AI chatbots" were counted as users (B = {ai_alt_B:.2f}, {pv(ai_alt_p)}); the 32 reclassified respondents had the highest cyberchondria of any group (mean {d.loc[d.ai_model_inconsistent==1,"CSS"].mean():.1f}), so there is no reliable evidence that AI use is associated with cyberchondria independently of health anxiety. No other variable was robustly associated, and the model diagnostics supported the stability of the health-anxiety effect (Table 13).')
P(f'In the reverse model, cyberchondria was the strongest predictor of health anxiety (β = {hiS.beta_std:.2f}, {pv(hiS.p)}), together with chronic disease (B = {hiChron.B:.2f}, {pv(hiChron.p)}) and searching for instant reassurance ({pv(hiMot.p)}); after adjustment, medical students no longer differed from other groups.')
rows = []
lab = {'Intercept': 'Constant', "C(age_c, Treatment('20–29'))[T.18–19]": 'Age 18–19 (ref. 20–29)', "C(age_c, Treatment('20–29'))[T.30–39]": 'Age 30–39', "C(age_c, Treatment('20–29'))[T.≥40]": 'Age ≥40',
       "C(occ_c, Treatment('Non-health employed/other'))[T.Healthcare worker]": 'Healthcare worker (ref. non-health employed)', "C(occ_c, Treatment('Non-health employed/other'))[T.Medical student]": 'Medical student',
       "C(occ_c, Treatment('Non-health employed/other'))[T.Non-health student]": 'Non-health student', "C(occ_c, Treatment('Non-health employed/other'))[T.Other health student]": 'Other health-science student',
       'female': 'Female', 'chronic': 'Chronic condition', 'lang_en': 'Answered mainly in English', 'ai_user': 'Uses AI chatbots', 'tool_search': 'Uses search engines',
       'tool_medplat': 'Uses medical platforms', 'tool_social': 'Uses social media', 'trust': 'Trust in online/AI (per point)', 'mot_reassurance': 'Motive: instant reassurance',
       'mot_selfdx': 'Motive: self-diagnosis', 'mot_cost': 'Motive: cost/logistics', 'mot_triage': 'Motive: need for a doctor?', 'SHAI': 'Health anxiety (SHAI, per point)'}
for idx, r in ols.iterrows():
    rows.append([lab[idx], f'{r.B:.2f}', ci(r.CI_low, r.CI_high), '' if np.isnan(r.beta_std) else f'{r.beta_std:.2f}', pnum(r.p)])
caption('Table', 'Hierarchical robust linear regression of cyberchondria (CSS-12 total) – final model (n = 300)')
table(['Predictor', 'B', '95% CI', 'β', 'p'], rows, widths=[7.6, 1.6, 3.2, 1.4, 1.6], size=10,
      bold_rows=[i for i, r in enumerate(rows) if r[4] != '' and r[4] != 'nan' and (r[4] == '<0.001' or float(r[4]) < 0.05) and r[0] != 'Constant'],
      note=f'Block 1 (socio-demographics) R² = {hier.R2.iloc[0]:.3f}; Block 2 (+ digital use) R² = {hier.R2.iloc[1]:.3f}, ΔR² = {hier.dR2.iloc[1]:.3f}, p = {hier.p_change.iloc[1]:.4f}; Block 3 (+ SHAI) R² = {hier.R2.iloc[2]:.3f}, ΔR² = {hier.dR2.iloc[2]:.3f}, p < 0.001; adjusted R² = {hier.adjR2.iloc[2]:.3f}; F = {R["ols_css"]["F"]:.2f}, p < 0.001. HC3 robust standard errors. β: standardised coefficient.')

P(f'In logistic regression (Table 10, Figure 8), elevated health anxiety was independently associated with higher cyberchondria (AOR = {lg_css.AOR:.2f} per SD, 95% CI {ci(lg_css.CI_low, lg_css.CI_high)}), with searching for instant reassurance (AOR = {lg_mot.AOR:.2f}, 95% CI {ci(lg_mot.CI_low, lg_mot.CI_high)}) and with younger age (AOR = {lg_age.AOR:.2f} per age-group step). Discrimination was good (AUC {E["auc"]["apparent"]:.2f}; {E["auc"]["corrected"]:.2f} after bootstrap correction for optimism), but with about five events per predictor the odds ratios are likely to be optimistic and are treated as exploratory.')
rows = []
lab2 = {'age_ord': 'Age group (per step)', 'female': 'Female', 'health_background': 'Health-related background', 'chronic': 'Chronic condition', 'lang_en': 'Answered mainly in English',
        'ai_user': 'Uses AI chatbots', 'tool_search': 'Uses search engines', 'trust': 'Trust in online/AI (per point)', 'mot_reassurance': 'Motive: instant reassurance',
        'mot_selfdx': 'Motive: self-diagnosis', 'zCSS': 'Cyberchondria (per 1 SD)'}
for idx, r in lg.drop(index='Intercept').iterrows():
    rows.append([lab2[idx], f'{r.AOR:.2f}', ci(r.CI_low, r.CI_high), pnum(r.p)])
caption('Table', 'Multivariable logistic regression of elevated health anxiety (SHAI ≥ 18; 57 events, n = 300)')
table(['Predictor', 'AOR', '95% CI', 'p'], rows, widths=[8, 2, 3.5, 2], bold_rows=[i for i, r in enumerate(rows) if r[3] == '<0.001' or float(r[3]) < 0.05],
      note=f'AUC = {E["auc"]["apparent"]:.2f} (apparent; optimism-corrected {E["auc"]["corrected"]:.2f}); McFadden pseudo-R² = {R["logit_HA"]["pseudoR2"]:.2f}; likelihood-ratio p < 0.001; robust (HC1) standard errors.')
figure(f'{FIG}/fig7_forest_HA.png', 'Adjusted odds ratios for elevated health anxiety (SHAI ≥ 18). Orange: p < 0.05.', width=14)

H('3.8 Health anxiety, cyberchondria and pre-consultation behaviour', 2)
bU = bh('Urgent visit/ER', 'zCSS'); bI = bh('Ignore symptom', 'zCSS'); bT = bh('Delay care (terrified)', 'zCSS'); bNS = bh('Never disclose to physician', 'zSHAI'); bNC = bh('Never disclose to physician', 'zCSS')
bM = bh('Multiple doctors', 'trust'); bR = bh('Negative effect on doctor relationship', 'zCSS'); oR = ordl[(ordl.Outcome.str.startswith('Damage')) & (ordl.Predictor == 'zCSS')].iloc[0]
P(f'When health anxiety and cyberchondria were entered together (Table 11), cyberchondria rather than health anxiety went with behaviour: higher CSS scores were associated with urgent visits (AOR = {bU.AOR:.2f}), fear-driven delay (AOR = {bT.AOR:.2f}), less ignoring of symptoms (AOR = {bI.AOR:.2f}) and a more strained relationship with physicians (ordinal model: OR = {oR.OR:.2f}, 95% CI {ci(oR.CI_low, oR.CI_high)}; the binary model of any negative effect in Table 11 gave a similar, borderline estimate, AOR = {bR.AOR:.2f}, 95% CI {ci(bR.CI_low, bR.CI_high)}). Only one behavioural association survived FDR correction across the 40 tests: higher cyberchondria was associated with lower odds of never disclosing searches to the physician (AOR = {bNC.AOR:.2f}, 95% CI {ci(bNC.CI_low, bNC.CI_high)}, q = {bNC.q_FDR:.3f}). Higher health anxiety showed the opposite tendency (AOR = {bNS.AOR:.2f}, q = {bNS.q_FDR:.3f}), which is exploratory. Greater trust in online/AI information was associated with fewer multiple-doctor consultations (AOR = {bM.AOR:.2f}). Neither score was associated with self-medication or with delaying care because of reassurance.')
rows = []
for outc in ['Urgent visit/ER', 'Multiple doctors', 'Delay/skip care (reassured)', 'Delay care (terrified)', 'Self-medication', 'Ignore symptom', 'Never disclose to physician', 'Negative effect on doctor relationship']:
    a = bh(outc, 'zSHAI'); b = bh(outc, 'zCSS')
    rows.append([outc, int(a.events), f'{a.AOR:.2f} ({ci(a.CI_low, a.CI_high)})', pnum(a.p), f'{b.AOR:.2f} ({ci(b.CI_low, b.CI_high)})', pnum(b.p)])
caption('Table', 'Adjusted associations of health anxiety and cyberchondria with pre-consultation behaviours and the doctor–patient relationship')
table(['Outcome', 'Events', 'SHAI AOR (95% CI)', 'p', 'CSS AOR (95% CI)', 'p'], rows, widths=[5, 1.4, 3.4, 1.4, 3.4, 1.4], size=10,
      note='AOR per 1 SD of each score, from logistic models containing both scores plus trust, AI use, age, gender, health background, chronic disease and language. FDR-adjusted q-values are given in the supplementary workbook.')

H('3.9 Pathways: mediation and moderation', 2)
P(f'In exploratory mediation models (Table 12, Figure 9), excessive searching statistically accounted for part of the association between health anxiety and post-search distress (indirect = {mA_ind.coef:.2f}, 95% CI {ci(mA_ind.CI_low, mA_ind.CI_high)}; direct c′ = {mA_dir.coef:.2f}), and post-search distress for almost all of the association between health anxiety and reassurance-seeking consultations (indirect = {mC_ind.coef:.2f}; direct c′ = {mC_dir.coef:.2f}, {pv(mC_dir.p)}). The reverse ordering was equally significant (indirect = {mD_ind.coef:.2f}, 95% CI {ci(mD_ind.CI_low, mD_ind.CI_high)}), so the data cannot distinguish direction. Participants with elevated health anxiety scored higher on all four dimensions, most markedly excessiveness and distress (Figure 10).')
P(f'None of the tested moderators (trust, AI use, health background, gender, chronic disease, language or age) significantly altered the SHAI–CSS association after FDR correction (all q > 0.40; Table 12 note), and the correlation was moderate to strong in every subgroup of adequate size (r = {sg[sg.n>=40].r.min():.2f} to {sg[sg.n>=40].r.max():.2f}).')
rows = []
for lab_, pre in [('A. HA → excessive searching → post-search distress', 'A:'), ('B. HA → excessive searching → compulsion', 'B:'),
                  ('C. HA → post-search distress → reassurance seeking', 'C:'), ('D. Excessive searching → distress → HA (reverse)', 'D:')]:
    a = med[med.Model.str.startswith(pre)].reset_index(drop=True)
    g = lambda pth: a[a.Path == pth].iloc[0]
    rows.append([lab_, f'{a.iloc[0].coef:.2f}', f'{g("b (M -> Y | X)").coef:.2f}', f'{g("Total").coef:.2f}', f'{g("Direct").coef:.2f}{"" if g("Direct").p < .05 else " (ns)"}',
                 f'{g("Indirect").coef:.2f} ({ci(g("Indirect").CI_low, g("Indirect").CI_high)})'])
rows.append(['E. Serial: HA → excess → distress → reassurance', '', '', '', f'{ser.iloc[3].coef:.2f} (ns)', f'{ser.iloc[2].coef:.2f} ({ci(ser.iloc[2].CI_low, ser.iloc[2].CI_high)})'])
caption('Table', 'Exploratory mediation models decomposing the association between health anxiety (HA) and the dimensions of cyberchondria (standardised coefficients, n = 300)')
table(['Model', 'a', 'b', 'Total (c)', 'Direct (c′)', 'Indirect (95% boot CI)'], rows, widths=[6.2, 1.2, 1.2, 1.7, 1.9, 3.5], size=10,
      note='a: predictor → mediator; b: mediator → outcome adjusted for the predictor; indirect effect = a × b = c − c′. All models adjusted for age, gender, health background, chronic disease, trust and AI use; 5000 bootstrap resamples. All a, b and total paths p < 0.001. Moderation of the SHAI–CSS association (interaction terms): ' +
      '; '.join([f'{r.Moderator.lower()} p = {r.p:.2f}' for _, r in mod.iterrows()]) + f' (all q > 0.40).')
figure(f'{FIG}/fig8_mediation.png', 'Mediation models: (A) excessive searching as a pathway from health anxiety to post-search distress; (B) post-search distress as a pathway from health anxiety to reassurance seeking.', width=16)
figure(f'{FIG}/fig5_subscales_by_HA.png', 'Cyberchondria dimensions by health-anxiety status (mean ± 95% CI).', width=13)

H('3.10 Sensitivity analyses', 2)
P(f'All sensitivity analyses left the main findings unchanged (Table 13). The only result that depended on an analytic decision was the association between AI use and cyberchondria, which disappeared under the strict definition of AI use.')
rows = [
    ['Main analysis (all participants)', f'n = {n}', f'r = {sc["pearson_r"]:.2f}', 'Reference'],
    ['Excluding the three annotated responses', f'n = {n - 3}', f'r = {sens["excluding_flagged_r"]:.2f}', 'Unchanged'],
    ['Excluding straight-line responders', f'n = {sens["n_after"]}', f'r = {sens["excluding_straightliners_r"]:.2f}', 'Unchanged'],
    ['SHAI-14 without item 2 (reordered options)', '13-item total', f'r = {E["item2"]["r_13item_raw"]:.2f}', 'Unchanged'],
    ['Bootstrap of the SHAI coefficient (CSS model)', f'n = {n}', f'B 95% CI {ci(*sens["boot_B_SHAI_CI"])}', 'Stable'],
    ['Quantile regression (25th–90th percentiles)', f'n = {n}', f'B = {quant.B_SHAI.min():.2f} to {quant.B_SHAI.max():.2f}', 'Consistent'],
    ['Quadratic term for SHAI', f'n = {n}', pv(R["quadratic"]["p"]), 'Linear association'],
    ['Multicollinearity (CSS model)', '', f'maximum VIF = {X["T14b_VIF"].VIF.max():.1f}', 'Low'],
    ['Strict AI-use definition (ticked only)', 'n = 234 users', f'B = {ai_alt_B:.2f}, {pv(ai_alt_p)}', 'AI effect not robust'],
    ['Early vs late responders', 'halves', f'CSS p = {sens["early_late_CSS_p"]:.2f}; SHAI p = {sens["early_late_SHAI_p"]:.2f}', 'No difference'],
    ['Regression residuals', '', f'Shapiro–Wilk p = {R["ols_css"]["resid_shapiro_p"]:.3f}; Breusch–Pagan p = {R["ols_css"]["bp_p"]:.3f}', 'Robust SEs used'],
]
caption('Table', 'Sensitivity analyses of the main findings')
table(['Analysis', 'Sample', 'Result', 'Conclusion'], rows, widths=[6.0, 2.4, 4.8, 2.6], size=10,
      note='r: Pearson correlation between SHAI-14 and CSS-12. B: unstandardised coefficient of SHAI in the robust regression of CSS-12. Straight-line responders gave identical answers to every item of the SHAI-14 or of the CSS-12.')

# ------------------------------------------------------------------ DISCUSSION
H('4. Discussion')
H('4.1 Principal findings', 2)
P(f'This study is, to our knowledge, the first to apply the CSS-12 in a Baghdad-based sample, and among the first to place AI chatbots alongside search engines as a source of health information before consulting a doctor. Four findings stand out. First, AI chatbots were used by {E["ai_profile"]["ticked_ai_pct"]:.1f}–{E["ai_profile"]["ai_user_pct"]:.1f}% of participants, depending on the definition, more than search engines, and about two in five used AI without search engines at all. Second, health anxiety and cyberchondria were moderately and robustly associated (r = {sc["pearson_r"]:.2f}), independently of all other measured factors, and health anxiety was the dominant predictor of cyberchondria. Third, the association was concentrated in the excessiveness and distress dimensions; an exploratory decomposition showed that most of it ran statistically through excessive searching and post-search distress. Fourth, cyberchondria was reflected in behaviour towards physicians, most robustly in more frequent disclosure of searches.')
H('4.2 Health anxiety and cyberchondria', 2)
P(f'The observed correlation (r = {sc["pearson_r"]:.2f}) supports H1 and H2 but is weaker than the pooled estimates of about 0.62–0.63 from meta-analyses {cite("mcmullan2019","schenkel2021")}. Part of the gap reflects measurement error: corrected for the reliability of both scales, the correlation would be about {E["disattenuated_r"]:.2f}, close to the meta-analytic range, although our observed estimate remains {sc["pearson_r"]:.2f}. Other explanations are also plausible. Our sample had relatively low health anxiety (mean SHAI {shai.mean():.1f}) and a narrow range in which correlations are attenuated; recruitment through online channels may have favoured confident, habitual Internet users for whom searching is routine rather than alarming; and most previous studies used the full 33-item CSS, whose distress and reassurance items overlap more with health anxiety. The pattern across dimensions is also informative. Distress and excessiveness, the dimensions closest to the cognitive model of health anxiety, were most strongly related to SHAI, while compulsion (interference with work and social life) was rare and only weakly related, consistent with the subscale range reported previously {cite("schenkel2021")}. At item level, it was the *interpretation* of sensations and the *fear* of serious illness, not mere awareness of bodily sensations, that tracked cyberchondria. This is consistent with the view that cyberchondria is more closely tied to catastrophic appraisal than to bodily vigilance itself {cite("salk1986","schenkel2021")}.')
P(f'The prevalence of elevated health anxiety ({prev["HA_clin"]:.0f}% at SHAI ≥ 18) should be interpreted cautiously. The cut-off was derived against healthy controls in Sweden {cite("osterman2022")}; it is not a diagnosis, and prevalence ranged from 7% to 33% across plausible cut-offs. Nevertheless, it indicates that a substantial minority of digitally active adults in Baghdad report elevated health worry, consistent with high rates of health anxiety reported in Iraq during the pandemic {cite("karim2020")}.')
H('4.3 Do health anxiety and cyberchondria fuel each other?', 2)
P(f'The mediation results are consistent with the reinforcing cycle proposed by cognitive-behavioural models and by the longitudinal Dutch study {cite("salk1986","tepoel2016")}: people with higher health anxiety search more, more searching goes with more distress, and distress goes with more reassurance seeking from doctors. That the direct effect of health anxiety on reassurance seeking became negligible once post-search distress was accounted for is compatible with online searching being one route by which health anxiety is turned into healthcare use, but it may equally reflect the strong overlap between the Distress and Reassurance subscales. However, these results must not be over-interpreted. In cross-sectional data, mediation tests are tests of a hypothesised ordering, not of causation, they can be seriously biased estimates of longitudinal processes {cite("olaughlin2018")}, and a significant indirect effect cannot by itself identify the true mediator or the causal order {cite("rohrer2022")}. Our reverse-direction model (searching → distress → health anxiety) was equally significant, which is exactly what one would expect if the relationship is bidirectional, but also what one would expect if both constructs simply share variance. In addition, the mediators and outcomes in models A–C are subscales of the same instrument, so part of their association reflects shared method variance and overlapping item content {cite("podsakoff2024")}. The appropriate conclusion is that our data are *compatible with*, but cannot *demonstrate*, a cycle in which health anxiety and cyberchondria fuel each other.')
P('H3 is therefore supported statistically, but not causally.')
H('4.4 The role of AI chatbots', 2)
P(f'The extent of AI chatbot use ({E["ai_profile"]["ticked_ai_pct"]:.0f}% ticked; {pct(ai_n)} including those who named a chatbot) is a new finding and contrasts with a 2024 US survey in which about one in five respondents reported using ChatGPT for health information {cite("ayo2024")}, and with a 2025 online survey in which 21% used LLM chatbots for health information against 98% using search engines {cite("yun2025")}. Our sample was young and highly educated, which partly explains the difference: AI use fell from 96% in those aged 18–19 to 72% in those aged 40 and over. Under the inclusive definition, AI users had higher cyberchondria, mainly in excessiveness and reassurance seeking, but this association disappeared under the stricter definition, rested on a small and older comparison group (n = 34), and AI use did not modify the strength of the health anxiety–cyberchondria link. We therefore find no reliable evidence that AI chatbot use is associated with cyberchondria independently of health anxiety; this is an absence of evidence rather than evidence of absence. Because LLM chatbots answer in fluent, personalised and empathetic language {cite("thiru2023","ayers2023")}, they could invite repeated, conversational querying; alternatively, people who already search heavily may simply adopt every available tool. The level of AI use in our sample resembles that of young Turkish dermatology outpatients (61%), in whom pre-visit AI consultation mainly confirmed an existing decision to seek care and was not associated with increased anxiety {cite("digis2026")}; in a large Czech sample, health anxiety was linked to AI use only through trust {cite("svestkova2025")}, whereas in our data trust was unrelated to health anxiety. On current evidence, AI chatbots appear to be a new channel for, rather than a demonstrated driver of, cyberchondria, which is consistent with observations that health-anxious people are over-represented among users of digital symptom checkers {cite("wetzel2024")}.')
P(f'Trust in online and AI information was mostly moderate and was associated with excessive searching but not with distress. Higher trust was also associated with lower odds of consulting several doctors, suggesting that trusted AI answers may substitute for some "doctor shopping". This is potentially beneficial for health services, but it is also where false reassurance becomes a risk: higher trust showed a non-significant trend towards delaying care because of reassurance (AOR = {bh("Delay/skip care (reassured)","trust").AOR:.2f}, {pv(bh("Delay/skip care (reassured)","trust").p)}), echoing a multinational study from the Middle East and North Africa in which trust in online information strongly predicted delayed consultation {cite("dahshan2026")}.')
H('4.5 Pre-consultation behaviour and the doctor–patient relationship', 2)
P(f'The most common response after searching, delaying or skipping care because the information was reassuring (35%), is a double-edged finding. For self-limiting symptoms it may save unnecessary visits; for serious ones it represents a risk of delayed diagnosis. Notably, this behaviour was not related to health anxiety or cyberchondria, meaning it occurs across the spectrum and cannot be dismissed as a feature of anxious users. Conversely, cyberchondria was associated with urgent visits and emergency attendance and with fear-driven delay, although these associations did not survive FDR correction and are exploratory, mirroring evidence that health anxiety and cyberchondria increase healthcare utilisation {cite("tyrer2018","mathes2018")}. Thus online searching appears to push different people in opposite directions: towards complacency in some and towards over-use of services in others.')
P(f'The disclosure findings are clinically important. Almost a third of participants said they never told their doctor about their searches for fear of being judged or dismissed; because the response option combined frequency with a reason, this figure describes non-disclosure attributed to fear of judgement rather than all non-disclosure. Higher cyberchondria was robustly associated with more disclosure (q = {bNC.q_FDR:.3f}), whereas the tendency for higher health anxiety to go with concealment was nominal only (q = {bNS.q_FDR:.3f}). One interpretation is that patients for whom searching is a dominant behaviour bring their findings to the consultation as part of reassurance seeking, while health-anxious patients may anticipate being labelled as "worried well"; the second part of this interpretation needs confirmation. Concealment matters because online information discussed openly can strengthen the doctor–patient relationship, whereas undisclosed information is more likely to undermine it {cite("luo2022")}. One in three participants reported that searching had complicated (22%) or significantly reduced (13%) their relationship with or trust in physicians, and this tended to be more likely at higher levels of cyberchondria (a nominal association).')
P('H4 is therefore only partially supported: the only behavioural association that survived correction for multiple testing was between higher cyberchondria and more frequent disclosure of searches to physicians.')
H('4.6 Medical and health-science students', 2)
P(f'Medical students had higher unadjusted health anxiety than non-health employees, but this difference disappeared after adjustment, largely reflecting their younger age; age was an independent predictor of elevated health anxiety. The SHAI–CSS correlation tended to be stronger among medical students. This is compatible with the idea of "medical student syndrome", but evidence for that concept is weak: in a recent Palestinian study using the same SHAI ≥ 18 threshold, elevated health anxiety was actually least common among medical students {cite("fasfoos2026")}, and our data suggest that medical knowledge does not protect against cyberchondria (medical students\' CSS scores were identical to those of other participants).')
H('4.7 Comparison with regional studies', 2)
P(f'Our findings are in line with emerging Arab-region data. In Jeddah, cyberchondria was common and associated with smartphone addiction {cite("elzayat2023")}; among Saudi primary-care patients, cyberchondria had a positive effect on health anxiety in structural models {cite("pasayan2025")}; and the Arabic CSS-12 showed a structure similar to ours in Lebanon {cite("hallit2023")}. Among 1435 Egyptian medical students, the population closest to ours, 85.8% showed moderate cyberchondria on the CSS-12, and worry about one\'s own or a family member\'s health predicted it {cite("elzoghby2024")}; a Saudi validation of the CSS-12 likewise found acceptable reliability and positive correlations with health anxiety {cite("alshaibani2023")}. The good fit of the four-factor CSS-12, its full scalar invariance across Arabic and English responders and the absence of item-level DIF add to the evidence that the instrument functions well in Arabic-speaking populations.')
H('4.8 Strengths and limitations', 2)
P(f'Strengths of this study include the use of two established instruments with good reliability and confirmed structure; a bilingual questionnaire with formal tests of measurement invariance across languages; the separate assessment of AI chatbots; complete data; correction for multiple testing; robust regression, bootstrap inference and several sensitivity analyses; and the linking of psychological measures to concrete behaviours relevant to clinical practice.')
P('The limitations are substantial and should be weighed carefully:')
for b in ['**Design and causality:** the cross-sectional design cannot establish temporal order; mediation results describe statistical pathways, not causal mechanisms, and may be biased relative to longitudinal effects.',
          f'**Sampling and generalisability:** an online convenience/snowball sample is subject to self-selection. The sample was young, highly educated and over-represented medical students ({pct(medst)}) and people with health backgrounds ({pct(hb)}), so prevalence estimates and the frequency of AI use cannot be generalised to the adult population of Baghdad. Residence in Baghdad was assured by the distribution channels rather than verified by a question, and non-Internet users, older adults and less-educated people are under-represented by design.',
          f'**Measurement:** the Arabic wording was produced by the research team without a formal forward–backward translation and cognitive pre-testing; formal tests supported full (scalar) invariance of the CSS-12 and metric invariance of the SHAI-14 across language groups, with no item showing DIF after correction, but SHAI-14 intercepts were not fully equivalent and its baseline model fitted poorly, so its invariance results are hard to interpret, the language groups were self-selected rather than randomised, and statistical invariance does not replace formal cross-cultural adaptation with cognitive pre-testing. Published Arabic versions of both scales exist {cite("alshayea2020","hallit2023","alshaibani2023")} but were not used, so comparability with Arabic studies that used them is uncertain. On the form, the response options of one SHAI item (item 2) were displayed out of their original order; scoring followed the original key, and dropping the item did not change the main result, but the order may still have influenced answers. CSS item 3 refers only to search engines and may under-capture repeated querying of AI chatbots. "Language relied on" was self-selected, not randomised. The SHAI-14 one-factor model fitted poorly under maximum-likelihood estimation. The SHAI cut-off was derived in Sweden, and the CSS-12 has no validated clinical cut-off, so the "high cyberchondria" group is sample-relative.',
          '**Single-item and self-designed measures:** trust, motivations, behaviours, disclosure and relationship were assessed with single, non-validated items, some allowing multiple answers. The questionnaire asked for "most frequent" behaviours but allowed several answers; the trust item combined online tools and AI, so it cannot separate trust in search results from trust in chatbots; the disclosure option combined frequency with a reason (fear of judgement); and "somewhat complicated" is not clearly a negative effect on the relationship.',
          '**Self-report bias:** all measures were self-reported and may be affected by recall and social desirability bias; no clinical data or diagnoses were available, and chronic disease was self-reported.',
          '**Multiple testing and power:** despite FDR correction, the large number of exploratory tests means that some isolated associations may be false positives; several behavioural associations were nominally significant only. Some subgroups (non-AI users, n = 34; healthcare workers, n = 15; older age groups) were small, and the logistic model for elevated health anxiety had about five events per predictor.',
          '**Classification of AI use:** 32 respondents named an AI chatbot without ticking the AI option. They were classed as users, and the independent association between AI use and cyberchondria depended on this decision, so it should be regarded as tentative.',
          '**Data quality:** an online survey cannot exclude careless responding entirely; nine straight-line responders were identified, although their exclusion did not change the results.']:
    bullet(b)

# ------------------------------------------------------------------ CONCLUSIONS
H('5. Conclusions and Recommendations')
H('5.1 Conclusions', 2)
for b in [f'AI chatbots, mainly ChatGPT, have become a leading source of health information before consulting a doctor among digitally active adults in Baghdad: {E["ai_profile"]["ticked_ai_pct"]:.1f}% ticked them ({pct(ai_n)} including those who named a chatbot), more than used search engines.',
          f'About one in five participants ({prev["HA_clin"]:.0f}%) had elevated health anxiety (SHAI ≥ 18, a screening threshold rather than a diagnosis; {sens["prev_SHAI_ge_29"]:.1f}% at the stricter cut-off of 29), and younger people and those searching for instant reassurance were most affected.',
          f'Health anxiety and cyberchondria are moderately and robustly associated (r = {sc["pearson_r"]:.2f}); health anxiety is the strongest independent predictor of cyberchondria, especially of excessive searching and post-search distress.',
          'The pattern of associations is compatible with a reinforcing cycle (health anxiety, excessive searching, distress, reassurance-seeking consultations), but the cross-sectional decomposition, based on subscales of one instrument, cannot establish direction.',
          'There is no reliable evidence that AI-chatbot use is associated with cyberchondria independently of health anxiety: the association depended on how inconsistent answers about AI use were classified, and AI use did not change the strength of the health anxiety–cyberchondria link.',
          'Online searching shapes the consultation: about one-third of participants delay care because they feel reassured, about one-third never disclose their searches to their doctor for fear of judgement, and about one-third say searching has complicated or reduced their trust in physicians. Higher cyberchondria was robustly linked with more disclosure; links with urgent care-seeking, concealment by health-anxious participants and a strained relationship were exploratory.']:
    numbered(b)
H('5.2 Recommendations', 2)
P('**For clinicians and medical education:**', indent=False)
for b in ['Routinely and non-judgementally ask patients what they have searched for or asked an AI chatbot, to bring hidden information into the consultation and reduce concealment.',
          'Recognise repeated searching, post-search distress and repeated reassurance seeking as possible markers of health anxiety, and screen with a brief tool such as the SHAI where appropriate; offer cognitive-behavioural strategies rather than repeated reassurance or investigations.',
          'Include digital health communication, AI literacy and the management of health anxiety in undergraduate medical curricula, and support medical students who may themselves be vulnerable.']:
    bullet(b)
P('**For the Ministry of Health and public-health bodies:**', indent=False)
for b in ['The Ministry of Health may consider campaigns on digital and AI health literacy that explain both the uses and the limits of online information, especially false reassurance that leads to delayed care.',
          'It may also consider providing or endorsing reliable Arabic-language health information sources and triage services so that people searching for "whether I need a doctor" are directed to safe advice.']:
    bullet(b)
P('**For developers of AI tools:**', indent=False)
for b in ['Developers may consider designing health responses that recognise signs of health anxiety (e.g. repeated questions about the same symptom), avoid escalating rare diagnoses without context, and encourage appropriate professional consultation, in Arabic as well as English.']:
    bullet(b)
P('**For future research:**', indent=False)
for b in [f'Develop and test interventions: ClinicalTrials.gov lists only nine registered studies on cyberchondria (October 2026), none in Iraq and six of them observational and three interventional {cite("ctgov2026")}, so trials of brief digital health-literacy or cognitive-behavioural interventions in Arabic are a clear gap.',
          'Conduct longitudinal or experience-sampling studies to test whether health anxiety and cyberchondria reinforce each other over time, and experimental studies comparing AI chatbot and search-engine answers on post-search anxiety.',
          'Use probability sampling of the general Baghdad population, including older and less-educated adults, and use formally adapted Arabic instruments (the published CSS-12-Ar and Arabic SHAI, or a new forward–backward adaptation with measurement-invariance testing), with CSS item 3 worded to cover both search engines and AI chatbots.',
          'Link self-reported behaviours to objective healthcare utilisation and clinical outcomes, especially delayed diagnosis following false reassurance.']:
    bullet(b)

# ------------------------------------------------------------------ REFERENCES
H('6. References')
for i, k in enumerate(order, 1):
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
    p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(4); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(f'{i}.\t{REFS[k]}'); r.font.size = Pt(12)
unused = [k for k in REFS if k not in order]

# ------------------------------------------------------------------ APPENDIX
page_break()
H('Appendices')
H('Appendix A. Item-by-item correlations between the SHAI-14 and CSS-12', 2)
P(f'Item-by-item Spearman correlations between all 14 SHAI-14 items and all 12 CSS-12 items (168 pairs). Correction for multiple testing was applied within this family of 168 tests: {ib["sig_fdr"]} pairs were significant after Benjamini–Hochberg FDR correction and {ib["sig_holm"]} after Holm–Bonferroni correction. Full values are given in the supplementary workbook (sheet T28_item_by_item).', indent=False)
figure(f'{FIG}/fig9_item_by_item.png', 'Item-by-item correlations between SHAI-14 and CSS-12 items (Spearman ρ). * significant after FDR correction across the 168 pairs; ** also significant after Holm–Bonferroni correction.', width=16)

page_break()
H('Appendix B. Study questionnaire', 2)
P('The bilingual (English–Arabic) questionnaire as administered through Google Forms is reproduced below (41 questions).', indent=False)
import glob
from PIL import Image as _Im
QIMGS = sorted(glob.glob(f'{OUT}/questionnaire/c-*.png'))   # pages cropped to content; they flow onto pages naturally
for qi in QIMGS:
    w_px, h_px = _Im.open(qi).size
    w_cm = min(12.5, 12.5 * w_px / 760)                     # same scale for every page; two form pages fit per A4 page
    if w_cm * h_px / w_px > 23.5: w_cm = 23.5 * w_px / h_px  # never taller than the page body
    pq = doc.add_paragraph(); pq.alignment = WD_ALIGN_PARAGRAPH.CENTER; pq.paragraph_format.space_after = Pt(4)
    pq.paragraph_format.line_spacing = 1.0
    pq.add_run().add_picture(qi, width=Cm(w_cm))

# ------------------------------------------------------------------ fill lists of tables/figures
PAGES = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
def fld(kind_):
    e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), kind_); return e
def fill_list(anchor, items, kind):
    # Word TOC field over the captions (refreshes on open); cached result carries page numbers from the render pass
    prev_el = anchor
    for i, t_ in enumerate(items, 1):
        p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Cm(2.0); p.paragraph_format.first_line_indent = Cm(-2.0)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(2.0))
        from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
        p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        if i == 1:
            r0 = p.add_run(); r0._r.append(fld('begin'))
            it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = f'TOC \\h \\z \\c "{kind}"'; r0._r.append(it); r0._r.append(fld('separate'))
        r = p.add_run(f'{kind} {i}.\t'); r.bold = True; r.font.size = Pt(13)
        r2 = p.add_run(t_); r2.font.size = Pt(13)
        r3 = p.add_run(f'\t{PAGES.get(f"{kind} {i}", "")}'); r3.font.size = Pt(13)
        if i == len(items): r3._r.append(fld('end'))
        prev_el._p.addnext(p._p); prev_el = p
fill_list(LT_anchor, tables_list, 'Table'); fill_list(LF_anchor, figures_list, 'Figure')

# table of contents: Word TOC field over Heading 1-2 (refreshes on open); cached entries carry rendered page numbers
start = next(i for i, (l, t) in enumerate(HEADS) if t.startswith('Summary'))
TOC = HEADS[start:]
json.dump(TOC, open(f'{OUT}/toc_entries.json', 'w'))
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
prev_el = TOC_anchor
for i, (lvl, t_) in enumerate(TOC):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(3 if lvl > 1 else 5)
    p.paragraph_format.left_indent = Cm(0 if lvl == 1 else 0.8)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    if i == 0:
        r0 = p.add_run(); r0._r.append(fld('begin'))
        it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = 'TOC \\o "1-2" \\h \\z \\u'; r0._r.append(it); r0._r.append(fld('separate'))
    r = p.add_run(t_); r.font.size = Pt(13 if lvl == 1 else 12); r.bold = (lvl == 1)
    r3 = p.add_run(f'\t{PAGES.get("H::" + t_, "")}'); r3.font.size = Pt(13 if lvl == 1 else 12)
    if i == len(TOC) - 1: r3._r.append(fld('end'))
    prev_el._p.addnext(p._p); prev_el = p

# ------------------------------------------------------------------ page numbering
def page_number_footer(section, fmt, start, title_page=False):
    sectPr = section._sectPr
    pg = OxmlElement('w:pgNumType'); pg.set(qn('w:fmt'), fmt); pg.set(qn('w:start'), str(start)); sectPr.append(pg)
    section.footer.is_linked_to_previous = False
    fp = section.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run(); r.font.name = FONT; r.font.size = Pt(12); add_field(r, 'PAGE')
    if title_page:
        section.different_first_page_header_footer = True
s1, s2 = doc.sections[0], doc.sections[1]
page_number_footer(s1, 'lowerRoman', 1, title_page=True)
page_number_footer(s2, 'decimal', 1)
for s in doc.sections:
    s.page_height, s.page_width = Cm(29.7), Cm(21.0)
    s.left_margin = Cm(3.0); s.right_margin = Cm(2.5); s.top_margin = Cm(2.5); s.bottom_margin = Cm(2.5)
# ask Word to refresh fields on open
settings = doc.settings.element; uf = OxmlElement('w:updateFields'); uf.set(qn('w:val'), 'true'); settings.append(uf)
# typographic minus for negative numbers (hyphen-minus -> U+2212), skipping hyphens inside words, ranges and identifiers
def _minus(paragraphs):
    for para in paragraphs:
        prev = ' '
        for run in para.runs:
            s = run.text; out = []
            for i, ch in enumerate(s):
                before = s[i - 1] if i else prev
                nxt = s[i + 1] if i + 1 < len(s) else ''
                out.append('\u2212' if ch == '-' and nxt.isdigit() and not (before.isalnum() or before in '–-/.:') else ch)
            new = ''.join(out)
            if new != s: run.text = new   # only touch runs that change (field runs stay intact)
            if s: prev = s[-1]
_minus(doc.paragraphs)
for _t in doc.tables:
    for _row in _t.rows:
        for _c in _row.cells: _minus(_c.paragraphs)
doc.save(DOCX)
print('saved', DOCX, '| refs cited:', len(order), '| unused refs:', unused, '| tables:', len(tables_list), '| figures:', len(figures_list))
