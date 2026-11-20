import sys, copy
from docx import Document
from docx.oxml.ns import qn
IN, OUT_M, OUT_C = sys.argv[1:4]
d = Document(IN); P = d.paragraphs
src = next(p for p in P if p.text.lstrip('\t ').startswith('AI-chatbot users had higher cyberchondria than non-users, and the association'))
ref = next(p for p in P if p.text.startswith('H2 was not supported'))
T1 = ('AI-chatbot users had higher cyberchondria than non-users, and the association remained after adjustment for health anxiety and the other factors '
      '(B = 5.33, p < 0.001). Unlike a search engine, a chatbot can be questioned repeatedly and at any time, which may draw people into a cycle of '
      'repeated searching and reassurance seeking.')
T2 = ('However, the non-user group was small (n = 34), so this finding needs confirmation in larger studies. Most participants trusted online and '
      'AI-generated medical information only moderately, but AI answers may still provide false reassurance.')
def make(text):
    p = copy.deepcopy(ref._p)                      # same paragraph formatting as the other Discussion paragraphs
    for r in p.findall(qn('w:r')): p.remove(r)
    r = copy.deepcopy(ref.runs[0]._r)
    for t in r.findall(qn('w:t')) + r.findall(qn('w:tab')) + r.findall(qn('w:br')): r.remove(t)
    rpr = r.find(qn('w:rPr'))
    if rpr is None: rpr = r.makeelement(qn('w:rPr'), {}); r.insert(0, rpr)
    for h in rpr.findall(qn('w:highlight')): rpr.remove(h)
    rpr.append(rpr.makeelement(qn('w:highlight'), {qn('w:val'): 'green'}))
    t = r.makeelement(qn('w:t'), {}); t.text = text; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); r.append(t)
    p.append(r); return p
a, b = make(T1), make(T2)
src._p.addprevious(a); src._p.addprevious(b); src._p.getparent().remove(src._p)
d.save(OUT_M)
c = Document(OUT_M)
for el in list(c.element.body.iter(qn('w:highlight'))): el.getparent().remove(el)
c.save(OUT_C); print('ok')
