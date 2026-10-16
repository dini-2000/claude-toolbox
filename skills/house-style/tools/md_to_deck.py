#!/usr/bin/env python3
"""Turn a Markdown outline into a kit deck (deck source HTML), to build with tools/build.py.

    python3 tools/md_to_deck.py talk.md                 writes talk.html beside it
    python3 tools/md_to_deck.py talk.md -o decks/talk/talk.html --theme folio --format 4x5

The Markdown follows Marp and md-slides: slides split on '---' lines (or on '# ' headings when there are fewer than
three such lines), an optional front matter block first (title, theme, palette, mode, format, motion, lang), and
speaker notes in <!-- notes: ... --> blocks (speaker-notes: and presenter: work too). Each slide's layout comes from
its content, or from a <!-- layout: name --> line, with name one of:

    cover      first slide: '# Title', a line of text (subtitle), then '- ' items for the meta line
    section    '# Title' alone, or '## 01' then '# Title'
    content    a title with paragraphs, '- ' bullets or '1. ' steps ('**Step** text' items become numbered steps)
    stats      '- **4.6 t** of produce logged' items, two to four of them
    big-number one '**1.2 t**' line, then text
    statement  one sentence and nothing else (a title-less slide)
    quote      a '> ' blockquote, then '-- Name, role'
    checklist  '- [x] done' and '- [ ] to do' items
    table      a Markdown table (right-aligned columns become figures)
    code       a fenced code block, with text beside it if there is any
    cards      '### Heading' then a paragraph, two to four times
    split      text and one picture ('![alt](src)'), the picture on the side
    bleed      a picture and a title only: the picture fills the slide
    closing    last slide, with layout: closing; '- **Label** value' items become the contact lines

Any slide: '###### text' or <!-- kicker: text --> sets the kicker; <!-- surface: accent|inverse|alt --> its surface;
<!-- build: rise|fade|pop --> builds its list items one by one; <!-- section: name --> names the running head's section
from that slide on (section slides name it already). Raw HTML lines pass through untouched, so kit
markup (charts, timelines, compare panels) can sit in the Markdown as it is. Inline: **bold**, *italic*, `code`,
[links](url), ==highlight== (an accent mark).

The result is a starting point: read it, pick icons and charts where they help, then build and QC it as usual.
"""
import argparse
import html
import os
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
LAYOUTS = ('cover', 'section', 'content', 'stats', 'big-number', 'statement', 'quote', 'checklist', 'table', 'code',
           'cards', 'split', 'bleed', 'closing')
DECK_KEYS = ('title', 'theme', 'palette', 'mode', 'format', 'motion', 'lang')
NOTES = re.compile(r'<!--\s*(?:notes|speaker-notes|presenter)\s*:?\s*([\s\S]*?)-->', re.I)
DIRECTIVE = re.compile(r'<!--\s*(layout|kicker|surface|build|section)\s*:\s*([\s\S]*?)\s*-->', re.I)
FENCE = re.compile(r'^(```|~~~)')
WHERE = {}                                           # src: the Markdown's folder, out: the deck's folder


# ---------------------------------------------------------------- splitting
def front_matter(text):
    m = re.match(r'\A---\s*\n([\s\S]*?)\n---\s*\n', text)
    if not m or not re.search(r'^\w+\s*:', m.group(1), re.M):
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':')
        if k.strip().lower() in DECK_KEYS and v.strip():
            meta[k.strip().lower()] = v.strip().strip('"\'')
    return meta, text[m.end():]


def split_slides(text):
    lines, fence, hr, h1 = text.splitlines(), False, [], []
    for i, l in enumerate(lines):
        if FENCE.match(l.strip()):
            fence = not fence
        elif not fence and re.fullmatch(r'\s*---+\s*', l):
            hr.append(i)
        elif not fence and re.match(r'# ', l):
            h1.append(i)
    if len(hr) >= 3 or not h1:
        cuts, skip = hr, True
    else:
        cuts, skip = [], False
        for i in (i for i in h1 if i > 0):
            while i > 0 and (not lines[i - 1].strip() or DIRECTIVE.fullmatch(lines[i - 1].strip())):
                i -= 1
            cuts.append(i)
    out, start = [], 0
    for c in cuts + [len(lines)]:
        chunk = '\n'.join(lines[start:c]).strip()
        if chunk:
            out.append(chunk)
        start = c + 1 if skip else c
    return out


# ---------------------------------------------------------------- inline Markdown
def inline(s):
    keep = []
    def stash(m):
        keep.append(m.group(0))
        return '\x00%d\x00' % (len(keep) - 1)
    s = re.sub(r'<[^>]+>|&\w+;|&#\d+;', stash, s)                     # raw tags and entities pass through
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    s = re.sub(r'(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)', r'<em>\1</em>', s)
    s = re.sub(r'==(.+?)==', r'<span class="pc-mark" data-mark="highlight">\1</span>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: '<a href="%s">%s</a>' % (html.escape(m.group(2)), m.group(1)), s)
    s = s.replace(' -- ', ', ')
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- reading a slide
def blocks(body):
    """The slide body as typed blocks: h1..h6, p, ul, ol, quote, code, table, img, html."""
    out, lines, i = [], body.splitlines(), 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if not s:
            i += 1
            continue
        if FENCE.match(s):
            lang, j = s[3:].strip(), i + 1
            while j < len(lines) and not lines[j].strip().startswith(s[:3]):
                j += 1
            out.append(('code', lang, '\n'.join(lines[i + 1:j])))
            i = j + 1
            continue
        m = re.match(r'(#{1,6})\s+(.*)', s)
        if m:
            out.append(('h%d' % len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        m = re.fullmatch(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)', s)
        if m:
            out.append(('img', m.group(1), m.group(2)))
            i += 1
            continue
        if s.startswith('<') and not s.startswith('<!--'):
            j = i
            while j < len(lines) and lines[j].strip():
                j += 1
            out.append(('html', '\n'.join(lines[i:j])))
            i = j
            continue
        if s.startswith('|'):
            j = i
            while j < len(lines) and lines[j].strip().startswith('|'):
                j += 1
            out.append(('table', lines[i:j]))
            i = j
            continue
        if s.startswith('>'):
            j, q = i, []
            while j < len(lines) and lines[j].strip().startswith('>'):
                q.append(lines[j].strip()[1:].strip())
                j += 1
            out.append(('quote', ' '.join(q)))
            i = j
            continue
        m = re.match(r'([-*+]|\d+[.)])\s+', s)
        if m:
            kind, items, j = ('ol' if m.group(1)[0].isdigit() else 'ul'), [], i
            while j < len(lines) and lines[j].strip():
                t = lines[j].strip()
                mm = re.match(r'([-*+]|\d+[.)])\s+(.*)', t)
                if mm:
                    items.append(mm.group(2))
                elif items:
                    items[-1] += ' ' + t
                j += 1
            out.append((kind, items))
            i = j
            continue
        if BIG.fullmatch(s):
            out.append(('p', s))
            i += 1
            continue
        j, para = i, []
        while j < len(lines) and lines[j].strip() and not BIG.fullmatch(lines[j].strip()) and not re.match(r'(#{1,6}\s|[-*+]\s|\d+[.)]\s|>|\||```|~~~|!\[)', lines[j].strip()):
            para.append(lines[j].strip())
            j += 1
        out.append(('p', ' '.join(para)))
        i = j
    return out


BIG = re.compile(r'\*\*[^*]{1,10}\*\*')
STAT_ITEM = re.compile(r'\*\*([^*]{1,14})\*\*\s*[,:]?\s*(.*)')


def guess(bl, n, total):
    kinds = [b[0] for b in bl]
    heads = [b for b in bl if b[0] in ('h1', 'h2')]
    rest = [b for b in bl if b[0] not in ('h1', 'h2', 'h6')]
    lists = [b for b in bl if b[0] in ('ul', 'ol')]
    if n == 0:
        return 'cover'
    if heads and not rest:
        return 'section'
    if not heads and kinds == ['p'] and len(bl[0][1]) < 160:
        return 'statement'
    if 'quote' in kinds and len(rest) <= 2:
        return 'quote'
    if 'img' in kinds:
        return 'bleed' if not [b for b in rest if b[0] != 'img'] else 'split'
    if 'code' in kinds:
        return 'code'
    if 'table' in kinds:
        return 'table'
    if lists and all(re.match(r'\[[ xX]\]\s', it) for it in lists[0][1]):
        return 'checklist'
    if any(b[0] == 'p' and BIG.fullmatch(b[1]) for b in rest):
        return 'big-number'
    if lists and 2 <= len(lists[0][1]) <= 4 and all(STAT_ITEM.fullmatch(it) and re.search(r'\d', STAT_ITEM.fullmatch(it).group(1)) for it in lists[0][1]):
        return 'stats'
    if kinds.count('h3') >= 2 and not lists:
        return 'cards'
    return 'content'


# ---------------------------------------------------------------- writing a slide
def title_of(bl, tag='h2'):
    h = next((b for b in bl if b[0] in ('h1', 'h2')), None)
    return '  <%s class="pc-title">%s</%s>\n' % (tag, inline(h[1]), tag) if h else ''


def body_blocks(bl, build=None, skip=('h1', 'h2', 'h6')):
    out = []
    for b in bl:
        k = b[0]
        if k in skip:
            continue
        if k == 'p':
            out.append('<p>%s</p>' % inline(b[1]))
        elif k in ('h3', 'h4', 'h5'):
            out.append('<h3 class="pc-h3">%s</h3>' % inline(b[1]))
        elif k == 'ul':
            out.append('<ul class="pc-list"%s>\n%s\n    </ul>' % (' data-build-each="%s"' % build if build else '',
                       '\n'.join('      <li>%s</li>' % inline(it) for it in b[1])))
        elif k == 'ol':
            steps = all(re.match(r'\*\*[^*]+\*\*', it) for it in b[1])
            if steps:
                lis = []
                for it in b[1]:
                    m = re.match(r'\*\*([^*]+)\*\*[\s:.,-]*(.*)', it)
                    lis.append('      <li><b>%s</b>%s</li>' % (inline(m.group(1)), '<p>%s</p>' % inline(m.group(2)) if m.group(2) else ''))
                out.append('<ol class="pc-steps"%s>\n%s\n    </ol>' % (' data-build-each="%s"' % build if build else '', '\n'.join(lis)))
            else:
                out.append('<ol class="pc-list"%s>\n%s\n    </ol>' % (' data-build-each="%s"' % build if build else '',
                           '\n'.join('      <li>%s</li>' % inline(it) for it in b[1])))
        elif k == 'html':
            out.append(b[1])
        elif k == 'code':
            out.append('<pre class="pc-code"%s><code>%s</code></pre>' % (' data-lang="%s"' % esc(b[1]) if b[1] else '', html.escape(b[2])))
        elif k == 'table':
            out.append(table(b[1]))
        elif k == 'quote':
            out.append('<p class="pc-lead">%s</p>' % inline(b[1]))
    return out


def table(rows):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    align = []
    if len(cells) > 1 and all(re.fullmatch(r':?-+:?', c) for c in cells[1]):
        align = [c.endswith(':') and not c.startswith(':') for c in cells[1]]
        head, body = cells[0], cells[2:]
    else:
        head, body = None, cells
    num = lambda k: ' class="is-num"' if k < len(align) and align[k] else ''  # noqa: E731
    out = ['<table class="pc-table">']
    if head:
        out.append('      <thead><tr>%s</tr></thead>' % ''.join('<th%s>%s</th>' % (num(k), inline(c)) for k, c in enumerate(head)))
    out.append('      <tbody>')
    for r in body:
        total = r and re.fullmatch(r'\*\*.*\*\*', r[0])
        out.append('        <tr%s>%s</tr>' % (' class="pc-total"' if total else '', ''.join(
            '<td%s>%s</td>' % (num(k), inline(re.sub(r'^\*\*(.*)\*\*$', r'\1', c) if total else c)) for k, c in enumerate(r))))
    out.append('      </tbody>\n    </table>')
    return '\n'.join(out)


def picture(src):
    """A picture path relative to the Markdown, made relative to the deck instead."""
    if re.match(r'[a-z]+:|/|#', src) or not WHERE or not (WHERE['src'] / src).exists():
        return src
    return os.path.relpath(WHERE['src'] / src, WHERE['out']).replace(os.sep, '/')


def slide(chunk, n, total):
    notes = '\n\n'.join(m.group(1).strip() for m in NOTES.finditer(chunk))
    chunk = NOTES.sub('', chunk)
    d = {k.lower(): v.strip() for k, v in DIRECTIVE.findall(chunk)}
    chunk = DIRECTIVE.sub('', chunk)
    bl = blocks(chunk)
    kicker = d.get('kicker') or next((b[1] for b in bl if b[0] == 'h6'), None)
    layout = d.get('layout') or guess(bl, n, total)
    if layout not in LAYOUTS:
        sys.exit('Slide %d: no layout %r (one of %s)' % (n + 1, layout, ', '.join(LAYOUTS)))
    build = d.get('build')
    cls, attrs, inner = ['pc-slide'], [], ''
    kick = '  <p class="pc-kicker">%s</p>\n' % inline(kicker) if kicker else ''
    rest = [b for b in bl if b[0] not in ('h1', 'h2', 'h6')]

    if layout == 'cover':
        cls.append('pc-cover')
        meta = next((b[1] for b in rest if b[0] == 'ul'), [])
        sub = next((b[1] for b in rest if b[0] == 'p'), None)
        inner = kick + title_of(bl, 'h1') + ('  <p class="pc-sub">%s</p>\n' % inline(sub) if sub else '')
        if meta:
            inner += '  <div class="pc-meta">%s</div>\n' % ''.join('<span>%s</span>' % inline(m) for m in meta)
    elif layout == 'section':
        cls.append('pc-section')
        num = next((b[1] for b in bl if b[0] in ('h1', 'h2') and re.fullmatch(r'\d{1,2}', b[1])), None)
        heads = [b for b in bl if b[0] in ('h1', 'h2') and b[1] != num]
        inner = ('  <p class="pc-section-num">%s</p>\n' % esc(num) if num else '') + title_of(heads)
    elif layout == 'statement':
        cls.append('pc-statement')
        attrs.append('data-surface="%s"' % d.get('surface', 'accent'))
        text = ' '.join(b[1] for b in rest if b[0] == 'p') or next((b[1] for b in bl if b[0] in ('h1', 'h2')), '')
        inner = '  <p class="pc-say">%s</p>\n' % inline(text)
    elif layout == 'quote':
        q = next(b[1] for b in rest if b[0] == 'quote')
        who = next((b[1] for b in rest if b[0] == 'p'), '')
        who = re.sub(r'^(--|—|-)\s*', '', who)
        name, _, role = who.partition(',')
        cap = ('\n      <figcaption><span><b>%s</b>%s</span></figcaption>' % (inline(name.strip()), inline(role.strip()))) if name else ''
        inner = kick + title_of(bl) + ('  <div class="pc-body pc-body--center">\n    <figure class="pc-quote">\n      <blockquote>%s</blockquote>%s\n'
                                       '    </figure>\n  </div>\n' % (inline(q), cap))
    elif layout == 'stats':
        items = next(b[1] for b in rest if b[0] == 'ul')
        cells = []
        for it in items:
            m = STAT_ITEM.fullmatch(it)
            cells.append('      <div><span class="pc-stat">%s</span><p class="pc-stat-text">%s</p></div>' % (inline(m.group(1)), inline(m.group(2))))
        others = body_blocks([b for b in rest if b[0] != 'ul'])
        inner = kick + title_of(bl) + ('  <div class="pc-body pc-body--center">\n    <div class="pc-stats" style="--n:%d" data-build-each="%s">\n%s\n    </div>\n%s  </div>\n'
                                       % (len(items), build or 'rise', '\n'.join(cells), ''.join('    %s\n' % o for o in others)))
    elif layout == 'big-number':
        fig = next(b for b in rest if b[0] == 'p' and BIG.fullmatch(b[1]))
        after = [b for b in rest if b is not fig]
        lead = next((b for b in after if b[0] == 'p'), None)
        facts = next((b[1] for b in after if b[0] == 'ul'), [])
        dl = ''
        if facts and all(STAT_ITEM.fullmatch(f) for f in facts):
            dl = '        <dl class="pc-facts">\n%s\n        </dl>\n' % '\n'.join(
                '          <div><dt>%s</dt><dd>%s</dd></div>' % (inline(STAT_ITEM.fullmatch(f).group(1)), inline(STAT_ITEM.fullmatch(f).group(2))) for f in facts)
        inner = kick + title_of(bl) + ('  <div class="pc-body pc-body--center">\n    <div class="pc-big">\n      <span class="pc-stat">%s</span>\n'
                                       '      <div class="pc-stack">\n%s%s      </div>\n    </div>\n  </div>\n'
                                       % (inline(fig[1][2:-2]), '        <p class="pc-lead">%s</p>\n' % inline(lead[1]) if lead else '', dl))
    elif layout == 'checklist':
        items = next(b[1] for b in rest if b[0] == 'ul')
        lis = '\n'.join('      <li class="%s">%s</li>' % ('is-done' if re.match(r'\[[xX]\]', it) else 'is-todo', inline(it[3:].strip())) for it in items)
        others = body_blocks([b for b in rest if b[0] != 'ul'])
        inner = kick + title_of(bl) + '  <div class="pc-body">\n%s    <ul class="pc-checks">\n%s\n    </ul>\n  </div>\n' % (
            ''.join('    %s\n' % o for o in others), lis)
    elif layout == 'code':
        code = next(b for b in rest if b[0] == 'code')
        text = body_blocks([b for b in rest if b is not code])
        pre = body_blocks([code])[0]
        if text:
            inner = kick + title_of(bl) + ('  <div class="pc-body">\n    <div class="pc-grid pc-cols-3-2 pc-grid--center">\n      %s\n      <div class="pc-stack">%s</div>\n'
                                           '    </div>\n  </div>\n' % (pre, ''.join(text).replace('<p>', '<p class="pc-lead">')))
        else:
            inner = kick + title_of(bl) + '  <div class="pc-body">\n    %s\n  </div>\n' % pre
    elif layout == 'cards':
        cards, cur = [], None
        for b in rest:
            if b[0] in ('h3', 'h4'):
                cur = ['<h3 class="pc-h3">%s</h3>' % inline(b[1])]
                cards.append(cur)
            elif cur is not None and b[0] == 'p':
                cur.append('<p>%s</p>' % inline(b[1]))
        inner = kick + title_of(bl) + ('  <div class="pc-body pc-body--center">\n    <div class="pc-grid pc-cols-%d pc-grid--stretch" data-build-each="%s">\n%s\n    </div>\n  </div>\n'
                                       % (min(len(cards), 4), build or 'rise', '\n'.join('      <div class="pc-card">%s</div>' % ''.join(c) for c in cards)))
    elif layout in ('split', 'bleed'):
        img = next(b for b in rest if b[0] == 'img')
        pic = '<div class="pc-media pc-media--%s"><img src="%s" alt="%s"></div>' % ('side' if layout == 'split' else 'bg', esc(picture(img[2])), esc(img[1]))
        others = body_blocks([b for b in rest if b is not img], build)
        cls.append('pc-' + layout)
        if layout == 'split':
            inner = kick + title_of(bl) + ('  <div class="pc-body">\n%s  </div>\n' % ''.join('    %s\n' % o for o in others) if others else '') + '  %s\n' % pic
        else:
            inner = '  %s\n  <div class="pc-body pc-body--end">\n%s%s%s  </div>\n' % (
                pic, kick.replace('  <p', '    <p'), title_of(bl).replace('  <h2', '    <h2'), ''.join('    %s\n' % o for o in others))
    elif layout == 'closing':
        cls.append('pc-closing')
        attrs.append('data-surface="%s"' % d.get('surface', 'inverse'))
        items = next((b[1] for b in rest if b[0] == 'ul'), [])
        lines = [STAT_ITEM.fullmatch(it) for it in items]
        inner = kick + title_of(bl)
        if items and all(lines):
            inner += '  <div class="pc-contact">\n%s\n  </div>\n' % '\n'.join('    <div><b>%s</b>%s</div>' % (inline(m.group(1)), inline(m.group(2))) for m in lines)
        else:
            inner += ''.join('  %s\n' % o.replace('<p>', '<p class="pc-sub">') for o in body_blocks(rest))
    else:                                            # content, and table
        others = body_blocks(rest, build)
        inner = kick + title_of(bl) + '  <div class="pc-body">\n%s  </div>\n' % ''.join('    %s\n' % o for o in others)
    if d.get('section') is not None:
        attrs.append('data-section="%s"' % esc(d['section']))
    if d.get('surface') and layout not in ('statement', 'closing'):
        attrs.append('data-surface="%s"' % esc(d['surface']))
    if notes:
        paras = [p.strip() for p in re.split(r'\n\s*\n', notes) if p.strip()]
        inner += '  <div class="pc-notes">%s</div>\n' % ''.join('<p>%s</p>' % inline(' '.join(p.split())) for p in paras)
    return '<section class="%s"%s>\n%s</section>\n' % (' '.join(cls), ''.join(' ' + a for a in attrs), inner), layout


def convert(src, out=None, **opts):
    text = Path(src).read_text(encoding='utf-8')
    meta, text = front_matter(text)
    meta.update({k: v for k, v in opts.items() if v})
    chunks = split_slides(text)
    if len(chunks) < 2:
        sys.exit('Found %d slide: split slides with --- lines or # headings' % len(chunks))
    out = Path(out) if out else Path(src).with_suffix('.html')
    WHERE.update(src=Path(src).resolve().parent, out=out.resolve().parent)
    slides, used = [], []
    for n, c in enumerate(chunks):
        s, layout = slide(c, n, len(chunks))
        slides.append(s)
        used.append(layout)
    first = re.search(r'class="pc-title">(.*?)</h', slides[0])
    title = meta.get('title') or (html.unescape(re.sub(r'<[^>]+>', '', first.group(1))) if first else 'Deck')
    theme = meta.get('theme', 'meridian')
    import build_themes as bt                     # a theme in themes/, or outside it through PC_THEME_DIRS
    if not (bt.folder(theme) / 'theme.json').exists():
        sys.exit('No theme %r. Themes: %s' % (theme, ', '.join(bt.theme_ids())))
    rel = lambda p: os.path.relpath(KIT / p, out.resolve().parent).replace(os.sep, '/')  # noqa: E731
    attrs = ' '.join('data-%s="%s"' % (k, esc(meta[k])) for k in ('palette', 'mode') if meta.get(k))
    page = ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>%s</title>\n<link rel="stylesheet" href="%s">\n<link rel="stylesheet" href="%s">\n<link rel="stylesheet" href="%s">\n'
            '<script src="%s"></script>\n</head>\n<body>\n<div class="pc-deck" data-theme="%s"%s data-format="%s" data-motion="%s" data-title="%s">\n\n%s\n</div>\n'
            '<script src="%s"></script>\n</body>\n</html>\n') % (
        esc(meta.get('lang', 'en')), esc(title), rel('engine/core.css'), rel('themes/%s/tokens.css' % theme), rel('themes/%s/theme.css' % theme),
        rel('icons/lucide.js'), theme, ' ' + attrs if attrs else '', esc(meta.get('format', '16x9')), esc(meta.get('motion', 'basic')), esc(title),
        '\n'.join(slides), rel('engine/runtime.js'))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    print('Wrote %s: %d slides (%s)' % (out, len(slides), ', '.join('%d %s' % (k + 1, l) for k, l in enumerate(used))))
    return out


def main():
    ap = argparse.ArgumentParser(description='Turn a Markdown outline into a kit deck.')
    ap.add_argument('src')
    ap.add_argument('-o', '--out')
    for k in DECK_KEYS:
        if k != 'title':
            ap.add_argument('--' + k)
    ap.add_argument('--theme-dir', help='a theme kept outside themes/ (a job\'s style folder); the deck uses it unless --theme names another')
    a = ap.parse_args()
    if a.theme_dir:
        import build_themes as bt
        a.theme = a.theme or bt.add_dir(a.theme_dir)
    convert(a.src, a.out, **{k: getattr(a, k) for k in DECK_KEYS if k != 'title'})


if __name__ == '__main__':
    main()
