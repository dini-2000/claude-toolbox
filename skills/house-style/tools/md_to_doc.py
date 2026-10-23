#!/usr/bin/env python3
"""Turn a Markdown file into a kit document (document source HTML), to build with tools/build.py and print with
tools/doc_pdf.py.

    python3 tools/md_to_doc.py report.md                     writes report.html beside it
    python3 tools/md_to_doc.py report.md -o docs/report.html --theme folio --type paper

The Markdown is what Pandoc, Quarto and GitHub read, with a front matter block first:

    ---
    title: Northside Community Garden: the 2026 season
    short-title: 2026 season report        (the running head; the title when left out)
    subtitle: What we grew, what it cost, and what changes in 2027
    kicker: Annual report to members
    author: Garden committee               (organisation: works too)
    date: 14 November 2026
    meta: For the annual members' meeting  (a second cover line)
    theme: seminar    palette: green    mode: light
    type: report      (report, paper, proposal, guide, casestudy, letter, memo, onepager, newsletter)
    page: a4          (a4, letter, a5, legal, b5)    orient: landscape
    cover: band       (band, type, minimal, full, split, none; full and split take cover-image:)
    toc: 2            (true, false or the depth; on by default for reports with three chapters or more)
    notes: end        (end, side or foot)
    numbered: true    (numbered headings 1, 1.1, 1.1.1)
    openers: page     (each chapter opens on a page of its own with a big number)
    lead: auto        (a short first paragraph under a chapter title becomes its lead; false turns it off)
    ---

Chapters start at each '# ' heading. Heading attributes in braces: '{#id}', '{-}' or '{.unnumbered}', '{.appendix}'
(lettered A, B), '{.opener}'. Paragraph attributes at the end of a paragraph: '{.lead}', '{.dropcap}', '{.source}'.

    footnotes        [^1] with '[^1]: text' anywhere, or inline ^[text]: notes at the end, the side or the page foot
    figures          an image alone on a line, '![alt](src "Caption")'; the caption is the title, else the alt text
    tables           pipe tables; ':---:' or '---:' columns of figures align right; 'Table: caption' before or after;
                     a first cell of '**Total**', '**Subtotal**' or '**Grand total**', or a row bold in every cell,
                     marks a totals row; a bold label alone, such as '**Fees**', stays an ordinary row
    callouts         GitHub alerts '> [!NOTE] Title', TIP, IMPORTANT, WARNING, CAUTION
    task lists       '- [x] done', '- [ ] to do', '- [-] dropped'
    definitions      'Term' then ': definition' lines, as a facts list
    charts           a fenced ```chart block of 'key: value' lines: type, labels, values, caption, height and any
                     other chart attribute (suffix, prefix, highlight, series ...)
    page breaks      '\\newpage' or '<!-- page -->'
    cross references [text](#id) shows the page number of #id
    fenced divs      '::: name' ... ':::' around blocks, name one of
                     sidebar, cols-2, cols-3, wide, pull (a pull quote; a last line '-- Source' is its source),
                     keyfigs ('- **4.6 t** produce logged' items), timeline ('- **Nov 2025** text' items),
                     agenda ('- **9.30** Item | detail' items; '- **Afternoon**' alone is a section label),
                     steps (an ordered list of '**Step.** text' items), facts ('- **Label**: value' items),
                     signature ('Name' then a role line), refs (a reference list with hanging indents),
                     note, tip, warning, key (callouts, with an optional title after the name)
    raw HTML         lines starting with '<' pass through, so any kit markup can sit in the Markdown

A letter or memo (type: letter) reads from:, address:, to:, subject:, signature: and role: from the front matter
(address and to as lists or ' / '-separated lines) and needs no headings.

The result is a starting point: read it, add icons and charts where they help, then build, print and QC it.
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import md_to_deck as md  # noqa: E402  (inline Markdown, tables, picture paths)

KIT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r'^(```+|~~~+)\s*(.*)$')
DIV = re.compile(r'^:{3,}\s*(?:\{\s*\.?([\w-]+)[^}]*\}|([\w-]+))?\s*(.*)$')
ATTRS = re.compile(r'\s*\{([^{}]*)\}\s*$')
LIST = re.compile(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$')
TASK = re.compile(r'^\[([ xX~-])\]\s+(.*)$')
ALERT = {'NOTE': 'note', 'TIP': 'tip', 'IMPORTANT': 'key', 'WARNING': 'warning', 'CAUTION': 'warning'}
CALLOUT_ICON = {'note': 'info', 'tip': 'lightbulb', 'key': 'star', 'warning': 'triangle-alert'}
CALLOUT_WORD = {'note': 'Note', 'tip': 'Tip', 'key': 'Key point', 'warning': 'Warning'}
LONG_TYPES = ('report', 'paper', 'guide', 'casestudy', 'proposal')
esc = md.esc


# ---------------------------------------------------------------- front matter
def front_matter(text):
    """A small YAML subset: 'key: value' lines and 'key:' followed by '  - item' lines."""
    m = re.match(r'\A---\s*\n([\s\S]*?)\n(?:---|\.\.\.)\s*\n', text)
    if not m or not re.search(r'^[\w-]+\s*:', m.group(1), re.M):
        return {}, text
    meta, key = {}, None
    for line in m.group(1).splitlines():
        item = re.match(r'\s+-\s+(.*)', line)
        if item and key:
            meta[key] = (meta[key] if isinstance(meta[key], list) else []) + [unquote(item.group(1))]
            continue
        k, sep, v = line.partition(':')
        if sep and re.fullmatch(r'[\w-]+', k.strip()):
            key = k.strip().lower().replace('_', '-')
            meta[key] = unquote(v.strip()) if v.strip() else ''
    return meta, text[m.end():]


def unquote(v):
    return v[1:-1] if len(v) > 1 and v[0] == v[-1] and v[0] in '"\'' else v


def lines_of(v):
    """A front matter value as lines: a list, or one string split at ' / '."""
    if isinstance(v, list):
        return v
    return [x.strip() for x in str(v or '').split(' / ') if x.strip()]


def truthy(v, default=False):
    if v in (None, ''):
        return default
    return str(v).strip().lower() not in ('false', 'no', 'off', '0', 'none')


# ---------------------------------------------------------------- footnotes
def take_footnotes(text):
    """Pull out '[^id]: text' definitions (with indented continuation lines) and return (text, {id: note})."""
    notes, out, lines, i = {}, [], text.splitlines(), 0
    fence = False
    while i < len(lines):
        l = lines[i]
        if FENCE.match(l.strip()):
            fence = not fence
        m = None if fence else re.match(r'^\[\^([^\]]+)\]:\s*(.*)$', l)
        if m:
            body, i = [m.group(2)], i + 1
            while i < len(lines) and (lines[i].startswith(('    ', '\t')) or (not lines[i].strip() and i + 1 < len(lines) and lines[i + 1].startswith(('    ', '\t')))):
                body.append(lines[i].strip())
                i += 1
            notes[m.group(1)] = ' '.join(b for b in body if b)
            continue
        out.append(l)
        i += 1
    return '\n'.join(out), notes


def inline(s, notes):
    """Inline Markdown, with footnote references turned into kit notes and #links into page references."""
    keep = []
    def note(text):
        keep.append('<span class="pc-fn">%s</span>' % md.inline(text))
        return '\x01%d\x01' % (len(keep) - 1)
    s = re.sub(r'\^\[((?:[^\[\]]|\[[^\]]*\])+)\]', lambda m: note(m.group(1)), s)
    s = re.sub(r'\[\^([^\]]+)\]', lambda m: note(notes[m.group(1)]) if m.group(1) in notes else m.group(0), s)
    s = md.inline(s)
    s = re.sub(r'<a href="#', '<a class="pc-ref" href="#', s)
    s = re.sub(r'(?<=\S)\s+(?=\x01)', '', s)                     # a note sits right after its word
    return re.sub(r'\x01(\d+)\x01', lambda m: keep[int(m.group(1))], s)


# ---------------------------------------------------------------- blocks
def parse(text):
    """The body as a list of blocks: (kind, ...). Fenced divs nest: ('div', name, rest, [blocks])."""
    lines = text.splitlines()
    pos = [0]

    def run(stop_div=False):
        out = []
        while pos[0] < len(lines):
            i = pos[0]
            l = lines[i]
            s = l.strip()
            if not s:
                pos[0] += 1
                continue
            m = DIV.match(s)
            if m and s.startswith(':::'):
                name = (m.group(1) or m.group(2) or '').lower()
                pos[0] += 1
                if not name:
                    if stop_div:
                        return out
                    continue                                     # a stray closing fence
                out.append(('div', name, m.group(3).strip(), run(True)))
                continue
            m = FENCE.match(s)
            if m:
                tick, lang, j = m.group(1), m.group(2).strip(), i + 1
                while j < len(lines) and not lines[j].strip().startswith(tick):
                    j += 1
                out.append(('code', lang, '\n'.join(lines[i + 1:j])))
                pos[0] = j + 1
                continue
            if s in ('\\newpage', '\\pagebreak') or re.fullmatch(r'<!--\s*page(break)?\s*-->', s):
                out.append(('break',))
                pos[0] += 1
                continue
            if s.startswith('<!--'):
                j = i
                while j < len(lines) and '-->' not in lines[j]:
                    j += 1
                pos[0] = j + 1
                continue
            m = re.match(r'(#{1,6})\s+(.*?)\s*#*$', s)
            if m:
                t, attrs = split_attrs(m.group(2))
                out.append(('h', len(m.group(1)), t, attrs))
                pos[0] += 1
                continue
            m = re.fullmatch(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)(\{[^}]*\})?', s)
            if m:
                out.append(('img', m.group(1), m.group(2), m.group(3), parse_attrs(m.group(4) or '')))
                pos[0] += 1
                continue
            if s.startswith('<'):
                j = i
                while j < len(lines) and lines[j].strip():
                    j += 1
                out.append(('html', '\n'.join(lines[i:j])))
                pos[0] = j
                continue
            if re.match(r'(Table)?:\s+\S', s) and nxt(lines, i + 1).startswith('|'):
                pos[0] += 1
                out.append(('caption', re.sub(r'^(Table)?:\s+', '', s)))
                continue
            if s.startswith('|'):
                j = i
                while j < len(lines) and lines[j].strip().startswith('|'):
                    j += 1
                cap = None
                k = j
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k < len(lines) and re.match(r'(Table)?:\s+\S', lines[k].strip()):
                    cap, j = re.sub(r'^(Table)?:\s+', '', lines[k].strip()), k + 1
                if out and out[-1][0] == 'caption':
                    cap = out.pop()[1]
                out.append(('table', [x for x in lines[i:j] if x.strip().startswith('|')], cap))
                pos[0] = j
                continue
            if s.startswith('>'):
                j, q = i, []
                while j < len(lines) and lines[j].strip().startswith('>'):
                    q.append(re.sub(r'^>\s?', '', lines[j].strip()))
                    j += 1
                pos[0] = j
                a = re.match(r'\[!(\w+)\]\s*(.*)$', q[0])
                if a and a.group(1).upper() in ALERT:
                    out.append(('callout', ALERT[a.group(1).upper()], a.group(2).strip(), sub_parse('\n'.join(q[1:]))))
                else:
                    out.append(('quote', sub_parse('\n'.join(q))))
                continue
            if LIST.match(l):
                pos[0] = i
                out.append(read_list(lines, pos))
                continue
            if i + 1 < len(lines) and re.match(r'^:\s+\S', lines[i + 1].strip()) and not s.startswith(':'):
                items, j = [], i
                while j < len(lines):
                    if not lines[j].strip():
                        if j + 1 < len(lines) and lines[j + 1].strip() and nxt(lines, j + 2).startswith(': '):
                            j += 1
                            continue
                        break
                    term, j, defs = lines[j].strip(), j + 1, []
                    while j < len(lines) and lines[j].strip().startswith(': '):
                        defs.append(lines[j].strip()[2:])
                        j += 1
                    items.append((term, defs))
                    if not defs:
                        break
                out.append(('dl', items))
                pos[0] = j
                continue
            j, para = i, []
            while j < len(lines) and lines[j].strip() and not starts_block(lines[j]):
                para.append(lines[j].strip())
                j += 1
            if not para:                                          # a line no rule took: keep it as text
                para, j = [s], i + 1
            t, attrs = split_attrs('\n'.join(para))           # line breaks kept: a signature or pull source may need them
            out.append(('p', t, attrs))
            pos[0] = j
        return out

    return run()


def nxt(lines, j):
    while j < len(lines) and not lines[j].strip():
        j += 1
    return lines[j].strip() if j < len(lines) else ''


def starts_block(l):
    s = l.strip()
    return bool(LIST.match(l) or re.match(r'(#{1,6}\s|>|\||```|~~~|:::|!\[.*\]\(.*\)\s*$|<(?!/?(a|b|i|em|strong|span|code|br|sup|sub)\b))', s)
                or s in ('\\newpage', '\\pagebreak'))


def sub_parse(text):
    return parse(text)


def split_attrs(t):
    m = ATTRS.search(t)
    if m and re.fullmatch(r'\s*([#.][\w-]+|-)(\s+([#.][\w-]+|-))*\s*', m.group(1)):
        return t[:m.start()].rstrip(), parse_attrs(m.group(0))
    return t, {'id': None, 'classes': []}


def parse_attrs(s):
    s = s.strip().strip('{}')
    toks = s.split()
    return {'id': next((t[1:] for t in toks if t.startswith('#')), None),
            'classes': [t[1:] for t in toks if t.startswith('.')] + (['unnumbered'] if '-' in toks else [])}


def read_list(lines, pos):
    """A list with nesting by indent: ('list', ordered, [(text, task, children)])."""
    first = LIST.match(lines[pos[0]])
    base, ordered = len(first.group(1)), first.group(2)[0].isdigit()
    items = []
    while pos[0] < len(lines):
        l = lines[pos[0]]
        if not l.strip():
            if nxt(lines, pos[0] + 1) and LIST.match(lines[skip_blank(lines, pos[0])]) and \
                    len(LIST.match(lines[skip_blank(lines, pos[0])]).group(1)) >= base:
                pos[0] = skip_blank(lines, pos[0])
                continue
            break
        m = LIST.match(l)
        if m and len(m.group(1)) == base:
            text, task = m.group(3), None
            t = TASK.match(text)
            if t:
                task, text = {' ': 'todo', '~': 'no', '-': 'no'}.get(t.group(1), 'done'), t.group(2)
            items.append([text, task, None])
            pos[0] += 1
        elif m and len(m.group(1)) > base and items:
            items[-1][2] = read_list(lines, pos)
        elif m:
            break
        elif items and (l.startswith((' ', '\t')) or not starts_block(l)):
            items[-1][0] += ' ' + l.strip()
            pos[0] += 1
        else:
            break
    return ('list', ordered, items)


def skip_blank(lines, j):
    while j < len(lines) and not lines[j].strip():
        j += 1
    return min(j, len(lines) - 1)


# ---------------------------------------------------------------- writing
class Writer:
    def __init__(self, meta, notes):
        self.meta, self.notes = meta, notes
        self.lead = truthy(meta.get('lead'), meta.get('type', 'report') in LONG_TYPES)

    def il(self, s):
        return inline(s, self.notes)

    def blocks(self, bl, ind='  '):
        out = []
        for k, b in enumerate(bl):
            out.append(self.block(b, ind, bl[k + 1] if k + 1 < len(bl) else None))
        return '\n'.join(x for x in out if x)

    def block(self, b, ind, after=None):
        kind = b[0]
        if kind == 'p':
            cls = [c for c in b[2]['classes'] if c in ('lead', 'dropcap', 'source', 'muted', 'wide')]
            return '%s<p%s%s>%s</p>' % (ind, id_attr(b[2]), class_attr(['pc-' + c for c in cls]), self.il(b[1]))
        if kind == 'h':
            return '%s<h%d%s%s>%s</h%d>' % (ind, b[1], id_attr(b[3]), ' data-unnumbered' if 'unnumbered' in b[3]['classes'] else '',
                                            self.il(b[2]), b[1])
        if kind == 'break':
            return ind + '<div class="pc-pagebreak"></div>'
        if kind == 'html':
            return b[1]
        if kind == 'caption':
            return '%s<p class="pc-source">%s</p>' % (ind, self.il(b[1]))
        if kind == 'img':
            alt, src, title, attrs = b[1], md.picture(b[2]), b[3], b[4]
            cap = title if title is not None else alt
            cls = ['pc-fig'] + (['pc-wide'] if 'wide' in attrs['classes'] else [])
            return '%s<figure%s%s>\n%s  <img src="%s" alt="%s">%s\n%s</figure>' % (
                ind, id_attr(attrs), class_attr(cls), ind, esc(src), esc(alt),
                '\n%s  <figcaption>%s</figcaption>' % (ind, self.il(cap)) if cap else '', ind)
        if kind == 'table':
            t = md.table(b[1]).replace('class="pc-table"', 'class="pc-tab"')
            if b[2]:
                t = t.replace('<table class="pc-tab">', '<table class="pc-tab">\n      <caption>%s</caption>' % self.il(b[2]), 1)
            return ind + t.replace('\n    ', '\n' + ind)
        if kind == 'code':
            if b[1].lower() == 'chart':
                return self.chart(b[2], ind)
            return '<pre class="pc-code"%s><code>%s</code></pre>' % (' data-lang="%s"' % esc(b[1]) if b[1] else '', html.escape(b[2], quote=False))
        if kind == 'quote':
            return '%s<blockquote>\n%s\n%s</blockquote>' % (ind, self.blocks(b[1], ind + '  '), ind)
        if kind == 'callout':
            return self.callout(b[1], b[2], b[3], ind)
        if kind == 'list':
            return self.list(b, ind)
        if kind == 'dl':
            rows = ''.join('\n%s  <div><dt>%s</dt>%s</div>' % (ind, self.il(t), ''.join('<dd>%s</dd>' % self.il(d) for d in ds)) for t, ds in b[1])
            return '%s<dl class="pc-facts">%s\n%s</dl>' % (ind, rows, ind)
        if kind == 'div':
            return self.div(b[1], b[2], b[3], ind)
        return ''

    def list(self, b, ind, cls=None):
        ordered, items = b[1], b[2]
        tag = 'ol' if ordered else 'ul'
        if cls is None and any(t for _, t, _ in items):
            cls = 'pc-checks'
        out = []
        for text, task, sub in items:
            li_cls = {'todo': ' class="is-todo"', 'no': ' class="is-no"'}.get(task, '')
            inner = self.il(text)
            if sub:
                inner += '\n' + self.list(sub, ind + '    ') + '\n' + ind + '  '
            out.append('%s  <li%s>%s</li>' % (ind, li_cls, inner))
        return '%s<%s%s>\n%s\n%s</%s>' % (ind, tag, class_attr([cls] if cls else []), '\n'.join(out), ind, tag)

    def callout(self, kind, title, body, ind):
        word = title or CALLOUT_WORD[kind]
        label = '%s  <p class="pc-callout-label"><i class="pc-icon" data-icon="%s"></i>%s</p>' % (ind, CALLOUT_ICON[kind], self.il(word))
        return '%s<div class="pc-callout"%s>\n%s\n%s\n%s</div>' % (ind, '' if kind == 'note' else ' data-kind="%s"' % kind, label,
                                                                   self.blocks(body, ind + '  '), ind)

    def chart(self, src, ind):
        kv = {}
        for line in src.splitlines():
            k, sep, v = line.partition(':')
            if sep and k.strip():
                kv[k.strip().lower()] = v.strip()
        cap, height = kv.pop('caption', ''), kv.pop('height', '')
        if 'labels' in kv:
            kv['labels'] = ','.join(x.strip() for x in kv['labels'].split(','))
        if 'values' in kv:
            kv['values'] = ','.join(x.strip() for x in kv['values'].split(','))
        attrs = ''.join(' data-%s="%s"' % (k, esc(v)) for k, v in kv.items())
        style = ' style="height: %s"' % esc(height) if height else ''
        return '%s<figure class="pc-chart pc-fig"%s%s>%s\n%s</figure>' % (
            ind, attrs, style, '\n%s  <figcaption>%s</figcaption>' % (ind, self.il(cap)) if cap else '', ind)

    def div(self, name, rest, bl, ind):
        if name in ('note', 'tip', 'warning', 'key', 'important', 'caution'):
            return self.callout({'important': 'key', 'caution': 'warning'}.get(name, name), unquote(rest), bl, ind)
        if name.startswith('callout-'):                          # Quarto's {.callout-tip}
            return self.callout({'important': 'key', 'caution': 'warning'}.get(name[8:], name[8:]) if name[8:] in
                                ('note', 'tip', 'warning', 'important', 'caution') else 'note', unquote(rest), bl, ind)
        lists = [b for b in bl if b[0] == 'list']
        if name == 'keyfigs' and lists:
            cells = []
            for text, _, _ in lists[0][2]:
                m = re.match(r'\*\*(.+?)\*\*[\s,:]*(.*)', text)
                fig, rest_t = (m.group(1), m.group(2)) if m else (text, '')
                cells.append('%s  <div><b class="pc-stat">%s</b><p>%s</p></div>' % (ind, self.il(fig), self.il(rest_t)))
            return '%s<div class="pc-keyfigs" style="--n: %d">\n%s\n%s</div>' % (ind, len(cells), '\n'.join(cells), ind)
        if name == 'timeline' and lists:
            rows = []
            for text, _, _ in lists[0][2]:
                m = re.match(r'\*\*(.+?)\*\*[\s,:]*(.*)', text)
                rows.append('%s  <li><b>%s</b>%s</li>' % (ind, self.il(m.group(1)), self.il(m.group(2))) if m else '%s  <li>%s</li>' % (ind, self.il(text)))
            return '%s<ol class="pc-timeline">\n%s\n%s</ol>' % (ind, '\n'.join(rows), ind)
        if name == 'agenda' and lists:
            rows = []
            for text, _, _ in lists[0][2]:
                m = re.match(r'\*\*(.+?)\*\*\s*(.*)', text)
                if not m or not m.group(2).strip():
                    rows.append('%s  <li class="pc-agenda-sec">%s</li>' % (ind, self.il(m.group(1) if m else text)))
                    continue
                item, _, more = m.group(2).partition(' | ')
                rows.append('%s  <li><time>%s</time><div><b>%s</b>%s</div></li>' % (ind, self.il(m.group(1)), self.il(item.strip()),
                            '<span>%s</span>' % self.il(more.strip()) if more.strip() else ''))
            return '%s<ol class="pc-agenda">\n%s\n%s</ol>' % (ind, '\n'.join(rows), ind)
        if name == 'steps' and lists:
            return self.list(('list', True, lists[0][2]), ind, 'pc-steps')
        if name == 'refs' and lists:
            return self.list(('list', False, lists[0][2]), ind, 'pc-refs')
        if name == 'facts' and lists:
            rows = []
            for text, _, _ in lists[0][2]:
                m = re.match(r'\*\*(.+?)\*\*\s*:?\s*(.*)', text) or re.match(r'([^:]+):\s*(.*)', text)
                t, d = (m.group(1).rstrip(':'), m.group(2)) if m else (text, '')
                rows.append('%s  <div><dt>%s</dt><dd>%s</dd></div>' % (ind, self.il(t), self.il(d)))
            return '%s<dl class="pc-facts">\n%s\n%s</dl>' % (ind, '\n'.join(rows), ind)
        if name in ('pull', 'signature'):
            paras = [x for b in bl if b[0] == 'p' for x in ([b[1]] if name == 'pull' else b[1].split('\n'))]
        if name == 'pull':
            if paras and '\n' in paras[-1] and re.match(r'^(--|—|–)\s*', paras[-1].split('\n')[-1]):
                paras[-1:] = paras[-1].rsplit('\n', 1)
            src = ''
            if paras and re.match(r'^(--|—|–)\s*', paras[-1]):
                src = re.sub(r'^(--|—|–)\s*', '', paras.pop())
            return '%s<div class="pc-pull">%s%s</div>' % (ind, self.il(' '.join(paras)), '<cite>%s</cite>' % self.il(src) if src else '')
        if name == 'signature':
            return signature(paras[0] if paras else '', ' '.join(paras[1:]), ind, self.il)
        cls = {'sidebar': 'pc-sidebar', 'cols-2': 'pc-cols-2', 'cols-3': 'pc-cols-3', 'wide': 'pc-wide',
               'columns': 'pc-cols-2', 'aside': 'pc-sidebar'}.get(name, 'pc-' + name)
        return '%s<div class="%s">\n%s\n%s</div>' % (ind, cls, self.blocks(bl, ind + '  '), ind)


def id_attr(attrs):
    return ' id="%s"' % esc(attrs['id']) if attrs and attrs.get('id') else ''


def class_attr(cls):
    cls = [c for c in cls if c]
    return ' class="%s"' % ' '.join(cls) if cls else ''


def signature(name, role, ind, il):
    return '%s<div class="pc-signature">\n%s  <div class="pc-sign-line"></div>\n%s  <b>%s</b>%s\n%s</div>' % (
        ind, ind, ind, il(name), '<span>%s</span>' % il(role) if role else '', ind)


def slug(t):
    s = re.sub(r'<[^>]+>|&\w+;', '', t)
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:48] or 'section'


# ---------------------------------------------------------------- the document
def chapters(bl):
    """Split blocks at level-1 headings: (heading or None, blocks)."""
    out, cur = [], (None, [])
    for b in bl:
        if b[0] == 'h' and b[1] == 1:
            if cur[0] or cur[1]:
                out.append(cur)
            cur = (b, [])
        else:
            cur[1].append(b)
    if cur[0] or cur[1]:
        out.append(cur)
    return out


def cover(meta, w):
    kind = (meta.get('cover') or 'band').lower()
    if kind in ('none', 'false', 'no'):
        return ''
    img = meta.get('cover-image') or meta.get('image')
    if kind in ('full', 'split') and not img:
        kind = 'band'
    title, sub, kick = meta.get('title', ''), meta.get('subtitle', ''), meta.get('kicker', '')
    who = meta.get('author') or meta.get('organisation') or meta.get('organization') or ''
    when = ' / '.join(x for x in (meta.get('meta', ''), meta.get('date', '')) if x)
    out = ['<section class="pc-cover" data-cover="%s">' % kind]
    if img and kind in ('full', 'split'):
        out.append('  <div class="pc-media"><img src="%s" alt="%s"></div>' % (esc(md.picture(img)), esc(meta.get('cover-alt', ''))))
    if meta.get('logo'):
        out.append('  <img class="pc-logo" src="%s" alt="%s">' % (esc(md.picture(meta['logo'])), esc(who or 'Logo')))
    head = ['<h1>%s</h1>' % w.il(title)] + (['<p class="pc-sub">%s</p>' % w.il(sub)] if sub else [])
    if kick:
        out.append('  <p class="pc-kicker">%s</p>' % w.il(kick))
    if kind == 'band':
        out.append('  <div class="pc-cover-band">\n    %s\n  </div>' % '\n    '.join(head))
    else:
        out.extend('  ' + h for h in head)
    if who or when:
        out.append('  <div class="pc-meta">\n    %s%s\n  </div>' % ('<b>%s</b>\n    ' % w.il(who) if who else '',
                                                               '<br>'.join(w.il(x) for x in when.split(' / ')) if when else ''))
    out.append('</section>')
    return '\n'.join(out)


def chapter_html(head, bl, w, openers):
    attrs = head[3] if head else {'id': None, 'classes': []}
    cls = ['pc-chapter'] + (['pc-appendix'] if 'appendix' in attrs['classes'] else [])
    unnum = 'unnumbered' in attrs['classes']
    title = head[2] if head else ''
    hid = attrs['id'] or (slug(title) if head else None)
    opener = head and not unnum and 'appendix' not in attrs['classes'] and (openers or 'opener' in attrs['classes'])
    out = ['<section class="%s"%s>' % (' '.join(cls), ' data-unnumbered' if unnum else '')]
    lead = None
    if head and bl and bl[0][0] == 'p':
        a = bl[0][2]
        if 'lead' in a['classes'] or (w.lead and not a['classes'] and len(bl[0][1].split()) <= 40 and '[^' not in bl[0][1]):
            lead, bl = bl[0], bl[1:]
    h1 = '<h1 id="%s">%s</h1>' % (esc(hid), w.il(title)) if head else ''
    lead_html = '<p class="pc-lead">%s</p>' % w.il(lead[1]) if lead else ''
    if opener:
        out.append('  <div class="pc-opener">\n    <span class="pc-opener-num"></span>\n    %s%s\n  </div>' % (h1, '\n    ' + lead_html if lead_html else ''))
    elif head:
        out.append('  ' + h1 + ('\n  ' + lead_html if lead_html else ''))
    body = w.blocks(bl)
    if body:
        out.append(body)
    out.append('</section>')
    return '\n'.join(out)


def letter_html(meta, bl, w):
    org = meta.get('from') or meta.get('organisation') or meta.get('author') or ''
    addr = lines_of(meta.get('address'))
    out = ['<header class="pc-letterhead">',
           '  <div class="pc-org">%s</div>' % w.il(org)]
    if addr:
        out.append('  <address>%s</address>' % '<br>'.join(w.il(x) for x in addr))
    out.append('</header>')
    to = lines_of(meta.get('to'))
    if to:
        out.append('<address class="pc-recipient">%s</address>' % '<br>'.join(w.il(x) for x in to))
    if meta.get('date'):
        out.append('<p class="pc-date">%s</p>' % w.il(meta['date']))
    if meta.get('subject'):
        out.append('<p class="pc-subject">%s</p>' % w.il(meta['subject']))
    out.append('<section class="pc-flow">\n%s\n</section>' % w.blocks(bl))
    if meta.get('signature'):
        if meta.get('closing'):
            out.append('<p>%s</p>' % w.il(meta['closing']))
        out.append(signature(meta['signature'], meta.get('role', ''), '', w.il))
    return '\n'.join(out)


def convert(src, out=None, **opts):
    src = Path(src)
    text = src.read_text(encoding='utf-8').replace('\r\n', '\n')
    meta, body = front_matter(text)
    for k, v in opts.items():
        if v:
            meta[k] = v
    out = Path(out) if out else src.with_suffix('.html')
    md.WHERE.update(src=src.parent.resolve(), out=out.parent.resolve())
    body, notes = take_footnotes(body)
    bl = parse(body)
    dtype = (meta.get('type') or 'report').lower().replace(' ', '').replace('-', '')
    meta['type'] = dtype
    w = Writer(meta, notes)
    theme = meta.get('theme', 'seminar')
    import build_themes as bt                     # a theme in themes/, or outside it through PC_THEME_DIRS
    if not (bt.folder(theme) / 'theme.json').is_file():
        sys.exit('md_to_doc: no theme "%s". Themes: %s' % (theme, ', '.join(bt.theme_ids())))
    tj = bt.folder(theme) / 'theme.json'
    pals = list((json.loads(tj.read_text(encoding='utf-8')).get('palettes') or {})) if tj.is_file() else []
    if meta.get('palette') and pals and meta['palette'] not in pals:
        sys.exit('md_to_doc: theme %s has no palette "%s"; it has %s' % (theme, meta['palette'], ', '.join(pals)))
    title = meta.get('title') or next((b[2] for b in bl if b[0] == 'h' and b[1] == 1), src.stem)
    meta.setdefault('title', title)

    if dtype in ('letter', 'memo'):
        parts = [letter_html(meta, bl, w)]
    else:
        chs = chapters(bl)
        n_named = sum(1 for h, _ in chs if h)
        parts = []
        cov = cover(meta, w) if meta.get('cover') or dtype in LONG_TYPES else ''   # cover() drops 'none'
        if cov:
            parts.append(cov)
        toc = meta.get('toc')
        if toc in (None, ''):
            toc = '2' if dtype in LONG_TYPES and n_named >= 3 else 'false'
        if truthy(toc):
            depth = toc if str(toc).isdigit() else '2'
            parts.append('<nav class="pc-toc" data-depth="%s"></nav>' % depth)
        openers = (meta.get('openers') or '').lower() == 'page'
        for head, chb in chs:
            if head is None:
                if chb:
                    parts.append('<section class="pc-flow">\n%s\n</section>' % w.blocks(chb))
                continue
            parts.append(chapter_html(head, chb, w, openers))

    root = {'lang': meta.get('lang', 'en'), 'class': 'pc-deck pc-doc', 'data-theme': theme}
    for k in ('palette', 'mode', 'type', 'page', 'orient', 'notes', 'cover'):
        if meta.get(k) and k != 'cover':
            root['data-' + k] = meta[k]
    root.setdefault('data-page', 'a4')
    flags = ' data-numbered' if truthy(meta.get('numbered'), dtype in ('report', 'paper', 'guide')) else ''
    if (meta.get('openers') or '').lower() == 'page':
        root['data-openers'] = 'page'
    root['data-title'] = re.sub(r'<[^>]+>', '', md.inline(title))
    if meta.get('short-title') or meta.get('running'):
        root['data-short-title'] = meta.get('short-title') or meta.get('running')
    if meta.get('notes-title'):
        root['data-notes-title'] = meta['notes-title']
    attrs = ' '.join('%s="%s"' % (k, esc(v)) for k, v in root.items()) + flags
    rel = lambda p: os.path.relpath(KIT / p, out.parent.resolve()).replace(os.sep, '/')  # noqa: E731
    who = meta.get('author') or meta.get('organisation') or meta.get('from') or ''
    head = ['<meta charset="utf-8">', '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<title>%s</title>' % esc(root['data-title'])]
    if who:
        head.append('<meta name="author" content="%s">' % esc(re.sub(r'<[^>]+>', '', who)))
    if meta.get('description') or meta.get('subtitle'):
        head.append('<meta name="description" content="%s">' % esc(meta.get('description') or meta.get('subtitle')))
    head += ['<link rel="stylesheet" href="%s">' % rel('engine/doc.css'),
             '<link rel="stylesheet" href="%s">' % rel('themes/%s/tokens.css' % theme),
             '<script src="%s"></script>' % rel('icons/lucide.js')]
    doc = '<!doctype html>\n<html %s>\n<head>\n%s\n</head>\n<body>\n\n%s\n\n<script src="%s"></script>\n</body>\n</html>\n' % (
        attrs, '\n'.join(head), '\n\n'.join(parts), rel('engine/runtime.js'))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding='utf-8')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('md')
    ap.add_argument('-o', '--out')
    for k in ('theme', 'palette', 'mode', 'type', 'page', 'notes', 'cover'):
        ap.add_argument('--' + k)
    ap.add_argument('--theme-dir', help='a theme kept outside themes/ (a job\'s style folder); the document uses it unless --theme names another')
    a = ap.parse_args()
    if a.theme_dir:
        import build_themes as bt
        a.theme = a.theme or bt.add_dir(a.theme_dir)
    out = convert(a.md, a.out, theme=a.theme, palette=a.palette, mode=a.mode, type=a.type, page=a.page, notes=a.notes, cover=a.cover)
    print('Document source %s. Next: python3 tools/build.py %s%s -o <built.html>, then tools/doc_pdf.py <built.html> --built'
          % (out, out, ' --theme-dir "%s"' % a.theme_dir if a.theme_dir else ''))


if __name__ == '__main__':
    main()
