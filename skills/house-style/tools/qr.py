#!/usr/bin/env python3
"""QR codes for decks, documents and graphics, drawn by the vendored segno (BSD licence, tools/vendor/segno).

    python3 tools/qr.py "https://example.org/join" -o join.svg     # one code as an SVG file

In a source file, write the code as an image with data-qr and build.py swaps it for an inline SVG:

    <img class="pc-qr-code" data-qr="https://example.org/join" alt="Join the garden">

The SVG keeps the quiet zone (four modules) and draws dark modules in near-black on white, so every phone camera reads
it on any theme; size it with style="--qr-size: 300px". Error correction is M (15%), or Q with data-qr-level="q" when a
logo or wear may cover part of it.
"""
import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
import segno  # noqa: E402

TAG = re.compile(r'<img\b[^>]*\bdata-qr=(["\'])(.*?)\1[^>]*>', re.I | re.S)


def svg(data, level='m', label=''):
    """One QR code as an inline SVG element sized by CSS."""
    code = segno.make(data, error=level, micro=False)
    out = code.svg_inline(scale=1, border=4, dark='#111111', light='#ffffff', omitsize=True, svgclass='pc-qr-code',
                          title=label or None)
    return out.replace('<svg ', '<svg role="img" aria-label="%s" ' % html.escape(label or 'QR code'), 1)


def inline_all(text):
    """Every <img data-qr="..."> in a page, swapped for its QR code; other attributes (style, data-build) carry over."""
    def one(m):
        tag = m.group(0)
        data = html.unescape(m.group(2))
        level = (re.search(r'data-qr-level=(["\'])([lmqh])\1', tag, re.I) or [None, None, 'm'])[2].lower()
        alt = re.search(r'\balt=(["\'])(.*?)\1', tag, re.S)
        out = svg(data, level, html.unescape(alt.group(2)) if alt else '')
        extra = ' '.join(a.group(0) for a in re.finditer(r'\b(?:style|data-build|id)=(["\']).*?\1', tag, re.S))
        if extra:
            out = out.replace('<svg ', '<svg %s ' % extra, 1)
        cls = re.search(r'\bclass=(["\'])(.*?)\1', tag)
        more = ' '.join(c for c in (cls.group(2).split() if cls else []) if c != 'pc-qr-code')
        if more:
            out = out.replace('class="pc-qr-code"', 'class="pc-qr-code %s"' % html.escape(more), 1)
        return out
    return TAG.sub(one, text)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('data')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--level', default='m', choices=list('lmqh'))
    a = ap.parse_args()
    Path(a.out).write_text(svg(a.data, a.level), encoding='utf-8')
    print('wrote', a.out)


if __name__ == '__main__':
    main()
