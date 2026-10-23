#!/usr/bin/env python3
"""Font facts the PowerPoint converter needs, read straight from the kit's TTF files (no fontTools).

    python3 tools/fontinfo.py                 # list every face: PostScript name, PowerPoint name, metrics
    python3 tools/fontinfo.py SchibstedGrotesk-SemiBold

faces() maps each face's PostScript name (the name Chrome writes into a printed PDF, after the subset
prefix "ABCDEF+") to a Face: its file, the family name PowerPoint and Windows know it by (name ID 1,
"Schibsted Grotesk SemiBold"), whether it is that family's bold or italic, the Google Fonts family
(name ID 16, "Schibsted Grotesk"), its weight, and its vertical metrics as fractions of the font size.
eot(path) wraps a TTF as an uncompressed Embedded OpenType file, the form PowerPoint stores embedded
fonts in (ppt/fonts/*.fntdata).
"""
import json
import struct
import sys
from functools import lru_cache
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
FONTS = KIT / 'fonts'


def tables(data):
    """{tag: bytes} of an sfnt (TrueType or OpenType) file."""
    n = struct.unpack('>H', data[4:6])[0]
    out = {}
    for i in range(n):
        tag, _, off, length = struct.unpack('>4sIII', data[12 + 16 * i: 28 + 16 * i])
        out[tag.decode('latin-1')] = data[off:off + length]
    return out


def names(name):
    """{name id: string}, preferring Windows Unicode English records."""
    _, count, base = struct.unpack('>HHH', name[:6])
    got = {}
    for i in range(count):
        pid, eid, lid, nid, length, off = struct.unpack('>HHHHHH', name[6 + 12 * i: 18 + 12 * i])
        raw = name[base + off: base + off + length]
        if pid == 3 and eid in (0, 1, 10) and lid == 0x409:
            got[nid] = raw.decode('utf-16-be', 'replace')
        elif pid == 1 and nid not in got:
            got.setdefault(nid, raw.decode('mac-roman', 'replace'))
    return got


class Face:
    def __init__(self, path):
        self.path = Path(path)
        data = self.path.read_bytes()
        t = tables(data)
        n = names(t['name'])
        self.psname = n.get(6, self.path.stem)
        self.family = n.get(1, '')                  # the name PowerPoint and Windows use
        self.subfamily = n.get(2, 'Regular')        # Regular, Bold, Italic or Bold Italic
        self.gfamily = n.get(16, self.family)       # the typographic family, as Google Fonts lists it
        self.full = n.get(4, self.family)
        self.version = n.get(5, '')
        head, hhea, os2 = t['head'], t['hhea'], t.get('OS/2', b'')
        self.upm = struct.unpack('>H', head[18:20])[0]
        mac_style = struct.unpack('>H', head[44:46])[0]
        self.checksum_adj = struct.unpack('>I', head[8:12])[0]
        a, d, g = struct.unpack('>hhh', hhea[4:10])
        self.asc, self.desc, self.gap = a / self.upm, -d / self.upm, g / self.upm
        self.weight, self.fstype, self.fsselection = 400, 0, 0
        self.panose, self.ranges, self.codepages = bytes(10), (0, 0, 0, 0), (0, 0)
        self.win_asc, self.win_desc = self.asc, self.desc
        self.typo = None
        if len(os2) >= 78:
            self.weight = struct.unpack('>H', os2[4:6])[0]
            self.fstype = struct.unpack('>H', os2[8:10])[0]
            self.panose = os2[32:42]
            self.ranges = struct.unpack('>IIII', os2[42:58])
            self.fsselection = struct.unpack('>H', os2[62:64])[0]
            ta, td, tg, wa, wd = struct.unpack('>hhhHH', os2[68:78])
            self.typo = (ta / self.upm, -td / self.upm, tg / self.upm)
            self.win_asc, self.win_desc = wa / self.upm, wd / self.upm
            if len(os2) >= 86:
                self.codepages = struct.unpack('>II', os2[78:86])
        sub = self.subfamily.lower()
        self.bold = 'bold' in sub or bool(mac_style & 1 and 'bold' in sub)
        self.italic = 'italic' in sub or bool(self.fsselection & 1)
        self.size = len(data)

    @property
    def slot(self):
        """Which of a family's four embedded-font slots this face fills."""
        return {(False, False): 'regular', (True, False): 'bold', (False, True): 'italic',
                (True, True): 'boldItalic'}[(self.bold, self.italic)]

    def __repr__(self):
        return '<Face %s: "%s" %s, %d, asc %.3f desc %.3f gap %.3f>' % (
            self.psname, self.family, self.slot, self.weight, self.asc, self.desc, self.gap)


@lru_cache(None)
def faces():
    """{PostScript name: Face} for every TTF in fonts/."""
    out = {}
    for p in sorted(FONTS.glob('*/*.ttf')):
        try:
            f = Face(p)
        except Exception as e:                       # a damaged file should not stop a conversion
            print('fontinfo: skipped %s (%s)' % (p.name, e), file=sys.stderr)
            continue
        out[f.psname] = f
    return out


def lookup(pdf_font_name, italic=None):
    """The Face for a font name as a PDF gives it ("ABCDEF+SchibstedGrotesk-SemiBold"), or None. italic settles
    a name cut short that two faces share ("...-SemiBol" for SemiBold and SemiBoldItalic)."""
    name = pdf_font_name.split('+')[-1]
    got = faces().get(name)
    if got is None:                                  # Chrome sometimes drops the style suffix of a Regular face
        got = faces().get(name + '-Regular')
    if got is None and len(name) >= 20:              # and PDF font names can be cut short ("...-SemiBol")
        hits = [f for ps, f in faces().items() if ps.startswith(name)]
        if len(hits) > 1 and italic is not None:
            hits = [f for f in hits if f.italic == italic]
        got = hits[0] if len(hits) == 1 else None
    return got


def eot(path):
    """An uncompressed EOT (version 0x00020002, as PowerPoint and Google Slides write them) holding the TTF."""
    f = Face(path) if not isinstance(path, Face) else path
    data = f.path.read_bytes()

    def string(s):
        b = s.encode('utf-16-le')
        return struct.pack('<H', len(b)) + b

    body = (struct.pack('<H', 0) + string(f.family) + struct.pack('<H', 0) + string(f.subfamily)
            + struct.pack('<H', 0) + string(f.version) + struct.pack('<H', 0) + string(f.full)
            + struct.pack('<HH', 0, 0)                 # padding, empty root string
            + struct.pack('<II', 0x50475342, 0)        # root string checksum (of nothing), EUDC code page
            + struct.pack('<HHII', 0, 0, 0, 0))        # padding, no signature, no EUDC font
    fixed = 80
    total = fixed + len(body) + len(data)
    head = struct.pack('<IIII', total, len(data), 0x00020002, 0)
    head += f.panose + struct.pack('<BBIH', 1, 1 if f.italic else 0, f.weight, f.fstype)
    head += struct.pack('<H', 0x504C) + struct.pack('<IIII', *f.ranges) + struct.pack('<II', *f.codepages)
    head += struct.pack('<I', f.checksum_adj) + struct.pack('<IIII', 0, 0, 0, 0)
    assert len(head) == fixed, len(head)
    return head + body + data


def main():
    fs = faces()
    want = sys.argv[1:]
    for ps, f in fs.items():
        if not want or ps in want:
            print(json.dumps({'ps': ps, 'family': f.family, 'slot': f.slot, 'gfamily': f.gfamily,
                              'weight': f.weight, 'asc': round(f.asc, 3), 'desc': round(f.desc, 3),
                              'gap': round(f.gap, 3), 'win': [round(f.win_asc, 3), round(f.win_desc, 3)],
                              'fstype': f.fstype}))


if __name__ == '__main__':
    main()
