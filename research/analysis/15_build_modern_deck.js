// Modern, clean defence deck (16:9, white/navy with one orange accent, photos, native charts, speaker notes per student).
// Usage: NODE_PATH=<node_modules with pptxgenjs, jszip> node 15_build_modern_deck.js <numbers.json> <research dir> <out.pptx>
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const [, , NUMS, ROOT, OUTFILE] = process.argv;
const N = JSON.parse(fs.readFileSync(NUMS, "utf8"));
const FIG = N.figdir;
const PH = (f) => path.join(ROOT, "assets", "photos_modern", f);
const MAP = (f) => path.join(ROOT, "assets", "photos", f);
const LOGO = (f) => path.join(ROOT, "assets", "uobcom", f);

// ---------------------------------------------------------------- design system
const NAVY = "0B2545", INK = "1F2937", MUTED = "6B7280", ACCENT = "E86A33", SOFT = "F3F5F8", LINE = "E2E6EC", PALE = "FDF0E9", BLUE2 = "5B7DB1";
const FONT = "Calibri";
const W = 13.333, H = 7.5, M = 0.6;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad";
pres.subject = "Graduation research defence, University of Baghdad College of Medicine";
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
const pct = (s) => parseFloat(String(s).replace("%", ""));

let pageNo = 0;
function md(str) { // **accent bold** markup, "\n" = new paragraph
  const runs = [];
  str.split("\n").forEach((p, pi, arr) => {
    const parts = p.split(/(\*\*[^*]+\*\*)/).filter((x) => x.length);
    if (!parts.length) parts.push(" ");
    parts.forEach((t, ti) => {
      const hi = t.startsWith("**");
      const o = hi ? { bold: true, color: ACCENT } : {};
      if (ti === parts.length - 1 && pi < arr.length - 1) o.breakLine = true;
      runs.push({ text: hi ? t.slice(2, -2) : t, options: o });
    });
  });
  return runs;
}
function T(s, text, o) { s.addText(typeof text === "string" ? md(text) : text, { fontFace: FONT, fontSize: 16, color: INK, margin: 0, valign: "top", paraSpaceAfter: 6, ...o }); }
function content(kicker, title, notes, opts = {}) {
  const s = pres.addSlide(); pageNo++;
  s.background = { color: "FFFFFF" };
  const tw = opts.titleW || W - 2 * M;
  T(s, kicker.toUpperCase(), { x: M, y: 0.42, w: tw, h: 0.3, fontSize: 12, bold: true, color: ACCENT, charSpacing: 2 });
  T(s, title, { x: M, y: 0.72, w: tw, h: 0.75, fontSize: 30, bold: true, color: NAVY, valign: "middle" });
  s.addShape(pres.shapes.LINE, { x: M, y: H - 0.5, w: (opts.footW || W - 2 * M), h: 0, line: { color: LINE, width: 1 } });
  T(s, "Health anxiety, AI chatbots & cyberchondria · Baghdad", { x: M, y: H - 0.42, w: 6, h: 0.3, fontSize: 10, color: MUTED });
  T(s, String(pageNo), { x: (opts.footW ? M + opts.footW - 0.6 : W - M - 0.6), y: H - 0.42, w: 0.6, h: 0.3, fontSize: 10, color: MUTED, align: "right" });
  if (notes) s.addNotes(notes);
  return s;
}
function photo(s, file, x, y, w, h) { s.addImage({ path: PH(file), x, y, w, h, altText: file }); }
function tile(s, x, y, w, h, value, label, color, size) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: SOFT }, line: { color: SOFT } });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.08, h, fill: { color: color || ACCENT }, line: { color: color || ACCENT } });
  T(s, value, { x: x + 0.3, y: y + 0.15, w: w - 0.45, h: h * 0.55, fontSize: size || 34, bold: true, color: color || ACCENT, valign: "middle" });
  T(s, label, { x: x + 0.3, y: y + h * 0.58, w: w - 0.45, h: h * 0.4, fontSize: 14.5, color: INK, valign: "top" });
}
function card(s, x, y, w, h, head, body, color, fs) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: SOFT }, line: { color: SOFT } });
  T(s, head, { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: 0.45, fontSize: 17, bold: true, color: color || NAVY });
  T(s, body, { x: x + 0.25, y: y + 0.7, w: w - 0.5, h: h - 0.85, fontSize: fs || 14 });
}
function badge(s, x, y, txt, color) {
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.5, h: 0.5, fill: { color: color || NAVY }, line: { color: color || NAVY } });
  T(s, String(txt), { x, y, w: 0.5, h: 0.5, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
}
function figure(s, file, x, y, maxW, maxH, caption) {
  const a = N.aspect[file] || 1.54; let w = maxW, h = w / a; if (h > maxH) { h = maxH; w = h * a; }
  s.addImage({ path: path.join(FIG, file), x: x + (maxW - w) / 2, y, w, h, altText: caption || file });
  if (caption) T(s, caption, { x, y: y + h + 0.05, w: maxW, h: 0.3, fontSize: 10.5, italic: true, color: MUTED, align: "center" });
  return h;
}
function callout(s, x, y, w, h, text) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: PALE }, line: { color: PALE } });
  T(s, text, { x: x + 0.25, y, w: w - 0.5, h, fontSize: 15, valign: "middle" });
}
function divider(num, title, sub, file, notes) {
  const s = pres.addSlide(); pageNo++;
  s.background = { color: NAVY };
  photo(s, file, 7.33, 0, 6.0, 7.5);
  T(s, num, { x: M, y: 1.7, w: 4, h: 1.2, fontSize: 80, bold: true, color: ACCENT });
  T(s, title, { x: M, y: 2.95, w: 6.4, h: 1.0, fontSize: 44, bold: true, color: "FFFFFF" });
  T(s, sub, { x: M, y: 4.05, w: 6.2, h: 1.6, fontSize: 18, color: "C9D3E3" });
  if (notes) s.addNotes(notes);
  return s;
}
const barBase = (fmt) => ({
  barDir: "bar", catAxisOrientation: "maxMin", barGapWidthPct: 55, showValue: true, dataLabelPosition: "outEnd",
  dataLabelFontSize: 13, dataLabelColor: INK, dataLabelFontFace: FONT, dataLabelFormatCode: fmt || '0.0"%"',
  catAxisLabelFontSize: 13, catAxisLabelColor: INK, catAxisLabelFontFace: FONT, catAxisLineShow: false,
  valAxisHidden: true, valGridLine: { style: "none" }, showLegend: false, chartArea: { fill: { color: "FFFFFF" } },
});
const S1 = "[STUDENT 1 · Introduction & Methods]\n", S2 = "[STUDENT 2 · Results]\n", S3 = "[STUDENT 3 · Discussion & Conclusions]\n";

// ================================================================ 1 Title
let s = pres.addSlide(); pageNo++;
s.background = { color: NAVY };
photo(s, "title.jpg", 7.33, 0, 6.0, 7.5);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 0.55, w: 2.1, h: 0.95, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" } });
s.addImage({ path: LOGO("logo_uob.png"), x: M + 0.15, y: 0.62, w: 0.8, h: 0.8 });
s.addImage({ path: LOGO("logo_med.png"), x: M + 1.15, y: 0.62, w: 0.68, h: 0.8 });
T(s, "University of Baghdad · College of Medicine", { x: M + 2.35, y: 0.75, w: 4.3, h: 0.6, fontSize: 14, color: "C9D3E3", valign: "middle" });
T(s, "Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad", { x: M, y: 2.0, w: 6.3, h: 2.2, fontSize: 36, bold: true, color: "FFFFFF", valign: "bottom" });
T(s, "An online cross-sectional survey", { x: M, y: 4.3, w: 6.3, h: 0.5, fontSize: 20, color: ACCENT });
T(s, [{ text: "Presented by", options: { bold: true, color: "FFFFFF", breakLine: true } }, { text: "[Student 1]  ·  [Student 2]  ·  [Student 3]", options: { breakLine: true } },
  { text: " ", options: { fontSize: 8, breakLine: true } }, { text: "Supervisor", options: { bold: true, color: "FFFFFF", breakLine: true } }, { text: "[Title and name]", options: {} }],
  { x: M, y: 5.2, w: 6.3, h: 1.6, fontSize: 15, color: "C9D3E3" });
s.addNotes(S1 + "Good morning. We are [names], supervised by [supervisor]. Our research looks at what happens when people search their symptoms online, and now ask AI chatbots like ChatGPT, before they see a doctor; and how this relates to health anxiety and cyberchondria.");

// ================================================================ 2 Why it matters
s = content("Background", "Why this study matters", S1 + "Looking up symptoms online is now ordinary, and in Iraq more than four in five people are online. AI chatbots now answer health questions in fluent, personal language. For some people searching relieves worry; for others it makes it worse: that is cyberchondria. Nobody had studied this in Baghdad, and AI chatbots had hardly been studied next to search engines.", { titleW: 6.6, footW: 6.6 });
photo(s, "why.jpg", 7.73, 0, 5.6, 7.5);
[["> 80%", "of Iraqis are online: symptoms are searched before they reach a doctor"], ["AI", "chatbots now answer health questions conversationally and without limit"], ["0", "studies of health anxiety and cyberchondria in Baghdad before ours"]].forEach(([v, l], i) => {
  tile(s, M, 1.75 + i * 1.65, 6.6, 1.45, v, l, i === 1 ? NAVY : ACCENT, 32);
});

// ================================================================ 3 Concepts
s = content("Key concepts", "Health anxiety and cyberchondria", S1 + "Health anxiety is persistent worry about having a serious illness, kept going by misreading normal sensations and seeking reassurance. We measured it with the SHAI-14, scored 0 to 42. Cyberchondria is excessive or repeated online searching that increases distress rather than relieving it. We measured it with the CSS-12, which has four facets: excessiveness, compulsion, distress and reassurance seeking.");
card(s, M, 1.7, 3.75, 4.9, "Health anxiety", "Persistent worry about having a serious illness, kept going by **misreading normal sensations** and **seeking reassurance**.\n\nMeasured with the **SHAI-14** (14 items, 0–42).", NAVY, 15);
card(s, M + 3.95, 1.7, 3.75, 4.9, "Cyberchondria", "Excessive or repeated online health searching that **increases** distress instead of relieving it.\n\nMeasured with the **CSS-12** (12 items, 12–60): excessiveness · compulsion · distress · reassurance.", ACCENT, 15);
photo(s, "concepts.jpg", 8.65, 1.7, 4.08, 4.9);

// ================================================================ 4 Model and hypotheses
s = content("Our model", "A vicious cycle, and four hypotheses", S1 + "This is our conceptual framework. Health anxiety leads to excessive searching, which leads to post-search distress, which leads to reassurance seeking; reassurance gives short relief, so the cycle repeats. Our four hypotheses sit on this model. H1: health anxiety is linked to cyberchondria. H2: this holds after adjusting for other factors. H3: excessive searching is a step between health anxiety and distress. H4: cyberchondria goes with care-seeking and a strained relationship with doctors.");
figure(s, "fig0a_framework.png", M, 1.65, 8.4, 5.1);
[["H1", "Health anxiety ↔ cyberchondria"], ["H2", "Independent of other factors"], ["H3", "Excessive searching is a step to distress"], ["H4", "Cyberchondria ↔ care-seeking & doctor relationship"]].forEach(([k, t], i) => {
  const y = 1.75 + i * 1.22; badge(s, 9.35, y + 0.1, k, i < 2 ? NAVY : ACCENT);
  T(s, t, { x: 10.0, y, w: 2.75, h: 0.75, fontSize: 15, valign: "middle" });
});

// ================================================================ 5 Methods
s = content("Methods", "How we did it", S1 + `An analytical cross-sectional online survey, reported with the STROBE and CHERRIES checklists. Data were collected in Baghdad from ${N.d0} to ${N.d1}, through Baghdad-based social-media and messaging groups, using convenience and snowball sampling. Adults aged 18 or older who could read Arabic or English and gave consent were included. ${N.n} people answered, with no missing data. The form was bilingual, and the analysis used Python with correction for multiple testing.`, { footW: 8.2 });
photo(s, "methods.jpg", 9.13, 0, 4.2, 7.5);
[["Design", "Analytical cross-sectional online survey (STROBE, CHERRIES)"], ["Setting", `Baghdad · ${N.d0} – ${N.d1}`], ["Sampling", "Convenience + snowball via Baghdad-based online groups"],
 ["Participants", `n = ${N.n} adults ≥ 18 · consent · Arabic or English`], ["Questionnaire", "Bilingual Google Form · 5 parts · SHAI-14 · CSS-12"], ["Ethics", "Anonymous · e-consent first · [approval no.]"]].forEach(([h, b], i) => {
  const x = M + (i % 2) * 4.15, y = 1.7 + Math.floor(i / 2) * 1.65;
  badge(s, x, y + 0.05, i + 1, i % 2 ? ACCENT : NAVY);
  T(s, h, { x: x + 0.65, y, w: 3.3, h: 0.45, fontSize: 17, bold: true, color: NAVY });
  T(s, b, { x: x + 0.65, y: y + 0.45, w: 3.3, h: 1.0, fontSize: 14 });
});

// ================================================================ 6 Sample size & analysis
s = content("Methods", "Sample size and analysis", S1 + `Our main question is a correlation. With alpha 0.05 and 80% power we needed ${N.nreq} people to detect a correlation of 0.20; we collected ${N.n}. For percentages that gives a margin of error of plus or minus ${N.moe} percent. We checked reliability and structure, including whether the scales work the same in Arabic and English, then used correlations, group comparisons, regression and mediation, with false discovery rate correction and sensitivity analyses. Now my colleague will present the results.`);
tile(s, M, 1.75, 3.9, 1.6, `${N.nreq} → ${N.n}`, "needed (r = 0.20, α 0.05, 80% power) → collected", ACCENT, 34);
tile(s, M, 3.55, 3.9, 1.5, `±${N.moe}%`, "margin of error for percentages", NAVY, 30);
tile(s, M, 5.25, 3.9, 1.5, "≈ 0.62", "expected r from meta-analyses: our target is conservative", NAVY, 30);
[["Psychometrics", "Cronbach α, McDonald ω, CFA; Arabic vs English invariance"], ["Associations", "Pearson / Spearman, Mann–Whitney, Kruskal–Wallis, χ²"], ["Models", "Hierarchical robust regression; logistic regression (AUC)"],
 ["Pathways", "Bootstrapped mediation (5000 resamples); moderation"], ["Rigour", "FDR correction for many tests; sensitivity analyses"]].forEach(([h, b], i) => {
  const y = 1.75 + i * 1.0;
  s.addShape(pres.shapes.RECTANGLE, { x: 4.85, y, w: 0.08, h: 0.8, fill: { color: i % 2 ? ACCENT : NAVY }, line: { color: i % 2 ? ACCENT : NAVY } });
  T(s, h, { x: 5.1, y, w: 2.4, h: 0.8, fontSize: 16, bold: true, color: NAVY, valign: "middle" });
  T(s, b, { x: 7.5, y, w: 5.2, h: 0.8, fontSize: 15, valign: "middle" });
});

// ================================================================ 7 Divider Results
divider("02", "Results", "Who took part · how they search · how anxious they are · the main link · who is at risk · behaviour · AI", "results.jpg",
  S2 + "Thank you. I will present our results: who took part, how they search, how anxious they are, the main link, who is at risk, behaviour after searching, and finally AI chatbots.");

// ================================================================ 8 Participants
s = content("Participants", "A young, educated, digitally active sample", S2 + `Table 1: ${N.n} adults answered. ${N.age20} were aged 20 to 29, ${N.fem} were women, and ${N.med} were medical students; ${N.hb} had a health-related background and ${N.chron} a chronic condition. In summary: a young, educated sample, which we keep in mind when reading percentages; the associations, however, were consistent across all subgroups.`);
[[String(N.n), "participants · no missing data"], [N.age20, "aged 20–29"], [N.fem, "female"], [N.med, "medical students"], [N.hb, "health-related background"], [N.chron, "chronic condition"]].forEach(([v, l], i) => {
  tile(s, M + (i % 3) * 4.1, 1.75 + Math.floor(i / 3) * 1.95, 3.85, 1.75, v, l, i === 3 ? ACCENT : NAVY, 38);
});
callout(s, M, 5.75, 12.1, 0.8, "Percentages describe **this sample**; the associations, however, held in every subgroup.");

// ================================================================ 9 How they search
s = content("How people search", "AI chatbots are now the first stop", S2 + `Figure 3: ${N.ai_tick} ticked AI chatbots, ${N.ai} if we include those who named a chatbot, ahead of search engines at ${N.se}. ${N.ai_only} used AI without any search engine, and ChatGPT alone was used by ${N.gpt}. The top motives were convenience, deciding whether a doctor is needed, and instant reassurance. In summary: for many people the first "doctor" is now an AI chatbot.`);
s.addChart(pres.charts.BAR, [{ name: "Tools", labels: ["AI chatbots", "Search engines", "Medical platforms", "Social media"], values: [pct(N.ai_tick), N.tools[1], N.tools[2], N.tools[3]].map((v) => Math.round(v * 10) / 10) }],
  { x: M, y: 1.75, w: 6.0, h: 3.9, ...barBase(), chartColors: [NAVY], showTitle: true, title: "Tools used to look up symptoms (%)", titleFontSize: 15, titleColor: INK, titleFontFace: FONT });
s.addChart(pres.charts.BAR, [{ name: "Motives", labels: ["Convenience", "Is a doctor needed?", "Instant reassurance", "Self-diagnosis", "Cost / logistics"], values: N.motives.map((v) => Math.round(v * 10) / 10) }],
  { x: 6.85, y: 1.75, w: 5.9, h: 3.9, ...barBase(), chartColors: [ACCENT], showTitle: true, title: "Why they search (%)", titleFontSize: 15, titleColor: INK, titleFontFace: FONT });
[[N.ai, "use AI incl. those who named a chatbot"], [N.ai_only, "use AI without any search engine"], [N.gpt, "use ChatGPT"]].forEach(([v, l], i) => tile(s, M + i * 4.1, 5.8, 3.85, 0.95, v, l, NAVY, 22));

// ================================================================ 10 Levels & scales
s = content("Health anxiety and the scales", "One in five scored in the elevated range", S2 + `Table 4: ${N.hac} scored 18 or more on the SHAI-14, our threshold for elevated health anxiety, 95% CI ${N.hac_ci}. This is a screening threshold, not a diagnosis, and the estimate depends on the cut-off: 33% at 15 down to 0.7% at 29. Both scales were reliable, alpha ${N.aS} and ${N.aC}, and the CSS-12 worked identically in Arabic and English. In summary: our tools measured well.`);
tile(s, M, 1.75, 4.2, 2.2, N.hac, `elevated health anxiety (SHAI ≥ 18) · 95% CI ${N.hac_ci}`, ACCENT, 54);
s.addTable([
  [{ text: "SHAI-14 cut-off", options: { bold: true, fill: { color: SOFT } } }, { text: "%", options: { bold: true, fill: { color: SOFT } } }],
  ["≥ 15", "32.7"], [{ text: "≥ 18 (used)", options: { bold: true, color: ACCENT } }, { text: "19.0", options: { bold: true, color: ACCENT } }], ["≥ 22", "7.3"], ["≥ 29", "0.7"],
], { x: M, y: 4.2, w: 4.2, colW: [2.9, 1.3], rowH: 0.45, fontFace: FONT, fontSize: 14, color: INK, border: { type: "solid", pt: 0.75, color: LINE } });
[[`α ${N.aS}`, "SHAI-14 reliability"], [`α ${N.aC}`, "CSS-12 reliability"], [`CFI ${N.cfaC}`, "CSS-12 four-factor structure confirmed"], ["Same", "CSS-12 in Arabic and English (full invariance)"]].forEach(([v, l], i) => {
  tile(s, 5.2 + (i % 2) * 3.85, 1.75 + Math.floor(i / 2) * 2.0, 3.6, 1.8, v, l, NAVY, 30);
});
T(s, `SHAI mean ${N.shai_m} / 42 · CSS mean ${N.css_m} / 60 · excessiveness highest, compulsion lowest`, { x: 5.2, y: 5.95, w: 7.5, h: 0.6, fontSize: 14, color: MUTED });

// ================================================================ 11 Main result
s = content("Main result", "Health anxiety and cyberchondria rise together", S2 + `Figure 5 is our main result. Each dot is a participant; the line rises clearly: r = ${N.r}, 95% CI ${N.rci}. After adjusting for age, gender, background, chronic disease, trust and AI use, it is still ${N.pr}. The link is strongest for excessive searching and post-search distress. In summary: hypotheses 1 and 2 are supported.`);
figure(s, "fig1_scatter_shai_css.png", M, 1.6, 7.1, 5.05);
tile(s, 8.1, 1.7, 4.65, 1.55, `r = ${N.r}`, `95% CI ${N.rci} · p < 0.001 · partial r = ${N.pr}`, ACCENT, 40);
s.addChart(pres.charts.BAR, [{ name: "r", labels: ["Excessiveness", "Distress", "Compulsion", "Reassurance"], values: N.subr.map((v) => Math.round(v * 100) / 100) }],
  { x: 8.1, y: 3.45, w: 4.65, h: 2.6, ...barBase("0.00"), chartColors: [NAVY], showTitle: true, title: "Correlation with each facet", titleFontSize: 14, titleColor: INK, titleFontFace: FONT });
T(s, "H1 and H2 **supported**", { x: 8.1, y: 6.15, w: 4.65, h: 0.45, fontSize: 16, bold: true, color: NAVY });

// ================================================================ 12 What predicts
s = content("What predicts cyberchondria", "How anxious you are matters more than who you are", S2 + `Table 9, hierarchical regression. Demographics alone explain about 3% of cyberchondria; adding digital use brings it to 13%; adding health anxiety brings it to 32%, an extra ${N.dR2}. Health anxiety is by far the strongest predictor, beta ${N.beta}: each extra SHAI point adds about ${N.B} CSS points. In summary: health anxiety, not demographics, explains cyberchondria.`);
s.addChart(pres.charts.BAR, [{ name: "R²", labels: ["Demographics", "+ digital use", "+ health anxiety"], values: [pct(N.R2a) * 100, pct(N.R2b) * 100, pct(N.R2c) * 100].map((v) => Math.round(v)) }],
  { x: M, y: 1.75, w: 7.0, h: 4.8, barDir: "col", barGapWidthPct: 45, showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 18, dataLabelColor: INK, dataLabelFontFace: FONT, dataLabelFormatCode: '0"%"',
    catAxisLabelFontSize: 15, catAxisLabelColor: INK, catAxisLabelFontFace: FONT, valAxisHidden: true, valGridLine: { style: "none" }, showLegend: false, chartColors: [BLUE2, BLUE2, ACCENT],
    showTitle: true, title: "Variance in cyberchondria explained (R²)", titleFontSize: 15, titleColor: INK, titleFontFace: FONT });
tile(s, 8.0, 1.75, 4.75, 1.6, `+${N.dR2}`, "extra variance explained by health anxiety", ACCENT, 40);
tile(s, 8.0, 3.55, 4.75, 1.4, `β = ${N.beta}`, `strongest predictor · B = ${N.B} CSS points per SHAI point`, NAVY, 30);
tile(s, 8.0, 5.15, 4.75, 1.4, "Not robust", `AI use: +${N.Bai} (inclusive) but +${N.Balt}, p = ${N.palt} (strict)`, MUTED, 26);

// ================================================================ 13 What drives searching
s = content("What drives searching", "Fear and interpretation, not noticing", S2 + `Figure 10 compares the four facets between people with and without elevated health anxiety: the biggest gaps are in excessive searching and distress. At item level, Figure 11, the strongest links are fear of serious illness with panicking when reading about a rare condition, rho 0.43, and interpreting body sensations with searching every sensation, 0.42. Simply noticing aches is almost unrelated. In summary: fear drives searching, not noticing.`);
figure(s, "fig5_subscales_by_HA.png", M, 1.65, 7.3, 4.6, "Figure 10: CSS facets by health-anxiety status (mean ± 95% CI)");
[["ρ 0.43", "Fear of serious illness ↔ panic on reading of a rare condition", ACCENT], ["ρ 0.42", "Interpreting sensations ↔ searching every sensation", ACCENT], ["≈ 0", "Merely noticing aches or sensations", MUTED]].forEach(([v, l, c], i) => {
  tile(s, 8.25, 1.7 + i * 1.6, 4.5, 1.42, v, l, c, 28);
});
T(s, `${N.ibF} of 168 item pairs significant after FDR`, { x: 8.25, y: 6.55 - 0.15, w: 4.5, h: 0.35, fontSize: 13, color: MUTED });

// ================================================================ 14 Who is at risk
s = content("Who is at risk", "Young people who search for reassurance", S2 + `Figure 8 shows the logistic model for elevated health anxiety. Each standard deviation of cyberchondria triples the odds, adjusted odds ratio ${N.orCSS}; searching for instant reassurance almost quadruples them, ${N.orMot}; older age is protective, ${N.orAge}. The model discriminates well: AUC ${N.auc}, ${N.aucc} after correcting for optimism. In summary: the person most at risk is young and searches to feel reassured.`);
figure(s, "fig7_forest_HA.png", M, 1.6, 7.6, 4.9, "Figure 8: adjusted odds ratios; orange = p < 0.05");
[[`${N.orCSS}×`, "odds per SD of cyberchondria", ACCENT], [`${N.orMot}×`, "if searching for instant reassurance", ACCENT], [`${N.orAge}×`, "per older age group (protective)", NAVY], [`AUC ${N.aucc}`, `after optimism correction (apparent ${N.auc})`, NAVY]].forEach(([v, l, c], i) => {
  tile(s, 8.55, 1.7 + i * 1.22, 4.2, 1.08, v, l, c, 24);
});

// ================================================================ 15 Pathways
s = content("Pathways", "Compatible with a cycle, not proof of one", S2 + `Figure 9, mediation. Part of the link from health anxiety to distress runs through excessive searching, indirect effect ${N.mA}. Almost all of the link from health anxiety to reassurance-seeking visits runs through distress: the direct effect falls to ${N.mCd}. But the reverse direction also fits, ${N.mD}. In summary: our data are compatible with a vicious cycle, but one survey at one time point cannot prove the direction. Hypothesis 3 is supported statistically, not causally.`);
figure(s, "fig8_mediation.png", M, 1.6, 12.1, 3.75, "Figure 9: mediation models (standardised; 5000 bootstrap resamples)");
[[N.mA, `indirect via excessive searching (CI ${N.mAci})`], [N.mCd, "direct effect left after distress (not significant)"], [N.mD, "reverse direction also significant"]].forEach(([v, l], i) => tile(s, M + i * 4.1, 5.65, 3.85, 1.15, v, l, i === 2 ? ACCENT : NAVY, 26));

// ================================================================ 16 Behaviour
s = content("Behaviour after searching", "Searching shapes the consultation", S2 + `Figure 4: after searching, ${N.dr} delayed or skipped care because they felt reassured; others escalated, consulting several doctors or seeking urgent care. Only ${N.always} always tell their doctor, and ${N.never} never do, citing fear of being judged. Higher cyberchondria went with more disclosure, and this was the only behavioural result that survived correction. In summary: searching changes the consultation before it begins.`);
s.addChart(pres.charts.BAR, [{ name: "Behaviour", labels: ["Delay/skip care (reassured)", "Ignore the symptom", "Visit several doctors", "Urgent visit / ER", "Self-medication", "Delay care (frightened)"], values: N.behav.map((v) => Math.round(v * 10) / 10) }],
  { x: M, y: 1.7, w: 7.2, h: 5.0, ...barBase(), chartColors: [NAVY], showTitle: true, title: "After searching, people… (%)", titleFontSize: 15, titleColor: INK, titleFontFace: FONT });
tile(s, 8.1, 1.75, 4.65, 1.5, N.never, "never tell their doctor (fear of judgement)", ACCENT, 38);
tile(s, 8.1, 3.45, 4.65, 1.5, N.relneg, "say searching strained their relationship with doctors", NAVY, 34);
tile(s, 8.1, 5.15, 4.65, 1.5, `OR ${N.nsC}`, `higher cyberchondria → less hiding (q = ${N.nsCq}, robust)`, NAVY, 30);

// ================================================================ 17 AI
s = content("AI chatbots", "No reliable independent effect of AI", S2 + `Did AI itself matter? Under the inclusive definition AI users scored ${N.Bai} points higher. But ${N.inc} people named a chatbot without ticking the AI option, and they had the highest scores. With the strict definition the difference is only ${N.Balt}, p = ${N.palt}; and only 34 people were true non-users. AI also did not change the strength of the anxiety–cyberchondria link. In summary: no reliable independent effect of AI; absence of evidence, not evidence of absence. I now hand over to my colleague.`, { titleW: 7.6, footW: 7.6 });
photo(s, "ai.jpg", 8.73, 0, 4.6, 7.5);
tile(s, M, 1.75, 3.65, 1.75, `+${N.Bai}`, "CSS points · inclusive definition", NAVY, 40);
tile(s, M + 3.95, 1.75, 3.65, 1.75, `+${N.Balt}`, `strict definition · p = ${N.palt}`, ACCENT, 40);
[[`${N.inc} respondents named a chatbot but did not tick “AI”; they scored highest`], ["Only 34 true non-users: a small comparison group"], ["AI use did not change the health anxiety ↔ cyberchondria link"]].forEach(([t], i) => {
  badge(s, M, 3.85 + i * 0.85, i + 1, NAVY); T(s, t, { x: M + 0.7, y: 3.8 + i * 0.85, w: 6.9, h: 0.6, fontSize: 15, valign: "middle" });
});
callout(s, M, 6.25, 7.6, 0.55, "Absence of evidence, not evidence of absence.");

// ================================================================ 18 Divider Discussion
divider("03", "Discussion", "How we compare · why · AI and the consultation · medical students · limitations · recommendations", "discussion.jpg",
  S3 + "Thank you. I will discuss what these results mean, how they compare with other studies, our limitations and our recommendations.");

// ================================================================ 19 Vs world
s = content("Compared with the world", "Same direction, weaker link: four reasons", S3 + `To our knowledge, this is the first CSS-12 study in Baghdad. Our correlation of ${N.r} is weaker than the meta-analytic 0.62 and 0.63. Four reasons: measurement error, since corrected for reliability it would be about ${N.disr}; our sample had low and narrow health anxiety; online recruitment favours confident internet users; and most earlier studies used the longer 33-item scale.`);
s.addChart(pres.charts.BAR, [{ name: "r", labels: ["Meta-analysis 2019", "Meta-analysis 2021", "Ours, corrected", "Ours"], values: [0.62, 0.63, parseFloat(N.disr), parseFloat(N.r)] }],
  { x: M, y: 1.7, w: 6.4, h: 4.9, ...barBase("0.00"), chartColors: ["9AA9C0", "9AA9C0", "F2A57F", ACCENT], showTitle: true, title: "Correlation: health anxiety ↔ cyberchondria", titleFontSize: 15, titleColor: INK, titleFontFace: FONT });
[["Measurement error", `corrected for reliability, r ≈ ${N.disr}`], ["Narrow range", `low health anxiety (mean ${N.shai_m}) weakens r`], ["Who answered", "online recruitment favours confident users"], ["Short form", "most studies used the 33-item CSS"]].forEach(([h, b], i) => {
  const y = 1.8 + i * 1.2; badge(s, 7.4, y, i + 1, i % 2 ? ACCENT : NAVY);
  T(s, h, { x: 8.05, y: y - 0.05, w: 4.7, h: 0.4, fontSize: 17, bold: true, color: NAVY });
  T(s, b, { x: 8.05, y: y + 0.38, w: 4.7, h: 0.5, fontSize: 14 });
});

// ================================================================ 20 Arab region
s = content("Compared with the Arab region", "Consistent with regional studies", S3 + "Our findings agree with the Arab region: in Jeddah cyberchondria was common and linked with smartphone addiction; in Saudi primary care it was linked with health anxiety; in Lebanon the Arabic CSS-12 had the same structure as ours; and among 1435 Egyptian medical students, 85.8% had moderate cyberchondria.");
s.addImage({ path: MAP("map_region.png"), x: M, y: 1.7, w: 6.4, h: 4.8, altText: "Map: Iraq, Saudi Arabia, Lebanon, Egypt" });
[["Saudi Arabia · Jeddah", "Common; linked with smartphone addiction"], ["Saudi Arabia · primary care", "Linked with health anxiety"], ["Lebanon", "Arabic CSS-12: same four-factor structure"], ["Egypt · 1435 medical students", "85.8% moderate cyberchondria"]].forEach(([h, b], i) => {
  card(s, 7.35, 1.7 + i * 1.22, 5.4, 1.08, h, b, i === 3 ? ACCENT : NAVY, 14);
});

// ================================================================ 21 AI and medical students
s = content("Two groups worth discussing", "AI users and medical students", S3 + `AI use here, ${N.ai_tick} to ${N.ai}, is far higher than about one in five in a 2024 US survey and 21% in a 2025 survey; our sample is young, and AI use fell from 96% at 18 to 19 years to 72% at 40 or older. ${N.med} of our sample were medical students: their higher unadjusted health anxiety disappeared after adjustment for age, and their cyberchondria was the same as everyone else's. Medical knowledge did not protect them. A Palestinian study using the same SHAI cut-off even found medical students had the lowest health anxiety.`);
card(s, M, 1.7, 4.1, 5.0, "AI chatbots", `Our use **${N.ai_tick}–${N.ai}** vs ≈ 20% (US 2024) and 21% (2025).\n\nYoung sample: **96%** at 18–19 y vs **72%** at ≥ 40 y.\n\nConversational AI may invite “one more question”.`, NAVY, 15);
card(s, M + 4.3, 1.7, 4.1, 5.0, "Medical students", `**${N.med}** of our sample.\n\nHigher health anxiety **disappeared after adjustment** (younger age).\n\nSame cyberchondria as others: **knowledge did not protect**.`, ACCENT, 15);
photo(s, "students.jpg", 9.2, 1.7, 3.53, 5.0);

// ================================================================ 22 Consultation
s = content("What it means for the consultation", "Ask every patient what they searched", S3 + `Delaying care because of reassurance, ${N.dr}, is double-edged: it can save unnecessary visits for minor symptoms but risks delayed diagnosis for serious ones, and it happened at all levels of anxiety. Almost a third never tell their doctor what they searched. Higher cyberchondria went with more disclosure, while health anxiety tended towards concealment, which is exploratory. So the practical message is simple: ask, without judgement.`, { titleW: 7.6, footW: 7.6 });
photo(s, "recs.jpg", 8.73, 0, 4.6, 7.5);
[[N.dr, "delay care when reassured: saves visits, but risks delayed diagnosis"], [N.never, "never tell the doctor: hidden information in the consultation"], ["H4", "only partially supported: disclosure was the robust finding"]].forEach(([v, l], i) => tile(s, M, 1.75 + i * 1.5, 7.6, 1.3, v, l, i === 1 ? ACCENT : NAVY, 30));
callout(s, M, 6.25, 7.6, 0.6, "**Clinical message:** ask, without judgement, what patients searched or asked an AI.");

// ================================================================ 23 Limitations
s = content("Limitations", "What limits our conclusions, and what we did", S3 + "Our main limitations. The design is cross-sectional, so we cannot prove direction. The sample is an online convenience sample, young and heavy in medical students, so percentages cannot be generalised; but associations were consistent across subgroups. The Arabic wording was ours, without formal back-translation; but reliability was equal and the CSS-12 was fully invariant. Behaviour questions were single, non-validated items. And we ran many tests, so we used FDR correction.");
[["Cross-sectional design", "No causal direction", "Reverse models tested; “compatible with”"], ["Convenience sample", "Young, 44% medical students", "Percentages not generalised; associations consistent"], ["Arabic wording", "No back-translation", "Equal reliability; CSS-12 fully invariant"],
 ["Single-item measures", "Behaviour, disclosure, trust", "Reported descriptively; labelled exploratory"], ["Many tests", "Risk of false positives", "FDR correction; robust vs exploratory"]].forEach(([a, b, c], i) => {
  const y = 1.7 + i * 0.98;
  s.addShape(pres.shapes.RECTANGLE, { x: M, y, w: 12.1, h: 0.85, fill: { color: i % 2 ? "FFFFFF" : SOFT }, line: { color: SOFT } });
  badge(s, M + 0.15, y + 0.17, i + 1, NAVY);
  T(s, a, { x: M + 0.85, y, w: 3.4, h: 0.85, fontSize: 16, bold: true, color: NAVY, valign: "middle" });
  T(s, b, { x: M + 4.3, y, w: 3.3, h: 0.85, fontSize: 14, color: MUTED, valign: "middle" });
  T(s, "→ " + c, { x: M + 7.6, y, w: 4.4, h: 0.85, fontSize: 14, valign: "middle" });
});

// ================================================================ 24 Recommendations
s = content("Recommendations", "From findings to action", S3 + "For clinicians: ask without judgement, recognise repeated searching and reassurance seeking as signs of health anxiety, and teach digital and AI literacy in medical school. The Ministry of Health may consider Arabic digital and AI health-literacy campaigns and reliable Arabic triage sources. AI developers may consider anxiety-aware answers. And researchers should run longitudinal studies and intervention trials: ClinicalTrials.gov lists only nine cyberchondria studies, none in Iraq.");
[["Clinicians", "Ask non-judgementally; treat repeated searching as a sign of health anxiety; teach AI literacy"], ["Ministry of Health", "May consider Arabic digital & AI health-literacy campaigns and reliable triage sources"],
 ["AI developers", "May consider anxiety-aware answers that do not escalate rare diagnoses"], ["Researchers", "Longitudinal studies; probability samples; trials: only 9 registered, none in Iraq"]].forEach(([h, b], i) => {
  const x = M + (i % 2) * 6.15, y = 1.7 + Math.floor(i / 2) * 2.5;
  card(s, x, y, 5.95, 2.3, h, b, i % 2 ? ACCENT : NAVY, 18);
});

// ================================================================ 25 Conclusion
s = content("Conclusion", "Three things to remember", S3 + `To conclude. One: AI chatbots, mainly ChatGPT, are now the main source of health information before seeing a doctor in our sample. Two: health anxiety and cyberchondria are moderately and robustly linked, r = ${N.r}, compatible with a vicious cycle, with no reliable independent effect of AI. Three: searching shapes the consultation, so doctors should ask. Thank you.`);
[["1", "AI chatbots are the first stop", `${N.ai_tick} ticked them (${N.ai} incl. named), more than search engines.`], ["2", `Health anxiety ↔ cyberchondria, r = ${N.r}`, "Robust, compatible with a cycle; no reliable independent AI effect."], ["3", "Searching shapes the consultation", `${N.dr} delay care when reassured; ${N.never} never tell the doctor.`]].forEach(([n, h, b], i) => {
  const x = M + i * 4.1;
  T(s, n, { x, y: 1.75, w: 1.2, h: 1.1, fontSize: 64, bold: true, color: ACCENT });
  T(s, h, { x, y: 2.95, w: 3.8, h: 1.0, fontSize: 20, bold: true, color: NAVY });
  T(s, b, { x, y: 4.0, w: 3.8, h: 1.6, fontSize: 16 });
});
callout(s, M, 5.9, 12.1, 0.8, "**Ask every patient, without judgement, what they searched or asked an AI.**");

// ================================================================ 26 Thank you
s = pres.addSlide(); pageNo++;
s.background = { color: NAVY };
T(s, `r = ${N.r}`, { x: M, y: 1.6, w: W - 2 * M, h: 1.8, fontSize: 96, bold: true, color: ACCENT, align: "center", valign: "middle" });
T(s, "Health anxiety and cyberchondria travel together.", { x: M, y: 3.5, w: W - 2 * M, h: 0.6, fontSize: 24, color: "FFFFFF", align: "center" });
T(s, "Thank you · questions are welcome", { x: M, y: 4.7, w: W - 2 * M, h: 0.7, fontSize: 30, bold: true, color: "FFFFFF", align: "center" });
T(s, "Photos: StockSnap (CC0) · maps: Natural Earth (public domain)", { x: M, y: 6.8, w: W - 2 * M, h: 0.3, fontSize: 10, color: "8FA0BC", align: "center" });
s.addNotes("[ALL] Leave this slide up during questions. Each student answers on their own part; Student 2 takes statistics questions.");

// ---------------------------------------------------------------- one <a:pPr> per paragraph (pptxgenjs writes one per run)
async function fixParagraphProps(file) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const PPR = /<a:pPr\b[^>]*?\/>|<a:pPr\b[^>]*>[\s\S]*?<\/a:pPr>/g;
  for (const name of Object.keys(zip.files).filter((n) => /^ppt\/slides\/slide\d+\.xml$/.test(n))) {
    const xml = await zip.file(name).async("string");
    zip.file(name, xml.replace(/<a:p>([\s\S]*?)<\/a:p>/g, (m, inner) => { let seen = false; return "<a:p>" + inner.replace(PPR, (pp) => (seen ? "" : ((seen = true), pp))) + "</a:p>"; }));
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}
(async () => { await pres.writeFile({ fileName: OUTFILE }); await fixParagraphProps(OUTFILE); console.log("wrote", OUTFILE, pageNo, "slides"); })();
