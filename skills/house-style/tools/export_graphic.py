#!/usr/bin/env python3
"""Export a graphic: each slide of a source as PNG (and JPG) at its platform size, a PDF, and a print PDF with bleed.

    python3 tools/export_graphic.py post.html -o out/                        # PNG at 1x and 2x, and a PDF
    python3 tools/export_graphic.py post.html --theme confetti --format 4x5 --jpg -o out/
    python3 tools/export_graphic.py poster.html --format a4p --print --size a3 -o out/      # A3 with 3 mm bleed
    python3 tools/export_graphic.py card.html --format card --print --press --marks -o out/ # CMYK PDF/X-4 for a press

A graphic is a kit deck with data-medium="graphic" (set here if the source lacks it): every slide is one design, with
the slide components, theme art and charts; no page numbers or notes. --theme, --palette, --mode and --format work
as in build.py. Formats and their exports (1x PNG; --scale changes it, and @2x is always written beside it):

    1x1 1080 x 1080 (square post)       4x5 1080 x 1350 (portrait post)     9x16 1080 x 1920 (story, reel cover)
    16x9 1920 x 1080 (video thumbnail)  191x100 1200 x 627 (link preview, LinkedIn or Facebook post)
    3x1 1500 x 500 (X header)           4x1 1584 x 396 (LinkedIn banner)
    a4p, a4l: A4 at 150 dpi on screen; prints at A5, A4, A3 or A2 (--size), the flyer and poster sizes
    5x7 (invitation, 127 x 178 mm), letter-p (US Letter flyer), card (business card, 85 x 55 mm)

Banners: X and LinkedIn crop a profile picture over the lower left, so keep words out of the left third there.

--print writes <name>-print.pdf at the real size with --bleed mm (3 by default) on every side: the slide's background
and art run into the bleed, the content keeps its place inside the trim, and each page carries its TrimBox and
BleedBox. --press then makes <name>-press.pdf from it with tools/print_ready.py: CMYK on --profile (fogra39 by
default), PDF/X-4, and with --marks crop marks outside the bleed. Ask the print shop for its bleed and profile.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import chrome  # noqa: E402

MM = 96 / 25.4   # CSS px per mm
# 1x export size of each format in pixels
SCREEN = {'16x9': (1920, 1080), '4x3': (1440, 1080), '1x1': (1080, 1080), '4x5': (1080, 1350), '9x16': (1080, 1920),
          'a4p': (1240, 1754), 'a4l': (1754, 1240), '191x100': (1200, 627), '3x1': (1500, 500), '4x1': (1584, 396),
          '5x7': (1500, 2100), 'letter-p': (1275, 1650), 'card': (1004, 650)}
# trim sizes in mm: each print format's own, and the sizes --size offers (portrait; turned for landscape formats)
TRIM = {'a4p': (210, 297), 'a4l': (297, 210), '5x7': (127, 177.8), 'letter-p': (215.9, 279.4), 'card': (85, 55)}
SIZES = {'a5': (148, 210), 'a4': (210, 297), 'a3': (297, 420), 'a2': (420, 594), 'letter': (215.9, 279.4),
         '5x7': (127, 177.8), 'card': (55, 85)}


def trim_size(fmt, size):
    """The trim in mm for a format and an optional --size (a name above or WxHmm), checked against the shape."""
    W, H = build.FORMATS[fmt]
    if size:
        m = re.fullmatch(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)mm', size)
        if m:
            tw, th = float(m.group(1)), float(m.group(2))
        elif size in SIZES:
            tw, th = SIZES[size]
            if (W > H) != (tw > th):
                tw, th = th, tw
        else:
            sys.exit('--size is one of %s, or a size such as 200x200mm' % ', '.join(SIZES))
    elif fmt in TRIM:
        tw, th = TRIM[fmt]
    else:
        sys.exit('%s has no print size of its own: give --size, such as --size %dx%dmm' % (fmt, round(W / 10), round(H / 10)))
    if abs((tw / th) / (W / H) - 1) > .01:
        sys.exit('A %g x %g mm page is not the shape of %s (%d x %d); pick the format with that shape' % (tw, th, fmt, W, H))
    return tw, th


def variant(built_text, style):
    """The built page with a style of its own last in the cascade."""
    i = built_text.rfind('</body>')   # the last one: the inlined runtime mentions </body> in a string
    return built_text[:i] + '<style>%s</style>\n' % style + built_text[i:]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('src')
    ap.add_argument('-o', '--out', required=True, help='folder for the exports')
    ap.add_argument('--theme')
    ap.add_argument('--theme-dir', help='a theme kept outside themes/ (a job\'s style folder)')
    ap.add_argument('--palette')
    ap.add_argument('--mode', choices=['light', 'dark'])
    ap.add_argument('--format', choices=list(build.FORMATS))
    ap.add_argument('--scale', type=float, default=1.0, help='PNG size against the platform size (default 1; @2x is written too)')
    ap.add_argument('--jpg', action='store_true', help='also write JPGs (quality 90)')
    ap.add_argument('--print', dest='prn', action='store_true', help='write <name>-print.pdf at the real size with bleed')
    ap.add_argument('--size', help='print size: a5, a4, a3, a2, letter, 5x7, card, or WxHmm')
    ap.add_argument('--bleed', type=float, default=3.0, help='mm of bleed on every side (default 3)')
    ap.add_argument('--press', action='store_true', help='also a CMYK PDF/X-4 press file through print_ready.py')
    ap.add_argument('--marks', action='store_true', help='crop marks on the press file')
    ap.add_argument('--profile', default='fogra39', help='press profile for --press (fogra39, gracol, uncoated, or a .icc)')
    a = ap.parse_args()
    if a.marks and not a.press:
        sys.exit('--marks goes on the press file: add --press')
    import fitz
    from PIL import Image

    src, out = Path(a.src).resolve(), Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    stem = src.stem
    with tempfile.TemporaryDirectory(prefix='pc-graphic-') as tmp:
        tmp = Path(tmp)
        built = tmp / (stem + '.html')
        cmd = [sys.executable, str(HERE / 'build.py'), str(src), '-o', str(built), '--motion', 'static']
        for k in ('theme', 'theme_dir', 'palette', 'mode', 'format'):
            if getattr(a, k):
                cmd += ['--' + k.replace('_', '-'), getattr(a, k)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode or not built.exists():
            sys.exit('build.py stopped:\n' + (r.stderr or r.stdout))
        text = built.read_text(encoding='utf-8')
        deck = re.search(r'<div class="pc-deck"[^>]*>', text)
        fmt = re.search(r'data-format="([^"]+)"', deck.group(0)).group(1)
        if 'data-medium=' not in deck.group(0):
            text = text[:deck.end() - 1] + ' data-medium="graphic"' + text[deck.end() - 1:]
        n = len(re.findall(r'<section class="pc-slide\b[^>]*\bdata-n="', text))   # build.py numbers every slide
        W, H = build.FORMATS[fmt]

        # Screen PDF at the slide's own size (the format's print size for a4, 5x7, letter and card), then the pictures
        page = tmp / 'page.html'
        page.write_text(text, encoding='utf-8')
        pdf = out / (stem + '.pdf')
        chrome.print_pdf(page, pdf, expect=n)
        sw, sh = SCREEN.get(fmt, (W, H))
        doc = fitz.open(pdf)
        written = [pdf.name]
        for i, pg in enumerate(doc):
            tag = '' if len(doc) == 1 else '-%02d' % (i + 1)
            for k, suffix in ((a.scale, ''), (a.scale * 2, '@2x')):
                tw, th = round(sw * k), round(sh * k)
                pix = pg.get_pixmap(matrix=fitz.Matrix(tw / pg.rect.width, th / pg.rect.height), alpha=False)
                name = '%s%s%s.png' % (stem, tag, suffix)
                pix.save(str(out / name))
                written.append(name)
                if a.jpg and not suffix:
                    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                    jname = '%s%s.jpg' % (stem, tag)
                    img.save(out / jname, quality=90, optimize=True, progressive=True)
                    written.append(jname)
        doc.close()

        if a.prn or a.press:
            tw_mm, th_mm = trim_size(fmt, a.size)
            b = a.bleed
            bleed_px = b / tw_mm * W              # the bleed in slide pixels
            zoom = tw_mm * MM / W                 # slide pixels to page pixels
            style = '.pc-deck { --bleed: %.3fpx; }\n@media print { .pc-deck .pc-slide { zoom: %.6f !important; } }' % (bleed_px, zoom)
            ptext = variant(text, style)
            size = '%.3fmm %.3fmm' % (tw_mm + 2 * b, th_mm + 2 * b)
            tag = re.search(r'<div class="pc-deck"[^>]*>', ptext)   # the deck element, not the inlined CSS that names it
            ptext = ptext[:tag.end() - 1] + ' data-bleed="%gmm" data-page="%s"' % (b, size) + ptext[tag.end() - 1:]
            ptext = re.sub(r'<style id="pc-page"[^>]*>[^<]*</style>',   # build.py writes the format's page size; the runtime keeps data-page
                           '<style id="pc-page" data-size="%s">@page { size: %s; margin: 0; }</style>' % (size, size), ptext, 1)
            ppage = tmp / 'print.html'
            ppage.write_text(ptext, encoding='utf-8')
            ppdf = out / (stem + '-print.pdf')
            chrome.print_pdf(ppage, ppdf, expect=n)
            doc = fitz.open(ppdf)
            bp = b * 72 / 25.4
            for pg in doc:
                r_ = pg.rect
                pg.set_bleedbox(r_)
                pg.set_trimbox(fitz.Rect(r_.x0 + bp, r_.y0 + bp, r_.x1 - bp, r_.y1 - bp))
            doc.saveIncr()
            doc.close()
            written.append(ppdf.name)
            if a.press:
                press = out / (stem + '-press.pdf')
                cmd = [sys.executable, str(HERE / 'print_ready.py'), str(ppdf), '-o', str(press), '--profile', a.profile]
                if a.marks:
                    cmd.append('--marks')
                r = subprocess.run(cmd, capture_output=True, text=True)
                if r.returncode:
                    sys.exit('print_ready.py stopped:\n' + (r.stderr or r.stdout))
                written.append(press.name)
    print('%s: %d design%s, %s; wrote %s in %s' % (src.name, n, '' if n == 1 else 's', fmt, ', '.join(written), out))


if __name__ == '__main__':
    main()
