"""Team guide for the three presenting students: study plan, per-student parts, safe editing of the
Word file, writing in your own voice (and honest AI disclosure), and presenting.
Usage: python3 11_team_guide.py <numbers.json> <out.html>   (then print to PDF with Chromium)"""
import sys, json, html
N = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
e = html.escape

CSS = """
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, Carlito, Arial, sans-serif; font-size: 10.6pt; color: #222; line-height: 1.42; margin: 0; }
h1 { font-family: Cambria, Caladea, Georgia, serif; color: #1E5B4F; font-size: 25pt; margin: 0 0 4px; }
h2 { font-family: Cambria, Caladea, Georgia, serif; color: #1E5B4F; font-size: 16pt; margin: 18px 0 6px; padding-bottom: 3px; border-bottom: 2px solid #1E5B4F; page-break-after: avoid; }
h3 { color: #B45F06; font-size: 12pt; margin: 12px 0 4px; page-break-after: avoid; }
p { margin: 4px 0 6px; }
ul, ol { margin: 3px 0 7px; padding-left: 20px; } li { margin: 2px 0; }
.sub { color: #555; font-size: 11.5pt; margin-bottom: 12px; }
.box { border: 1px solid #c9d3d1; border-left: 5px solid #1E5B4F; background: #F4F8F7; padding: 8px 11px; margin: 8px 0; page-break-inside: avoid; }
.warn { border-left-color: #B45F06; background: #FFF7ED; }
.red { border-left-color: #7F1D3A; background: #FBF1F4; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.8pt; page-break-inside: avoid; }
th { background: #DCE6E4; text-align: left; } th, td { border: 1px solid #c8cfcd; padding: 4px 6px; vertical-align: top; }
.s1 { color: #fff; background: #1E5B4F; } .s2 { color: #fff; background: #0B5394; } .s3 { color: #fff; background: #7F1D3A; }
.tag { display: inline-block; padding: 1px 8px; border-radius: 9px; font-weight: bold; font-size: 9.5pt; }
.page { page-break-before: always; }
.q { font-weight: bold; color: #1E5B4F; } .a { margin: 0 0 7px 12px; }
.num { font-weight: bold; color: #B45F06; }
.cols { display: flex; gap: 12px; } .cols > div { flex: 1; }
.small { font-size: 9.4pt; color: #555; }
"""

def qa(items):
    return ''.join(f'<p class="q">Q: {e(q)}</p><p class="a">{a}</p>' for q, a in items)

H = []
w = H.append
w(f'<!doctype html><html><head><meta charset="utf-8"><title>Team Guide</title><style>{CSS}</style></head><body>')

# ------------------------------------------------------------------ cover
w(f'''<h1>Team Guide: Study, Edit, Present</h1>
<div class="sub">Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad · for the three presenting students</div>
<div class="box"><b>How to use this guide.</b> Part 1 is for <b>all three of you</b>. Part 2 has one section per student. Part 3 covers <b>editing</b> the thesis
safely and making the writing your own. Part 4 covers <b>presenting</b>. The last page is a checklist for the day before the defence.</div>
<h2>The plan at a glance</h2>
<table><tr><th>Who</th><th>Presents (slides)</th><th>Owns in the thesis (study deeply, edit)</th><th>Time</th></tr>
<tr><td><span class="tag s1">Student 1</span></td><td>1–12: title, quote, objectives, Introduction, Methodology</td><td>Ch. 1 Introduction, Ch. 2 Method, Acknowledgment</td><td>≈ 5 min</td></tr>
<tr><td><span class="tag s2">Student 2</span></td><td>13–23: Results</td><td>Ch. 3 Results, all tables and figures, Appendix A</td><td>≈ 6 min</td></tr>
<tr><td><span class="tag s3">Student 3</span></td><td>24–33: Discussion, limitations, recommendations, conclusion</td><td>Ch. 4 Discussion, Ch. 5 Conclusions &amp; Recommendations</td><td>≈ 4 min</td></tr>
<tr><td>All three</td><td>Questions</td><td>Abstract (rewrite together, last), title page, final read-through</td><td>Q&amp;A</td></tr></table>
<h3>Suggested timeline (adjust to your defence date)</h3>
<table><tr><th>When</th><th>Everyone</th></tr>
<tr><td>Week 1</td><td>Each reads the <b>whole</b> thesis once (Part 1 reading order). Learn the 15 core numbers. Each student studies their own chapter deeply and starts rewriting it in their own words.</td></tr>
<tr><td>Week 2</td><td>Finish rewriting. Swap chapters and check each other's (accuracy + one voice). Fill the placeholders. Practise your own slides alone, out loud, 3 times.</td></tr>
<tr><td>Week 3</td><td>Rewrite the Abstract together. Final Word checks (Part 3). Two full rehearsals with timing, then a mock committee: each student asks the others the questions in Part 2.</td></tr>
<tr><td>Day before</td><td>Checklist (last page). One calm run-through. Sleep.</td></tr></table>''')

# ------------------------------------------------------------------ Part 1
w('<h2 class="page">Part 1 · What all three of you must know</h2>')
w('''<div class="box warn"><b>Rule:</b> the committee can ask <b>any</b> student about <b>any</b> part. You split the presentation, not the knowledge.
Each of you must be able to explain the whole study in two minutes without slides.</div>
<h3>Reading order (do it once, all of you)</h3>
<ol><li><b>Abstract</b>: the whole study on one page.</li>
<li><b>1.8 Aim and objectives</b> and the hypotheses H1–H4: everything else answers these.</li>
<li><b>Chapter 5 Conclusions</b>: what you claim.</li>
<li><b>Chapter 3 Results</b> with Tables 1–13 and Figures 1–10 open beside you.</li>
<li><b>Chapter 4 Discussion</b>, especially <b>4.8 Limitations</b> (committees love limitations).</li>
<li><b>Chapters 1–2</b> last: background and methods.</li></ol>
<p>While reading, mark every sentence you could <b>not</b> explain to a friend. Bring those to the team or ask me.</p>''')
core = [
 ("Who and when", f"<span class='num'>{N['n']}</span> adults, Baghdad, online survey, {N['d0']} – {N['d1']}"),
 ("Sample size", f"<span class='num'>{N['nreq']}</span> needed (r = 0.20, 80% power); we have 300"),
 ("Sample profile", f"<span class='num'>{N['age20']}</span> aged 20–29 · {N['fem']} female · <span class='num'>{N['med']}</span> medical students · {N['hb']} health background"),
 ("AI chatbots", f"<span class='num'>{N['ai_tick']}</span> ticked AI (<span class='num'>{N['ai']}</span> incl. named) vs {N['se']} search engines · ChatGPT {N['gpt']}"),
 ("Health anxiety", f"SHAI mean {N['shai_m']} / 42 · <span class='num'>{N['hac']}</span> elevated (≥ 18; 95% CI {N['hac_ci']})"),
 ("Cyberchondria", f"CSS mean {N['css_m']} / 60 · excessiveness highest, compulsion lowest"),
 ("Reliability", f"α = {N['aS']} (SHAI), {N['aC']} (CSS); CSS-12 invariant across Arabic and English"),
 ("Main result", f"<span class='num'>r = {N['r']}</span> (95% CI {N['rci']}); partial r = {N['pr']} after adjusting for everything"),
 ("Regression", f"demographics explain {float(N['R2a'])*100:.0f}%; health anxiety adds <span class='num'>{N['dR2']}</span>; β = {N['beta']}"),
 ("Who is anxious", f"AOR <span class='num'>{N['orCSS']}</span> per SD of cyberchondria · {N['orMot']} if searching for reassurance · {N['orAge']} per older age group · AUC {N['auc']} → {N['aucc']}"),
 ("Pathways", f"via excessive searching {N['mA']} · via distress {N['mC']} (direct → {N['mCd']}) · reverse also {N['mD']}: a cycle is <i>compatible</i>, not proven"),
 ("Behaviour", f"<span class='num'>{N['dr']}</span> delay care when reassured · <span class='num'>{N['never']}</span> never tell the doctor · higher cyberchondria → more disclosure (OR {N['nsC']}, q = {N['nsCq']})"),
 ("AI effect", f"+{N['Bai']} CSS points (inclusive) but {N['Balt']}, p = {N['palt']} (strict) → <b>no reliable independent effect</b>"),
 ("The 32", f"{N['inc']} people named a chatbot without ticking “AI”; how they are classified decides the AI result"),
 ("Big limitation", "cross-sectional (no causation) · convenience sample, young, many medical students"),
]
w('<h3>The 15 core facts (memorise; the committee will test these)</h3><table><tr><th style="width:24%">Topic</th><th>Fact</th></tr>' +
  ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in core) + '</table>')
w('''<h3>Ten concepts in plain words</h3>
<table><tr><th style="width:22%">Term</th><th>Say it like this</th></tr>
<tr><td>Health anxiety</td><td>Persistent worry about having a serious illness, kept going by misreading normal body sensations and seeking reassurance.</td></tr>
<tr><td>Cyberchondria</td><td>Searching online about health so much, or so repeatedly, that it makes you <i>more</i> worried, not less.</td></tr>
<tr><td>Correlation r</td><td>How closely two scores move together, from 0 (none) to 1 (perfect). 0.47 is moderate: clear, but far from identical.</td></tr>
<tr><td>Partial correlation</td><td>The same link after removing the effect of age, gender, background and the rest. Ours barely changed (0.48).</td></tr>
<tr><td>FDR correction</td><td>When you run many tests, some come out “significant” by luck. FDR adjusts for this; findings that do not survive are called exploratory.</td></tr>
<tr><td>Adjusted odds ratio</td><td>How many times the odds of an outcome change for one unit of a factor, holding the others constant. 3.12 = odds about triple.</td></tr>
<tr><td>AUC</td><td>How well a model tells two groups apart: 0.5 = coin toss, 1 = perfect. 0.83 (0.79 after correcting for over-fitting) is good.</td></tr>
<tr><td>Mediation</td><td>Splitting a link into a part that goes <i>through</i> a third variable and a direct part. Statistical, not proof of cause.</td></tr>
<tr><td>CFA</td><td>Checks that questionnaire items group into the factors they are supposed to measure (e.g., the four CSS facets).</td></tr>
<tr><td>Measurement invariance</td><td>Checks that the questionnaire measures the same thing in Arabic and English, so the two groups can be compared fairly.</td></tr></table>''')
w('''<div class="box red"><b>Never say</b> (it overclaims, and the committee will catch it):
<ul><li>“Health anxiety <i>causes</i> cyberchondria” → say “is associated with”, “is compatible with a cycle”.</li>
<li>“19% <i>have</i> health anxiety disorder” → say “19% scored in the elevated range on a screening tool”.</li>
<li>“AI makes people more anxious” → our data show <b>no reliable independent effect</b> of AI.</li>
<li>“Our results apply to all of Baghdad” → the sample is a young, online, convenience sample.</li></ul></div>''')

# ------------------------------------------------------------------ Part 2 per student
def student(tag, cls, title, slides, study, numbers, qas, edit_tips):
    w(f'<h2 class="page"><span class="tag {cls}">{tag}</span> {title}</h2>')
    w(f'<div class="box"><b>You present:</b> {slides}</div>')
    w('<h3>Study deeply</h3><ul>' + ''.join(f'<li>{x}</li>' for x in study) + '</ul>')
    w('<h3>Your numbers (know them without looking)</h3><ul>' + ''.join(f'<li>{x}</li>' for x in numbers) + '</ul>')
    w('<h3>Questions you should be ready for</h3>' + qa(qas))
    w('<h3>When you edit your chapter</h3><ul>' + ''.join(f'<li>{x}</li>' for x in edit_tips) + '</ul>')

student('Student 1', 's1', 'Introduction & Methods',
 'slides 1–12 (title → statistical analysis), ≈ 5 minutes. You open the defence, so you set the tone: slow, clear, confident. End by handing over: “Now my colleague will present our results.”',
 ['<b>1.2–1.4</b>: health anxiety, cyberchondria, the cognitive-behavioural cycle, the two meta-analyses (r ≈ 0.62) and the Dutch longitudinal study.',
  '<b>1.5</b>: why AI chatbots are different from search engines (conversational, repeatable, empathetic-sounding).',
  '<b>1.7 Rationale</b>: the three gaps your study fills. Practise saying them in one breath.',
  '<b>Figure 1</b> (conceptual framework) and <b>Figure 2</b> (study flowchart): you present the study model and the study flow.',
  '<b>2.1–2.5</b>: design, sampling, inclusion criteria, sample size calculation, the five parts of the questionnaire, the SHAI ≥ 18 definition and why it is called “elevated”.',
  '<b>2.6</b> at headline level: you name the methods; Student 2 explains them in detail.'],
 [f'Data collection {N["d0"]} – {N["d1"]}; n = 300', f'Sample size {N["nreq"]} for r = 0.20 (α 0.05, 80% power); margin of error ±{N["moe"]}%',
  'SHAI-14: 14 items, 0–42; cut-off 18 (Swedish study); CSS-12: 12 items, 12–60, four facets', 'Iraq: > 80% online; Iraqi COVID survey: about half reported health anxiety'],
 [("Why did you choose this topic?", "Give your <b>real</b> reason (what you noticed in patients, family or yourselves using ChatGPT before seeing a doctor). Then: no Iraqi data, and AI chatbots had not been studied next to search engines."),
  ("Why cross-sectional and not longitudinal?", "Feasible within a student project; it measures associations. We say clearly that it cannot show direction, and we recommend longitudinal studies."),
  ("Convenience sampling is biased. Why use it?", "No sampling frame for online adults in Baghdad. We describe the sample honestly, avoid generalising percentages, and show associations were consistent across subgroups."),
  ("How did you calculate the sample size?", f"Fisher's z for a correlation: r = 0.20, α = 0.05, 80% power gives {N['nreq']}; we collected 300. Meta-analytic r is ≈ 0.62, so this is conservative."),
  ("Why SHAI ≥ 18?", "It best separated people with health anxiety from healthy controls in a Swedish diagnostic study. It is a screening threshold, so we say “elevated”, and we report other cut-offs (only 0.7% at 29)."),
  ("Is your Arabic version validated?", "Not by formal back-translation, which is a limitation. But we tested it: equal reliability, and formal invariance tests showed the CSS-12 works identically in Arabic and English; the SHAI-14 had equal loadings."),
  ("How did you make sure participants lived in Baghdad?", "Through Baghdad-based distribution channels; there was no residence question, and we list this as a limitation."),
  ("Do you have ethical approval?", "Give the committee name, number and date (fill this in the thesis before the defence).")],
 ['Introduction: rewrite the explanations in your own words, but keep every reference number [n] attached to the claim it supports.',
  'Do not change numbers, cut-offs, dates or test names in the Method.',
  'Add what only you know: why you chose the topic, how you shared the link, problems you met while collecting data (must be true).',
  'Write the Acknowledgment yourselves: it is personal and should sound like you.'])

student('Student 2', 's2', 'Results',
 'slides 13–23 (Results divider → AI chatbots), ≈ 6 minutes. Each results slide has a script in the speaker notes: <b>Opening → Main finding → Closing “In summary…”</b>. End: “I now hand over to my colleague for the discussion.”',
 ['<b>Every table and figure</b> (Tables 1–13, Figures 1–11): what each column means, and the one message of each.',
  '<b>3.4</b> reliability, CFA, the cut-off table (Table 4) and the invariance table (Table 5, Arabic vs English).',
  '<b>3.5</b> the main correlation, partial r, and why excessiveness and distress are stronger than compulsion and reassurance.',
  '<b>3.7</b> hierarchical regression (Table 9) and logistic regression (Table 10, Figure 8), including AUC.',
  '<b>3.9</b> mediation (Figure 9): what “indirect effect” means and why it is not proof of cause.',
  '<b>2.6 Statistical analysis</b>: you are the team\'s statistics person; you answer method questions.'],
 [f'r = {N["r"]} (95% CI {N["rci"]}), Spearman ρ = {N["rho"]}, partial r = {N["pr"]}', f'Facets: excessiveness {N["rE"]}, distress {N["rD"]}, compulsion {N["rC"]}, reassurance {N["rR"]}',
  f'R²: {N["R2a"]} → {N["R2b"]} → {N["R2c"]} (health anxiety adds {N["dR2"]}); β = {N["beta"]}; B = {N["B"]} CSS points per SHAI point',
  f'Logistic: AOR {N["orCSS"]} (cyberchondria per SD), {N["orMot"]} (reassurance motive), {N["orAge"]} (age); AUC {N["auc"]} → {N["aucc"]}',
  f'Mediation: indirect {N["mA"]} (CI {N["mAci"]}); via distress {N["mC"]}, direct {N["mCd"]}; reverse {N["mD"]}',
  f'AI: +{N["Bai"]} (CI {N["Baici"]}) inclusive vs +{N["Balt"]} (p = {N["palt"]}) strict; {N["inc"]} named-not-ticked; 34 non-users',
  f'{N["ibF"]} / 168 item pairs significant after FDR'],
 [("Why non-parametric tests?", "The scores were not normally distributed (Shapiro–Wilk). We also ran parametric tests (Welch) as confirmation; conclusions were the same."),
  ("What is FDR and why use it?", "We ran many tests; FDR controls the share of false positives among significant results. What did not survive is labelled exploratory."),
  ("Explain r = 0.47 to a non-statistician.", "People with more health anxiety tend clearly to have more cyberchondria; anxiety explains about a fifth (22%) of the differences in cyberchondria."),
  ("Why hierarchical regression?", "To show how much health anxiety adds <i>after</i> demographics and digital use: 18.4% extra variance, the biggest block by far."),
  ("Does mediation prove a vicious cycle?", "No. The data are from one time point and the reverse direction fits too. It is <b>compatible</b> with a cycle; only longitudinal data can show direction."),
  ("Why does the AI effect disappear?", f"It depends on {N['inc']} people who named a chatbot but did not tick the box; they had the highest scores. With the strict definition, p = {N['palt']}. And only 34 people were non-users, a small comparison group."),
  ("Chronic illness was not significant in the logistic model. Why?", "Turning SHAI into yes/no (≥ 18) loses information and power. On the continuous SHAI score, chronic illness <b>is</b> significant: p = 0.004 unadjusted, and still p = 0.029 in the adjusted linear model (B = +1.7 points)."),
  ("What do CFI and RMSEA mean?", "Fit indices for CFA: CFI near 0.95 or above and RMSEA below about 0.08 indicate acceptable fit. CSS-12 four factors: CFI 0.95, RMSEA 0.07."),
  ("What is the AUC, and why is it corrected?", "How well the model separates elevated from non-elevated anxiety. A model always looks better on its own data, so we corrected for this by bootstrapping: 0.83 → 0.79.")],
 ['Results are mostly numbers: <b>do not change any number</b>, p-value, CI or test name. Rewrite only the connecting sentences.',
  'Keep “Table n” and “Figure n” mentions; never type caption numbers by hand (they are automatic fields).',
  'If a sentence seems wrong or unclear, do not “fix” the statistics yourself: mark it with a comment and ask.',
  'You will be asked about statistics in the Method too: read 2.6 until you can explain each method in one sentence.'])

student('Student 3', 's3', 'Discussion & Conclusions',
 'slides 24–33 (Discussion divider → closing slide), ≈ 4 minutes. You end the defence: finish strongly on the conclusion and the clinical message, then “Thank you; we welcome your questions.”',
 ['<b>4.1–4.2</b>: principal findings and why our r (0.47) is weaker than the meta-analyses (0.62–0.63): four reasons.',
  '<b>4.3</b>: the cycle question, and why the answer is “compatible, not proven”.',
  '<b>4.4–4.5</b>: AI chatbots (why our AI use is so much higher than in US surveys) and the consultation (delay, non-disclosure, trust).',
  '<b>4.6–4.7</b>: medical students and regional studies (Jeddah, Saudi primary care, Lebanon, Egypt).',
  '<b>4.8 Limitations</b>: know all of them and what was done about each.',
  '<b>Chapter 5</b>: the six conclusions and the recommendations, by audience.'],
 [f'Our r {N["r"]} vs meta-analyses 0.62–0.63; corrected for reliability ≈ {N["disr"]}', 'AI use: ours 78–89% vs ≈ 20% (US 2024) and 21% (2025); 96% at 18–19 y vs 72% at ≥ 40 y',
  f'{N["dr"]} delay care when reassured; {N["never"]} never tell the doctor; {N["relneg"]} say trust was strained', 'Egypt: 1435 medical students, 85.8% moderate cyberchondria',
  'ClinicalTrials.gov: only 9 cyberchondria studies, none in Iraq'],
 [("Why is your correlation weaker than other studies?", f"Measurement error (corrected r ≈ {N['disr']}), low and narrow health anxiety in our sample, online recruitment of confident users, and the short CSS-12 instead of the 33-item version."),
  ("Is your sample representative of Baghdad?", "No, and we say so: young, educated, many medical students. Percentages should not be generalised; associations were consistent across subgroups."),
  ("What is new in your study?", "First CSS-12 data from Baghdad; AI chatbots studied separately from search engines; psychology linked to real behaviour before the consultation."),
  ("Why is AI use so high in your sample?", "A young, educated, health-oriented sample; AI use fell clearly with age. It is not an estimate for all adults."),
  ("What is your biggest limitation?", "The cross-sectional design: we cannot say what causes what. Second, the convenience sample."),
  ("If you repeated the study, what would you change?", "Random sampling of all ages, formal Arabic adaptation, a clearer AI-use question, and a follow-up to test the cycle over time."),
  ("What should a doctor do differently on Monday?", "Ask every patient, without judgement, what they searched or asked an AI; recognise repeated searching and reassurance seeking as signs of health anxiety."),
  ("Are medical students more anxious?", "Unadjusted yes, but it disappeared after adjustment: it reflected their younger age. Their cyberchondria was the same as everyone else's.")],
 ['Discussion is the most “human” chapter: interpret in your own words, add your own clinical reasoning, keep every reference [n].',
  'Do not strengthen claims (no “proves”, “causes”). Keep hedges such as “compatible with”, “exploratory”.',
  'Recommendations can carry your own voice and local knowledge (Iraqi health system, Arabic resources), as long as they follow from the results.'])

# ------------------------------------------------------------------ Part 3 editing
w('<h2 class="page">Part 3 · Editing the thesis safely</h2>')
w('''<div class="box warn"><b>Important: the Word file is now your master copy.</b> The thesis was generated by a script. If you edit in Word and then someone
regenerates it, your edits are lost. From now on, edit only the .docx. If you want me to change something later, send me your edited file
and I will work on that version.</div>
<h3>Set-up (do this first)</h3>
<ol><li>Keep an untouched copy: <b>Thesis_ORIGINAL.docx</b>. Never edit it.</li>
<li>Work in <b>one</b> shared file (OneDrive / Word Online lets all three edit at once and keeps the automatic fields working). Avoid converting to Google Docs: it breaks the table of contents and caption numbering.</li>
<li>Turn on <b>Review → Track Changes</b>, so the team (and your supervisor) can see what changed.</li>
<li>Each student edits only their own chapters (Part 2). The Abstract is rewritten together at the end.</li></ol>
<h3>Do not touch (protected)</h3>
<table><tr><th>Item</th><th>Why</th></tr>
<tr><td>Any number, %, p, CI, r, OR, β, n</td><td>They come from the analysis; one wrong digit is a factual error.</td></tr>
<tr><td>Reference numbers like [12] or [18,19]</td><td>Each supports the claim it is attached to. If you move a sentence, move its [n] with it.</td></tr>
<tr><td>The reference list (Chapter 6)</td><td>Vancouver order matches the order of first citation.</td></tr>
<tr><td>Table/Figure captions, table of contents, lists of tables/figures</td><td>Automatic fields. Never type numbers by hand.</td></tr>
<tr><td>Heading numbers (1.1, 2.6…) and styles</td><td>The table of contents is built from them.</td></tr>
<tr><td>Times New Roman 14, page numbering (roman → arabic)</td><td>College format.</td></tr></table>
<h3>After editing (in this order)</h3>
<ol><li>Ctrl + A, then F9 (or right-click → Update Field → Update entire table) to refresh the table of contents, the lists, and the caption numbers.</li>
<li>Check the Abstract is still ≤ 1.5 pages and the Introduction ≥ 4 pages.</li>
<li>Search the document for “[” to find any placeholder left: names, supervisor, college, year, degree, ethics approval, the Google Forms question.</li>
<li>Swap chapters: each student reads another's chapter for accuracy (numbers unchanged?) and voice (does it sound like the rest?).</li>
<li>Export to PDF and look at every page.</li></ol>''')
w('''<h2>Making the writing genuinely yours</h2>
<p>A thesis you can defend is one you could have written: every sentence is something you understand and would say. That is also what protects you best,
whatever tool your college uses to check the text.</p>
<h3>The rewrite method (paragraph by paragraph)</h3>
<ol><li><b>Read</b> the paragraph until you understand it. Look up anything you can't explain.</li>
<li><b>Close it</b> and explain it out loud, as you would to a classmate.</li>
<li><b>Write</b> your version from that explanation, in your normal academic English.</li>
<li><b>Compare</b> with the original: same facts, same numbers, same [n] references, nothing claimed more strongly than before.</li>
<li><b>Read aloud</b>. If you would never say a phrase, change it.</li></ol>
<h3>What makes text sound like you</h3>
<ul><li><b>Your own reasons and observations</b>: why you chose the topic, what you saw in clinics or among friends, what surprised you in the results. Only true things.</li>
<li><b>Your experience of the study</b>: how you shared the link, how people reacted, what was hard. A short paragraph in the Method or Discussion is fine if true.</li>
<li><b>Local context</b> you know better than any source: how people in Baghdad use ChatGPT, pharmacies, private clinics, the cost of visits.</li>
<li><b>Plain, varied sentences.</b> Cut stock phrases such as “it is important to note”, “plays a crucial role”, “in today's digital age”, “delve into”, “a testament to”.</li>
<li><b>One team voice:</b> after rewriting, one student reads the whole thesis and smooths differences in style.</li></ul>
<div class="box red"><b>About AI detectors, honestly.</b> Detectors are unreliable in both directions, and tricks to fool them (paraphrasing tools,
deliberate errors, odd synonyms) make the thesis worse and can count as misconduct. I won't help with those. What protects you:
<ol style="margin-top:4px"><li><b>Check your college's AI policy</b> and ask your supervisor what must be declared.</li>
<li><b>Declare the AI assistance</b> if required. A sentence you can adapt for the Acknowledgment or Method:<br>
<i>“The statistical analysis code and an initial draft of this report were prepared with the assistance of an AI tool (Claude, Anthropic). All analyses were checked, and the text was reviewed and rewritten by the authors, who take full responsibility for its content.”</i></li>
<li><b>Keep your edit history</b> (Track Changes, OneDrive version history, your notes): it shows your own work.</li>
<li><b>Understand every sentence</b>: the oral defence is the real test, and this guide prepares you for it.</li></ol></div>''')

# ------------------------------------------------------------------ Part 4 presenting
w('<h2 class="page">Part 4 · Presenting</h2>')
w(f'''<h3>Practise like this</h3>
<ol><li><b>Alone</b>: read your speaker notes (in PowerPoint: View → Notes), then present your slides out loud three times, each time using fewer notes.</li>
<li><b>Time yourself</b>: Student 1 ≈ 5 min, Student 2 ≈ 6 min, Student 3 ≈ 4 min. If over, cut words, not slides.</li>
<li><b>Together</b>: two full run-throughs with handovers, standing up, with the clicker.</li>
<li><b>Mock committee</b>: take turns asking each other the Part 2 questions. Answer in under 40 seconds each.</li>
<li>Record one rehearsal on a phone and watch it once: speed, filler words (“umm”, “so basically”), eye contact.</li></ol>
<div class="cols"><div><h3>On the day</h3><ul>
<li>Look at the committee, not the screen. Point to the number you are talking about.</li>
<li>One message per slide: say the “In summary…” line from your notes.</li>
<li>Speak slower than feels natural; pause after key numbers (r = {N["r"]}, {N["hac"]}, {N["ai_tick"]}).</li>
<li>Stand to one side; the next speaker stands ready before the handover.</li>
<li>Bring the deck on a USB stick and as a PDF (in case the PC lacks fonts).</li></ul></div>
<div><h3>Handling questions</h3><ul>
<li><b>Who answers:</b> the owner of that part answers first; statistics → Student 2. Others add only if needed.</li>
<li>Pause, repeat the question briefly, answer in two or three sentences, stop.</li>
<li>Accept limitations calmly: “Yes, that is a limitation; we addressed it by… and recommend…”.</li>
<li>If you don't know: “We did not examine that directly; based on our data we would expect…, and it is a good question for future research.” Never invent a number.</li>
<li>If a teammate struggles, help with “If I may add…”.</li></ul></div></div>
<h3>Handover lines (memorise)</h3>
<ul><li>Student 1 → 2: “That was our methodology. Now my colleague will present what we found.”</li>
<li>Student 2 → 3: “Those are our results. My colleague will now discuss what they mean.”</li>
<li>Student 3 → committee: “Thank you for listening; we welcome your questions.” (leave the r = {N["r"]} slide up)</li></ul>''')
w('''<h2>Checklist: the day before</h2>
<table><tr><th style="width:6%">✓</th><th>Item</th></tr>''' + ''.join(f'<tr><td>☐</td><td>{x}</td></tr>' for x in [
 'All placeholders filled: names, supervisor, college, logo, degree, year, ethics approval, the Google Forms question, Acknowledgment',
 'Fields updated (Ctrl + A, F9); table of contents page numbers correct; PDF exported and checked page by page',
 'AI-assistance declaration added if your college requires it',
 'Names and supervisor filled on slide 1 of the presentation; ethics number on slide 10',
 'Presentation on USB + PDF copy + email to yourselves; clicker tested',
 'Each student can state the 15 core facts and explain their own slides without notes',
 'Each student has answered every question in Part 2 out loud at least once',
 'Printed copy of the thesis for the committee, if required',
 'Sleep, breakfast, arrive early; agree who stands where']) + '</table>')
w('<p class="small">Generated from the study outputs (numbers.json), so every number here matches the thesis.</p></body></html>')
open(OUT, 'w').write('\n'.join(H))
print('wrote', OUT)
