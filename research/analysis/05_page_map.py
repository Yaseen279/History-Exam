"""Find the printed page number of every table/figure caption in a rendered PDF.
Usage: python3 05_page_map.py <rendered.pdf> <out.json>"""
import sys, re, json, pdfplumber
pdf = pdfplumber.open(sys.argv[1]); texts = [(p.extract_text() or '') for p in pdf.pages]
start = next(i for i, t in enumerate(texts) if t.strip().startswith('1. Introduction'))
pages = {}
for i, t in enumerate(texts[start:], start):
    for m in re.finditer(r'^(Table|Figure) (\d+)\. ', t, re.M):
        pages.setdefault(f'{m.group(1)} {m.group(2)}', i - start + 1)
# headings for the table of contents (optional third argument: toc_entries.json)
def roman(k):
    vals = [(10, 'x'), (9, 'ix'), (5, 'v'), (4, 'iv'), (1, 'i')]; s = ''
    for v, r in vals:
        while k >= v: s += r; k -= v
    return s
if len(sys.argv) > 3:
    norm = lambda s: re.sub(r'\s+', ' ', s).strip()
    lines = [[norm(l) for l in t.split('\n')] for t in texts]
    # skip the table-of-contents pages themselves: search from the List of Abbreviations onwards
    cur = next(i for i, t in enumerate(texts) if t.strip().startswith('List of Abbreviations'))
    for lvl, h in json.load(open(sys.argv[3])):
        key = norm(h)[:38]
        for i in range(cur, len(lines)):
            if any(l.startswith(key) for l in lines[i]):
                pages['H::' + h] = (i - start + 1) if i >= start else roman(i + 1); cur = i; break
json.dump(pages, open(sys.argv[2], 'w')); print(pages)
