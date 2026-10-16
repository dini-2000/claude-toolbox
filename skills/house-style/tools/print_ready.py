#!/usr/bin/env python3
"""Turn a kit PDF (Chrome prints RGB) into a press file: CMYK, PDF/X-4, trim and bleed boxes, optional crop marks.

    python3 tools/print_ready.py dist/report.pdf                       # -> dist/report-print.pdf, FOGRA39 coated
    python3 tools/print_ready.py poster.pdf --bleed 3 --marks          # the PDF already carries 3 mm bleed on each side
    python3 tools/print_ready.py flyer.pdf --profile uncoated --proof  # also writes flyer-print-proof.png

Colour: black and neutral greys go to the black plate alone (K-only), matched in lightness through the profile, so
small text stays sharp on press; other colours and pictures go through the press profile (relative colorimetric
with black point compensation for flat colour, perceptual for pictures). Soft masks go to grey. The press profile
is embedded as the PDF/X output intent, every page gets a TrimBox and BleedBox, links and bookmarks are dropped
(a press file has no use for them) and the file is marked PDF/X-4 in its XMP and version header. check() lists
anything that breaks those rules; no free validator certifies PDF/X, so the print shop's preflight has the last word.

Profiles (assets/icc): fogra39 = Coated FOGRA39 (VIGC, ISO 12647-2 coated paper, the default in Europe and Asia;
"may be used, embedded, exchanged, and shared without restriction"); gracol = GRACoL2013 CRPC6 (Idealliance, US
coated; same terms); uncoated = PSO Uncoated v3 FOGRA52 (ECI; "may be used, embedded and exchanged without
restriction", not distributed, so the kit does not include it). A print shop's own .icc can be given as a path.
"""
import argparse
import datetime
import io
import re
import sys
import uuid
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
ICC = KIT / 'assets' / 'icc'
PROFILES = {
    'fogra39': ('Coated_Fogra39L_VIGC_300.icc', 'FOGRA39', 'Coated FOGRA39 (ISO 12647-2:2004), 300% total ink'),
    'gracol': ('GRACoL2013_CRPC6.icc', 'CGATS21_CRPC6', 'GRACoL 2013 coated (CGATS 21-2 CRPC6)'),
    'uncoated': ('PSOuncoated_v3_FOGRA52.icc', 'FOGRA52', 'PSO Uncoated v3 (ISO 12647-2:2013), FOGRA52'),
}
MM = 72 / 25.4
NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)'
RGB_OP = re.compile(r'(?<![^\s\[\]])(%s)\s+(%s)\s+(%s)\s+(rg|RG)(?=[\s\[\]/<(]|$)' % (NUM, NUM, NUM))


class Colour:
    """sRGB to press CMYK, with neutrals on the black plate alone."""

    def __init__(self, profile):
        from PIL import ImageCms
        self.cms = ImageCms
        srgb = ImageCms.createProfile('sRGB')
        press = ImageCms.getOpenProfile(str(profile))
        lab = ImageCms.createProfile('LAB')
        bpc = ImageCms.Flags.BLACKPOINTCOMPENSATION
        self.flat = ImageCms.buildTransform(srgb, press, 'RGB', 'CMYK', ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=bpc)
        self.photo = ImageCms.buildTransform(srgb, press, 'RGB', 'CMYK', ImageCms.Intent.PERCEPTUAL)
        self.to_lab = ImageCms.buildTransform(srgb, lab, 'RGB', 'LAB')
        # the press's K-only lightness curve, for matching greys
        from PIL import Image
        ramp = Image.frombytes('CMYK', (256, 1), bytes(b for k in range(256) for b in (0, 0, 0, k)))
        back = ImageCms.buildTransform(press, lab, 'CMYK', 'LAB', ImageCms.Intent.RELATIVE_COLORIMETRIC)
        self.kcurve = [px[0] * 100 / 255 for px in ImageCms.applyTransform(ramp, back).getdata()]   # L* by K 0..255
        self.cache = {}

    def lstar(self, r, g, b):
        from PIL import Image
        px = self.cms.applyTransform(Image.new('RGB', (1, 1), (round(r * 255), round(g * 255), round(b * 255))), self.to_lab)
        return px.getpixel((0, 0))[0] * 100 / 255

    def k_for(self, r, g, b):
        """K-only tint whose printed lightness matches the grey, the sRGB range mapped onto the press's K range."""
        lo, target = self.kcurve[-1], self.lstar(r, g, b)
        want = lo + target / 100 * (100 - lo)
        for k in range(256):
            if self.kcurve[k] <= want:
                if k == 0:
                    return 0.0
                a, b2 = self.kcurve[k - 1], self.kcurve[k]
                return ((k - 1) + (a - want) / (a - b2 or 1)) / 255
        return 1.0

    def cmyk(self, r, g, b):
        key = (round(r, 4), round(g, 4), round(b, 4))
        if key not in self.cache:
            r, g, b = (min(1, max(0, v)) for v in key)
            if max(r, g, b) - min(r, g, b) < 0.012:
                out = (0, 0, 0, round(self.k_for(r, g, b), 4))
            else:
                from PIL import Image
                px = self.cms.applyTransform(Image.new('RGB', (1, 1), (round(r * 255), round(g * 255), round(b * 255))), self.flat)
                out = tuple(round(v / 255, 4) for v in px.getpixel((0, 0)))
            self.cache[key] = out
        return self.cache[key]

    def image(self, rgb_bytes, w, h):
        """Photos through the perceptual intent. Flat art (512 colours at most, such as a logo or an icon saved as
        PNG) goes colour by colour like vector colour, so its greys and black print on the black plate alone."""
        from PIL import Image
        im = Image.frombytes('RGB', (w, h), rgb_bytes)
        cols = im.getcolors(512)
        if cols:
            lut = {c: bytes(round(v * 255) for v in self.cmyk(*(x / 255 for x in c))) for _, c in cols}
            return b''.join(lut[p] for p in im.getdata())
        return self.cms.applyTransform(im, self.photo).tobytes()


def fmt(v):
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


def grey(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def rewrite(text, col, mask):
    def sub(m):
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        op = m.group(4)
        if mask:
            return '%s %s' % (fmt(grey(r, g, b)), 'g' if op == 'rg' else 'G')
        return '%s %s' % (' '.join(fmt(v) for v in col.cmyk(r, g, b)), 'k' if op == 'rg' else 'K')
    text = RGB_OP.sub(sub, text)
    text = re.sub(r'/DeviceRGB(\s+)(cs|CS)', (lambda m: ('/DeviceGray' if mask else '/DeviceCMYK') + m.group(1) + m.group(2)), text)
    return text


def refs(obj):
    return [int(x) for x in re.findall(r'(\d+) 0 R', obj)]


def convert(doc, col, warn):
    import fitz
    n = doc.xref_length()
    objs = {x: doc.xref_object(x, compressed=True) for x in range(1, n)}
    # forms that are soft masks (and what they draw) are converted to grey, not CMYK
    mask = set()
    todo = [int(m) for o in objs.values() for m in re.findall(r'/SMask\s*<<[^>]*?/G\s+(\d+) 0 R', o)]
    while todo:
        x = todo.pop()
        if x in mask or x not in objs:
            continue
        mask.add(x)
        todo += [r for r in refs(objs[x]) if r in objs and ('/Subtype/Form' in objs[r].replace(' ', '') or '/ShadingType' in objs[r] or '/PatternType' in objs[r])]
    content = set()
    for page in doc:
        content.update(page.get_contents())
    stats = {'streams': 0, 'shadings': 0, 'images': 0, 'groups': 0}
    for x, o in objs.items():
        flat = o.replace(' ', '')
        is_form = '/Subtype/Form' in flat or '/PatternType1' in flat
        if (x in content or is_form) and doc.xref_is_stream(x):
            t = doc.xref_stream(x).decode('latin-1')
            t2 = rewrite(t, col, x in mask)
            if t2 != t:
                doc.update_stream(x, t2.encode('latin-1'))
                stats['streams'] += 1
        if '/Group' in o and '/DeviceRGB' in o:
            doc.xref_set_key(x, 'Group/CS', '/DeviceGray' if x in mask else '/DeviceCMYK')
            stats['groups'] += 1
        if '/ShadingType' in o:
            stats['shadings'] += shading(doc, x, o, col, x in mask, warn)
        if '/Subtype/Image' in flat:
            stats['images'] += image(doc, x, o, col, warn)
    # Type3 glyphs and anything else left in RGB
    for x in range(1, doc.xref_length()):
        o = doc.xref_object(x, compressed=True)
        if '/DeviceRGB' in o or '/ICCBased' in o and '/N 3' in o:
            warn.append('object %d still uses RGB: %s' % (x, o[:120]))
    return stats


def conv_fn(fn, col, mask, warn):
    """Convert a function's output colours (types 2 and 3; type 0 is sampled and left with a warning)."""
    def c(arr):
        v = [float(a) for a in arr.split()]
        if len(v) != 3:
            return None
        out = [grey(*v)] if mask else list(col.cmyk(*v))
        return '[' + ' '.join(fmt(a) for a in out) + ']'
    done = 0
    for key in ('C0', 'C1'):
        m = re.search(r'/%s\s*\[([^\]]*)\]' % key, fn)
        if m:
            new = c(m.group(1))
            if new:
                fn = fn[:m.start()] + '/%s%s' % (key, new) + fn[m.end():]
                done += 1
    if '/FunctionType 2' in fn and '/C0' not in fn:
        fn = fn.replace('/FunctionType 2', '/C0 [0 0 0 0] /FunctionType 2' if not mask else '/C0 [0] /FunctionType 2')
    if '/FunctionType 0' in fn:
        warn.append('a sampled gradient was left in RGB')
    return fn, done


def shading(doc, x, o, col, mask, warn):
    if '/DeviceRGB' not in o:
        return 0
    cs = '/DeviceGray' if mask else '/DeviceCMYK'

    def fix_dict(s):
        s = s.replace('/ColorSpace/DeviceRGB', '/ColorSpace' + cs).replace('/ColorSpace /DeviceRGB', '/ColorSpace ' + cs)
        # inline functions (type 2, and type 3 with type 2 parts)
        s, _ = conv_fn(s, col, mask, warn)
        for m in list(re.finditer(r'<<[^<>]*?/FunctionType\s+2[^<>]*?>>', s)):
            new, _ = conv_fn(m.group(0), col, mask, warn)
            s = s.replace(m.group(0), new)
        bg = re.search(r'/Background\s*\[([^\]]*)\]', s)
        if bg:
            v = [float(a) for a in bg.group(1).split()]
            s = s.replace(bg.group(0), '/Background[%s]' % ' '.join(fmt(a) for a in ([grey(*v)] if mask else col.cmyk(*v))))
        return s
    new = fix_dict(o)
    # functions held as separate objects
    for r in refs(o):
        ro = doc.xref_object(r, compressed=True)
        if '/FunctionType' in ro:
            for rr in [r] + refs(ro):
                fo = doc.xref_object(rr, compressed=True)
                if '/FunctionType' in fo:
                    doc.update_object(rr, conv_fn(fo, col, mask, warn)[0])
    doc.update_object(x, new)
    return 1


def image(doc, x, o, col, warn):
    import fitz
    if '/DeviceRGB' not in o and not re.search(r'/ColorSpace\s*\[\s*/ICCBased', o):
        return 0
    if '/ImageMask true' in o:
        return 0
    try:
        pix = fitz.Pixmap(doc, x)
    except Exception as e:
        warn.append('image %d could not be read: %s' % (x, e))
        return 0
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    data = col.image(pix.samples, pix.width, pix.height)
    smask = re.search(r'/SMask\s+(\d+) 0 R', o)
    import zlib
    doc.update_object(x, '<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceCMYK /BitsPerComponent 8 /Filter /FlateDecode%s >>'
                      % (pix.width, pix.height, ' /SMask %s 0 R' % smask.group(1) if smask else ''))
    doc.update_stream(x, zlib.compress(data, 9), compress=False)
    doc.xref_set_key(x, 'Filter', '/FlateDecode')
    return 1


def output_intent(doc, key):
    if key in PROFILES:
        name, ident, info = PROFILES[key]
        path = ICC / name
    else:
        path = Path(key)
        ident = info = path.stem
    if not path.is_file():
        raise SystemExit('No colour profile at %s. PSO Uncoated v3 FOGRA52 does not come with the kit (ECI does not '
                         'allow passing it on): download it from eci.org into assets/icc/, or give the print shop\'s '
                         'own .icc' % path)
    icc = path.read_bytes()
    if icc[16:20] != b'CMYK':
        raise SystemExit('%s is not a CMYK profile' % path)
    px = doc.get_new_xref()
    doc.update_object(px, '<< /N 4 >>')
    doc.update_stream(px, icc, compress=True)
    oi = doc.get_new_xref()
    esc = lambda s: s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    doc.update_object(oi, '<< /Type /OutputIntent /S /GTS_PDFX /OutputConditionIdentifier (%s) /OutputCondition (%s) '
                          '/RegistryName (http://www.color.org) /Info (%s) /DestOutputProfile %d 0 R >>'
                      % (esc(ident), esc(info), esc(info), px))
    doc.xref_set_key(doc.pdf_catalog(), 'OutputIntents', '[%d 0 R]' % oi)
    return path, info


def xmp(title, author, when, doc_id):
    esc = lambda s: (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
    xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"
    xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/">
   <dc:format>application/pdf</dc:format>
   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">%s</rdf:li></rdf:Alt></dc:title>
   <dc:creator><rdf:Seq><rdf:li>%s</rdf:li></rdf:Seq></dc:creator>
   <xmp:CreateDate>%s</xmp:CreateDate>
   <xmp:ModifyDate>%s</xmp:ModifyDate>
   <xmp:MetadataDate>%s</xmp:MetadataDate>
   <xmp:CreatorTool>House Style</xmp:CreatorTool>
   <pdf:Producer>House Style print_ready.py (PyMuPDF)</pdf:Producer>
   <pdf:Trapped>False</pdf:Trapped>
   <xmpMM:DocumentID>uuid:%s</xmpMM:DocumentID>
   <xmpMM:InstanceID>uuid:%s</xmpMM:InstanceID>
   <xmpMM:VersionID>1</xmpMM:VersionID>
   <xmpMM:RenditionClass>default</xmpMM:RenditionClass>
   <pdfxid:GTS_PDFXVersion>PDF/X-4</pdfxid:GTS_PDFXVersion>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>''' % (esc(title), esc(author), when, when, when, doc_id, uuid.uuid4())


def marks(doc, slug=10 * MM, length=5 * MM, gap=2 * MM):
    """New pages with room around the bleed for crop marks in registration colour."""
    import fitz
    out = fitz.open()
    for i, page in enumerate(doc):
        mb = page.mediabox
        trim = page.trimbox
        w, h = mb.width + 2 * slug, mb.height + 2 * slug
        np_ = out.new_page(width=w, height=h)
        np_.show_pdf_page(fitz.Rect(slug, slug, slug + mb.width, slug + mb.height), doc, i)
        t = fitz.Rect(trim.x0 - mb.x0 + slug, trim.y0 - mb.y0 + slug, trim.x1 - mb.x0 + slug, trim.y1 - mb.y0 + slug)
        bleed = max(0, trim.x0 - page.bleedbox.x0)   # the page's own bleed
        reg = (1, 1, 1, 1)
        off = bleed + gap
        for x in (t.x0, t.x1):
            for y in (t.y0, t.y1):
                sx = -1 if x == t.x0 else 1
                sy = -1 if y == t.y0 else 1
                np_.draw_line((x + sx * off, y), (x + sx * (off + length), y), color=reg, width=0.25)
                np_.draw_line((x, y + sy * off), (x, y + sy * (off + length)), color=reg, width=0.25)
        # boxes in the new page's own (top-left) coordinates
        np_.set_bleedbox(fitz.Rect(t.x0 - bleed, t.y0 - bleed, t.x1 + bleed, t.y1 + bleed))
        np_.set_trimbox(t)
    return out


def make(src, out=None, profile='fogra39', bleed=None, crop=False, proof=False, quiet=False):
    import fitz
    src = Path(src).resolve()
    out = Path(out).resolve() if out else src.with_name(src.stem + '-print.pdf')
    say = (lambda *a: None) if quiet else print
    doc = fitz.open(src)
    warn = []
    path = ICC / PROFILES[profile][0] if profile in PROFILES else Path(profile)
    col = Colour(path)
    stats = convert(doc, col, warn)
    # boxes: an existing TrimBox wins, else --bleed insets it from the page edge
    for page in doc:
        mb = page.mediabox
        has_trim = '/TrimBox' in doc.xref_object(page.xref, compressed=True)
        if bleed and not has_trim:
            b = bleed * MM
            page.set_trimbox(fitz.Rect(b, b, mb.width - b, mb.height - b))
        elif not has_trim:
            page.set_trimbox(fitz.Rect(0, 0, mb.width, mb.height))
        page.set_bleedbox(fitz.Rect(0, 0, mb.width, mb.height))
        for l in page.get_links():
            page.delete_link(l)
        a = page.first_annot
        while a:
            a = page.delete_annot(a)
    doc.set_toc([])
    if crop:
        doc2 = marks(doc)
        doc.close()
        doc = doc2
    md = fitz.open(src).metadata or {}
    title = md.get('title') or src.stem
    now = datetime.datetime.now().astimezone()
    when = now.isoformat(timespec='seconds')
    pdfdate = now.strftime("D:%Y%m%d%H%M%S") + now.strftime('%z')[:3] + "'" + now.strftime('%z')[3:] + "'"
    _, info = output_intent(doc, profile)
    doc.set_metadata({'title': title, 'author': md.get('author', ''), 'subject': md.get('subject', ''),
                      'keywords': md.get('keywords', ''), 'creator': 'House Style', 'producer': 'House Style print_ready.py (PyMuPDF)',
                      'creationDate': pdfdate, 'modDate': pdfdate, 'trapped': ''})
    info_x = int(doc.xref_get_key(-1, 'Info')[1].split()[0])
    doc.xref_set_key(info_x, 'Trapped', '/False')
    doc.set_xml_metadata(xmp(title, md.get('author', ''), when, uuid.uuid4()))
    buf = doc.tobytes(garbage=3, deflate=True, no_new_id=False)
    buf = re.sub(rb'^%PDF-1\.\d', b'%PDF-1.6', buf, count=1)
    out.write_bytes(buf)
    probs = check(out)
    say('Print file %s: %d pages, %s, %d content streams, %d gradients, %d pictures converted to CMYK; %s'
        % (out, len(fitz.open(out)), info, stats['streams'], stats['shadings'], stats['images'], kb(out.stat().st_size)))
    for w in warn + probs:
        say('  ! ' + w)
    if proof:
        p = soft_proof(out, path)
        say('  soft proof (how the press colours look on screen): %s' % p)
    return {'path': out, 'problems': warn + probs}


def kb(n):
    return '%.1f MB' % (n / 1048576) if n > 1048576 else '%d KB' % (n // 1024)


def check(pdf):
    """The PDF/X-4 rules this tool can check without a certified validator."""
    import fitz
    probs = []
    raw = Path(pdf).read_bytes()
    if not raw.startswith(b'%PDF-1.6'):
        probs.append('version header is not PDF 1.6')
    d = fitz.open(pdf)
    cat = d.xref_object(d.pdf_catalog(), compressed=True)
    m = re.search(r'/OutputIntents\s*\[\s*(\d+) 0 R', cat)
    if not m:
        probs.append('no output intent')
    else:
        oi = d.xref_object(int(m.group(1)), compressed=True)
        if '/GTS_PDFX' not in oi or '/DestOutputProfile' not in oi:
            probs.append('output intent lacks GTS_PDFX or its profile')
    x = d.get_xml_metadata()
    if 'PDF/X-4' not in x:
        probs.append('XMP does not name PDF/X-4')
    info = d.xref_object(int(d.xref_get_key(-1, 'Info')[1].split()[0]), compressed=True)
    if '/Trapped/False' not in info.replace(' ', '') and '/Trapped/True' not in info.replace(' ', ''):
        probs.append('Info has no Trapped key')
    if not (d.metadata or {}).get('title'):
        probs.append('no title')
    if '/ID' not in d.pdf_trailer():
        probs.append('no file ID')
    for i, page in enumerate(d):
        mb, bb, tb = page.mediabox, page.bleedbox, page.trimbox
        if not (mb.contains(bb) and bb.contains(tb)):
            probs.append('page %d: boxes do not nest (trim in bleed in media)' % (i + 1))
        if page.first_annot or page.get_links():
            probs.append('page %d has annotations or links' % (i + 1))
        for f in page.get_fonts():
            if f[2] != 'Type3' and f[1] in ('n/a', ''):
                probs.append('page %d: font not embedded: %s' % (i + 1, f[3]))
    rgb = 0
    for xr in range(1, d.xref_length()):
        o = d.xref_object(xr, compressed=True)
        if '/DeviceRGB' in o:
            rgb += 1
        elif d.xref_is_stream(xr) and ('/Subtype/Form' in o.replace(' ', '') or xr in {c for p in d for c in p.get_contents()}):
            if RGB_OP.search(d.xref_stream(xr).decode('latin-1')):
                rgb += 1
    if rgb:
        probs.append('%d objects still use RGB colour' % rgb)
    return probs


def soft_proof(pdf, profile, cols=4, width=300):
    """Render the CMYK pages and show them through the press profile, as a contact sheet."""
    import fitz
    from PIL import Image, ImageCms
    d = fitz.open(pdf)
    tr = ImageCms.buildTransform(ImageCms.getOpenProfile(str(profile)), ImageCms.createProfile('sRGB'), 'CMYK', 'RGB',
                                 ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
    tiles = []
    for page in d:
        z = width / page.rect.width
        pm = page.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csCMYK)
        tiles.append(ImageCms.applyTransform(Image.frombytes('CMYK', (pm.width, pm.height), pm.samples), tr))
    h = max(t.height for t in tiles)
    gap = 14
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (width + gap) + gap, rows * (h + gap) + gap), (205, 205, 205))
    for i, t in enumerate(tiles):
        sheet.paste(t, (gap + (i % cols) * (width + gap), gap + (i // cols) * (h + gap)))
    out = Path(pdf).with_name(Path(pdf).stem + '-proof.png')
    sheet.save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('pdf')
    ap.add_argument('-o', '--out')
    ap.add_argument('--profile', default='fogra39', help='fogra39 (default), gracol, uncoated, or a path to a CMYK .icc')
    ap.add_argument('--bleed', type=float, help='mm of bleed already on each side of the page (when the PDF has no TrimBox)')
    ap.add_argument('--marks', action='store_true', help='add crop marks outside the bleed')
    ap.add_argument('--proof', action='store_true', help='write a soft-proof contact sheet beside the print file')
    a = ap.parse_args()
    res = make(a.pdf, a.out, a.profile, a.bleed, a.marks, a.proof)
    sys.exit(1 if res['problems'] else 0)


if __name__ == '__main__':
    main()
