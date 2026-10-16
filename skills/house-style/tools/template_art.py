#!/usr/bin/env python3
"""Render a PowerPoint theme's or template's artwork: its title, content and section layouts as empty slides.

    python3 tools/template_art.py "office:Ion" out/            # writes cover.jpg, content.jpg, section.jpg, art.json
    python3 tools/template_art.py template.potx out/ --width 1920

It builds a small presentation with one empty slide per layout (Title Slide, Title and Content, Section Header),
so only the master's and layouts' own shapes and pictures show, never placeholder text, and LibreOffice draws it to
a PDF. Each page becomes a JPEG at the deck's width. art.json gives the slide size and, per layout, the title and body
placeholder boxes as fractions of the slide, so a theme can keep its text where the template keeps it.
A .thmx is a presentation package under theme/; a .potx or .pptx is one under ppt/. Either is copied under ppt/,
with only the new slides listed. tools/make_theme.py --art uses this.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

WANT = {'cover': ('Title Slide',), 'content': ('Title and Content', 'Title Only'), 'section': ('Section Header',)}
NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
SLIDE = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld %s><p:cSld><p:spTree><p:nvGrpSpPr>'
         '<p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>'
         '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>' % NS)
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
SOFFICE = [p for p in (Path.home() / 'Applications/LibreOffice.app/Contents/MacOS/soffice',
                       Path('/Applications/LibreOffice.app/Contents/MacOS/soffice')) if p.exists()]


def boxes(xml, master_xml, size):
    """Title and body placeholder boxes of a layout, as fractions; a placeholder with no position takes the master's."""
    def find(x, kinds):
        for sp in re.findall(r'<p:sp>.*?</p:sp>', x, re.S):
            ph = re.search(r'<p:ph\b([^>]*)/?>', sp)
            if not ph:
                continue
            t = (re.search(r'type="(\w+)"', ph.group(1)) or [None, 'body'])[1]
            if t in kinds:
                off, ext = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', sp), re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', sp)
                if off and ext:
                    return [int(off.group(1)) / size[0], int(off.group(2)) / size[1],
                            int(ext.group(1)) / size[0], int(ext.group(2)) / size[1]]
                return 'inherit'
        return None
    out = {}
    for name, kinds in (('title', ('title', 'ctrTitle')), ('body', ('body', 'subTitle', 'obj'))):
        b = find(xml, kinds)
        if b == 'inherit' or b is None:
            mb = find(master_xml, ('title',) if name == 'title' else ('body',))
            b = mb if isinstance(mb, list) else None
        if b:
            out[name] = [round(v, 4) for v in b]
    return out


def render(src, out, width=1920):
    src, out = Path(src), Path(out)
    if not SOFFICE:
        sys.exit('LibreOffice is needed to draw the artwork (not found in Applications)')
    z = zipfile.ZipFile(src)
    names = z.namelist()
    root = 'theme/' if 'theme/presentation.xml' in names else 'ppt/'
    work = Path(tempfile.mkdtemp(prefix='pc-art-'))
    pkg = work / 'art.pptx'
    pres = z.read(root + 'presentation.xml').decode('utf-8')
    size = tuple(int(v) for v in re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', pres).groups())
    layouts = {}
    for n in names:
        if re.match(re.escape(root) + r'slideLayouts/slideLayout\d+\.xml$', n):
            layouts[re.search(r'<p:cSld name="([^"]*)"', z.read(n).decode('utf-8')).group(1)] = n
    master = next(n for n in names if re.match(re.escape(root) + r'slideMasters/slideMaster1\.xml$', n))
    picked = {}
    for kind, wanted in WANT.items():
        hit = next((layouts[w] for w in wanted if w in layouts), None)
        if hit:
            picked[kind] = hit
    if not picked:
        sys.exit('No Title Slide, Title and Content or Section Header layout in %s' % src.name)

    rels = z.read(root + '_rels/presentation.xml.rels').decode('utf-8')
    rels = re.sub(r'<Relationship\b[^>]*Type="%sslide"[^>]*/>' % re.escape(REL), '', rels)
    ids, ctypes = [], z.read('[Content_Types].xml').decode('utf-8-sig')
    with zipfile.ZipFile(pkg, 'w', zipfile.ZIP_DEFLATED) as w:
        for n in names:
            if n in ('[Content_Types].xml', root + 'presentation.xml', root + '_rels/presentation.xml.rels', '_rels/.rels') \
                    or re.match(re.escape(root) + r'slides/', n):
                continue
            w.writestr('ppt/' + n[len(root):] if n.startswith(root) else n, z.read(n))
        for i, (kind, lay) in enumerate(picked.items(), 1):
            w.writestr('ppt/slides/slide%d.xml' % i, SLIDE)
            w.writestr('ppt/slides/_rels/slide%d.xml.rels' % i,
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.'
                       'openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="%sslideLayout" '
                       'Target="../slideLayouts/%s"/></Relationships>' % (REL, lay.rsplit('/', 1)[1]))
            rels = rels.replace('</Relationships>', '<Relationship Id="rIdArt%d" Type="%sslide" Target="slides/slide%d.xml"/>'
                                '</Relationships>' % (i, REL, i))
            ids.append('<p:sldId id="%d" r:id="rIdArt%d"/>' % (255 + i, i))
        pres = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>|<p:sldIdLst/>', '', pres, flags=re.S)
        pres = re.sub(r'(</p:sldMasterIdLst>)', r'\1' + '<p:sldIdLst>%s</p:sldIdLst>' % ''.join(ids), pres, count=1)
        w.writestr('ppt/presentation.xml', pres)
        w.writestr('ppt/_rels/presentation.xml.rels', rels)
        w.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://'
                   'schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="%sofficeDocument" '
                   'Target="ppt/presentation.xml"/></Relationships>' % REL)
        ctypes = ctypes.replace('PartName="/%s' % root, 'PartName="/ppt/')
        ctypes = re.sub(r'<Override PartName="/ppt/presentation.xml" ContentType="[^"]*"',
                        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.'
                        'presentationml.presentation.main+xml"', ctypes)
        ctypes = re.sub(r'<Override PartName="/ppt/slides/[^>]*/>', '', ctypes)
        ctypes = ctypes.replace('</Types>', ''.join(
            '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.'
            'presentationml.slide+xml"/>' % i for i in range(1, len(picked) + 1)) + '</Types>')
        w.writestr('[Content_Types].xml', ctypes)

    r = subprocess.run([str(SOFFICE[0]), '--headless', '-env:UserInstallation=file://' + str(work / 'lo'), '--convert-to', 'pdf',
                        '--outdir', str(work), str(pkg)], capture_output=True, text=True, timeout=240)
    pdf = work / 'art.pdf'
    if not pdf.exists():
        sys.exit('LibreOffice could not draw %s: %s' % (src.name, (r.stderr or r.stdout)[-400:]))
    import fitz
    out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    master_xml = z.read(master).decode('utf-8')
    info = {'source': src.name, 'size': [size[0], size[1]], 'ratio': round(size[0] / size[1], 4), 'layouts': {}}
    for i, (kind, lay) in enumerate(picked.items()):
        page = doc[i]
        zoom = width / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        pix.save(str(out / (kind + '.jpg')), jpg_quality=86)
        info['layouts'][kind] = {'layout': re.search(r'<p:cSld name="([^"]*)"', z.read(lay).decode('utf-8')).group(1),
                                 'file': kind + '.jpg', **boxes(z.read(lay).decode('utf-8'), master_xml, size)}
    (out / 'art.json').write_text(json.dumps(info, indent=1) + '\n', encoding='utf-8')
    shutil.rmtree(work, ignore_errors=True)
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('template', help='a .thmx, .potx or .pptx, or office:<name>')
    ap.add_argument('out', help='folder for the images and art.json')
    ap.add_argument('--width', type=int, default=1920)
    a = ap.parse_args()
    src = a.template
    if src.lower().startswith('office:'):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from make_theme import office_theme
        src = office_theme(src[7:])
    info = render(src, a.out, a.width)
    for k, v in info['layouts'].items():
        print('%-8s %-20s title %s  body %s' % (k, v['layout'], v.get('title'), v.get('body')))


if __name__ == '__main__':
    main()
