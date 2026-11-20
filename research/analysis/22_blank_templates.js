// Blank presentation templates in the four designs of 21_defence_slides.js. Usage: node 22_blank_templates.js <out dir>
const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/25741026-d946-4dbc-8c24-ac9a6070fdfc_a0e8a8de-929a-428a-b59c-ea7dac5ee207/pptx/scripts/apply_theme.js');
const DIR = process.argv[2];
const STYLES = { Navy: { main: '1F3B4D', acc: 'B4541C', pale: 'EEF2F6', page: 'FFFFFF', head: 'Cambria' }, Green: { main: '1E4D3A', acc: 'A8791A', pale: 'EDF3EE', page: 'FFFFFF', head: 'Cambria' },
  Burgundy: { main: '6D1F2F', acc: '2F4858', pale: 'F4EEEF', page: 'FFFFFF', head: 'Bookman Old Style' }, Paper: { main: '4A3728', acc: '2E6F6B', pale: 'EAE1D0', page: 'F7F2E8', head: 'Century Schoolbook' } };
const build = async (name, ST) => {
  const THEME = { name: 'Academic ' + name, headFontFace: ST.head, bodyFontFace: 'Calibri', colors: { dk1: '1D2230', lt1: 'FFFFFF', dk2: ST.main, lt2: ST.pale, accent1: ST.main, accent2: ST.acc,
    accent3: '2E7D6B', accent4: '8A6D1F', accent5: '6A4C9C', accent6: '9D1C4A', hlink: '1F6FA0', folHlink: '6A4C9C' } };
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace }; pres.title = 'Academic template ' + name;
  const C = pres.SchemeColor, MAIN = C.text2, ACC = C.accent2, INK = C.text1, WHITE = C.background1, PALE = C.background2;
  const R = (x, y, w, h, color) => ({ rect: { x, y, w, h, fill: { color } } });
  const FOOT = (c, y = 7.08) => ({ text: { text: 'College of Medicine · University of Baghdad', options: { x: 0.5, y, w: 10.5, h: 0.42, fontSize: 11, color: c, valign: 'middle', margin: 0 } } });
  const TITLE = c => ({ placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.1, w: 12.3, h: 0.85, fontSize: 30, bold: true, color: c, valign: 'middle', margin: 0 }, text: 'Click to add title' } });
  const BODY = (x, w, n = 'body') => ({ placeholder: { options: { name: n, type: 'body', x, y: 1.45, w, h: 5.4, fontSize: 20, color: INK, valign: 'top', bullet: true, paraSpaceAfter: 8 }, text: 'Click to add text' } });
  const FRAME = { navy: [R(0, 0, 13.33, 1.05, MAIN), R(0, 1.05, 13.33, 0.07, ACC), R(0, 7.08, 13.33, 0.42, PALE), FOOT(MAIN)],
    green: [R(0, 0, 13.33, 0.14, MAIN), R(0.5, 1.02, 12.33, 0.07, ACC), R(0, 7.08, 13.33, 0.42, MAIN), FOOT(WHITE)],
    burgundy: [R(0, 0, 13.33, 1.05, MAIN), R(0, 0, 0.32, 1.05, ACC), R(0, 1.05, 13.33, 0.07, PALE), R(0, 7.08, 13.33, 0.42, PALE), R(0, 7.08, 0.32, 0.42, ACC), FOOT(MAIN)],
    paper: [{ rect: { x: 0.15, y: 0.12, w: 13.03, h: 7.26, fill: { type: 'none' }, line: { color: ST.main, width: 1.5 } } }, R(0.5, 1.0, 12.33, 0.04, MAIN), R(0.5, 1.07, 12.33, 0.02, MAIN), FOOT(MAIN, 6.98)] }[name.toLowerCase()];
  const tc = (name === 'Green' || name === 'Paper') ? MAIN : WHITE, nc = name === 'Green' ? WHITE : MAIN;
  const num = { x: 12.1, y: name === 'Paper' ? 6.98 : 7.08, w: 0.8, h: 0.42, fontSize: 12, bold: true, color: nc, align: 'right' };
  pres.defineSlideMaster({ title: 'Title Slide', background: { color: MAIN }, objects: [R(0, 7.2, 13.33, 0.3, ACC),
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 1.6, w: 12.1, h: 2.2, fontSize: 40, bold: true, color: WHITE, valign: 'bottom', align: 'left', margin: 0 }, text: 'Click to add the title' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 4.0, w: 12.1, h: 2.6, fontSize: 20, color: WHITE, valign: 'top', margin: 0 }, text: 'Names, supervisor, college, year' } }] });
  pres.defineSlideMaster({ title: 'Title and Content', background: { color: ST.page }, objects: FRAME.concat([TITLE(tc), BODY(0.5, 12.33)]), slideNumber: Object.assign({}, num) });
  pres.defineSlideMaster({ title: 'Text and Picture', background: { color: ST.page }, objects: FRAME.concat([TITLE(tc), BODY(0.5, 7.2)]), slideNumber: Object.assign({}, num) });
  pres.defineSlideMaster({ title: 'Title Only', background: { color: ST.page }, objects: FRAME.concat([TITLE(tc)]), slideNumber: Object.assign({}, num) });
  pres.defineSlideMaster({ title: 'Section Header', background: { color: MAIN }, objects: [R(0.6, 4.05, 3.0, 0.08, ACC),
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 2.4, w: 12.1, h: 1.5, fontSize: 44, bold: true, color: WHITE, valign: 'bottom', align: 'left', margin: 0 }, text: 'Section title' } }] });
  let s = pres.addSlide({ masterName: 'Title Slide' }); s.addText('Presentation Title', { placeholder: 'title', align: 'left', fontSize: 40 }); s.addText('Student names · Supervisor · College of Medicine, University of Baghdad · 2026', { placeholder: 'body' });
  s = pres.addSlide({ masterName: 'Section Header' }); s.addText('Section Title', { placeholder: 'title', align: 'left', fontSize: 44 });
  s = pres.addSlide({ masterName: 'Title and Content' }); s.addText('Title and Content', { placeholder: 'title' }); s.addText('Write your points here', { placeholder: 'body' });
  s = pres.addSlide({ masterName: 'Text and Picture' }); s.addText('Text and Picture', { placeholder: 'title' }); s.addText('Text on the left; insert a picture on the right', { placeholder: 'body' });
  s.addShape(pres.ShapeType.rect, { x: 8.1, y: 1.45, w: 4.73, h: 5.3, fill: { color: PALE }, line: { color: ST.main, width: 1, dashType: 'dash' } });
  s.addText('Insert picture here', { x: 8.1, y: 1.45, w: 4.73, h: 5.3, fontSize: 16, italic: true, color: MAIN, align: 'center', valign: 'middle', isTextBox: true });
  s = pres.addSlide({ masterName: 'Title Only' }); s.addText('Title Only (for tables, charts and figures)', { placeholder: 'title' });
  s.addTable([['Heading', 'Heading', 'Heading'].map(t => ({ text: t, options: { bold: true, color: WHITE, fill: { color: MAIN } } })), ['Text', 'Text', 'Text'], ['Text', 'Text', 'Text'].map(t => ({ text: t, options: { fill: { color: ST.pale } } }))],
    { x: 0.5, y: 1.5, w: 7.5, colW: [2.5, 2.5, 2.5], fontSize: 16, color: INK, border: { type: 'solid', pt: 0.75, color: 'B8C4CE' }, margin: [3, 6, 3, 6] });
  s.addText('Key message box', { x: 0.5, y: 5.9, w: 12.33, h: 0.75, fontSize: 18, bold: true, color: WHITE, fill: { color: MAIN }, align: 'center', valign: 'middle', isTextBox: true });
  s.addText('Second colour box', { x: 8.4, y: 1.5, w: 4.43, h: 1.6, fontSize: 18, bold: true, color: WHITE, fill: { color: ACC }, align: 'center', valign: 'middle', isTextBox: true });
  const f = `${DIR}/Template_${name}.pptx`; await pres.writeFile({ fileName: f }); await applyTheme(f, THEME);
  const JSZip = require('jszip'), fs = require('fs'); const z = await JSZip.loadAsync(fs.readFileSync(f));
  Object.keys(z.files).filter(n => z.files[n].dir).forEach(n => delete z.files[n]); fs.writeFileSync(f, await z.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' })); console.log('wrote', f); };
(async () => { for (const [n, st] of Object.entries(STYLES)) await build(n, st); })();
