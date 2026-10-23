#!/usr/bin/env python3
"""The craft loop for drawn art: render each candidate the ways people will see it, measure what the eye can miss,
then look, refine and run it again (SKILL.md "Drawn art").

    python3 tools/art_loop.py a.svg b.svg c.svg -o <dir> [--round 2] [--theme <id>] [--word "Name" --font Outfit]
    python3 tools/art_loop.py cover.svg -o <dir> --kind art
    python3 tools/art_loop.py final.svg -o <dir> --export

Marks (the default) get a contact sheet, <dir>/sheet-r<round>.png, with a row per candidate: 256 px on the light
and dark grounds; 64, 32, 24 and 16 px on both; one colour on both; the 16 and 32 px renders blown up pixel for
pixel; an app icon, a browser tab and, with --word, a lockup. Beside it <name>-1024.png (zoom in on joins, curves
and gaps) and <name>-build.png (the mark over its grid, read from the SVG's data-grid, with its centre lines, the
ink's box in red and its centre of weight). The report, printed and saved as report-r<round>.txt, gives the ink's
margins, how far its weight sits off centre, its mirror symmetry, how much of it vanishes or fills in at 16 and
32 px, and each colour's contrast on both grounds. FLAG lines are worth fixing before anyone sees the mark.

--kind art is for cover art and illustrations: 960, 480 and 240 px wide on both grounds and in one colour, with
the weight, coverage and colour measures. --export writes the finished mark as transparent PNGs at 16 to 1024 px
and favicon.ico. --theme takes the grounds, ink and accent from a kit theme (its default palette), so cover art is
judged on the ground it will sit on.

SVGs may use currentColor for ink: the sheet sets it to each ground's ink, and the one-colour tiles force every
fill and stroke to it (masks and clip paths keep theirs).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / 'tools'))
import chrome  # noqa: E402

GROUNDS = {'light': ('#FFFFFF', '#14161A'), 'dark': ('#14161A', '#F4F4F2'), 'accent': '#2B59C3'}
CSS = ('*{box-sizing:border-box}html,body{margin:0;background:%s;font:13px/1.3 -apple-system,Helvetica,Arial,'
       'sans-serif;color:#333}.t{position:absolute;overflow:hidden}.t>svg{width:100%%;height:100%%;display:block}'
       '.p{position:absolute;border-radius:6px}.l{position:absolute;font-size:12px;color:#555;white-space:nowrap}'
       '.n{position:absolute;font-weight:600;font-size:14px;color:#222}'
       '.mono svg :not(defs, defs *, mask, mask *, clipPath, clipPath *, pattern *):not([fill="none"])'
       '{fill:currentColor!important}'
       '.mono svg :not(defs *, mask *, clipPath *)[stroke]:not([stroke="none"]){stroke:currentColor!important}')


def lum(h):
    h = h.lstrip('#')
    if len(h) in (3, 4):
        h = ''.join(c * 2 for c in h[:3])
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4  # noqa: E731
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def theme_grounds(tid):
    p = Path(tid)
    if not p.suffix:
        p = KIT / 'themes' / tid / 'theme.json'
    t = json.loads(p.read_text())
    pal = t['palettes'][t['defaults']['palette']]
    return {'light': (t['modes']['light']['bg'], t['modes']['light']['ink']),
            'dark': (t['modes']['dark']['bg'], t['modes']['dark']['ink']), 'accent': pal['light']['accent']}


class Art:
    """One candidate SVG, with its ids made unique for the sheet."""

    def __init__(self, path, k):
        self.path = Path(path)
        self.name = self.path.stem
        src = self.path.read_text()
        src = re.sub(r'<\?xml[^>]*\?>|<!DOCTYPE[^>]*>|<!--.*?-->', '', src, flags=re.S).strip()
        m = re.search(r'<svg\b[^>]*>', src)
        if not m:
            raise SystemExit('%s: no <svg> element' % path)
        head = m.group(0)
        vb = re.search(r'viewBox="([^"]+)"', head)
        if vb:
            self.view = [float(v) for v in re.split(r'[\s,]+', vb.group(1).strip())]
        else:
            w = re.search(r'\bwidth="([\d.]+)', head)
            h = re.search(r'\bheight="([\d.]+)', head)
            if not (w and h):
                raise SystemExit('%s: the <svg> has neither a viewBox nor a width and height' % path)
            self.view = [0, 0, float(w.group(1)), float(h.group(1))]
            head = head.replace('<svg', '<svg viewBox="0 0 %s %s"' % (w.group(1), h.group(1)), 1)
        g = re.search(r'data-grid="([\d.]+)(?:\s+([\d.]+))?"', head)
        self.grid = (float(g.group(1)), float(g.group(2) or g.group(1))) if g else None
        head = re.sub(r'\s(width|height)="[^"]*"', '', head)
        if 'xmlns=' not in head:
            head = head.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        body = src[:m.start()] + head + src[m.end():]
        pre = 'k%d-' % k
        for i in set(re.findall(r'\bid="([^"]+)"', body)):
            q = re.escape(i)
            body = re.sub(r'\bid="%s"' % q, 'id="%s%s"' % (pre, i), body)
            body = re.sub(r'url\(#%s\)' % q, 'url(#%s%s)' % (pre, i), body)
            body = re.sub(r'href="#%s"' % q, 'href="#%s%s"' % (pre, i), body)
        self.svg = body
        outside = re.sub(r'<defs\b.*?</defs>|<mask\b.*?</mask>|<clipPath\b.*?</clipPath>', '', src, flags=re.S)
        self.colors = sorted({c.upper() for c in re.findall(r'(?:fill|stroke|stop-color)\s*[=:]\s*"?\s*(#[0-9a-fA-F]{3,8})\b',
                                                             outside)})
        self.strokes = len([s for s in re.findall(r'stroke\s*[=:]\s*"?([^";\s>]+)', outside) if s != 'none'])
        self.segments = sum(len(re.findall(r'[MLCQAHVSTZ]', d, re.I)) for d in re.findall(r'\bd="([^"]*)"', outside))

    @property
    def aspect(self):
        return self.view[2] / self.view[3]

    def fit(self, box_w, box_h):
        """Where the viewBox lands inside a box (meet): x, y, w, h in px."""
        s = min(box_w / self.view[2], box_h / self.view[3])
        w, h = self.view[2] * s, self.view[3] * s
        return (box_w - w) / 2, (box_h - h) / 2, w, h


def tile(art, x, y, w, h, bg=None, ink='#000', mono=False):
    style = 'left:%dpx;top:%dpx;width:%dpx;height:%dpx;color:%s%s' % (x, y, w, h, ink, ';background:%s' % bg if bg else '')
    return '<div class="t%s" style="%s">%s</div>' % (' mono' if mono else '', style, art.svg)


def panel(x, y, w, h, bg):
    return '<div class="p" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;background:%s"></div>' % (x, y, w, h, bg)


def label(x, y, s, cls='l'):
    return '<div class="%s" style="left:%dpx;top:%dpx">%s</div>' % (cls, x, y, s)


def shoot(html, w, h, out, transparent=False):
    tmp = Path(tempfile.mkdtemp(prefix='art-loop-'))
    page = tmp / 'sheet.html'
    page.write_text(html)
    cmd = [chrome.need_chrome()] + chrome.FLAGS + ['--force-device-scale-factor=1', '--window-size=%d,%d' % (w, h),
                                                   '--screenshot=%s' % out]
    if transparent:
        cmd.append('--default-background-color=00000000')
    subprocess.run(cmd + [page.as_uri()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180, cwd=tmp)
    page.unlink()
    tmp.rmdir()
    if not Path(out).exists():
        raise SystemExit('Chrome made no screenshot (%s)' % out)
    return Image.open(out).convert('RGBA' if transparent else 'RGB')


def wordmark(word, font, weight, size, color):
    from mark import text, text_width
    w = text_width(word, size, font, weight)
    s = text(word, 0, size * .78, size, font, weight)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 %s %s %s" style="width:%dpx;height:%dpx;display:block">' \
           '<path d="%s" fill="%s"/></svg>' % (-size * .02, w, size, w, size, s.d(), color), w


ROW = 256 + 40
SMALL = (64, 32, 24, 16)
SMALL_X = (10, 86, 130, 166)


def mark_sheet(arts, g, args, out):
    W = 1600
    H = 44 + len(arts) * (ROW + 16)
    (lb, li), (db, di), acc = g['light'], g['dark'], g['accent']
    h = ['<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>' % (CSS % '#E9E9EC')]
    for x, s in ((16, '256 px, light'), (284, '256 px, dark'), (552, '64, 32, 24, 16 px'), (780, 'one colour, 64, 32, 16 px'),
                 (1008, 'pixels: 16 px x8, 32 px x4'), (1284, 'in use')):
        h.append(label(x, 14, s))
    spots = []
    for i, a in enumerate(arts):
        y0 = 44 + i * (ROW + 16)
        y = y0 + 22
        h.append(label(16, y0, a.name, 'n'))
        h.append(tile(a, 16, y, 256, 256, lb, li))
        h.append(tile(a, 284, y, 256, 256, db, di))
        for k, (bg, ink) in enumerate(((lb, li), (db, di))):
            py = y + k * 132
            h.append(panel(552, py, 216, 124, bg))
            for s, sx in zip(SMALL, SMALL_X):
                h.append(tile(a, 552 + sx, py + 62 - s // 2, s, s, None, ink))
            h.append(panel(780, py, 216, 124, bg))
            h.append(tile(a, 780 + 14, py + 30, 64, 64, None, ink, mono=True))
            h.append(tile(a, 780 + 100, py + 46, 32, 32, None, ink, mono=True))
            h.append(tile(a, 780 + 150, py + 54, 16, 16, None, ink, mono=True))
        spots.append(y)
        # in use: app icons on the accent, a browser tab on each ground, a lockup
        h.append('<div class="p" style="left:1284px;top:%dpx;width:96px;height:96px;border-radius:22px;background:%s"></div>' % (y, acc))
        h.append(tile(a, 1284 + 20, y + 20, 56, 56, None, '#FFFFFF', mono=True))
        h.append('<div class="p" style="left:1392px;top:%dpx;width:48px;height:48px;border-radius:11px;background:%s"></div>' % (y + 48, acc))
        h.append(tile(a, 1392 + 10, y + 58, 28, 28, None, '#FFFFFF', mono=True))
        for k, (bar, tab, ink) in enumerate((('#DADCE0', '#FFFFFF', '#202124'), ('#202124', '#35363A', '#E8EAED'))):
            ty = y + 108 + k * 40
            h.append(panel(1284, ty, 300, 34, bar))
            h.append('<div class="p" style="left:1292px;top:%dpx;width:200px;height:28px;border-radius:8px 8px 0 0;background:%s"></div>' % (ty + 6, tab))
            h.append(tile(a, 1302, ty + 12, 16, 16, None, ink))
            h.append('<div class="l" style="left:1326px;top:%dpx;color:%s">%s</div>' % (ty + 13, ink, args.word or a.name))
        if args.word:
            for k, (bg, ink) in enumerate(((lb, li), (db, di))):
                ly = y + 194 + k * 32
                svg, ww = wordmark(args.word, args.font, args.weight, 20, ink)
                h.append(panel(1284, ly, 300, 30, bg))
                h.append(tile(a, 1292, ly + 3, 24, 24, None, ink))
                h.append('<div class="t" style="left:1324px;top:%dpx;width:%dpx;height:20px">%s</div>' % (ly + 5, ww, svg))
    h.append('</body></html>')
    im = shoot(''.join(h), W, H, out)
    # pixel views, blown up from the 16 and 32 px tiles
    for i, y in enumerate(spots):
        for k in (0, 1):
            py = y + k * 132
            for s, sx, z, col in ((16, SMALL_X[3], 8, 0), (32, SMALL_X[1], 4, 1)):
                x0, y1 = 552 + sx, py + 62 - s // 2
                crop = im.crop((x0, y1, x0 + s, y1 + s)).resize((s * z, s * z), Image.NEAREST)
                im.paste(crop, (1008 + col * 132, y + k * 132))
    im.save(out)
    return im


def big_renders(arts, g, outdir):
    """1024 px colour renders, 768 px construction views and 256 px one-colour renders for the measures."""
    (lb, li) = g['light']
    W, RH = 1024 + 16 + 768, 1040
    h = ['<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>' % (CSS % '#FFFFFF')]
    for i, a in enumerate(arts):
        y = i * RH
        h.append(tile(a, 0, y, 1024, 1024, lb, li))
        h.append(tile(a, 1040, y, 768, 768, '#FFFFFF', li))
        h.append(tile(a, 1040, y + 784, 256, 256, '#FFFFFF', '#000000', mono=True))
    h.append('</body></html>')
    im = shoot(''.join(h), W, len(arts) * RH, str(outdir / '_big.png'))
    (outdir / '_big.png').unlink()
    res = []
    for i, a in enumerate(arts):
        y = i * RH
        im.crop((0, y, 1024, y + 1024)).save(outdir / ('%s-1024.png' % a.name))
        mono = im.crop((1040, y + 784, 1296, y + 1040)).convert('L')
        build = im.crop((1040, y, 1808, y + 768))
        res.append((a, mono, build))
    return res


def measure(a, mono, g):
    """Numbers for one mark from its 256 px one-colour render."""
    ox, oy, vw, vh = a.fit(256, 256)
    box = (round(ox), round(oy), round(ox + vw), round(oy + vh))
    m = mono.crop(box)
    W, H = m.size
    px = m.load()
    ink = [(x, y) for y in range(H) for x in range(W) if px[x, y] < 128]
    out, flags = {}, []
    if not ink:
        return {'empty': True}, ['FLAG nothing drawn: the one-colour render is blank']
    n = len(ink)
    xs, ys = [p[0] for p in ink], [p[1] for p in ink]
    x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
    out['ink'] = n / (W * H)
    out['margins'] = (x0 / W, y0 / H, (W - x1) / W, (H - y1) / H)
    cx, cy = sum(xs) / n, sum(ys) / n
    out['weight'] = ((cx - W / 2) / W, (cy - H / 2) / H)
    out['box'] = (x0 / W, y0 / H, x1 / W, y1 / H)
    out['centre'] = (cx / W, cy / H)
    inks = set(ink)
    bx, by = (x0 + x1 - 1), (y0 + y1 - 1)
    lr = sum(1 for (x, y) in ink if (bx - x, y) in inks)
    tb = sum(1 for (x, y) in ink if (x, by - y) in inks)
    out['mirror'] = (lr / n, tb / n)
    def count(im):
        return sum(1 for v in im.getdata() if v < 128)
    for size, s in ((16, 9), (32, 5)):
        k = 256 / max(vw, vh)
        s = max(3, int(round(s * k)) | 1)
        opened = count(m.filter(ImageFilter.MaxFilter(s)).filter(ImageFilter.MinFilter(s)))
        closed = count(m.filter(ImageFilter.MinFilter(s)).filter(ImageFilter.MaxFilter(s)))
        out['thin%d' % size] = max(0, n - opened) / n
        out['gaps%d' % size] = max(0, closed - n) / n
    if min(out['margins']) < .01:
        flags.append('FLAG the ink touches the edge of the canvas: leave clear space round the mark')
    if abs(out['weight'][0]) > .04 or abs(out['weight'][1]) > .04:
        flags.append('FLAG its weight sits %+.0f%% across and %+.0f%% down from the centre: rebalance it or mean it'
                     % (100 * out['weight'][0], 100 * out['weight'][1]))
    if out['ink'] < .08:
        flags.append('FLAG light: ink covers %.0f%% of the canvas, so it will look faint and small beside other marks' % (100 * out['ink']))
    if out['ink'] > .75:
        flags.append('FLAG heavy: ink covers %.0f%% of the canvas' % (100 * out['ink']))
    for axis, v in zip(('left to right', 'top to bottom'), out['mirror']):
        if .93 <= v < .995:
            flags.append('FLAG almost symmetric %s (%.1f%%): make it exact or clearly not' % (axis, 100 * v))
    if out['thin16'] > .02:
        flags.append('FLAG %.0f%% of the ink is thinner than half a pixel at 16 px and will vanish: thicken it or drop it '
                     'from the small version' % (100 * out['thin16']))
    if out['gaps16'] > .03:
        flags.append('FLAG gaps under half a pixel at 16 px will fill in (%.0f%% of the ink): open them or make a small version'
                     % (100 * out['gaps16']))
    if out['thin32'] > .02:
        flags.append('FLAG %.0f%% of the ink vanishes at 32 px' % (100 * out['thin32']))
    for c in a.colors:
        for gname in ('light', 'dark'):
            r = contrast(c, g[gname][0])
            if r < 3:
                flags.append('FLAG %s is %.1f:1 on the %s ground (%s): graphics need 3:1, so make a %s version'
                             % (c, r, gname, g[gname][0], gname))
    if len(a.colors) > 3:
        flags.append('FLAG %d colours: a mark rarely needs more than two or three' % len(a.colors))
    if a.strokes:
        flags.append('FLAG %d strokes: outline them (mark.py line, band, polyline) so they scale with the mark' % a.strokes)
    return out, flags


def build_view(a, build, res, path):
    """The 768 px render with its grid, centre lines, ink box and centre of weight."""
    im = build.convert('RGB')
    d = ImageDraw.Draw(im, 'RGBA')
    ox, oy, vw, vh = a.fit(768, 768)
    gw, gh = a.grid or (a.view[2], a.view[3])
    if a.grid:
        step = 1
        while gw / step > 48:
            step *= 2
        u = vw / gw
        for k in range(0, int(gw / step) + 1):
            x = ox + k * step * u
            d.line([(x, oy), (x, oy + vh)], fill=(0, 120, 255, 40 if k % 4 else 90))
        for k in range(0, int(gh / step) + 1):
            y = oy + k * step * vh / gh
            d.line([(ox, y), (ox + vw, y)], fill=(0, 120, 255, 40 if k % 4 else 90))
    d.line([(ox + vw / 2, oy), (ox + vw / 2, oy + vh)], fill=(0, 120, 255, 140))
    d.line([(ox, oy + vh / 2), (ox + vw, oy + vh / 2)], fill=(0, 120, 255, 140))
    d.rectangle([ox, oy, ox + vw, oy + vh], outline=(0, 120, 255, 140))
    if 'box' in res:
        b = res['box']
        d.rectangle([ox + b[0] * vw, oy + b[1] * vh, ox + b[2] * vw, oy + b[3] * vh], outline=(230, 40, 40, 200), width=2)
        cx, cy = ox + res['centre'][0] * vw, oy + res['centre'][1] * vh
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(230, 40, 40, 230), width=2)
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(230, 40, 40, 230), width=2)
    im.save(path)


def describe(a, res, g):
    if res.get('empty'):
        return '%s: blank' % a.name
    m = res['margins']
    cols = ', '.join('%s %.1f:1 light / %.1f:1 dark' % (c, contrast(c, g['light'][0]), contrast(c, g['dark'][0]))
                     for c in a.colors) or 'currentColor only'
    return ('%s: ink %.0f%% | margins L %.0f T %.0f R %.0f B %.0f %% | weight %+.1f%% across, %+.1f%% down | mirror '
            'L-R %.1f%%, T-B %.1f%% | 16 px: thin %.1f%%, gaps %.1f%% | 32 px: thin %.1f%%, gaps %.1f%% | %s | %d segments'
            % (a.name, 100 * res['ink'], *(100 * v for v in m), 100 * res['weight'][0], 100 * res['weight'][1],
               100 * res['mirror'][0], 100 * res['mirror'][1], 100 * res['thin16'], 100 * res['gaps16'],
               100 * res['thin32'], 100 * res['gaps32'], cols, a.segments))


def art_sheet(arts, g, out):
    (lb, li), (db, di) = g['light'], g['dark']
    rows, y = [], 64
    for a in arts:
        h1 = round(960 / a.aspect)
        rows.append((a, y, h1))
        y += max(h1, round(480 / a.aspect) * 2 + 16) + 40
    W, H = 960 + 16 + 480 + 32, y
    h = ['<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>' % (CSS % '#E9E9EC')]
    h.append(label(16, 14, '960 px, light'))
    h.append(label(992, 14, '480 px dark; 240 px one colour; 120 px'))
    for a, y, h1 in rows:
        h.append(label(16, y - 22, a.name, 'n'))
        h.append(tile(a, 16, y, 960, h1, lb, li))
        h2 = round(480 / a.aspect)
        h.append(tile(a, 992, y, 480, h2, db, di))
        h.append(tile(a, 992, y + h2 + 16, 240, round(240 / a.aspect), lb, li, mono=True))
        h.append(tile(a, 1248, y + h2 + 16, 120, round(120 / a.aspect), lb, li))
    h.append('</body></html>')
    return shoot(''.join(h), W, H, out)


def export(arts, outdir):
    sizes = (16, 32, 48, 64, 128, 180, 192, 256, 512, 1024)
    for a in arts:
        x, h = 0, ['<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>' % (CSS % 'transparent')]
        spots = []
        for s in sizes:
            h.append(tile(a, x, 0, s, s, None, '#000'))
            spots.append((x, s))
            x += s + 8
        h.append('</body></html>')
        im = shoot(''.join(h), x, 1024, str(outdir / '_export.png'), transparent=True)
        (outdir / '_export.png').unlink()
        for x0, s in spots:
            im.crop((x0, 0, x0 + s, s)).save(outdir / ('%s-%d.png' % (a.name, s)))
        im.crop((spots[7][0], 0, spots[7][0] + 256, 256)).save(outdir / ('%s-favicon.ico' % a.name),
                                                               sizes=[(16, 16), (32, 32), (48, 48)])
        print('%s: PNG at %s px and %s-favicon.ico in %s' % (a.name, ', '.join(map(str, sizes)), a.name, outdir))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('svgs', nargs='+')
    ap.add_argument('-o', '--out', required=True, help='folder for the sheet, renders and report')
    ap.add_argument('--round', type=int, default=1, help='round number, kept in the file names so rounds can be compared')
    ap.add_argument('--kind', choices=('mark', 'art'), default='mark')
    ap.add_argument('--theme', help='a kit theme id (or a theme.json) for the grounds, ink and accent')
    ap.add_argument('--word', help='a name to set beside the mark (lockup and browser tab)')
    ap.add_argument('--font', default='Outfit', help='kit font family for --word (default Outfit)')
    ap.add_argument('--weight', type=int, default=700)
    ap.add_argument('--export', action='store_true', help='write transparent PNGs at 16 to 1024 px and favicon.ico')
    args = ap.parse_args()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    g = theme_grounds(args.theme) if args.theme else GROUNDS
    arts = [Art(p, k) for k, p in enumerate(args.svgs)]
    names = [a.name for a in arts]
    if len(set(names)) < len(names):
        raise SystemExit('two candidates share a file name; give each its own')
    if args.export:
        export(arts, outdir)
        return
    tag = 'r%d' % args.round
    sheet = outdir / ('sheet-%s.png' % tag)
    if args.kind == 'art':
        art_sheet(arts, g, str(sheet))
        lines = []
        for a in arts:
            cols = ', '.join('%s %.1f:1 light / %.1f:1 dark' % (c, contrast(c, g['light'][0]), contrast(c, g['dark'][0]))
                             for c in a.colors) or 'currentColor only'
            lines.append('%s: %s | %d colours | %d segments' % (a.name, cols, len(a.colors), a.segments))
    else:
        mark_sheet(arts, g, args, str(sheet))
        lines = []
        for a, mono, build in big_renders(arts, g, outdir):
            res, flags = measure(a, mono, g)
            build_view(a, build, res, outdir / ('%s-build.png' % a.name))
            lines.append(describe(a, res, g))
            lines += ['  ' + f for f in flags]
    report = '\n'.join(lines) + '\n'
    (outdir / ('report-%s.txt' % tag)).write_text(report)
    print(report + 'Sheet: %s' % sheet)
    if args.kind == 'mark':
        print('Renders: <name>-1024.png and <name>-build.png in %s' % outdir)


if __name__ == '__main__':
    main()
