#!/usr/bin/env python3
"""QC a deck the way people receive it: the built single file, alone in its folder, in headless Chrome.

    python3 tools/qc.py <deck.html> [-o OUT] [--formats 4x3,1x1 | all] [--no-sheets]

A deck that still links the kit is built first (as tools/build.py does), once per format asked for; a built file is
checked as it is. For each format, OUT (default: pc-qc/<deck> in the system temp folder) gets deck.html, deck.pdf
(Chrome's print), qc.json and sheet-NN.png, contact sheets of six slides for the look at every slide that no script
replaces. The checks: tools/qc.js measures every slide (content past the edge or taller than the body, cut-off
containers, text over text, crowded chart labels, text out of its box or margins, boxes over boxes, empty parts,
pictures, titles, small text, icons, charts, fonts, script errors); this script adds contrast, measured on the printed
page behind each line of text, and compares the print with one made without scripts, so viewers who block scripts
see the same slides. Prints a summary and exits 1 when anything is found.
"""
import argparse
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import chrome  # noqa: E402

KIT = Path(__file__).resolve().parent.parent
QC_JS = Path(__file__).resolve().parent / 'qc.js'
OUT_RE = re.compile(r'<pre id="pc-qc"[^>]*>(.*?)</pre>', re.S)


# ---------- colour ----------

def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def over(fg, a, bg):
    return tuple(f * a + g * (1 - a) for f, g in zip(fg, bg))


def needed(size, weight):
    """WCAG AA on the stage: 3:1 for large text (32 px, or 24 px at weight 600 and up), else 4.5:1."""
    return 3.0 if size >= 32 or (size >= 24 and weight >= 600) else 4.5


# ---------- pages ----------

def render(pdf, width=None, scale=None):
    """Each page of a PDF as a PIL image, `width` px wide or at `scale` px per point."""
    import fitz
    from PIL import Image
    out = []
    with fitz.open(pdf) as d:
        for p in d:
            z = scale if scale else width / p.rect.width
            pix = p.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
            out.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    return out


def contrast_issues(pdf, data):
    """Contrast of each line of text against what the printed page shows behind it."""
    from PIL import Image, ImageStat
    if not data['slides']:
        return {}
    import fitz
    with fitz.open(pdf) as d:
        if d.page_count != len(data['slides']):
            return {}
        k = data['W'] / d[0].rect.width
    pages = render(pdf, scale=k)
    found = {}
    for s, img in zip(data['slides'], pages):
        said = set()
        worst = 99.0
        for x, y, r, b, R, G, B, A, size, weight, sample in s['lines']:
            box = (max(0, int(x)), max(0, int(y)), min(img.width, int(r + .5)), min(img.height, int(b + .5)))
            if box[2] - box[0] < 4 or box[3] - box[1] < 4:
                continue
            crop = img.crop(box)
            bg = tuple(ImageStat.Stat(crop).median[:3])
            fg = over((R, G, B), A, bg)
            need = needed(size, weight)
            # The pixels clearly apart from the text colour are the background. Edge blends, which lie on the line
            # from the text colour to the plain background, are left out: in a short label such as a page number
            # they are a large share. The background's middle half spread over a wide range of lightness means a
            # picture or pattern sits behind the text: then the darker or lighter quarter counts, whichever is worse.
            step = max(1, int((crop.width * crop.height / 20000) ** 0.5 + 0.999))
            small = crop if step == 1 else crop.resize((max(1, crop.width // step), max(1, crop.height // step)), Image.NEAREST)
            v = [bg[i] - fg[i] for i in range(3)]
            vv = sum(c * c for c in v) or 1

            def blend(q):
                d = [q[i] - fg[i] for i in range(3)]
                t = sum(d[i] * v[i] for i in range(3)) / vv
                return 0 < t < .9 and sum((d[i] - t * v[i]) ** 2 for i in range(3)) < 24 ** 2
            px = [q for q in small.getdata() if sum(abs(q[i] - fg[i]) for i in range(3)) > 90 and not blend(q)]
            busy = False
            if len(px) >= 12:
                ls = sorted(lum(q) for q in px)
                q1, q2, q3 = ls[len(ls) // 4], ls[len(ls) // 2], ls[3 * len(ls) // 4]
                busy = q3 - q1 > 0.15
                lf = lum(fg)
                rate = lambda l: (max(l, lf) + 0.05) / (min(l, lf) + 0.05)
                cr = min(rate(q1), rate(q3)) if busy else rate(q2)
            else:
                cr = ratio(fg, bg)
            worst = min(worst, cr)
            if cr < need and sample not in said:
                said.add(sample)
                found.setdefault(s['n'], []).append({'kind': 'contrast', 'text': sample, 'msg': 'text contrast %.1f:1 (needs %.1f:1)%s'
                                                     % (cr, need, ' over a busy background' if busy else '')})
        s['info']['minContrast'] = round(worst, 2) if worst < 99 else None
    return found


def nojs_issues(src_html, pdf, n, out):
    """Print the deck with its scripts removed and compare each page with the normal print."""
    from PIL import ImageChops
    text = src_html.read_text(encoding='utf-8')
    text = re.sub(r'<script\b[^>]*>.*?</script\s*>', '', text, flags=re.S | re.I)
    text = re.sub(r'</?noscript>', '', text, flags=re.I)
    bare = out / 'nojs.html'
    bare.write_text(text, encoding='utf-8')
    try:
        bare_pdf = chrome.print_pdf(bare, out / 'nojs.pdf')
    finally:
        bare.unlink(missing_ok=True)
    a, b = render(pdf, width=480), render(bare_pdf, width=480)
    if len(b) != n:
        return {0: [{'kind': 'no-scripts', 'text': '', 'msg': 'without scripts the print has %d pages for %d slides' % (len(b), n)}]}
    found = {}
    for i, (p, q) in enumerate(zip(a, b), 1):
        if p.size != q.size:
            q = q.resize(p.size)
        diff = ImageChops.difference(p.convert('L'), q.convert('L')).point(lambda v: 255 if v > 40 else 0)
        share = diff.histogram()[255] / (p.width * p.height)
        if share > 0.003:
            found.setdefault(i, []).append({'kind': 'no-scripts', 'text': '', 'msg': 'looks different without scripts (%.1f%% of the slide)' % (share * 100)})
    (out / 'nojs.pdf').unlink(missing_ok=True)
    return found


def sheets(pdf, out, landscape):
    from PIL import Image
    for old in out.glob('sheet-*.png'):
        old.unlink()
    w, cols, per, g = (500 if landscape else 340), 3, 6, 8
    pages = render(pdf, width=w)
    made = []
    for start in range(0, len(pages), per):
        group = pages[start:start + per]
        h = max(p.height for p in group)
        rows = (len(group) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * (w + g) + g, rows * (h + g) + g), (120, 120, 120))
        for k, im in enumerate(group):
            sheet.paste(im, (g + (k % cols) * (w + g), g + (k // cols) * (h + g)))
        path = out / ('sheet-%02d.png' % (start // per + 1))
        sheet.save(path)
        made.append('%s (slides %d to %d)' % (path.name, start + 1, start + len(group)))
    return made


# ---------- one format ----------

def run_qc(deck_html, size):
    text = chrome.inject(deck_html.read_text(encoding='utf-8'), first=chrome.ERRORS,
                         body='<script>\n' + QC_JS.read_text(encoding='utf-8') + '\n</script>')
    tmp = chrome.temp_beside(deck_html, text, 'qc')
    try:
        dom = chrome.dump_dom(tmp, size=size, budget=25000, timeout=180)
    finally:
        tmp.unlink(missing_ok=True)
    found = OUT_RE.findall(dom)
    if not found:
        sys.exit('The QC script wrote nothing for %s (the page did not load or the runtime did not start)' % deck_html)
    return json.loads(html.unescape(found[-1]))


def check(deck_html, out, fmt, shots=True):
    """QC one built file that sits alone in `out`. Returns the number of issues."""
    size = build.FORMATS[fmt]
    data = run_qc(deck_html, size)
    pdf = chrome.print_pdf(deck_html, out / 'deck.pdf', expect=len(data['slides']) or None)
    extra = {}
    for part in (contrast_issues(pdf, data), nojs_issues(deck_html, pdf, len(data['slides']), out)):
        for n, items in part.items():
            extra.setdefault(n, []).extend(items)
    for s in data['slides']:
        s['issues'] += extra.pop(s['n'], [])
    whole = extra.pop(0, [])
    for s in data['slides']:
        s.pop('lines', None)
    (out / 'qc.json').write_text(json.dumps(data, indent=1), encoding='utf-8')

    n = 0
    say = print
    say('%s: %d slides, %s theme, %s, %s mode, %s motion; checked as %s' % (
        fmt, len(data['slides']), data.get('theme'), data.get('palette') or 'default palette', data.get('mode'),
        data.get('motion'), deck_html))
    say('  fonts loaded: %d%s' % (len(data['loaded']), ('; FAILED: ' + ', '.join(data['failed'])) if data['failed'] else ''))
    n += len(data['failed'])
    for e in dict.fromkeys(data['errors']):
        say('  script error: ' + str(e)[:200])
        n += 1
    for i in whole:
        say('  [%s] %s' % (i['kind'], i['msg']))
        n += 1
    for s in data['slides']:
        if not s['issues']:
            continue
        say('  slide %s%s' % (s['label'], (' "%s"' % s['title'][:50]) if s['title'] else ''))
        for i in s['issues']:
            say('    [%s] %s%s' % (i['kind'], i['msg'], ('  <- "%s"' % i['text']) if i['text'] else ''))
            n += 1
    quiet = [s['label'] for s in data['slides'] if not s['info'].get('notes')]
    long_titles = ['%s (%d)' % (s['label'], s['info']['titleLines']) for s in data['slides'] if (s['info'].get('titleLines') or 0) > 2]
    code = ['%s: %s' % (s['label'], s['info']['code']) for s in data['slides'] if s['info'].get('code')]
    lowc = [s['info'].get('minContrast') for s in data['slides'] if s['info'].get('minContrast')]
    if not re.search(r'<div class="pc-deck"[^>]*data-medium="graphic"', deck_html.read_text(encoding='utf-8')):   # a graphic has no notes
        say('  notes missing on: %s' % (', '.join(quiet) if quiet else 'none'))
    if long_titles:
        say('  three-line titles: ' + ', '.join(long_titles))
    if code:
        say('  code fitted: ' + '; '.join(code))
    if lowc:
        say('  lowest text contrast: %.1f:1' % min(lowc))
    sizes = {}
    for s in data['slides']:
        for sel, fss in s['info'].get('type', {}).items():
            for fs in fss:
                sizes.setdefault(sel, {}).setdefault(fs, []).append(s['label'])
    mixed = {sel: d for sel, d in sizes.items() if len(d) > 1}
    if mixed:
        say('  sizes that vary across slides (fine when a slide fits its content on purpose):')
        for sel, d in mixed.items():
            say('    %s: %s' % (sel, '; '.join('%d px on %s' % (fs, ', '.join(v[:8]) + (' ...' if len(v) > 8 else '')) for fs, v in sorted(d.items()))))
    if shots:
        w, h = size
        made = sheets(pdf, out, w >= h)
        say('  contact sheets in %s: %s' % (out, ', '.join(made)))
    say('  issues: %d' % n)
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('deck')
    ap.add_argument('-o', '--out')
    ap.add_argument('--formats', help='comma-separated formats to build and check, or "all" (source decks only)')
    ap.add_argument('--no-sheets', action='store_true', help='skip the contact sheets')
    ap.add_argument('--theme', help='build source decks with this theme (and --palette, --mode) instead of their own')
    ap.add_argument('--palette')
    ap.add_argument('--mode', choices=('light', 'dark'))
    a = ap.parse_args()
    src = Path(a.deck).resolve()
    text = src.read_text(encoding='utf-8')
    built = 'data-pc="core"' in text
    root = Path(a.out).resolve() if a.out else Path(tempfile.gettempdir()) / 'pc-qc' / src.stem
    m = build.DECK_RE.search(text)
    if not m:
        sys.exit('%s has no pc-deck element' % src.name)
    own = dict(build.parse_tag(m.group(0))[1]).get('data-format') or '16x9'
    if a.formats:
        if built:
            sys.exit('--formats needs the source deck (the one that links the kit), not a built file')
        fmts = list(build.DECK_FORMATS) if a.formats == 'all' else [f.strip() for f in a.formats.split(',') if f.strip()]
        bad = [f for f in fmts if f not in build.FORMATS]
        if bad:
            sys.exit('Unknown format: %s (formats: %s)' % (', '.join(bad), ', '.join(build.FORMATS)))
    else:
        fmts = [own]
    total = 0
    for f in fmts:
        out = root / f if len(fmts) > 1 else root
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        target = out / 'deck.html'
        if built:
            shutil.copy(src, target)
        else:
            r = build.build(src, out=target, fmt=None if f == own else f, theme_id=a.theme, palette=a.palette,
                            mode=a.mode, quiet=True, check=False)
            for p in r['problems']:
                print('  build: ' + p)
                total += 1
        total += check(target, out, f, shots=not a.no_sheets)
    if len(fmts) > 1:
        print('ISSUES in %d formats: %d' % (len(fmts), total))
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
