#!/usr/bin/env python3
"""Build one self-contained HTML file from a kit deck: the file to share.

    python3 tools/build.py DECK.html [-o OUT.html] [--theme ID | --theme-dir DIR] [--palette ID] [--mode light|dark]
        [--format 16x9|4x3|1x1|4x5|9x16|a4p|a4l, or for graphics 191x100|3x1|4x1|5x7|letter-p|card] [--motion static|basic|complex]
        [--variants] [--all-faces] [--no-probe] [--no-check]

A deck links the kit's files: engine/core.css, themes/<id>/tokens.css and theme.css, icons/lucide.js and
engine/runtime.js (samples/showcase.html shows the head). The built file carries them inline:
- core.css, theme.css, runtime.js and any other local style sheet or script the deck links;
- the theme's colours for the deck's mode and palette with their inverse (--variants keeps every mode and palette,
  so PCDeck.set can switch them);
- only the Lucide icons the deck uses;
- fonts as WOFF data URIs: only the faces Chrome loads when it renders the deck, notes and menus included
  (--all-faces, or no Chrome: every face of the theme); Noto Sinhala and Tamil only when the text uses them;
- pictures as data URIs;
- the format's @page, and for viewers that run no scripts (Quick Look, mail previews) a style that stacks the
  slides, with charts, marks, icons, slide numbers, theme labels and code colours already drawn into the page.
The overrides (--theme and the rest) build the same deck in another style. Without -o the file goes to the deck's
dist/ folder, named after the deck and the overrides. After building, the tool opens the file in headless Chrome
and reports script errors, fonts that failed and missing icons (--no-check skips this).
"""
import argparse
import base64
import html
import json
import re
import struct
import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_icons  # noqa: E402
import build_themes as bt  # noqa: E402
import chrome  # noqa: E402

KIT = bt.KIT
FONTS = KIT / 'fonts'
DECK_FORMATS = {'16x9': (1920, 1080), '4x3': (1440, 1080), '1x1': (1080, 1080), '4x5': (1080, 1350),
                '9x16': (1080, 1920), 'a4p': (1080, 1527), 'a4l': (1527, 1080)}
# graphics also come in link-preview and banner shapes (1080 high) and print pieces sized in mm or inches
GRAPHIC_FORMATS = {'191x100': (2063, 1080), '3x1': (3240, 1080), '4x1': (4320, 1080), '5x7': (1080, 1512),
                   'letter-p': (1080, 1398), 'card': (1669, 1080)}
FORMATS = dict(DECK_FORMATS, **GRAPHIC_FORMATS)
PAGE = {'a4p': '210mm 297mm', 'a4l': '297mm 210mm', '5x7': '127mm 177.8mm', 'letter-p': '8.5in 11in', 'card': '85mm 55mm'}
DOC_VIEW = (1000, 1400)   # the Chrome window a document is probed in: wider than any page, so nothing wraps differently
MOTIONS = ('static', 'basic', 'complex')
MIME = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
        '.webp': 'image/webp', '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff': 'font/woff',
        '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf'}
SCRIPTS = {'Sinhala': '[඀-෿]', 'Tamil': '[஀-௿]'}
DECK_RE = re.compile(r'<(?:div|main|html)\b[^>]*\bclass\s*=\s*"(?:[^"]*\s)?pc-deck(?:\s[^"]*)?"[^>]*>', re.I)
ATTR_RE = re.compile(r'''([^\s=/>"']+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?''')
FACE_RE = re.compile(r'@font-face \{ font-family: "([^"]+)"; font-style: (\w+); font-weight: (\d+);[^}]*?'
                     r'src: url\("([^"]+)"\) format\("truetype"\);[^}]*\}\n?')
URL_RE = re.compile(r'''url\(\s*(["']?)([^"')]+)\1\s*\)''')


class Problems(list):
    def add(self, msg):
        if msg not in self:
            self.append(msg)


# ---------- small helpers ----------

def woff(ttf):
    """Wrap a TrueType or OpenType font as WOFF 1.0, each table zlib-compressed (stored as is when that is no smaller)."""
    flavor, num = struct.unpack('>IH', ttf[:6])
    tables = sorted(struct.unpack('>4sIII', ttf[12 + 16 * i:28 + 16 * i]) for i in range(num))
    offset, total, dirs, blobs = 44 + 20 * num, 12 + 16 * num, [], []
    for tag, check, off, length in tables:
        raw = ttf[off:off + length]
        comp = zlib.compress(raw, 9)
        if len(comp) >= length:
            comp = raw
        dirs.append(struct.pack('>4sIIII', tag, offset, len(comp), length, check))
        blobs.append(comp + b'\0' * (-len(comp) % 4))
        offset += len(blobs[-1])
        total += length + (-length % 4)
    head = struct.pack('>IIIHHIHHIIIII', 0x774F4646, flavor, offset, num, 0, total, 1, 0, 0, 0, 0, 0, 0)
    return head + b''.join(dirs) + b''.join(blobs)


def data_uri(path, mime=None):
    mime = mime or MIME.get(path.suffix.lower())
    if not mime:
        raise ValueError('no data type for %s' % path.name)
    return 'data:%s;base64,%s' % (mime, base64.b64encode(path.read_bytes()).decode('ascii'))


def is_remote(ref):
    return bool(re.match(r'(?i)(https?:)?//', ref))


def is_inline(ref):
    return bool(re.match(r'(?i)(data:|#|%23|about:|javascript:|mailto:|tel:)', ref)) or not ref.strip()


def resolve(ref, base):
    """A local file a deck refers to: a file:// URL, an absolute path or a path relative to `base`."""
    ref = html.unescape(ref.strip())
    if ref.lower().startswith('file:'):
        return Path(unquote(urlparse(ref).path))
    ref = unquote(ref.split('#')[0].split('?')[0])
    p = Path(ref)
    return p if p.is_absolute() else (base / p).resolve()


def parse_tag(tag):
    m = re.match(r'<\s*([\w:-]+)', tag)
    body = tag[m.end():].rstrip('>').rstrip()
    selfclose = body.endswith('/')
    attrs = []
    for name, val in ATTR_RE.findall(body.rstrip('/')):
        if val[:1] in ('"', "'"):
            val = val[1:-1]
        attrs.append([name, html.unescape(val) if val else ('' if val == '' else None)])
    return m.group(1), attrs, selfclose


def make_tag(name, attrs, selfclose=False):
    out = '<' + name
    for k, v in attrs:
        out += ' ' + k if v is None else ' %s="%s"' % (k, html.escape(v, quote=True))
    return out + (' />' if selfclose else '>')


def set_attrs(tag, changes):
    """Rewrite an opening tag: each change sets an attribute (in place when present) or removes it (value False)."""
    name, attrs, selfclose = parse_tag(tag)
    seen = set()
    out = []
    for k, v in attrs:
        if k in changes:
            seen.add(k)
            if changes[k] is False:
                continue
            v = changes[k]
        out.append([k, v])
    out += [[k, v] for k, v in changes.items() if k not in seen and v is not False]
    return make_tag(name, out, selfclose)


def attr(tag, name):
    for k, v in parse_tag(tag)[1]:
        if k == name:
            return v
    return None


def classes(tag):
    return (attr(tag, 'class') or '').split()


def kb(n):
    return '%.0f KB' % (n / 1024) if n < 1024 * 1024 else '%.1f MB' % (n / 1024 / 1024)


# ---------- reading the deck's structure ----------

PCX_PARTS = {'pcx-hbar', 'pcx-share', 'pcx-flow'}


class Scan(HTMLParser):
    """Finds slides, charts, marks, code, icons and the snippet parts (snippets/: pcx-hbar, pcx-share, pcx-flow)
    with their offsets in the source, for the drawn-in copy."""
    TRACK = ('section', 'article', 'div', 'figure', 'span', 'pre', 'code', 'i')

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.starts = [0] + [m.end() for m in re.finditer('\n', text)]
        self.slides, self.charts, self.marks, self.codes, self.icons, self.pcx = [], [], [], [], [], []
        self.open = {t: [] for t in self.TRACK}
        self.slide = self.chart = self.pre = None

    def pos(self):
        line, col = self.getpos()
        return self.starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag not in self.TRACK and tag not in ('figcaption', 'table'):
            return
        start, raw = self.pos(), self.get_starttag_text()
        assert self.text[start:start + len(raw)] == raw, 'scanner lost its place at %d' % start
        rec = {'start': start, 'open_end': start + len(raw), 'tag': raw}
        cls = dict(attrs).get('class', '') or ''
        cls = cls.split()
        kind = None
        if tag in ('section', 'article', 'div') and 'pc-slide' in cls and self.slide is None:
            kind, self.slide = 'slide', rec
            rec['has_num'] = False
            self.slides.append(rec)
        elif tag == 'div' and PCX_PARTS.intersection(cls):
            self.pcx.append(rec)
        elif tag == 'figure' and 'pc-chart' in cls:
            kind, self.chart = 'chart', rec
            self.charts.append(rec)
        elif tag == 'span' and 'pc-mark' in cls and 'data-mark' in dict(attrs):
            kind = 'mark'
            self.marks.append(rec)
        elif tag == 'pre' and 'pc-code' in cls:
            kind, self.pre = 'pre', rec
            self.codes.append(rec)
        elif tag == 'code' and self.pre is not None and 'code_start' not in self.pre:
            kind = 'code'
            self.pre['code_start'] = rec['open_end']
        elif tag == 'i' and 'pc-icon' in cls and dict(attrs).get('data-icon'):
            kind = 'icon'
            rec['name'] = dict(attrs)['data-icon']
            self.icons.append(rec)
        if tag in ('figcaption', 'table'):
            if self.chart is not None and 'insert_at' not in self.chart:
                self.chart['insert_at'] = start
            return
        if self.slide is not None and 'pc-num' in cls:
            self.slide['has_num'] = True
        self.open[tag].append((kind, rec))

    def handle_startendtag(self, tag, attrs):
        if tag in self.TRACK:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag not in self.TRACK or not self.open[tag]:
            return
        kind, rec = self.open[tag].pop()
        start = self.pos()
        end = self.text.index('>', start) + 1 if self.text.startswith('</', start) else start
        rec['close'], rec['close_end'] = start, end
        if kind == 'slide':
            self.slide = None
        elif kind == 'chart':
            self.chart = None
        elif kind == 'pre':
            self.pre = None
        elif kind == 'code':
            for p in self.codes:
                if p.get('code_start') == rec['open_end']:
                    p['code_end'] = start


# ---------- the probe: what Chrome draws and loads ----------

TITLE_EL = re.compile(r'(<(h[1-6]|p)\b[^>]*\bclass="[^"]*\bpc-(?:title|say)\b[^"]*"[^>]*>)(.*?)(</\2>)', re.S)
HYPHENED = re.compile(r'[^\s-]-[^\s-]')


def keep_hyphens(text):
    """A hyphenated word in a title goes in a nowrap span, as the runtime does, so viewers without scripts see the
    same line breaks ("co-op" stays whole)."""
    def title(m):
        parts, svg = re.split(r'(<[^>]+>)', m.group(3)), 0
        for k, part in enumerate(parts):
            if k % 2:
                svg += 1 if re.match(r'<svg\b', part) else -1 if part.startswith('</svg') else 0
                continue
            if svg or 'pc-nobr' in (parts[k - 1] if k else '') or not HYPHENED.search(part):
                continue
            parts[k] = ''.join(w if len(w) > 18 or not HYPHENED.search(w) else '<span class="pc-nobr">%s</span>' % w
                               for w in re.split(r'(\s+)', part))
        return m.group(1) + ''.join(parts) + m.group(4)
    return TITLE_EL.sub(title, text)


PROBE = r'''<script>
addEventListener('load', function () {
  var out = { faces: [], slides: [], charts: [], marks: [], code: [], pcx: [], missing: [], errors: window.__pcErrs || [] };
  var done = function () { var pre = document.createElement('pre'); pre.id = 'pc-probe'; pre.hidden = true; pre.textContent = JSON.stringify(out); document.body.appendChild(pre); };
  if (!window.PCDeck) { out.errors.push('The runtime did not start'); return done(); }
  PCDeck.ready().then(async function () {
    var deck = document.querySelector('.pc-deck');
    deck.querySelectorAll(':scope > .pc-slide').forEach(function (s) {
      out.slides.push({ n: s.dataset.n, side: s.dataset.side || null, section: s.dataset.sectionName === undefined ? null : s.dataset.sectionName,
        title: s.dataset.deckTitle || '', of: s.dataset.of || '', secn: s.dataset.secN || '', cycle: s.dataset.cycle, progress: s.style.getPropertyValue('--progress'),
        khero: s.style.getPropertyValue('--k-hero').trim(), kown: s.dataset.kHero === undefined ? null : s.dataset.kHero,
        kstat: s.style.getPropertyValue('--k-stat').trim(), kstatown: s.dataset.kStat === undefined ? null : s.dataset.kStat,
        role: s.getAttribute('role'), rd: s.getAttribute('aria-roledescription'), label: s.getAttribute('aria-label') });
    });
    deck.querySelectorAll('figure.pc-chart').forEach(function (f) {
      var svg = f.querySelector(':scope > svg'), lg = f.querySelector(':scope > .ch-legend');
      out.charts.push({ svg: svg ? svg.outerHTML : '', legend: lg ? lg.outerHTML : '', side: f.classList.contains('ch-side') });
    });
    deck.querySelectorAll('.pc-mark[data-mark]').forEach(function (m) { var s = m.querySelector(':scope > svg.pc-mark-svg'); out.marks.push(s ? s.outerHTML : ''); });
    deck.querySelectorAll('pre.pc-code').forEach(function (p) { var c = p.querySelector('code'); out.code.push(c ? { html: c.innerHTML, fit: p.dataset.fit || null, size: p.style.fontSize || null } : null); });
    deck.querySelectorAll('.pc-icon[data-missing]').forEach(function (i) { if (out.missing.indexOf(i.dataset.icon) < 0) out.missing.push(i.dataset.icon); });
    // Lay out the text that shows only later, so its faces load too: every slide's notes, the menu and the shortcut list.
    var box = document.createElement('div'); box.className = 'pc-notes-panel';
    box.style.cssText = 'display:block;visibility:hidden;position:absolute;left:0;top:0;width:1200px;height:auto;max-height:none;overflow:visible';
    box.innerHTML = Array.prototype.map.call(deck.querySelectorAll('.pc-notes'), function (n) { return n.innerHTML; }).join('');
    deck.appendChild(box);
    var dl = deck.querySelector('.pc-ui button[aria-controls="pc-download-menu"]'); if (dl) dl.click();
    deck.querySelectorAll('.pc-tip, .pc-menu, .pc-toast').forEach(function (e) { e.hidden = false; e.style.visibility = 'hidden'; if (!e.textContent.trim()) e.textContent = 'Saved 0123456789'; });
    await document.fonts.ready; await new Promise(function (r) { setTimeout(r, 150); }); await document.fonts.ready;
    document.fonts.forEach(function (f) { if (f.status === 'loaded') out.faces.push([f.family.replace(/^["']|["']$/g, ''), f.style, String(f.weight)]); });
    if (window.PCXParts) PCXParts.redraw();
    deck.querySelectorAll('div.pcx-hbar, div.pcx-share, div.pcx-flow').forEach(function (p) { out.pcx.push(p.getAttribute('data-done') ? p.outerHTML : ''); });
  }).catch(function (e) { out.errors.push(String(e)); }).then(done);
});
</script>'''

CHECK = r'''<script>
addEventListener('load', function () {
  var out = { errors: window.__pcErrs || [] };
  var done = function () { var pre = document.createElement('pre'); pre.id = 'pc-probe'; pre.hidden = true; pre.textContent = JSON.stringify(out); document.body.appendChild(pre); };
  if (!window.PCDeck) { out.errors.push('The runtime did not start'); return done(); }
  PCDeck.ready().then(function () {
    out.slides = PCDeck.count; out.chapters = document.querySelectorAll('.pc-chapter').length; out.loaded = []; out.failed = [];
    document.fonts.forEach(function (f) { var id = f.family.replace(/^["']|["']$/g, '') + ' ' + f.weight + (f.style === 'italic' ? ' italic' : ''); if (f.status === 'error') out.failed.push(id); else if (f.status === 'loaded') out.loaded.push(id); });
    out.missing = Array.prototype.map.call(document.querySelectorAll('.pc-icon[data-missing]'), function (i) { return i.dataset.icon; });
    var figs = document.querySelectorAll('figure.pc-chart');
    out.charts = [figs.length, Array.prototype.filter.call(figs, function (f) { return f.querySelector(':scope > svg'); }).length];
  }).catch(function (e) { out.errors.push(String(e)); }).then(done);
});
</script>'''


def run_probe(src, text, size, script):
    if not chrome.find_chrome():
        return None
    tmp = chrome.temp_beside(src, chrome.inject(text, first=chrome.ERRORS, body=script), 'probe')
    try:
        dom = chrome.dump_dom(tmp, size=size)
    finally:
        tmp.unlink(missing_ok=True)
    m = re.search(r'<pre id="pc-probe"[^>]*>(.*?)</pre>', dom, re.S)
    return json.loads(html.unescape(m.group(1))) if m else None


def weight(w):
    w = str(w).split()[0]
    return {'normal': 400, 'bold': 700}.get(w) or int(float(w))


# ---------- drawing into the page ----------

OPEN_TAG = re.compile(r'<div(?:\s+[^\s=>]+(?:="[^"]*")?)*>')


def draw_in(text, report, icons, problems):
    sc = Scan(text)
    sc.feed(text)
    sc.close()
    patches = []
    for rec in sc.icons:
        name = rec['name']
        if name not in icons or 'close' not in rec or text[rec['open_end']:rec['close']].strip():
            continue
        tag = set_attrs(rec['tag'], {'data-drawn': name, 'aria-hidden': False if attr(rec['tag'], 'aria-label') else 'true'})
        patches.append((rec['start'], rec['close_end'], tag + '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
                        + icons[name] + '</svg></i>'))
    if report:
        def matched(part, recs, what):
            if len(report.get(part) or []) != len(recs):
                problems.add('Not drawn in for viewers without scripts: %s (Chrome found %d, the source has %d)'
                             % (what, len(report.get(part) or []), len(recs)))
                return []
            return list(zip(recs, report[part]))
        for rec, s in matched('slides', sc.slides, 'slide labels'):
            style = attr(rec['tag'], 'style') or ''
            if '--progress' not in style and s['progress']:
                style = (style.rstrip().rstrip(';') + '; ' if style.strip() else '') + '--progress: ' + s['progress']
            for var, now, own in (('hero', 'khero', 'kown'), ('stat', 'kstat', 'kstatown')):   # titles and figures the runtime stepped down
                if s.get(own) is not None and s[now] != s[own]:
                    style = re.sub(r'(^|;)\s*--k-%s\s*:[^;]*' % var, r'\1', style).strip().strip(';').strip()
                    style = (style + '; ' if style else '') + '--k-%s: %s' % (var, s[now])
            ch = {'data-n': s['n'], 'data-side': s['side'] or False, 'data-deck-title': s['title'], 'data-of': s.get('of') or False, 'data-sec-n': s.get('secn') or False, 'data-cycle': s['cycle'],
                  'data-section-name': False if s['section'] is None else s['section'], 'style': style or False}
            if s.get('kown') is not None and s['khero'] != s['kown']:
                ch['data-k-hero'] = s['kown']
            if s.get('kstatown') is not None and s['kstat'] != s['kstatown']:
                ch['data-k-stat'] = s['kstatown']
            if attr(rec['tag'], 'aria-label') is None and s['label']:
                ch.update({'role': s['role'] or False, 'aria-roledescription': s['rd'] or False, 'aria-label': s['label']})
            patches.append((rec['start'], rec['open_end'], set_attrs(rec['tag'], ch)))
            if not rec['has_num'] and 'close' in rec:
                patches.append((rec['close'], rec['close'], '<span class="pc-num" aria-hidden="true">%s</span>' % html.escape(s['n'])))
        for rec, c in matched('charts', sc.charts, 'charts'):
            if c['svg'] and 'close' in rec:
                if c['side']:
                    patches.append((rec['start'], rec['open_end'], set_attrs(rec['tag'], {'class': ' '.join(classes(rec['tag']) + ['ch-side'])})))
                at = rec.get('insert_at', rec['close'])
                patches.append((at, at, c['svg'] + c['legend']))
        for rec, svg in matched('marks', sc.marks, 'hand-drawn marks'):
            if svg and 'close' in rec:
                patches.append((rec['close'], rec['close'], svg))
        for rec, code in matched('code', sc.codes, 'code colours'):
            if code is not None and 'code_end' in rec:
                ch = {'data-lit': '1', 'data-fit': code['fit'] or False}
                if code['size']:
                    style = (attr(rec['tag'], 'style') or '').strip().rstrip(';')
                    ch['style'] = (style + '; ' if style else '') + 'font-size: ' + code['size']
                patches.append((rec['start'], rec['open_end'], set_attrs(rec['tag'], ch)))
                patches.append((rec['code_start'], rec['code_end'], code['html']))
        # snippet parts: Chrome's drawn copy, with the source kept in a <template> that parts.js puts back and draws live
        for rec, drawn in matched('pcx', sc.pcx, 'snippet parts'):
            m = OPEN_TAG.match(drawn or '')
            if m and 'close_end' in rec:
                whole = (rec['start'], rec['close_end'])
                patches = [p for p in patches if not (whole[0] <= p[0] and p[1] <= whole[1]
                                                      and not (p[0] == p[1] and p[0] in whole))]
                patches.append(whole + (m.group(0) + '<template class="pcx-src">' + text[whole[0]:whole[1]] + '</template>'
                                        + drawn[m.end():],))
    patches.sort(key=lambda p: (p[0], p[1]), reverse=True)
    last = len(text) + 1
    for start, end, repl in patches:
        assert end <= last, 'overlapping changes at %d' % start
        text = text[:start] + repl + text[end:]
        last = start
    return text


# ---------- inlining ----------

def inline_urls(css, base, problems, counts):
    def rep(m):
        ref = m.group(2)
        if is_inline(ref):
            return m.group(0)
        if is_remote(ref):
            problems.add('Links to a file on the internet, so the built deck needs a connection: ' + ref)
            return m.group(0)
        p = resolve(ref, base)
        if not p.is_file():
            problems.add('Missing file: %s' % p)
            return m.group(0)
        counts['pictures'] = counts.get('pictures', 0) + 1
        return 'url("%s")' % data_uri(p)
    return URL_RE.sub(rep, css)


def theme_doc_css(tid, problems, counts):
    """A document's share of its theme: the motif pictures theme.css holds as custom properties (--pebble: url(data:...)),
    which the theme's doc.css draws with, and themes/<id>/doc.css itself. A theme without one looks right from tokens."""
    d = bt.folder(tid)
    out = ''
    if (d / 'theme.css').is_file():
        pics = re.findall(r'(--[a-z0-9-]+):\s*(url\("data:[^"]*"\))', (d / 'theme.css').read_text(encoding='utf-8'))
        if pics:
            out += style_block('.pc-doc[data-theme="%s"] { %s }' % (tid, ' '.join('%s: %s;' % kv for kv in pics)), pc='theme-pics', theme=tid)
        clips = re.search(r'/\* clip paths: .*?/\* end of clip paths \*/', (d / 'theme.css').read_text(encoding='utf-8'), re.S)
        if clips:
            out += style_block(clips.group(0), pc='theme-clips', theme=tid)
    if (d / 'doc.css').is_file():
        out += style_block(inline_urls((d / 'doc.css').read_text(encoding='utf-8'), d, problems, counts), pc='theme-doc', theme=tid)
    return out


def style_block(css, **data):
    if re.search(r'</style', css, re.I):
        sys.exit('A style sheet contains "</style", which would end the style block early')
    attrs = ''.join(' data-%s="%s"' % (k, html.escape(v)) for k, v in data.items())
    return '<style%s>\n%s\n</style>' % (attrs, css.strip())


def script_block(js, **data):
    js = re.sub(r'</(script)', r'<\\/\1', js, flags=re.I)
    if '<!--' in js:
        sys.exit('A script contains "<!--", which can upset the HTML parser; write it another way')
    attrs = ''.join(' data-%s="%s"' % (k, html.escape(v)) for k, v in data.items())
    return '<script%s>\n%s\n</script>' % (attrs, js.strip())


def noscript_css(fmt):
    w = FORMATS[fmt][0]
    zoom = lambda vw: '%.4f' % min(1, max(0.1, (vw - 32) / w))
    rules = ['html, body { height: auto !important; overflow: auto !important; }',
             '.pc-deck { position: static !important; inset: auto !important; width: auto !important; height: auto !important;'
             ' overflow: visible !important; display: flex !important; flex-direction: column; align-items: center; gap: 24px; padding: 24px 0; }',
             '.pc-deck > .pc-slide { position: relative !important; left: auto !important; top: auto !important; flex: none;'
             ' transform: none !important; visibility: visible !important; zoom: %s; }' % zoom(360)]
    out = '@media screen {\n  ' + '\n  '.join(rules) + '\n}'
    for vw in (480, 640, 800, 1024, 1280, 1440, 1600, 1920, 2240, 2560):
        out += '\n@media screen and (min-width: %dpx) { .pc-deck > .pc-slide { zoom: %s; } }' % (vw, zoom(vw))
    return out


def static_problems(out):
    """References a single file must not have, looked for outside scripts."""
    found = []
    bare = re.sub(r'(<script\b[^>]*>).*?(</script\s*>)', r'\1\2', out, flags=re.S | re.I)
    tags = re.sub(r'(<style\b[^>]*>).*?(</style\s*>)', r'\1\2', bare, flags=re.S | re.I)
    for m in re.finditer(r'<(link|script|img|image|source|video|audio|iframe|embed|object)\b[^>]*>', tags, re.I):
        for k, v in parse_tag(m.group(0))[1]:
            if k.lower() in ('src', 'href', 'xlink:href', 'poster', 'data') and v and not is_inline(v):
                if m.group(1).lower() == 'link' and (attr(m.group(0), 'rel') or '').lower() in ('canonical', 'author', 'license'):
                    continue
                found.append('<%s %s="%s">' % (m.group(1), k, v[:120]))
    sheets = [re.sub(r'/\*.*?\*/', '', c, flags=re.S) for c in re.findall(r'<style\b[^>]*>(.*?)</style\s*>', bare, re.S | re.I)]
    for css in sheets + re.findall(r'\sstyle="([^"]*)"', tags):
        for m in URL_RE.finditer(html.unescape(css)):
            if not is_inline(m.group(2)):
                found.append('url(%s)' % m.group(2)[:120])
    return found


# ---------- the build ----------

def build(src, out=None, theme_id=None, palette=None, mode=None, fmt=None, motion=None, variants=False,
          all_faces=False, probe=True, check=True, quiet=False):
    src = Path(src).resolve()
    base = src.parent
    text = src.read_text(encoding='utf-8')
    problems, counts = Problems(), {}
    say = (lambda *a: None) if quiet else print

    m = DECK_RE.search(text)
    if not m:
        sys.exit('%s has no <div class="pc-deck"> (or <main class="pc-deck">, or <html class="pc-deck pc-doc"> for a document)' % src.name)
    deck = {k: v for k, v in parse_tag(m.group(0))[1]}
    is_doc = 'pc-doc' in classes(m.group(0))
    asked = {'data-theme': theme_id, 'data-palette': palette, 'data-mode': mode, 'data-format': fmt}
    tid = theme_id or deck.get('data-theme')
    if not tid or not (bt.folder(tid) / 'theme.json').is_file():
        sys.exit('Unknown theme %r. Themes: %s' % (tid, ', '.join(bt.theme_ids())))
    theme = bt.load(tid)
    if theme.get('custom') and not (theme['custom'].get('checked') or {}).get('passed'):
        print('Note: %s is a custom theme that has not passed its check (python3 tools/make_theme.py --check %s); '
              'tools/publish.py will not publish decks in it until it does.' % (tid, tid), file=sys.stderr)
    pal = palette or deck.get('data-palette')
    if pal not in theme['palettes']:
        if palette:
            sys.exit('%s has no palette %r. Palettes: %s' % (theme['name'], pal, ', '.join(theme['palettes'])))
        if pal:
            print('Note: %s has no palette %r, so the build uses %s. Palettes: %s' % (
                theme['name'], pal, theme['defaults']['palette'], ', '.join(theme['palettes'])), file=sys.stderr)
        pal = theme['defaults']['palette']
    # documents print light unless they ask for dark (data-mode or --mode), whatever the theme's slides default to
    mode = mode or deck.get('data-mode') or (theme['defaults'].get('docMode', 'light') if is_doc else theme['defaults']['mode'])
    fmt = fmt or deck.get('data-format') or '16x9'
    motion = motion or deck.get('data-motion') or 'basic'
    if mode not in bt.MODES or fmt not in FORMATS or motion not in MOTIONS:
        sys.exit('Mode is light or dark; format one of %s; motion one of %s' % (', '.join(FORMATS), ', '.join(MOTIONS)))
    if is_doc:   # a document's page comes from data-page and data-orient, which the runtime reads
        fmt, motion = 'doc', 'static'
        text = text[:m.start()] + set_attrs(m.group(0), {'data-theme': tid, 'data-palette': pal, 'data-mode': mode}) + text[m.end():]
    else:
        text = text[:m.start()] + set_attrs(m.group(0), {'data-theme': tid, 'data-palette': pal, 'data-mode': mode,
                                                         'data-format': fmt, 'data-motion': motion}) + text[m.end():]
    tdir = bt.folder(tid)
    if tdir == bt.THEMES / tid:
        text = re.sub(r'(themes/)[a-z0-9-]+(/(?:tokens|theme|doc)\.css)', lambda x: x.group(1) + tid + x.group(2), text)
    else:   # a theme outside the kit: link its own files, so the probe loads them too
        text = re.sub(r'(href=["\'])[^"\']*themes/[a-z0-9-]+/((?:tokens|theme|doc)\.css)', lambda x: x.group(1) + (tdir / x.group(2)).as_uri(), text)
    view = DOC_VIEW if is_doc else FORMATS[fmt]

    text = keep_hyphens(text)
    if 'data-qr=' in text:   # QR codes become inline SVG (tools/qr.py, segno)
        import qr
        text = qr.inline_all(text)
    # a theme or palette drawn from an open one keeps its notice in a hidden comment beside its inlined CSS; nothing
    # the reader sees names it (SKILL.md, Content rules: no credits in the work)
    credit = '. '.join(lbl + c for lbl, c in (('Theme: ', theme.get('credit')), ('Palette: ', theme['palettes'][pal].get('credit'))) if c)
    if credit:
        note = '<!-- %s -->' % credit.replace('--', '- -')
        if note not in text:
            text = re.sub(r'(<head[^>]*>)', lambda m: m.group(1) + note, text, count=1, flags=re.I)

    # What Chrome draws and loads for this deck
    report = run_probe(src, text, view, PROBE) if probe else None
    if probe and report is None:
        problems.add('Chrome could not read the deck, so every face of the theme is embedded and nothing is drawn in ahead')
    if report and report.get('errors'):
        problems.add('Script errors in the source deck: ' + '; '.join(report['errors'][:5]))

    # Fonts
    manifest = json.loads((FONTS / 'fonts.json').read_text(encoding='utf-8'))
    wanted = {k: bool(re.search(rx, text)) for k, rx in SCRIPTS.items()}
    faces = {}
    for fam in bt.families(theme):
        if fam.startswith('Noto') and not any(fam.endswith(k) and hit for k, hit in wanted.items()):
            continue
        for f in manifest[fam]['faces']:
            faces[(fam, f['style'], int(f['weight']))] = f['file']
    if report and report.get('faces') and not all_faces:
        loaded = {(f, s, weight(w)) for f, s, w in report['faces']}
        faces = {k: v for k, v in faces.items() if k in loaded}
    font_bytes = 0

    def face(fm):
        nonlocal font_bytes
        file = faces.get((fm.group(1), fm.group(2), int(fm.group(3))))
        if not file:
            return ''
        data = woff((FONTS / file).read_bytes())
        font_bytes += len(data)
        uri = 'data:font/woff;base64,' + base64.b64encode(data).decode('ascii')
        return fm.group(0).replace(fm.group(4), uri).replace('format("truetype")', 'format("woff")')

    tokens, _ = bt.theme_css(theme, manifest, modes=bt.MODES if variants else (mode,), palettes=None if variants else [pal])
    tokens = FACE_RE.sub(face, tokens)

    # Icons, drawn in as well as shipped for the runtime
    names = sorted(set(re.findall(r'\bdata-icon\s*=\s*"([^"]+)"', text)))
    icons = build_icons.load_icons()
    unknown = [n for n in names if n not in icons]
    if unknown:
        problems.add('Unknown icon names (see icons/lucide-sprite.svg for the 1,866 names): ' + ', '.join(unknown))
    names = [n for n in names if n in icons]
    text = draw_in(text, report, icons, problems)

    # The deck's own style blocks and inline styles point at pictures beside the deck
    text = re.sub(r'(<style\b[^>]*>)(.*?)(</style\s*>)', lambda x: x.group(1) + inline_urls(x.group(2), base, problems, counts) + x.group(3),
                  text, flags=re.S | re.I)
    text = re.sub(r'(\sstyle=")([^"]*)(")', lambda x: x.group(1) + html.escape(inline_urls(html.unescape(x.group(2)), base, problems, counts), quote=True) + x.group(3), text)

    def media(mt):
        tag = mt.group(0)
        name = mt.group(1).lower()
        ch = {}
        for k, v in parse_tag(tag)[1]:
            if v is None or is_inline(v):
                continue
            kl = k.lower()
            if kl in ('src', 'href', 'xlink:href', 'poster') and name in ('img', 'image', 'source', 'video', 'input'):
                if is_remote(v):
                    problems.add('Picture on the internet, so the built deck needs a connection: ' + v)
                    continue
                p = resolve(v, base)
                if p.suffix.lower() not in MIME or MIME[p.suffix.lower()].startswith('font'):
                    problems.add('Not inlined (only pictures are): ' + v)
                    continue
                if not p.is_file():
                    problems.add('Missing picture: %s' % p)
                    continue
                ch[k] = data_uri(p)
                counts['pictures'] = counts.get('pictures', 0) + 1
            elif kl == 'srcset':
                problems.add('srcset is not inlined; use src: ' + v[:80])
        return set_attrs(tag, ch) if ch else tag
    text = re.sub(r'<(img|image|source|video|input)\b[^>]*>', media, text, flags=re.I)

    # Style sheets and scripts
    def link(lm):
        tag = lm.group(0)
        rel = (attr(tag, 'rel') or '').lower().split()
        href = attr(tag, 'href') or ''
        if 'icon' in rel and href and not is_inline(href) and not is_remote(href):
            p = resolve(href, base)
            return set_attrs(tag, {'href': data_uri(p)}) if p.is_file() else tag
        if 'stylesheet' not in rel or is_inline(href):
            return tag
        if is_remote(href):
            problems.add('Style sheet on the internet, so the built deck needs a connection: ' + href)
            return tag
        p = resolve(href, base)
        posix = p.as_posix()
        own = p.parent == tdir or bool(re.search(r'/themes/[a-z0-9-]+/(?:tokens|theme|doc)\.css$', posix))
        if own and p.name == 'tokens.css':
            return style_block(tokens, pc='tokens', theme=tid)
        if not p.is_file():
            sys.exit('%s links a style sheet that is not there: %s' % (src.name, p))
        css = inline_urls(p.read_text(encoding='utf-8'), p.parent, problems, counts)
        if posix.endswith('/engine/core.css'):
            return style_block(css, pc='core')
        if posix.endswith('/engine/doc.css'):   # a document also takes its theme's motif pictures and themes/<id>/doc.css
            return style_block(css, pc='doc') + theme_doc_css(tid, problems, counts)
        if own and p.name == 'theme.css':
            return style_block(css, pc='theme', theme=tid)
        if own and p.name == 'doc.css':   # comes with engine/doc.css, for the theme the build uses
            return ''
        return style_block(css, pc='deck')
    text = re.sub(r'<link\b[^>]*>', link, text, flags=re.I)

    def script(sm):
        tag = sm.group(1)
        srcref = attr(tag, 'src')
        if not srcref or is_inline(srcref):
            return sm.group(0)
        if is_remote(srcref):
            problems.add('Script on the internet, so the built deck needs a connection: ' + srcref)
            return sm.group(0)
        p = resolve(srcref, base)
        if p.as_posix().endswith('/icons/lucide.js'):
            return script_block(build_icons.icon_script(names), pc='icons')
        if not p.is_file():
            sys.exit('%s links a script that is not there: %s' % (src.name, p))
        js = p.read_text(encoding='utf-8')
        return script_block(js, pc='runtime' if p.as_posix().endswith('/engine/runtime.js') else 'deck')
    text = re.sub(r'(<script\b[^>]*>)\s*</script\s*>', script, text, flags=re.I)

    # Page size, viewer without scripts, head basics
    text = re.sub(r'<style\b[^>]*\bid="pc-page"[^>]*>.*?</style\s*>', '', text, flags=re.S | re.I)
    if is_doc:   # the runtime writes the page rules (#pc-doc-pages) from the document's own attributes
        head = ''
    else:
        page = PAGE.get(fmt) or '%dpx %dpx' % FORMATS[fmt]
        head = ('<style id="pc-page" data-size="%s">@page { size: %s; margin: 0; }</style>\n' % (page, page)
                + '<noscript>' + style_block(noscript_css(fmt), pc='noscript') + '</noscript>\n')
    if not re.search(r'<meta\b[^>]*name="viewport"', text, re.I):
        head = '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + head
    title = deck.get('data-title')
    if not re.search(r'<title\b', text, re.I) and title:
        head = '<title>%s</title>\n' % html.escape(title) + head
    text = chrome.inject(text, head=head)
    if not re.search(r'<meta\b[^>]*charset', text, re.I):
        text = chrome.inject(text, first='<meta charset="utf-8">')

    left = static_problems(text)
    if left:
        problems.add('Still refers to outside files: ' + '; '.join(left[:8]))

    if out is None:
        extra = [v for k, v in asked.items() if v and v != deck.get(k)]
        out = base / 'dist' / (src.stem + ''.join('-' + x for x in extra) + '.html')
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')

    size = out.stat().st_size
    if is_doc:
        say('Built %s: %s (document, %s theme, %s palette, %s, %s page)' % (out, kb(size), theme['name'], pal, mode, deck.get('data-page') or 'a4'))
    else:
        say('Built %s: %s (%s theme, %s palette, %s, %s, %s motion)' % (out, kb(size), theme['name'], pal, mode, fmt, motion))
    say('  fonts %s in %d faces: %s' % (kb(font_bytes * 4 / 3), len(faces), ', '.join(
        '%s %d%s' % (f, w, ' italic' if s == 'italic' else '') for f, s, w in sorted(faces))))
    say('  %d icons, %d pictures%s' % (len(names), counts.get('pictures', 0), ', every mode and palette' if variants else ''))

    result = {'path': out, 'bytes': size, 'faces': sorted(faces), 'icons': names, 'problems': problems}
    if check:
        rep = run_probe(out, out.read_text(encoding='utf-8'), view, CHECK)
        if rep is None:
            problems.add('Could not open the built file in Chrome to check it')
        else:
            result['check'] = rep
            if rep.get('errors'):
                problems.add('Script errors in the built file: ' + '; '.join(rep['errors'][:5]))
            if rep.get('failed'):
                problems.add('Fonts that failed to load: ' + ', '.join(rep['failed']))
            if rep.get('missing'):
                problems.add('Icons missing: ' + ', '.join(sorted(set(rep['missing']))))
            if rep.get('charts') and rep['charts'][0] != rep['charts'][1]:
                problems.add('Charts not drawn: %d of %d' % (rep['charts'][0] - rep['charts'][1], rep['charts'][0]))
            ch = rep.get('charts') or [0, 0]
            say('  checked in Chrome: %d %s, %d faces loaded, %d of %d charts drawn, %s'
                % (rep.get('slides', 0) if not is_doc else rep.get('chapters', 0), 'chapters' if is_doc else 'slides', len(rep.get('loaded', [])), ch[1], ch[0],
                   'script errors (below)' if rep.get('errors') else 'no script errors'))
    for p in problems:
        say('  ! ' + p)
    return result


def main():
    ap = argparse.ArgumentParser(description='Build one self-contained HTML file from a kit deck.')
    ap.add_argument('deck')
    ap.add_argument('-o', '--out')
    ap.add_argument('--theme')
    ap.add_argument('--theme-dir', help='a theme kept outside themes/ (a job\'s style folder); builds in it unless --theme names another')
    ap.add_argument('--palette')
    ap.add_argument('--mode', choices=bt.MODES)
    ap.add_argument('--format', choices=list(FORMATS))
    ap.add_argument('--motion', choices=MOTIONS)
    ap.add_argument('--variants', action='store_true', help='keep every mode and palette of the theme')
    ap.add_argument('--all-faces', action='store_true', help='embed every face of the theme, not only those the deck uses')
    ap.add_argument('--no-probe', action='store_true', help='skip the Chrome run that finds faces and draws charts in ahead')
    ap.add_argument('--no-check', action='store_true', help='skip opening the built file in Chrome')
    a = ap.parse_args()
    if a.theme_dir:
        tid = bt.add_dir(a.theme_dir)
        a.theme = a.theme or tid
    r = build(a.deck, a.out, a.theme, a.palette, a.mode, a.format, a.motion, a.variants, a.all_faces,
              not a.no_probe, not a.no_check)
    sys.exit(1 if any(p.startswith(('Script errors', 'Fonts that failed', 'Still refers')) for p in r['problems']) else 0)


if __name__ == '__main__':
    main()
