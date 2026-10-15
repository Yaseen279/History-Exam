"""Find the printed page number of every table/figure caption in a rendered PDF.
Usage: python3 05_page_map.py <rendered.pdf> <out.json>"""
import sys, re, json, pdfplumber
pdf = pdfplumber.open(sys.argv[1]); texts = [(p.extract_text() or '') for p in pdf.pages]
start = next(i for i, t in enumerate(texts) if t.strip().startswith('1. Introduction'))
pages = {}
for i, t in enumerate(texts[start:], start):
    for m in re.finditer(r'^(Table|Figure) (\d+)\. ', t, re.M):
        pages.setdefault(f'{m.group(1)} {m.group(2)}', i - start + 1)
json.dump(pages, open(sys.argv[2], 'w')); print(pages)
