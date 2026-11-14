"""Long-version → short-version table/figure numbers, and a text remapper.
Removed items (only in the long version) become a short phrase instead of a number."""
import re

TABLES = {1: 1, 2: 2, 3: 3, 4: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11}
FIGURES = {1: 1, 3: 2, 4: 3, 5: 4, 7: 5, 8: 6, 9: 7, 10: 8}
GONE = {('Table', 5): 'the invariance results (Section 3.2)', ('Table', 13): 'the sensitivity checks (Section 3.5)',
        ('Figure', 2): 'the study flowchart (long version)', ('Figure', 6): 'the correlation heatmap (long version)',
        ('Figure', 11): 'the item-by-item figure (long version)'}

_PAT = re.compile(r'\b(Tables?|Figures?) (\d+)((?:(?:, | and |–)\d+)*)')

def _map(kind, n):
    m = (TABLES if kind == 'Table' else FIGURES)
    return m.get(n)

def remap(text):
    def sub(mt):
        word, first, rest = mt.group(1), mt.group(2), mt.group(3)
        kind = 'Table' if word.startswith('Table') else 'Figure'
        toks = re.split(r'(, | and |–)', first + rest)
        nums, seps = toks[0::2], toks[1::2]
        if '–' in seps and len(nums) == 2:                 # range: map the end points
            a, b = int(nums[0]), int(nums[1])
            keep = [_map(kind, k) for k in range(a, b + 1) if _map(kind, k)]
            return f'{kind}s {keep[0]}–{keep[-1]}' if len(keep) > 1 else f'{kind} {keep[0]}'
        kept = [_map(kind, int(k)) for k in nums if _map(kind, int(k))]
        if not kept:
            return GONE.get((kind, int(nums[0])), f'{word} {first}')
        if len(kept) == 1:
            return f'{kind} {kept[0]}'
        return f'{kind}s ' + ', '.join(map(str, kept[:-1])) + f' and {kept[-1]}'
    return _PAT.sub(sub, text)

if __name__ == '__main__':
    for s in ['Table 9', 'Tables 3, 4, 5', 'Table 12, Figures 9, 10, Table 13', 'Figure 11', 'Tables 1–13', 'Figures 1–11', 'Table 10 + Figure 8']:
        print(f'{s!r} -> {remap(s)!r}')
