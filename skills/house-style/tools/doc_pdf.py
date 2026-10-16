#!/usr/bin/env python3
"""Print a kit document (<html class="pc-deck pc-doc">) to a finished PDF.

    python3 tools/doc_pdf.py samples/docs/garden-report.html            # builds it, then writes dist/garden-report.pdf
    python3 tools/doc_pdf.py dist/report.html --built -o report.pdf     # a file tools/build.py already built
    python3 tools/doc_pdf.py report.html --print --marks                # also report-print.pdf for a press (CMYK, PDF/X-4, 3 mm bleed)

Chrome prints the document twice. The first print shows where each link target landed (Chrome writes a named
destination for every one), and the second carries those pages in window.PC_PAGES, so the contents and "(p. 12)"
cross-references show real numbers; a third print runs only if the numbers moved a page break. The bookmarks come
from Chrome's outline with titles from the headings themselves (Chrome's own titles run wrapped lines together and
double some), and the PDF gets its title, author, subject and keywords from the document's head. A document with
data-notes="foot" is laid out by Paged.js (tools/vendor/pagedjs, MIT; engine/paged-run.js) so its notes sit at the
foot of the page, and printed through DevTools once Paged.js is done.
"""
import argparse
import html
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chrome  # noqa: E402

HEADS = r'''<script>
addEventListener('load', function () {
  var out = { heads: [], errors: window.__pcErrs || [] };
  var done = function () { var pre = document.createElement('pre'); pre.id = 'pc-probe'; pre.hidden = true; pre.textContent = JSON.stringify(out); document.body.appendChild(pre); };
  (window.PCDeck && PCDeck.ready ? PCDeck.ready() : Promise.resolve()).then(function () {
    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(function (h) {
      if (!h.getClientRects().length) return;
      var t = (h.dataset.toc || h.textContent).replace(/\s+/g, ' ').trim(), n = h.dataset.n || '';
      out.heads.push([+h.tagName[1], n ? n + (/^Appendix/.test(n) ? ': ' : ' ') + t : t]);
    });
  }).catch(function (e) { out.errors.push(String(e)); }).then(done);
});
</script>'''


def meta(text, name):
    m = re.search(r'<meta\b[^>]*\bname="%s"[^>]*\bcontent="([^"]*)"' % name, text, re.I)
    return html.unescape(m.group(1)).strip() if m else ''


def pages_of(pdf):
    import fitz
    with fitz.open(pdf) as d:
        return {k: v['page'] + 1 for k, v in d.resolve_names().items() if v.get('page', -1) >= 0}


def make_pdf(html_path, out, title=None, quiet=False, bleed=0):
    import fitz
    html_path, out = Path(html_path).resolve(), Path(out).resolve()
    text = html_path.read_text(encoding='utf-8')
    say = (lambda *a: None) if quiet else print
    work = Path(tempfile.mkdtemp(prefix='pc-docpdf-'))
    pre = '<script>window.PC_BLEED = %s;</script>' % float(bleed) if bleed else ''
    if re.search(r'<html\b[^>]*\bdata-notes="foot"', text) and 'pc-fn' in text:
        # notes at the page foot: Paged.js lays the pages out, and Chrome prints through DevTools once it is done
        kit = Path(__file__).resolve().parent.parent
        esc = lambda t: t.replace('</script', '<\\/script')
        tail = ('<script>window.PagedConfig = { auto: false };</script><script>%s</script><script>%s</script>'
                % (esc((kit / 'tools/vendor/pagedjs/paged.polyfill.js').read_text(encoding='utf-8')),
                   esc((kit / 'engine/paged-run.js').read_text(encoding='utf-8'))))
        prt = lambda dst, head: chrome.print_pdf_wait(html_path, dst, 'window.PC_PAGED', head=head, tail=tail, outline=True)
    else:
        prt = lambda dst, head: chrome.print_pdf(html_path, dst, outline=True, head=head)
    pdf = prt(work / 'pass1.pdf', pre)
    pages, passes = pages_of(pdf), 1
    while passes < 3:
        head = pre + '<script>window.PC_PAGES = %s;</script>' % json.dumps(pages)
        pdf = prt(work / ('pass%d.pdf' % (passes + 1)), head)
        passes += 1
        now = pages_of(pdf)
        if now == pages:
            break
        pages = now

    # bookmarks: Chrome's levels and pages, the headings' own titles
    import build
    rep = build.run_probe(html_path, text, build.DOC_VIEW, HEADS) or {}
    heads = rep.get('heads') or []
    doc = fitz.open(pdf)
    toc = doc.get_toc(simple=True)
    if len(heads) == len(toc) and all(h[0] == t[0] for h, t in zip(heads, toc)):
        toc = [[t[0], h[1], t[2]] for h, t in zip(heads, toc)]
        how = 'titles from the headings'
    else:
        half = lambda s: s[:len(s) // 2] if len(s) % 2 == 0 and s[:len(s) // 2] == s[len(s) // 2:] else s
        toc = [[t[0], half(t[1]), t[2]] for t in toc]
        how = "Chrome's titles (the headings did not match one for one: %d against %d)" % (len(heads), len(toc))
    doc.set_toc(toc)

    m = re.search(r'<html\b[^>]*\bdata-title="([^"]*)"', text, re.I) or re.search(r'<title>(.*?)</title>', text, re.I | re.S)
    md = doc.metadata or {}
    md.update({'title': title or (html.unescape(m.group(1)).strip() if m else ''), 'author': meta(text, 'author'),
               'subject': meta(text, 'description'), 'keywords': meta(text, 'keywords'),
               'creator': 'House Style' + ('. ' + meta(text, 'theme-credit') if meta(text, 'theme-credit') else '')})
    doc.set_metadata(md)
    doc.set_pagemode('UseOutlines' if toc else 'UseNone')
    if bleed:
        b = bleed * 72 / 25.4
        for page in doc:
            mb = page.mediabox
            page.set_bleedbox(fitz.Rect(0, 0, mb.width, mb.height))
            page.set_trimbox(fitz.Rect(b, b, mb.width - b, mb.height - b))
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out, garbage=4, deflate=True)
    n = doc.page_count
    doc.close()
    say('PDF %s: %d pages, %d bookmarks (%s), %d page references, %d prints, %s'
        % (out, n, len(toc), how, len(pages), passes, build.kb(out.stat().st_size)))
    if rep.get('errors'):
        say('  ! script errors: ' + '; '.join(rep['errors'][:5]))
    for p in work.iterdir():
        p.unlink()
    work.rmdir()
    return {'path': out, 'pages': n, 'toc': toc, 'refs': pages, 'passes': passes}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('doc', help='a document source, or a built file with --built')
    ap.add_argument('-o', '--out', help='the PDF (default: dist/<name>.pdf beside the document)')
    ap.add_argument('--built', action='store_true', help='the file is already built by tools/build.py')
    ap.add_argument('--theme')
    ap.add_argument('--palette')
    ap.add_argument('--mode')
    ap.add_argument('--print', action='store_true', help='also write <name>-print.pdf for a press: CMYK PDF/X-4 with bleed (tools/print_ready.py)')
    ap.add_argument('--bleed', type=float, default=3, help='mm of bleed on each side of the print file (default 3)')
    ap.add_argument('--marks', action='store_true', help='crop marks on the print file')
    ap.add_argument('--profile', default='fogra39', help='press profile: fogra39 (default), gracol, uncoated or a .icc path')
    ap.add_argument('--proof', action='store_true', help='soft-proof contact sheet of the print file')
    a = ap.parse_args()
    src = Path(a.doc).resolve()
    if a.built:
        built = src
    else:
        import build
        res = build.build(src, theme_id=a.theme, palette=a.palette, mode=a.mode)
        built = res['path']
        if res['problems']:
            print('Build problems (above); printing anyway.', file=sys.stderr)
    out = Path(a.out) if a.out else built.with_suffix('.pdf')
    make_pdf(built, out)
    if a.print:
        import print_ready
        tmp = Path(tempfile.mkdtemp(prefix='pc-press-')) / 'bleed.pdf'
        make_pdf(built, tmp, quiet=True, bleed=a.bleed)
        print_ready.make(tmp, out.with_name(out.stem + '-print.pdf'), a.profile, None, a.marks, a.proof)
        tmp.unlink()
        tmp.parent.rmdir()


if __name__ == '__main__':
    main()
