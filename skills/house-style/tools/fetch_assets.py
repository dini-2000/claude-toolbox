#!/usr/bin/env python3
"""Download the kit's fonts and icons (run once; re-run to add a family).

Fonts: static TrueType files from Google Fonts (SIL Open Font License 1.1; Roboto Slab Apache 2.0), one folder per
family in fonts/, with the family's licence file from github.com/google/fonts, and fonts/fonts.json
listing every face. Icons: Lucide's sprite.svg and licence (ISC) from jsDelivr into icons/.

Ask the user before a run that fetches: what, where from, and the size. Files come over HTTPS from Google
Fonts, google/fonts on GitHub and jsDelivr only, at most 20 MB each, and a font must be a TrueType file; each is
written under a temporary name and renamed once complete. The Google Fonts CSS and jsDelivr's version lookup are
read straight into memory. Where the Claude Toolbox download screen (safe_get) is installed, set SAFE_GET_DIR to its
folder and every file goes through its quarantine and screen instead.

    python3 tools/fetch_assets.py            # fetch what is missing
"""
import json, os, re, sys, urllib.parse, urllib.request
from pathlib import Path

HOSTS = {'fonts.gstatic.com', 'raw.githubusercontent.com', 'cdn.jsdelivr.net'}
MAX_BYTES = 20 * 1024 * 1024


def plain_download_many(todo, folder, job=None, opener=None):
    """Save each (url, name, _) of todo in folder: HTTPS from HOSTS only, at most MAX_BYTES, fonts checked as TrueType."""
    opener = opener or urllib.request.urlopen
    for url, name, _ in todo:
        u = urllib.parse.urlsplit(url)
        if u.scheme != 'https' or u.hostname not in HOSTS:
            raise ValueError('not an expected source: ' + url)
        if os.path.basename(name) != name or name.startswith('.'):
            raise ValueError('not a plain file name: ' + name)
        data = opener(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60).read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('larger than %d MB: %s' % (MAX_BYTES >> 20, url))
        if name.endswith('.ttf') and data[:4] not in (b'\x00\x01\x00\x00', b'true'):
            raise ValueError('not a TrueType font: ' + url)
        part = Path(folder) / (name + '.part')
        part.write_bytes(data)
        part.replace(Path(folder) / name)


if os.environ.get('SAFE_GET_DIR'):
    sys.path.insert(0, os.environ['SAFE_GET_DIR'])
    from safe_get import download_many
else:
    download_many = plain_download_many

KIT = Path(__file__).resolve().parent.parent
FONTS, ICONS = KIT / 'fonts', KIT / 'icons'
UA = 'Mozilla/4.0'   # an old browser: Google Fonts then serves static TTF files
FAMILIES = {         # family: css2 axis spec (the weights and italics the themes use)
    'Schibsted Grotesk': 'ital,wght@0,400;0,500;0,600;0,700;1,400;1,600',   # italics and strong weights for documents
    'IBM Plex Sans': 'ital,wght@0,400;0,500;0,600;0,700;1,400;1,600',   # italics and strong weights for documents
    'IBM Plex Serif': 'wght@500;600',
    'IBM Plex Mono': 'wght@400;500',
    'Newsreader': 'ital,wght@0,400;0,500;0,600;1,400;1,500',
    'Atkinson Hyperlegible Next': 'ital,wght@0,400;0,700;1,400;1,700',   # italics and strong weights for documents
    'Caveat': 'wght@500;700',
    'Geist': 'ital,wght@0,400;0,500;0,600;0,700;1,400;1,600',   # italics and strong weights for documents
    'Geist Mono': 'wght@400;500',
    'Bricolage Grotesque': 'wght@400;600;800',
    'Cormorant Garamond': 'ital,wght@0,400;0,500;0,600;1,400;1,500',
    'Jost': 'ital,wght@0,300;0,400;0,500;0,600;1,400;1,500',   # italics and strong weights for documents
    'Fraunces': 'ital,wght@0,400;0,600;0,700;1,400',
    'Figtree': 'ital,wght@0,400;0,500;0,600;0,700;1,400;1,600',   # italics and strong weights for documents
    'Barlow': 'ital,wght@0,400;0,500;0,600;1,400;1,600',   # italics and strong weights for documents
    'Barlow Condensed': 'wght@500;600;700',
    'Pinyon Script': 'wght@400',
    'Archivo': 'ital,wght@0,400;0,500;0,700;0,900;1,400;1,700',   # italics and strong weights for documents
    'Source Serif 4': 'ital,wght@0,400;0,600;0,700;1,400;1,600',   # italics and strong weights for documents
    'Source Sans 3': 'ital,wght@0,400;0,600;0,700;1,400;1,600',   # italics and bold for documents
    'Instrument Serif': 'ital@0;1',
    'Instrument Sans': 'ital,wght@0,400;0,500;0,600;0,700;1,400;1,600',   # italics and strong weights for documents
    'Noto Sans Sinhala': 'wght@400;500;600;700',
    'Noto Serif Sinhala': 'wght@400;600;700',
    'Noto Sans Tamil': 'wght@400;500;600;700',
    'Noto Serif Tamil': 'wght@400;600;700',
    'Montserrat': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Poppins': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Lato': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Open Sans': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Roboto': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Inter': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Playfair Display': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Merriweather': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'EB Garamond': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Oswald': 'wght@400;500;600;700',   # for copied themes; no italics
    'DM Sans': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Raleway': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Nunito': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Lora': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # for copied themes
    'Roboto Slab': 'wght@400;500;600;700',   # for copied themes; no italics, and an ital axis empties the request
    'Source Code Pro': 'ital,wght@0,400;0,500;0,600;0,700;1,400',   # italics and strong weights for documents
    'Bodoni Moda': 'ital,wght@0,400;0,500;0,700;1,400',   # the kit's themes, ported and own
    'Bebas Neue': 'wght@400',   # the kit's themes, ported and own
    'Fredoka': 'wght@400;500;600;700',   # the kit's themes, ported and own
    'Space Grotesk': 'wght@400;500;700',   # the kit's themes, ported and own
    'Space Mono': 'ital,wght@0,400;0,700;1,400',   # the kit's themes, ported and own
    'Syne': 'wght@400;600;700;800',   # the kit's themes, ported and own
    'Unbounded': 'wght@400;600;800',   # the kit's themes, ported and own
    'Sora': 'wght@300;400;600;700',   # the kit's themes, ported and own
    'Plus Jakarta Sans': 'ital,wght@0,400;0,500;0,700;0,800;1,400;1,700',   # the kit's themes, ported and own
    'DM Serif Display': 'ital,wght@0,400;1,400',   # the kit's themes, ported and own
    'Kalam': 'wght@400;700',   # the kit's themes, ported and own
    'Lexend': 'wght@400;500;600;700',   # the kit's themes, ported and own
    'Rubik': 'ital,wght@0,400;0,500;0,700;1,400;1,700',   # the kit's themes, ported and own
    'Alfa Slab One': 'wght@400',   # the kit's themes, ported and own
    'Neucha': 'wght@400',   # the kit's themes, ported and own
    'Cabin Sketch': 'wght@400;700',   # the kit's themes, ported and own
    'League Gothic': 'wght@400',   # the kit's themes, ported and own
    'Quicksand': 'wght@400;500;600;700',   # the kit's themes, ported and own
    'News Cycle': 'wght@400;700',   # the kit's themes, ported and own
    'Nunito Sans': 'ital,wght@0,400;0,600;0,700;0,800;1,400;1,700',   # the kit's themes, ported and own
}
APACHE = {'Roboto Slab'}   # licensed under Apache 2.0, so google/fonts keeps it under apache/ with LICENSE.txt


def read_text(url):
    """A small text file (CSS, JSON) read into memory, never saved."""
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8')


def fetch_family(fam, spec, manifest):
    folder = FONTS / fam
    folder.mkdir(parents=True, exist_ok=True)
    css = read_text('https://fonts.googleapis.com/css2?family=%s:%s' % (fam.replace(' ', '+'), spec))
    faces, todo = [], []
    for block in re.findall(r'@font-face\s*{([^}]*)}', css):
        style = re.search(r'font-style:\s*(\w+)', block).group(1)
        weight = int(re.search(r'font-weight:\s*(\d+)', block).group(1))
        url = re.search(r'url\((https://[^)]+\.ttf)\)', block).group(1)
        name = '%s-%d%s.ttf' % (fam.replace(' ', ''), weight, 'i' if style == 'italic' else '')
        if not (folder / name).exists():
            todo.append((url, name, None))
        faces.append({'weight': weight, 'style': style, 'file': '%s/%s' % (fam, name), 'name': name})
    slug, apache = re.sub(r'[^a-z0-9]', '', fam.lower()), fam in APACHE
    lic = 'LICENSE.txt' if apache else 'OFL.txt'
    if not (folder / lic).exists():
        todo.append(('https://raw.githubusercontent.com/google/fonts/main/%s/%s/%s' % ('apache' if apache else 'ofl', slug, lic), lic, None))
    if todo:
        download_many(todo, str(folder), 'fonts-' + fam.lower().replace(' ', '-'))
    for f in faces:
        f['bytes'] = (folder / f.pop('name')).stat().st_size
    manifest[fam] = {'licence': 'Apache License 2.0' if apache else 'SIL Open Font License 1.1', 'licence_file': '%s/%s' % (fam, lic),
                     'source': 'Google Fonts', 'faces': sorted(faces, key=lambda f: (f['style'], f['weight']))}
    print('%-28s %d faces' % (fam, len(faces)))


def fetch_icons():
    ICONS.mkdir(exist_ok=True)
    ver = json.loads(read_text('https://data.jsdelivr.com/v1/packages/npm/lucide-static/resolved'))['version']
    base = 'https://cdn.jsdelivr.net/npm/lucide-static@%s/' % ver
    download_many([(base + 'sprite.svg', 'lucide-sprite.svg', None), (base + 'LICENSE', 'LICENSE-lucide.txt', None)],
                  str(ICONS), 'lucide-' + ver)
    (ICONS / 'lucide-version.txt').write_text(ver + '\n')
    n = (ICONS / 'lucide-sprite.svg').read_text().count('<symbol')
    print('Lucide %s: %d icons' % (ver, n))


if __name__ == '__main__':
    FONTS.mkdir(exist_ok=True)
    mpath = FONTS / 'fonts.json'
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    for fam, spec in FAMILIES.items():
        try:
            fetch_family(fam, spec, manifest)
        except Exception as e:
            print('FAILED %s: %s' % (fam, e), file=sys.stderr)
    mpath.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    if not (ICONS / 'lucide-sprite.svg').exists():
        fetch_icons()
