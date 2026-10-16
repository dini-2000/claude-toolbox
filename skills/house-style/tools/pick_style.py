#!/usr/bin/env python3
"""The style picker: build it, and serve it so the pick comes back to Claude.

    python3 tools/pick_style.py [--medium deck|document|graphic] [--kind report] [--title "..."] [--suggest a,b,c]
    python3 tools/pick_style.py --build                      only build picker/picker.html and every preview

The picker page (picker/picker.html, built from picker/picker.src.html) asks how to choose the look (the user picks,
Claude picks, or Claude designs something new), what is being made (deck, document or graphic), then the theme,
colour, format or page, and motion for decks, and shows each choice at once in the sample deck (samples/showcase.html,
built per theme with every mode and palette into picker/previews/<theme>.html the first time it is shown). Themes come
grouped by category, with the --suggest themes first; the cover shows --title.

Each run serves the page under a new token, and the page starts from the brief given here, never from an earlier
pick. Its "Use this style" button posts the pick to this script, which prints it as one line of JSON (PICK {...})
and exits; a post from an older tab is refused. Run it as a background command and read its output. Opened straight
from disk, the page shows a pick code instead ("pc-pick theme=folio palette=ink ..."), for the user to paste.
"""
import argparse
import http.server
import json
import re
import secrets
import socketserver
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

KIT = build.KIT
PICKER = KIT / 'picker'
SRC = PICKER / 'picker.src.html'
OUT = PICKER / 'picker.html'
PREVIEWS = PICKER / 'previews'
SHOWCASE = KIT / 'samples' / 'showcase.html'
FORMATS = [
    {'id': '16x9', 'label': 'Widescreen', 'use': 'Screens and projectors'},
    {'id': '4x3', 'label': 'Standard', 'use': 'Older projectors'},
    {'id': '1x1', 'label': 'Square', 'use': 'Social posts'},
    {'id': '4x5', 'label': 'Portrait post', 'use': 'Instagram, LinkedIn'},
    {'id': '9x16', 'label': 'Vertical', 'use': 'Stories, phones'},
    {'id': 'a4p', 'label': 'A4 portrait', 'use': 'Printed reports'},
    {'id': 'a4l', 'label': 'A4 landscape', 'use': 'Printed slides'},
]
GRAPHIC_FORMATS = [
    {'id': '1x1', 'label': 'Square post', 'use': 'Instagram, LinkedIn'},
    {'id': '4x5', 'label': 'Portrait post', 'use': 'Instagram, LinkedIn'},
    {'id': '9x16', 'label': 'Story', 'use': 'Stories, reel covers'},
    {'id': '191x100', 'label': 'Link post', 'use': 'LinkedIn, Facebook'},
    {'id': '16x9', 'label': 'Thumbnail', 'use': 'YouTube, video'},
    {'id': '3x1', 'label': 'X header', 'use': '1500 x 500'},
    {'id': '4x1', 'label': 'LinkedIn banner', 'use': '1584 x 396'},
    {'id': 'a4p', 'label': 'Poster', 'use': 'A5 to A2, flyers'},
    {'id': 'a4l', 'label': 'Landscape', 'use': 'Certificates'},
    {'id': '5x7', 'label': 'Invitation', 'use': '5 x 7 in card'},
    {'id': 'letter-p', 'label': 'US flyer', 'use': 'Letter size'},
    {'id': 'card', 'label': 'Business card', 'use': '85 x 55 mm'},
]
PAGES = [{'id': 'a4', 'label': 'A4', 'use': '210 x 297 mm', 'w': 210, 'h': 297},
         {'id': 'letter', 'label': 'Letter', 'use': '8.5 x 11 in', 'w': 216, 'h': 279},
         {'id': 'a5', 'label': 'A5', 'use': 'Booklets, programmes', 'w': 148, 'h': 210}]
DOC_TYPES = [('report', 'Report'), ('paper', 'Paper or brief'), ('proposal', 'Proposal'), ('guide', 'Guide'),
             ('casestudy', 'Case study'), ('letter', 'Letter'), ('memo', 'Memo'), ('cv', 'CV'), ('invoice', 'Invoice'),
             ('onepager', 'One-pager'), ('newsletter', 'Newsletter'), ('agenda', 'Agenda'), ('programme', 'Programme')]
COVERS = ['band', 'type', 'minimal', 'full', 'split']
NOTES = ['side', 'end', 'foot']
KEYS = ('how', 'medium', 'kind', 'structure', 'theme', 'palette', 'mode', 'format', 'motion', 'page', 'cover', 'notes')


def built_themes():
    """Themes from themes/themes.json that have their tokens and art."""
    listed = json.loads((KIT / 'themes' / 'themes.json').read_text(encoding='utf-8'))['themes']
    return [t for t in listed if (KIT / 'themes' / t['id'] / 'tokens.css').exists()
            and (KIT / 'themes' / t['id'] / 'theme.css').exists()]


def inputs():
    """Files the picker and its previews are made from."""
    files = [SRC, SHOWCASE, KIT / 'themes' / 'themes.json', KIT / 'guide' / 'structures.json', Path(build.__file__)]
    files += sorted((KIT / 'engine').glob('*')) + sorted((KIT / 'samples' / 'img').glob('*'))
    files += sorted((KIT / 'themes').glob('*/*.css'))
    return [f for f in files if f.is_file()]


def older(path, files):
    return not path.exists() or path.stat().st_mtime < max(f.stat().st_mtime for f in files)


def stale():
    return older(OUT, inputs())


def preview(tid, quiet=True):
    """Build one theme's preview if the sample deck or the theme changed since it was built; False on problems."""
    out = PREVIEWS / (tid + '.html')
    if not older(out, [f for f in inputs() if f != SRC]):
        return True
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    r = build.build(SHOWCASE, out=out, theme_id=tid, variants=True, quiet=True)
    bad = [p for p in r['problems'] if p.startswith(('Script errors', 'Fonts that failed', 'Still refers', 'Charts not'))]
    if not quiet:
        print('  preview %-12s %s%s' % (tid, build.kb(r['bytes']), ''.join('\n    ! ' + p for p in bad)))
    return not bad


def make(quiet=False, previews=False):
    themes = built_themes()
    if not themes:
        sys.exit('No built themes: run tools/build_themes.py first')
    say = (lambda *a: None) if quiet else print
    ok = True
    if previews:                             # otherwise each preview is built the first time the picker shows it
        for t in themes:
            ok = preview(t['id'], quiet) and ok
    guide = json.loads((KIT / 'guide' / 'structures.json').read_text(encoding='utf-8'))
    ids = {t['id'] for t in themes}
    for s in guide['structures']:            # suggested themes that are built, in the guide's order
        s['suggest']['themes'] = [x for x in s['suggest']['themes'] if x in ids]
    data = {'themes': themes, 'structures': guide['structures'], 'layouts': guide['layouts'], 'formats': [],
            'graphicFormats': [], 'pages': PAGES, 'docTypes': [{'id': i, 'name': n} for i, n in DOC_TYPES],
            'covers': COVERS, 'notes': NOTES, 'previews': {t['id']: 'previews/%s.html' % t['id'] for t in themes}}
    for key, fs in (('formats', FORMATS), ('graphicFormats', GRAPHIC_FORMATS)):
        for f in fs:
            w, h = build.FORMATS[f['id']]
            data[key].append(dict(f, w=w, h=h))
    page = SRC.read_text(encoding='utf-8')
    if page.count('/*DATA*/null') != 1:
        sys.exit('picker.src.html needs exactly one /*DATA*/null placeholder')
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    OUT.write_text(page.replace('/*DATA*/null', blob), encoding='utf-8')
    say('Built %s (%d themes, %d structures)' % (OUT, len(themes), len(guide['structures'])))
    return ok


def clean(p):
    """Keep only known keys with short plain values."""
    if not isinstance(p, dict):
        return None
    out = {}
    for k in KEYS:
        v = p.get(k)
        if v is None:
            continue
        if not isinstance(v, str) or len(v) > 32 or not all(c.isalnum() or c == '-' for c in v):
            return None
        out[k] = v
    return out if out.get('theme') or out.get('how') in ('auto', 'creative') else None


def serve(port, timeout, brief):
    done = threading.Event()
    result = {}
    token = secrets.token_urlsafe(9)
    brief = dict(brief, token=token)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(PICKER), **k)

        def log_message(self, *a):
            pass

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def do_GET(self):
            path = self.path.split('?')[0]
            if path in ('/', ''):
                self.path = '/picker.html'
            elif path == '/brief':
                body = json.dumps(brief).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            m = re.fullmatch(r'/previews/([a-z0-9-]+)\.html', path)
            if m and any(t['id'] == m.group(1) for t in built_themes()):
                preview(m.group(1))          # the first look at a theme builds its preview (a few seconds)
            super().do_GET()

        def do_POST(self):
            if self.path.split('?')[0] != '/pick':
                self.send_error(404)
                return
            if self.path.split('?', 1)[-1] != 's=' + token:
                self.send_error(403, 'This picker tab is from an earlier run: use the address the picker printed last')
                return
            n = int(self.headers.get('Content-Length') or 0)
            try:
                pick = clean(json.loads(self.rfile.read(min(n, 4096)) or b'null'))
            except ValueError:
                pick = None
            if not pick:
                self.send_error(400, 'Not a pick')
                return
            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            result['pick'] = pick
            done.set()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', port), Handler) as httpd:
        httpd.daemon_threads = True
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        print('Picker at http://127.0.0.1:%d/?s=%s  (waiting up to %d minutes for a pick)'
              % (httpd.server_address[1], token, timeout), flush=True)
        got = done.wait(timeout * 60)
        httpd.shutdown()
    if not got:
        print('No pick within %d minutes' % timeout, flush=True)
        return 2
    print('PICK ' + json.dumps(result['pick']), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(description='Build and serve the style picker.')
    ap.add_argument('--build', action='store_true', help='only build the picker and its previews')
    ap.add_argument('--port', type=int, default=8765, help='port on 127.0.0.1 (0 picks a free one)')
    ap.add_argument('--timeout', type=int, default=30, help='minutes to wait for a pick')
    ap.add_argument('--medium', choices=['deck', 'document', 'graphic'], help='what is being made (the page starts there)')
    ap.add_argument('--kind', help='the kind of piece: a deck structure, a document type or a graphic format')
    ap.add_argument('--title', help='the real title, shown on the preview cover')
    ap.add_argument('--suggest', help='comma-separated theme ids to suggest first, best first')
    a = ap.parse_args()
    if a.build:
        sys.exit(0 if make(previews=True) else 1)
    brief = {'medium': a.medium, 'kind': a.kind, 'title': (a.title or '')[:140],
             'suggest': [s.strip() for s in (a.suggest or '').split(',') if s.strip()]}
    if stale():
        print('Building the picker first', flush=True)
        if not make():
            print('  (the previews above have problems; serving anyway)', flush=True)
    sys.exit(serve(a.port, a.timeout, brief))


if __name__ == '__main__':
    main()
