"""Phone version of the Student 2 master file: one self-contained HTML page (figures embedded) with
collapsible sections, progress ticks and a flashcard mode built from the questions, self-test and drills.
Usage: python3 16_phone_guide.py <Student2_Master_File.html> <out.html>"""
import sys, re, io, json, base64, html as H
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
t = open(SRC).read()
body = re.search(r'<body>(.*)</body>', t, re.S).group(1)

# ---------------------------------------------------------------- figures -> small embedded JPEGs
cache = {}
def embed(m):
    path = m.group(1).replace('file://', '')
    if path not in cache:
        im = Image.open(path).convert('RGBA'); bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[3])
        w = 1400 if im.width / im.height > 2.2 else 1100
        if bg.width > w: bg = bg.resize((w, round(bg.height * w / bg.width)), Image.LANCZOS)
        b = io.BytesIO(); bg.save(b, 'JPEG', quality=72, optimize=True)
        cache[path] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    return f'src="{cache[path]}" loading="lazy" alt="Figure from the thesis (tap to enlarge)"'
body = re.sub(r'src="(file://[^"]+)"', embed, body)
body = re.sub(r'<img class="fig"', '<img class="fig" tabindex="0"', body)
body = body.replace(' class="page"', '')
body = re.sub(r'<table', '<div class="tw"><table', body); body = body.replace('</table>', '</table></div>')
body = re.sub(r' style="[^"]*"', '', body)

# ---------------------------------------------------------------- flashcards
def clean(x): return H.unescape(re.sub(r'<[^>]+>', '', x)).strip()
cards = []
for q, a in re.findall(r'<p class="q">(.*?)</p>\s*<p class="a">(.*?)</p>', body, re.S):
    cards.append(dict(d='Questions', q=clean(q).removeprefix('Q:').strip(), a=clean(a)))
def table_after(marker, qcol, acol, deck):
    i = body.find(marker)
    if i < 0: return
    tb = body[i:body.find('</table>', i)]
    for row in re.findall(r'<tr>(.*?)</tr>', tb, re.S)[1:]:
        c = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        if len(c) > max(qcol, acol): cards.append(dict(d=deck, q=clean(c[qcol]), a=clean(c[acol])))
table_after('<h3>Self-test</h3>', 1, 2, 'Self-test')
table_after('Drills: explain it simply', 0, 1, 'Explain it')
table_after('<h2>13 · Cheat sheet</h2>', 0, 1, 'Numbers')

# ---------------------------------------------------------------- sections
parts = re.split(r'(<h2[^>]*>.*?</h2>)', body)
intro, secs = parts[0], []
for i in range(1, len(parts), 2):
    title = clean(parts[i]); num, _, name = title.partition(' · ')
    secs.append((num.strip(), name.strip(), parts[i + 1]))
intro = re.sub(r'<h1>.*?</h1>', '', intro, flags=re.S)
intro = re.sub(r'^\s*<p>Everything you need.*?</p>', '', intro, flags=re.S)
intro = re.sub(r'<h3>Contents</h3><ol class="toc">.*?</ol>', '', intro, flags=re.S)
sec_html = ''.join(f'''<details class="sec" id="s{n}" data-id="{n}"><summary><span class="sn">{n}</span><span class="st">{H.escape(nm)}</span><span class="tick" aria-hidden="true"></span></summary>
<div class="sb">{b}<button class="done" type="button" data-id="{n}">Mark section {n} as studied</button></div></details>''' for n, nm, b in secs)

page = r'''<title>Student 2 Gym Guide</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Archivo:wght@600;800&display=swap">
<style>
/* Layout: one narrow reading column; sticky two-tab bar (Read / Cards); sections fold so the phone shows one topic at a time. */
:root {
  --bg: #f3f6f4; --surface: #ffffff; --ink: #14231d; --muted: #55665f; --line: #d5ded9;
  --accent: #0f6b52; --accent-ink: #ffffff; --warm: #b5541c; --warm-bg: #fbeee4;
  --say-bg: #e6f2ed; --trap-bg: #f8e9ec; --trap: #8a2341; --tip-bg: #eef1fa; --tip: #2f4a8a;
  --f-body: "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif; --f-head: "Archivo", "Arial Narrow", system-ui, sans-serif;
  --fs: 1.07rem;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0e1513; --surface: #16201d; --ink: #e5eeea; --muted: #9db0a8; --line: #2a3833;
  --accent: #39b98f; --accent-ink: #06140f; --warm: #f0995f; --warm-bg: #2b1d14;
  --say-bg: #13291f; --trap-bg: #2c161d; --trap: #f08aa6; --tip-bg: #161d30; --tip: #9fb4f0; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0e1513; --surface: #16201d; --ink: #e5eeea; --muted: #9db0a8; --line: #2a3833;
  --accent: #39b98f; --accent-ink: #06140f; --warm: #f0995f; --warm-bg: #2b1d14;
  --say-bg: #13291f; --trap-bg: #2c161d; --trap: #f08aa6; --tip-bg: #161d30; --tip: #9fb4f0; color-scheme: dark }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: var(--fs)/1.6 var(--f-body); }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--surface); }
.wrap { max-width: 44rem; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 0 4rem; }
header.bar { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--surface); border-bottom: 1px solid var(--line); }
.bar .in { max-width: 44rem; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: .55rem; display: flex; align-items: center; gap: .75rem; }
.brand { font: 800 1.02rem/1.1 var(--f-head); letter-spacing: .01em; flex: 1; min-width: 0; }
.brand small { display: block; font: 400 .8rem var(--f-body); color: var(--muted); }
.tabs { display: flex; background: var(--bg); border-radius: 999px; padding: 3px; gap: 2px; }
.tabs a { text-decoration: none; color: var(--muted); font: 600 .95rem var(--f-head); padding: .45rem .95rem; border-radius: 999px; min-height: 2.5rem; display: flex; align-items: center; }
.tabs a[aria-current="page"] { background: var(--accent); color: var(--accent-ink); }
.prog { height: 4px; background: var(--line); } .prog i { display: block; height: 100%; width: 0; background: var(--accent); transition: width .3s; }
h1 { font: 800 1.75rem/1.15 var(--f-head); margin: 1.2rem 0 .3rem; text-wrap: balance; }
.lede { color: var(--muted); margin: 0 0 1rem; }
h2, h3, h4 { font-family: var(--f-head); text-wrap: balance; line-height: 1.25; }
h3 { font-size: 1.12rem; margin: 1.4rem 0 .4rem; color: var(--warm); }
h4 { font-size: 1rem; margin: 1rem 0 .3rem; }
p { margin: .35rem 0 .7rem; } ul, ol { padding-left: 1.25rem; margin: .3rem 0 .8rem; } li { margin: .25rem 0; }
.quick { display: grid; grid-template-columns: 1fr 1fr; gap: .6rem; margin: 1rem 0 1.3rem; }
.quick button { font: 700 1rem var(--f-head); padding: .9rem .8rem; border-radius: 12px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); text-align: left; min-height: 3.4rem; cursor: pointer; }
.quick button span { display: block; font: 400 .82rem var(--f-body); color: var(--muted); }
details.sec { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; margin: .6rem 0; }
details.sec > summary { list-style: none; cursor: pointer; display: flex; gap: .75rem; align-items: center; padding: .95rem 1rem; min-height: 3.5rem; }
details.sec > summary::-webkit-details-marker { display: none; }
.sn { font: 800 .95rem var(--f-head); color: var(--accent); min-width: 1.6rem; font-variant-numeric: tabular-nums; }
.st { flex: 1; font: 600 1.02rem/1.3 var(--f-head); min-width: 0; }
.tick { width: 1.5rem; height: 1.5rem; border-radius: 50%; border: 2px solid var(--line); flex: none; }
details.sec.is-done .tick { background: var(--accent); border-color: var(--accent); box-shadow: inset 0 0 0 3px var(--surface); }
details.sec[open] > summary { border-bottom: 1px solid var(--line); position: sticky; top: calc(env(safe-area-inset-top, 0px) + 3.6rem); background: var(--surface); border-radius: 14px 14px 0 0; z-index: 2; }
.sb { padding: .3rem 1rem 1.1rem; min-width: 0; }
.done { width: 100%; margin-top: 1.2rem; font: 700 1rem var(--f-head); padding: .9rem; border-radius: 12px; border: 2px solid var(--accent); background: transparent; color: var(--accent); cursor: pointer; min-height: 3.2rem; }
details.sec.is-done .done { background: var(--accent); color: var(--accent-ink); }
.say, .why, .trap, .tip, .box { border-radius: 10px; padding: .65rem .85rem; margin: .7rem 0; }
.say { background: var(--say-bg); } .say::before { content: "Say it: "; font-weight: 700; color: var(--accent); }
.why { background: var(--warm-bg); } .why::before { content: "Why: "; font-weight: 700; color: var(--warm); }
.trap { background: var(--trap-bg); } .trap::before { content: "Trap: "; font-weight: 700; color: var(--trap); }
.tip { background: var(--tip-bg); }
.box { background: var(--bg); border: 1px solid var(--line); } .box.red { background: var(--trap-bg); border-color: transparent; } .box.warn { background: var(--warm-bg); border-color: transparent; }
.lesson, .card, .slide { border: 1px solid var(--line); border-radius: 12px; padding: .7rem .9rem; margin: .8rem 0; }
.lesson .t, .card .hd { font: 700 1.02rem var(--f-head); color: var(--accent); display: block; margin-bottom: .3rem; }
.ex { background: var(--bg); border-radius: 8px; padding: .55rem .75rem; margin: .5rem 0; font-variant-numeric: tabular-nums; font-size: .97rem; }
.num { color: var(--warm); font-weight: 700; } .small { font-size: .88rem; color: var(--muted); }
.q { font-weight: 700; margin: 1rem 0 .2rem; } .a { margin: 0 0 .8rem; padding-left: .8rem; border-left: 3px solid var(--line); }
.tw { overflow-x: auto; margin: .6rem 0 1rem; -webkit-overflow-scrolling: touch; }
table { border-collapse: collapse; width: 100%; font-size: .93rem; min-width: 18rem; }
th, td { text-align: left; vertical-align: top; padding: .45rem .5rem; border-bottom: 1px solid var(--line); }
th { font: 700 .82rem var(--f-head); text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
img.fig { display: block; width: 100%; height: auto; border-radius: 8px; background: #fff; margin: .6rem 0 .2rem; cursor: zoom-in; }
.zoom { position: fixed; inset: 0; z-index: 20; background: rgba(0,0,0,.92); overflow: auto; padding: calc(env(safe-area-inset-top, 0px) + 3.5rem) max(12px, env(safe-area-inset-right, 0px)) 2rem max(12px, env(safe-area-inset-left, 0px)); }
.zoom img { width: 230%; max-width: none; background: #fff; border-radius: 6px; }
.zoom button { position: fixed; top: calc(env(safe-area-inset-top, 0px) + .6rem); right: max(12px, env(safe-area-inset-right, 0px)); font: 700 1rem var(--f-head); padding: .6rem 1rem; border-radius: 999px; border: 0; background: #fff; color: #111; min-height: 2.75rem; }
.zoom p { color: #ddd; font-size: .85rem; margin: .6rem 0 0; }
/* cards */
.decks { display: flex; flex-wrap: wrap; gap: .45rem; margin: 1rem 0; }
.decks button { font: 600 .95rem var(--f-head); padding: .55rem .95rem; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); min-height: 2.75rem; cursor: pointer; }
.decks button[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.stage { perspective: 1200px; }
.fc { width: 100%; min-height: 19rem; border: 0; padding: 0; background: none; cursor: pointer; display: block; color: inherit; font: inherit; text-align: left; }
.fc .face { background: var(--surface); border: 1px solid var(--line); border-radius: 18px; padding: 1.3rem 1.2rem; min-height: 19rem; display: flex; flex-direction: column; gap: .8rem; }
.fc .lab { font: 700 .78rem var(--f-head); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); display: flex; justify-content: space-between; gap: .5rem; }
.fc .qq { font: 700 1.35rem/1.35 var(--f-head); text-wrap: balance; }
.fc .aa { font-size: 1.15rem; line-height: 1.55; border-top: 1px dashed var(--line); padding-top: .8rem; }
.fc .hint { margin-top: auto; color: var(--muted); font-size: .9rem; }
.ctrl { display: grid; grid-template-columns: 1fr 1fr; gap: .6rem; margin-top: .8rem; }
.ctrl button { font: 700 1.05rem var(--f-head); padding: 1rem; border-radius: 14px; border: 0; min-height: 3.6rem; cursor: pointer; }
.again { background: var(--trap-bg); color: var(--trap); } .got { background: var(--accent); color: var(--accent-ink); }
.sub { display: flex; justify-content: space-between; align-items: center; gap: .6rem; margin-top: .8rem; color: var(--muted); font-size: .92rem; flex-wrap: wrap; }
.sub button { font: 600 .92rem var(--f-head); background: none; border: 1px solid var(--line); color: var(--ink); border-radius: 999px; padding: .5rem .9rem; min-height: 2.6rem; cursor: pointer; }
.empty { text-align: center; padding: 2rem 1rem; background: var(--surface); border-radius: 18px; border: 1px solid var(--line); }
:focus-visible { outline: 3px solid var(--warm); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
</style>

<header class="bar"><div class="in">
  <div class="brand">Student 2 · Results<small id="sub">Cyberchondria study, Baghdad</small></div>
  <nav class="tabs" aria-label="Mode"><a href="#read" id="t-read">Read</a><a href="#cards" id="t-cards">Cards</a></nav>
</div><div class="prog" aria-hidden="true"><i id="pbar"></i></div></header>

<main class="wrap">
<section id="v-read">
  <h1>Your Results part, pocket size</h1>
  <p class="lede">Health anxiety, AI chatbots and cyberchondria in 300 adults in Baghdad. Open one section per set. Tap a figure to zoom. Tick a section when you can explain it out loud.</p>
  <div class="quick">
    <button type="button" data-open="13">Cheat sheet<span>All key numbers, one screen</span></button>
    <button type="button" data-go="cards">Flashcards<span id="qcount">Test yourself between sets</span></button>
    <button type="button" data-open="8">My slides<span>What to point at and say</span></button>
    <button type="button" data-open="9">Hard questions<span>Model answers</span></button>
  </div>
  <div class="intro">__INTRO__</div>
  __SECS__
  <p class="small">Built from the Student 2 master file (short thesis, SPSS-level analysis). Your ticks are saved on this device only.</p>
</section>

<section id="v-cards" hidden>
  <h1>Flashcards</h1>
  <p class="lede">Read the question, answer out loud, tap to check. “Again” puts the card back in the pile.</p>
  <div class="decks" id="decks" role="group" aria-label="Card deck"></div>
  <div id="cardbox"></div>
</section>
</main>
<div class="zoom" id="zoom" hidden><button type="button" id="zclose">Close</button><img id="zimg" alt="Enlarged figure"><p>Scroll sideways to see the whole figure. Turn the phone for a bigger view.</p></div>

<script>
const CARDS = __CARDS__;
const KEY = 'stu2-gym-v1';
let S = { done: [], known: [] };
try { S = Object.assign(S, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const secs = $$('details.sec');

function paintProgress() {
  secs.forEach(d => d.classList.toggle('is-done', S.done.includes(d.dataset.id)));
  $$('.done').forEach(b => b.textContent = S.done.includes(b.dataset.id) ? `Section ${b.dataset.id} studied ✓ (tap to undo)` : `Mark section ${b.dataset.id} as studied`);
  const r = mode === 'cards' ? S.known.length / CARDS.length : S.done.length / secs.length;
  $('#pbar').style.width = (r * 100).toFixed(1) + '%';
  $('#sub').textContent = mode === 'cards' ? `${S.known.length} of ${CARDS.length} cards known` : `${S.done.length} of ${secs.length} sections studied`;
}
$$('.done').forEach(b => b.addEventListener('click', () => {
  const id = b.dataset.id; S.done = S.done.includes(id) ? S.done.filter(x => x !== id) : [...S.done, id]; save(); paintProgress();
  if (S.done.includes(id)) { const d = b.closest('details'); d.open = false; d.scrollIntoView({ block: 'start' }); }
}));
secs.forEach(d => d.addEventListener('toggle', () => { if (d.open) { secs.forEach(o => { if (o !== d) o.open = false; }); d.scrollIntoView({ block: 'start' }); } }));
$$('[data-open]').forEach(b => b.addEventListener('click', () => { const d = $('#s' + b.dataset.open); d.open = true; }));
$$('[data-go]').forEach(b => b.addEventListener('click', () => { location.hash = b.dataset.go; }));
$('#qcount').textContent = `${CARDS.length} cards from your Q&A and self-test`;

// zoom
$$('img.fig').forEach(im => { const open = () => { $('#zimg').src = im.src; $('#zoom').hidden = false; }; im.addEventListener('click', open); im.addEventListener('keydown', e => { if (e.key === 'Enter') open(); }); });
$('#zclose').addEventListener('click', () => { $('#zoom').hidden = true; });

// cards
const DECKS = ['All', ...new Set(CARDS.map(c => c.d))];
let deck = 'All', pile = [], flipped = false;
function build() {
  pile = CARDS.map((c, i) => i).filter(i => (deck === 'All' || CARDS[i].d === deck) && !S.known.includes(i));
  for (let i = pile.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [pile[i], pile[j]] = [pile[j], pile[i]]; }
  flipped = false; draw();
}
function draw() {
  const total = CARDS.filter(c => deck === 'All' || c.d === deck).length, box = $('#cardbox');
  $('#decks').innerHTML = DECKS.map(d => `<button type="button" aria-pressed="${d === deck}" data-d="${d}">${d} · ${d === 'All' ? CARDS.length : CARDS.filter(c => c.d === d).length}</button>`).join('');
  $$('#decks button').forEach(b => b.addEventListener('click', () => { deck = b.dataset.d; build(); }));
  if (!pile.length) {
    box.innerHTML = `<div class="empty"><h3>All ${total} cards in this deck known</h3><p>Rest, then go again.</p><div class="sub" style="justify-content:center"><button type="button" id="reset">Reset this deck</button></div></div>`;
    $('#reset').addEventListener('click', () => { const ids = CARDS.map((c, i) => i).filter(i => deck === 'All' || CARDS[i].d === deck); S.known = S.known.filter(i => !ids.includes(i)); save(); paintProgress(); build(); });
    return;
  }
  const c = CARDS[pile[0]], esc = s => s.replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));
  box.innerHTML = `<div class="stage"><button type="button" class="fc" id="fc" aria-label="Flashcard, tap to show the answer"><div class="face">
    <div class="lab"><span>${esc(c.d)}</span><span>${total - pile.length + 1} / ${total}</span></div>
    <div class="qq">${esc(c.q)}</div>
    ${flipped ? `<div class="aa">${esc(c.a)}</div>` : `<div class="hint">Say your answer out loud, then tap the card.</div>`}
  </div></button></div>
  <div class="ctrl"><button type="button" class="again" id="again">Again</button><button type="button" class="got" id="got">${flipped ? 'Got it' : 'Show answer'}</button></div>
  <div class="sub"><span>${pile.length} left in this pile</span><button type="button" id="shuf">Shuffle</button></div>`;
  $('#fc').addEventListener('click', () => { flipped = !flipped; draw(); });
  $('#again').addEventListener('click', () => { pile.push(pile.shift()); flipped = false; draw(); });
  $('#got').addEventListener('click', () => { if (!flipped) { flipped = true; draw(); return; } S.known.push(pile.shift()); save(); paintProgress(); flipped = false; draw(); });
  $('#shuf').addEventListener('click', build);
}
document.addEventListener('keydown', e => {
  if (mode !== 'cards' || !pile.length) return;
  if (e.key === ' ' || e.key === 'Enter') { if (document.activeElement && document.activeElement.id !== 'fc' && document.activeElement.tagName === 'BUTTON') return; e.preventDefault(); flipped = !flipped; draw(); }
  if (e.key === 'ArrowRight' && flipped) $('#got').click();
  if (e.key === 'ArrowLeft') $('#again').click();
});

// screen awake while studying cards (optional)
let lock = null;
async function wake(on) { try { if (on && 'wakeLock' in navigator && !lock) { lock = await navigator.wakeLock.request('screen'); lock.addEventListener('release', () => { lock = null; }); } else if (!on && lock) { await lock.release(); } } catch (e) {} }
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && mode === 'cards') wake(true); });

// routing
let mode = 'read';
function route() {
  mode = location.hash === '#cards' ? 'cards' : 'read';
  $('#v-read').hidden = mode !== 'read'; $('#v-cards').hidden = mode !== 'cards';
  $('#t-read').setAttribute('aria-current', mode === 'read' ? 'page' : 'false'); $('#t-cards').setAttribute('aria-current', mode === 'cards' ? 'page' : 'false');
  if (mode === 'cards') { build(); wake(true); } else wake(false);
  paintProgress(); window.scrollTo(0, 0);
}
window.addEventListener('hashchange', route); route();
</script>
'''
page = page.replace('__INTRO__', intro).replace('__SECS__', sec_html).replace('__CARDS__', json.dumps(cards, ensure_ascii=False).replace('</', '<\\/'))
open(OUT, 'w').write(page)
print('wrote', OUT, f'{len(page)/1e6:.2f} MB', len(cards), 'cards', len(secs), 'sections')
