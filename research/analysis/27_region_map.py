"""Arab-region map for the regional-comparison slide (Natural Earth 1:50m borders).
Palestine is drawn as one whole territory. Usage: python3 27_region_map.py <countries.geojson> <out.png>"""
import sys, json, glob, os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib import font_manager as fm
for f in glob.glob(os.path.expanduser('~/.fonts/static/*.ttf')): fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'DMSansStatic'
NAVY, LIGHT, OTHER, SEA, EDGE = '#0E2A47', '#B9CBDA', '#E3E9EF', '#F5F8FA', '#FFFFFF'
STUDY = {'Iraq': NAVY, 'Saudi Arabia': LIGHT, 'Egypt': LIGHT, 'Lebanon': LIGHT, 'Palestine': LIGHT, 'Israel': LIGHT}   # Israel's polygon is part of Palestine here
d = json.load(open(sys.argv[1]))
f, a = plt.subplots(figsize=(8, 6), dpi=200); a.set_facecolor(SEA)
for feat in d['features']:
    name = feat['properties']['ADMIN']; g = feat['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    fc = STUDY.get(name, OTHER)
    ec = fc if name in ('Israel', 'Palestine') else EDGE          # no border inside Palestine
    for poly in polys:
        a.add_patch(Polygon(poly[0], closed=True, fc=fc, ec=ec, lw=0.9 if ec == EDGE else 0.3, zorder=2 if name in STUDY else 1))
a.set_xlim(24, 59); a.set_ylim(13.5, 39.5); a.set_aspect('equal'); a.set_xticks([]); a.set_yticks([])
for s in a.spines.values(): s.set_visible(False)
lab = dict(fontsize=13, fontweight='bold', ha='center', va='center', zorder=5)
a.text(43.6, 33.2, 'Iraq', color='white', **lab)
a.text(45.0, 23.8, 'Saudi Arabia', color=NAVY, **lab)
a.text(29.6, 26.5, 'Egypt', color=NAVY, **lab)
for name, (x, y), (tx, ty) in (('Lebanon', (35.85, 33.9), (31.0, 35.6)), ('Palestine', (35.0, 31.4), (30.0, 32.6))):
    a.plot([x, tx + 1.7], [y, ty], color=NAVY, lw=1, zorder=4); a.plot(x, y, 'o', color=NAVY, ms=4, zorder=5)
    a.text(tx, ty, name, color=NAVY, fontsize=12, fontweight='bold', ha='center', va='center', zorder=5,
           bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=LIGHT, lw=0.8))
f.savefig(sys.argv[2], bbox_inches='tight', pad_inches=0.02, facecolor=SEA); print('wrote', sys.argv[2])
