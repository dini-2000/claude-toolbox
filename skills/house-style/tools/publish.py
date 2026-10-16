#!/usr/bin/env python3
"""Publish a deck for sharing: one HTML file whose Download menu offers the PDF and the PowerPoint.

    python3 tools/publish.py decks/talk/talk.html                    # builds dist/talk.html, stores both inside
    python3 tools/publish.py talk.html --theme folio --format 4x5    # style options, for a source deck
    python3 tools/publish.py dist/talk.html --png --scale 2          # also every slide as a PNG
    python3 tools/publish.py dist/talk.html --png --max-kb 900       # PNGs over 900 KB saved as JPEG instead

1. A source deck (one that links engine/) is built into one file first, with any style options given, to
   the same dist/ path tools/build.py uses (or to -o). A deck that is one file already is published in place
   unless -o names another file; style options need the source deck.
2. tools/to_pptx.py converts it, and Chrome's print of it (one page per slide at the deck's own size) is
   kept as the PDF. Both are saved beside the HTML.
3. Both go inside the HTML (script#pc-pdf and script#pc-pptx, which engine/runtime.js reads), so anyone with
   only the HTML can download them in any browser, Safari and iPhone included.
--png saves each slide as "<name> slides/slide-NN.png", drawn from the same PDF: --scale 1 is the deck's CSS
pixels (1920 x 1080 for 16:9), 2 doubles it. --max-kb keeps each file under a size (social sites cap
uploads) by saving that slide as a JPEG, at the best quality that fits.
Publish again after any change to the deck: the stored files do not follow edits.
Before any of this, it runs tools/qc.py on the deck as it will be published and stops on an issue, and it will not
publish a deck in a custom theme that has not passed its check (tools/make_theme.py --check). --accept "<why>" lets a
deck through after you have looked at each issue and found it a false alarm.
"""
import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build    # noqa: E402
import to_pptx  # noqa: E402

PPTX_TYPE = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
PDF_TYPE = 'application/pdf'
STORED = re.compile(r'<script type="(?:%s|%s)" id="pc-(?:pptx|pdf)"[^>]*>.*?</script>\s*'
                    % (re.escape(PPTX_TYPE), re.escape(PDF_TYPE)), re.S)
SOURCE = re.compile(r'(?:href|src)=["\'][^"\']*engine/(?:core\.css|runtime\.js)')


def export_png(pdf, folder, scale=1.0, max_kb=None):
    """Each page of the deck's PDF as a PNG (or a JPEG where max_kb asks) in folder. Returns the files."""
    folder = Path(folder)
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    zoom = 4 / 3 * scale                                 # PDF points to CSS pixels, then the scale
    out = []
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            data, ext = pix.tobytes('png'), 'png'
            if max_kb and len(data) > max_kb * 1024:
                for q in (95, 90, 85, 80, 75, 70, 60, 50):
                    data, ext = pix.tobytes('jpeg', jpg_quality=q), 'jpg'
                    if len(data) <= max_kb * 1024:
                        break
                else:
                    print('Slide %d is still %d KB as a JPEG at quality 50: try a smaller --scale.'
                          % (i, len(data) // 1024))
            path = folder / ('slide-%02d.%s' % (i, ext))
            path.write_bytes(data)
            out.append(path)
    return out


def store(text, pdf, pptx):
    """The HTML with the PDF and PowerPoint inside it, after the <body> tag."""
    stored = ''
    for path, kind, mime in ((pdf, 'pdf', PDF_TYPE), (pptx, 'pptx', PPTX_TYPE)):
        data = base64.b64encode(Path(path).read_bytes()).decode('ascii')
        data = '\n'.join(data[i:i + 120] for i in range(0, len(data), 120))
        stored += '<script type="%s" id="pc-%s" data-name="%s">\n%s\n</script>\n' % (
            mime, kind, to_pptx.esc(Path(path).name), data)
    m = re.search(r'<body\b[^>]*>', text, flags=re.I)
    if not m:
        sys.exit('The deck has no <body> tag.')
    return text[:m.end()] + '\n' + stored + text[m.end():]


def qc_gate(src, style, accept):
    """QC the deck as it will be published. Issues stop the publish unless --accept gives the reason each is a false alarm."""
    text = Path(src).read_text(encoding='utf-8')
    m = build.DECK_RE.search(text)
    tid = style.get('theme_id') or (dict(build.parse_tag(m.group(0))[1]).get('data-theme') if m else None)
    tj = build.bt.folder(tid or '') / 'theme.json'
    custom = (json.loads(tj.read_text(encoding='utf-8')).get('custom') if tid and tj.is_file() else None) or None
    if custom and not (custom.get('checked') or {}).get('passed') and not accept:
        sys.exit('Not published: %s is a custom theme that has not passed its check. Run python3 tools/make_theme.py '
                 '--check %s, fix what it finds, then publish again.' % (tid, tid))
    out = Path(tempfile.mkdtemp(prefix='pc-publish-qc-'))
    args = [sys.executable, str(HERE / 'qc.py'), str(src), '-o', str(out)]
    for k, flag in (('theme_id', '--theme'), ('palette', '--palette'), ('mode', '--mode'), ('fmt', '--formats')):
        if style.get(k):
            args += [flag, style[k]]
    print('QC before publishing...', flush=True)
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        print('\n'.join((r.stdout + r.stderr).strip().splitlines()[-40:]))
        if not accept:
            sys.exit('Not published: QC found issues (above; contact sheets in %s). Fix them in the deck and publish again. '
                     'If each one is a false alarm you have looked at, publish with --accept "<why>".' % out)
        print('Publishing with QC issues accepted: %s' % accept)
    else:
        print('QC clean. Look at every contact sheet in %s as well.' % out)


def publish(src, out=None, style=None, check=False, powerpoint=False, png=False, scale=1.0, max_kb=None):
    src = Path(src).resolve()
    if not src.exists():
        sys.exit('No such file: %s' % src)
    text = src.read_text(encoding='utf-8')
    style = {k: v for k, v in (style or {}).items() if v}
    if SOURCE.search(text):
        res = build.build(src, out=out, quiet=True, **style)
        if res['problems']:
            print('Build problems:\n  ' + '\n  '.join(str(p) for p in res['problems']))
        out = Path(res['path'])
        text = out.read_text(encoding='utf-8')
    else:
        if style:
            sys.exit('This deck is one file already, so it keeps its style. Publish its source deck with %s.'
                     % ', '.join('--' + k.replace('theme_id', 'theme').replace('fmt', 'format') for k in style))
        out = Path(out).resolve() if out else src
    text = STORED.sub('', text)
    out.write_text(text, encoding='utf-8')               # the deck as it is now, without old stored files
    pptx, pdf = out.with_suffix('.pptx'), out.with_suffix('.pdf')
    work = Path(tempfile.mkdtemp(prefix='pc-publish-'))
    try:
        to_pptx.convert(out, pptx, keep=work, check=check, powerpoint=powerpoint)
        with fitz.open(work / 'full.pdf') as doc:        # Chrome's print, which the PowerPoint was made from;
            doc.save(pdf, garbage=4, deflate=True)       # Chrome repeats a shared picture on every page (Chalk's
                                                         # grain: 10.3 MB), and garbage=4 keeps one copy (1.1 MB)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    sides = pptx.with_name(pptx.stem + ' check')           # --check's side-by-sides stay out of the deck's folder
    if sides.exists():
        keep = Path(tempfile.gettempdir()) / 'pc-publish-check' / sides.name
        shutil.rmtree(keep, ignore_errors=True)
        keep.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(sides), str(keep))
        print('Side-by-side images moved to %s' % keep)
    out.write_text(store(text, pdf, pptx), encoding='utf-8')
    print('Published %s (%.1f MB): Download offers the PDF (%.1f MB) and PowerPoint (%.1f MB) stored in it, '
          'also saved beside it.' % (out, out.stat().st_size / 1e6, pdf.stat().st_size / 1e6, pptx.stat().st_size / 1e6))
    if png:
        files = export_png(pdf, out.with_name(out.stem + ' slides'), scale, max_kb)
        kinds = sorted({f.suffix[1:].upper() for f in files})
        print('Slide images: %d %s files in "%s".' % (len(files), ' and '.join(kinds), files[0].parent))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('deck', help='a source deck (links engine/) or a built one-file deck')
    ap.add_argument('-o', '--out', help='the one-file HTML to write (default: dist/ for a source deck, else in place)')
    for opt in ('theme', 'palette', 'mode', 'format', 'motion'):
        ap.add_argument('--' + opt, help='style option for a source deck, as tools/build.py takes it')
    ap.add_argument('--check', action='store_true', help='compare every slide (to_pptx.py --check)')
    ap.add_argument('--powerpoint', action='store_true', help='also check in PowerPoint (to_pptx.py --powerpoint)')
    ap.add_argument('--png', action='store_true', help='also save every slide as an image')
    ap.add_argument('--scale', type=float, default=1.0, help='image size: 1 = the deck\'s CSS pixels (default)')
    ap.add_argument('--max-kb', type=int, help='largest image file, in KB; bigger slides are saved as JPEG')
    ap.add_argument('--accept', metavar='WHY', help='publish despite QC issues, giving the reason each is a false alarm')
    a = ap.parse_args()
    style = {'theme_id': a.theme, 'palette': a.palette, 'mode': a.mode, 'fmt': a.format, 'motion': a.motion}
    if not Path(a.deck).is_file():
        sys.exit('No such file: %s' % a.deck)
    qc_gate(Path(a.deck).resolve(), {k: v for k, v in style.items() if v}, a.accept)
    publish(a.deck, a.out, style, a.check, a.powerpoint, a.png, a.scale, a.max_kb)


if __name__ == '__main__':
    main()
