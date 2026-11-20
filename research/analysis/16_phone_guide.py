"""Phone version of the Student 2 master file: one self-contained HTML page (figures embedded) with
one-screen pages with a Next button, a section menu and a flashcard mode built from the questions, self-test and drills.
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
# ---------------------------------------------------------------- split everything into phone-sized pages
from bs4 import BeautifulSoup, NavigableString
BUDGET = 650            # characters of text per page (about one phone screen at 17px)
def tlen(node): return len(node.get_text(' ', strip=True)) if hasattr(node, 'get_text') else len(str(node).strip())
def pieces(node):
    """Break long lists and tables into smaller pieces; keep everything else whole."""
    if getattr(node, 'name', None) in ('ul', 'ol') and tlen(node) > BUDGET:
        lis = node.find_all('li', recursive=False); out, cur = [], []
        for li in lis:
            cur.append(str(li))
            if sum(len(BeautifulSoup(x, 'html.parser').get_text()) for x in cur) > BUDGET * .8:
                out.append(f'<{node.name}>' + ''.join(cur) + f'</{node.name}>'); cur = []
        if cur: out.append(f'<{node.name}>' + ''.join(cur) + f'</{node.name}>')
        return [(x, min(len(BeautifulSoup(x, 'html.parser').get_text()), BUDGET)) for x in out]
    if getattr(node, 'name', None) == 'div' and 'tw' in (node.get('class') or []) and tlen(node) > BUDGET:
        rows = node.find_all('tr'); head = str(rows[0]) if rows and rows[0].find('th') else ''
        body_rows = rows[1:] if head else rows; out, cur, n = [], [], 0
        for r in body_rows:
            cur.append(str(r)); n += tlen(r)
            if n > BUDGET * .85: out.append((f'<div class="tw"><table>{head}{"".join(cur)}</table></div>', n)); cur, n = [], 0
        if cur: out.append((f'<div class="tw"><table>{head}{"".join(cur)}</table></div>', n))
        return out
    if getattr(node, 'name', None) == 'img': return [(str(node), BUDGET)]
    return [(str(node), tlen(node) + (BUDGET if getattr(node, 'find', None) and node.find('img') else 0))]
PAGES = []      # (section number, section name, html)
def paginate(num, name, html_):
    soup = BeautifulSoup(html_, 'html.parser'); cur, n = [], 0
    def flush():
        nonlocal cur, n
        if cur and any(BeautifulSoup(x, 'html.parser').get_text(strip=True) or '<img' in x for x in cur): PAGES.append((num, name, ''.join(cur)))
        cur, n = [], 0
    for node in soup.contents:
        if isinstance(node, NavigableString) and not node.strip(): continue
        heading = getattr(node, 'name', None) in ('h3', 'h4')
        if heading and n > BUDGET * .35: flush()
        for piece, size in pieces(node):
            if n and n + size > BUDGET and not (cur and cur[-1].startswith(('<h3', '<h4'))): flush()
            cur.append(piece); n += size
    flush()
paginate('0', 'Start here', intro)
for n_, nm, b in secs: paginate(n_, nm, b)
SECS = [{'n': n_, 'name': nm, 'first': next(k for k, p in enumerate(PAGES) if p[0] == n_)} for n_, nm, b in secs]
pages_html = ''.join(f'<article class="pg" data-sec="{n_}" hidden><div class="eyebrow">{"<span>Start here</span>" if n_ == "0" else f"<span>Section {n_}</span> {H.escape(nm)}"}</div>{h}</article>' for n_, nm, h in PAGES)
page = r'''<title>Student 2 Gym Guide</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Archivo:wght@600;800&display=swap">
<style>
/* Layout: one narrow reading column; sticky top bar (menu, Read / Cards); the Read view shows one screen-sized page at a time with a thumb-height Next bar. */
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
[hidden] { display: none !important; }
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
.pg { padding-block: 1rem 7.5rem; min-height: 60vh; }
.eyebrow { font: 700 .78rem var(--f-head); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin-bottom: .6rem; }
.eyebrow span { color: var(--accent); margin-right: .35rem; }
.pg > h3:first-of-type, .pg > .eyebrow + h3, .pg > .eyebrow + h4 { margin-top: .3rem; }
.pager { position: fixed; left: 0; right: 0; bottom: 0; z-index: 6; display: flex; gap: .6rem; background: var(--surface); border-top: 1px solid var(--line);
  padding: .6rem max(16px, env(safe-area-inset-right, 0px)) calc(.6rem + env(safe-area-inset-bottom, 0px)) max(16px, env(safe-area-inset-left, 0px)); }
.pager button { border: 0; border-radius: 16px; font: 800 1.25rem var(--f-head); min-height: 4rem; cursor: pointer; }
#back { width: 4.2rem; background: var(--bg); color: var(--ink); font-size: 1.8rem; }
#next { flex: 1; background: var(--accent); color: var(--accent-ink); }
#next small { display: block; font: 400 .8rem var(--f-body); opacity: .85; }
#back:disabled { opacity: .35; }
.menu { border: 1px solid var(--line); background: var(--surface); color: var(--ink); border-radius: 12px; width: 2.75rem; height: 2.75rem; font-size: 1.2rem; cursor: pointer; flex: none; }
.sheet { position: fixed; inset: 0; z-index: 15; background: rgba(0,0,0,.45); display: flex; align-items: flex-end; }
.sheet-in { background: var(--surface); width: 100%; max-height: 85%; overflow: auto; border-radius: 18px 18px 0 0;
  padding: 1rem max(16px, env(safe-area-inset-right, 0px)) calc(1rem + env(safe-area-inset-bottom, 0px)) max(16px, env(safe-area-inset-left, 0px)); }
.sheet-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }
.sheet-hd button { font: 600 .95rem var(--f-head); border: 1px solid var(--line); background: none; color: var(--ink); border-radius: 999px; padding: .5rem 1rem; min-height: 2.6rem; }
#toc { list-style: none; padding: 0; margin: 0; }
#toc button { width: 100%; text-align: left; display: flex; gap: .7rem; align-items: center; padding: .85rem .4rem; border: 0; border-bottom: 1px solid var(--line); background: none; color: var(--ink); font: 600 1rem var(--f-head); min-height: 3.2rem; cursor: pointer; }
#toc .sn { min-width: 1.6rem; } #toc .tk { margin-left: auto; color: var(--accent); }
#toc .here { background: var(--say-bg); }
:focus-visible { outline: 3px solid var(--warm); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
</style>

<header class="bar"><div class="in">
  <div class="brand">Student 2 · Results<small id="sub">Cyberchondria study, Baghdad</small></div>
  <button type="button" class="menu" id="menu" aria-label="Sections">☰</button><nav class="tabs" aria-label="Mode"><a href="#read" id="t-read">Read</a><a href="#cards" id="t-cards">Cards</a></nav>
</div><div class="prog" aria-hidden="true"><i id="pbar"></i></div></header>

<main class="wrap">
<section id="v-read">
  <div id="pages">__PAGES__</div>
</section>

<section id="v-cards" hidden>
  <h1>Flashcards</h1>
  <p class="lede">Read the question, answer out loud, tap to check. “Again” puts the card back in the pile.</p>
  <div class="decks" id="decks" role="group" aria-label="Card deck"></div>
  <div id="cardbox"></div>
</section>
</main>
<nav class="pager" id="pager" aria-label="Page controls">
  <button type="button" id="back" aria-label="Previous page">‹</button>
  <button type="button" id="next">Next</button>
</nav>
<div class="sheet" id="sheet" hidden><div class="sheet-in"><div class="sheet-hd"><b>Jump to a section</b><button type="button" id="sclose">Close</button></div><ol id="toc"></ol></div></div>
<div class="zoom" id="zoom" hidden><button type="button" id="zclose">Close</button><img id="zimg" alt="Enlarged figure"><p>Scroll sideways to see the whole figure. Turn the phone for a bigger view.</p></div>

<script>
const CARDS = __CARDS__;
const KEY = 'stu2-gym-v1';
let S = { done: [], known: [] };
try { S = Object.assign(S, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const SECS = __SECJSON__;
const pages = $$('.pg');
let pi = 0; try { pi = Math.min(pages.length - 1, Math.max(0, +(localStorage.getItem(KEY + '-page') || 0))); } catch (e) {}
function paintProgress() {
  const r = mode === 'cards' ? S.known.length / CARDS.length : (pi + 1) / pages.length;
  $('#pbar').style.width = (r * 100).toFixed(1) + '%';
  $('#sub').textContent = mode === 'cards' ? `${S.known.length} of ${CARDS.length} cards known` : `Page ${pi + 1} of ${pages.length}`;
}
function show(k) {
  pi = Math.min(pages.length - 1, Math.max(0, k));
  pages.forEach((p, i) => p.hidden = i !== pi);
  const sec = pages[pi].dataset.sec;
  // a section counts as studied once you reach its last page
  if (pi === pages.length - 1 || pages[pi + 1].dataset.sec !== sec) { if (sec !== '0' && !S.done.includes(sec)) { S.done.push(sec); save(); } }
  try { localStorage.setItem(KEY + '-page', pi); } catch (e) {}
  $('#back').disabled = pi === 0;
  const nxt = pages[pi + 1];
  $('#next').innerHTML = !nxt ? 'Finished · go to cards' : (nxt.dataset.sec !== sec ? `Next<small>Section ${nxt.dataset.sec}: ${SECS.find(x => x.n === nxt.dataset.sec).name}</small>` : 'Next');
  paintProgress(); window.scrollTo(0, 0);
}
$('#next').addEventListener('click', () => { if (pi === pages.length - 1) { location.hash = 'cards'; return; } show(pi + 1); });
$('#back').addEventListener('click', () => show(pi - 1));
let sx = null;
$('#pages').addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, { passive: true });
$('#pages').addEventListener('touchend', e => { if (sx === null || e.target.closest('.tw')) return; const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 70) show(pi + (dx < 0 ? 1 : -1)); sx = null; }, { passive: true });
function openToc() {
  const cur = pages[pi].dataset.sec;
  $('#toc').innerHTML = [{ n: '0', name: 'Start here', first: 0 }, ...SECS].map(x => `<li><button type="button" data-p="${x.first}" class="${x.n === cur ? 'here' : ''}"><span class="sn">${x.n === '0' ? '•' : x.n}</span><span>${x.name}</span><span class="tk">${S.done.includes(x.n) ? '✓' : ''}</span></button></li>`).join('')
    + `<li><button type="button" data-cards="1"><span class="sn">★</span><span>Flashcards (${CARDS.length})</span></button></li>`;
  $$('#toc button').forEach(b => b.addEventListener('click', () => { $('#sheet').hidden = true; if (b.dataset.cards) { location.hash = 'cards'; return; } if (mode !== 'read') location.hash = 'read'; show(+b.dataset.p); }));
  $('#sheet').hidden = false;
}
$('#menu').addEventListener('click', openToc);
$('#sclose').addEventListener('click', () => { $('#sheet').hidden = true; });
$('#sheet').addEventListener('click', e => { if (e.target.id === 'sheet') $('#sheet').hidden = true; });
document.addEventListener('keydown', e => { if (mode === 'read' && $('#zoom').hidden && $('#sheet').hidden) { if (e.key === 'ArrowRight') show(pi + 1); if (e.key === 'ArrowLeft') show(pi - 1); } });

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
  $('#pager').hidden = mode !== 'read';
  if (mode === 'cards') { build(); wake(true); paintProgress(); window.scrollTo(0, 0); } else { wake(true); show(pi); }
}
window.addEventListener('hashchange', route); route();
</script>
'''
page = page.replace('__PAGES__', pages_html).replace('__SECJSON__', json.dumps(SECS, ensure_ascii=False)).replace('__CARDS__', json.dumps(cards, ensure_ascii=False).replace('</', '<\\/'))
open(OUT, 'w').write(page)
print('wrote', OUT, f'{len(page)/1e6:.2f} MB', len(cards), 'cards', len(secs), 'sections')
