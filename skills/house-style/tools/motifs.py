#!/usr/bin/env python3
"""Motif library: the art a theme recipe (the "art" block of theme.json) draws from, written out as CSS.

    python3 tools/motifs.py --list              the motifs and the parameters each takes
    python3 tools/motifs.py --sheet out.html    a page drawing every shape and pattern, to pick from
    from motifs import recipe_css; deck_css, doc_css = recipe_css(theme)

Shapes are SVG masks, so they take any colour token; patterns are SVG tiles repeated inside a box; bars, frames,
rules and glows are plain CSS. Each slot (cover, section, statement, closing, content for decks; cover, opener for
documents) holds up to two motifs, drawn on its ::before and ::after behind the text. Deck sizes and offsets are in
art pixels (--art-px, so they scale with the format), document ones in mm. plan/motifs.md has the recipe format.
"""
import argparse
import math
import re
import sys
from urllib.parse import quote

# Shapes on a 100 x 100 box unless a view box is given; filled, so a mask shows them in the motif's colour
def _star(n, r1, r2, rot=-90):
    pts = []
    for i in range(2 * n):
        r, a = (r1 if i % 2 == 0 else r2), math.radians(rot + i * 180 / n)
        pts.append('%.1f %.1f' % (50 + r * math.cos(a), 50 + r * math.sin(a)))
    return '<path d="M%sZ"/>' % 'L'.join(pts)


def _rays(n=16):
    out = []
    for i in range(n):
        a, d = math.radians(i * 360 / n), math.radians(360 / n / 4)
        out.append('M50 50L%.1f %.1fL%.1f %.1fZ' % (50 + 70 * math.cos(a - d), 50 + 70 * math.sin(a - d),
                                                    50 + 70 * math.cos(a + d), 50 + 70 * math.sin(a + d)))
    return '<path d="%s"/>' % ''.join(out)


SHAPES = {
    'circle': ('0 0 100 100', '<circle cx="50" cy="50" r="50"/>'),
    'ring': ('0 0 100 100', '<path fill-rule="evenodd" d="M50 0a50 50 0 1 0 0 100a50 50 0 1 0 0-100zm0 16a34 34 0 1 1 0 68a34 34 0 1 1 0-68z"/>'),
    'blob': ('0 0 100 100', '<path d="M64 4c18 4 32 18 34 36 2 16-8 26-6 40 1 12-12 20-26 18-14-1-22 2-36 0C14 96 2 84 2 66s12-22 12-36S40-2 64 4z"/>'),
    'blob-2': ('0 0 100 100', '<path d="M30 6c14-6 26 4 40 4s26 8 28 24-10 24-8 38-8 26-26 26-30-6-44-12S0 70 2 52 16 12 30 6z"/>'),
    'burst': ('0 0 100 100', _star(16, 50, 38)),
    'star': ('0 0 100 100', _star(5, 50, 21)),
    'rays': ('0 0 100 100', _rays()),
    'arc': ('0 0 100 100', '<path d="M0 100A100 100 0 0 1 100 0v16A84 84 0 0 0 16 100z"/>'),
    'half-disc': ('0 0 100 50', '<path d="M0 50a50 50 0 0 1 100 0z"/>'),
    'quarter-disc': ('0 0 100 100', '<path d="M0 0h100A100 100 0 0 1 0 100z"/>'),
    'squiggle': ('0 0 100 34', '<path d="M5 17q11.25-16 22.5 0t22.5 0 22.5 0 22.5 0" fill="none" stroke="#000" stroke-width="7" stroke-linecap="round"/>'),
    'wave': ('0 0 100 30', '<path d="M0 12q12.5-12 25 0t25 0 25 0 25 0V30H0z"/>'),
    'diamond': ('0 0 100 100', '<path d="M50 0 100 50 50 100 0 50z"/>'),
    'triangle': ('0 0 100 100', '<path d="M50 4 98 92H2z"/>'),
    'leaf': ('0 0 100 100', '<path d="M6 94C6 40 40 6 94 6c0 54-34 88-88 88z"/>'),
    'plus': ('0 0 100 100', '<path d="M38 0h24v38h38v24H62v38H38V62H0V38h38z"/>'),
    'cross': ('0 0 100 100', '<path transform="rotate(45 50 50)" d="M40 0h20v40h40v20H60v40H40V60H0V40h40z"/>'),
    'corner': ('0 0 100 100', '<path d="M0 0h100v5H5v95H0z"/><circle cx="20" cy="20" r="7"/><path d="M14 40h5v30h-5zM40 14v5h30v-5z"/>'),
    'bracket': ('0 0 40 100', '<path d="M0 0h40v7H7v86h33v7H0z"/>'),
}

# Pattern tiles: (view box, svg, default tile size)
PATTERNS = {
    'dots': ('0 0 10 10', '<circle cx="5" cy="5" r="1.5"/>', 18),
    'halftone': ('0 0 10 10', '<circle cx="2.5" cy="2.5" r="1.6"/><circle cx="7.5" cy="7.5" r="1.6"/>', 14),
    'grid': ('0 0 10 10', '<path d="M0 0h10v.5H.5V10H0z"/>', 24),
    'graph': ('0 0 50 50', '<path d="M0 0h50v1H1v49H0z"/><path opacity=".45" d="M10 0h.4v50H10zM20 0h.4v50H20zM30 0h.4v50H30zM40 0h.4v50H40zM0 10h50v.4H0zM0 20h50v.4H0zM0 30h50v.4H0zM0 40h50v.4H0z"/>', 80),
    'lines': ('0 0 10 10', '<path d="M0 0h10v1.1H0z"/>', 12),
    'diagonal': ('0 0 10 10', '<path d="M-1 1 1-1M0 10 10 0M9 11l2-2" stroke="#000" stroke-width="1.3"/>', 12),
    'checks': ('0 0 10 10', '<path d="M0 0h5v5H0zM5 5h5v5H5z"/>', 20),
    'waves': ('0 0 20 10', '<path d="M0 5q5-4 10 0t10 0" fill="none" stroke="#000" stroke-width="1.1"/>', 26),
    'plus-grid': ('0 0 10 10', '<path d="M4.5 3h1v1.5H7v1H5.5V7h-1V5.5H3v-1h1.5z"/>', 20),
    'zigzag': ('0 0 10 10', '<path d="M0 7 2.5 3 5 7 7.5 3 10 7" fill="none" stroke="#000" stroke-width="1"/>', 16),
}
# Motifs print as clip paths (CSS shape()), never as large masks: Quartz (Preview, Safari, Quick Look) clips any CSS
# mask in a Chrome PDF to about 35 mm, while a clip path is plain vector art in every reader.
_NUM = r'-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?'
_ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}


def _arc(p0, rx, ry, phi, large, sweep, p):
    """An SVG arc as cubic segments [(c1, c2, end)]."""
    (x1, y1), (x2, y2) = p0, p
    if rx == 0 or ry == 0 or (x1, y1) == (x2, y2):
        return [(p0, p, p)]
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    co = math.sqrt(max(0, num / (rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2))) * (-1 if large == sweep else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = cp * cxp - sp * cyp + (x1 + x2) / 2, sp * cxp + cp * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(1, math.ceil(abs(dt) / (math.pi / 2)))
    k = 4 / 3 * math.tan(dt / n / 4)
    pt = lambda t: (cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp)
    dv = lambda t: (-rx * math.sin(t) * cp - ry * math.cos(t) * sp, -rx * math.sin(t) * sp + ry * math.cos(t) * cp)
    out = []
    for i in range(n):
        a, b = t1 + dt * i / n, t1 + dt * (i + 1) / n
        pa, pb, da, db = pt(a), pt(b), dv(a), dv(b)
        out.append(((pa[0] + k * da[0], pa[1] + k * da[1]), (pb[0] - k * db[0], pb[1] - k * db[1]), pb))
    out[-1] = (out[-1][0], out[-1][1], p)
    return out


def _subpaths(d):
    """SVG path data as subpaths [start, [(c1, c2, end) or (None, None, end)], closed], all absolute."""
    toks = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|' + _NUM, d)
    subs, cur, start, last_c, cmd, prev, i = [], (0, 0), (0, 0), None, None, None, 0
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd in 'Zz':
                if subs:
                    subs[-1][2] = True
                cur, last_c = start, None
                continue
        n = _ARGS[cmd.upper()]
        a = [float(v) for v in toks[i:i + n]]; i += n
        rel, C = cmd.islower(), cmd.upper()
        ox, oy = cur if rel else (0, 0)
        if C == 'M':
            cur = start = (ox + a[0], oy + a[1]); subs.append([cur, [], False]); last_c = None
            cmd, prev = ('l' if rel else 'L'), 'M'
            continue
        if C in 'LHV':
            if C == 'L':
                e = (ox + a[0], oy + a[1])
            elif C == 'H':
                e = ((cur[0] if rel else 0) + a[0], cur[1])
            else:
                e = (cur[0], (cur[1] if rel else 0) + a[0])
            seg = (None, None, e); last_c = None
        elif C == 'C':
            seg = ((ox + a[0], oy + a[1]), (ox + a[2], oy + a[3]), (ox + a[4], oy + a[5])); last_c = seg[1]
        elif C == 'S':
            c1 = (2 * cur[0] - last_c[0], 2 * cur[1] - last_c[1]) if last_c else cur
            seg = (c1, (ox + a[0], oy + a[1]), (ox + a[2], oy + a[3])); last_c = seg[1]
        elif C in 'QT':
            if C == 'Q':
                q, e = (ox + a[0], oy + a[1]), (ox + a[2], oy + a[3])
            else:
                q = (2 * cur[0] - last_c[0], 2 * cur[1] - last_c[1]) if last_c and prev in ('Q', 'T') else cur
                e = (ox + a[0], oy + a[1])
            seg = ((cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1])),
                   (e[0] + 2 / 3 * (q[0] - e[0]), e[1] + 2 / 3 * (q[1] - e[1])), e)
            last_c = q
        elif C == 'A':
            for c1, c2, e in _arc(cur, a[0], a[1], a[2], int(a[3]), int(a[4]), (ox + a[5], oy + a[6])):
                subs[-1][1].append((c1, c2, e))
            cur, last_c, prev = (ox + a[5], oy + a[6]), None, 'A'
            continue
        prev = C
        subs[-1][1].append(seg); cur = seg[2]
    return subs


def _circle(cx, cy, r):
    return _subpaths('M%g %gA%g %g 0 1 1 %g %gA%g %g 0 1 1 %g %gZ' % (cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy))


def _flatten(sub, steps=14):
    start, segs, _ = sub
    pts, cur = [start], start
    for c1, c2, e in segs:
        if c1 is None:
            pts.append(e)
        else:
            for k in range(1, steps + 1):
                t = k / steps; u = 1 - t
                pts.append((u ** 3 * cur[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * e[0],
                            u ** 3 * cur[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * e[1]))
        cur = e
    return pts


def _outline(sub, w, round_cap, steps=14):
    """A stroked open path as a closed polygon subpath."""
    pts = _flatten(sub, steps)
    h, left, right = w / 2, [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * h, dx / L * h
        left.append((x + nx, y + ny)); right.append((x - nx, y - ny))
    def cap(p, q):   # half circle from the left edge to the right edge round end point p, heading away from q
        if not round_cap:
            return []
        dx, dy = p[0] - q[0], p[1] - q[1]; L = math.hypot(dx, dy) or 1
        base = math.atan2(-dx / L, dy / L)
        return [(p[0] + h * math.cos(base - math.pi * k / 8), p[1] + h * math.sin(base - math.pi * k / 8)) for k in range(1, 8)]
    ring = left + cap(pts[-1], pts[-2]) + right[::-1] + cap(pts[0], pts[1])
    return [ring[0], [(None, None, p) for p in ring[1:]], True]


def geometry(body, steps=14):
    """Every element of a motif's SVG body as filled subpaths (strokes outlined) and the fill rule."""
    subs, evenodd = [], 'evenodd' in body
    for tag, attrs in re.findall(r'<(path|circle|rect)\b([^>]*)/?>', body):
        at = dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
        if tag == 'circle':
            got = _circle(float(at.get('cx', 0)), float(at.get('cy', 0)), float(at['r']))
        elif tag == 'rect':
            x, y, w, h = (float(at.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
            got = _subpaths('M%g %gh%gv%gh%gz' % (x, y, w, h, -w))
        else:
            got = _subpaths(at['d'])
        if 'stroke' in at:
            got = [_outline(sp, float(at.get('stroke-width', 1)), at.get('stroke-linecap') == 'round', steps) for sp in got]
        rot = re.match(r'rotate\((%s)\s+(%s)\s+(%s)\)' % (_NUM, _NUM, _NUM), at.get('transform', ''))
        if rot:
            a, cx, cy = math.radians(float(rot.group(1))), float(rot.group(2)), float(rot.group(3))
            R = lambda p: (cx + (p[0] - cx) * math.cos(a) - (p[1] - cy) * math.sin(a),
                           cy + (p[0] - cx) * math.sin(a) + (p[1] - cy) * math.cos(a))
            got = [[R(st), [(c1 and R(c1), c2 and R(c2), R(e)) for c1, c2, e in segs], cl] for st, segs, cl in got]
        subs += got
    return subs, evenodd


def _xf(subs, f):
    return [[f(st), [(c1 and f(c1), c2 and f(c2), f(e)) for c1, c2, e in segs], cl] for st, segs, cl in subs]


def _cmds(subs, P):
    """shape() commands for subpaths, each starting with "move to"; P writes a point."""
    out = []
    for st, segs, closed in subs:
        out.append('move to ' + P(st))
        for c1, c2, e in segs:
            out.append('line to %s' % P(e) if c1 is None else 'curve to %s with %s / %s' % (P(e), P(c1), P(c2)))
        if closed:
            out.append('close')
    return out


def _shape(cmds, evenodd=False):
    return 'shape(%sfrom %s)' % ('evenodd ' if evenodd else '', ', '.join(cmds)[len('move to '):])


def shape_css(subs, evenodd, W, H, nd=2):
    """Subpaths in a W x H box as a CSS shape(), in percentages so it scales with its box."""
    return _shape(_cmds(subs, lambda p: '%s%% %s%%' % (_fmt(p[0] / W * 100, nd), _fmt(p[1] / H * 100, nd))), evenodd)


def _fmt(v, nd):
    t = ('%.*f' % (nd, v)).rstrip('0').rstrip('.')
    return '0' if t in ('-0', '') else t


BANDS = {'wave'}   # shapes that run edge to edge: they stretch to their box unless a recipe says "stretch": false


def shape_clip(kind, W=None, H=None, stretch=False):
    """clip-path for a shape motif. With a numeric box W x H the shape keeps its proportions (contain), centred."""
    view, body = SHAPES[kind]
    vx, vy, vw, vh = (float(v) for v in view.split())
    subs, eo = geometry(body)
    subs = _xf(subs, lambda p: (p[0] - vx, p[1] - vy))
    if stretch or not (isinstance(W, (int, float)) and isinstance(H, (int, float))):
        return shape_css(subs, eo, vw, vh)
    k = min(W / vw, H / vh); ox, oy = (W - vw * k) / 2, (H - vh * k) / 2
    return shape_css(_xf(subs, lambda p: (ox + p[0] * k, oy + p[1] * k)), eo, W, H)


def pattern_clip(kind, W, H, tile, fade=None):
    """clip-path for a pattern motif: its tile repeated over a W x H box (all in one unit); a fade shrinks the tiles
    toward the faded edge, like a halftone."""
    view, body, _ = PATTERNS[kind]
    vx, vy, vw, vh = (float(v) for v in view.split())
    subs, eo = geometry(body, steps=4)
    tw, th = tile, tile * vh / vw
    out = []
    for j in range(math.ceil(H / th)):
        for i in range(math.ceil(W / tw)):
            cx, cy = (i + .5) * tw, (j + .5) * th
            f = 1.0
            if fade == 'radial':
                f = (1 - math.hypot((cx / W - .5) * 2, (cy / H - .5) * 2)) / .75
            elif fade in ('l', 'r', 't', 'b'):
                f = {'l': cx / W, 'r': 1 - cx / W, 't': cy / H, 'b': 1 - cy / H}[fade] / .65
            f = max(0.0, min(1.0, f))
            if f < .12:
                continue
            k = tw / vw
            out += _xf(subs, lambda p, i=i, j=j, f=f, k=k: (cx + ((p[0] - vx) * k - tw / 2) * f, cy + ((p[1] - vy) * k - th / 2) * f))
    return shape_css(out, eo, W, H, nd=1) if out else 'inset(50%)'


# Clip paths for a hand-made theme's own pictures. Preview, Safari and Quick Look clip a CSS mask bigger than about
# 35 mm in Chrome's PDFs, so a theme draws big shapes with clip-path: var(--NAME-clip) and build_themes.py writes each
# one from the pictures theme.css holds (clips_css). Small masks (icons, list marks) print fine and stay masks.
CLIPS_START = '/* clip paths: written by tools/build_themes.py from the pictures above, since big CSS masks print wrong in Preview and Safari. Do not edit. */'
CLIPS_END = '/* end of clip paths */'


def _affine(xf):
    """An SVG transform list (translate, scale, rotate, matrix) as a function on points."""
    M = (1, 0, 0, 1, 0, 0)
    mul = lambda A, B: (A[0] * B[0] + A[2] * B[1], A[1] * B[0] + A[3] * B[1], A[0] * B[2] + A[2] * B[3],
                        A[1] * B[2] + A[3] * B[3], A[0] * B[4] + A[2] * B[5] + A[4], A[1] * B[4] + A[3] * B[5] + A[5])
    for fn, args in re.findall(r'(\w+)\(([^)]*)\)', xf):
        a = [float(v) for v in re.findall(_NUM, args)]
        if fn == 'translate':
            T = (1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0)
        elif fn == 'scale':
            T = (a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0)
        elif fn == 'rotate':
            c, s = math.cos(math.radians(a[0])), math.sin(math.radians(a[0]))
            cx, cy = (a[1], a[2]) if len(a) > 2 else (0, 0)
            T = (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy)
        elif fn == 'matrix':
            T = tuple(a)
        else:
            sys.exit('motifs: SVG transform %s() is not handled' % fn)
        M = mul(M, T)
    return lambda p: (M[0] * p[0] + M[2] * p[1] + M[4], M[1] * p[0] + M[3] * p[1] + M[5])


def uri_geometry(uri, steps=14):
    """View box and filled subpaths (from the view box's corner) of an SVG data URI as theme.css holds it.
    Shapes drawn black inside a <mask> become holes."""
    from urllib.parse import unquote
    svg = unquote(uri).replace("'", '"')
    vx, vy, vw, vh = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).replace(',', ' ').split())
    holes = [e for m in re.findall(r'<mask\b.*?</mask>', svg, re.S)
             for e in re.findall(r'<(?:path|circle|rect)\b[^>]*>', m) if re.search(r'"(black|#000|#000000)"', e)]
    svg = re.sub(r'<defs>.*?</defs>|<mask\b.*?</mask>', '', svg, flags=re.S)
    subs, eo = [], False
    for xf, inner in re.findall(r'<g transform="([^"]*)">(.*?)</g>', svg, re.S):
        got, e = geometry(inner, steps)
        subs += _xf(got, _affine(xf))
        eo = eo or e
    got, e = geometry(re.sub(r'<g\b.*?</g>', '', svg, flags=re.S), steps)
    subs, eo = subs + got, eo or e
    if holes:
        subs += geometry(''.join(holes), steps)[0]
        eo = True
    return (vw, vh), _xf(subs, lambda p: (p[0] - vx, p[1] - vy)), eo


def _calc(size, f, base=None):
    """A length f of the way across a corner box of the given size, from the box's start or (base) its end."""
    f = round(f, 3)
    t = _fmt(f, 3).replace('0.', '.', 1)
    if base is None:
        return '0' if f == 0 else 'calc(%s*%s)' % (size, t)
    return base if f == 0 else 'calc(%s - %s*%s)' % (base, size, t)


def corners_clip(uris, size):
    """Four corner pictures (tl, tr, bl, br), each drawn size x size (a CSS length) in its corner of the box."""
    cmds, eo = [], False
    for c in ('tl', 'tr', 'bl', 'br'):
        (vw, vh), subs, e = uri_geometry(uris[c], steps=4)
        eo = eo or e
        P = lambda p, c=c, vw=vw, vh=vh: '%s %s' % (
            _calc(size, p[0] / vw) if c[1] == 'l' else _calc(size, 1 - p[0] / vw, '100%'),
            _calc(size, p[1] / vh) if c[0] == 't' else _calc(size, 1 - p[1] / vh, '100%'))
        cmds += _cmds(subs, P)
    return _shape(cmds, eo)


def cols_clip(n, w='var(--rule-w, .4pt)', inset='var(--bleed, 0mm)'):
    """n columns across the box inside the inset, drawn as a hairline at the start of each."""
    return _shape(['move to calc(%s + (100%% - 2 * %s) * %s) 0, hline by %s, vline to 100%%, hline by calc(-1 * %s), close'
                   % (inset, inset, _fmt(k / n, 5), w, w) for k in range(n)])


def grid_clip(cell, w='var(--rule-w, .4pt)', inset='var(--bleed, 0mm)', extent=440):
    """Square grid paper: hairlines every cell mm from the inset corner, enough for pages up to extent mm."""
    ks = range(-1, int(extent / cell) + 1)
    at = lambda k: 'calc(%s + %smm)' % (inset, _fmt(k * cell, 3))
    return _shape(['move to %s 0, hline by %s, vline to 100%%, hline by calc(-1 * %s), close' % (at(k), w, w) for k in ks] +
                  ['move to 0 %s, hline to 100%%, vline by %s, hline to 0, close' % (at(k), w) for k in ks])


def clips_css(tid, *css):
    """The clip paths a theme's CSS asks for with var(--NAME-clip), as one rule for the deck (and each slide, so sizes
    set on slides apply). NAME is a picture in theme.css (stretched to the box); or NAME-tl, -tr, -bl and -br pictures
    (corners, each var(--NAME-size) square); or cols-N (N hairline columns inside --bleed); or grid-Nmm (grid paper)."""
    text = '\n'.join(css)
    pics = dict(re.findall(r'--([a-z0-9-]+):\s*url\("(data:image/svg\+xml,[^"]*)"\)', text))
    out = []
    for name in sorted(set(re.findall(r'var\(--([a-z0-9-]+)-clip\)', text))):
        if name in pics:
            (vw, vh), subs, eo = uri_geometry(pics[name])
            val = shape_css(subs, eo, vw, vh)
        elif all('%s-%s' % (name, c) in pics for c in ('tl', 'tr', 'bl', 'br')):
            val = corners_clip({c: pics['%s-%s' % (name, c)] for c in ('tl', 'tr', 'bl', 'br')}, 'var(--%s-size)' % name)
        elif re.fullmatch(r'cols-\d+', name):
            val = cols_clip(int(name[5:]))
        elif re.fullmatch(r'grid-\d+(\.\d+)?mm', name):
            val = grid_clip(float(name[5:-2]))
        else:
            sys.exit('%s: var(--%s-clip) has no picture --%s to draw from' % (tid, name, name))
        out.append('--%s-clip: %s;' % (name, val))
    if not out:
        return ''
    root = '.pc-deck[data-theme="%s"]' % tid
    return '%s\n%s, %s .pc-slide {\n  %s }\n%s\n' % (CLIPS_START, root, root, '\n  '.join(out), CLIPS_END)


OTHER = {
    'bar': 'a solid band on one edge: at t, b, l or r; size = its thickness',
    'frame': 'a border inset from the edges: inset, thickness, line (solid or double)',
    'rule': 'a short solid line: w, h, at',
    'glow': 'soft radial light, a gradient-mesh look: at, size, color, opacity',
}
PARAMS = 'at (tl tr bl br t b l r c full), size or w and h, x, y, color (a token or a hex), opacity, rotate, fade (l r t b radial), tile (patterns)'
DECK_SLOTS = {
    'cover': '.pc-cover', 'section': '.pc-section', 'statement': '.pc-statement', 'closing': '.pc-closing',
    'content': '.pc-slide:not(.pc-cover, .pc-section, .pc-statement, .pc-closing)',
}
NARROW = ':is(%s)' % ', '.join('[data-format="%s"]' % f for f in ('1x1', '4x5', '9x16', 'a4p', '5x7', 'letter-p'))
WIDE = ':is([data-format="3x1"], [data-format="4x1"])'
WIDE_K = .6


def shrink(m, k):
    """A motif with its pixel sizes and offsets scaled by k (sizes in % or other units stay as they are)."""
    if m.get('motif') in ('bar', 'frame', 'rule'):   # edge bands and frames keep their thickness
        return m
    out = dict(m)
    for key in ('size', 'w', 'h', 'x', 'y', 'tile', 'inset', 'thickness'):
        if isinstance(out.get(key), (int, float)) and not isinstance(out.get(key), bool):
            out[key] = round(out[key] * k, 1)
    return out


TOKENS = ('accent', 'accent-2', 'accent-ink', 'ink', 'ink-2', 'ink-3', 'line', 'surface', 'surface-2', 'bg')


def svg_uri(view, body):
    svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='%s'>%s</svg>" % (view, body.replace('"', "'"))
    return 'url("data:image/svg+xml,%s")' % quote(svg, safe=" '=:/;,.-()")


def color(c):
    c = str(c or 'accent')
    if c.startswith('#') or c.startswith('rgb') or c.startswith('var('):
        return c
    if c.startswith('chart-'):
        return 'var(--%s, var(--accent))' % c
    return 'var(--%s, var(--accent))' % c if c in TOKENS else c


def length(v, unit):
    if isinstance(v, str):
        return v   # given with its unit: "100%", "12mm", "calc(...)"
    return 'calc(%g * var(--art-px))' % v if unit == 'art' else '%gmm' % v


def fade_layer(f):
    return {'l': 'linear-gradient(to left, #000 35%, transparent)', 'r': 'linear-gradient(to right, #000 35%, transparent)',
            't': 'linear-gradient(to top, #000 35%, transparent)', 'b': 'linear-gradient(to bottom, #000 35%, transparent)',
            'radial': 'radial-gradient(closest-side, #000 25%, transparent)'}.get(f)


def _box(m, unit):
    """A motif's box (w, h) as given: numbers in the slot's unit, or strings with their own unit. A shape given only
    a size takes its view box's proportions."""
    size = m.get('size', 300 if unit == 'art' else 60)
    w, h = m.get('w', size), m.get('h', size)
    if m.get('motif') in SHAPES and 'h' not in m and isinstance(w, (int, float)):
        vb = [float(v) for v in SHAPES[m['motif']][0].split()]
        h = w * vb[3] / vb[2]
    return w, h


FADE_OVER = {'l': 'linear-gradient(to left, transparent 35%%, %s)', 'r': 'linear-gradient(to right, transparent 35%%, %s)',
             't': 'linear-gradient(to top, transparent 35%%, %s)', 'b': 'linear-gradient(to bottom, transparent 35%%, %s)',
             'radial': 'radial-gradient(closest-side, transparent 25%%, %s)'}


def place(m, unit, bleed):
    """Position and size of a motif's box inside its slot."""
    at = m.get('at', 'tr')
    if at == 'full':
        return ['inset: 0']
    w, h = _box(m, unit)
    kind = m.get('motif')
    if kind == 'bar':
        thick = length(m.get('size', 14 if unit == 'art' else 4), unit)
        edge = {'t': 'top', 'b': 'bottom', 'l': 'left', 'r': 'right'}.get(at[0], 'top')
        if edge in ('top', 'bottom'):
            return ['%s: 0' % edge, 'left: 0', 'right: 0', 'height: calc(%s%s)' % (thick, ' + var(--bleed, 0mm)' if bleed else '')]
        return ['%s: 0' % edge, 'top: 0', 'bottom: 0', 'width: calc(%s%s)' % (thick, ' + var(--bleed, 0mm)' if bleed else '')]
    W, H, X, Y = length(w, unit), length(h, unit), length(m.get('x', 0), unit), length(m.get('y', 0), unit)
    out = ['width: %s' % W, 'height: %s' % H]
    out.append('left: %s' % X if 'l' in at else 'right: %s' % X if 'r' in at else 'left: calc(50%% - %s / 2 + %s)' % (W, X))
    out.append('top: %s' % Y if 't' in at else 'bottom: %s' % Y if 'b' in at else 'top: calc(50%% - %s / 2 + %s)' % (H, Y))
    return out


def motif_css(m, unit, bleed=False):
    """The declarations that draw one motif in its pseudo-element."""
    kind = m.get('motif')
    col = color(m.get('color'))
    d = ['content: ""', 'position: absolute', 'pointer-events: none'] + place(m, unit, bleed)
    masks, fade, (W, H) = [], m.get('fade'), _box(m, unit)
    num = lambda v: isinstance(v, (int, float))
    under = color(m.get('fade_to', 'bg'))
    if kind in SHAPES:
        d.append('background: %s%s' % (FADE_OVER[fade] % under + ', ' if fade in FADE_OVER else '', col))
        d.append('clip-path: %s' % shape_clip(kind, W, H, m.get('stretch', kind in BANDS)))
    elif kind in PATTERNS:
        tile = m.get('tile', PATTERNS[kind][2] if unit == 'art' else PATTERNS[kind][2] / 4)
        d.append('background: %s' % col)
        if num(W) and num(H) and num(tile) and m.get('at') != 'full':
            d.append('clip-path: %s' % pattern_clip(kind, W, H, tile, fade))
        else:   # a box sized in % or with units: a mask, which Quartz clips beyond about 35 mm in PDFs
            masks.append('var(--m-%s) 0 0 / %s %s repeat' % (kind, length(tile, unit), length(tile, unit)))
            if fade_layer(fade):
                masks.append(fade_layer(fade))
    elif kind in ('bar', 'rule'):
        d.append('background: %s%s' % (FADE_OVER[fade] % under + ', ' if fade in FADE_OVER else '', col))
    elif kind == 'frame':
        inset = length(m.get('inset', 28 if unit == 'art' else 10), unit)
        thick = length(m.get('thickness', 2 if unit == 'art' else .6), unit)
        d = ['content: ""', 'position: absolute', 'pointer-events: none',
             'inset: %s' % ('calc(%s + var(--bleed, 0mm))' % inset if bleed else inset),
             'border: %s %s %s' % (thick, m.get('line', 'solid'), col)]
    elif kind == 'glow':
        d.append('background: radial-gradient(closest-side, color-mix(in srgb, %s 70%%, transparent), transparent)' % col)
        d.append('border-radius: 50%')
    else:
        raise ValueError('unknown motif %r (python3 tools/motifs.py --list)' % kind)
    if masks:
        d.append('-webkit-mask: %s' % ', '.join(masks))
        d.append('mask: %s' % ', '.join(masks))
        if len(masks) > 1:
            d.append('-webkit-mask-composite: source-in')
            d.append('mask-composite: intersect')
    if m.get('opacity') is not None:
        d.append('opacity: %g' % m['opacity'])
    if m.get('rotate'):
        d.append('transform: rotate(%gdeg)' % m['rotate'])
    return d


def used(art):
    names = set()
    for part in ('deck', 'doc'):
        for slot, ms in (art.get(part) or {}).items():
            for m in (ms if isinstance(ms, list) else [ms]):
                names.add(m.get('motif'))
    return sorted(n for n in names if n in SHAPES or n in PATTERNS)


def pictures(names):
    out = []
    for n in names:
        view, body = SHAPES[n] if n in SHAPES else PATTERNS[n][:2]
        out.append('  --m-%s: %s;' % (n, svg_uri(view, body)))
    return out


def rule(sel, decls):
    return '%s {\n  %s; }' % (sel, ';\n  '.join(decls))


KICKERS = {   # filled kickers: --accent-text meets 4.5:1 against --bg on every surface, so --bg text on it passes too; photo slides set --kicker-on
    'pill': ['width: fit-content', 'padding: .38em .9em .42em', 'border-radius: 999px', 'background: var(--accent-text)', 'color: var(--kicker-on, var(--bg))'],
    'tab': ['width: fit-content', 'padding: .38em .7em .42em', 'border-radius: 2px', 'background: var(--accent-text)', 'color: var(--kicker-on, var(--bg))'],
    'underline': ['width: fit-content', 'padding-bottom: .35em', 'border-bottom: .16em solid var(--accent)'],
    'outline': ['width: fit-content', 'padding: .34em .8em .38em', 'border-radius: 999px', 'border: .1em solid currentColor'],
}
CARDS = {
    'outline': ['box-shadow: none', 'border: 2px solid var(--ink)'],
    'shadow': ['box-shadow: 7px 7px 0 var(--ink)', 'border: 2px solid var(--ink)'],
    'soft': ['box-shadow: 0 12px 34px rgba(0, 0, 0, .12)', 'border: 0'],
    'flat': ['box-shadow: none', 'border: 0', 'background: var(--surface-2)'],
}


def recipe_css(theme):
    """(theme.css, doc.css) for a theme whose theme.json has an "art" block."""
    art, tid = theme['art'], theme['id']
    deck = '.pc-deck[data-theme="%s"]' % tid
    doc = '.pc-doc[data-theme="%s"]' % tid
    head = '/* %s: art from the recipe in theme.json (tools/motifs.py). Edit the recipe, or extra.css for the theme\'s own touches. */' % theme.get('name', tid)
    pics = pictures(used(art))
    a = [head, '%s {\n%s\n}' % (deck, '\n'.join(pics)) if pics else '']
    for part in ('deck', 'doc'):   # each slot draws on its ::before and ::after, so a third motif would vanish unseen
        for slot, ms in (art.get(part) or {}).items():
            if isinstance(ms, list) and len(ms) > 2:
                raise ValueError('%s: art.%s.%s has %d motifs; a slot holds at most two' % (tid, part, slot, len(ms)))
    for slot, ms in (art.get('deck') or {}).items():
        ms = ms if isinstance(ms, list) else [ms]
        base = '%s %s:not(.pc-split, .pc-bleed)' % (deck, DECK_SLOTS[slot])
        for m, pseudo in zip(ms[:2], ('::before', '::after')):
            a.append(rule(base + pseudo, ['z-index: -1'] + motif_css(m, 'art')))
            small = shrink(m, WIDE_K)   # banners are short: the art at 60%, so it keeps clear of the words
            if small != m:
                a.append(rule('%s%s %s:not(.pc-split, .pc-bleed)%s' % (deck, WIDE, DECK_SLOTS[slot], pseudo),
                              ['inset: auto'] + motif_css(small, 'art')))
    for slot, vs in (art.get('vars') or {}).items():   # "cover@narrow" applies on the square and portrait formats only
        name, _, scope = slot.partition('@')
        a.append(rule('%s%s %s' % (deck, NARROW if scope == 'narrow' else '', DECK_SLOTS[name]), ['%s: %s' % kv for kv in vs.items()]))
    if art.get('kicker') in KICKERS:
        a.append(rule('%s .pc-kicker' % deck, KICKERS[art['kicker']]))
    elif art.get('kicker') == 'dash':
        a.append(rule('%s .pc-kicker::before' % deck, ['content: ""', 'display: inline-block', 'width: 1.4em', 'height: .14em',
                                                      'background: var(--accent)', 'vertical-align: .3em', 'margin-right: .55em']))
    if art.get('cards') in CARDS:
        a.append(rule('%s .pc-card:not(.pc-card--flat)' % deck, CARDS[art['cards']]))
    b = [head.replace('art from', 'document art from')]
    dart = art.get('doc') or {}
    for slot in ('cover', 'opener'):
        ms = dart.get(slot) or []
        ms = ms if isinstance(ms, list) else [ms]
        if not ms:
            continue
        sel = '%s .pc-cover:not([data-cover="full"])' % doc if slot == 'cover' else '%s .pc-opener' % doc
        if slot == 'opener':
            b.append(rule(sel, ['position: relative']))
        for m, pseudo in zip(ms[:2], ('::before', '::after')):
            b.append(rule(sel + pseudo, ['z-index: 0'] + motif_css(m, 'mm', bleed=slot == 'cover')))
        b.append(rule('%s > :not(.pc-media)' % sel, ['position: relative', 'z-index: 1']))
    if dart.get('mark'):
        m = dict(dart['mark'])
        size = m.get('size', 5)
        decl = ['content: ""', 'display: block', 'width: %gpt' % m.get('w', size), 'height: %gpt' % m.get('h', size),
                'margin: 9pt 0 0', 'background: %s' % color(m.get('color'))]
        if m.get('motif') in SHAPES:
            decl += ['-webkit-mask: var(--m-%s) center / contain no-repeat' % m['motif'], 'mask: var(--m-%s) center / contain no-repeat' % m['motif']]
        b.append(rule('%s .pc-chapter > h1::after' % doc, decl))
    if art.get('kicker') in KICKERS and art.get('kicker_doc', True):
        b.append(rule('%s .pc-kicker' % doc, KICKERS[art['kicker']]))
    return '\n'.join(x for x in a if x) + '\n', '\n'.join(b) + '\n'


def sheet(out):
    css, cells = [], []
    for n, (view, body) in SHAPES.items():
        css.append('.m-%s{-webkit-mask:%s center/contain no-repeat;mask:%s center/contain no-repeat}' % (n, svg_uri(view, body), svg_uri(view, body)))
        cells.append('<figure><div class="m-%s"></div><figcaption>%s</figcaption></figure>' % (n, n))
    for n, (view, body, tile) in PATTERNS.items():
        css.append('.p-%s{-webkit-mask:%s 0 0/%dpx %dpx repeat;mask:%s 0 0/%dpx %dpx repeat}' % (n, svg_uri(view, body), tile, tile, svg_uri(view, body), tile, tile))
        cells.append('<figure><div class="p-%s"></div><figcaption>%s (pattern)</figcaption></figure>' % (n, n))
    page = ('<!doctype html><meta charset="utf-8"><title>Motifs</title><style>body{font:14px system-ui;margin:24px;background:#fff;color:#16181d}'
            'main{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:16px}figure{margin:0}'
            'figure div{height:110px;background:#3b5bdb}figcaption{margin-top:6px;color:#4a505c}%s</style><h1>Motifs</h1><main>%s</main>'
            % (''.join(css), ''.join(cells)))
    open(out, 'w', encoding='utf-8').write(page)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--sheet', metavar='OUT.html')
    a = ap.parse_args()
    if a.sheet:
        sheet(a.sheet)
        print('wrote', a.sheet)
    if a.list or not a.sheet:
        print('Shapes: ' + ', '.join(SHAPES))
        print('Patterns: ' + ', '.join(PATTERNS))
        for k, v in OTHER.items():
            print('%s: %s' % (k, v))
        print('Parameters: ' + PARAMS)
        print('Deck slots: ' + ', '.join(DECK_SLOTS) + '; document slots: cover, opener, mark')
        print('Kickers: ' + ', '.join(list(KICKERS) + ['dash']) + '; cards: ' + ', '.join(CARDS))


if __name__ == '__main__':
    sys.exit(main())
