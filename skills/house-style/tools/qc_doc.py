#!/usr/bin/env python3
"""Check a kit document and its PDF, and draw a contact sheet to look at every page.

    python3 tools/qc_doc.py dist/report.html dist/report.pdf        # writes dist/report-sheet.png
    python3 tools/qc_doc.py dist/report.html dist/report.pdf --cols 5 --width 320

In the built HTML (Chrome, at the page width): script errors, icons that did not draw, charts that did not draw,
links to ids that are not there, and anything wider than the text column (tables, code, pictures, charts).
In the PDF: blank pages, a heading in the lowest 30% of a page with fewer than two lines of its own below it,
fonts that are not embedded or are not the theme's (a sign a face failed to load), links whose target is missing,
and a last page with only a few lines on it; a note for a page that is two thirds empty. The contact sheet is for the look at every page that QC still needs.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

DOM = r'''<script>
addEventListener('load', function () {
  var out = { errors: window.__pcErrs || [], wide: [], links: [], icons: [], charts: [0, 0] };
  var done = function () { var pre = document.createElement('pre'); pre.id = 'pc-probe'; pre.hidden = true; pre.textContent = JSON.stringify(out); document.body.appendChild(pre); };
  if (!window.PCDeck) { out.errors.push('The runtime did not start'); return done(); }
  PCDeck.ready().then(function () {
    var b = document.body, cs = getComputedStyle(b), right = b.getBoundingClientRect().right - parseFloat(cs.paddingRight) + 1;
    var name = function (e) { var h = e.closest('.pc-chapter'); h = h && h.querySelector('h1');
      return e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '') + (h ? ' in "' + h.textContent.trim().slice(0, 40) + '"' : ''); };
    b.querySelectorAll('table, pre, figure, img, svg, .pc-grid, .pc-keyfigs, .pc-callout, p, li').forEach(function (e) {
      if (e.closest('.pc-cover, .pc-fullpage, .pc-mark, .pc-icon')) return;
      var r = e.getBoundingClientRect();
      if (r.width && r.right > right) out.wide.push(name(e) + ' by ' + Math.round(r.right - right) + 'px');
      if ((e.tagName === 'PRE' || e.tagName === 'TABLE') && e.scrollWidth > e.clientWidth + 1) out.wide.push(name(e) + ' scrolls inside');
    });
    document.querySelectorAll('a[href^="#"]').forEach(function (a) { var id = decodeURIComponent(a.getAttribute('href').slice(1)); if (id && !document.getElementById(id)) out.links.push(a.textContent.trim().slice(0, 40) + ' -> #' + id); });
    document.querySelectorAll('.pc-icon[data-missing]').forEach(function (i) { out.icons.push(i.dataset.icon); });
    var figs = document.querySelectorAll('figure.pc-chart');
    out.charts = [figs.length, Array.prototype.filter.call(figs, function (f) { return f.querySelector(':scope > svg'); }).length];
    var rs = getComputedStyle(document.documentElement);
    out.theme = [];
    ['--font-body', '--font-label', '--font-display', '--font-mono', '--font-stat', '--font-quote'].forEach(function (v) { out.theme = out.theme.concat(rs.getPropertyValue(v).split(',')); });
  }).catch(function (e) { out.errors.push(String(e)); }).then(done);
});
</script>'''


def sheet(pdf, out, cols=4, width=300):
    import fitz
    d = fitz.open(pdf)
    r = d[0].rect
    h, gap = int(width * r.height / r.width), 14
    rows = (d.page_count + cols - 1) // cols
    sh = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, cols * (width + gap) + gap, rows * (h + gap) + gap), False)
    sh.clear_with(205)
    for i, page in enumerate(d):
        z = width / page.rect.width
        pm = page.get_pixmap(matrix=fitz.Matrix(z, z))
        pm.set_origin(gap + (i % cols) * (width + gap), gap + (i // cols) * (h + gap))
        sh.copy(pm, pm.irect)
    sh.save(str(out))
    return out


def check_pdf(pdf, fonts_ok):
    import fitz
    probs = []
    d = fitz.open(pdf)
    names = d.resolve_names()
    toc = d.get_toc(simple=False)
    for i, page in enumerate(d):
        words = [w for w in page.get_text('words') if not re.fullmatch(r'\d+|Page|of', w[4])]
        area = page.rect.width * page.rect.height   # the page's own background fill is not content
        marks = [g for g in page.get_drawings() if g['rect'].width * g['rect'].height < area * .9]
        if not words and not page.get_images() and len(marks) < 2:
            probs.append('Page %d is blank' % (i + 1))
        for l in page.get_links():
            if l.get('kind') == fitz.LINK_NAMED and l.get('nameddest') and l['nameddest'] not in names:
                probs.append('Page %d: link to a missing target %s' % (i + 1, l['nameddest']))
    # a heading near the foot of a page with fewer than two lines of its own under it (Chrome's bookmarks all
    # point at the page top, so the heading is found as the text block that starts with its title)
    pnum = re.compile(r'\s*(Page\s+)?\d+(\s+of\s+\d+)?\s*')
    for lvl, title, pno, dest in toc:
        if lvl < 2 or pno < 1:
            continue
        page = d[pno - 1]
        key = re.sub(r'\s+', ' ', title).strip()
        lines = [(l['bbox'][1], l['bbox'][3], ''.join(s['text'] for s in l['spans']).strip())
                 for blk in page.get_text('dict')['blocks'] for l in blk.get('lines', [])]
        heads = [y1 for y0, y1, t in lines if t and key.startswith(t) and len(t) >= min(len(key), 6)]
        if not heads:
            continue
        top = max(heads)
        below = [t for y0, y1, t in lines if y0 > top + 1 and t and not pnum.fullmatch(t)]
        if top > page.rect.height * 0.7 and len(below) < 2:
            probs.append('Page %d: "%s" sits at the foot of the page with its text on the next' % (pno, title[:50]))
    # fonts: embedded, and the theme's own (a span in another face means a glyph the theme fonts lack, or a face
    # that failed to load); Type3 fonts are what Chrome makes of symbol and emoji fallbacks
    stray, type3 = {}, set()
    for i, page in enumerate(d):
        for f in page.get_fonts():
            base = f[3].split('+', 1)[-1]
            if f[2] == 'Type3':
                type3.add(i + 1)
            elif f[1] == 'n/a' or not f[1]:
                probs.append('Page %d: font not embedded: %s' % (i + 1, base))
        if not fonts_ok:
            continue
        for blk in page.get_text('dict')['blocks']:
            for l in blk.get('lines', []):
                for sp in l['spans']:
                    base = sp['font'].split('+', 1)[-1].replace('-', '').replace(' ', '').lower()
                    if sp['text'].strip() and not any(base.startswith(k) for k in fonts_ok):
                        stray.setdefault(sp['font'], []).append('p%d "%s"' % (i + 1, sp['text'].strip()[:12]))
    for font, where in stray.items():
        probs.append('Text in a font that is not the theme\'s: %s at %s' % (font, ', '.join(where[:4])))
    if type3:
        probs.append('Type3 font (a symbol or emoji from a fallback font) on page %s' % ', '.join(map(str, sorted(type3))))
    last = d[-1]
    lines = [b for b in last.get_text('blocks') if not re.fullmatch(r'\s*(Page\s+)?\d+(\s+of\s+\d+)?\s*', b[4])]
    if d.page_count > 1 and 0 < len(lines) <= 2 and sum(len(b[4]) for b in lines) < 160:
        probs.append('The last page holds only %d short block(s): tighten the text or let it run onto the page before' % len(lines))
    # notes, not problems: a page whose text stops in its top third before a break (often a chapter ending early),
    # worth a look in case a picture, a callout or a little more text would fill it
    notes = []
    for i, page in enumerate(d):
        if i in (0, d.page_count - 1):
            continue
        h = page.rect.height
        body = [b for b in page.get_text('blocks') if h * 0.08 < b[1] and b[3] < h * 0.92 and not pnum.fullmatch(b[4])]
        art = [r for r in [im['bbox'] for im in page.get_image_info()] + [g['rect'] for g in page.get_drawings()]
               if h * 0.08 < r[1] and r[3] < h * 0.92]
        if len(body) < 3 and not art:
            continue   # a title or opener page, sparse by design
        low = max([b[3] for b in body] + [r[3] for r in art])
        if low < h * 0.38:
            notes.append('Page %d is two thirds empty: its text stops at %d%% of the page' % (i + 1, low * 100 / h))
    return probs, d.page_count, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('html', help='the built document')
    ap.add_argument('pdf', help='its PDF from tools/doc_pdf.py')
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--width', type=int, default=300)
    a = ap.parse_args()
    html_path, pdf = Path(a.html).resolve(), Path(a.pdf).resolve()
    probs = []
    rep = build.run_probe(html_path, html_path.read_text(encoding='utf-8'), build.DOC_VIEW, DOM)
    fonts_ok = []
    if rep is None:
        probs.append('Chrome could not open the document')
    else:
        probs += ['Script error: ' + e for e in rep.get('errors', [])[:5]]
        probs += ['Wider than the text column: ' + w for w in rep.get('wide', [])[:12]]
        probs += ['Link to a missing id: ' + l for l in rep.get('links', [])[:12]]
        if rep.get('icons'):
            probs.append('Icons not drawn: ' + ', '.join(sorted(set(rep['icons']))))
        c = rep.get('charts') or [0, 0]
        if c[0] != c[1]:
            probs.append('Charts not drawn: %d of %d' % (c[0] - c[1], c[0]))
        fonts_ok = [f.strip().strip('"\'').replace(' ', '').replace('-', '').lower() for f in rep.get('theme') or []]
        system = ('serif', 'sansserif', 'monospace', 'systemui', 'uimonospace', 'applesystem', 'segoeui', 'georgia',
                  'timesnewroman', 'menlo', 'consolas', 'arial', 'helvetica', 'helveticaneue', 'courier', 'couriernew')
        fonts_ok = sorted({f for f in fonts_ok if f and f not in system})
    pp, n, notes = check_pdf(pdf, fonts_ok)
    probs += pp
    out = sheet(pdf, pdf.with_name(pdf.stem + '-sheet.png'), a.cols, a.width)
    print('QC %s: %d pages, %d problem%s; contact sheet %s' % (pdf.name, n, len(probs), '' if len(probs) == 1 else 's', out))
    for p in probs:
        print('  ! ' + p)
    for p in notes:
        print('  - note: ' + p)
    print('Now look at every page on the contact sheet, then zoom into any page that looks off.')
    sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
