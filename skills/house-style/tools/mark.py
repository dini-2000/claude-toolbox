#!/usr/bin/env python3
"""Marks (logos, emblems, icons, badges) built from exact geometric shapes on a grid, for the craft loop
(tools/art_loop.py renders them; SKILL.md "Drawn art" gives the method).

    import sys; sys.path.insert(0, '<kit>/tools'); from mark import *
    m = Mark(24)                                   # a 24-unit grid: viewBox 0 0 24 24
    m.add(circle(12, 12, 10), 'accent')            # fill: a palette key, a hex colour, or 'ink' (currentColor)
    m.cut(circle(12, 12, 5))                       # knock a shape out of everything drawn so far
    m.cut(line(5, 19, 19, 5, 2), gap=1)            # the same, plus a 1-unit gap round the shape
    m.add(line(5, 19, 19, 5, 2), 'accent-2')       # ...then draw the shape inside its gap
    m.save('mark.svg', palette={'accent': '#1D4E9E', 'accent-2': '#D7261E'})
    m.save('mark-mono.svg', mono=True)             # every fill in currentColor

Shapes: circle, ellipse, rect (corner radius r: one value or four, clockwise from top left), poly (any polygon,
its corners rounded with true arcs by r), regular, star, sector (a pie slice), band (a thick arc with butt or
round ends), ring, line and polyline (strokes turned into outlines), leaf (two arcs between two points), drop,
squircle, and text (a kit font as outlines, kerned from the font's own tables; Latin, no ligatures). Shapes move,
rotate, scale and mirror, and `a + b` joins two shapes into one: every outer contour runs clockwise and every
hole the other way, so the nonzero fill rule draws the union. radial(shape, n) repeats a shape round a centre;
overshoot(shape) enlarges a round shape slightly so it looks as big as a square one. `a - b` makes b a hole in a
(b must lie inside a); Mark.cut knocks out anything, with a gap. save_shape(shape, 'x.svg', w) writes one shape for a
theme's art recipe, where it takes the theme's colours in light and dark.

Angles are degrees clockwise from 3 o'clock, since SVG's y axis runs down. Units are grid units: keep key points
on the grid or on its halves. A cut is drawn as an SVG mask, which browsers and Chrome's PDFs draw exactly.
"""
import json
import math
import re
import struct
import sys
from functools import lru_cache
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / 'tools'))

__all__ = ['Shape', 'Mark', 'circle', 'ellipse', 'rect', 'poly', 'regular', 'star', 'sector', 'band', 'ring',
           'line', 'polyline', 'leaf', 'drop', 'squircle', 'text', 'text_width', 'radial', 'overshoot', 'union']


def _num(v):
    s = ('%.3f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '', '-') else s


def _arc(cx, cy, rx, ry, a0, a1):
    """Cubic segments of an elliptical arc from angle a0 to a1 (degrees, clockwise from 3 o'clock)."""
    n = max(1, math.ceil(abs(a1 - a0) / 90 - 1e-9))
    out = []
    for i in range(n):
        t0 = math.radians(a0 + (a1 - a0) * i / n)
        t1 = math.radians(a0 + (a1 - a0) * (i + 1) / n)
        h = 4 / 3 * math.tan((t1 - t0) / 4)
        c1 = (cx + rx * (math.cos(t0) - h * math.sin(t0)), cy + ry * (math.sin(t0) + h * math.cos(t0)))
        c2 = (cx + rx * (math.cos(t1) + h * math.sin(t1)), cy + ry * (math.sin(t1) - h * math.cos(t1)))
        out.append(('C', c1, c2, (cx + rx * math.cos(t1), cy + ry * math.sin(t1))))
    return out


def _pt(cx, cy, r, a):
    return (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))


def _flat(contour, steps=12):
    """A contour as a list of points (cubics sampled)."""
    pts = [contour[0][1]]
    for s in contour[1:]:
        if s[0] == 'L':
            pts.append(s[1])
        else:
            p0, (c1, c2, p) = pts[-1], s[1:]
            for k in range(1, steps + 1):
                t = k / steps
                u = 1 - t
                pts.append((u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p[0],
                            u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p[1]))
    return pts


def _area(contour):
    """Signed area; positive when the contour runs clockwise on screen (y down)."""
    p = _flat(contour)
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(p, p[1:] + p[:1])) / 2


def _reverse(contour):
    c = list(contour)
    first, last = c[0][1], c[-1][-1]
    if math.dist(first, last) > 1e-9:
        c.append(('L', first))
    starts = [c[0][1]] + [s[-1] for s in c[1:-1]]
    out = [('M', c[-1][-1])]
    for s, q in zip(reversed(c[1:]), reversed(starts)):
        out.append(('L', q) if s[0] == 'L' else ('C', s[2], s[1], q))
    return out


def _cw(contour):
    return contour if _area(contour) >= 0 else _reverse(contour)


class Shape:
    """Closed contours, each a list of segments: ('M', p), then ('L', p) or ('C', c1, c2, p)."""

    def __init__(self, contours=None):
        self.contours = [c for c in (contours or []) if len(c) > 1]

    def __add__(self, other):
        return Shape(self.contours + other.contours)

    def __sub__(self, other):
        """A hole: other, reversed, inside this shape. It must lie wholly inside one filled part (else use Mark.cut)."""
        return Shape(self.contours + other.reverse().contours)

    def _map(self, f):
        return Shape([[(s[0],) + tuple(f(p) for p in s[1:]) for s in c] for c in self.contours])

    def bbox(self):
        pts = [p for c in self.contours for p in _flat(c)]
        if not pts:
            return (0, 0, 0, 0)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def center(self):
        x0, y0, x1, y1 = self.bbox()
        return ((x0 + x1) / 2, (y0 + y1) / 2)

    def move(self, dx, dy):
        return self._map(lambda p: (p[0] + dx, p[1] + dy))

    def rotate(self, deg, cx=None, cy=None):
        if cx is None:
            cx, cy = self.center()
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        return self._map(lambda p: (cx + (p[0] - cx) * ca - (p[1] - cy) * sa, cy + (p[0] - cx) * sa + (p[1] - cy) * ca))

    def scale(self, sx, sy=None, cx=None, cy=None):
        sy = sx if sy is None else sy
        if cx is None:
            cx, cy = self.center()
        s = self._map(lambda p: (cx + (p[0] - cx) * sx, cy + (p[1] - cy) * sy))
        return s.reverse() if sx * sy < 0 else s

    def mirror(self, axis='x', at=None):
        """axis 'x' flips left to right about the line x = at (the shape's centre by default); 'y' flips top to bottom."""
        cx, cy = self.center()
        if axis == 'x':
            return self.scale(-1, 1, cx if at is None else at, cy)
        return self.scale(1, -1, cx, cy if at is None else at)

    def reverse(self):
        return Shape([_reverse(c) for c in self.contours])

    def d(self):
        out = []
        for c in self.contours:
            for s in c:
                out.append(s[0] + ' '.join('%s %s' % (_num(p[0]), _num(p[1])) for p in s[1:]))
            out.append('Z')
        return ''.join(out)


def union(*shapes):
    out = Shape()
    for s in shapes:
        out = out + s
    return out


def ellipse(cx, cy, rx, ry):
    return Shape([[('M', (cx + rx, cy))] + _arc(cx, cy, rx, ry, 0, 360)])


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def rect(x, y, w, h, r=0):
    """A rectangle; r is one corner radius or four (top left, top right, bottom right, bottom left)."""
    tl, tr, br, bl = (r, r, r, r) if isinstance(r, (int, float)) else r
    lim = min(w, h) / 2
    tl, tr, br, bl = (min(max(v, 0), lim) for v in (tl, tr, br, bl))
    c = [('M', (x + tl, y)), ('L', (x + w - tr, y))]
    if tr:
        c += _arc(x + w - tr, y + tr, tr, tr, -90, 0)
    c.append(('L', (x + w, y + h - br)))
    if br:
        c += _arc(x + w - br, y + h - br, br, br, 0, 90)
    c.append(('L', (x + bl, y + h)))
    if bl:
        c += _arc(x + bl, y + h - bl, bl, bl, 90, 180)
    c.append(('L', (x, y + tl)))
    if tl:
        c += _arc(x + tl, y + tl, tl, tl, 180, 270)
    return Shape([c])


def poly(points, r=0):
    """A polygon through the points, each corner rounded by a true arc of radius r (smaller where an edge is short)."""
    pts = [tuple(p) for p in points]
    if sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) < 0:
        pts.reverse()
    if not r:
        return Shape([[('M', pts[0])] + [('L', p) for p in pts[1:]]])
    rs = r if isinstance(r, (list, tuple)) else [r] * len(pts)
    n = len(pts)
    c = []
    for i, p in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % n]
        la, lb = math.dist(a, p), math.dist(b, p)
        u1 = ((a[0] - p[0]) / la, (a[1] - p[1]) / la)
        u2 = ((b[0] - p[0]) / lb, (b[1] - p[1]) / lb)
        th = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        if rs[i] <= 0 or th > math.pi - 1e-6:
            seg = [('L', p)]
        else:
            t = min(rs[i] / math.tan(th / 2), la / 2, lb / 2)
            reff = t * math.tan(th / 2)
            t1 = (p[0] + u1[0] * t, p[1] + u1[1] * t)
            t2 = (p[0] + u2[0] * t, p[1] + u2[1] * t)
            hl = 4 / 3 * math.tan((math.pi - th) / 4) * reff
            seg = [('L', t1), ('C', (t1[0] - u1[0] * hl, t1[1] - u1[1] * hl), (t2[0] - u2[0] * hl, t2[1] - u2[1] * hl), t2)]
        c += seg
    c[0] = ('M', c[0][1])
    return Shape([c])


def regular(cx, cy, r, n, rot=-90, rr=0):
    """A regular polygon of n sides, a corner at angle rot (straight up by default), corners rounded by rr."""
    return poly([_pt(cx, cy, r, rot + 360 * k / n) for k in range(n)], rr)


def star(cx, cy, r1, r2, n=5, rot=-90, rr=0):
    """A star of n points, outer radius r1 and inner radius r2."""
    return poly([_pt(cx, cy, r1 if k % 2 == 0 else r2, rot + 180 * k / n) for k in range(2 * n)], rr)


def sector(cx, cy, r, a0, a1):
    """A pie slice from angle a0 to a1."""
    if a1 < a0:
        a0, a1 = a1, a0
    return Shape([[('M', (cx, cy)), ('L', _pt(cx, cy, r, a0))] + _arc(cx, cy, r, r, a0, a1)])


def ring(cx, cy, r_out, r_in):
    return circle(cx, cy, r_out) + circle(cx, cy, r_in).reverse()


def band(cx, cy, r, w, a0, a1, cap='butt'):
    """A thick arc: centre line of radius r, width w, from angle a0 to a1; cap 'butt' or 'round'."""
    if a1 < a0:
        a0, a1 = a1, a0
    if a1 - a0 >= 360 - 1e-9:
        return ring(cx, cy, r + w / 2, r - w / 2)
    ro, ri, h = r + w / 2, r - w / 2, w / 2
    c = [('M', _pt(cx, cy, ro, a0))] + _arc(cx, cy, ro, ro, a0, a1)
    e = _pt(cx, cy, r, a1)
    c += _arc(e[0], e[1], h, h, a1, a1 + 180) if cap == 'round' else [('L', _pt(cx, cy, ri, a1))]
    c += _arc(cx, cy, ri, ri, a1, a0)
    s = _pt(cx, cy, r, a0)
    c += _arc(s[0], s[1], h, h, a0 + 180, a0 + 360) if cap == 'round' else [('L', _pt(cx, cy, ro, a0))]
    return Shape([_cw(c)])


def line(x1, y1, x2, y2, w, cap='round'):
    """A straight stroke of width w as an outline; cap 'round', 'butt' or 'square'."""
    L = math.dist((x1, y1), (x2, y2))
    if L < 1e-9:
        return circle(x1, y1, w / 2) if cap == 'round' else Shape()
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    if cap == 'square':
        x1, y1, x2, y2 = x1 - ux * w / 2, y1 - uy * w / 2, x2 + ux * w / 2, y2 + uy * w / 2
    nx, ny, h = uy, -ux, w / 2
    au = math.degrees(math.atan2(uy, ux))
    c = [('M', (x1 + nx * h, y1 + ny * h)), ('L', (x2 + nx * h, y2 + ny * h))]
    c += _arc(x2, y2, h, h, au - 90, au + 90) if cap == 'round' else [('L', (x2 - nx * h, y2 - ny * h))]
    c.append(('L', (x1 - nx * h, y1 - ny * h)))
    if cap == 'round':
        c += _arc(x1, y1, h, h, au + 90, au + 270)
    return Shape([_cw(c)])


def polyline(points, w, cap='round', closed=False):
    """A stroke through the points with round joins: segments plus a disc at each joint."""
    pts = [tuple(p) for p in points] + ([tuple(points[0])] if closed else [])
    out = Shape()
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        out = out + line(a[0], a[1], b[0], b[1], w, 'butt')
    joints = pts[1:-1] + ([pts[0]] if closed else [])
    if cap == 'round' and not closed:
        joints += [pts[0], pts[-1]]
    for p in joints:
        out = out + circle(p[0], p[1], w / 2)
    return out


def leaf(x1, y1, x2, y2, bulge=.5):
    """A leaf or lens: two circular arcs from point 1 to point 2, each bulging out by bulge x half the distance."""
    c = math.dist((x1, y1), (x2, y2))
    s = bulge * c / 2
    R = (c * c / 4 + s * s) / (2 * s)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    nx, ny = -(y2 - y1) / c, (x2 - x1) / c

    def ang(o, p):
        return math.degrees(math.atan2(p[1] - o[1], p[0] - o[0]))

    contour = [('M', (x1, y1))]
    for sign, pa, pb in ((1, (x1, y1), (x2, y2)), (-1, (x2, y2), (x1, y1))):
        o = (mx - sign * nx * (R - s), my - sign * ny * (R - s))
        top = (mx + sign * nx * s, my + sign * ny * s)
        a, b, m = ang(o, pa), ang(o, pb), ang(o, top)
        cw = (b - a) % 360
        contour += _arc(o[0], o[1], R, R, a, a + cw if (m - a) % 360 < cw else a - (360 - cw))
    return Shape([_cw(contour)])


def drop(cx, cy, r, tip):
    """A drop: a circle of radius r at (cx, cy) drawn to a point tip units above its centre."""
    if tip <= r:
        return circle(cx, cy, r)
    b = math.degrees(math.acos(r / tip))
    c = [('M', (cx, cy - tip)), ('L', _pt(cx, cy, r, -90 + b))] + _arc(cx, cy, r, r, -90 + b, 270 - b)
    return Shape([_cw(c)])


def squircle(cx, cy, w, h=None, n=4.0):
    """A superellipse |x/a|^n + |y/b|^n = 1 (n 4 or 5 for the soft square of app icons), smooth cubic outline."""
    h = w if h is None else h
    a, b, N = w / 2, h / 2, 64
    pts = []
    for k in range(N):
        t = 2 * math.pi * k / N
        ct, st = math.cos(t), math.sin(t)
        pts.append((cx + a * math.copysign(abs(ct) ** (2 / n), ct), cy + b * math.copysign(abs(st) ** (2 / n), st)))
    c = [('M', pts[0])]
    for i in range(N):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % N], pts[(i + 2) % N]
        c.append(('C', (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6),
                  (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6), p2))
    return Shape([_cw(c)])


def radial(shape, n, cx, cy, start=0):
    """n copies of a shape turned evenly round (cx, cy)."""
    return union(*[shape.rotate(start + 360 * k / n, cx, cy) for k in range(n)])


def overshoot(shape, f=.015):
    """Enlarge a round or pointed shape by f (1.5% by default) about its centre, so it looks as big as a square."""
    return shape.scale(1 + f)


# ---- text as outlines, from the kit's TrueType files ----

class _Font:
    def __init__(self, path):
        import fontinfo
        data = Path(path).read_bytes()
        self.t = t = fontinfo.tables(data)
        self.upm = struct.unpack('>H', t['head'][18:20])[0]
        self.long_loca = struct.unpack('>h', t['head'][50:52])[0] == 1
        self.nglyphs = struct.unpack('>H', t['maxp'][4:6])[0]
        self.nmetrics = struct.unpack('>H', t['hhea'][34:36])[0]
        self.cmap = self._cmap(t['cmap'])
        self.kern = self._gpos_kern(t.get('GPOS')) or self._kern_table(t.get('kern'))
        self.cache = {}

    def _cmap(self, cm):
        n = struct.unpack('>H', cm[2:4])[0]
        best = None
        for i in range(n):
            pid, eid, off = struct.unpack('>HHI', cm[4 + 8 * i: 12 + 8 * i])
            fmt = struct.unpack('>H', cm[off:off + 2])[0]
            rank = {(3, 10): 3, (0, 4): 3, (3, 1): 2, (0, 3): 2}.get((pid, eid), 0) + (1 if fmt in (4, 12) else -9)
            if best is None or rank > best[0]:
                best = (rank, off, fmt)
        _, off, fmt = best
        out = {}
        if fmt == 4:
            seg2 = struct.unpack('>H', cm[off + 6: off + 8])[0]
            seg = seg2 // 2
            ends = struct.unpack('>%dH' % seg, cm[off + 14: off + 14 + seg2])
            base = off + 16 + seg2
            starts = struct.unpack('>%dH' % seg, cm[base: base + seg2])
            deltas = struct.unpack('>%dh' % seg, cm[base + seg2: base + 2 * seg2])
            ro_at = base + 2 * seg2
            ros = struct.unpack('>%dH' % seg, cm[ro_at: ro_at + seg2])
            for i in range(seg):
                for ch in range(starts[i], ends[i] + 1):
                    if ch == 0xFFFF:
                        continue
                    if ros[i] == 0:
                        g = (ch + deltas[i]) & 0xFFFF
                    else:
                        at = ro_at + 2 * i + ros[i] + 2 * (ch - starts[i])
                        g = struct.unpack('>H', cm[at: at + 2])[0]
                        g = (g + deltas[i]) & 0xFFFF if g else 0
                    out[ch] = g
        elif fmt == 12:
            groups = struct.unpack('>I', cm[off + 12: off + 16])[0]
            for i in range(groups):
                s, e, g = struct.unpack('>III', cm[off + 16 + 12 * i: off + 28 + 12 * i])
                for k in range(e - s + 1):
                    out[s + k] = g + k
        return out

    def advance(self, g):
        hm = self.t['hmtx']
        i = min(g, self.nmetrics - 1)
        return struct.unpack('>H', hm[4 * i: 4 * i + 2])[0]

    def _coverage(self, d, off):
        fmt = struct.unpack('>H', d[off:off + 2])[0]
        cov = {}
        if fmt == 1:
            n = struct.unpack('>H', d[off + 2: off + 4])[0]
            for i, g in enumerate(struct.unpack('>%dH' % n, d[off + 4: off + 4 + 2 * n])):
                cov[g] = i
        else:
            n = struct.unpack('>H', d[off + 2: off + 4])[0]
            for i in range(n):
                s, e, si = struct.unpack('>HHH', d[off + 4 + 6 * i: off + 10 + 6 * i])
                for g in range(s, e + 1):
                    cov[g] = si + g - s
        return cov

    def _classdef(self, d, off):
        fmt = struct.unpack('>H', d[off:off + 2])[0]
        cls = {}
        if fmt == 1:
            start, n = struct.unpack('>HH', d[off + 2: off + 6])
            for i, c in enumerate(struct.unpack('>%dH' % n, d[off + 6: off + 6 + 2 * n])):
                cls[start + i] = c
        else:
            n = struct.unpack('>H', d[off + 2: off + 4])[0]
            for i in range(n):
                s, e, c = struct.unpack('>HHH', d[off + 4 + 6 * i: off + 10 + 6 * i])
                for g in range(s, e + 1):
                    cls[g] = c
        return cls

    def _gpos_kern(self, d):
        """Pair kerning from GPOS lookups of the 'kern' feature: a function (left, right) -> x advance change."""
        if not d:
            return None
        _, _, _, fl, ll = struct.unpack('>HHHHH', d[:10])
        nf = struct.unpack('>H', d[fl: fl + 2])[0]
        idx = set()
        for i in range(nf):
            tag, off = struct.unpack('>4sH', d[fl + 2 + 6 * i: fl + 8 + 6 * i])
            if tag == b'kern':
                n = struct.unpack('>H', d[fl + off + 2: fl + off + 4])[0]
                idx.update(struct.unpack('>%dH' % n, d[fl + off + 4: fl + off + 4 + 2 * n]))
        nl = struct.unpack('>H', d[ll: ll + 2])[0]
        lookups = struct.unpack('>%dH' % nl, d[ll + 2: ll + 2 + 2 * nl])
        subs = []
        for li in sorted(idx):
            lo = ll + lookups[li]
            typ, _, n = struct.unpack('>HHH', d[lo: lo + 6])
            group = []
            for so in struct.unpack('>%dH' % n, d[lo + 6: lo + 6 + 2 * n]):
                st, at = typ, lo + so
                if typ == 9:
                    _, st, ext = struct.unpack('>HHI', d[at: at + 8])
                    at += ext
                if st == 2:
                    group.append(at)
            subs.append(group)

        def vsize(vf):
            return 2 * bin(vf).count('1')

        def xadv(at, vf):
            if not vf & 4:
                return 0
            return struct.unpack('>h', d[at + 2 * bin(vf & 3).count('1'): at + 2 * bin(vf & 3).count('1') + 2])[0]

        parsed = []
        for group in subs:
            pg = []
            for at in group:
                fmt, cov, vf1, vf2 = struct.unpack('>HHHH', d[at: at + 8])
                coverage = self._coverage(d, at + cov)
                if fmt == 1:
                    n = struct.unpack('>H', d[at + 8: at + 10])[0]
                    sets = struct.unpack('>%dH' % n, d[at + 10: at + 10 + 2 * n])
                    pg.append(('1', coverage, at, sets, vf1, vf2))
                elif fmt == 2:
                    c1, c2, n1, n2 = struct.unpack('>HHHH', d[at + 8: at + 16])
                    pg.append(('2', coverage, at, (self._classdef(d, at + c1), self._classdef(d, at + c2), n2), vf1, vf2))
            parsed.append(pg)

        def kern(a, b):
            total = 0
            for pg in parsed:
                for fmt, coverage, at, extra, vf1, vf2 in pg:
                    if a not in coverage:
                        continue
                    rec = 2 + vsize(vf1) + vsize(vf2)
                    if fmt == '1':
                        ps = at + extra[coverage[a]]
                        n = struct.unpack('>H', d[ps: ps + 2])[0]
                        hit = None
                        for k in range(n):
                            r = ps + 2 + rec * k
                            if struct.unpack('>H', d[r: r + 2])[0] == b:
                                hit = r + 2
                                break
                        if hit is None:
                            continue
                        total += xadv(hit, vf1)
                    else:
                        cd1, cd2, n2 = extra
                        r = at + 16 + (cd1.get(a, 0) * n2 + cd2.get(b, 0)) * (vsize(vf1) + vsize(vf2))
                        total += xadv(r, vf1)
                    break
            return total
        return kern

    def _kern_table(self, d):
        if not d:
            return lambda a, b: 0
        pairs = {}
        n = struct.unpack('>H', d[2:4])[0]
        at = 4
        for _ in range(n):
            _, length, cov = struct.unpack('>HHH', d[at: at + 6])
            if cov >> 8 == 0:
                np_ = struct.unpack('>H', d[at + 6: at + 8])[0]
                for k in range(np_):
                    l_, r_, v = struct.unpack('>HHh', d[at + 14 + 6 * k: at + 20 + 6 * k])
                    pairs[(l_, r_)] = v
            at += length
        return lambda a, b: pairs.get((a, b), 0)

    def glyph(self, g):
        """Contours of glyph g in font units (y up): lists of (x, y, on_curve)."""
        if g in self.cache:
            return self.cache[g]
        loca, glyf = self.t['loca'], self.t['glyf']
        if self.long_loca:
            a, b = struct.unpack('>II', loca[4 * g: 4 * g + 8])
        else:
            a, b = (2 * v for v in struct.unpack('>HH', loca[2 * g: 2 * g + 4]))
        out = []
        if b > a:
            d = glyf[a:b]
            nc = struct.unpack('>h', d[:2])[0]
            if nc >= 0:
                ends = struct.unpack('>%dH' % nc, d[10: 10 + 2 * nc])
                npts = ends[-1] + 1 if nc else 0
                at = 10 + 2 * nc
                il = struct.unpack('>H', d[at: at + 2])[0]
                at += 2 + il
                flags = []
                while len(flags) < npts:
                    f = d[at]
                    at += 1
                    flags.append(f)
                    if f & 8:
                        r = d[at]
                        at += 1
                        flags += [f] * r
                coords = []
                for short, same in ((2, 16), (4, 32)):
                    v, vals = 0, []
                    for f in flags:
                        if f & short:
                            dv = d[at]
                            at += 1
                            v += dv if f & same else -dv
                        elif not f & same:
                            v += struct.unpack('>h', d[at: at + 2])[0]
                            at += 2
                        vals.append(v)
                    coords.append(vals)
                s = 0
                for e in ends:
                    out.append([(coords[0][i], coords[1][i], bool(flags[i] & 1)) for i in range(s, e + 1)])
                    s = e + 1
            else:
                at = 10
                while True:
                    fl, gi = struct.unpack('>HH', d[at: at + 4])
                    at += 4
                    if fl & 1:
                        dx, dy = struct.unpack('>hh', d[at: at + 4])
                        at += 4
                    else:
                        dx, dy = struct.unpack('>bb', d[at: at + 2])
                        at += 2
                    if not fl & 2:
                        dx = dy = 0
                    m = (1, 0, 0, 1)
                    if fl & 8:
                        s = struct.unpack('>h', d[at: at + 2])[0] / 16384
                        at += 2
                        m = (s, 0, 0, s)
                    elif fl & 0x40:
                        sx, sy = struct.unpack('>hh', d[at: at + 4])
                        at += 4
                        m = (sx / 16384, 0, 0, sy / 16384)
                    elif fl & 0x80:
                        m = tuple(v / 16384 for v in struct.unpack('>hhhh', d[at: at + 8]))
                        at += 8
                    for c in self.glyph(gi):
                        out.append([(m[0] * x + m[2] * y + dx, m[1] * x + m[3] * y + dy, on) for x, y, on in c])
                    if not fl & 0x20:
                        break
        self.cache[g] = out
        return out


@lru_cache(None)
def _font(family, weight=400, italic=False):
    index = json.loads((KIT / 'fonts' / 'fonts.json').read_text())
    if family not in index:
        raise KeyError('the kit holds no font family %r (tools/make_theme.py --fonts lists them)' % family)
    faces = index[family]['faces']
    want = 'italic' if italic else 'normal'
    pool = [f for f in faces if f['style'] == want] or faces
    face = min(pool, key=lambda f: abs(f['weight'] - weight))
    return _Font(KIT / 'fonts' / face['file'])


def _glyph_contours(contours, ox, oy, k):
    """TrueType quadratic contours placed at (ox, oy) baseline, scale k, y flipped, as cubic segment lists."""
    out = []
    for c in contours:
        if not c:
            continue
        pts = [((ox + x * k), (oy - y * k), on) for x, y, on in c]
        if not any(p[2] for p in pts):
            a, b = pts[0], pts[1]
            pts.insert(1, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, True))
        start = next(i for i, p in enumerate(pts) if p[2])
        pts = pts[start:] + pts[:start]
        seg = [('M', pts[0][:2])]
        cur, ctrl = pts[0][:2], None
        for p in pts[1:] + [pts[0]]:
            if p[2]:
                if ctrl is None:
                    seg.append(('L', p[:2]))
                else:
                    seg.append(('C', (cur[0] + 2 / 3 * (ctrl[0] - cur[0]), cur[1] + 2 / 3 * (ctrl[1] - cur[1])),
                                (p[0] + 2 / 3 * (ctrl[0] - p[0]), p[1] + 2 / 3 * (ctrl[1] - p[1])), p[:2]))
                cur, ctrl = p[:2], None
            else:
                if ctrl is not None:
                    mid = ((ctrl[0] + p[0]) / 2, (ctrl[1] + p[1]) / 2)
                    seg.append(('C', (cur[0] + 2 / 3 * (ctrl[0] - cur[0]), cur[1] + 2 / 3 * (ctrl[1] - cur[1])),
                                (mid[0] + 2 / 3 * (ctrl[0] - mid[0]), mid[1] + 2 / 3 * (ctrl[1] - mid[1])), mid))
                    cur = mid
                ctrl = p[:2]
        out.append(_reverse(seg))
    return out


def _layout(s, size, family, weight, italic, track, kern):
    f = _font(family, weight, italic)
    k = size / f.upm
    gl = [f.cmap.get(ord(ch), 0) for ch in s]
    x, placed = 0.0, []
    for i, g in enumerate(gl):
        placed.append((g, x))
        x += f.advance(g) * k + track * size / 1000
        if kern and i + 1 < len(gl):
            x += f.kern(g, gl[i + 1]) * k
    width = x - (track * size / 1000 if gl else 0)
    return f, k, placed, width


def text_width(s, size, family='Outfit', weight=700, italic=False, track=0, kern=True):
    return _layout(s, size, family, weight, italic, track, kern)[3]


def text(s, x, y, size, family='Outfit', weight=700, italic=False, track=0, kern=True, anchor='start'):
    """A line of text in a kit font as outlines, its baseline at y. track is in thousandths of the size (as in
    design tools); anchor 'start', 'middle' or 'end' places x. Kerning comes from the font's GPOS or kern table."""
    f, k, placed, width = _layout(s, size, family, weight, italic, track, kern)
    x0 = x - {'start': 0, 'middle': width / 2, 'end': width}[anchor]
    out = []
    for g, gx in placed:
        out += _glyph_contours(f.glyph(g), x0 + gx, y, k)
    return Shape(out)


# ---- the mark ----

def save_shape(shape, path, w=24, h=None):
    """One shape as a one-colour SVG on a w x h grid, for a theme's art recipe: the style spec's "art": {"shapes":
    {"sprig": "sprig.svg"}} makes "sprig" a motif in any colour token (make_theme.py --spec reads the file)."""
    h = w if h is None else h
    Path(path).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" data-grid="%s %s"><path d="%s"/></svg>\n'
                          % (_num(w), _num(h), _num(w), _num(h), shape.d()))
    return path


class Mark:
    """A mark on a w x h grid: shapes added in order, each in one colour, and cuts that knock out what came before."""

    def __init__(self, w=24, h=None):
        self.w, self.h = w, (w if h is None else h)
        self.ops = []

    def add(self, shape, color='ink', opacity=1):
        self.ops.append(('add', shape, color, opacity))
        return self

    def cut(self, shape, gap=0):
        self.ops.append(('cut', shape, gap))
        return self

    def svg(self, palette=None, mono=False, title=None, pad=0):
        palette = palette or {}

        def fill(c):
            if mono or c == 'ink':
                return 'currentColor'
            if c in palette:
                return palette[c]
            if re.fullmatch(r'#[0-9a-fA-F]{3,8}', c):
                return c
            raise KeyError('no colour for %r: pass palette={%r: "#..."}' % (c, c))

        W, H = self.w, self.h
        body, masks, n = '', [], 0
        for op in self.ops:
            if op[0] == 'add':
                _, shape, color, opacity = op
                body += '<path d="%s" fill="%s"%s/>' % (shape.d(), fill(color),
                                                        '' if opacity == 1 else ' fill-opacity="%s"' % _num(opacity))
            elif body:
                _, shape, gap = op
                n += 1
                stroke = (' stroke="#000" stroke-width="%s" stroke-linejoin="round"' % _num(2 * gap)) if gap else ''
                masks.append('<mask id="cut%d" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
                             '<rect x="%s" y="%s" width="%s" height="%s" fill="#fff"/><path d="%s" fill="#000"%s/></mask>'
                             % (n, _num(-W), _num(-H), _num(3 * W), _num(3 * H), _num(-W), _num(-H), _num(3 * W),
                                _num(3 * H), shape.d(), stroke))
                body = '<g mask="url(#cut%d)">%s</g>' % (n, body)
        view = '%s %s %s %s' % (_num(-pad), _num(-pad), _num(W + 2 * pad), _num(H + 2 * pad))
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" data-grid="%s %s">%s%s%s</svg>\n'
                % (view, _num(W), _num(H), '<title>%s</title>' % title if title else '',
                   '<defs>%s</defs>' % ''.join(masks) if masks else '', body))

    def save(self, path, **kw):
        Path(path).write_text(self.svg(**kw))
        return path
