// Defence presentation (classic academic style, ~22 slides). Usage: node 21_defence_slides.js <output dir> <out.pptx>
const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/25741026-d946-4dbc-8c24-ac9a6070fdfc_a0e8a8de-929a-428a-b59c-ea7dac5ee207/pptx/scripts/apply_theme.js');
const OUT = process.argv[2], FILE = process.argv[3];
const FIG = OUT + '/figures/', PH = OUT + '/figures/photos/';
const THEME = { name: 'Baghdad Defence', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '1D2230', lt1: 'FFFFFF', dk2: '1F3B4D', lt2: 'EEF2F6', accent1: '1F3B4D', accent2: 'B4541C', accent3: '2E7D6B',
    accent4: '8A6D1F', accent5: '6A4C9C', accent6: '9D1C4A', hlink: '1F6FA0', folHlink: '6A4C9C' } };
const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad'; pres.author = 'Graduation research project';
const C = pres.SchemeColor, NAVY = C.text2, ORANGE = C.accent2, INK = C.text1, WHITE = C.background1, PALE = C.background2;
const HX = THEME.colors;
const FOOT = 'College of Medicine · University of Baghdad   |   Health Anxiety, AI Chatbot Use and Cyberchondria';

pres.defineSlideMaster({ title: 'Content', background: { color: WHITE }, objects: [
  { rect: { x: 0, y: 0, w: 13.33, h: 1.05, fill: { color: NAVY } } },
  { rect: { x: 0, y: 1.05, w: 13.33, h: 0.07, fill: { color: ORANGE } } },
  { rect: { x: 0, y: 7.08, w: 13.33, h: 0.42, fill: { color: PALE } } },
  { text: { text: FOOT, options: { x: 0.5, y: 7.08, w: 10.5, h: 0.42, fontSize: 11, color: NAVY, valign: 'middle', margin: 0 } } },
  { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.1, w: 12.3, h: 0.85, fontSize: 30, bold: true, color: WHITE, valign: 'middle', margin: 0 }, text: 'Title' } }],
  slideNumber: { x: 12.1, y: 7.08, w: 0.8, h: 0.42, fontSize: 12, bold: true, color: NAVY, align: 'right' } });
pres.defineSlideMaster({ title: 'Cover', background: { color: NAVY } });

let SEC = '';
const sec = t => { SEC = t; pres.addSection({ title: t }); };
const S = title => { const s = pres.addSlide({ masterName: 'Content', sectionTitle: SEC }); s.addText(title, { placeholder: 'title' }); return s; };
const bul = (s, items, x, y, w, h, fs = 18) => s.addText(items.map((t, i) => {
  const runs = t.split('**').map((r, j) => ({ r, b: j % 2 === 1 })).filter(o => o.r !== '');
  return runs.map((o, j) => ({ text: o.r, options: Object.assign({ bold: o.b, color: o.b ? NAVY : INK },
    j === 0 ? { bullet: true, paraSpaceAfter: 8 } : {}, j === runs.length - 1 && i < items.length - 1 ? { breakLine: true } : {}) }));
}).flat(), { x, y, w, h, fontSize: fs, valign: 'top', isTextBox: true, margin: 4 });
const head = (s, t, x, y, w) => s.addText(t, { x, y, w, h: 0.42, fontSize: 19, bold: true, color: ORANGE, fontFace: THEME.headFontFace, isTextBox: true, margin: 0 });
const tbl = (s, hd, rows, x, y, w, colW, fs = 14, hi = []) => s.addTable(
  [hd.map(t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY } } }))].concat(rows.map((r, i) => r.map((t, j) =>
    ({ text: String(t), options: { color: INK, bold: j === 0 || hi.includes(i), fill: { color: hi.includes(i) ? 'FFF1B8' : (i % 2 ? 'EEF2F6' : 'FFFFFF') } } })))),
  { x, y, w, colW, fontSize: fs, border: { type: 'solid', pt: 0.75, color: 'B8C4CE' }, valign: 'middle', margin: [3, 6, 3, 6] });
const stat = (s, num, label, x, y, w, h = 1.5, col = NAVY) => {
  s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: PALE }, line: { color: 'B8C4CE', width: 0.75 } });
  s.addText(num, { x, y: y + 0.08, w, h: h * 0.52, fontSize: 34, bold: true, color: col, align: 'center', valign: 'middle', fontFace: THEME.headFontFace, isTextBox: true, margin: 0 });
  s.addText(label, { x: x + 0.1, y: y + h * 0.56, w: w - 0.2, h: h * 0.4, fontSize: 13, color: INK, align: 'center', valign: 'top', isTextBox: true, margin: 0 }); };
const pic = (s, f, x, y, w, h, cap) => { s.addImage({ path: f, x, y, w, h }); s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { type: 'none' }, line: { color: HX.dk2, width: 1.25 } });
  if (cap) s.addText(cap, { x, y: y + h + 0.03, w, h: 0.28, fontSize: 10, italic: true, color: '555555', align: 'center', isTextBox: true, margin: 0 }); };
const note = (s, t, x, y, w, h = 0.75, col = NAVY) => s.addText(t, { x, y, w, h, fontSize: 16, bold: true, color: WHITE, fill: { color: col }, align: 'center', valign: 'middle', isTextBox: true, margin: 8 });
const CH = { catAxisLabelColor: HX.dk1, valAxisLabelColor: HX.dk1, catAxisLabelFontSize: 13, valAxisLabelFontSize: 12, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt', titleFontFace: '+mn-lt',
  valGridLine: { color: 'D5DBE1', size: 0.75 }, catGridLine: { style: 'none' }, showLegend: false, showValue: true, dataLabelColor: HX.dk1, dataLabelFontSize: 13, dataLabelFormatCode: '0.0"%"', dataLabelPosition: 'outEnd',
  showTitle: true, titleFontSize: 15, titleColor: HX.dk2, valAxisMaxVal: 100, valAxisMinVal: 0, valAxisLabelFormatCode: '0"%"' };
const bar = (s, title, labels, vals, x, y, w, h, color, extra = {}) => s.addChart(pres.charts.BAR, [{ name: title, labels, values: vals }],
  Object.assign({ x, y, w, h, barDir: 'bar', title, chartColors: [color], barGapWidthPct: 55, catAxisOrientation: 'maxMin', valAxisHidden: false }, CH, extra));

// ---------------------------------------------------------------- 1 Title
sec('Introduction');
let s = pres.addSlide({ masterName: 'Cover', sectionTitle: SEC });
s.addShape(pres.ShapeType.rect, { x: 8.33, y: 1.15, w: 4.5, h: 5.1, fill: { color: WHITE } });
s.addImage({ path: PH + 'c_title.jpg', x: 8.43, y: 1.25, w: 4.3, h: 4.9 });
s.addText('University of Baghdad', { x: 8.33, y: 6.3, w: 4.5, h: 0.35, fontSize: 12, italic: true, color: 'D9E2EA', align: 'center', isTextBox: true, margin: 0 });
s.addShape(pres.ShapeType.rect, { x: 0, y: 7.2, w: 13.33, h: 0.3, fill: { color: ORANGE } });
s.addText('University of Baghdad  ·  College of Medicine  ·  Department of Biochemistry', { x: 0.6, y: 0.5, w: 7.2, h: 0.4, fontSize: 14, color: 'D9E2EA', isTextBox: true, margin: 0 });
s.addText('Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad', { x: 0.6, y: 1.25, w: 7.2, h: 2.3, fontSize: 36, bold: true, color: WHITE, fontFace: THEME.headFontFace, valign: 'top', isTextBox: true, margin: 0 });
s.addText('An Online Cross-Sectional Survey', { x: 0.6, y: 3.6, w: 7.2, h: 0.5, fontSize: 22, italic: true, color: 'F2C9A8', isTextBox: true, margin: 0 });
s.addText([{ text: 'A graduation research project presented by', options: { color: 'D9E2EA', fontSize: 14, breakLine: true } },
  { text: 'Abdulrahman Jamal Ghazi', options: { breakLine: true } }, { text: 'Mustafa Wamedh Mustafa', options: { breakLine: true } }, { text: 'Yaseen Omar Lutfi', options: { breakLine: true } },
  { text: 'Supervised by', options: { color: 'D9E2EA', fontSize: 14, breakLine: true } }, { text: 'Assist. Prof. Dr. Thikra Hasan Mathkor' }],
  { x: 0.6, y: 4.45, w: 7.2, h: 2.3, fontSize: 18, bold: true, color: WHITE, valign: 'top', paraSpaceAfter: 3, isTextBox: true, margin: 0 });
s.addText('2026', { x: 0.6, y: 6.85, w: 3, h: 0.35, fontSize: 14, color: 'D9E2EA', isTextBox: true, margin: 0 });

// ---------------------------------------------------------------- 2 Outline
s = S('Outline');
[['1', 'Introduction', 'Background, definitions, rationale, aim and hypotheses'], ['2', 'Method', 'Design, participants, questionnaire, statistical analysis'],
 ['3', 'Results', 'Participants, levels, the main association, predictors, medical students'], ['4', 'Discussion', 'Comparison with other studies, strengths and limitations'],
 ['5', 'Conclusions', 'Conclusions and recommendations']].forEach((r, i) => { const y = 1.5 + i * 1.07;
  s.addShape(pres.ShapeType.ellipse, { x: 0.7, y, w: 0.8, h: 0.8, fill: { color: NAVY } });
  s.addText(r[0], { x: 0.7, y, w: 0.8, h: 0.8, fontSize: 24, bold: true, color: WHITE, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
  s.addText(r[1], { x: 1.75, y: y - 0.02, w: 5.4, h: 0.42, fontSize: 22, bold: true, color: NAVY, fontFace: THEME.headFontFace, isTextBox: true, margin: 0 });
  s.addText(r[2], { x: 1.75, y: y + 0.4, w: 5.6, h: 0.4, fontSize: 15, color: INK, isTextBox: true, margin: 0 }); });
pic(s, PH + 'c_campus.jpg', 8.0, 1.5, 4.6, 5.2, 'University of Baghdad campus (photo: alameedy, CC0)');

// ---------------------------------------------------------------- 3 Background
s = S('Background');
bul(s, ['Many people now **search their symptoms online** or **ask an AI chatbot** before they see a doctor',
  'The information is immediate, free and available at any time',
  'For some people, searching **increases worry instead of relieving it**: this is called **cyberchondria**',
  'About **four in five Iraqis are online**, yet no study from Baghdad has examined this',
  'Search logs show that searches for harmless symptoms often **escalate to serious diagnoses**'], 0.5, 1.45, 7.2, 4.6, 19);
note(s, 'Does searching reassure the worried, or feed the worry?', 0.5, 6.05, 7.2, 0.75, ORANGE);
pic(s, PH + 'c_dark.jpg', 8.1, 1.45, 4.6, 5.2, 'Photo: Japanexperterna.se, CC BY-SA 2.0');

// ---------------------------------------------------------------- 4 Concepts
s = S('Health Anxiety and Cyberchondria');
const card = (t, lines, x, col) => { s.addShape(pres.ShapeType.rect, { x, y: 1.45, w: 4.05, h: 3.0, fill: { color: PALE }, line: { color: 'B8C4CE', width: 0.75 } });
  s.addText(t, { x, y: 1.45, w: 4.05, h: 0.55, fontSize: 18, bold: true, color: WHITE, fill: { color: col }, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
  bul(s, lines, x + 0.1, 2.1, 3.85, 2.3, 15); };
card('Health anxiety', ['Persistent worry about having or getting a **serious illness**', 'Kept going by **misreading normal body sensations**', 'A spectrum: mild worry → illness anxiety disorder (DSM-5-TR)'], 0.5, NAVY);
card('Cyberchondria', ['**Excessive, repeated** online health searching that **increases distress**', 'A behavioural pattern, **not a diagnosis**', 'Four dimensions: excessiveness, compulsion, distress, reassurance seeking'], 4.65, ORANGE);
head(s, 'What is already known', 0.5, 4.65, 8.2);
bul(s, ['Two meta-analyses found a strong link (**r = 0.62–0.63**)', 'An experiment showed that searching **raises** health anxiety', 'A Dutch panel study found the relationship runs **both ways**'], 0.5, 5.1, 8.2, 1.8, 16);
pic(s, PH + 'c_laptop.jpg', 8.9, 1.45, 3.93, 2.25);
pic(s, PH + 'c_screen.jpg', 8.9, 3.95, 3.93, 2.32, 'Photos: A. Escamilla; Rawpixel (CC0)');

// ---------------------------------------------------------------- 5 AI chatbots
s = S('From Search Engines to AI Chatbots');
pic(s, PH + 'c_chatgpt.jpg', 0.5, 1.45, 5.6, 3.5, 'Photo: Jernej Furman, CC BY 2.0');
bul(s, ['Chatbots give **fluent, personal, conversational** answers', 'Their answers were rated **more empathetic** than physicians’ answers (Ayers 2023)',
  'About **1 in 5 Americans** has used ChatGPT for health questions', 'They can be asked **again and again**, at any hour',
  'Almost **no studies** separate AI chatbots from ordinary search engines'], 6.4, 1.45, 6.4, 4.0, 18);
note(s, 'The gap: no data from Baghdad, and almost none on AI chatbots', 0.5, 5.6, 12.33, 0.7);
s.addText('Medical students are often said to be more affected (“medical student syndrome”), but the evidence is mixed.', { x: 0.5, y: 6.38, w: 12.33, h: 0.5, fontSize: 15, italic: true, color: INK, align: 'center', isTextBox: true, margin: 0 });

// ---------------------------------------------------------------- 6 Aim & hypotheses
s = S('Aim, Objectives and Hypotheses');
head(s, 'Aim', 0.5, 1.4, 6);
s.addText('To study the relationship between health anxiety and cyberchondria among adults in Baghdad who search for health information online, with a focus on AI chatbots and medical students.', { x: 0.5, y: 1.8, w: 5.9, h: 1.3, fontSize: 16, color: INK, valign: 'top', isTextBox: true, margin: 0 });
head(s, 'Objectives', 0.5, 3.15, 6);
bul(s, ['Describe where people look for health information and what they do after searching', 'Estimate the levels of health anxiety and cyberchondria and their association', 'Compare medical students with other participants'], 0.5, 3.55, 5.9, 2.2, 16);
note(s, 'H1: more health anxiety → more cyberchondria, independently of other factors', 0.5, 5.75, 5.9, 0.6);
note(s, 'H2: medical students have higher health anxiety and cyberchondria', 0.5, 6.4, 5.9, 0.6, ORANGE);
pic(s, FIG + 'fig0a_framework_short.png', 6.7, 1.9, 6.13, 3.41, 'Conceptual framework of the study');

// ---------------------------------------------------------------- 7 Design
sec('Method');
s = S('Method: Design and Participants');
[['Design', 'Analytical cross-sectional online survey'], ['Setting', 'Baghdad; Google Form in Arabic and English'], ['Sampling', 'Convenience and snowball, through social-media and messaging groups'],
 ['Eligibility', 'Adults aged 18 or older who gave electronic consent'], ['Sample', '300 participants (194 needed to detect r = 0.20, power 80%)']].forEach((r, i) => { const y = 1.45 + i * 0.86;
  s.addText(r[0], { x: 0.5, y, w: 2.1, h: 0.72, fontSize: 17, bold: true, color: WHITE, fill: { color: NAVY }, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
  s.addText(r[1], { x: 2.6, y, w: 5.6, h: 0.72, fontSize: 16, color: INK, fill: { color: PALE }, valign: 'middle', isTextBox: true, margin: 10 }); });
s.addText('Reported according to STROBE and CHERRIES. One response per Google account; no missing data.', { x: 0.5, y: 5.85, w: 7.7, h: 0.75, fontSize: 15, italic: true, color: INK, isTextBox: true, margin: 0 });
head(s, 'Ethical considerations', 8.6, 1.4, 4.2);
bul(s, ['Anonymous and voluntary', 'Electronic **informed consent** before any question', 'No names, e-mails or contact details collected', 'No intervention and no patient records'], 8.6, 1.85, 4.25, 3.0, 16);
stat(s, 'n = 300', 'adults in Baghdad, complete data', 8.6, 5.0, 4.2, 1.6);

// ---------------------------------------------------------------- 8 Questionnaire
s = S('Method: The Questionnaire');
tbl(s, ['Part', 'Content', 'Scoring'], [
  ['1', 'Consent and socio-demographic data', 'Age, gender, education, study or work, chronic condition'],
  ['2', 'Digital health-information seeking', 'Tools used, main AI chatbot, motives, trust (1–5)'],
  ['3', 'Short Health Anxiety Inventory (SHAI-14)', '14 items, each 0–3; total 0–42'],
  ['4', 'Cyberchondria Severity Scale (CSS-12)', '12 items, each 1–5; total 12–60; four dimensions'],
  ['5', 'Behaviour after searching', 'Actions taken, telling the doctor, effect on the relationship']], 0.5, 1.45, 12.33, [0.9, 5.2, 6.23], 18, [2, 3]);
head(s, 'Definitions', 0.5, 4.7, 6);
bul(s, ['**Elevated health anxiety:** SHAI-14 score of 18 or more (a screening result, not a diagnosis)', '**High cyberchondria:** CSS-12 score above 33 (the upper third of the sample)',
  '**AI chatbot user:** reported using an AI chatbot for health information'], 0.5, 5.15, 12.33, 1.8, 17);

// ---------------------------------------------------------------- 9 Statistics
s = S('Method: Statistical Analysis');
tbl(s, ['Purpose', 'Test used', 'Reason'], [
  ['Describe the sample', 'n (%), mean ± SD, median (IQR), 95% CI', 'Categorical and continuous variables'],
  ['Reliability of the scales', 'Cronbach’s alpha', 'Internal consistency'],
  ['Normality', 'Shapiro–Wilk', 'Scores were not normally distributed'],
  ['Score between groups', 'Mann–Whitney U, Kruskal–Wallis H', 'Non-parametric alternatives to t-test and ANOVA'],
  ['Two categorical variables', 'Chi-square or Fisher’s exact, Cramér’s V', 'Fisher when expected counts are small'],
  ['Two scores', 'Pearson r, Spearman rho, partial r', 'Strength of association, with adjustment'],
  ['Predictors of cyberchondria', 'Hierarchical multiple linear regression', 'Outcome is a score; three blocks'],
  ['Predictors of elevated health anxiety', 'Binary logistic regression', 'Outcome is yes or no']], 0.5, 1.45, 12.33, [3.6, 4.6, 4.13], 17);
s.addText('IBM SPSS Statistics version 26; two-sided p < 0.05 was considered significant.', { x: 0.5, y: 6.4, w: 12.33, h: 0.45, fontSize: 16, italic: true, color: INK, isTextBox: true, margin: 0 });

// ---------------------------------------------------------------- 10 Participants
sec('Results');
s = S('Results: The Participants');
[['62.3%', 'aged 20–29 years'], ['56.3%', 'female'], ['44.0%', 'medical students'], ['63.3%', 'health-related background']].forEach((r, i) => stat(s, r[0], r[1], 0.5 + i * 3.11, 1.45, 3.0, 1.55));
tbl(s, ['Characteristic', 'Result'], [['Age 18–19 years', '18.7%'], ['Chronic medical condition', '21.7%'], ['Answered in Arabic', '70.7%'], ['Answered in English', '29.3%'], ['Missing data', 'None']], 0.5, 3.3, 5.6, [3.7, 1.9], 16);
s.addChart(pres.charts.DOUGHNUT, [{ name: 'Study or work', labels: ['Medical students', 'Other health-related', 'Non-health'], values: [44.0, 19.3, 36.7] }],
  { x: 6.5, y: 3.15, w: 6.3, h: 3.8, holeSize: 50, chartColors: [HX.dk2, HX.accent2, 'A9B7C3'], showLegend: true, legendPos: 'r', legendFontSize: 14, legendFontFace: '+mn-lt', legendColor: HX.dk1,
    showPercent: true, showValue: false, dataLabelColor: 'FFFFFF', dataLabelFontSize: 14, dataLabelFontBold: true, dataLabelFontFace: '+mn-lt', showTitle: true, title: 'Study or work background', titleFontSize: 15, titleColor: HX.dk2, titleFontFace: '+mn-lt' });

// ---------------------------------------------------------------- 11 Tools & motives
s = S('Results: Where People Search and Why');
bar(s, 'Tools used for health information', ['AI chatbots', 'Search engines', 'Medical platforms', 'Social media'], [88.7, 56.3, 18.3, 10.7], 0.5, 1.4, 6.1, 4.3, HX.dk2);
bar(s, 'Motives for searching', ['Convenience', '“Do I need a doctor?”', 'Instant reassurance'], [80.0, 57.7, 51.0], 6.75, 1.4, 6.1, 4.3, HX.accent2);
note(s, 'AI chatbots were the most used source: 88.7%. ChatGPT was the main chatbot (59.3%), then Gemini (23.7%)', 0.5, 5.9, 12.33, 0.85);

// ---------------------------------------------------------------- 12 Behaviour
s = S('Results: What People Do After Searching');
bar(s, 'Behaviour after searching', ['Delayed or skipped care (reassured)', 'Ignored the symptom', 'Visited several doctors', 'Sought urgent care'], [34.7, 30.0, 25.3, 22.0], 0.5, 1.4, 7.0, 4.0, HX.dk2, { valAxisMaxVal: 50 });
s.addChart(pres.charts.PIE, [{ name: 'Tell the doctor', labels: ['Always', 'Sometimes', 'Never'], values: [27.0, 41.3, 31.7] }],
  { x: 7.7, y: 1.4, w: 5.1, h: 4.0, chartColors: [HX.accent3, 'A9B7C3', HX.accent2], showLegend: true, legendPos: 'b', legendFontSize: 13, legendFontFace: '+mn-lt', legendColor: HX.dk1, showPercent: true, showValue: false,
    dataLabelColor: 'FFFFFF', dataLabelFontSize: 14, dataLabelFontBold: true, dataLabelFontFace: '+mn-lt', showTitle: true, title: 'Do you tell your doctor what you searched?', titleFontSize: 15, titleColor: HX.dk2, titleFontFace: '+mn-lt' });
stat(s, '34.7%', 'delayed care because they felt reassured', 0.5, 5.55, 3.95, 1.35, ORANGE);
stat(s, '31.7%', 'never tell their doctor', 4.69, 5.55, 3.95, 1.35, ORANGE);
stat(s, '34.7%', 'said searching strained the relationship', 8.88, 5.55, 3.95, 1.35, ORANGE);

// ---------------------------------------------------------------- 13 Levels
s = S('Results: Levels of Health Anxiety and Cyberchondria');
tbl(s, ['Scale', 'Mean ± SD', 'Median (IQR)', 'Cronbach’s alpha'], [
  ['SHAI-14 (0–42)', '12.35 ± 5.83', '12 (8–16)', '0.81'], ['CSS-12 (12–60)', '28.86 ± 8.36', '29 (23–34)', '0.86'],
  ['Excessiveness (3–15)', '9.66 ± 2.94', '10 (8–12)', '0.77'], ['Compulsion (3–15)', '5.00 ± 2.58', '4 (3–6)', '0.88'],
  ['Distress (3–15)', '7.24 ± 2.74', '7 (5–9)', '0.76'], ['Reassurance seeking (3–15)', '6.96 ± 2.81', '7 (5–9)', '0.76']], 0.5, 1.45, 8.3, [3.2, 1.8, 1.7, 1.6], 15, [0, 1]);
stat(s, '19.0%', 'elevated health anxiety (SHAI-14 ≥ 18); 95% CI 15.0–23.8%', 9.1, 1.45, 3.73, 2.0, ORANGE);
tbl(s, ['Cut-off', 'n', '%'], [['≥ 18', '57', '19.0'], ['≥ 22', '22', '7.3'], ['≥ 29', '2', '0.7']], 9.1, 3.65, 3.73, [1.5, 1.0, 1.23], 15);
bul(s, ['Both scales were **reliable**, equally in Arabic and English', 'People **search a lot** (excessiveness highest) but searching rarely disrupts daily life (compulsion lowest)',
  'About **one in five** screened in the elevated range: a screening result, **not a diagnosis**'], 0.5, 5.0, 8.3, 1.95, 16);

// ---------------------------------------------------------------- 14 Main association
s = S('Results: The Main Association (H1)');
pic(s, FIG + 'fig1_scatter_shai_css.png', 0.5, 1.4, 6.6, 4.71, 'Each dot is one participant; the line rises with health anxiety');
stat(s, 'r = 0.47', '95% CI 0.38–0.55; p < 0.001', 7.4, 1.4, 5.43, 1.4, ORANGE);
tbl(s, ['CSS-12 dimension', 'Pearson r', 'Spearman rho'], [['Total score', '0.47', '0.47'], ['Excessiveness', '0.46', '0.45'], ['Distress', '0.45', '0.44'], ['Compulsion', '0.25', '0.32'], ['Reassurance seeking', '0.24', '0.23']], 7.4, 2.95, 5.43, [2.63, 1.3, 1.5], 15, [0]);
bul(s, ['Health anxiety accounts for about **22%** of the differences', 'After adjustment for other factors: **partial r = 0.48**'], 7.4, 5.2, 5.43, 1.1, 15);
note(s, 'More health anxiety, more cyberchondria: H1 is supported', 0.5, 6.42, 12.33, 0.55, C.accent3);

// ---------------------------------------------------------------- 15 Groups
s = S('Results: Which Groups Differ');
tbl(s, ['Variable', 'Health anxiety (median)', 'p', 'Cyberchondria (median)', 'p'], [
  ['Chronic condition (yes vs no)', '14 vs 11', '0.004', 'similar', '0.435'],
  ['Motive: instant reassurance', '13 vs 10', '< 0.001', 'similar', '0.085'],
  ['AI chatbot user (yes vs no)', 'higher', '0.008', '30 vs 23.5', '< 0.001'],
  ['Social-media user', 'higher', '0.001', 'higher', '0.021'],
  ['Age group', 'younger higher', '0.008', 'no difference', 'ns'],
  ['Gender; language', 'no difference', 'ns', 'no difference', 'ns']], 0.5, 1.45, 7.6, [2.75, 1.6, 0.85, 1.55, 0.85], 14, [2]);
bul(s, ['Mann–Whitney and Kruskal–Wallis tests; medians reported', 'Post-hoc: **younger students** were the most health-anxious', 'High cyberchondria: **52.6%** with elevated health anxiety vs **23.0%** without (OR 3.71)'], 0.5, 4.85, 7.6, 2.1, 15);
pic(s, FIG + 'fig6_css_by_tool.png', 8.4, 1.6, 4.43, 2.92, 'Cyberchondria by tool profile');
stat(s, '30 vs 23.5', 'median cyberchondria: AI users vs non-users', 8.4, 5.1, 4.43, 1.6, ORANGE);

// ---------------------------------------------------------------- 16 Regression
s = S('Results: Independent Predictors of Cyberchondria');
s.addChart(pres.charts.BAR, [{ name: 'R²', labels: ['1. Socio-demographic', '2. + Digital use', '3. + Health anxiety'], values: [3.0, 13.3, 31.7] }],
  Object.assign({ x: 0.5, y: 1.4, w: 5.3, h: 4.2, barDir: 'col', title: 'Variance explained (R²) by block', chartColors: [HX.dk2], barGapWidthPct: 60 }, CH, { valAxisMaxVal: 40, catAxisLabelFontSize: 12 }));
tbl(s, ['Predictor (final model)', 'B (95% CI)', 'Beta', 'p'], [['Health anxiety (per SHAI point)', '0.68 (0.53–0.84)', '0.48', '< 0.001'], ['AI chatbot user', '5.33 (2.57–8.09)', '0.20', '< 0.001'],
  ['Age 30–39 (vs 20–29)', '6.27 (2.42–10.11)', '0.19', '0.001'], ['Age 40 or older', '3.98 (0.16–7.80)', '0.15', '0.041'], ['Gender, work, chronic condition, language, trust, motives', 'not significant', '', 'ns']],
  6.1, 1.45, 6.73, [3.0, 1.95, 0.75, 1.03], 14, [0, 1]);
bul(s, ['Health anxiety **added 18.4%** after all other factors', 'AI chatbot users scored **5.3 points higher**, independently of health anxiety', 'The full model explained **32%** of the differences'], 6.1, 4.55, 6.73, 1.6, 15);
note(s, 'Health anxiety is the strongest predictor of cyberchondria (beta = 0.48)', 0.5, 6.25, 12.33, 0.62);

// ---------------------------------------------------------------- 17 Logistic
s = S('Results: Predictors of Elevated Health Anxiety');
pic(s, FIG + 'fig7_forest_HA_simple.png', 0.5, 1.45, 7.2, 4.07, 'Adjusted odds ratios with 95% CI; vertical line at 1 = no effect');
tbl(s, ['Predictor', 'AOR (95% CI)', 'p'], [['Cyberchondria (per 1 SD)', '3.12 (2.11–4.62)', '< 0.001'], ['Motive: instant reassurance', '3.83 (1.80–8.18)', '< 0.001'], ['Older age group (per step)', '0.61 (0.39–0.93)', '0.023']], 8.0, 1.45, 4.83, [2.3, 1.63, 0.9], 14);
bul(s, ['Odds **triple** with each SD of cyberchondria', 'Reassurance seekers: odds almost **four times** higher', '**Older age is protective**', 'Model fit: Hosmer–Lemeshow p = 0.50; **AUC = 0.83**'], 8.0, 3.45, 4.83, 2.6, 15);
note(s, 'Higher cyberchondria, searching for reassurance and younger age go with elevated health anxiety', 0.5, 6.15, 12.33, 0.7);

// ---------------------------------------------------------------- 18 Medical students
s = S('Results: Medical Students Compared With Others (H2)');
tbl(s, ['Measure', 'Medical students (n = 132)', 'Others (n = 168)', 'p', 'Adjusted p'], [
  ['SHAI-14, median (IQR)', '12.5 (10–17)', '11 (7–15)', '0.004', '0.081'], ['Elevated health anxiety', '23.5%', '15.5%', '0.079', '0.238'],
  ['CSS-12, median (IQR)', '29 (23–34)', '29 (23–34)', '0.989', '0.627'], ['High cyberchondria', '28.0%', '29.2%', '0.829', '0.771']], 0.5, 1.45, 12.33, [3.4, 3.0, 2.6, 1.5, 1.83], 18, [0]);
bul(s, ['Before adjustment, medical students had **higher health anxiety**', 'After adjusting for **age**, gender, chronic condition and language, the difference was **no longer significant**',
  'Cyberchondria was **identical** in the two groups', 'Medical students are younger, and younger people were more health-anxious'], 0.5, 4.0, 7.9, 2.3, 16);
s.addShape(pres.ShapeType.rect, { x: 8.7, y: 4.0, w: 4.13, h: 2.75, fill: { color: ORANGE } });
s.addText([{ text: 'H2 is not supported', options: { fontSize: 24, bold: true, breakLine: true } }, { text: 'Age, not studying medicine, explained the difference', options: { fontSize: 16 } }],
  { x: 8.85, y: 4.0, w: 3.83, h: 2.75, color: WHITE, align: 'center', valign: 'middle', isTextBox: true, margin: 0, fontFace: THEME.headFontFace });

// ---------------------------------------------------------------- 19 Discussion
sec('Discussion and conclusions');
s = S('Discussion: Comparison With Other Studies');
tbl(s, ['Finding', 'Our study', 'Other studies', 'Explanation'], [
  ['Health anxiety–cyberchondria link', 'r = 0.47', 'r = 0.62–0.63 (two meta-analyses)', 'Low and narrow health anxiety in our sample; short CSS-12'],
  ['AI chatbot use for health', '88.7%', 'About 20% in US surveys', 'Our sample is young, educated and online'],
  ['AI use and cyberchondria', 'B = 5.33, p < 0.001', 'Very few studies', 'Chatbots can be asked repeatedly; may encourage reassurance seeking'],
  ['Medical students', 'No difference after adjustment', 'Palestine: least common in medical students; Egypt: high levels', 'Age explained the difference in our sample'],
  ['Hiding searches from the doctor', '31.7% never tell', 'Open discussion strengthens the relationship', 'Fear of being judged']], 0.5, 1.45, 12.33, [3.0, 2.2, 3.4, 3.73], 16);
note(s, 'First study of cyberchondria in Baghdad, and one of the few to examine AI chatbots separately', 0.5, 6.1, 12.33, 0.7);

// ---------------------------------------------------------------- 20 Strengths & limitations
s = S('Strengths and Limitations');
s.addText('Strengths', { x: 0.5, y: 1.45, w: 5.9, h: 0.55, fontSize: 19, bold: true, color: WHITE, fill: { color: C.accent3 }, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
s.addShape(pres.ShapeType.rect, { x: 0.5, y: 2.0, w: 5.9, h: 4.8, fill: { color: PALE }, line: { color: 'B8C4CE', width: 0.75 } });
bul(s, ['Validated and reliable scales (alpha 0.81 and 0.86)', 'Questionnaire in Arabic and English', 'AI chatbots studied separately from search engines', 'Complete data, no missing answers', 'Results adjusted for confounders'], 0.65, 2.15, 5.6, 4.5, 17);
s.addText('Limitations', { x: 6.93, y: 1.45, w: 5.9, h: 0.55, fontSize: 19, bold: true, color: WHITE, fill: { color: C.accent6 }, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
s.addShape(pres.ShapeType.rect, { x: 6.93, y: 2.0, w: 5.9, h: 4.8, fill: { color: PALE }, line: { color: 'B8C4CE', width: 0.75 } });
bul(s, ['**Cross-sectional:** shows association, not cause', '**Convenience online sample**, many medical students: percentages cannot be generalised', 'Arabic wording not formally back-translated', 'Self-reported answers', 'Small group of non-users of AI (n = 34)'], 7.08, 2.15, 5.6, 4.5, 17);

// ---------------------------------------------------------------- 21 Conclusions
s = S('Conclusions');
['AI chatbots, mainly ChatGPT, are now a leading source of health information (88.7%)', 'About one in five participants had elevated health anxiety on screening (19.0%)',
 'Health anxiety and cyberchondria are moderately associated, independently of other factors (r = 0.47)', 'AI chatbot use was associated with higher cyberchondria',
 'Medical students were not at higher risk once age was considered', 'One in three delayed care when reassured, and one in three never tell their doctor'].forEach((t, i) => { const y = 1.42 + i * 0.92;
  s.addShape(pres.ShapeType.ellipse, { x: 0.5, y: y + 0.06, w: 0.66, h: 0.66, fill: { color: i === 2 ? ORANGE : NAVY } });
  s.addText(String(i + 1), { x: 0.5, y: y + 0.06, w: 0.66, h: 0.66, fontSize: 20, bold: true, color: WHITE, align: 'center', valign: 'middle', isTextBox: true, margin: 0 });
  s.addText(t, { x: 1.35, y, w: 11.45, h: 0.78, fontSize: 18, bold: i === 2, color: INK, fill: { color: PALE }, valign: 'middle', isTextBox: true, margin: 10 }); });

// ---------------------------------------------------------------- 22 Recommendations
s = S('Recommendations');
tbl(s, ['For', 'Recommendation'], [
  ['Clinicians', 'Ask every patient, without judgement, what they searched or asked an AI. Treat repeated searching and reassurance seeking as possible signs of health anxiety'],
  ['Medical education', 'Teach digital and AI health literacy in the medical curriculum'],
  ['Ministry of Health', 'Arabic health-literacy campaigns and reliable Arabic sources for symptom advice'],
  ['AI developers', 'Answers that avoid escalating to rare diagnoses and encourage appropriate consultation'],
  ['Future research', 'Longitudinal studies, random samples and formally adapted Arabic scales']], 0.5, 1.45, 7.6, [2.1, 5.5], 15);
pic(s, PH + 'c_doctor.jpg', 8.4, 1.45, 4.43, 5.24, 'Photo: National Cancer Institute (public domain)');

// ---------------------------------------------------------------- 23 References
s = S('Selected References');
s.addText(['White RW, Horvitz E. Cyberchondria: studies of the escalation of medical concerns in web search. ACM Trans Inf Syst. 2009.',
  'Starcevic V, Berle D. Cyberchondria: towards a better understanding of excessive health-related internet use. Expert Rev Neurother. 2013.',
  'Salkovskis PM, et al. The Health Anxiety Inventory. Psychol Med. 2002.', 'McElroy E, et al. The CSS-12: a brief version of the Cyberchondria Severity Scale. Cyberpsychol Behav Soc Netw. 2019.',
  'McMullan RD, et al. The relationships between health anxiety, online health information seeking, and cyberchondria: meta-analysis. J Affect Disord. 2019.',
  'Schenkel SK, et al. Conceptualizations of cyberchondria and relations to the anxiety spectrum: meta-analysis. J Med Internet Res. 2021.',
  'Ayers JW, et al. Comparing physician and AI chatbot responses to patient questions. JAMA Intern Med. 2023.', 'Österman S, et al. The 14-item Short Health Anxiety Inventory as a screening tool. 2022.']
  .map((t, i, a) => ({ text: t, options: { bullet: { type: 'number' }, paraSpaceAfter: 6, breakLine: i < a.length - 1 } })), { x: 0.5, y: 1.4, w: 12.33, h: 4.75, fontSize: 16, color: INK, valign: 'top', isTextBox: true, margin: 4 });
s.addText('The full list of 31 references (Vancouver style) is in the thesis. Photographs: Wikimedia Commons – ChatGPT phone by Jernej Furman (CC BY 2.0); person with phone by Japanexperterna.se (CC BY-SA 2.0); University of Baghdad by alameedy (CC0) and Ahmed z1987 (CC BY-SA 4.0); doctor and patient by the National Cancer Institute (public domain); others CC0.',
  { x: 0.5, y: 6.2, w: 12.33, h: 0.75, fontSize: 10, italic: true, color: '555555', valign: 'top', isTextBox: true, margin: 0 });

// ---------------------------------------------------------------- 24 Thank you
s = pres.addSlide({ masterName: 'Cover', sectionTitle: SEC });
s.addImage({ path: PH + 'c_end.jpg', x: 0, y: 0, w: 13.33, h: 7.5 });
s.addShape(pres.ShapeType.rect, { x: 0, y: 2.3, w: 13.33, h: 2.9, fill: { color: NAVY, transparency: 12 } });
s.addText('Thank You', { x: 0.5, y: 2.5, w: 12.33, h: 1.3, fontSize: 60, bold: true, color: WHITE, align: 'center', valign: 'middle', fontFace: THEME.headFontFace, isTextBox: true, margin: 0 });
s.addText('Questions and discussion', { x: 0.5, y: 3.85, w: 12.33, h: 0.6, fontSize: 26, italic: true, color: 'F2C9A8', align: 'center', isTextBox: true, margin: 0 });
s.addText('College of Medicine · University of Baghdad', { x: 0.5, y: 4.5, w: 12.33, h: 0.45, fontSize: 16, color: 'D9E2EA', align: 'center', isTextBox: true, margin: 0 });

// pptxgenjs repeats a paragraph-properties element before later runs of a bulleted paragraph, which drops the bullet: remove the repeats
const fixBullets = async f => { const JSZip = require('jszip'), fs = require('fs'); const z = await JSZip.loadAsync(fs.readFileSync(f));
  for (const n of Object.keys(z.files).filter(n => /^ppt\/slides\/slide\d+\.xml$/.test(n)))
    z.file(n, (await z.file(n).async('string')).replace(/<\/a:r><a:pPr indent="0" marL="0"><a:buNone\/><\/a:pPr>/g, '</a:r>'));
  Object.keys(z.files).filter(n => z.files[n].dir).forEach(n => delete z.files[n]);
  fs.writeFileSync(f, await z.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' })); };
(async () => { await pres.writeFile({ fileName: FILE }); await applyTheme(FILE, THEME); await fixBullets(FILE); console.log('wrote', FILE); })();
