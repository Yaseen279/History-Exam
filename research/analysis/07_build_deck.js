// Defence presentation (PowerPoint) built from the analysis outputs.
// Usage: NODE_PATH=<node_modules with pptxgenjs> node 07_build_deck.js <numbers.json> <out.pptx> <apply_theme.js path>
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const [, , NUMS, OUTFILE, THEME_JS] = process.argv;
const N = JSON.parse(fs.readFileSync(NUMS, "utf8"));
const { applyTheme } = require(THEME_JS);
const FIG = N.figdir;

const THEME = {
  name: "Cyberchondria Baghdad",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1B1B", lt1: "FFFFFF", dk2: "0B2545", lt2: "EEF3FA",
    accent1: "2A78D6", accent2: "EB6834", accent3: "1BAF7A", accent4: "EDA100", accent5: "6250D6", accent6: "E34948",
    hlink: "2A78D6", folHlink: "6250D6",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.title = "Artificial Intelligence, Search Engines, and Cyberchondria";
pres.subject = "Graduation research defence";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333, H = 7.5, M = 0.6;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.9, w: W - 2 * M, h: 2.2, fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", fontFace: THEME.headFontFace }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.35, w: W - 2 * M, h: 1.6, fontSize: 18, color: C.background2, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECTION",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.6, w: W - 2 * M, h: 1.4, fontSize: 40, bold: true, color: C.background1, align: "left", fontFace: THEME.headFontFace }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.0, w: W - 2 * M, h: 1.0, fontSize: 18, color: C.background2 }, text: "" } },
  ],
  slideNumber: { x: W - 1.0, y: H - 0.5, w: 0.6, h: 0.3, fontSize: 10, color: C.background2, align: "right" },
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.85, fontSize: 30, bold: true, color: C.text2, valign: "middle", align: "left", fontFace: THEME.headFontFace }, text: "" } },
    { text: { text: "AI, search engines and cyberchondria · Baghdad", options: { x: M, y: H - 0.45, w: 7, h: 0.3, fontSize: 10, color: "898781" } } },
  ],
  slideNumber: { x: W - 1.0, y: H - 0.45, w: 0.6, h: 0.3, fontSize: 10, color: "898781", align: "right" },
});

// ---------------------------------------------------------------- helpers
let sec = "";
function slide(master, title, notes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: sec });
  if (title) s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function section(t) { sec = t; pres.addSection({ title: t }); }
function txt(s, text, o) { s.addText(text, { isTextBox: true, margin: 0, fontSize: 16, color: C.text1, valign: "top", ...o }); }
function card(s, x, y, w, h, name, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { color: fill || C.background2 }, objectName: name });
}
function stat(s, x, y, w, value, label, color, size) {
  card(s, x, y, w, 1.75, "stat " + label);
  txt(s, value, { x: x + 0.25, y: y + 0.2, w: w - 0.5, h: 0.85, fontSize: size || 40, bold: true, color: color || C.accent1, fontFace: THEME.headFontFace, valign: "middle" });
  txt(s, label, { x: x + 0.25, y: y + 1.05, w: w - 0.5, h: 0.6, fontSize: 14, color: C.text1 });
}
function circleNum(s, x, y, n, color) {
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.55, h: 0.55, fill: { color: color || C.accent1 }, line: { color: color || C.accent1 }, objectName: "marker " + n });
  s.addText(String(n), { isTextBox: true, x, y, w: 0.55, h: 0.55, margin: 0, align: "center", valign: "middle", fontSize: 18, bold: true, color: C.background1 });
}
function fig(s, file, x, y, maxW, maxH) {
  const a = N.aspect[file];
  let w = maxW, h = w / a;
  if (h > maxH) { h = maxH; w = h * a; }
  s.addImage({ path: `${FIG}/${file}`, x: x + (maxW - w) / 2, y, w, h, altText: file });
}
function bullets(s, items, o) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { isTextBox: true, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0.05, ...o });
}
const chartBase = (title) => ({
  showTitle: true, title, titleFontSize: 14, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFormatCode: '0"%"', dataLabelFontFace: "+mn-lt",
  catAxisLabelColor: "52514E", catAxisLabelFontSize: 13, catAxisLabelFontFace: "+mn-lt",
  valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false,
  barDir: "bar", barGapWidthPct: 60, catAxisOrientation: "maxMin",
});
const pct = (v) => Math.round(v * 10) / 10;

// ---------------------------------------------------------------- 1 Title
section("Introduction");
let s = slide("TITLE_DARK", "Artificial Intelligence, Search Engines, and Cyberchondria", null);
s.addText("A Study of Patient Pre-Consultation Behavior in Baghdad\n[Student names]  ·  Supervisor: [name]  ·  [College], [Year]", { placeholder: "body" });
s.addNotes("Introduce the title and the team. 'Today we present our study on how people in Baghdad use search engines and AI chatbots before seeing a doctor, and how this relates to health anxiety and cyberchondria.'");

// ---------------------------------------------------------------- 2 Why this matters
s = slide("CONTENT", "Why this study matters",
  "Everyone searches symptoms online; now AI chatbots answer them conversationally. For some people searching makes worry worse: cyberchondria. Health anxiety increases healthcare use and costs. Iraq has over 80% Internet penetration but no data on this, and AI chatbots had not been studied next to search engines.");
[["Everyone searches", "Looking up symptoms before seeing a doctor is now routine; more than 80% of Iraqis are online."],
 ["AI now answers", "ChatGPT and Gemini give fluent, personal, endlessly available answers about symptoms."],
 ["Searching can backfire", "For some, searching escalates worry instead of relieving it: cyberchondria."],
 ["No data from Iraq", "No study had linked health anxiety, cyberchondria and AI use in Baghdad."]].forEach(([h, b], i) => {
  const x = M + i * 3.07;
  card(s, x, 1.6, 2.85, 3.9, "reason " + (i + 1));
  circleNum(s, x + 0.3, 1.9, i + 1, i === 2 ? C.accent2 : C.accent1);
  txt(s, h, { x: x + 0.3, y: 2.7, w: 2.3, h: 0.9, fontSize: 20, bold: true, color: C.text2, fontFace: THEME.headFontFace });
  txt(s, b, { x: x + 0.3, y: 3.65, w: 2.3, h: 2.3, fontSize: 15 });
});

// ---------------------------------------------------------------- 3 Key concepts
s = slide("CONTENT", "Key concepts: health anxiety and cyberchondria",
  "Health anxiety: persistent worry about having a serious illness, kept going by misinterpreting sensations and seeking reassurance. Cyberchondria: excessive online searching that increases distress. Theory: a cycle in which anxiety drives searching, searching drives distress, and distress drives reassurance seeking. Our question was whether our data fit this cycle.");
card(s, M, 1.5, 5.6, 2.15, "def HA");
txt(s, "Health anxiety", { x: M + 0.3, y: 1.7, w: 5, h: 0.5, fontSize: 20, bold: true, color: C.accent1 });
txt(s, "Persistent worry about having a serious illness, maintained by misreading normal sensations and by reassurance seeking. Measured with SHAI-14 (0–42).", { x: M + 0.3, y: 2.25, w: 5.0, h: 1.3, fontSize: 15 });
card(s, M, 3.95, 5.6, 2.15, "def CC");
txt(s, "Cyberchondria", { x: M + 0.3, y: 4.15, w: 5, h: 0.5, fontSize: 20, bold: true, color: C.accent2 });
txt(s, "Excessive or repeated online health searching that increases distress. Measured with CSS-12 (12–60): excessiveness, compulsion, distress, reassurance.", { x: M + 0.3, y: 4.7, w: 5.0, h: 1.3, fontSize: 15 });
// cycle diagram
const cyc = [["Health anxiety", 9.3, 1.5], ["Excessive searching", 11.1, 3.3], ["Post-search distress", 9.3, 5.1], ["Reassurance seeking", 7.5, 3.3]];
cyc.forEach(([t, cx, cy], i) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx - 0.95, y: cy, w: 1.9, h: 0.95, rectRadius: 0.1, fill: { color: i === 0 ? C.accent1 : C.background2 }, line: { color: C.accent1, width: 1.5 }, objectName: "cycle " + t });
  s.addText(t, { isTextBox: true, x: cx - 0.95, y: cy, w: 1.9, h: 0.95, margin: 0.05, align: "center", valign: "middle", fontSize: 14, bold: true, color: i === 0 ? C.background1 : C.text2 });
});
const arr = (x1, y1, x2, y2) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1, line: { color: "52514E", width: 2, endArrowType: "triangle" } });
arr(10.25, 2.0, 11.1, 3.25); arr(11.1, 4.3, 10.25, 5.55); arr(8.35, 5.55, 7.5, 4.3); arr(7.5, 3.25, 8.35, 2.0);
txt(s, "The proposed cycle we tested", { x: 7.0, y: 6.2, w: 5.6, h: 0.4, fontSize: 13, italic: true, color: "52514E", align: "center" });

// ---------------------------------------------------------------- 4 Aim & hypotheses
s = slide("CONTENT", "Aim and hypotheses",
  "State the aim, then the four hypotheses briefly. Mention we also described tools, motives and behaviours.");
card(s, M, 1.5, 4.6, 4.7, "aim", C.text2);
txt(s, "Aim", { x: M + 0.35, y: 1.8, w: 4, h: 0.5, fontSize: 20, bold: true, color: C.background1 });
txt(s, "To study the relationship between health anxiety and cyberchondria, and their correlates, among adults in Baghdad who search for health information online, with attention to AI chatbots and pre-consultation behaviour.", { x: M + 0.35, y: 2.4, w: 3.9, h: 3.5, fontSize: 16, color: C.background1 });
const hyp = [["H1", "Health anxiety is positively associated with cyberchondria, most with distress and excessiveness"],
  ["H2", "The association is independent of demographic and digital-use factors"],
  ["H3", "Excessive searching mediates the link between health anxiety and post-search distress"],
  ["H4", "Higher cyberchondria goes with care-seeking and a strained doctor relationship"]];
hyp.forEach(([k, t], i) => {
  const y = 1.5 + i * 1.2;
  circleNum(s, 5.65, y + 0.15, k, C.accent1);
  txt(s, t, { x: 6.45, y: y + 0.05, w: 6.2, h: 1.0, fontSize: 16, valign: "middle" });
});

// ---------------------------------------------------------------- 5 Methods
section("Methods");
s = slide("SECTION", "Methods", null); s.addText("Design, sample, instruments and analysis", { placeholder: "body" });
s = slide("CONTENT", "How we did it",
  `Cross-sectional online survey in Baghdad, ${N.d0} to ${N.d1}. Convenience and snowball sampling, n = ${N.n}. Sample size: ${N.nreq} needed to detect r = 0.20 with 80% power; our sample of ${N.n} exceeds this. Bilingual Google Form with SHAI-14 and CSS-12. Analysis: reliability and CFA, correlations, non-parametric tests with FDR correction, robust regression, logistic models, bootstrapped mediation and moderation, sensitivity analyses.`);
[["Design", "Analytical cross-sectional online survey (STROBE, CHERRIES)"],
 ["Setting & time", `Baghdad · ${N.d0} – ${N.d1}`],
 ["Sample", `n = ${N.n}, convenience + snowball; a priori ${N.nreq} needed to detect r = 0.20`],
 ["Instruments", "Bilingual Google Form · SHAI-14 (health anxiety) · CSS-12 (cyberchondria, 4 subscales)"],
 ["Analysis", "Reliability & CFA · correlations · FDR-corrected tests · robust and logistic regression · bootstrapped mediation"],
 ["Ethics", "Anonymous, voluntary, e-consent before any question · [approval no.]"]].forEach(([h, b], i) => {
  const x = M + (i % 3) * 4.1, y = 1.5 + Math.floor(i / 3) * 2.45;
  card(s, x, y, 3.9, 2.25, "method " + h);
  txt(s, h, { x: x + 0.3, y: y + 0.25, w: 3.3, h: 0.45, fontSize: 18, bold: true, color: C.accent1 });
  txt(s, b, { x: x + 0.3, y: y + 0.8, w: 3.3, h: 1.35, fontSize: 15 });
});

// ---------------------------------------------------------------- 6 Participants
section("Results");
s = slide("SECTION", "Results", null); s.addText("What we found", { placeholder: "body" });
s = slide("CONTENT", "Participants: young, mostly students",
  `${N.n} adults. ${N.age20} aged 20–29, ${N.fem} female, ${N.med} medical students, ${N.chron} with a chronic condition. Acknowledge that the sample is young and heavy in medical students: this limits generalisation of percentages, but associations were the same across groups.`);
[[String(N.n), "participants"], [N.age20, "aged 20–29"], [N.fem, "female"], [N.med, "medical students"], [N.chron, "chronic condition"]].forEach(([v, l], i) => {
  stat(s, M + i * 2.46, 2.0, 2.26, v, l);
});
txt(s, `Health-related background: ${N.hb} · Answered mainly in Arabic: ${N.ar}`, { x: M, y: 4.2, w: 12, h: 0.5, fontSize: 16, color: "52514E" });
card(s, M, 4.95, 12.1, 1.3, "caveat sample", "FDEEE7");
txt(s, "Interpret percentages with care: the sample over-represents young people and medical students. Associations, however, were consistent across every subgroup.", { x: M + 0.3, y: 5.1, w: 11.5, h: 1.0, fontSize: 16, valign: "middle" });

// ---------------------------------------------------------------- 7 How people search
s = slide("CONTENT", "AI chatbots are now the main gateway",
  `${N.ai} use AI chatbots versus ${N.se} search engines; ${N.ai_only} use AI without any search engine. ChatGPT dominates. Main motives: convenience, deciding whether a doctor is needed, and instant reassurance.`);
s.addChart(pres.charts.BAR, [{ name: "Tools", labels: ["AI chatbots", "Search engines", "Medical platforms", "Social media"], values: N.tools.map(pct) }],
  { x: M, y: 1.4, w: 5.9, h: 4.6, ...chartBase("Tools used to look up symptoms (%)"), chartColors: [HEX.accent1] });
s.addChart(pres.charts.BAR, [{ name: "Motives", labels: ["Convenience", "Is a doctor needed?", "Instant reassurance", "Self-diagnosis", "Cost / logistics"], values: N.motives.map(pct) }],
  { x: 6.8, y: 1.4, w: 5.9, h: 4.6, ...chartBase("Motivations for searching (%)"), chartColors: [HEX.accent1] });
txt(s, `ChatGPT is the main chatbot for ${N.gpt} of all participants · ${N.ai_only} use AI without any search engine`, { x: M, y: 6.25, w: 12.1, h: 0.4, fontSize: 15, italic: true, color: "52514E" });

// ---------------------------------------------------------------- 8 Levels
s = slide("CONTENT", "One in five has elevated health anxiety",
  `SHAI mean ${N.shai_m}; ${N.hac} scored 18 or more (95% CI ${N.hac_ci}). CSS mean ${N.css_m}. People search a lot (excessiveness highest) but it rarely disrupts daily life (compulsion lowest). Both scales reliable.`);
stat(s, M, 1.6, 2.85, N.shai_m, "mean SHAI-14 (0–42)");
stat(s, M + 3.07, 1.6, 2.85, N.hac, "elevated (SHAI ≥ 18)", C.accent2);
stat(s, M + 6.14, 1.6, 2.85, N.css_m, "mean CSS-12 (12–60)");
stat(s, M + 9.21, 1.6, 2.85, `${N.aS} / ${N.aC}`, "reliability α (SHAI / CSS)", null, 30);
fig(s, "fig5_subscales_by_HA.png", M, 3.6, 12.1, 3.2);

// ---------------------------------------------------------------- 9 Main result
s = slide("CONTENT", "Health anxiety and cyberchondria travel together",
  `Main result. r = ${N.r} (95% CI ${N.rci}); partial r = ${N.pr} after adjusting for all covariates. Strongest for excessive searching (${N.rE}) and post-search distress (${N.rD}). In regression, health anxiety is the strongest predictor (beta ${N.beta}); R-squared rises from ${N.R2b} to ${N.R2c} when health anxiety is added.`);
fig(s, "fig1_scatter_shai_css.png", M, 1.4, 6.4, 4.75);
stat(s, 7.4, 1.4, 2.55, `r = ${N.r}`, "overall correlation");
stat(s, 10.15, 1.4, 2.55, N.pr, "partial r (adjusted)");
s.addChart(pres.charts.BAR, [{ name: "r", labels: ["Excessiveness", "Distress", "Compulsion", "Reassurance"], values: N.subr.map((v) => Math.round(v * 100) / 100) }],
  { x: 7.4, y: 3.35, w: 5.3, h: 2.85, ...chartBase("Correlation with each CSS subscale"), dataLabelFormatCode: "0.00", chartColors: [HEX.accent2] });

// ---------------------------------------------------------------- 10 What drives it
s = slide("CONTENT", "What drives searching is fear, not noticing",
  `Item by item, ${N.ibF} of 168 pairs were significant after FDR correction. The strongest links involve fear of serious illness and interpreting sensations, for example fear of illness with panic when reading about a rare condition. Simply noticing aches and sensations was not linked. This fits the cognitive model.`);
fig(s, "fig9_item_by_item.png", M, 1.35, 7.2, 5.4);
[["Fear of serious illness ↔ panic on reading a rare condition", "ρ = 0.43"],
 ["Interpreting sensations ↔ searching every sensation", "ρ = 0.42"],
 ["Mere awareness of aches and sensations", "≈ unrelated"]].forEach(([t, v], i) => {
  const y = 1.5 + i * 1.65;
  card(s, 8.1, y, 4.6, 1.45, "driver " + i, i === 2 ? "F0EFEC" : null);
  txt(s, v, { x: 8.35, y: y + 0.15, w: 4.1, h: 0.5, fontSize: 22, bold: true, color: i === 2 ? "52514E" : C.accent2 });
  txt(s, t, { x: 8.35, y: y + 0.7, w: 4.1, h: 0.7, fontSize: 14 });
});
txt(s, `${N.ibF}/168 item pairs significant after FDR`, { x: 8.1, y: 6.5, w: 4.6, h: 0.35, fontSize: 13, italic: true, color: "52514E" });

// ---------------------------------------------------------------- 11 Predictors
s = slide("CONTENT", "Who is most affected",
  `Elevated health anxiety is independently associated with higher cyberchondria (AOR ${N.orCSS} per SD), searching for instant reassurance (AOR ${N.orMot}) and younger age (AOR ${N.orAge} per age step). AUC ${N.auc}. Chronic illness predicts SHAI in linear models. Demographics explain almost none of cyberchondria (R-squared ${N.R2a}).`);
fig(s, "fig7_forest_HA.png", M, 1.4, 7.6, 4.9);
[[N.orCSS + "×", "odds per SD of cyberchondria"], [N.orMot + "×", "odds if searching for instant reassurance"], [N.auc, "AUC: good discrimination"]].forEach(([v, l], i) => {
  stat(s, 8.6, 1.4 + i * 1.95, 4.1, v, l, i === 1 ? C.accent2 : C.accent1);
});

// ---------------------------------------------------------------- 12 Pathways
s = slide("CONTENT", "A pattern consistent with a cycle",
  `Excessive searching carries part of the link from health anxiety to distress (indirect ${N.mA}, CI ${N.mAci}). Post-search distress carries almost all of the link from health anxiety to reassurance-seeking visits (direct effect drops to ${N.mCd}). The reverse path is also significant (${N.mD}). Say clearly: consistent with a two-way cycle, but one-time data cannot prove direction.`);
fig(s, "fig8_mediation.png", M, 1.45, 12.1, 4.3);
card(s, M, 5.85, 12.1, 0.95, "caveat causality", "FDEEE7");
txt(s, `Reverse path also significant (indirect ${N.mD}): compatible with mutual reinforcement, but cross-sectional data cannot prove direction.`, { x: M + 0.3, y: 5.95, w: 11.5, h: 0.75, fontSize: 16, valign: "middle" });

// ---------------------------------------------------------------- 13 Behaviour
s = slide("CONTENT", "Searching shapes the consultation",
  `Most common response: delay or skip care because reassured (${N.dr}). Others escalate: urgent care ${N.urg}, multiple doctors ${N.mdoc}. Only ${N.always} always tell their doctor; ${N.never} never do. Paradox: higher health anxiety means more hiding (AOR ${N.nsS}); higher cyberchondria means less (AOR ${N.nsC}). Clinicians should ask.`);
s.addChart(pres.charts.BAR, [{ name: "Behaviour", labels: ["Delay/skip care (reassured)", "Ignore the symptom", "Visit multiple doctors", "Urgent visit / ER", "Self-medication", "Delay care (frightened)"], values: N.behav.map(pct) }],
  { x: M, y: 1.4, w: 6.6, h: 4.9, ...chartBase("After searching, people… (%)"), chartColors: [HEX.accent1] });
stat(s, 7.5, 1.4, 5.2, N.never, "never tell their doctor about searches (fear of being judged)", C.accent2);
card(s, 7.5, 3.35, 5.2, 2.95, "paradox");
txt(s, "The concealment paradox", { x: 7.8, y: 3.55, w: 4.6, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
txt(s, [{ text: `Higher health anxiety → more hiding (AOR ${N.nsS})`, options: { bullet: true, breakLine: true } },
  { text: `Higher cyberchondria → more sharing (AOR ${N.nsC})`, options: { bullet: true, breakLine: true } },
  { text: `${N.relneg} say searching strained their trust in doctors`, options: { bullet: true } }],
  { x: 7.8, y: 4.1, w: 4.7, h: 2.1, fontSize: 15, paraSpaceAfter: 6 });

// ---------------------------------------------------------------- 14 AI chatbots
s = slide("CONTENT", "AI chatbots: a new channel, not a proven cause",
  `AI users had higher cyberchondria (+${N.Bai} points, adjusted), mainly excessiveness and reassurance seeking. But with the strict definition (only those who ticked AI), the effect disappears (B = ${N.Balt}, p = ${N.palt}). ${N.inc} people named a chatbot without ticking it, and they had the highest scores; only 34 were non-users. AI did not change the strength of the anxiety-cyberchondria link.`);
stat(s, M, 1.6, 3.8, `+${N.Bai}`, "CSS points in AI users (adjusted)");
stat(s, M + 4.15, 1.6, 3.8, N.Balt, `with strict definition (p = ${N.palt})`, C.accent2);
stat(s, M + 8.3, 1.6, 3.8, "34", "true non-users: a small comparison group", "52514E");
bullets(s, [
  `${N.inc} respondents named a chatbot without ticking "AI chatbots"; how they are classified decides the result`,
  "Effect concentrated in excessiveness and reassurance seeking: conversational AI may invite \"one more question\"",
  "AI use did not change the strength of the health anxiety–cyberchondria link",
], { x: M, y: 3.75, w: 12.1, h: 2.6, fontSize: 17 });

// ---------------------------------------------------------------- 15 Limitations
section("Discussion");
s = slide("CONTENT", "Limitations and how we addressed them",
  "Go through each briefly; emphasise what was done to mitigate it.");
[["Cross-sectional", "No causal claims; reverse paths tested; longitudinal work recommended"],
 ["Convenience sample", "Young, 44% medical students; associations consistent across all subgroups"],
 ["Arabic wording", "Not back-translated; equal reliability and loadings across Arabic and English responders"],
 ["Single-item measures", "Behaviour and trust items are descriptive; their associations labelled exploratory"],
 ["Many tests", "FDR correction applied; robust vs exploratory findings separated"],
 ["Self-report online", "Anonymous; careless responders checked; excluding them changed nothing"]].forEach(([h, b], i) => {
  const x = M + (i % 3) * 4.1, y = 1.5 + Math.floor(i / 3) * 2.45;
  card(s, x, y, 3.9, 2.25, "limitation " + h);
  txt(s, h, { x: x + 0.3, y: y + 0.25, w: 3.3, h: 0.45, fontSize: 18, bold: true, color: C.accent2 });
  txt(s, b, { x: x + 0.3, y: y + 0.8, w: 3.3, h: 1.35, fontSize: 15 });
});

// ---------------------------------------------------------------- 16 Conclusions & recommendations
s = slide("CONTENT", "Conclusions and recommendations",
  "Three conclusions, then recommendations for clinicians, public health, AI developers and researchers.");
card(s, M, 1.5, 5.9, 4.85, "conclusions", C.text2);
txt(s, "Conclusions", { x: M + 0.3, y: 1.7, w: 5.3, h: 0.5, fontSize: 20, bold: true, color: C.background1 });
s.addText([
  { text: `AI chatbots are now the main source of pre-consultation health information (${N.ai})`, options: { bullet: true, breakLine: true } },
  { text: `Health anxiety and cyberchondria are linked (r = ${N.r}), via excessive searching and distress`, options: { bullet: true, breakLine: true } },
  { text: "Searching shapes the consultation: false reassurance, over-use, and hidden searches", options: { bullet: true } },
], { isTextBox: true, x: M + 0.3, y: 2.3, w: 5.3, h: 3.9, fontSize: 16, color: C.background1, paraSpaceAfter: 10, valign: "top" });
[["Clinicians", "Ask every patient, without judgement, what they searched or asked an AI"],
 ["Public health", "Arabic digital and AI health-literacy campaigns; warn about false reassurance"],
 ["AI developers", "Anxiety-aware answers that do not escalate rare diagnoses"],
 ["Research", "Longitudinal studies; formal Arabic validation; random sampling"]].forEach(([h, b], i) => {
  const y = 1.5 + i * 1.22;
  circleNum(s, 6.85, y + 0.2, i + 1, C.accent1);
  txt(s, h, { x: 7.6, y: y + 0.05, w: 5.1, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
  txt(s, b, { x: 7.6, y: y + 0.45, w: 5.1, h: 0.65, fontSize: 15 });
});

// ---------------------------------------------------------------- 17 Thank you
s = slide("TITLE_DARK", "Thank you", "Keep this slide up during questions.");
s.addText(`Questions are welcome\nHealth anxiety ↔ cyberchondria: r = ${N.r}  ·  AI chatbots used by ${N.ai}  ·  ${N.never} never tell their doctor`, { placeholder: "body" });

(async () => {
  await pres.writeFile({ fileName: OUTFILE });
  await applyTheme(OUTFILE, THEME);
  console.log("wrote", OUTFILE);
})();
