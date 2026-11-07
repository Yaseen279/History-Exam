"""Export the cleaned, scored dataset to SPSS (.sav) with variable/value labels and measurement levels,
plus a syntax file (.sps) that reproduces the study's methodology in SPSS.

Usage: python3 08_spss_export.py <analysed.pkl> <outdir>
"""
import sys, os
import numpy as np, pandas as pd
import pyreadstat

d = pd.read_pickle(sys.argv[1]); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)

SHAI_LAB = ['Worry about health', 'Noticing aches/pains', 'Awareness of bodily sensations', 'Resisting thoughts of illness',
            'Fear of serious illness', 'Images of being ill', 'Distraction from health thoughts', 'Relief after medical reassurance',
            'Hearing about an illness', 'Interpreting bodily sensations', 'Perceived risk of serious illness', 'Thinking you are ill',
            'Unexplained sensations', 'Family/friends view']
CSS_LAB = ['Search unexplained sensation online', 'Read different pages on same condition', 'Enter same symptoms repeatedly',
           'Distracts from news/sports/entertainment', 'Interrupts work', 'Interrupts offline social activities',
           'Panic on reading of rare/serious condition', 'Feel fine until reading online', 'More anxious after searching',
           'Leads to consulting GP', 'Suggest diagnostic procedure to doctor', 'Leads to consulting other specialists']

def code(series, mapping):
    out = series.map(mapping)
    assert out.notna().all(), (series.name, set(series[out.isna()]))
    return out.astype(int)

YN = {0: 'No', 1: 'Yes'}
cats = {
 'age_group': (['18-19', '20-29', '30-39', '40-49', '50-59', '60+'], 'Age group (years)'),
 'age4': (['18-19', '20-29', '30-39', '≥40'], 'Age group, 40+ merged (analysis)'),
 'education': (['Currently a student', 'High school or below', 'Diploma/Vocational', 'Bachelor', 'Postgraduate'], 'Highest education'),
 'occupation': (['Medical student', 'Other health-science student', 'Healthcare worker', 'Non-health student', 'Non-health employee/other'], 'Study/work (recoded)'),
 'ai_model': (['None reported', 'ChatGPT', 'Gemini', 'Claude', 'Other AI'], 'Main AI chatbot'),
 'tool_profile': (['AI + search engine', 'AI without search engine', 'No AI (search/other only)'], 'Tool profile'),
 'share': (['Always', 'Sometimes', 'Never (fear of judgement)'], 'Discloses online/AI searches to physician'),
 'relationship': (['No negative impact', 'Somewhat complicated', 'Significantly reduced trust'], 'Effect of searching on relationship/trust with doctors'),
 'language': (['Arabic', 'English'], 'Language mainly relied on when answering'),
 'gender': (['Male', 'Female'], 'Gender'),
}
s = pd.DataFrame({'id': d['id'].astype(int)})
s['date'] = pd.to_datetime(d['timestamp']).dt.normalize()
vlab = {'id': 'Participant ID', 'date': 'Date of submission'}
vals = {}; measure = {'id': 'nominal', 'date': 'scale'}

for v, (levels, lab) in cats.items():
    start = 0 if v == 'ai_model' else 1
    mp = {lv: i + start for i, lv in enumerate(levels)}
    s[v] = code(d[v].astype(str), mp)
    vlab[v] = lab; vals[v] = {i: lv for lv, i in mp.items()}
    measure[v] = 'ordinal' if v in ('age_group', 'age4', 'share', 'relationship') else 'nominal'

binaries = {
 'female': 'Female (1 = yes)', 'health_background': 'Health-related background (medical/health student or worker)',
 'medical_student': 'Medical student', 'chronic': 'Diagnosed chronic medical condition',
 'tool_search': 'Tool used: search engine', 'tool_ai': 'Tool used: AI chatbot (ticked)', 'ai_user': 'AI chatbot user (ticked or named a chatbot)',
 'ai_model_inconsistent': 'Named a chatbot without ticking AI', 'tool_medplat': 'Tool used: dedicated medical platform', 'tool_social': 'Tool used: social media',
 'mot_convenience': 'Motive: convenience/accessibility', 'mot_cost': 'Motive: cost/logistic barriers', 'mot_reassurance': 'Motive: instant reassurance',
 'mot_selfdx': 'Motive: self-diagnosis / double-check prescription', 'mot_triage': 'Motive: check whether a doctor visit is needed',
 'beh_selfmed': 'After search: self-medication', 'beh_delay_reassured': 'After search: delay/skip care (reassured)',
 'beh_delay_terrified': 'After search: delay care (frightened)', 'beh_urgent': 'After search: urgent appointment/ER/fast diagnosis',
 'beh_multidoc': 'After search: visit multiple doctors', 'beh_ignore': 'After search: ignore the symptom',
 'share_never': 'Never discloses searches to physician', 'rel_negative': 'Any negative effect on relationship with doctors',
 'HA_clin': 'Elevated health anxiety (SHAI-14 >= 18)', 'CSS_high': 'High cyberchondria (CSS-12 > 33, upper tertile)',
}
for v, lab in binaries.items():
    s[v] = d[v].astype(int); vlab[v] = lab; vals[v] = YN; measure[v] = 'nominal'
s = s.rename(columns={'HA_clin': 'HA_elevated'}); vlab['HA_elevated'] = vlab.pop('HA_clin'); vals['HA_elevated'] = vals.pop('HA_clin'); measure['HA_elevated'] = measure.pop('HA_clin')

s['trust'] = d['trust'].astype(int); vlab['trust'] = 'Trust in medical data from online tools/AI (1-5)'
vals['trust'] = {1: 'Do not trust at all', 2: 'Slightly trust', 3: 'Moderately trust', 4: 'Very much trust', 5: 'Completely trust'}; measure['trust'] = 'ordinal'
for k, lab in enumerate(SHAI_LAB, 1):
    v = f'shai{k}'; s[v] = d[v].astype(int); vlab[v] = f'SHAI item {k}: {lab} (0-3)'
    vals[v] = {0: '0 (least)', 1: '1', 2: '2', 3: '3 (most)'}; measure[v] = 'ordinal'
for k, lab in enumerate(CSS_LAB, 1):
    v = f'css{k}'; s[v] = d[v].astype(int); vlab[v] = f'CSS item {k}: {lab}'
    vals[v] = {1: 'Never', 2: 'Rarely', 3: 'Sometimes', 4: 'Often', 5: 'Always'}; measure[v] = 'ordinal'
scores = {'SHAI': 'SHAI-14 total (0-42)', 'CSS': 'CSS-12 total (12-60)', 'CSS_excess': 'CSS Excessiveness (3-15)', 'CSS_compul': 'CSS Compulsion (3-15)',
          'CSS_distress': 'CSS Distress (3-15)', 'CSS_reassur': 'CSS Reassurance seeking (3-15)', 'n_tools': 'Number of tool types used', 'n_motives': 'Number of motives'}
for v, lab in scores.items():
    s[v] = d[v].astype(int); vlab[v] = lab; measure[v] = 'scale'
s['age_ord'] = d['age_ord'].astype(int); vlab['age_ord'] = 'Age group as ordinal number (1-6)'; measure['age_ord'] = 'ordinal'
s['chronic_text'] = d['chronic_text'].fillna('').astype(str).str.strip(); vlab['chronic_text'] = 'Chronic condition (free text, as written)'; measure['chronic_text'] = 'nominal'

order = (['id', 'date', 'age_group', 'age4', 'age_ord', 'gender', 'female', 'education', 'occupation', 'health_background', 'medical_student',
          'chronic', 'chronic_text', 'language', 'tool_search', 'tool_ai', 'ai_user', 'ai_model_inconsistent', 'tool_medplat', 'tool_social',
          'n_tools', 'tool_profile', 'ai_model', 'mot_convenience', 'mot_triage', 'mot_reassurance', 'mot_selfdx', 'mot_cost', 'n_motives', 'trust']
         + [f'shai{k}' for k in range(1, 15)] + [f'css{k}' for k in range(1, 13)]
         + ['SHAI', 'HA_elevated', 'CSS', 'CSS_excess', 'CSS_compul', 'CSS_distress', 'CSS_reassur', 'CSS_high',
            'beh_delay_reassured', 'beh_ignore', 'beh_multidoc', 'beh_urgent', 'beh_selfmed', 'beh_delay_terrified',
            'share', 'share_never', 'relationship', 'rel_negative'])
s = s[order]
pyreadstat.write_sav(s, f'{OUT}/Cyberchondria_Baghdad.sav', column_labels=[vlab[c] for c in order],
                     variable_value_labels=vals, variable_measure=measure,
                     variable_display_width={'chronic_text': 30}, file_label='Cyberchondria Baghdad 2026 - cleaned and scored (n=300)')
# codebook
cb = pd.DataFrame({'Variable': order, 'Label': [vlab[c] for c in order], 'Measure': [measure[c] for c in order],
                   'Values': ['; '.join(f'{k} = {v}' for k, v in vals[c].items()) if c in vals else '' for c in order]})
cb.to_csv(f'{OUT}/Codebook.csv', index=False, encoding='utf-8-sig')
# round-trip check
back, meta = pyreadstat.read_sav(f'{OUT}/Cyberchondria_Baghdad.sav')
assert back.shape == s.shape and (back['SHAI'] == s['SHAI']).all() and (back['CSS'] == s['CSS']).all()
print('wrote', f'{OUT}/Cyberchondria_Baghdad.sav', back.shape, '| labelled vars:', len(meta.variable_value_labels))
