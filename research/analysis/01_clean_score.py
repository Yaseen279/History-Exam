"""Clean, recode and score the questionnaire responses.

Usage: python3 01_clean_score.py <raw.xlsx> <out.pkl>
SHAI-14 (Salkovskis et al., 2002): 14 items, each 0-3 by the meaning of the option
(not by its position on the form), total 0-42.
CSS-12 (McElroy et al., 2019): 12 items, Never=1 ... Always=5, total 12-60;
subscales of 3 items: Excessiveness, Compulsion, Distress, Reassurance.
"""
import sys, re
import numpy as np, pandas as pd

raw = pd.read_excel(sys.argv[1])
C = list(raw.columns)
en = lambda s: s.astype(str).str.split(' / ').str[0].str.strip()
d = pd.DataFrame(index=raw.index)
d['id'] = np.arange(1, len(raw) + 1)
d['timestamp'] = raw[C[0]]

# ---------- demographics ----------
age = en(raw[C[2]])
d['age_group'] = pd.Categorical(age, ['18-19', '20-29', '30-39', '40-49', '50-59', '60+'], ordered=True)
d['age_ord'] = d['age_group'].cat.codes + 1
d['age4'] = pd.Categorical(age.replace({'40-49': '≥40', '50-59': '≥40', '60+': '≥40'}),
                           ['18-19', '20-29', '30-39', '≥40'], ordered=True)
d['gender'] = en(raw[C[3]])
d['female'] = (d['gender'] == 'Female').astype(int)

edu = en(raw[C[4]])
edu = edu.replace({'Postgraduate degree (Master\'s or Ph.D.)': 'Postgraduate', 'PhD': 'Postgraduate',
                   "Bachelor's degree": 'Bachelor', 'Diploma': 'Diploma/Vocational',
                   'High school or below': 'High school or below', 'Currently a student': 'Currently a student'})
d['education'] = edu

occ_raw = raw[C[5]].astype(str)
def occ(s):
    s0 = s.split(' / ')[0].strip()
    if s0.startswith('Medical student'): return 'Medical student'
    if s0.startswith('Student in another healthcare'): return 'Other health-science student'
    if s0.startswith('Student in a non-healthcare') : return 'Non-health student'
    if s0.startswith('Medical Doctor') or s0.startswith('Other healthcare professional'): return 'Healthcare worker'
    if s0.startswith('Employed/working in a non-healthcare'): return 'Non-health employee/other'
    low = s0.lower()
    # free-text "Other" answers: students and secondary-school leavers -> non-health student
    student_words = ['student', 'طالب', 'سادس', 'لم ادخل الجامعة']
    if any(w in low for w in student_words): return 'Non-health student'
    # remaining free text: engineer, business owner, university staff, housewife, not working, etc.
    return 'Non-health employee/other'
d['occupation'] = occ_raw.map(occ)
d['occ_raw'] = occ_raw.str.split(' / ').str[0]
d['health_background'] = d['occupation'].isin(['Medical student', 'Other health-science student', 'Healthcare worker']).astype(int)
d['medical_student'] = (d['occupation'] == 'Medical student').astype(int)

d['chronic'] = (en(raw[C[6]]) == 'Yes').astype(int)
d['chronic_text'] = raw[C[7]]

# ---------- tools (multi-select) ----------
tools = raw[C[8]].fillna('')
d['tool_search'] = tools.str.contains('Search engine').astype(int)
d['tool_ai'] = tools.str.contains('AI Chatbots').astype(int)
d['tool_medplat'] = tools.str.contains('Dedicated Medical Platforms').astype(int)
d['tool_social'] = tools.str.contains('Social Media').astype(int)
ai_model = raw[C[9]].fillna('').astype(str).str.strip()
def aim(s):
    if s.lower() in ('nan', 'none', ''): return 'None reported'
    if s in ('ChatGPT', 'Gemini', 'Claude'): return s
    return 'Other AI'
d['ai_model'] = ai_model.map(aim)
d['ai_model_inconsistent'] = ((d['ai_model'] != 'None reported') & (d.tool_ai == 0)).astype(int)
# A respondent naming an AI model is counted as an AI user (decision reported in Methods)
d['ai_user'] = ((d.tool_ai == 1) | (d['ai_model'] != 'None reported')).astype(int)
d['n_tools'] = d[['tool_search', 'tool_ai', 'tool_medplat', 'tool_social']].sum(axis=1)
d['ai_only'] = ((d.ai_user == 1) & (d.tool_search == 0) & (d.tool_medplat == 0) & (d.tool_social == 0)).astype(int)
def toolprofile(r):
    if r.ai_user and r.tool_search: return 'AI + search engine'
    if r.ai_user: return 'AI without search engine'
    return 'No AI (search/other only)'
d['tool_profile'] = d.apply(toolprofile, axis=1)

# ---------- motivations ----------
mot = raw[C[10]].fillna('')
d['mot_convenience'] = mot.str.contains('Immediate convenience').astype(int)
d['mot_cost'] = mot.str.contains('High costs').astype(int)
d['mot_reassurance'] = mot.str.contains('instant reassurance').astype(int)
d['mot_selfdx'] = mot.str.contains('self-diagnose').astype(int)
d['mot_triage'] = mot.str.contains('serious enough').astype(int)
d['n_motives'] = d[['mot_convenience', 'mot_cost', 'mot_reassurance', 'mot_selfdx', 'mot_triage']].sum(axis=1)

trust_map = {'Do not trust at all': 1, 'Slightly trust': 2, 'Moderately trust': 3, 'Very much trust': 4, 'Completely trust': 5}
d['trust'] = raw[C[11]].astype(str).str.split('/').str[0].str.strip().map(trust_map)

# ---------- SHAI-14 ----------
shai_keys = [  # (column index, short name, [option stems in score order 0..3])
 (12, 'Worry', ['I do not worry', 'I occasionally worry', 'I spend much of my time', 'I spend most of my time']),
 (13, 'Body awareness', ['I notice aches/pains less', 'I notice aches/pains as much', 'I notice aches/pains more', 'I am aware of aches/pains in my body all the time']),
 (14, 'Sensations', ['As a rule, I am not aware', 'Sometimes I am aware', 'I am often aware', 'I am constantly aware']),
 (15, 'Resisting thoughts', ['Resisting thoughts of illness is never', 'Most of the time I can resist', 'I try to resist', 'Thoughts of illness are so strong']),
 (16, 'Fear of illness', ['As a rule, I am not afraid', 'I am sometimes afraid', 'I am often afraid', 'I am always afraid']),
 (17, 'Images of illness', ['I do not have images', 'I occasionally have images', 'I frequently have images', 'I constantly have images']),
 (18, 'Distraction', ['I do not have any difficulty', 'I sometimes have difficulty', 'I often have difficulty', 'Nothing can take my mind']),
 (19, 'Reassurance', ['I am lastingly relieved', 'I am initially relieved, but the worries sometimes', 'I am initially relieved, but the worries always', 'I am not relieved']),
 (20, 'Hearing about illness', ['If I hear about an illness, I never', 'If I hear about an illness, I sometimes', 'If I hear about an illness, I often', 'If I hear about an illness, I always']),
 (21, 'Interpretation', ['I rarely wonder', 'I often wonder', 'I always wonder', 'I must know']),
 (22, 'Perceived risk', ['very low risk', 'fairly low risk', 'moderate risk', 'high risk']),
 (23, 'Thinking ill', ['I never think I have', 'I sometimes think I have', 'I often think I have', 'I usually think that I am']),
 (24, 'Unexplained sensations', ["I don't find it difficult", 'I sometimes find it difficult', 'I often find it difficult', 'I always find it difficult']),
 (25, 'Family view', ['do not worry enough', 'normal attitude', 'worry too much', 'hypochondriac']),
]
for k, (ci, name, stems) in enumerate(shai_keys, 1):
    col = raw[C[ci]].astype(str)
    sc = pd.Series(np.nan, index=raw.index)
    for v, stem in enumerate(stems):
        hit = col.str.contains(re.escape(stem), regex=True)
        assert not (hit & sc.notna()).any(), (name, stem)
        sc[hit] = v
    assert sc.notna().all(), f'unscored SHAI item {name}: {col[sc.isna()].unique()[:3]}'
    d[f'shai{k}'] = sc.astype(int)
SHAI = [f'shai{k}' for k in range(1, 15)]
d['SHAI'] = d[SHAI].sum(axis=1)
d['HA_clin'] = (d['SHAI'] >= 18).astype(int)   # >=18: optimal cut-off vs healthy controls (Österman et al., 2022)

# ---------- CSS-12 ----------
freq = {'Never': 1, 'Rarely': 2, 'Sometimes': 3, 'Often': 4, 'Always': 5}
css_names = ['Search unexplained sensation', 'Read different pages', 'Enter same symptoms repeatedly',
             'Distracts from news/entertainment', 'Interrupts work', 'Interrupts social activities',
             'Panic on reading rare/serious', 'Feel fine until reading', 'More anxious after searching',
             'Consult GP', 'Suggest diagnostic procedure', 'Consult other specialists']
for k in range(12):
    v = en(raw[C[26 + k]]).map(freq)
    assert v.notna().all()
    d[f'css{k+1}'] = v.astype(int)
CSS = [f'css{k}' for k in range(1, 13)]
d['CSS'] = d[CSS].sum(axis=1)
d['CSS_excess'] = d[['css1', 'css2', 'css3']].sum(axis=1)
d['CSS_compul'] = d[['css4', 'css5', 'css6']].sum(axis=1)
d['CSS_distress'] = d[['css7', 'css8', 'css9']].sum(axis=1)
d['CSS_reassur'] = d[['css10', 'css11', 'css12']].sum(axis=1)

# ---------- behavioural responses ----------
beh = raw[C[38]].fillna('')
d['beh_selfmed'] = beh.str.contains('self-prescribed').astype(int)
d['beh_delay_reassured'] = beh.str.contains('reassured me').astype(int)
d['beh_delay_terrified'] = beh.str.contains('terrified').astype(int)
d['beh_urgent'] = beh.str.contains('urgent appointment').astype(int)
d['beh_multidoc'] = beh.str.contains('multiple different doctors').astype(int)
d['beh_ignore'] = beh.str.contains('ignore the symptom').astype(int)
d['beh_any_delay'] = ((d.beh_delay_reassured + d.beh_delay_terrified) > 0).astype(int)
d['beh_any_overuse'] = ((d.beh_urgent + d.beh_multidoc) > 0).astype(int)

share = en(raw[C[39]])
d['share'] = share.map(lambda s: 'Always' if s.startswith('Yes') else ('Sometimes' if s.startswith('Sometimes') else 'Never (fear of judgement)'))
d['share_never'] = (d.share == 'Never (fear of judgement)').astype(int)
rel = en(raw[C[40]])
d['relationship'] = rel.map(lambda s: 'No negative impact' if s.startswith('It had no') else
                            ('Somewhat complicated' if s.startswith('It somewhat') else 'Significantly reduced trust'))
d['rel_negative'] = (d.relationship != 'No negative impact').astype(int)
d['language'] = en(raw[C[41]]).map(lambda s: 'English' if 'English' in s else 'Arabic')

d['flag_note'] = raw[C[42]].fillna('').astype(str) + raw[C[43]].fillna('').astype(str)
d.to_pickle(sys.argv[2])
print(d.shape)
print(d[['SHAI', 'CSS', 'CSS_excess', 'CSS_compul', 'CSS_distress', 'CSS_reassur', 'trust']].describe().round(2).to_string())
print('HA>=18:', d.HA_clin.sum(), '| AI users:', d.ai_user.sum(), '| inconsistent AI:', d.ai_model_inconsistent.sum())
print(d.occupation.value_counts().to_string())
