"""Student 2: the Results part explained from zero (statistics lessons with our own numbers, why each table and
figure was chosen, how to read it, what to say, slide-by-slide pointing guide, drills and a cheat sheet).
Usage: python3 13_student2_from_zero.py <output dir> <out.html>"""
import sys, json, html
import numpy as np, pandas as pd

OUT, HTML = sys.argv[1], sys.argv[2]
import os
SHORT = os.environ.get('THESIS') == 'short'
N = json.load(open(f'{OUT}/study/numbers.json')); FIG = N['figdir']
X = pd.read_excel(f'{OUT}/tables/all_results.xlsx', sheet_name=None, index_col=0)
d = pd.read_pickle(f'{OUT}/analysed.pkl')
INV = pd.read_csv(f'{OUT}/tables/invariance_mgcfa.csv')
e = html.escape
f2 = lambda x: f'{x:.2f}'

# ---------------------------------------------------------------- numbers pulled from the result tables
med = X['T21_mediation']
def mrow(prefix, path): return med[med.Model.str.startswith(prefix) & (med.Path == path)].iloc[0]
A_a, A_b, A_t, A_d, A_i = [mrow('A:', p).coef for p in ['CSS_excess ~ X', 'b (M -> Y | X)', 'Total', 'Direct', 'Indirect']]
C_a, C_b, C_t, C_d, C_i = [mrow('C:', p).coef for p in ['CSS_distress ~ X', 'b (M -> Y | X)', 'Total', 'Direct', 'Indirect']]
lg = X['T18_logit_HA_clin']
beh = X['T19_logit_behaviours']
def bh(o, p): return beh[(beh.Outcome == o) & (beh.Predictor == p)].iloc[0]
chron_y, chron_n = d.loc[d.chronic == 1, 'SHAI'].mean(), d.loc[d.chronic == 0, 'SHAI'].mean()
reas_y, reas_n = d.loc[d.mot_reassurance == 1, 'SHAI'].mean(), d.loc[d.mot_reassurance == 0, 'SHAI'].mean()
ai_y, ai_n = d.loc[d.ai_user == 1, 'CSS'].mean(), d.loc[d.ai_user == 0, 'CSS'].mean()
css_sd = d.CSS.std()

CSS = """
@page { size: A4; margin: 15mm 14mm 15mm 14mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, Carlito, Arial, sans-serif; font-size: 11pt; color: #222; line-height: 1.45; margin: 0; }
h1 { font-family: Cambria, Caladea, Georgia, serif; color: #0B5394; font-size: 25pt; margin: 0 0 4px; }
h2 { font-family: Cambria, Caladea, Georgia, serif; color: #0B5394; font-size: 16pt; margin: 16px 0 6px; padding-bottom: 3px; border-bottom: 2px solid #0B5394; page-break-after: avoid; }
h3 { color: #B45F06; font-size: 12.5pt; margin: 13px 0 4px; page-break-after: avoid; }
p { margin: 3px 0 6px; } ul, ol { margin: 3px 0 7px; padding-left: 20px; } li { margin: 2px 0; }
.page { page-break-before: always; }
.lesson { border: 1px solid #c9d3e0; border-radius: 6px; padding: 7px 11px; margin: 9px 0; page-break-inside: avoid; }
.lesson .t { font-weight: bold; color: #0B5394; font-size: 12pt; }
.say { border-left: 5px solid #1E5B4F; background: #EEF6F3; padding: 5px 10px; margin: 6px 0; font-style: italic; page-break-inside: avoid; }
.say:before { content: "Say: "; font-style: normal; font-weight: bold; color: #1E5B4F; }
.why { border-left: 5px solid #B45F06; background: #FFF7ED; padding: 5px 10px; margin: 6px 0; page-break-inside: avoid; }
.why:before { content: "Why this was chosen: "; font-weight: bold; color: #B45F06; }
.trap { border-left: 5px solid #7F1D3A; background: #FBF1F4; padding: 5px 10px; margin: 6px 0; page-break-inside: avoid; }
.trap:before { content: "Trap: "; font-weight: bold; color: #7F1D3A; }
.ex { background: #F4F6FA; padding: 5px 10px; margin: 5px 0; font-family: Consolas, 'DejaVu Sans Mono', monospace; font-size: 10pt; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 5px 0 9px; font-size: 10pt; } tr { page-break-inside: avoid; }
th { background: #DCE4F0; text-align: left; } th, td { border: 1px solid #c8cfd8; padding: 3px 6px; vertical-align: top; }
img.fig { display: block; max-width: 100%; max-height: 300px; margin: 6px auto; border: 1px solid #ddd; }
.num { font-weight: bold; color: #B45F06; } .small { font-size: 9.5pt; color: #555; }
.card { border: 1px solid #c9d3e0; border-radius: 6px; padding: 8px 11px; margin: 10px 0; }
.card .hd { font-weight: bold; color: #fff; background: #0B5394; margin: -8px -11px 6px; padding: 4px 11px; border-radius: 6px 6px 0 0; font-size: 12pt; }
"""
H = []; w = H.append
def lesson(title, body): w(f'<div class="lesson"><div class="t">{title}</div>{body}</div>')
def say(t): return f'<div class="say">{t}</div>'
def why(t): return f'<div class="why">{t}</div>'
def trap(t): return f'<div class="trap">{t}</div>'
def ex(t): return f'<div class="ex">{t}</div>'
def img(f): return f'<img class="fig" src="file://{FIG}/{f}">'
def table(head, rows): return '<table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table>'
def card(title, parts): w(f'<div class="card"><div class="hd">{title}</div>{"".join(parts)}</div>')

w(f'<!doctype html><html><head><meta charset="utf-8"><title>Results From Zero</title><style>{CSS}</style></head><body>')

# ================================================================ cover
w(f'''<h1>Your Results, From Zero</h1>
<p style="font-size:12.5pt;color:#555">For Student 2 · everything explained step by step, with our own numbers</p>
<p>You do not need to be good at statistics to present the Results. You need to understand <b>one idea per table or figure</b>
and be able to say it simply. This guide teaches you exactly that.</p>
<h3>How to use this guide (3 sittings)</h3>
<ol><li><b>Sitting 1 (1.5 h):</b> Part A (the story of the results) and Part B (statistics lessons). Read slowly. Say every "Say" box out loud.</li>
<li><b>Sitting 2 (2 h):</b> Part C (why each table and figure exists, how to read it). Have the thesis open next to you.</li>
<li><b>Sitting 3 (1.5 h):</b> Part D (your slides: what to point at), Part E (drills). Then do the drills again the next day without looking.</li></ol>
<p>Keep the one-page cheat sheet (last page) in your pocket for the week before the defence.</p>''')

# ================================================================ PART A story
w('<h2 class="page">Part A · The Results tell one story in nine steps</h2>')
w('<p>Every table and figure in Chapter 3 answers one question. They come in a logical order: first <b>who</b> answered, then <b>what they do</b>, then <b>how anxious</b> they are, then the <b>main link</b>, then <b>what else</b> could explain it, then <b>who is at risk</b>, then <b>behaviour</b>, then <b>pathways</b>, and finally <b>is it robust?</b></p>')
w(table(['Step', 'Question', 'Short answer', 'Where', 'Slide'], [
    ['1', 'Who took part?', f'{N["n"]} young, educated adults; {N["med"]} medical students', 'Table 1', '14'],
    ['2', 'How do they search?', f'AI chatbots first ({N["ai_tick"]}), search engines second ({N["se"]})', 'Table 2, Figure 3', '15'],
    ['3', 'What do they do after searching?', f'{N["dr"]} delay care when reassured; {N["never"]} never tell the doctor', 'Figure 4', '22'],
    ['4', 'How anxious are they? Do the scales work?', f'{N["hac"]} elevated; both scales reliable; CSS-12 same in Arabic and English', 'Tables 3, 4, 5', '16'],
    ['5', 'Are health anxiety and cyberchondria linked? (H1)', f'Yes, r = {N["r"]}', 'Table 6, Figures 5, 6, 11', '17, 19'],
    ['6', 'Which groups score higher?', 'Chronic illness, reassurance seekers; AI users (but see step 7)', 'Tables 7, 8, Figure 7', '–'],
    ['7', 'Does the link survive other factors? (H2) Who is at risk?', f'Yes; health anxiety adds {N["dR2"]}; AI effect not robust', 'Tables 9, 10, Figure 8', '18, 20, 23'],
    ['8', 'Does it affect behaviour? (H4)', 'Cyberchondria → more disclosure (robust); others exploratory', 'Table 11', '22'],
    ['9', 'Is there a cycle? (H3) Is everything robust?', 'Compatible with a cycle, not proven; all checks unchanged', 'Table 12, Figures 9, 10, Table 13', '21'],
]))
w(say(f'Our results answer nine questions in order. In short: AI chatbots are the main source of health information, one in five has elevated health anxiety, and health anxiety and cyberchondria are clearly linked, r = {N["r"]}, even after adjusting for everything else.'))

# ================================================================ PART B lessons
w('<h2 class="page">Part B · Statistics from zero (with our numbers)</h2><p>Each lesson: the idea in plain words, our example, and what to say. Read them in order; each one builds on the one before.</p>')
lesson('1. Variables: two kinds', '<ul><li><b>Categorical</b> = groups (gender, uses AI yes/no, tool profile). We describe them with <b>n and %</b>.</li><li><b>Continuous</b> = scores on a scale (SHAI 0–42, CSS 12–60). We describe them with <b>mean, SD, median</b>.</li></ul><p>This one fact decides almost every choice of test and chart in the thesis.</p>')
lesson('2. Mean and SD', f'<p><b>Mean</b> = the average. <b>SD (standard deviation)</b> = how spread out people are around the average. About two-thirds of people lie within 1 SD of the mean.</p>{ex(f"SHAI mean {N['shai_m']} ± SD {N['shai_sd']}  → most people scored between about 6.5 and 18")}{say(f"The average health-anxiety score was {N['shai_m']} out of 42.")}')
lesson('3. Median and IQR', f'<p>The <b>median</b> is the middle person. The <b>IQR</b> is the range of the middle half. We use them when scores are skewed (not a symmetrical bell shape).</p>{ex("SHAI median 12 (IQR 8–16): half of people scored 8 to 16")}')
lesson('4. Normal distribution and why it matters', f'<p>Many tests assume scores form a bell curve. The <b>Shapiro–Wilk test</b> checks this. Our scores were slightly skewed (p &lt; 0.01), so we used <b>non-parametric</b> tests (they do not need the bell shape) and <b>robust</b> regression.</p>{say("Our scores were not perfectly normal, so we used tests that do not assume normality.")}')
lesson('5. p-value', f'<p>Imagine there is truly <b>no</b> link. The p-value is the chance of seeing a result as strong as ours just by luck. Small p (below 0.05) = "unlikely to be luck" = <b>significant</b>. It does <b>not</b> say how big or important the effect is.</p>{ex("r = 0.47, p < 0.001 → almost impossible to get this by chance if there were no link")}{trap("p tells you if an effect exists, not how big it is. For size, look at r, β, OR.")}')
lesson('6. 95% confidence interval (CI)', f'<p>Our number is an estimate from 300 people. The CI is the range where the true value probably lies. Narrow CI = precise. If a CI for an odds ratio includes 1, the result is not significant.</p>{ex(f"r = {N['r']}, 95% CI {N['rci']} → the true correlation is probably between 0.38 and 0.55: always clearly above zero")}')
lesson('7. Correlation r', f'<p>How closely two scores move together: 0 = no link, 0.1 small, 0.3 moderate, 0.5 large, 1 = perfect. Positive = both go up together.</p>{ex(f"r = {N['r']}: people with more health anxiety tend to have more cyberchondria. r² = {N['r2']}: health anxiety explains about a fifth of the differences in cyberchondria.")}{say(f"Health anxiety and cyberchondria rise together: r = {N['r']}, a moderate link.")}')
lesson('8. Pearson vs Spearman', '<p><b>Pearson r</b> assumes a straight-line link; <b>Spearman ρ</b> uses ranks and does not need normal data. We report both; both were 0.47, so the result does not depend on the method.</p>')
lesson('9. Partial correlation', f'<p>The same correlation after "removing" other variables (age, gender, background, chronic disease, trust, AI use). If it stays the same, those variables are not the explanation.</p>{ex(f"r = {N['r']} → partial r = {N['pr']}: unchanged")}{say("The link stayed the same after adjusting for everything else, so it is not explained by age, gender or background.")}')
lesson('10. Comparing groups: Mann–Whitney and Kruskal–Wallis', f'<p>To compare a <b>score</b> between groups without assuming normality: <b>Mann–Whitney U</b> for 2 groups, <b>Kruskal–Wallis H</b> for 3 or more.</p>{ex(f"Chronic condition: SHAI {chron_y:.1f} vs {chron_n:.1f} → Mann–Whitney p = 0.004")}')
lesson('11. Chi-square (χ²)', '<p>To test if two <b>categorical</b> variables are related, e.g. "elevated health anxiety yes/no" and "uses social media yes/no". It compares the counts we saw with the counts we would expect if there were no link.</p>')
lesson('12. Many tests → FDR correction (q-value)', f'<p>If you run 162 tests at p &lt; 0.05, about 8 will be "significant" by pure luck (162 × 0.05 ≈ 8). The <b>Benjamini–Hochberg FDR</b> correction adjusts p-values into <b>q-values</b>. q &lt; 0.05 = <b>robust</b>; p &lt; 0.05 but q ≥ 0.05 = <b>exploratory</b> (could be luck).</p>{ex(f"Never disclosing: CSS q = {N['nsCq']} (robust) · SHAI q = {N['nsSq']} (exploratory)")}{say("Because we ran many tests, we corrected for multiple testing; results that did not survive are called exploratory.")}')
lesson('13. Linear regression, B and β', f'<p>Regression predicts a score (CSS) from several factors at the same time, so each factor is "adjusted" for the others. <b>B</b> = how many CSS points change per 1 unit of the factor. <b>β</b> = the same on a common scale, so you can compare factors (bigger β = stronger).</p>{ex(f"SHAI: B = {N['B']}, β = {N['beta']}. Someone with SHAI 20 vs 10 → about 6.8 CSS points higher.")}{say(f"Each extra point of health anxiety adds about 0.7 points of cyberchondria; it is by far the strongest factor.")}')
lesson('14. R², ΔR² and hierarchical regression', f'<p><b>R²</b> = share of differences the model explains (0–1). In <b>hierarchical</b> regression we add groups of variables in steps and see how much each step adds (<b>ΔR²</b>).</p>{ex(f"Step 1 demographics R² {N['R2a']} (3%) → step 2 digital use {N['R2b']} (13%) → step 3 health anxiety {N['R2c']} (32%). Health anxiety adds {N['dR2']}.")}{why("Hierarchical order shows that health anxiety matters even after everything else is already in the model.")}')
lesson('15. Robust standard errors (HC3)', '<p>Regression assumes the "errors" are equally spread. Ours were not (Breusch–Pagan p = 0.004). HC3 robust standard errors fix the p-values and CIs so they are still valid. You only need: "we used robust standard errors because the residuals were uneven".</p>')
lesson('16. Odds and odds ratios (logistic regression)', f'<p><b>Logistic regression</b> predicts a yes/no outcome (elevated health anxiety yes/no). It gives <b>odds ratios (OR)</b>: OR 1 = no effect, above 1 = higher odds, below 1 = lower odds. <b>Adjusted</b> OR (AOR) = after accounting for the other factors.</p>{ex("Worked example from our data:<br>With elevated health anxiety: 52.6% had high cyberchondria → odds = 52.6/47.4 = 1.11<br>Without: 23.0% → odds = 23.0/77.0 = 0.30<br>Odds ratio = 1.11 / 0.30 ≈ 3.7")}<p>In the model: AOR <span class="num">{N["orCSS"]}</span> per <b>1 SD</b> of cyberchondria (1 SD ≈ {css_sd:.1f} CSS points) means about three times the odds for every 8 extra points.</p>{trap("AOR below 1 means protective. Age AOR 0.61: each older age group had lower odds.")}')
lesson('17. AUC', f'<p>How well the logistic model separates people with and without elevated health anxiety. Pick one person with and one without: AUC is the chance the model gives the higher risk to the right one. 0.5 = coin toss, 1 = perfect.</p>{ex(f"AUC {N['auc']}, and {N['aucc']} after correcting for optimism (bootstrap): good")}{why("A model always looks better on the data it was built on, so we corrected the AUC with 500 bootstrap repeats.")}')
lesson('18. Bootstrap', '<p>A computer trick: draw 5000 new samples of 300 people from our own data (with replacement), redo the analysis each time, and see how much the result varies. That gives a CI without assuming normality. We used it for mediation and to check the regression coefficient.</p>')
lesson('19. Mediation (indirect effect)', f'<p>Does part of the link from X to Y go <b>through</b> a middle variable M? Path <b>a</b> = X → M; path <b>b</b> = M → Y (adjusted for X); <b>indirect</b> = a × b; <b>direct</b> (c′) = what is left.</p>{ex(f"Model A: health anxiety → excessive searching → distress<br>a = {A_a:.2f}, b = {A_b:.2f} → indirect = {A_a:.2f} × {A_b:.2f} ≈ {A_i:.2f}<br>total = {A_t:.2f}, direct = {A_d:.2f} → about {A_i/A_t*100:.0f}% goes through excessive searching<br>Model C: health anxiety → distress → reassurance seeking: indirect {C_i:.2f}, direct {C_d:.2f} → almost all goes through distress")}{trap("Mediation in one survey is NOT proof of cause. The reverse order was also significant (0.15). Always say: compatible with a cycle, not proof.")}')
lesson('20. Moderation (interaction)', '<p>Does a third variable change the <b>strength</b> of the link? E.g. is the SHAI–CSS link stronger in AI users? We tested 7 moderators; none were significant after FDR. So the link is similar in everyone.</p>')
lesson('21. Reliability: Cronbach α and McDonald ω', f'<p>Do the items of a scale measure the same thing? 0.7 acceptable, 0.8 good, 0.9 excellent.</p>{ex(f"SHAI α {N['aS']}, CSS α {N['aC']}: good")}')
lesson('22. CFA and fit indices', f'<p><b>Confirmatory factor analysis</b> checks whether the items group into the factors the scale claims (CSS-12 = four facets). Fit indices: <b>CFI</b> near 0.95 or higher = good; <b>RMSEA</b> and <b>SRMR</b> 0.08 or lower = acceptable.</p>{ex(f"CSS-12 four factors: CFI {N['cfaC']}, RMSEA {N['cfaR']}, SRMR {N['srmr']} → acceptable · SHAI one factor: CFI 0.83 → poor (it has two factors)")}')
lesson('23. Measurement invariance', '<p>Before comparing Arabic and English answers, we must check the questionnaire works the same in both, like checking two rulers measure the same centimetre. Three steps: <b>configural</b> (same shape), <b>metric</b> (items equally strong), <b>scalar</b> (same starting points). If fit does not get worse at a step (CFI drop ≤ 0.01), that step passes.</p><p>CSS-12 passed all three. SHAI-14 passed the first two.</p>')
lesson('24. DIF', '<p>Differential item functioning: does a <b>single question</b> behave differently in Arabic vs English for people with the same total score? None did after FDR correction.</p>')
lesson('25. Sensitivity analysis', '<p>Re-doing the main analysis in another way (excluding doubtful responses, removing one item, another method) to see if the result changes. Ours did not change: r stayed 0.46–0.48.</p>')

# ================================================================ PART C why each table/figure
w('<h2 class="page">Part C · Every table and figure: why it is there and how to read it</h2>')
w('<h3>The rules that decided every choice</h3>')
w(table(['If the data are…', '…we used', 'Example'], [
    ['Exact numbers that people need to look up', 'a <b>table</b>', 'Table 1 participants, Table 9 regression'],
    ['A pattern people should see at a glance', 'a <b>figure</b>', 'Figure 5 scatter plot'],
    ['Percentages of groups (categorical)', '<b>bar chart</b>', 'Figures 3, 4'],
    ['Two continuous scores together', '<b>scatter plot</b>', 'Figure 5'],
    ['Many correlations at once', '<b>heatmap</b> (colour = strength)', 'Figures 6, 11'],
    ['A score compared across groups, skewed data', '<b>box plot</b> (median, spread, outliers)', 'Figure 7'],
    ['Means of several facets in two groups', '<b>bar chart with 95% CI</b>', 'Figure 10'],
    ['Many odds ratios with CIs', '<b>forest plot</b>', 'Figure 8'],
    ['Paths between variables', '<b>path diagram</b>', 'Figure 9'],
]))
w('<p>Also: the most important results get <b>both</b> a table (exact numbers) and a figure (the picture), e.g. the main correlation (Table 6 + Figure 5) and the logistic model (Table 10 + Figure 8). Less central results have only a table.</p>')

items = [
 ('Table 1 · Who took part', None, 'Every study must describe its sample first, so the reader knows who the results apply to. A table, because the reader needs exact n and %.',
  ['Rows = characteristics (age, gender, education, study/work, background, chronic disease, language).', 'Columns = n (number of people) and %.'],
  f'A young sample ({N["age20"]} aged 20–29), {N["med"]} medical students, {N["hb"]} with a health background.',
  f'Our {N["n"]} participants were mostly young and educated; almost half were medical students. This matters when we interpret percentages.',
  'Why so many medical students? Answer: the link spread through our own networks first; we say percentages cannot be generalised.'),
 ('Table 2 + Figure 3 · How people search and why', 'fig2_tools_motives.png', 'Tools and motives are categories with multiple answers, so percentages are best shown as bars (Figure 3); Table 2 keeps every exact count.',
  ['Figure 3, panel A = tools; panel B = motives.', 'Each bar = % of all 300 who ticked that option.', 'Bars add up to more than 100% because people could tick several.'],
  f'AI chatbots {N["ai_tick"]} ticked ({N["ai"]} including those who named one) vs search engines {N["se"]}; convenience is the top motive.',
  f'AI chatbots are now the main gateway: {N["ai_tick"]} ticked them, compared with {N["se"]} for search engines.',
  'Why two AI numbers? 32 people named a chatbot but did not tick “AI”; we report both and test both.'),
 ('Figure 4 · What people do after searching', 'fig3_behaviours.png', 'Three related sets of categories (behaviour, disclosure, relationship) shown side by side so the committee sees the whole consultation story in one picture.',
  ['Panel A: behaviours after searching (multiple answers).', 'Panel B: do they tell the doctor? (always / sometimes / never).', 'Panel C: effect on the relationship with doctors.'],
  f'{N["dr"]} delay care when reassured; {N["never"]} never tell the doctor; {N["relneg"]} say trust was strained.',
  'Searching changes the consultation: one in three delays care because they feel reassured, and almost one in three never tells the doctor.', ''),
 ('Table 3 · Scores and reliability', None, 'Before using any score, we must show the scales work (reliability) and give their levels. A table because these are exact values.',
  ['Rows: SHAI, CSS and the four CSS facets.', 'Columns: mean ± SD, median (IQR), range, α (95% CI), ω.', 'The note under the table has the CFA fit.'],
  f'Both scales reliable (α {N["aS"]} and {N["aC"]}); excessiveness is the highest facet, compulsion the lowest.',
  'Both questionnaires were reliable. People search a lot, but it rarely disrupts their daily life.', ''),
 ('Table 4 · Prevalence at different cut-offs', None, 'The % with “elevated” health anxiety depends on the cut-off you choose. Showing four cut-offs is honest and stops the committee from accusing us of choosing the one that looks best.',
  ['Each row = a cut-off (15, 18, 22, 29).', 'Columns: n, %, 95% CI.', 'Bold row = 18, the one we use.'],
  '32.7% at 15, 19.0% at 18, 7.3% at 22, 0.7% at 29.', 'About one in five scored 18 or more; this is a screening threshold, not a diagnosis, and the table shows how the estimate changes with the cut-off.',
  'Why 18? It best separated people with health anxiety from healthy controls in the Swedish study.'),
 ('Table 5 · Arabic vs English (measurement invariance)', None, 'We combined Arabic and English answers. To do that fairly, we had to prove the questionnaire works the same in both languages.',
  ['Two blocks: CSS-12 and SHAI-14.', 'Three rows each: configural, metric, scalar.', 'Look at ΔCFI and the Decision column: “Supported” = that step passed.'],
  'CSS-12 passed all steps; SHAI-14 passed metric, not scalar; no item behaved differently.', 'The cyberchondria questionnaire works identically in Arabic and English, so combining the two languages was justified.', ''),
 ('Table 6 + Figure 5 · The main result', 'fig1_scatter_shai_css.png', 'This answers our main question (H1), so it gets both: a figure to see the pattern, a table for exact numbers. A scatter plot is the standard picture for two continuous scores.',
  ['Each dot = one participant (x = SHAI, y = CSS).', 'The red line = best-fit line; the shaded band = its 95% CI.', 'The dotted vertical line = SHAI 18 cut-off.', 'Table 6: r for the total and for each facet, plus adjusted β.'],
  f'Clear upward trend: r = {N["r"]}; strongest for excessiveness ({N["rE"]}) and distress ({N["rD"]}).',
  f'This is our main result: the more health anxiety, the more cyberchondria, r = {N["r"]}, and it holds after adjustment.',
  'Point at the line going up, then at the r value in the box. Do not say “causes”.'),
 ('Figure 6 · Correlation heatmap', 'fig4_corr_heatmap.png', 'We had 10 variables. Writing 45 correlations in text is unreadable; a heatmap shows them all at once, with colour for strength.',
  ['Each square = correlation between the row and column variable.', 'Darker red = stronger positive; blue = negative.', 'Stars = significant after FDR (* q<0.05, ** q<0.01, *** q<0.001).'],
  'Health anxiety correlates with every cyberchondria facet; trust relates only to excessiveness; age is slightly negative.', 'The heatmap shows all relationships at once: health anxiety is linked with every part of cyberchondria.', ''),
 ('Table 7 + Figure 7 · Which groups score higher', 'fig6_css_by_tool.png', 'Table 7 compares the scores across every participant group (exact means and p/q). Figure 7 is a box plot because CSS is skewed: it shows the median and spread, not just the mean.',
  ['Box plot: middle line = median; box = middle half of people; whiskers = range; dots = outliers.', 'Three groups: no AI, AI only, AI + search engine.'],
  f'Health anxiety higher with chronic illness ({chron_y:.1f} vs {chron_n:.1f}) and in reassurance seekers ({reas_y:.1f} vs {reas_n:.1f}); CSS higher in AI users ({ai_y:.1f} vs {ai_n:.1f}), highest in AI + search engine users.',
  'People who combine AI with search engines had the highest cyberchondria, but we will see this is not robust once we adjust.', 'Do not over-sell the AI difference; it disappears in the strict analysis.'),
 ('Table 8 · Yes/no outcomes (χ²)', None, 'Some outcomes are yes/no (elevated health anxiety, high cyberchondria). χ² tests show which categories go with them. Only significant ones are listed to keep it short.',
  ['Each row: variable, % with the outcome in each group, Cramér\'s V (strength), p, q.'],
  'With elevated health anxiety, 52.6% had high cyberchondria vs 23.0% without (OR ≈ 3.7).', 'People with elevated health anxiety were much more likely to have high cyberchondria.', ''),
 ('Table 9 · What predicts cyberchondria (regression)', None, 'Group comparisons look at one factor at a time; regression tests all factors together, so we know which matter independently (H2).',
  ['Rows = predictors; B = CSS points per unit; β = comparable strength; p.', 'Note under the table = R² for each step.'],
  f'Health anxiety β {N["beta"]} (largest by far); R² rises from {N["R2a"]} to {N["R2c"]}.', f'Demographics explain only 3%; adding health anxiety explains a further {N["dR2"]}. Health anxiety is by far the strongest predictor.',
  'AI row: significant here, but not with the strict definition (slide 23).'),
 ('Table 10 + Figure 8 · Who has elevated health anxiety', 'fig7_forest_HA.png', 'For a yes/no outcome we use logistic regression; a forest plot is the standard way to show many odds ratios with CIs at once.',
  ['Each dot = AOR; the line = its 95% CI.', 'Vertical line at 1 = no effect. If the line crosses 1 → not significant.', 'Log scale: 0.5 and 2 are the same distance from 1.', 'Orange = significant.'],
  f'Cyberchondria AOR {N["orCSS"]}, reassurance motive {N["orMot"]}, age {N["orAge"]} (protective); AUC {N["auc"]} → {N["aucc"]}.',
  'Three factors stand out: higher cyberchondria, searching for reassurance, and younger age.', 'Only 57 events, so the reassurance odds ratio has a wide CI; say “exploratory”.'),
 ('Table 11 · Behaviour models', None, 'To test H4 we need adjusted models for each behaviour. A table because there are 8 outcomes × 2 scores: too many for a chart.',
  ['Each row = a behaviour; columns = AOR (95% CI) and p for SHAI and for CSS.'],
  f'Higher CSS → urgent visits (AOR {N["urC"]}), less ignoring ({N["igC"]}), less never-disclosing ({N["nsC"]}, the only robust one).',
  'Cyberchondria, not health anxiety, is what goes with behaviour; only the link with disclosure survived correction.', ''),
 ('Table 12 + Figure 9 · Pathways (mediation)', 'fig8_mediation.png', 'To test H3 (the cycle). A path diagram is the clearest way to show a, b and direct paths; the table adds the CIs and the reverse model.',
  ['Boxes = variables; arrows = paths with coefficients.', 'a = X → M, b = M → Y, c′ = direct.', 'Below each diagram: the indirect effect with its CI.'],
  f'Via excessive searching {A_i:.2f}; via distress {C_i:.2f} (direct falls to {C_d:.2f}); reverse also 0.15.', 'The pattern fits a cycle, but because the reverse direction also fits, we cannot say which comes first.',
  'Never say “proves”.'),
 ('Figure 10 · Facets by health-anxiety group', 'fig5_subscales_by_HA.png', 'Shows simply that people with elevated health anxiety score higher on every facet, and which facets differ most. Bars with 95% CI are best for comparing means of two groups.',
  ['Blue = SHAI < 18 (243 people); orange = SHAI ≥ 18 (57 people).', 'Bar height = mean; small lines = 95% CI.'],
  'Biggest gaps: excessiveness (9.2 vs 11.6) and distress (6.8 vs 9.2).', 'People with elevated health anxiety score higher on every part of cyberchondria, most of all on excessive searching and distress.', ''),
 ('Figure 11 (Appendix) · Item by item', 'fig9_item_by_item.png', 'To see which exact questions drive the link (168 pairs). Only a heatmap can show 168 numbers readably, so it goes in the appendix.',
  ['Rows = 14 SHAI items; columns = 12 CSS items.', 'Colour = strength; stars = significant after FDR (**: also after the stricter Holm correction).'],
  f'{N["ibF"]}/168 pairs significant; strongest: fear of serious illness ↔ panic on reading of a rare condition (0.43). Noticing aches is almost unrelated.',
  'What drives searching is fear and interpretation, not simply noticing symptoms.', ''),
 ('Table 13 · Sensitivity analyses', None, 'Committees always ask “is it robust?”. One table answers all such questions at once.',
  ['Each row = a check; Result; Conclusion column.'], 'r stays 0.46–0.48 whatever we exclude; only the AI effect depended on a decision.', 'Every check left the main result unchanged.', ''),
]
if SHORT:   # items that exist only in the long version
    items = [it for it in items if not it[0].startswith(('Table 5 ·', 'Figure 6 ·', 'Table 13 ·'))]
    items = [(('Supplementary figure · Item by item (slide 19 only)',) + it[1:]) if it[0].startswith('Figure 11') else it for it in items]
for title, fig, whytxt, howto, shows, saytxt, traptxt in items:
    parts = [why(whytxt)]
    if fig: parts.append(img(fig))
    parts.append('<p><b>How to read it:</b></p><ol>' + ''.join(f'<li>{x}</li>' for x in howto) + '</ol>')
    parts.append(f'<p><b>What it shows:</b> {shows}</p>')
    parts.append(say(saytxt))
    if traptxt: parts.append(trap(traptxt))
    card(title, parts)

# ================================================================ PART D slides
w('<h2 class="page">Part D · Your 11 slides: what to point at and what to say</h2>')
w('<p>Short versions (three sentences each). The full scripts are in the speaker notes and in your Student 2 guide. Aim for 30–35 seconds per slide.</p>')
sl = [
 ('13 · Results divider', 'Nothing to point at.', 'Thank you. I will present our results in six steps: who took part, how they search, the levels of health anxiety and cyberchondria, the main association, the predictors and pathways, and behaviour and AI.'),
 ('14 · Participants (Table 1)', 'The highlighted rows: gender and medical students.', f'Table 1 shows our {N["n"]} participants. Most were young, {N["age20"]} aged 20 to 29, and {N["med"]} were medical students. In summary, a young and educated sample, which we keep in mind when reading percentages.'),
 ('15 · How people search (Figure 3)', 'The top bar of panel A (AI chatbots), then the four number boxes.', f'Figure 3 shows the tools people use. AI chatbots come first, {N["ai_tick"]}, ahead of search engines at {N["se"]}, and ChatGPT alone is used by {N["gpt"]}. In summary, for many people the first “doctor” is now an AI chatbot.'),
 ('16 · Levels & reliability (Table 3)', 'The first two rows, then the 19% box.', f'Table 3 shows the scores. {N["hac"]} scored in the elevated range of health anxiety, and both questionnaires were reliable, with alpha {N["aS"]} and {N["aC"]}. In summary, our tools measured well, in both Arabic and English.'),
 ('17 · Main result (Figure 5)', 'The rising line, then the r box.', f'This is our main result. Health anxiety and cyberchondria rise together, r = {N["r"]}, and the link stays {N["pr"]} after adjusting for everything else. In summary, hypotheses 1 and 2 are supported.'),
 ('18 · What predicts cyberchondria (Table 9)', 'The R² rows, then the 18.4% box.', f'Table 9 is our regression. Demographics explain only 3% of cyberchondria, but health anxiety adds another {N["dR2"]}. In summary, how anxious you are matters far more than who you are.'),
 ('19 · Item by item (Figure 11)', 'The 0.43 and 0.42 boxes, then the “≈ 0” box.', f'Figure 11 looks at every pair of questions. The strongest links are fear of serious illness and interpreting body sensations; simply noticing aches is almost unrelated. In summary, fear drives searching, not noticing.'),
 ('20 · Who has elevated health anxiety (Figure 8)', 'The orange dots, then the four boxes.', f'Figure 8 shows the odds ratios. Higher cyberchondria triples the odds, searching for reassurance nearly quadruples them, and older age is protective; the model\'s AUC is {N["aucc"]} after correction. In summary, the person most at risk is young and searches for reassurance.'),
 ('21 · Pathways (Figure 9)', 'Panel A indirect effect, then panel B direct effect, then the orange box.', f'Figure 9 shows the pathways. Part of the link runs through excessive searching ({N["mA"]}), and almost all of the link to reassurance seeking runs through distress. In summary, this is compatible with a cycle, but one survey cannot prove the direction.'),
 ('22 · Behaviour (Figure 4)', 'The first bar of panel A, then the four boxes.', f'Figure 4 shows what people do after searching: {N["dr"]} delay care because they feel reassured, and {N["never"]} never tell their doctor. Higher cyberchondria goes with more disclosure, and that result survived correction. In summary, searching changes the consultation before it begins.'),
 ('23 · AI chatbots', 'The table: inclusive vs strict rows.', f'Finally, AI. AI users scored {N["Bai"]} points higher, but with the strict definition the difference was only {N["Balt"]} and not significant, p = {N["palt"]}. In summary, there is no reliable independent effect of AI. I now hand over to my colleague.'),
]
w(table(['Slide', 'Point at', 'Say (short version)'], [[a, b, c] for a, b, c in sl]))

# ================================================================ PART E drills
w('<h2 class="page">Part E · Drills: explain it like you would to a 12-year-old</h2><p>Cover the right column. Answer out loud in one or two sentences. Then check.</p>')
w(table(['Explain…', 'Model answer'], [
    ['What is a p-value?', 'The chance of getting a result this strong by luck if there were really no effect. Below 0.05 we call it significant.'],
    ['What does r = 0.47 mean?', 'When health anxiety goes up, cyberchondria tends to go up too; a moderate link, explaining about a fifth of the differences.'],
    ['What is a confidence interval?', 'The range where the true value probably lies. Ours for r is 0.38 to 0.55.'],
    ['Why did you correct for multiple tests?', 'With 162 tests, about 8 would be significant just by luck; FDR correction separates real results from probable luck.'],
    ['What is regression for?', 'To see which factors matter when we look at all of them together.'],
    ['What is β?', 'The strength of each factor on a common scale, so we can compare them. Health anxiety had the biggest, 0.48.'],
    ['What is an odds ratio of 3?', 'The odds are three times higher. Below 1 means lower odds.'],
    ['What is AUC?', 'How well our model tells anxious from non-anxious people apart: 0.79 is good.'],
    ['What is mediation?', 'Checking whether part of a link passes through a middle step, here searching or distress.'],
    ['Does mediation prove a cycle?', 'No. The reverse also fits, and it is one survey at one time point.'],
    ['Why did the AI effect disappear?', 'It depended on 32 people who named a chatbot but did not tick the box; only 34 non-users. With the strict definition it was not significant.'],
    ['Why non-parametric tests?', 'Our scores were not perfectly normal; these tests do not need that.'],
    ['What is Cronbach\'s alpha?', 'Whether the questions of a scale measure the same thing; ours were 0.81 and 0.86, good.'],
    ['What is measurement invariance?', 'Checking the questionnaire measures the same thing in Arabic and English, like checking two rulers. The CSS-12 passed fully.'],
    ['What is a sensitivity analysis?', 'Doing the analysis in other ways to see if the result changes. It did not.'],
    ['Why both a table and a figure for some results?', 'The figure shows the pattern; the table gives the exact numbers. We did both for the most important results.'],
    ['Why a box plot for Figure 7?', 'Cyberchondria scores are skewed, so the median and spread are more honest than a bar of means.'],
    ['Why a forest plot for Figure 8?', 'It shows many odds ratios and their CIs at once; anything crossing 1 is not significant.'],
    ['Why a heatmap for Figure 6?', 'There are 45 correlations; colour lets you see them all at once.'],
    ['Why is Figure 11 in the appendix?', 'It has 168 numbers: important detail, but too much for the main chapter.'],
]))

# ================================================================ cheat sheet
w('<h2 class="page">Cheat sheet (one page)</h2>')
w(table(['What', 'Number', 'Where'], [
    ['Participants', f'{N["n"]}; {N["age20"]} aged 20–29; {N["med"]} medical students', 'Table 1'],
    ['AI chatbots / search engines', f'{N["ai_tick"]} ({N["ai"]} incl. named) / {N["se"]}; ChatGPT {N["gpt"]}', 'Figure 3'],
    ['Delay care when reassured / never tell the doctor', f'{N["dr"]} / {N["never"]}', 'Figure 4'],
    ['SHAI mean / CSS mean', f'{N["shai_m"]} / {N["css_m"]}', 'Table 3'],
    ['Reliability α', f'{N["aS"]} / {N["aC"]}', 'Table 3'],
    ['Elevated health anxiety', f'{N["hac"]} (CI {N["hac_ci"]}); 32.7 / 19.0 / 7.3 / 0.7% at 15/18/22/29', 'Table 4'],
    ['Invariance', 'CSS-12 scalar ✓; SHAI-14 metric ✓, scalar ✗; no DIF', 'Table 5'],
    ['Main correlation', f'r = {N["r"]} ({N["rci"]}); partial {N["pr"]}; r² {N["r2"]}', 'Table 6, Figure 5'],
    ['Facets', f'excess {N["rE"]}, distress {N["rD"]}, compulsion {N["rC"]}, reassurance {N["rR"]}', 'Table 6'],
    ['Regression R²', f'{N["R2a"]} → {N["R2b"]} → {N["R2c"]}; ΔR² {N["dR2"]}; β {N["beta"]}; B {N["B"]}', 'Table 9'],
    ['Logistic', f'AOR {N["orCSS"]} / {N["orMot"]} / {N["orAge"]}; AUC {N["auc"]} → {N["aucc"]}', 'Table 10, Figure 8'],
    ['Behaviour (robust)', f'CSS → never disclose AOR {N["nsC"]}, q {N["nsCq"]}', 'Table 11'],
    ['Mediation', f'via excess {N["mA"]} ({N["mAci"]}); via distress {N["mC"]}, direct {N["mCd"]}; reverse {N["mD"]}', 'Table 12, Figure 9'],
    ['AI effect', f'+{N["Bai"]} inclusive vs +{N["Balt"]} strict (p {N["palt"]}); 32 named-not-ticked; 34 non-users', 'Table 9, slide 23'],
    ['Item level', f'{N["ibF"]}/168 FDR; top ρ 0.43', 'Figure 11'],
    ['Robustness', 'r 0.46–0.48 in every check', 'Table 13'],
]))
w('<div class="say">Health anxiety and cyberchondria travel together, r = 0.47; AI chatbots are the main source but have no reliable independent effect; and searching changes the consultation before it begins.</div>')
w('</body></html>')
out = '\n'.join(H)
if SHORT:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from numbering import remap
    for a, b in [("19 · Item by item (Figure 11)", "19 · Item by item (supplementary figure)"),
                 ("Figure 11 looks at every pair of questions.", "This supplementary figure looks at every pair of questions."),
                 ("<tr><td>Why a heatmap for Figure 6?</td><td>There are 45 correlations; colour lets you see them all at once.</td></tr>", ""),
                 ("Why is Figure 11 in the appendix?", "Why is the item-by-item figure only on a slide, not in the thesis?"),
                 ("It has 168 numbers: important detail, but too much for the main chapter.", "It has 168 numbers: the thesis reports the key result in one sentence; the full figure is in the long version."),
                 ("Chapter 3 (Results)", "Chapter 3 (Results, 3.1–3.6)"),
                 ("<td>Figures 6, 11</td>", "<td>Table 6 (heatmaps are only in the long version)</td>")]:
        out = out.replace(a, b)
    out = remap(out)
open(HTML, 'w').write(out); print('wrote', HTML)
