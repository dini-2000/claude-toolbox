#!/usr/bin/env python3
"""Check that the kit works on this computer: build and QC the showcase deck in every theme, turn the sample
outline into a deck, convert one deck to PowerPoint, and draw one overview sheet to look at.

    python3 tools/selftest.py                      every theme at 16:9 (about ten minutes)
    python3 tools/selftest.py --quick              Meridian only, plus the outline and the PowerPoint
    python3 tools/selftest.py --themes folio,noir --formats all -o ~/Desktop/pc-selftest

It writes to selftest/ in the kit folder unless -o says otherwise: summary.txt (one line per check), overview.png
(one row per theme: cover, figures, chart, photo, table and closing, in each theme's default palette and mode), and each
check's own QC folder with its contact sheets. Look at overview.png as well as the summary: QC finds overflow,
contrast and missing fonts, not slides that look wrong.
"""
import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
TOOLS = KIT / 'tools'
SHOW = KIT / 'samples' / 'showcase.html'
PAGES = (1, 4, 6, 13, 18, 29)                 # cover, stats, chart, photo, table, closing in the showcase deck


def run(args, log):
    t = time.time()
    p = subprocess.run([sys.executable] + [str(a) for a in args], capture_output=True, text=True, cwd=KIT)
    log.write_text(p.stdout + p.stderr, encoding='utf-8')
    return p, time.time() - t


def qc_line(p):
    issues = [int(n) for n in re.findall(r'^\s*issues: (\d+)', p.stdout, re.M)]
    if not issues:                                      # qc.py exits 1 on issues too: only no count means it failed
        return False, 'failed to run (exit %d)' % p.returncode
    bad = sum(issues)
    return bad == 0, '%d of %d formats clean%s' % (sum(1 for n in issues if n == 0), len(issues), '' if bad == 0 else ', %d issues' % bad)


def overview(rows, out):
    import fitz
    from PIL import Image, ImageDraw, ImageFont
    w, g, lab = 360, 6, 150
    strips = []
    for name, pdf in rows:
        doc = fitz.open(pdf)
        ims = []
        for n in PAGES:
            if n <= len(doc):
                pg = doc[n - 1]
                z = w / pg.rect.width
                pix = pg.get_pixmap(matrix=fitz.Matrix(z, z))
                ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
        strips.append((name, ims))
    h = max(im.height for _, ims in strips for im in ims)
    sheet = Image.new('RGB', (lab + len(PAGES) * (w + g) + g, len(strips) * (h + g) + g), (120, 120, 120))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default(size=24)
    except TypeError:                                   # Pillow before 10.1
        font = ImageFont.load_default()
    for r, (name, ims) in enumerate(strips):
        y = g + r * (h + g)
        d.text((14, y + h // 2 - 12), name, fill=(255, 255, 255), font=font)
        for k, im in enumerate(ims):
            sheet.paste(im, (lab + g + k * (w + g), y))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser(description='Check that the kit works on this computer.')
    ap.add_argument('--themes', default='all', help='comma-separated theme ids, or "all" (default)')
    ap.add_argument('--formats', default='16x9', help='formats to check each theme in, or "all" (default 16x9)')
    ap.add_argument('--modes', default='', help='check each theme in these modes, e.g. light,dark (default: the deck\'s own)')
    ap.add_argument('--quick', action='store_true', help='Meridian only, plus the outline and the PowerPoint')
    ap.add_argument('--theme-dir', action='append', default=[], help='a theme kept outside themes/ (a job\'s style folder); '
                    'repeat for more; checks only these unless --themes names others')
    ap.add_argument('-o', '--out', default=str(KIT / 'selftest'))
    a = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_themes as bt
    dirs = [bt.add_dir(d) for d in a.theme_dir]
    built = bt.theme_ids()
    themes = ['meridian'] if a.quick else dirs if dirs and a.themes == 'all' else sorted(p.parent.name for p in (KIT / 'themes').glob('*/theme.json')) if a.themes == 'all' else [t.strip() for t in a.themes.split(',') if t.strip()]
    missing = [t for t in themes if t not in built]
    if missing:
        sys.exit('No theme %s. Built themes: %s' % (', '.join(missing), ', '.join(built)))
    out = Path(a.out).expanduser().resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    lines, rows, ok_all = [], [], True

    def note(ok, what, detail, secs):
        nonlocal ok_all
        ok_all &= ok
        line = '%-4s %-34s %s (%.0f s)' % ('ok' if ok else 'FAIL', what, detail, secs)
        lines.append(line)
        print(line, flush=True)

    modes = [m.strip() for m in a.modes.split(',') if m.strip()] or [None]
    for t in themes:
        for m in modes:
            tag = t + ('-' + m if m else '')
            p, secs = run([TOOLS / 'qc.py', SHOW, '--formats', a.formats, '--theme', t, '-o', out / tag] + (['--mode', m] if m else []),
                          out / (tag + '.log'))
            ok, detail = qc_line(p)
            note(ok, 'showcase, ' + t + (', ' + m if m else ''), detail, secs)
            pdf = next(iter(sorted((out / tag).glob('16x9/deck.pdf'))), None) or next(iter(sorted((out / tag).glob('**/deck.pdf'))), None)
            if pdf:
                rows.append((tag, pdf))

    md = out / 'outline' / 'outline.html'
    p, secs = run([TOOLS / 'md_to_deck.py', KIT / 'samples' / 'outline.md', '-o', md], out / 'outline-convert.log')
    if p.returncode:
        note(False, 'outline.md to a deck', 'failed: ' + (p.stderr.strip().splitlines() or ['?'])[-1], secs)
    else:
        own = [] if a.themes == 'all' or a.quick else ['--theme', themes[0]]     # checking named themes: the outline in the first
        p, secs2 = run([TOOLS / 'qc.py', md, '-o', out / 'outline' / 'qc'] + own, out / 'outline-qc.log')
        ok, detail = qc_line(p)
        note(ok, 'outline.md to a deck', detail, secs + secs2)

    first = themes[0] + ('-' + modes[0] if modes[0] else '')
    deck = out / first / ('16x9' if (out / first / '16x9').exists() else '') / 'deck.html'
    if deck.exists():
        pp = out / 'powerpoint' / 'deck.pptx'
        pp.parent.mkdir(exist_ok=True)
        p, secs = run([TOOLS / 'to_pptx.py', deck, '-o', pp, '--check'], out / 'powerpoint.log')
        tail = (p.stdout.strip().splitlines() or ['no output'])[-1]
        note(p.returncode == 0 and pp.exists(), 'PowerPoint from ' + themes[0], tail[:90], secs)
    else:
        note(False, 'PowerPoint', 'no built deck to convert', 0)

    # Graphics: three posts at 1080 x 1080, and a business card's print file at 85 x 55 mm with 3 mm bleed
    gx, src = out / 'graphics', KIT / 'samples' / 'graphics'
    p, secs = run([TOOLS / 'export_graphic.py', src / 'social-posts.html', '--theme', themes[0], '-o', gx], out / 'graphics.log')
    p2, secs2 = run([TOOLS / 'export_graphic.py', src / 'business-card.html', '--theme', themes[0], '--print', '-o', gx], out / 'graphics-print.log')
    from PIL import Image
    import fitz
    posts = [f for f in sorted(gx.glob('social-posts-0?.png')) if Image.open(f).size == (1080, 1080)]
    card = gx / 'business-card-print.pdf'
    size = [round(v / 72 * 25.4) for v in fitz.open(card)[0].rect][2:] if card.exists() else None
    good = not p.returncode and not p2.returncode and len(posts) == 3 and size == [91, 61]
    note(good, 'graphics from ' + themes[0], '%d of 3 posts at 1080 x 1080; card print file %s' %
         (len(posts), '%d x %d mm' % tuple(size) if size else 'missing'), secs + secs2)

    if rows:
        overview(rows, out / 'overview.png')
    lines.append('')
    lines.append('All checks passed.' if ok_all else 'Some checks failed: read the .log file named for each one.')
    lines.append('Look at overview.png too: one row per theme (cover, figures, chart, photo, table, closing).')
    (out / 'summary.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines[-3:]))
    print('Results in %s' % out)
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
