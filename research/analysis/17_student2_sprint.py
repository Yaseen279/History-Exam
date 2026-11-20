"""Student 2 sprint guide: the Results part and the statistics, mastered in about 2.5 hours.
Written from scratch for the final short thesis (SPSS-level analysis). One phone page at a time, a Next button,
five timed blocks, a quiz after each block and a final flashcard round.
Usage: python3 17_student2_sprint.py <output dir> <out.html>"""
import sys, io, json, base64
from PIL import Image

OUT, HTML = sys.argv[1], sys.argv[2]
N = json.load(open(f'{OUT}/study/numbers.json')); S = json.load(open(f'{OUT}/simple.json'))
L = S['logit_HA']; M = {m['key']: m for m in S['mediation']}
B = {(b['Outcome'], b['Predictor']): b for b in S['behaviour']}
def b(o, p): return B[(o, p)]
f2 = lambda x: f'{x:.2f}'
def pv(p): return 'p < 0.001' if p < .001 else f'p = {p:.3f}'

def img(name, alt):
    im = Image.open(f'{OUT}/figures/{name}.png').convert('RGBA'); bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[3])
    w = 1300 if im.width / im.height > 2.2 else 1000
    if bg.width > w: bg = bg.resize((w, round(bg.height * w / bg.width)), Image.LANCZOS)
    bb = io.BytesIO(); bg.save(bb, 'JPEG', quality=72, optimize=True)
    return f'<img class="fig" tabindex="0" alt="{alt}" src="data:image/jpeg;base64,{base64.b64encode(bb.getvalue()).decode()}">'

def say(t): return f'<p class="say">{t}</p>'
def trap(t): return f'<p class="trap">{t}</p>'
def nums(rows): return '<div class="nums">' + ''.join(f'<div><b>{v}</b><span>{k}</span></div>' for k, v in rows) + '</div>'
def tbl(head, rows): return '<div class="tw"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'

BLOCKS = [('1', 'The study on one page', 20), ('2', 'Your Results, table by table', 45), ('3', 'The statistics you must explain', 35),
          ('4', 'Your slides 13–23', 25), ('5', 'Questions the committee will ask', 25)]
P = []   # (block, title, html)
def page(blk, title, html): P.append((blk, title, html))

# ---------------------------------------------------------------- 0 start
page('0', 'Can you master this in 2.5 hours?', f'''
<p><b>Yes, for your part.</b> You built the questionnaire and collected the data, so you already know the hardest thing: what every variable is and where it came from. This guide adds only what you still need: the key numbers, what each test does, what to say on your slides, and how to answer questions.</p>
{tbl(['Block', 'What', 'Time'], [[k, t, f'{m}&nbsp;min'] for k, t, m in BLOCKS])}
<p>Total about <b>2.5 hours</b>. Each block ends with a 5-question quiz. Then one full run of your slides out loud with a timer (about 6 minutes).</p>
<p class="tip"><b>Tomorrow:</b> 20 minutes on the flashcards and one more out-loud run. Sleep is what fixes the numbers in memory.</p>''')
page('0', 'How to use this', '''<ul><li>One page at a time: read it, then press <b>Next</b>.</li><li>Say every green <b>“Say it”</b> line out loud. Out loud is what makes it stick.</li>
<li>Red <b>“Trap”</b> lines are the mistakes examiners wait for.</li><li>The ☰ menu jumps to any block. Your place is saved on this phone.</li></ul>''')

# ---------------------------------------------------------------- 1 study on one page
page('1', 'What we studied', f'''<p><b>Question:</b> in adults in Baghdad, is health anxiety linked to cyberchondria, and how do online and AI searching shape what people do before seeing a doctor?</p>
<p><b>Design:</b> analytical cross-sectional online survey (your Google Form), Arabic and English, July–September 2026, convenience and snowball sampling, <b>n = {N["n"]}</b>, no missing data, one response per Google account.</p>
<p><b>Two scales you put in the form:</b></p><ul>
<li><b>SHAI-14</b> (health anxiety): 14 items scored 0–3, total 0–42. ≥ 18 = “elevated” (screening, not a diagnosis).</li>
<li><b>CSS-12</b> (cyberchondria): 12 items scored 1–5, total 12–60, four 3-item dimensions: excessiveness, compulsion, distress, reassurance seeking.</li></ul>
{say("We surveyed 300 adults in Baghdad online, using the SHAI-14 for health anxiety and the CSS-12 for cyberchondria.")}''')
page('1', 'The four hypotheses and the verdicts', tbl(['Hypothesis', 'Verdict'], [
    ['<b>H1</b> More health anxiety → more cyberchondria, most in distress and excessiveness', f'<b>Supported</b>: r = {N["r"]}; excessiveness {N["rE"]}, distress {N["rD"]}'],
    ['<b>H2</b> This holds after adjusting for other factors', f'<b>Supported</b>: partial r = {N["pr"]}; health anxiety adds {N["dR2"]} in regression'],
    ['<b>H3</b> Excessive searching carries part of the link to post-search distress', f'<b>Supported statistically, not causally</b>: Sobel z = {M["A"]["sobel_z"]:.2f}; the reverse order also fits'],
    ['<b>H4</b> Cyberchondria → urgent visits, multiple doctors, strained relationship', '<b>Partly supported</b>: urgent visits and strained relationship yes; multiple doctors no']]) +
    say('H1 and H2 were supported, H3 statistically but not causally, and H4 partly.'))
page('1', 'The twelve numbers to know by heart', nums([
    ('participants', N['n']), ('aged 20–29', N['age20']), ('medical students', N['med']), ('ticked AI chatbots', N['ai_tick']),
    ('used search engines', N['se']), ('elevated health anxiety', N['hac']), ('main correlation r', N['r']), ('added by health anxiety', N['dR2']),
    ('AOR per SD of cyberchondria', N['orCSS']), ('delay care when reassured', N['dr']), ('never tell the doctor', N['never']), ('AUC', f2(L['AUC']))]) +
    '<p class="small">If you remember only these twelve, you can answer most questions.</p>')
page('1', 'The whole result in four sentences', say(f'AI chatbots are now the main source of health information in our sample: {N["ai_tick"]} ticked them, more than search engines.') +
     say(f'About one in five ({N["hac"]}) had elevated health anxiety on a screening threshold.') +
     say(f'Health anxiety and cyberchondria are moderately linked, r = {N["r"]}, even after adjusting for everything else.') +
     say(f'Searching changes the consultation: {N["dr"]} delay care when reassured and {N["never"]} never tell their doctor; there is no reliable independent effect of AI.'))
page('1', 'Quiz 1', '<ol class="quiz">' + ''.join(f'<li><details><summary>{q}</summary><p>{a}</p></details></li>' for q, a in [
    ('What does SHAI-14 measure, and its range?', 'Health anxiety, 0–42; ≥ 18 = elevated'), ('CSS-12: range and four dimensions?', '12–60; excessiveness, compulsion, distress, reassurance seeking'),
    ('Main correlation?', f'r = {N["r"]} (95% CI {N["rci"]})'), ('Which hypothesis was only partly supported?', 'H4'), ('What % ticked AI chatbots?', N['ai_tick'])]) + '</ol>')

# ---------------------------------------------------------------- 2 results table by table
page('2', 'Your chapter at a glance', tbl(['Section', 'Tables / figures', 'One-line message'], [
    ['3.1 Participants and searching', 'Tables 1–2, Figures 2–3', 'Young sample; AI first; searching changes behaviour'],
    ['3.2 Levels', 'Tables 3–4', '19% elevated; both scales reliable'],
    ['3.3 Main association', 'Table 5, Figure 4', 'r = 0.47, strongest with excessiveness and distress'],
    ['3.4 Group differences', 'Tables 6–7, Figure 5', 'Reassurance seekers, chronic illness; AI users higher CSS'],
    ['3.5 Independent predictors', 'Tables 8–9, Figure 6', 'Health anxiety is by far the strongest predictor'],
    ['3.6 Behaviour and pathways', 'Tables 10–11, Figures 7–8', 'Cyberchondria, not anxiety, goes with behaviour']]))
page('2', 'Table 1 · Who answered', f'''<p>The sample (Table 1). You collected it, so you know why it looks like this: the link spread through your own networks first.</p>
{nums([('aged 20–29', N['age20']), ('female', N['fem']), ('medical students', N['med']), ('health background', N['hb']), ('chronic condition', N['chron']), ('answered in Arabic', N['ar'])])}
{say(f"Our {N['n']} participants were mostly young, and almost half were medical students, so percentages cannot be generalised to all of Baghdad.")}
{trap("Never say the sample represents Baghdad. Say “a young online convenience sample”.")}''')
page('2', 'Table 2 + Figure 2 · How they search', f'''{img('fig2_tools_motives', 'Tools and motives')}
{nums([('ticked AI chatbots', N['ai_tick']), ('incl. those who named one', N['ai']), ('search engines', N['se']), ('ChatGPT', N['gpt']), ('AI with no search engine', N['ai_only']), ('motive: convenience', N['conv'])])}
<p>Bars add to more than 100% because people could tick several (your Q8 and Q10 were multi-select).</p>
{trap(f"Two AI numbers: {N['inc']} people named a chatbot in Q9 but did not tick AI in Q8. We report both and test both.")}''')
page('2', 'Figure 3 · What they do after searching', f'''{img('fig3_behaviours', 'Behaviours after searching')}
{nums([('delay care, reassured', N['dr']), ('ignore the symptom', N['ign']), ('several doctors', N['mdoc']), ('urgent visit', N['urg']), ('always tell the doctor', N['always']), ('never tell (fear of judgement)', N['never'])])}
{say(f"Searching changes the consultation: one in three delays care because they feel reassured, and almost one in three never tells the doctor.")}''')
page('2', 'Tables 3–4 · Levels and reliability', f'''<p><b>SHAI</b> mean {N["shai_m"]} ± {N["shai_sd"]}; <b>CSS</b> mean {N["css_m"]} ± {N["css_sd"]}. Excessiveness was the highest dimension and compulsion the lowest: people search a lot, but it rarely disrupts their day.</p>
<p><b>Reliability</b> (Cronbach's α): SHAI {N["aS"]}, CSS {N["aC"]}: good (≥ 0.7 acceptable, ≥ 0.8 good). Arabic and English answers did not differ.</p>
{tbl(['SHAI-14 cut-off (Swedish study)', '% elevated'], [['≥ 18 (our definition)', f'<b>19.0%</b> (95% CI {N["hac_ci"]})'], ['≥ 22', '7.3%'], ['≥ 29', '0.7%']])}
{trap("19% is a screening result, not a diagnosis of illness anxiety disorder.")}''')
page('2', 'Table 5 + Figure 4 · THE main result', f'''{img('fig1_scatter_shai_css', 'Scatter plot of SHAI against CSS')}
<p>Each dot is one participant. The line goes up: more health anxiety, more cyberchondria.</p>
{nums([('Pearson r', N['r']), ('95% CI', N['rci']), ('Spearman ρ', N['rho']), ('variance explained', N['r2']), ('partial r (adjusted)', N['pr'])])}
<p>By dimension: excessiveness {N["rE"]}, distress {N["rD"]}, compulsion {N["rC"]}, reassurance {N["rR"]}.</p>
{say(f"Health anxiety and cyberchondria rise together, r = {N['r']}, and the link stays {N['pr']} after adjustment. Hypotheses 1 and 2 are supported.")}
{trap("Say “associated with”, never “causes”.")}''')
page('2', 'Tables 6–7 + Figure 5 · Which groups differ', f'''{img('fig6_css_by_tool', 'CSS by tool profile')}
<ul><li>Health anxiety higher with a <b>chronic condition</b> (p = 0.004) and in people searching for <b>instant reassurance</b> (p &lt; 0.001); also differed by age, education and occupation. Gender: no difference.</li>
<li>Cyberchondria higher in <b>AI users</b> (p &lt; 0.001), highest in those using AI <i>and</i> search engines (box plot above).</li>
<li>Elevated health anxiety → <b>52.6% vs 23.0%</b> had high cyberchondria (OR 3.71) (Table 7, χ²).</li></ul>
{trap("The AI difference here disappears in the strict analysis (Table 8). Do not oversell it.")}''')
page('2', 'Table 8 · What predicts cyberchondria', f'''<p>Hierarchical multiple linear regression: three blocks entered in order.</p>
{tbl(['Block', 'R²', 'Added'], [['1 · Demographics', N['R2a'], '3% (p = 0.53)'], ['2 · + Digital use', N['R2b'], '+10% (p &lt; 0.001)'], ['3 · + Health anxiety', N['R2c'], f'<b>+{N["dR2"]}</b> (p &lt; 0.001)']])}
<p>Health anxiety: <b>B = {N["B"]}, β = {N["beta"]}</b>, p &lt; 0.001: each SHAI point adds about 0.7 CSS points. Ages 30–39 and ≥ 40 also scored higher than 20–29.</p>
<p><b>AI:</b> +{N["Bai"]} points with the inclusive definition, but only +{N["Balt"]} (p = {S["ai_strict"]["p"]:.2f}) with the strict one → no reliable AI effect.</p>
{say(f"Who you are explains only 3%; how anxious you are adds another {N['dR2']}.")}''')
page('2', 'Table 9 + Figure 6 · Who has elevated health anxiety', f'''{img('fig7_forest_HA_simple', 'Forest plot of odds ratios')}
<p>Binary logistic regression. Dots = adjusted odds ratios; lines = 95% CI; crossing 1 = not significant; orange = significant.</p>
{nums([('per SD of cyberchondria', N['orCSS'] + '×'), ('searching for reassurance', N['orMot'] + '×'), ('per older age group', N['orAge'] + '×'), ('AUC', f2(L['AUC'])), ('Hosmer–Lemeshow p', f2(L['HL_p'])), ('correctly classified', f"{L['correct']:.0f}%")])}
{say("Higher cyberchondria triples the odds, searching for reassurance nearly quadruples them, and older age is protective.")}
{trap("Only 57 people had elevated health anxiety, so the odds ratios may be overestimated.")}''')
page('2', 'Table 10 · Behaviour', tbl(['Behaviour', 'Cyberchondria (per SD)', 'Health anxiety (per SD)'], [
    ['Urgent visit', f'<b>{b("Urgent visit/ER","zCSS")["AOR"]:.2f}</b> ({pv(b("Urgent visit/ER","zCSS")["p"])})', 'ns'],
    ['Ignore the symptom', f'<b>{b("Ignore symptom","zCSS")["AOR"]:.2f}</b> ({pv(b("Ignore symptom","zCSS")["p"])})', 'ns'],
    ['Never tell the doctor', f'<b>{b("Never disclose to physician","zCSS")["AOR"]:.2f}</b> ({pv(b("Never disclose to physician","zCSS")["p"])})', f'<b>{b("Never disclose to physician","zSHAI")["AOR"]:.2f}</b> ({pv(b("Never disclose to physician","zSHAI")["p"])})'],
    ['Strained relationship', f'<b>{b("Negative effect on doctor relationship","zCSS")["AOR"]:.2f}</b> ({pv(b("Negative effect on doctor relationship","zCSS")["p"])})', 'ns'],
    ['Several doctors, self-medication, delay', 'ns', 'ns']]) +
    f'<p>Trust in online/AI information → <b>fewer</b> multiple-doctor visits (AOR {b("Multiple doctors","trust")["AOR"]:.2f}, p = 0.004).</p>' +
    say('Cyberchondria, more than health anxiety, goes with behaviour: urgent visits, a strained relationship and more disclosure; health anxiety goes with hiding searches.') +
    trap('These are uncorrected p-values from many tests: say “associated”, and “may” for the weaker ones.'))
page('2', 'Table 11 + Figure 7 · Pathways', f'''{img('fig8_mediation_sobel', 'Mediation diagrams')}
<ul><li><b>A:</b> health anxiety → excessive searching → distress: indirect {M["A"]["indirect"]:.2f}, Sobel z = {M["A"]["sobel_z"]:.2f} (about a third of the link).</li>
<li><b>B:</b> health anxiety → distress → reassurance seeking: indirect {M["C"]["indirect"]:.2f}, z = {M["C"]["sobel_z"]:.2f}; direct effect falls to {M["C"]["c_prime"]:.2f} (almost all goes through distress).</li>
<li><b>Reverse</b> order also significant (indirect {M["D"]["indirect"]:.2f}, z = {M["D"]["sobel_z"]:.2f}).</li></ul>
{say("This fits a cycle, but because the reverse order also fits, one survey cannot show which comes first.")}''')
page('2', 'Figure 8 · Dimensions by anxiety group', f'''{img('fig5_subscales_by_HA', 'CSS dimensions by HA status')}
<p>People with elevated health anxiety score higher on all four dimensions, most of all excessiveness and distress.</p>''')
page('2', 'Quiz 2', '<ol class="quiz">' + ''.join(f'<li><details><summary>{q}</summary><p>{a}</p></details></li>' for q, a in [
    ('R² of the three regression blocks?', f'{N["R2a"]} → {N["R2b"]} → {N["R2c"]}'), ('B and β of health anxiety?', f'B {N["B"]}, β {N["beta"]}'),
    ('Three predictors of elevated health anxiety?', f'Cyberchondria {N["orCSS"]}, reassurance motive {N["orMot"]}, age {N["orAge"]}'),
    ('Which behaviours go with cyberchondria?', 'Urgent visits, less ignoring, strained relationship, more disclosure'), ('Why is H3 “not causal”?', 'Reverse order also significant; one time point')]) + '</ol>')

# ---------------------------------------------------------------- 3 statistics
STATS = [
 ('p-value', 'The chance of a result this strong if there were really no effect. Below 0.05 = significant. It says nothing about size.', 'r = 0.47, p < 0.001'),
 ('95% confidence interval', 'The range where the true value probably lies. For an odds ratio, if it includes 1 → not significant.', 'r 95% CI 0.38–0.55, always above 0'),
 ('Mean ± SD / median (IQR)', 'Average and spread; median and IQR when data are skewed.', f'SHAI {N["shai_m"]} ± {N["shai_sd"]}; median 12 (8–16)'),
 ('Shapiro–Wilk', 'Tests whether scores are normally distributed. Ours were not (p < 0.01), so groups were compared with non-parametric tests.', 'SHAI and CSS p < 0.01'),
 ('Cronbach α', 'Do the items of a scale measure the same thing? ≥ 0.7 acceptable, ≥ 0.8 good.', f'SHAI {N["aS"]}, CSS {N["aC"]}'),
 ('Mann–Whitney U / Kruskal–Wallis H', 'Compare a score between 2 groups / 3 or more groups without assuming normality.', 'Chronic condition: SHAI higher, p = 0.004'),
 ('Chi-square (χ²) / Fisher / Cramér’s V', 'Is a yes/no outcome related to a category? Fisher when cells are small. V = strength (0.1 small, 0.3 medium).', '52.6% vs 23.0% high CSS, OR 3.71'),
 ('Pearson r / Spearman ρ / partial r', 'Strength of a link between two scores; Spearman uses ranks (checks Pearson); partial r removes other variables.', f'r {N["r"]}, ρ {N["rho"]}, partial {N["pr"]}'),
 ('Multiple linear regression, B, β, R²', 'Predicts a score from many factors at once. B = change per unit; β = comparable strength; R² = share explained; hierarchical = blocks in order.', f'SHAI β {N["beta"]}; R² {N["R2c"]}'),
 ('Binary logistic regression, AOR', 'Predicts a yes/no outcome. Adjusted odds ratio: 1 = no effect, > 1 higher odds, < 1 lower.', f'AOR {N["orCSS"]} per SD of CSS'),
 ('Hosmer–Lemeshow, Nagelkerke R², AUC', 'Logistic model checks: H–L p > 0.05 = good fit; Nagelkerke ≈ R²; AUC = how well it separates groups (0.8+ good).', f'H–L p {f2(L["HL_p"])}, Nagelkerke {f2(L["nagelkerke"])}, AUC {f2(L["AUC"])}'),
 ('Mediation + Sobel test', 'Does part of X → Y pass through M? Paths a (X→M) and b (M→Y); indirect = a × b; Sobel z tests if it is above zero (|z| > 1.96).', f'a {M["A"]["a"]:.2f} × b {M["A"]["b"]:.2f} = {M["A"]["indirect"]:.2f}, z {M["A"]["sobel_z"]:.2f}'),
 ('z-scores', 'Scores converted so mean = 0 and SD = 1, so effects are “per 1 SD” and comparable.', 'AOR 3.12 per 1 SD (≈ 8 CSS points)'),
 ('VIF', 'Checks that predictors are not near-duplicates; below 5 is fine.', 'all low'),
]
page('3', 'Why each test was chosen (one rule)', '<p>The <b>type of variable</b> decides the test:</p>' + tbl(['You compare…', 'Test'], [
    ['a score between 2 groups', 'Mann–Whitney U'], ['a score between 3+ groups', 'Kruskal–Wallis H'], ['two categories (yes/no × group)', 'χ² (Fisher if small)'],
    ['two scores', 'Pearson r (+ Spearman)'], ['a score from many factors', 'multiple linear regression'], ['a yes/no from many factors', 'binary logistic regression'], ['a path through a middle variable', 'mediation + Sobel test']]) +
    say('Our scores were not normally distributed, so we compared groups with non-parametric tests, and all analyses were done in SPSS 26 with p < 0.05.'))
for k in range(0, len(STATS), 3):
    page('3', f'The tests ({k // 3 + 1} of {(len(STATS) + 2) // 3})', ''.join(f'<div class="stat"><b>{t}</b><p>{d}</p><p class="ex">Ours: {e}</p></div>' for t, d, e in STATS[k:k + 3]))
page('3', 'Quiz 3', '<ol class="quiz">' + ''.join(f'<li><details><summary>{q}</summary><p>{a}</p></details></li>' for q, a in [
    ('Why Mann–Whitney and not the t-test?', 'Scores were not normal (Shapiro–Wilk p < 0.01)'), ('What does AOR 0.61 for age mean?', 'Each older age group has lower odds: protective'),
    ('What does a Hosmer–Lemeshow p of 0.50 mean?', 'The model fits well (we want p > 0.05)'), ('How is the Sobel z calculated?', 'a×b / √(b²SEa² + a²SEb²); |z| > 1.96 → p < 0.05'),
    ('What is β for?', 'To compare the strength of predictors on one scale')]) + '</ol>')

# ---------------------------------------------------------------- 4 slides
SLIDES = [
 ('13 · Results', 'Thank you. I will present our results: who took part, how they search, the levels of health anxiety and cyberchondria, the main link, the predictors and pathways, and behaviour.'),
 ('14 · Participants', f'Table 1: our {N["n"]} participants were mostly young, {N["age20"]} aged 20 to 29, and {N["med"]} were medical students: a young, educated sample.'),
 ('15 · How people search', f'AI chatbots come first: {N["ai_tick"]} ticked them, ahead of search engines at {N["se"]}, and ChatGPT alone is used by {N["gpt"]}. For many, the first “doctor” is now an AI.'),
 ('16 · Levels and reliability', f'{N["hac"]} scored in the elevated range of health anxiety, and both questionnaires were reliable, alpha {N["aS"]} and {N["aC"]}.'),
 ('17 · Main result', f'Health anxiety and cyberchondria rise together, r = {N["r"]}, and the link stays {N["pr"]} after adjustment. Hypotheses 1 and 2 are supported.'),
 ('18 · What predicts cyberchondria', f'Demographics explain only 3%; health anxiety adds another {N["dR2"]}. How anxious you are matters far more than who you are.'),
 ('19 · Item by item (supplementary)', 'The strongest links are fear of serious illness and interpreting body sensations; simply noticing aches is almost unrelated. Fear drives searching, not noticing.'),
 ('20 · Who has elevated health anxiety', f'Higher cyberchondria triples the odds, searching for reassurance nearly quadruples them, and older age is protective; AUC {f2(L["AUC"])}.'),
 ('21 · Pathways', 'Part of the link runs through excessive searching, and almost all of the link to reassurance seeking runs through distress. Compatible with a cycle, but one survey cannot prove direction.'),
 ('22 · Behaviour', f'{N["dr"]} delay care because they feel reassured and {N["never"]} never tell their doctor. Higher cyberchondria goes with urgent visits and with more disclosure.'),
 ('23 · AI chatbots', f'AI users scored {N["Bai"]} points higher, but with the strict definition only {N["Balt"]}, not significant. No reliable independent effect of AI. I now hand over to my colleague.'),
]
page('4', 'Your 11 slides: the plan', '<p>About <b>30 seconds per slide</b>, 6 minutes in total. Pattern for every slide: <b>what it shows → one number → one-line meaning</b>.</p>' +
     tbl(['Slide', 'Point at'], [[s.split(' · ')[0], s.split(' · ')[1]] for s, _ in SLIDES]) + '<p class="tip">Handover line: “Those are our results. My colleague will now discuss what they mean.”</p>')
for k in range(0, len(SLIDES), 3):
    page('4', f'Slide scripts ({k // 3 + 1} of {(len(SLIDES) + 2) // 3})', ''.join(f'<div class="stat"><b>Slide {s}</b>{say(t)}</div>' for s, t in SLIDES[k:k + 3]))
page('4', 'Now do it out loud', '<p>Open the deck, start a timer and present slides 13–23 once without stopping. Aim for 6 minutes. If you stop, say the slide’s one number and move on.</p>' +
     trap('Do not read the slide. Look at the committee, point at the number, say the meaning.'))

# ---------------------------------------------------------------- 5 questions
QA = [
 ('You made the questionnaire. Why these two scales?', 'The SHAI-14 and the CSS-12 are short, validated and widely used, so our results can be compared with other countries; the CSS-12 keeps the four dimensions of the long scale.'),
 ('Why is the sample mostly young medical students?', 'Convenience and snowball sampling through our own networks; we say percentages cannot be generalised, but associations are still informative.'),
 ('How did you stop people answering twice?', 'The form accepted one response per Google account, and no duplicate patterns were found.'),
 ('Why SHAI ≥ 18?', 'It best separated people with health anxiety from healthy controls in the Swedish validation study; we also show 22 and 29.'),
 ('Did you translate the scales formally?', 'No formal back-translation; that is a limitation. Reliability was good and Arabic and English scores did not differ.'),
 ('Which software?', 'IBM SPSS Statistics version 26, with a syntax file that reproduces every table.'),
 ('Why did you not correct for multiple testing?', 'We used the standard p < 0.05 and state it as a limitation; the main results have p < 0.001.'),
 ('Explain r = 0.47 to a patient.', 'People who worry more about illness tend to search more and more anxiously; worry explains about a fifth of the differences.'),
 ('Why is your r lower than the meta-analyses (0.62)?', 'Low and narrow health anxiety, confident internet users and the short 12-item scale all weaken correlations.'),
 ('Does this prove a vicious cycle?', 'No: one time point, and the reverse order fits too. It is compatible with a cycle.'),
 ('Why did the AI effect disappear?', f'It depended on {N["inc"]} people who named a chatbot without ticking AI; with the strict definition p = {S["ai_strict"]["p"]:.2f}. Only 34 were non-users.'),
 ('What is the clinical message?', 'Ask every patient, without judgement, what they searched or asked an AI.'),
 ('Why non-parametric tests but linear regression?', 'Groups were compared non-parametrically because scores were skewed; regression residuals were close to normal and n = 300 is large, and Spearman confirmed Pearson.'),
 ('What is the most important limitation?', 'Cross-sectional design: we cannot tell which comes first.'),
]
for k in range(0, len(QA), 4):
    page('5', f'Questions and answers ({k // 4 + 1} of {(len(QA) + 3) // 4})', ''.join(f'<div class="qa"><p class="q">{q}</p><p class="a">{a}</p></div>' for q, a in QA[k:k + 4]))
page('5', 'Never say', '<ul class="never"><li>“Health anxiety <b>causes</b> cyberchondria” → “is associated with”.</li><li>“19% <b>have</b> health anxiety disorder” → “scored in the elevated range on a screening tool”.</li>'
     '<li>“AI makes people anxious” → “no reliable independent effect of AI”.</li><li>“Our results represent Baghdad” → “a young online convenience sample”.</li><li>“We proved a cycle” → “compatible with a cycle”.</li></ul>')
page('5', 'Done', '<p><b>That is everything you need.</b> Now do the flashcards once (the <b>Cards</b> tab), then one timed run of your slides.</p><p>Tomorrow: 20 minutes of cards and one more run. You are ready.</p>')

CARDS = [dict(q=q, a=a) for q, a in [
    ('Participants?', f'{N["n"]}; {N["age20"]} aged 20–29; {N["med"]} medical students'), ('AI chatbots ticked / search engines?', f'{N["ai_tick"]} / {N["se"]}'),
    ('Elevated health anxiety (≥ 18)?', f'{N["hac"]} (95% CI {N["hac_ci"]})'), ('Cronbach α SHAI / CSS?', f'{N["aS"]} / {N["aC"]}'),
    ('Main correlation and CI?', f'r = {N["r"]} ({N["rci"]})'), ('Partial r?', N['pr']), ('Strongest dimensions?', f'Excessiveness {N["rE"]}, distress {N["rD"]}'),
    ('Regression R² by block?', f'{N["R2a"]} → {N["R2b"]} → {N["R2c"]}'), ('What health anxiety adds?', N['dR2']), ('B and β of SHAI?', f'{N["B"]} / {N["beta"]}'),
    ('AI effect inclusive vs strict?', f'+{N["Bai"]} vs +{N["Balt"]} (p {S["ai_strict"]["p"]:.2f})'), ('Logistic AORs?', f'CSS {N["orCSS"]}, reassurance {N["orMot"]}, age {N["orAge"]}'),
    ('AUC, H–L p, % correct?', f'{f2(L["AUC"])}, {f2(L["HL_p"])}, {L["correct"]:.0f}%'), ('Sobel z for A and B?', f'{M["A"]["sobel_z"]:.2f} and {M["C"]["sobel_z"]:.2f}'),
    ('Delay when reassured / never tell?', f'{N["dr"]} / {N["never"]}'), ('Behaviours linked to cyberchondria?', 'Urgent visits, less ignoring, strained relationship, more disclosure'),
    ('Verdicts H1–H4?', 'Supported; supported; statistically not causally; partly'), ('Software and significance?', 'SPSS 26; p < 0.05, two-sided'),
    ('Why Mann–Whitney?', 'Scores not normal (Shapiro–Wilk)'), ('Sobel formula?', 'a×b / √(b²SEa² + a²SEb²)')]] + [dict(q=q, a=a) for q, a in QA]

# ---------------------------------------------------------------- page shell
pages_html = ''.join(f'<article class="pg" data-b="{bk}" hidden><div class="eyebrow">{"Start" if bk == "0" else "Block " + bk + " · " + next(t for k, t, m in BLOCKS if k == bk)}</div><h2>{t}</h2>{h}</article>' for bk, t, h in P)
first = {k: next(i for i, p in enumerate(P) if p[0] == k) for k, _, _ in BLOCKS}
shell = open(__file__.replace('17_student2_sprint.py', 'sprint_shell.html')).read()
html_ = shell.replace('__PAGES__', pages_html).replace('__BLOCKS__', json.dumps([dict(k=k, t=t, m=m, first=first[k]) for k, t, m in BLOCKS], ensure_ascii=False)).replace('__CARDS__', json.dumps(CARDS, ensure_ascii=False).replace('</', '<\\/'))
open(HTML, 'w').write(html_)
print('wrote', HTML, len(P), 'pages', len(CARDS), 'cards', f'{len(html_) / 1e6:.2f} MB')
