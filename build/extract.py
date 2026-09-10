import re, json, math, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SRC = os.path.join(ROOT, 'cube.svg')
s = open(SRC).read()
paths = re.findall(r'<path d="([^"]+)" fill="([^"]+)"', s)

tok = re.compile(r'([MLVHCZ])([-\d.,\s]*)')

def parse(d):
    """-> list of (cmd, [nums]) with absolute coords"""
    out = []
    for cmd, args in tok.findall(d):
        nums = [float(v) for v in re.findall(r'-?\d*\.?\d+', args)]
        out.append((cmd, nums))
    return out

def bbox_first_subpath(segs):
    xs, ys = [], []
    cx = cy = 0.0
    started = False
    for cmd, n in segs:
        if cmd == 'Z':
            break
        if cmd in 'MLC':
            step = 2 if cmd in 'ML' else 6
            for i in range(0, len(n), step):
                if cmd == 'C':
                    cx, cy = n[i+4], n[i+5]
                    xs += [n[i], n[i+2], cx]; ys += [n[i+1], n[i+3], cy]
                else:
                    cx, cy = n[i], n[i+1]
                    xs.append(cx); ys.append(cy)
        elif cmd == 'V':
            for v in n: cy = v; xs.append(cx); ys.append(cy)
        elif cmd == 'H':
            for v in n: cx = v; xs.append(cx); ys.append(cy)
    return (min(xs)+max(xs))/2, (min(ys)+max(ys))/2

def recenter(segs, ox, oy, p=1):
    """rewrite absolute path centered on (ox,oy); V/H expanded to L for simplicity"""
    out = []
    cx = cy = 0.0
    for cmd, n in segs:
        if cmd == 'Z':
            out.append('Z'); continue
        if cmd in 'ML':
            pts = []
            for i in range(0, len(n), 2):
                cx, cy = n[i], n[i+1]
                pts.append(f'{round(cx-ox,p)} {round(cy-oy,p)}')
            out.append(cmd + ' '.join(pts))
        elif cmd == 'V':
            pts = []
            for v in n:
                cy = v; pts.append(f'{round(cx-ox,p)} {round(cy-oy,p)}')
            out.append('L' + ' '.join(pts))
        elif cmd == 'H':
            pts = []
            for v in n:
                cx = v; pts.append(f'{round(cx-ox,p)} {round(cy-oy,p)}')
            out.append('L' + ' '.join(pts))
        elif cmd == 'C':
            pts = []
            for i in range(0, len(n), 6):
                seg = []
                for k in range(3):
                    seg.append(f'{round(n[i+2*k]-ox,p)} {round(n[i+2*k+1]-oy,p)}')
                cx, cy = n[i+4], n[i+5]
                pts.append(' '.join(seg))
            out.append('C' + ' '.join(pts))
    return ''.join(out)

raw = []
for d, fill in paths:
    segs = parse(d)
    ox, oy = bbox_first_subpath(segs)
    raw.append((ox, oy, fill, recenter(segs, ox, oy)))

# ---- geometry: fit the isometric cube frame -------------------------------
xs = [r[0] for r in raw]; ys = [r[1] for r in raw]
Cx = (min(xs)+max(xs))/2; Cy = (min(ys)+max(ys))/2
L = (max(ys)-min(ys))/2                      # cube edge length in px
C30 = math.cos(math.radians(30)); S30 = 0.5

VERTS = {
 'top':(0,0,1), 'ul':(0,1,1), 'ur':(1,0,1), 'll':(0,1,0), 'lr':(1,0,0),
 'bot':(1,1,0), 'ctr':(1,1,1)}
EDGES = [('top','ul'),('ul','ll'),('ll','bot'),('bot','lr'),('lr','ur'),('ur','top'),
         ('ctr','ul'),('ctr','ur'),('ctr','bot')]

def seg_dist(p, a, b):
    ab = [b[i]-a[i] for i in range(3)]
    ap = [p[i]-a[i] for i in range(3)]
    denom = sum(v*v for v in ab)
    t = max(0.0, min(1.0, sum(ap[i]*ab[i] for i in range(3))/denom))
    q = [a[i]+ab[i]*t for i in range(3)]
    return math.dist(p, q), t

colors = ['#124D11','#379B2B','#40CE30','#7FEE64','#9EFB87','#F6F573']
cidx = {c:i for i,c in enumerate(colors)}

shapes = {}
tiles = []
for ox, oy, fill, d in raw:
    sx = (ox-Cx)/L; sy = (oy-Cy)/L
    ang = math.degrees(math.atan2(-(oy-Cy), ox-Cx)) % 360
    if 30 <= ang < 150:      # top face, Z=1
        f = 0
        X = ((sy+1)/S30 + sx/C30)/2
        Y = ((sy+1)/S30 - sx/C30)/2
        Z = 1.0
    elif 150 <= ang < 270:   # left face, Y=1
        f = 1
        X = 1 + sx/C30
        Y = 1.0
        Z = (X+1)*S30 - sy
    else:                    # right face, X=1
        f = 2
        Y = 1 - sx/C30
        X = 1.0
        Z = (1+Y)*S30 - sy
    P = (X, Y, Z)
    best = min(((seg_dist(P, VERTS[a], VERTS[b]), i) for i, (a, b) in enumerate(EDGES)))
    (ed, et), ei = best
    if d not in shapes:
        shapes[d] = len(shapes)
    tiles.append([round(ox,1), round(oy,1), shapes[d], cidx[fill], f,
                  round(X,4), round(Y,4), round(Z,4), ei, round(et,4), round(ed,4)])

print('tiles', len(tiles), 'unique shapes', len(shapes))
print('cube', dict(Cx=round(Cx,2), Cy=round(Cy,2), L=round(L,2)))
r = lambda k: (round(min(t[k] for t in tiles),3), round(max(t[k] for t in tiles),3))
print('X', r(5), 'Y', r(6), 'Z', r(7), 'edgeDist', r(10))
print('faces', Counter(t[4] for t in tiles), 'edges', sorted(Counter(t[8] for t in tiles).items()))

shape_list = [None]*len(shapes)
for d, i in shapes.items(): shape_list[i] = d
data = dict(cx=round(Cx,2), cy=round(Cy,2), L=round(L,2),
            w=11727, h=13127, colors=colors, shapes=shape_list, tiles=tiles)
out = os.path.join(HERE, 'tiles.json')
json.dump(data, open(out,'w'), separators=(',',':'))
print('json bytes', os.path.getsize(out))
