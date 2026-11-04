// Defence presentation in the UOBCOM student-research style (watercolour background,
// college logos, green section titles, orange highlights, white boxed content).
// Usage: NODE_PATH=<node_modules with pptxgenjs> node 09_build_uobcom_deck.js <numbers.json> <assets dir> <questionnaire dir> <out.pptx>
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const [, , NUMS, ASSETS, QDIR, OUTFILE] = process.argv;
const N = JSON.parse(fs.readFileSync(NUMS, "utf8"));
const FIG = N.figdir;
const A = (f) => path.join(ASSETS, f);
const PH = (f) => path.join(ASSETS, "..", "photos", f); // CC0 photos (StockSnap) and Natural Earth maps; see photos/CREDITS.csv

// ---------------------------------------------------------------- style
const GREEN = "1E5B4F", ORANGE = "B45F06", INK = "222222", GREY = "666666", LINE = "BFBFBF", DECO = "8FA39F";
const BLUE = "0B5394", MAROON = "7F1D3A", PALE = "FFF7ED";
const HEAD = "Cambria", BODY = "Calibri";
const W = 10, H = 5.625;
const SHADOW = { type: "outer", blur: 4, offset: 2, angle: 45, color: "000000", opacity: 0.22 };

const pres = new pptxgen();
pres.defineLayout({ name: "UOB169", width: W, height: H });
pres.layout = "UOB169";
pres.title = "Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad";
pres.subject = "Graduation research defence, University of Baghdad College of Medicine";
pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };

// ---------------------------------------------------------------- helpers
function deco(s) {
  // the small "o o o" + hairline motif in two corners
  const dots = (x, y) => [0, 0.13, 0.26].forEach((d) => s.addShape(pres.shapes.OVAL, { x: x + d, y, w: 0.08, h: 0.08, fill: { type: "none" }, line: { color: DECO, width: 0.75 } }));
  dots(W - 0.62, 0.17);
  s.addShape(pres.shapes.LINE, { x: W - 3.2, y: 0.21, w: 2.5, h: 0, line: { color: DECO, width: 0.5 } });
  dots(0.25, H - 0.27);
  s.addShape(pres.shapes.LINE, { x: 0.68, y: H - 0.23, w: 2.5, h: 0, line: { color: DECO, width: 0.5 } });
}
function newSlide(bg, notes) {
  const s = pres.addSlide();
  s.background = { path: A(`bg${bg || 3}.jpg`) };
  deco(s);
  if (notes) s.addNotes(notes);
  return s;
}
// **orange bold** inline highlight; lines starting with "• " become bullets; "\n" separates paragraphs
function md(str, o = {}) {
  const runs = [];
  const paras = str.split("\n");
  paras.forEach((p, pi) => {
    let bullet = false;
    if (p.startsWith("• ")) { bullet = true; p = p.slice(2); }
    const parts = p.split(/(\*\*[^*]+\*\*)/).filter((t) => t.length);
    if (!parts.length) parts.push(" ");
    parts.forEach((t, ti) => {
      const hi = t.startsWith("**");
      const ro = {};
      if (hi) { ro.bold = true; ro.color = o.hiColor || ORANGE; }
      if (ti === 0 && bullet) ro.bullet = { indent: 14 };
      if (ti === parts.length - 1 && pi < paras.length - 1) ro.breakLine = true;
      runs.push({ text: hi ? t.slice(2, -2) : t, options: ro });
    });
  });
  return runs;
}
function txt(s, str, o) {
  s.addText(md(str, o), { fontFace: BODY, fontSize: 13, color: INK, margin: 0.04, valign: "top", paraSpaceAfter: 4, ...o });
}
function box(s, x, y, w, h, o = {}) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: o.fill || "FFFFFF" }, line: { color: o.line || LINE, width: 0.75 }, shadow: o.noShadow ? undefined : SHADOW });
}
function tag(s, text, style) {
  const w = Math.max(1.8, text.length * 0.095 + 0.6), x = (W - w) / 2;
  if (style === "orange") {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 0.28, w, h: 0.36, rectRadius: 0.06, fill: { color: ORANGE }, line: { color: ORANGE }, shadow: SHADOW });
    s.addText(text, { x, y: 0.28, w, h: 0.36, align: "center", valign: "middle", fontFace: BODY, fontSize: 14, bold: true, color: "FFFFFF", margin: 0 });
  } else {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 0.28, w, h: 0.34, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: "7F7F7F", width: 0.75 } });
    s.addText(text, { x, y: 0.28, w, h: 0.34, align: "center", valign: "middle", fontFace: BODY, fontSize: 13, bold: true, color: INK, margin: 0 });
  }
}
function bar(s, x, y, w, text, color, h = 0.34) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: color || GREEN }, line: { color: color || GREEN }, shadow: SHADOW });
  s.addText(text, { x: x + 0.1, y, w: w - 0.2, h, valign: "middle", fontFace: BODY, fontSize: 14, bold: true, color: "FFFFFF", margin: 0 });
}
function numBadge(s, x, y, n, color) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.3, h: 0.3, fill: { color: color || GREEN }, line: { color: color || GREEN } });
  s.addText(String(n), { x, y, w: 0.3, h: 0.3, align: "center", valign: "middle", fontSize: 12, bold: true, color: "FFFFFF", margin: 0, fontFace: BODY });
}
function figure(s, file, caption, x, y, maxW, maxH) {
  const a = N.aspect[file];
  let w = maxW, h = w / a;
  if (h > maxH) { h = maxH; w = h * a; }
  const fx = x + (maxW - w) / 2;
  box(s, fx - 0.08, y - 0.08, w + 0.16, h + 0.5);
  s.addImage({ path: path.join(FIG, file), x: fx, y, w, h, altText: caption });
  const [lab, rest] = caption.split(/:(.*)/s);
  s.addText([{ text: lab + ":", options: { bold: true, italic: true } }, { text: rest, options: { italic: true } }],
    { x: fx, y: y + h + 0.04, w, h: 0.36, fontSize: 10, color: INK, align: "center", valign: "middle", fontFace: BODY, margin: 0 });
}
function table(s, caption, head, rows, o) {
  const { x, y, w, colW, note, fontSize = 10.5, hi = [] } = o;
  const hdr = head.map((t) => ({ text: t, options: { bold: true, fill: { color: "DCE6E4" }, color: INK } }));
  const body = rows.map((r, ri) => r.map((t) => ({ text: String(t), options: { fill: { color: hi.includes(ri) ? PALE : ri % 2 ? "F5F7F7" : "FFFFFF" }, bold: hi.includes(ri) } })));
  const rowH = 0.27;
  const tH = rowH * (rows.length + 1);
  const extra = 0.42 + (note ? 0.34 : 0);
  box(s, x - 0.1, y - 0.42, w + 0.2, tH + extra + 0.05);
  const [lab, rest] = caption.split(/:(.*)/s);
  s.addText([{ text: lab + ":", options: { bold: true, italic: true } }, { text: rest, options: { italic: true } }], { x, y: y - 0.38, w, h: 0.32, fontSize: 11, color: INK, fontFace: BODY, margin: 0, valign: "middle" });
  s.addTable([hdr, ...body], { x, y, w, colW, rowH, fontFace: BODY, fontSize, color: INK, margin: [0.02, 0.06, 0.02, 0.06], valign: "middle", border: { type: "solid", pt: 0.5, color: "C8CFCD" } });
  if (note) s.addText(md(note), { x, y: y + tH + 0.03, w, h: 0.32, fontSize: 9, italic: true, color: GREY, fontFace: BODY, margin: 0, valign: "top" });
}
// ---- topic motifs drawn with shapes (stand in for the photos used in the reference deck)
function searchBar(s, x, y, w, query, sugg) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.46, rectRadius: 0.23, fill: { color: "FFFFFF" }, line: { color: "A6A6A6", width: 1 }, shadow: SHADOW });
  s.addShape(pres.shapes.OVAL, { x: x + 0.17, y: y + 0.11, w: 0.19, h: 0.19, fill: { type: "none" }, line: { color: GREY, width: 1.75 } });
  s.addShape(pres.shapes.LINE, { x: x + 0.33, y: y + 0.27, w: 0.08, h: 0.08, line: { color: GREY, width: 2 } });
  s.addText(md(query), { x: x + 0.5, y, w: w - 0.6, h: 0.46, fontSize: 12, color: "404040", valign: "middle", margin: 0, fontFace: BODY });
  if (sugg) {
    const hh = 0.3 * sugg.length + 0.1;
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.2, y: y + 0.5, w: w - 0.4, h: hh, fill: { color: "FFFFFF" }, line: { color: "D9D9D9", width: 0.75 }, shadow: SHADOW });
    sugg.forEach((t, i) => s.addText(md(t), { x: x + 0.35, y: y + 0.55 + i * 0.3, w: w - 0.7, h: 0.3, fontSize: 11, color: GREY, margin: 0, valign: "middle", fontFace: BODY }));
  }
}
function bubble(s, x, y, w, h, text, mine) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: mine ? GREEN : "FFFFFF" }, line: { color: mine ? GREEN : "BFBFBF", width: 0.75 }, shadow: SHADOW });
  s.addText(md(text), { x: x + 0.1, y, w: w - 0.2, h, fontSize: 11, color: mine ? "FFFFFF" : INK, valign: "middle", margin: 0, fontFace: BODY });
}
function photo(s, file, x, y, w, h) {
  s.addShape(pres.shapes.RECTANGLE, { x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, shadow: SHADOW });
  s.addImage({ path: PH(file), x, y, w, h, altText: file });
}
function divider(title, items, motif, notes) {
  const s = newSlide(1, notes);
  s.addText(title, { x: 0.6, y: 1.2, w: 6.5, h: 1.3, fontFace: HEAD, fontSize: 54, bold: true, color: GREEN, margin: 0, valign: "middle" });
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
    { x: 0.8, y: 2.6, w: 4.6, h: 0.3 * items.length + 0.2, fontFace: BODY, fontSize: 14, bold: true, color: INK, margin: 0, paraSpaceAfter: 2 });
  motif(s);
  return s;
}

const S1 = "[STUDENT 1 — Introduction & Methods]\n";
const S2 = "[STUDENT 2 — Results]\n";
const S3 = "[STUDENT 3 — Discussion & Conclusions]\n";

// ================================================================ 1 Title
let s = newSlide(1, S1 + "Good morning. We are [names], supervised by [supervisor]. Our research is titled: Health anxiety, AI chatbot use and cyberchondria among adults in Baghdad. In simple words: what happens when worried people search their symptoms online, and now ask AI chatbots like ChatGPT, before they see a doctor.");
s.addImage({ path: A("logo_uob.png"), x: 0.35, y: 0.3, w: 0.95, h: 0.95 });
s.addImage({ path: A("logo_med.png"), x: W - 1.2, y: 0.3, w: 0.8, h: 0.95 });
s.addText("Ministry of Higher Education and Scientific Research\nUniversity of Baghdad – College of Medicine", { x: 1.5, y: 0.35, w: 7.0, h: 0.75, align: "center", fontFace: BODY, fontSize: 14, bold: true, color: GREEN, margin: 0 });
s.addText("Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad", { x: 0.5, y: 1.35, w: 9.0, h: 0.95, align: "center", fontFace: HEAD, fontSize: 24, bold: true, color: INK, margin: 0, valign: "middle" });
s.addText("An online cross-sectional survey", { x: 0.5, y: 2.25, w: 9.0, h: 0.35, align: "center", fontFace: BODY, fontSize: 14, italic: true, color: ORANGE, margin: 0 });
s.addText([
  { text: "Prepared by:", options: { bold: true, color: GREEN, breakLine: true } },
  { text: "[Student 1 full name]", options: { italic: true, breakLine: true } },
  { text: "[Student 2 full name]", options: { italic: true, breakLine: true } },
  { text: "[Student 3 full name]", options: { italic: true, breakLine: true } },
  { text: " ", options: { fontSize: 6, breakLine: true } },
  { text: "Supervisor:", options: { bold: true, color: GREEN, breakLine: true } },
  { text: "[Title and full name]", options: { italic: true } },
], { x: 0.6, y: 2.85, w: 4.2, h: 2.2, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "top" });
photo(s, "title_phone.jpg", 5.05, 2.75, 4.4, 2.45);
searchBar(s, 5.35, 2.95, 3.8, "headache for 3 days causes **brain tumour**");
bubble(s, 6.45, 4.45, 2.85, 0.5, "Could my headache be serious?", true);

// ================================================================ 2 Quote
s = newSlide(2, S1 + "We open with two lines. The hadith reminds us that every illness has a cure, so seeking knowledge about health is good. The second line, from Montaigne, describes health anxiety exactly: the fear of illness is itself a kind of suffering. Our study sits between these two ideas: looking for information can help, or it can feed fear.");
box(s, 0.7, 1.25, 4.3, 1.2);
s.addText([{ text: "مَا أَنْزَلَ اللَّهُ دَاءً إِلَّا أَنْزَلَ لَهُ شِفَاءً", options: { breakLine: true, fontSize: 20, bold: true, rtlMode: true } },
  { text: "صحيح البخاري", options: { fontSize: 12, color: ORANGE, rtlMode: true } }],
  { x: 0.8, y: 1.3, w: 4.1, h: 1.1, align: "right", fontFace: "Arial", color: INK, margin: 0.05, valign: "middle", rtlMode: true });
box(s, 0.7, 2.75, 4.3, 1.3);
s.addText([{ text: "“He who fears he shall suffer, already suffers what he fears.”", options: { bold: true, breakLine: true } },
  { text: "Michel de Montaigne", options: { fontSize: 12, color: ORANGE, italic: true } }],
  { x: 0.85, y: 2.8, w: 4.0, h: 1.2, fontFace: BODY, fontSize: 16, color: INK, margin: 0.05, valign: "middle" });
photo(s, "quote_worried_laptop.jpg", 5.5, 1.25, 3.9, 3.3);
searchBar(s, 5.3, 1.0, 3.6, "is my chest pain a heart attack?");
bubble(s, 7.0, 4.2, 2.3, 0.45, "…but what if it is?", true);

// ================================================================ 3 Objectives
s = newSlide(3, S1 + "Our aim was to study the relationship between health anxiety and cyberchondria among adults in Baghdad who search for health information online. We had four objectives. First, describe how people search, including AI chatbots. Second, measure health anxiety and cyberchondria and how strongly they are linked. Third, look for pathways that fit a vicious cycle. Fourth, see how all this affects what people do before and during the consultation.");
s.addText("Objectives", { x: 0.6, y: 0.55, w: 4, h: 0.5, fontFace: HEAD, fontSize: 24, bold: true, color: GREEN, margin: 0 });
txt(s, [
  "• **Describe** online and AI-chatbot health-information seeking and pre-consultation behaviour among adults in Baghdad.",
  "• **Estimate** levels of health anxiety and cyberchondria and the **strength of their association**, independent of other factors.",
  "• **Examine pathways** consistent with a mutually reinforcing cycle between the two.",
  "• **Relate** both to pre-consultation behaviour, **disclosure** of searches to doctors and **trust** in physicians.",
].join("\n"), { x: 0.8, y: 1.3, w: 8.4, h: 3.0, fontSize: 16, paraSpaceAfter: 12 });
box(s, 0.8, 4.35, 8.4, 0.65, { fill: PALE, line: "E8C9A6", noShadow: true });
txt(s, "**Primary hypothesis (H1–H2):** health anxiety is positively associated with cyberchondria, independently of socio-demographic and digital-use factors.", { x: 0.95, y: 4.4, w: 8.1, h: 0.55, fontSize: 13, valign: "middle", hiColor: GREEN });

// ================================================================ 4 Divider: Introduction
divider("Introduction", ["Health anxiety", "Cyberchondria", "The vicious cycle", "From search engines to AI chatbots", "Rationale"], (s) => {
  photo(s, "intro_phone.jpg", 5.7, 0.95, 3.8, 3.6);
  searchBar(s, 5.4, 4.25, 3.7, "rash on arm meaning **skin cancer**");
}, S1 + "We will start with the background: what health anxiety is, what cyberchondria is, how they may feed each other, and why AI chatbots change the picture.");

// ================================================================ 5 Health anxiety
s = newSlide(3, S1 + "Health anxiety is a persistent worry about having a serious illness. It is a spectrum: most people have some health worry; at the far end it becomes illness anxiety disorder or somatic symptom disorder in DSM-5. The cognitive-behavioural model says normal sensations are misread as signs of disease, and safety behaviours such as checking and reassurance seeking give short relief but keep the worry going. It is common and costly. In Iraq, about half of online respondents reported health anxiety during COVID. We measured it with the Short Health Anxiety Inventory, SHAI-14.");
tag(s, "Health Anxiety");
bar(s, 0.5, 0.85, 4.4, "Definition & model", GREEN);
box(s, 0.5, 1.19, 4.4, 2.1);
txt(s, "• Persistent preoccupation with **having or acquiring a serious illness**.\n• A **continuum**: everyday worry → illness anxiety disorder / somatic symptom disorder (DSM-5).\n• Cognitive model: misreading normal sensations → anxiety → **checking & reassurance seeking** → short relief → worry returns.", { x: 0.6, y: 1.25, w: 4.2, h: 2.0, fontSize: 13 });
bar(s, 5.1, 0.85, 4.4, "Burden", ORANGE);
box(s, 5.1, 1.19, 4.4, 2.1);
txt(s, "• Lifetime prevalence **≈ 6%** in the population, up to **20%** in hospital outpatients.\n• Costly: **unnecessary medical contacts**; scores rising over three decades.\n• Iraq (COVID-19 online survey, n = 1591): **about half** reported health anxiety.", { x: 5.2, y: 1.25, w: 4.2, h: 2.0, fontSize: 13 });
bar(s, 0.5, 3.55, 9.0, "How we measured it", BLUE);
box(s, 0.5, 3.89, 9.0, 1.15);
txt(s, "**SHAI-14** (Short Health Anxiety Inventory): 14 items scored 0–3, total **0–42**. Validated in clinical and non-clinical samples; Arabic version validated in Saudi Arabia.\nWe used **≥ 18** to mark **elevated** health anxiety (a screening threshold, not a diagnosis).", { x: 0.6, y: 3.95, w: 8.8, h: 1.05, fontSize: 13 });

// ================================================================ 6 Cyberchondria
s = newSlide(3, S1 + "The word cyberchondria comes from White and Horvitz, who analysed search logs and found that searches for common, benign symptoms often escalated to rare and serious diagnoses. Starcevic and Berle defined it as excessive or repeated online health searching that increases rather than relieves distress. Searching itself is normal; it becomes cyberchondria when it is excessive, compulsive and distressing. We measured it with the CSS-12, which has four parts: excessiveness, compulsion, distress and reassurance seeking.");
tag(s, "Cyberchondria");
box(s, 0.5, 0.85, 9.0, 1.35);
txt(s, "**Definition:** excessive or repeated online searching for health information that **increases, rather than relieves,** distress or anxiety (Starcevic & Berle).\nSearch logs showed benign-symptom searches often **escalate to rare, serious diagnoses** (White & Horvitz). Searching is normal; it becomes cyberchondria when it is **excessive, compulsive and distressing**.", { x: 0.6, y: 0.9, w: 8.8, h: 1.25, fontSize: 12.5 });
s.addText("CSS-12: four facets (3 items each, total 12–60)", { x: 0.5, y: 2.35, w: 9, h: 0.35, fontSize: 14, bold: true, color: GREEN, margin: 0, fontFace: BODY });
[["Excessiveness", "Searching the same symptom again and again", BLUE],
 ["Compulsion", "Searching interrupts work and social life", MAROON],
 ["Distress", "Feeling worse, panicking after reading", ORANGE],
 ["Reassurance", "Searching leads to consulting a doctor", GREEN]].forEach(([h, b, c], i) => {
  const x = 0.5 + i * 2.28;
  bar(s, x, 2.8, 2.1, h, c);
  box(s, x, 3.14, 2.1, 1.1);
  txt(s, b, { x: x + 0.08, y: 3.2, w: 1.95, h: 1.0, fontSize: 12 });
});
txt(s, "Arabic CSS-12 versions show the same four-factor structure (Lebanon, Saudi Arabia).", { x: 0.5, y: 4.55, w: 9, h: 0.4, fontSize: 11, italic: true, color: GREY });

// ================================================================ 7 The cycle
s = newSlide(3, S1 + "Why study these together? Meta-analyses show health anxiety correlates strongly with cyberchondria, around r = 0.62. Health-anxious people feel worse after searching, while people with low anxiety feel relieved. A Dutch study of 5322 adults over four waves suggested the relationship goes both ways. This is the cycle on the slide: anxiety drives searching, searching drives distress, distress drives reassurance seeking, and reassurance does not last. We tested whether our data fit this cycle.");
tag(s, "The Vicious Cycle");
const cyc = [["Health anxiety", 6.6, 0.95, GREEN], ["Excessive searching", 8.25, 2.3, BLUE], ["Post-search distress", 6.6, 3.65, ORANGE], ["Reassurance seeking", 4.95, 2.3, MAROON]];
cyc.forEach(([t, cx, cy, c]) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx - 0.8, y: cy, w: 1.6, h: 0.7, rectRadius: 0.1, fill: { color: c }, line: { color: c }, shadow: SHADOW });
  s.addText(t, { x: cx - 0.8, y: cy, w: 1.6, h: 0.7, align: "center", valign: "middle", fontSize: 12, bold: true, color: "FFFFFF", margin: 0.03, fontFace: BODY });
});
const arr = (x1, y1, x2, y2) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1, line: { color: "404040", width: 1.75, endArrowType: "triangle" } });
arr(7.4, 1.5, 8.1, 2.25); arr(8.1, 3.05, 7.4, 3.75); arr(5.8, 3.75, 5.1, 3.05); arr(5.1, 2.25, 5.8, 1.5);
box(s, 0.5, 0.9, 3.7, 3.65);
txt(s, "• Meta-analyses: health anxiety ↔ cyberchondria **r ≈ 0.62–0.63**.\n• High-anxiety users feel **worse** after searching; low-anxiety users feel **relieved**.\n• Dutch 4-wave panel (n = 5322): evidence of a **reciprocal** relationship.\n• Reassurance gives **short relief**, so the cycle repeats.", { x: 0.6, y: 1.0, w: 3.5, h: 3.5, fontSize: 13.5, paraSpaceAfter: 10 });
txt(s, "Proposed cycle (cognitive-behavioural model)", { x: 4.6, y: 4.6, w: 4.4, h: 0.35, fontSize: 11, italic: true, color: GREY, align: "center" });

// ================================================================ 8 AI chatbots
s = newSlide(3, S1 + "Almost all the evidence comes from the search-engine era. AI chatbots are different: they answer fluently and personally, can be asked again and again, and can sound more empathetic than doctors. In a US survey about one in five people used ChatGPT for health information, and about a third changed medications or asked for referrals based on its answers. No study had compared AI chatbots with search engines in Iraq.");
tag(s, "From “Dr Google” to “Dr ChatGPT”");
bar(s, 0.5, 0.85, 4.6, "What changes with AI chatbots?", BLUE);
box(s, 0.5, 1.19, 4.6, 2.55);
txt(s, "• **Fluent, personalised, conversational** answers.\n• Can be questioned **again and again**: “one more question”.\n• Answers may seem **more empathetic** than physicians’.\n• US survey: ~**1 in 5** used ChatGPT for health; ~**1/3** of them changed medication or asked for referrals.", { x: 0.6, y: 1.25, w: 4.4, h: 2.45, fontSize: 13.5, paraSpaceAfter: 6 });
photo(s, "ai_robot.jpg", 5.45, 0.9, 4.0, 3.0);
bubble(s, 5.25, 3.2, 2.7, 0.5, "I feel tired and my hands shake. Is it serious?", true);
box(s, 0.5, 4.1, 9.0, 0.85, { fill: PALE, line: "E8C9A6", noShadow: true });
txt(s, "**Rationale:** first CSS-12 data from Baghdad · AI chatbots studied **separately** from search engines · psychology linked to **real behaviour before the consultation**. More than **80%** of Iraqis are online.", { x: 0.65, y: 4.15, w: 8.7, h: 0.75, fontSize: 12.5, valign: "middle" });

// ================================================================ 9 Divider: Methodology
divider("Methodology", ["Study design & setting", "Participants & sampling", "Sample size", "Questionnaire", "Statistical analysis"], (s) => {
  const p = path.join(QDIR, "c-01.png");
  box(s, 6.05, 0.75, 3.06, 3.9);
  s.addImage({ path: p, x: 6.13, y: 0.83, w: 2.9, h: 3.7 });
}, S1 + "Now the methodology: design, participants, sample size, the questionnaire and the analysis.");

// ================================================================ 10 Study design
s = newSlide(3, S1 + `This was an analytical cross-sectional study, reported using the STROBE and CHERRIES checklists. Data were collected online in Baghdad from ${N.d0} to ${N.d1}. We used convenience and snowball sampling through social media and messaging groups based in Baghdad. Inclusion: 18 or older, able to read Arabic or English, and gave consent. Participation was anonymous and voluntary, with electronic consent before any question.`);
tag(s, "Study Design & Settings");
bar(s, 0.5, 0.85, 4.7, "Study design & settings", GREEN);
box(s, 0.5, 1.19, 4.7, 1.75);
txt(s, `• **Analytical cross-sectional** online survey (STROBE, CHERRIES).\n• **Baghdad, Iraq**: ${N.d0} – ${N.d1}.\n• **Convenience + snowball** sampling via Baghdad-based social-media and messaging groups.`, { x: 0.6, y: 1.25, w: 4.5, h: 1.65, fontSize: 13 });
bar(s, 0.5, 3.15, 4.7, "Ethics", ORANGE);
box(s, 0.5, 3.49, 4.7, 1.5);
txt(s, "• **Anonymous & voluntary**; no names or contacts collected.\n• **Electronic consent** (and age ≥ 18) required before any question.\n• Approval: [committee, number, date].", { x: 0.6, y: 3.55, w: 4.5, h: 1.4, fontSize: 13 });
s.addText("Criteria", { x: 5.5, y: 0.85, w: 1.6, h: 0.36, fontSize: 15, bold: true, color: INK, margin: 0, fontFace: BODY });
[["1. Age ≥ 18 years", "Adult population; SHAI & CSS validated in adults"],
 ["2. Reads Arabic or English", "Bilingual questionnaire"],
 ["3. Gave informed consent", "Ethical requirement (e-consent page)"],
 ["4. Reached through Baghdad channels", "Defines the study setting"]].forEach(([c, b], i) => {
  const y = 1.35 + i * 0.9;
  s.addShape(pres.shapes.RECTANGLE, { x: 5.5, y, w: 2.15, h: 0.5, fill: { color: i % 2 ? GREEN : MAROON }, line: { color: "FFFFFF" }, shadow: SHADOW });
  s.addText(c, { x: 5.55, y, w: 2.05, h: 0.5, fontSize: 11.5, bold: true, color: "FFFFFF", valign: "middle", margin: 0, fontFace: BODY });
  s.addShape(pres.shapes.RECTANGLE, { x: 7.75, y: y + 0.03, w: 1.75, h: 0.6, fill: { color: "FFF2CC" }, line: { color: "D6B656", width: 0.75 } });
  s.addText(b, { x: 7.8, y: y + 0.03, w: 1.65, h: 0.6, fontSize: 10, color: INK, valign: "middle", margin: 0, fontFace: BODY });
});
s.addText("Basis", { x: 7.75, y: 0.85, w: 1.75, h: 0.36, fontSize: 13, bold: true, color: INK, margin: 0, fontFace: BODY, align: "center", fill: { color: "FFF2CC" }, line: { color: "D6B656" } });

// ================================================================ 11 Sample size & questionnaire
s = newSlide(3, S1 + `Sample size. Our main question is a correlation. With alpha 0.05 and 80% power we need ${N.nreq} people to detect a small-to-moderate correlation of 0.20. We collected ${N.n}, and the expected correlation from meta-analyses is much bigger, so the study is well powered (power about ${N.pw}). The questionnaire was a bilingual Google Form with five parts: consent and demographics; digital health seeking including AI chatbots; the SHAI-14; the CSS-12; and behaviour before the consultation and the relationship with the doctor. Every item was shown in Arabic and English.`);
tag(s, "Sample Size & Questionnaire");
bar(s, 0.5, 0.85, 3.6, "Sample size", BLUE);
box(s, 0.5, 1.19, 3.6, 3.8);
txt(s, `Primary outcome: **correlation** SHAI ↔ CSS\nFisher’s z, two-sided **α = 0.05**, **80% power**\nTo detect **r = 0.20** → **${N.nreq}** needed\n\nCollected: **n = ${N.n}**\nMargin of error for %: **±${N.moe}%**\nMeta-analytic r ≈ 0.62, so the target is **conservative**.`, { x: 0.65, y: 1.3, w: 3.3, h: 3.6, fontSize: 12.5, paraSpaceAfter: 5 });
[["1", "Consent & socio-demographics", "age, gender, education, study/work, chronic disease"],
 ["2", "Digital health seeking", "tools (search engines, **AI chatbots**…), motives, trust"],
 ["3", "SHAI-14", "health anxiety, 0–42"],
 ["4", "CSS-12", "cyberchondria, 12–60, four facets"],
 ["5", "Before the consultation", "behaviour after searching, **disclosure** to doctor, trust"]].forEach(([n, h, b], i) => {
  const y = 0.9 + i * 0.82;
  box(s, 4.35, y, 5.15, 0.68);
  numBadge(s, 4.45, y + 0.19, n, i === 2 || i === 3 ? ORANGE : GREEN);
  txt(s, `**${h}**\n${b}`, { x: 4.85, y: y + 0.03, w: 4.55, h: 0.62, fontSize: 11.5, paraSpaceAfter: 0, hiColor: INK, valign: "middle" });
});
txt(s, "Bilingual **Arabic–English** Google Form · Arabic wording by the research team", { x: 4.35, y: 4.98, w: 5.15, h: 0.3, fontSize: 10.5, italic: true, color: GREY });

// ================================================================ 12 Statistical analysis
s = newSlide(3, S1 + "For the analysis we used Python, with every step scripted so it can be reproduced, and we also prepared an SPSS file. We checked reliability and factor structure, then correlations, group comparisons, multivariable regression, and mediation with bootstrapping. Because we ran many tests, we corrected p-values with the false discovery rate method, and we labelled anything that did not survive as exploratory. Now my colleague will present the results.");
tag(s, "Statistical Analysis");
[["Describe", "Frequencies, mean ± SD, median (IQR); normality by Shapiro–Wilk", GREEN],
 ["Psychometrics", "Cronbach α, McDonald ω, confirmatory factor analysis (CFI, TLI, RMSEA, SRMR)", BLUE],
 ["Associations", "Pearson / Spearman (bootstrap CI), partial r; Mann–Whitney, Kruskal–Wallis; χ²", ORANGE],
 ["Multivariable", "Hierarchical robust (HC3) regression; logistic & ordinal logistic; AUC", MAROON],
 ["Pathways", "Bootstrapped mediation (5000 resamples); moderation by interaction terms", GREEN],
 ["Rigour", "Benjamini–Hochberg FDR for multiple testing; sensitivity analyses", BLUE]].forEach(([h, b, c], i) => {
  const x = 0.5 + (i % 3) * 3.05, y = 0.9 + Math.floor(i / 3) * 1.75;
  bar(s, x, y, 2.85, h, c);
  box(s, x, y + 0.34, 2.85, 1.2);
  txt(s, b, { x: x + 0.08, y: y + 0.4, w: 2.7, h: 1.1, fontSize: 12 });
});
box(s, 0.5, 4.5, 8.95, 0.5, { fill: PALE, line: "E8C9A6", noShadow: true });
txt(s, "Software: **Python 3** (pandas, SciPy, statsmodels, pingouin, semopy), fully scripted · SPSS dataset & syntax provided · **α = 0.05**, two-sided", { x: 0.6, y: 4.5, w: 8.75, h: 0.5, fontSize: 12, valign: "middle" });

// ================================================================ 13 Divider: Results
divider("Results", ["Participants", "How people search", "Levels & reliability", "Health anxiety ↔ cyberchondria", "Predictors & pathways", "Behaviour & AI chatbots"], (s) => {
  photo(s, "results_laptop.jpg", 5.7, 0.95, 3.8, 3.6);
}, S2 + "Thank you. I will present the results in six steps: who took part, how they search, the levels of health anxiety and cyberchondria, the main association, the predictors and pathways, and finally behaviour and AI chatbots.");

// ================================================================ 14 Table 1 participants
s = newSlide(3, S2 + `Opening: Table 1 shows our ${N.n} participants. Main finding: the sample is young, ${N.age20} aged 20 to 29, slightly more women at ${N.fem}, and ${N.med} are medical students; ${N.hb} have a health-related background, and ${N.chron} reported a chronic condition. ${N.ar} answered mainly in Arabic. Closing: so this is a young, educated, digitally active sample, and that matters when we interpret percentages.`);
tag(s, "Participants");
table(s, `Table 1: Socio-demographic characteristics of the participants (n = ${N.n})`, ["Variable", "Category", "n (%)"], [
  ["Age group (years)", "18–19 / 20–29 / 30–39 / ≥ 40", "56 (18.7) / 187 (62.3) / 21 (7.0) / 36 (12.0)"],
  ["Gender", "Female / Male", "169 (56.3) / 131 (43.7)"],
  ["Education", "Currently a student", "189 (63.0)"],
  ["Study / work", "Medical student", "132 (44.0)"],
  ["", "Other health-science student / healthcare worker", "43 (14.3) / 15 (5.0)"],
  ["", "Non-health student / non-health employee or other", "46 (15.3) / 64 (21.3)"],
  ["Health-related background", "Yes", "190 (63.3)"],
  ["Chronic medical condition", "Yes", "65 (21.7)"],
  ["Language relied on", "Arabic / English", "212 (70.7) / 88 (29.3)"],
], { x: 0.6, y: 1.25, w: 8.8, colW: [2.2, 3.5, 3.1], hi: [1, 3], note: "Health-related background = medical students, other health-science students and healthcare workers." });

// ================================================================ 15 Fig 1 tools
s = newSlide(3, S2 + `Opening: Figure 1 shows the tools people use and why. Main finding: AI chatbots are now the main gateway. ${N.ai_tick} ticked AI chatbots, ${N.ai} if we include those who named one, compared with ${N.se} for search engines. ${N.ai_only} use AI with no search engine at all, and ChatGPT alone is used by ${N.gpt}. The top motives are convenience at ${N.conv}, checking whether a doctor is needed at ${N.tri}, and instant reassurance at ${N.reas}. Closing: in summary, for this sample, the first doctor is often an AI chatbot.`);
tag(s, "How People Search", "orange");
figure(s, "fig2_tools_motives.png", "Figure 1: Tools used and motivations for searching for health information online (n = 300)", 0.45, 0.85, 9.1, 3.05);
[[N.ai_tick, "ticked AI chatbots"], [N.se, "search engines"], [N.ai_only, "AI without search engine"], [N.gpt, "use ChatGPT"]].forEach(([v, l], i) => {
  const x = 0.6 + i * 2.25;
  box(s, x, 4.48, 2.05, 0.6);
  s.addText([{ text: v + "  ", options: { bold: true, color: ORANGE, fontSize: 16 } }, { text: l, options: { fontSize: 10.5 } }], { x: x + 0.05, y: 4.48, w: 1.95, h: 0.6, valign: "middle", align: "center", margin: 0, fontFace: BODY, color: INK });
});

// ================================================================ 16 Table 3 levels & reliability
s = newSlide(3, S2 + `Opening: Table 3 shows the scores and reliability. Main finding: mean SHAI was ${N.shai_m} out of 42 and ${N.hac} scored 18 or more, our threshold for elevated health anxiety, with a 95% confidence interval of ${N.hac_ci}. Mean CSS was ${N.css_m} out of 60. Excessiveness was the highest facet and compulsion the lowest: people search a lot, but it rarely disrupts their lives. Both scales were reliable, alpha ${N.aS} and ${N.aC}, and reliability was the same in Arabic and English responders. Formal invariance testing showed the CSS-12 works the same way in both languages, and no single item behaved differently. Closing: our tools measured well in this population.`);
tag(s, "Levels & Reliability", "orange");
table(s, "Table 3: Descriptive statistics, reliability and language equivalence of the SHAI-14 and CSS-12 (n = 300)", ["Scale (range)", "Mean ± SD", "Median (IQR)", "α (95% CI)", "ω", "α Arabic / English"], [
  ["SHAI-14 (0–42)", "12.35 ± 5.83", "12 (8–16)", "0.81 (0.78–0.84)", "0.82", "0.81 / 0.81"],
  ["CSS-12 (12–60)", "28.86 ± 8.36", "29 (23–34)", "0.86 (0.84–0.89)", "0.87", "0.86 / 0.88"],
  ["  Excessiveness (3–15)", "9.66 ± 2.94", "10 (8–12)", "0.77 (0.72–0.81)", "0.77", ""],
  ["  Compulsion (3–15)", "5.00 ± 2.58", "4 (3–6)", "0.88 (0.86–0.90)", "0.89", ""],
  ["  Distress (3–15)", "7.24 ± 2.74", "7 (5–9)", "0.76 (0.71–0.81)", "0.77", ""],
  ["  Reassurance (3–15)", "6.96 ± 2.81", "7 (5–9)", "0.76 (0.71–0.81)", "0.77", ""],
], { x: 0.55, y: 1.25, w: 8.9, colW: [2.1, 1.3, 1.25, 1.65, 0.7, 1.9], hi: [0, 1], note: `CSS-12 four-factor CFA (ML): CFI ${N.cfaC}, RMSEA ${N.cfaR}, SRMR ${N.srmr}. Arabic vs English: means equal; CSS-12 scalar-invariant, SHAI-14 metric-invariant (multi-group CFA); no item DIF after FDR.` });
[[N.hac, "elevated health anxiety (SHAI ≥ 18)"], [N.hac_ci, "95% CI"]].forEach(([v, l], i) => {
  const x = 0.6 + i * 4.5;
  box(s, x, 4.15, 4.3, 0.75, { fill: PALE, line: "E8C9A6", noShadow: true });
  s.addText([{ text: v + "  ", options: { bold: true, color: ORANGE, fontSize: 22 } }, { text: l, options: { fontSize: 12 } }], { x, y: 4.15, w: 4.3, h: 0.75, align: "center", valign: "middle", margin: 0, fontFace: BODY, color: INK });
});

// ================================================================ 17 Fig 3 main association
s = newSlide(3, S2 + `Opening: this is our main result, Figure 3. Main finding: health anxiety and cyberchondria rise together, r = ${N.r}, 95% CI ${N.rci}, so health anxiety explains about ${N.r2} of the variation in cyberchondria. After adjusting for every other variable, the partial correlation is still ${N.pr}. The link is strongest for excessive searching, ${N.rE}, and distress, ${N.rD}, and weaker for compulsion and reassurance. Closing: in summary, hypotheses 1 and 2 are supported.`);
tag(s, "Health Anxiety ↔ Cyberchondria", "orange");
figure(s, "fig1_scatter_shai_css.png", "Figure 3: Health anxiety (SHAI-14) against cyberchondria (CSS-12), least-squares line and 95% band", 0.45, 0.9, 5.3, 3.75);
box(s, 6.1, 0.9, 3.4, 1.15);
s.addText([{ text: `r = ${N.r}`, options: { bold: true, color: ORANGE, fontSize: 28, breakLine: true } }, { text: `95% CI ${N.rci} · p < 0.001`, options: { fontSize: 12 } }], { x: 6.1, y: 0.9, w: 3.4, h: 1.15, align: "center", valign: "middle", margin: 0, fontFace: BODY, color: INK });
box(s, 6.1, 2.2, 3.4, 2.85);
txt(s, `Partial r (all covariates): **${N.pr}**\n\nBy CSS facet:\n• Excessiveness **${N.rE}**\n• Distress **${N.rD}**\n• Compulsion ${N.rC}\n• Reassurance ${N.rR}\n\nH1 & H2 **supported**`, { x: 6.25, y: 2.28, w: 3.15, h: 2.7, fontSize: 12.5, paraSpaceAfter: 1 });

// ================================================================ 18 Table 7 regression
s = newSlide(3, S2 + `Opening: Table 7 is the hierarchical regression for cyberchondria. Main finding: demographics alone explain only about 3% of cyberchondria. Adding digital-use variables brings it to 13%. Adding health anxiety adds another ${N.dR2}, to about 32%. Health anxiety is the strongest predictor, standardised beta ${N.beta}: each extra SHAI point adds about ${N.B} CSS points. Closing: who you are matters little; how anxious you are matters most.`);
tag(s, "What Predicts Cyberchondria?", "orange");
table(s, "Table 7: Hierarchical robust (HC3) linear regression of cyberchondria (CSS-12 total)", ["Block", "R²", "ΔR²", "p (change)"], [
  ["1. Socio-demographics", "0.030", "0.030", "—"],
  ["2. + Digital-use variables", "0.133", "0.103", "< 0.001"],
  ["3. + Health anxiety (SHAI-14)", "0.317", "0.184", "< 0.001"],
], { x: 0.55, y: 1.3, w: 5.0, colW: [2.6, 0.75, 0.75, 0.9], hi: [2] });
table(s, "Final model: key predictors", ["Predictor", "B (95% CI)", "β", "p"], [
  ["SHAI-14 (per point)", "0.68 (0.53–0.84)", "0.48", "< 0.001"],
  ["AI-chatbot user*", "5.33 (2.34–8.32)", "0.20", "< 0.001"],
  ["Age 30–39 (vs 20–29)", "6.27 (0.19–12.34)", "0.19", "0.043"],
  ["Gender, chronic, language, job", "n.s.", "", "> 0.5"],
], { x: 0.55, y: 3.0, w: 5.0, colW: [2.15, 1.45, 0.5, 0.9], hi: [0], fontSize: 10, note: "*Inclusive definition; with the strict definition the AI effect is not significant (slide 23)." });
box(s, 6.0, 0.9, 3.5, 4.15);
s.addText([{ text: "18.4%", options: { bold: true, color: ORANGE, fontSize: 34, breakLine: true } }, { text: "extra variance explained by health anxiety, after everything else", options: { fontSize: 13, breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 8 } },
  { text: "3%", options: { bold: true, color: GREEN, fontSize: 28, breakLine: true } }, { text: "explained by demographics alone", options: { fontSize: 13 } }],
  { x: 6.15, y: 1.0, w: 3.2, h: 3.95, align: "center", valign: "middle", margin: 0, fontFace: BODY, color: INK });

// ================================================================ 19 Fig 9 item by item
s = newSlide(3, S2 + `Opening: Figure 9 breaks the association down item by item, all 168 pairs. Main finding: ${N.ibF} pairs remained significant after FDR correction. The strongest links involve fear of serious illness and interpreting body sensations; for example fear of illness with panicking when reading about a rare condition. Simply noticing aches and pains was almost unrelated. Closing: what drives searching is fear and interpretation, not just noticing symptoms, exactly what the cognitive model predicts.`);
tag(s, "Item by Item: What Drives Searching?", "orange");
figure(s, "fig9_item_by_item.png", "Figure 9: Item-by-item Spearman correlations, SHAI-14 × CSS-12 (* FDR, ** Holm)", 0.45, 0.85, 5.0, 3.8);
[["ρ = 0.43", "Fear of serious illness ↔ panic on reading of a rare condition", ORANGE],
 ["ρ = 0.42", "Interpreting sensations ↔ searching every sensation", ORANGE],
 ["≈ 0", "Merely noticing aches / sensations", GREY]].forEach(([v, t, c], i) => {
  const y = 0.9 + i * 1.2;
  box(s, 5.9, y, 3.6, 1.0);
  txt(s, `${v}`, { x: 6.05, y: y + 0.05, w: 3.3, h: 0.4, fontSize: 18, bold: true, color: c });
  txt(s, t, { x: 6.05, y: y + 0.45, w: 3.3, h: 0.5, fontSize: 11.5 });
});
txt(s, `**${N.ibF}/168** pairs significant after FDR`, { x: 5.9, y: 4.6, w: 3.6, h: 0.35, fontSize: 12, align: "center" });

// ================================================================ 20 Fig 6 logistic
s = newSlide(3, S2 + `Opening: Figure 6 shows who has elevated health anxiety, in a multivariable logistic model. Main finding: three factors are independent. Each standard deviation of cyberchondria triples the odds, adjusted odds ratio ${N.orCSS}. Searching for instant reassurance almost quadruples them, ${N.orMot}. Older age is protective, ${N.orAge} per age step. The model discriminates well: AUC ${N.auc}, ${N.aucc} after correcting for optimism. Closing: the person most at risk is young and searches to feel reassured.`);
tag(s, "Who Has Elevated Health Anxiety?", "orange");
figure(s, "fig7_forest_HA.png", "Figure 6: Adjusted odds ratios for elevated health anxiety (SHAI ≥ 18). Orange: p < 0.05", 0.45, 0.85, 5.6, 3.8);
[[N.orCSS + "×", "odds per SD of cyberchondria", ORANGE], [N.orMot + "×", "if searching for instant reassurance", ORANGE], [N.orAge + "×", "per older age group (protective)", GREEN], [`${N.auc} → ${N.aucc}`, "AUC (apparent → optimism-corrected)", BLUE]].forEach(([v, l, c], i) => {
  const y = 0.85 + i * 1.06;
  box(s, 6.45, y, 3.05, 0.9);
  s.addText([{ text: v, options: { bold: true, color: c, fontSize: 20, breakLine: true } }, { text: l, options: { fontSize: 11 } }], { x: 6.5, y, w: 2.95, h: 0.9, align: "center", valign: "middle", margin: 0, fontFace: BODY, color: INK });
});

// ================================================================ 21 Fig 7 mediation
s = newSlide(3, S2 + `Opening: Figure 7 shows the pathways. Main finding: in model A, part of the link from health anxiety to post-search distress runs through excessive searching, indirect effect ${N.mA}, CI ${N.mAci}. In model B, post-search distress carries almost all of the link from health anxiety to reassurance-seeking visits: the direct effect drops to ${N.mCd}. But the reverse direction also fits, ${N.mD}. Closing: our data are compatible with the cycle, but one survey at one time point cannot prove direction. Hypothesis 3 is supported statistically, not causally.`);
tag(s, "Pathways: Is There a Cycle?", "orange");
figure(s, "fig8_mediation.png", "Figure 7: Mediation models (standardised; 5000 bootstrap resamples)", 0.45, 0.85, 9.1, 2.95);
box(s, 0.5, 4.35, 9.0, 0.7, { fill: PALE, line: "E8C9A6", noShadow: true });
txt(s, `Indirect via excessive searching **${N.mA}** (CI ${N.mAci}) · via distress **${N.mC}** (direct → **${N.mCd}**) · reverse path also **${N.mD}** → **compatible with a cycle, not proof of direction**`, { x: 0.65, y: 4.38, w: 8.7, h: 0.64, fontSize: 12, valign: "middle" });

// ================================================================ 22 Fig 2 behaviour
s = newSlide(3, S2 + `Opening: Figure 2 shows what people do after searching. Main finding: the most common response is to delay or skip care because they feel reassured, ${N.dr}. Others escalate: urgent visits ${N.urg}, multiple doctors ${N.mdoc}. Only ${N.always} always tell their doctor about their searches, and ${N.never} never do, for fear of being judged. Higher cyberchondria was linked with more disclosure, odds ratio ${N.nsC}, and this survived FDR correction. ${N.relneg} say searching complicated or reduced trust in their doctor. Closing: searching changes the consultation before it begins.`);
tag(s, "Behaviour Before the Consultation", "orange");
figure(s, "fig3_behaviours.png", "Figure 2: Behaviour after searching, disclosure to physicians and effect on the doctor–patient relationship", 0.45, 0.85, 9.1, 2.25);
[[N.dr, "delay / skip care because reassured"], [N.never, "never tell their doctor (fear of judgement)"], [`OR ${N.nsC}`, "higher cyberchondria → more disclosure (q = " + N.nsCq + ")"], [N.relneg, "say searching strained trust in doctors"]].forEach(([v, l], i) => {
  const x = 0.5 + i * 2.27;
  box(s, x, 3.75, 2.1, 1.25);
  s.addText([{ text: v, options: { bold: true, color: ORANGE, fontSize: 20, breakLine: true } }, { text: l, options: { fontSize: 11 } }], { x: x + 0.05, y: 3.75, w: 2.0, h: 1.25, align: "center", valign: "middle", margin: 0, fontFace: BODY, color: INK });
});

// ================================================================ 23 AI chatbots
s = newSlide(3, S2 + `Opening: finally, did AI chatbots themselves matter? Main finding: AI users scored ${N.Bai} points higher on cyberchondria after adjustment, mainly excessiveness and reassurance. But ${N.inc} people named a chatbot without ticking the AI option. When we use the strict definition, only people who ticked it, the effect disappears: B = ${N.Balt}, p = ${N.palt}. And only 34 people were true non-users. AI use also did not change the strength of the anxiety–cyberchondria link. Closing: no reliable independent effect of AI. Absence of evidence, not evidence of absence. I now hand over to my colleague for the discussion.`);
tag(s, "AI Chatbots: An Independent Effect?", "orange");
table(s, "Table: Adjusted difference in cyberchondria (CSS-12) for AI-chatbot users", ["Definition of AI user", "B (CSS points)", "95% CI", "p"], [
  ["Inclusive: ticked OR named a chatbot", `+${N.Bai}`, N.Baici, "< 0.001"],
  ["Strict: ticked “AI chatbots” only", `+${N.Balt}`, "—", N.palt],
], { x: 0.55, y: 1.3, w: 8.9, colW: [4.1, 1.6, 1.6, 1.6], hi: [1], note: `${N.inc} respondents named a chatbot without ticking it (mean CSS ${N.inc_css} vs ${N.non_css} in non-users); only 34 were non-users.` });
[["The classification decides it", `${N.inc} “named but not ticked” respondents had the **highest** scores`, ORANGE],
 ["Small comparison group", "Only **34** true non-users", BLUE],
 ["No moderation", "AI use did **not** change the SHAI ↔ CSS link", GREEN]].forEach(([h, b, c], i) => {
  const x = 0.5 + i * 3.05;
  bar(s, x, 3.15, 2.85, h, c);
  box(s, x, 3.49, 2.85, 0.95);
  txt(s, b, { x: x + 0.08, y: 3.55, w: 2.7, h: 0.85, fontSize: 12, valign: "middle" });
});
txt(s, "**Conclusion:** no reliable evidence that AI use is linked to cyberchondria **beyond health anxiety**.", { x: 0.5, y: 4.6, w: 9, h: 0.4, fontSize: 13, align: "center", hiColor: GREEN });

// ================================================================ 24 Divider: Discussion
divider("Discussion", ["Our main finding vs the world", "Why weaker than meta-analyses?", "AI chatbots", "The consultation", "Medical students", "Limitations & future directions"], (s) => {
  photo(s, "discussion_doctor.jpg", 5.7, 0.95, 3.8, 3.6);
  bubble(s, 5.4, 4.15, 3.4, 0.55, "So, is searching the problem, or the anxiety?", true);
}, S3 + "Thank you. I will discuss what these results mean, how they compare with other studies, our limitations, and our conclusions.");

// ================================================================ 25 First in Baghdad
s = newSlide(3, S3 + `To our knowledge, this is the first study to use the CSS-12 in Baghdad, and among the first anywhere to look at AI chatbots next to search engines before seeing a doctor. Our main finding, r = ${N.r}, supports our first two hypotheses: health anxiety and cyberchondria go together, independently of everything else we measured.`);
box(s, 0.6, 1.3, 5.2, 2.6);
txt(s, `To our knowledge, this is the **first** study to apply the CSS-12 in a **Baghdad**-based sample, and among the first to place **AI chatbots** alongside search engines as a source of health information before consulting a doctor.\n\nHealth anxiety and cyberchondria were **moderately and robustly associated (r = ${N.r})**, independent of all other measured factors.`, { x: 0.75, y: 1.4, w: 4.9, h: 2.4, fontSize: 14, paraSpaceAfter: 6 });
s.addImage({ path: PH("map_iraq.png"), x: 6.05, y: 0.75, w: 3.5, h: 3.5, altText: "Map of Iraq with Baghdad marked" });
s.addText([{ text: `n = ${N.n}  ·  `, options: { fontSize: 16 } }, { text: `r = ${N.r}`, options: { bold: true, color: ORANGE, fontSize: 22 } }], { x: 6.05, y: 4.35, w: 3.5, h: 0.5, align: "center", valign: "middle", margin: 0, fontFace: HEAD, color: INK });

// ================================================================ 25b World map header (as in the reference deck)
s = newSlide(3, S3 + "Now, how do our results compare with studies from around the world?");
tag(s, "Comparison with Worldwide Results", "orange");
s.addImage({ path: PH("map_world.png"), x: 0.9, y: 1.0, w: 8.2, h: 4.1, altText: "World map, Baghdad marked" });

// ================================================================ 26 Compared with world
s = newSlide(3, S3 + `Our correlation of ${N.r} is weaker than the pooled estimates of about 0.62 from meta-analyses. Several reasons: first, measurement error; corrected for reliability it would be about ${N.disr}, close to the meta-analytic range. Second, our sample had low health anxiety, and a narrow range weakens correlations. Third, online recruitment may favour confident, habitual internet users. Fourth, most earlier studies used the full 33-item scale.`);
tag(s, "Comparison with Worldwide Results", "orange");
box(s, 0.5, 0.9, 4.2, 1.35);
txt(s, `Our study: **r = ${N.r}**\nMeta-analyses (McMullan 2019; Mestre-Bach 2023): **r ≈ 0.62–0.63**\nOur r corrected for unreliability: **≈ ${N.disr}**`, { x: 0.6, y: 0.95, w: 4.0, h: 1.25, fontSize: 13, paraSpaceAfter: 4 });
s.addText("Why weaker?", { x: 0.5, y: 2.4, w: 4.2, h: 0.35, fontSize: 14, bold: true, color: GREEN, margin: 0, fontFace: BODY });
[["Measurement error", "Corrected for reliability, r ≈ " + N.disr],
 ["Narrow range", `Low health anxiety (mean SHAI ${N.shai_m}) attenuates r`],
 ["Who answered", "Online recruitment favours confident, habitual users"],
 ["Short form", "Most earlier studies used the 33-item CSS"]].forEach(([h, b], i) => {
  const y = 2.8 + i * 0.57;
  numBadge(s, 0.5, y + 0.05, i + 1, i % 2 ? ORANGE : GREEN);
  txt(s, `**${h}:** ${b}`, { x: 0.9, y, w: 3.8, h: 0.5, fontSize: 11.5, hiColor: INK, valign: "middle" });
});
const studies = [["Meta-analysis (2019)", 0.62], ["Meta-analysis (2023)", 0.63], ["Our study, corrected", parseFloat(N.disr)], ["Our study", parseFloat(N.r)]];
box(s, 5.0, 0.9, 4.5, 4.15);
s.addText("Correlation: health anxiety ↔ cyberchondria", { x: 5.1, y: 0.95, w: 4.3, h: 0.35, fontSize: 12, bold: true, color: INK, align: "center", margin: 0, fontFace: BODY });
studies.forEach(([l, v], i) => {
  const y = 1.5 + i * 0.85;
  s.addText(l, { x: 5.15, y, w: 4.2, h: 0.3, fontSize: 11, color: INK, margin: 0, fontFace: BODY });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.15, y: y + 0.32, w: 3.4 * v / 0.7, h: 0.3, fill: { color: i === 3 ? ORANGE : i === 2 ? "E3A869" : "9DB3AE" }, line: { color: "FFFFFF" } });
  s.addText(v.toFixed(2), { x: 5.2 + 3.4 * v / 0.7, y: y + 0.32, w: 0.6, h: 0.3, fontSize: 11, bold: true, color: INK, margin: 0, valign: "middle", fontFace: BODY });
});

// ================================================================ 27 Regional
s = newSlide(3, S3 + "Our findings agree with the Arab region. In Jeddah, cyberchondria was common and linked with smartphone addiction. In Saudi primary care, cyberchondria was linked with health anxiety. In Lebanon, the Arabic CSS-12 had the same structure as ours. And among 1435 Egyptian medical students, the group closest to ours, most had moderate cyberchondria.");
tag(s, "Comparison with Regional Studies", "orange");
photo(s, "map_region.png", 0.55, 0.95, 4.4, 3.3);
[["Saudi Arabia – Jeddah", "Cyberchondria **common**, linked with **smartphone addiction**", GREEN],
 ["Saudi Arabia – primary care", "Cyberchondria linked with **health anxiety**", GREEN],
 ["Lebanon", "Arabic CSS-12: **same four-factor structure** as ours", MAROON],
 ["Egypt – 1435 medical students", "**85.8%** moderate cyberchondria; health worry predicted it", BLUE]].forEach(([h, b, c], i) => {
  const y = 0.9 + i * 0.88;
  bar(s, 5.3, y, 4.2, h, c, 0.3);
  box(s, 5.3, y + 0.3, 4.2, 0.48);
  txt(s, b, { x: 5.38, y: y + 0.3, w: 4.05, h: 0.48, fontSize: 11.5, valign: "middle" });
});
txt(s, "Our results are **in line** with emerging Arab-region data.", { x: 0.5, y: 4.6, w: 9, h: 0.4, fontSize: 13, align: "center" });

// ================================================================ 28 AI & consultation
s = newSlide(3, S3 + `AI use in our sample, ${N.ai_tick} to ${N.ai}, is far higher than in a 2024 US survey, about 1 in 5, and a 2025 survey, 21%. Our sample is young; AI use fell from 96% at 18 to 19 years to 72% at 40 and above. On the consultation: delaying care because of reassurance can save visits for minor symptoms, but risks delayed diagnosis for serious ones, and it happened across all anxiety levels. About a third never tell their doctor what they searched. So doctors should ask.`);
tag(s, "AI Chatbots & the Consultation");
bar(s, 0.5, 0.85, 4.4, "AI chatbots", BLUE);
box(s, 0.5, 1.19, 4.4, 3.0);
txt(s, `• Our use **${N.ai_tick}–${N.ai}** vs ~**20%** (US 2024) and **21%** (2025 survey).\n• Young sample: AI use fell from **96%** (18–19 y) to **72%** (≥ 40 y).\n• Conversational AI may invite “**one more question**” (excessiveness, reassurance).\n• Higher trust → **fewer** multiple-doctor visits, but a trend to **delay care** (OR 1.33, p = 0.088).`, { x: 0.6, y: 1.25, w: 4.2, h: 2.9, fontSize: 13.5, paraSpaceAfter: 8 });
bar(s, 5.1, 0.85, 4.4, "The consultation", ORANGE);
box(s, 5.1, 1.19, 4.4, 3.0);
txt(s, `• Delay because reassured (**${N.dr}**): saves visits, but risks **delayed diagnosis**; seen at **all** anxiety levels.\n• **${N.never}** never disclose searches (fear of judgement).\n• Higher cyberchondria → **more** disclosure (robust); health anxiety → concealment (**exploratory**).\n• H4 only **partially** supported.`, { x: 5.2, y: 1.25, w: 4.2, h: 2.9, fontSize: 13.5, paraSpaceAfter: 8 });
box(s, 0.5, 4.4, 9.0, 0.6, { fill: PALE, line: "E8C9A6", noShadow: true });
txt(s, "**Clinical message:** ask every patient, without judgement, what they searched or asked an AI.", { x: 0.65, y: 4.4, w: 8.7, h: 0.6, fontSize: 13.5, valign: "middle", align: "center", hiColor: GREEN });

// ================================================================ 29 Medical students
s = newSlide(3, S3 + `${N.med} of our sample were medical students, a distinct group: high medical awareness, academic stress, and exposure to descriptions of serious disease. They had higher unadjusted health anxiety, but this disappeared after adjustment, because they are younger, and age was the independent factor. Their cyberchondria scores were identical to everyone else's. So medical knowledge did not protect against cyberchondria.`);
box(s, 0.6, 0.8, 5.5, 0.8);
txt(s, `**${N.med}** of our sample were **medical students**, a distinct group:`, { x: 0.75, y: 0.85, w: 5.2, h: 0.7, fontSize: 14, valign: "middle" });
box(s, 0.6, 1.8, 5.5, 1.3, { fill: PALE, line: "E8C9A6" });
txt(s, "• **Heightened medical awareness** of rare and serious diseases.\n• **High academic stress.**\n• The popular idea of “medical student syndrome” (weak evidence).", { x: 0.75, y: 1.85, w: 5.2, h: 1.2, fontSize: 13, paraSpaceAfter: 2 });
box(s, 0.6, 3.3, 5.5, 1.75);
txt(s, "Higher unadjusted health anxiety, but this **disappeared after adjustment**: it reflected their **younger age**.\nCyberchondria scores were **identical** to other participants’: **medical knowledge did not protect** against cyberchondria.", { x: 0.75, y: 3.35, w: 5.2, h: 1.65, fontSize: 13, paraSpaceAfter: 6 });
photo(s, "students_laptop.jpg", 6.45, 0.8, 3.0, 4.25);

// ================================================================ 30 Limitations
s = newSlide(3, S3 + "We have several limitations. First, the design is cross-sectional, so we cannot prove direction; the mediation is statistical, not causal. Second, the sample is online convenience and snowball, young, and heavy in medical students, so percentages cannot be generalised to all of Baghdad, although associations were consistent across subgroups. Third, the Arabic wording was ours, without formal back-translation, although reliability and means were the same in both languages. Fourth, behaviour items were single, non-validated questions. Fifth, many tests; we corrected with FDR.");
tag(s, "Limitations");
[["Cross-sectional design", "Cannot establish direction; mediation is **statistical, not causal**"],
 ["Online convenience sample", `Young, **${N.med}** medical students; percentages **not generalisable**, associations consistent across subgroups`],
 ["Arabic wording", "Team translation without formal back-translation; but CSS-12 **fully invariant** and SHAI-14 metric invariant across languages, no item DIF"],
 ["Single-item measures", "Behaviour, disclosure and trust items **not validated**; labelled exploratory"],
 ["Multiple testing & self-report", "FDR correction applied; recall and social-desirability bias possible"]].forEach(([h, b], i) => {
  const y = 0.85 + i * 0.84;
  numBadge(s, 0.5, y + 0.17, i + 1, i % 2 ? ORANGE : GREEN);
  box(s, 0.95, y, 8.55, 0.7);
  txt(s, `**${h}:** ${b}`, { x: 1.05, y, w: 8.35, h: 0.7, fontSize: 13.5, valign: "middle", hiColor: GREEN });
});

// ================================================================ 31 Future directions & recommendations
s = newSlide(3, S3 + "For the future: longitudinal studies to test the cycle over time; experiments comparing AI chatbot and search-engine answers; probability sampling of all Baghdad adults; and formally adapted Arabic scales. ClinicalTrials.gov lists only nine cyberchondria studies and none in Iraq, so intervention trials are a clear gap. For practice: doctors should ask about searches; the Ministry may consider digital and AI health-literacy campaigns; and AI developers may consider anxiety-aware answers.");
tag(s, "Future Directions & Recommendations");
bar(s, 0.5, 0.85, 4.4, "Future research should prioritise:", GREEN);
box(s, 0.5, 1.19, 4.4, 3.8);
txt(s, "• **Longitudinal** / experience-sampling studies of the cycle.\n• **Experiments**: AI chatbot vs search-engine answers and anxiety.\n• **Probability sampling** of Baghdad adults, including older and less-educated people.\n• **Formally adapted Arabic** scales with invariance testing.\n• **Intervention trials**: only **9** cyberchondria studies on ClinicalTrials.gov, **none in Iraq**.", { x: 0.6, y: 1.25, w: 4.2, h: 3.7, fontSize: 13.5, paraSpaceAfter: 10 });
[["Clinicians", "Ask, without judgement, what patients searched or asked an AI; screen with the SHAI", BLUE],
 ["Ministry of Health", "May consider Arabic digital and AI health-literacy campaigns; warn about false reassurance", ORANGE],
 ["AI developers", "May consider anxiety-aware answers that do not escalate rare diagnoses", MAROON]].forEach(([h, b, c], i) => {
  const y = 0.85 + i * 1.4;
  bar(s, 5.1, y, 4.4, h, c);
  box(s, 5.1, y + 0.34, 4.4, 0.9);
  txt(s, b, { x: 5.2, y: y + 0.38, w: 4.2, h: 0.82, fontSize: 12.5, valign: "middle" });
});

// ================================================================ 32 Conclusion
s = newSlide(3, S3 + `To conclude. AI chatbots, mainly ChatGPT, are now the main source of health information before seeing a doctor in our sample. About one in five has elevated health anxiety. Health anxiety and cyberchondria are moderately and robustly linked, r = ${N.r}, compatible with a cycle. We found no reliable independent effect of AI. And searching shapes the consultation: delays, non-disclosure and strained trust. Thank you.`);
s.addText("Conclusion", { x: 0.6, y: 0.5, w: 4, h: 0.5, fontFace: HEAD, fontSize: 24, bold: true, color: GREEN, margin: 0 });
box(s, 0.6, 1.15, 8.8, 3.85);
txt(s, [
  `• **AI chatbots** (mainly ChatGPT) are a leading source of health information: **${N.ai_tick}** ticked them (**${N.ai}** incl. named), more than search engines.`,
  `• **${N.hac}** had elevated health anxiety (SHAI ≥ 18, a screening threshold); younger people and reassurance-seekers most affected.`,
  `• Health anxiety and cyberchondria are **moderately and robustly associated (r = ${N.r})**, mainly through excessive searching and distress, compatible with a **cycle**.`,
  "• **No reliable independent effect of AI** beyond health anxiety.",
  `• Searching shapes the consultation: **${N.dr}** delay care when reassured, **${N.never}** never disclose searches.`,
].join("\n"), { x: 0.8, y: 1.25, w: 8.4, h: 3.7, fontSize: 16, paraSpaceAfter: 10 });

// ================================================================ 33 Closing number
s = newSlide(1, "[ALL] Leave this slide up during questions. Each student answers questions on their own part; Student 2 takes statistics questions.");
s.addText(`r = ${N.r}`, { x: 0.5, y: 1.0, w: 9.0, h: 1.6, align: "center", fontFace: HEAD, fontSize: 80, bold: true, color: ORANGE, margin: 0, valign: "middle" });
s.addText("Health anxiety and cyberchondria travel together.", { x: 0.5, y: 2.6, w: 9.0, h: 0.5, align: "center", fontFace: BODY, fontSize: 18, color: INK, margin: 0 });
s.addText("Thank you — questions are welcome", { x: 0.5, y: 3.6, w: 9.0, h: 0.6, align: "center", fontFace: HEAD, fontSize: 26, bold: true, color: GREEN, margin: 0 });

// pptxgenjs writes one <a:pPr> per run; a paragraph may only have one (the first), so drop the rest
async function fixParagraphProps(file) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const PPR = /<a:pPr\b[^>]*?\/>|<a:pPr\b[^>]*>[\s\S]*?<\/a:pPr>/g;
  for (const name of Object.keys(zip.files).filter((n) => /^ppt\/slides\/slide\d+\.xml$/.test(n))) {
    const xml = await zip.file(name).async("string");
    const fixed = xml.replace(/<a:p>([\s\S]*?)<\/a:p>/g, (m, inner) => {
      let seen = false;
      return "<a:p>" + inner.replace(PPR, (pp) => (seen ? "" : ((seen = true), pp))) + "</a:p>";
    });
    zip.file(name, fixed);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

(async () => {
  await pres.writeFile({ fileName: OUTFILE });
  await fixParagraphProps(OUTFILE);
  console.log("wrote", OUTFILE);
})();
