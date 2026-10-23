#!/usr/bin/env python3
"""Make a custom theme from a brand: its colours and fonts on the layout and artwork of a built theme.

    python3 tools/make_theme.py acme --name "Acme" --base meridian --accent "#E4572E" --accent-2 "#17BEBB"
    python3 tools/make_theme.py acme --tokens brand/design-tokens.json --base folio
    python3 tools/make_theme.py acme --brand docs/brand-guidelines.md --display Fraunces --body Figtree
    python3 tools/make_theme.py acme --logo brand/logo.png --base grid      colours read from a logo
    python3 tools/make_theme.py ion --reference "office:Ion"  copy an Office theme (--office lists them)
    python3 tools/make_theme.py talk --reference their-deck.pdf   copy a deck's colours and fonts (also .potx, .pptx, a picture)
    python3 tools/make_theme.py berlin --reference "office:Berlin" --art   ... and its own slide artwork (PowerPoint only)
    python3 tools/make_theme.py talk --reference template.potx --art --credit "Template: Name by Author, CC BY 4.0"
    python3 tools/make_theme.py --check acme                   check a custom theme again (an id or a style folder)
    python3 tools/make_theme.py --spec style.json [--out job/style] [--formats 16x9,a4-doc]
                                                              a theme from a style spec: a theme.json in part (fonts,
                                                              tokens, modes, palettes, chart, art recipe, name), laid
                                                              over its "base" theme (default meridian); --out keeps it
                                                              in a job's style folder instead of themes/<id>
    python3 tools/make_theme.py --fonts                       the font families the kit holds

Sources, later ones winning: the base theme; a design-tokens file (the design-system skill's format:
semantic.color.primary, accent or secondary, background, foreground, the dark set under dark.semantic, and
typography.font heading, body and mono; its radius is for UI parts, so only --radius sets one); a brand guidelines file (the brand skill's format: "Primary Color | #hex"
rows or "### Primary Colors" tables, and "Heading font" / "Body font" rows); a logo (PNG, JPEG, WebP or SVG: its most
used colour that is not near white, black or grey becomes the accent, and the next one of a clearly different hue the
second accent); a reference (a PowerPoint theme or file: accents 1 to 6, heading and body fonts, the master's
background for the mode, colour variants as palettes; a PDF: the biggest font for titles, the most used for text,
colours from its pages; a picture: as a logo, with its main colour as the background); then the flags. Fonts the kit
lacks are matched to the nearest held family (FONT_MAP).

After building it, the theme is checked (tools/selftest.py: the showcase in all seven formats, the sample outline and
a PowerPoint, into selftest/theme-<id>/) and the result goes in theme.json (custom.checked). tools/publish.py will not
publish a deck in a custom theme that has not passed. --no-check skips it for a quick look.

It writes themes/<id>/theme.json (the base's tokens and neutrals with the brand's accents, neutrals and fonts, a
"brand" palette, and the brand's colours at the head of the chart colours) and themes/<id>/theme.css (the base's
artwork, aimed at the new id), then builds the theme's tokens. tools/build_themes.py moves any colour that fails
contrast and says so. Fonts must be ones the kit holds (fonts/): a new family is a download, so ask the user first
(name, source, size) and add it with tools/fetch_assets.py. A missing family keeps the base theme's font, with a
warning. Each font role takes the held weight nearest to the one the base theme asks for.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_themes as bt  # noqa: E402

KIT = bt.KIT
THEMES = bt.THEMES
HEX = re.compile(r'^#[0-9A-Fa-f]{6}$')
WEIGHTS = {'display': ('--w-display', '--w-h1', '--w-h2'), 'body': ('--w-body', '--w-strong'),
           'label': ('--w-label',), 'stat': ('--w-stat',)}


def held_fonts():
    return json.loads((bt.FONTS / 'fonts.json').read_text(encoding='utf-8'))


def generic_of():
    """Each held family's generic class (sans, serif, mono, hand, script), as the built themes use it."""
    out = {}
    for f in THEMES.glob('*/theme.json'):
        for fam, gen in json.loads(f.read_text(encoding='utf-8')).get('fonts', {}).values():
            out.setdefault(fam, gen)
    return out


def first_family(stack):
    """'Space Grotesk', 'Inter', sans-serif -> Space Grotesk"""
    return stack.split(',')[0].strip().strip('"\'') if stack else None


def resolve(tokens, value, depth=0):
    """Follow {a.b.c} references in a design-tokens file to a final value."""
    while isinstance(value, dict) and '$value' in value:
        value = value['$value']
    m = re.fullmatch(r'\{([^}]+)\}', value.strip()) if isinstance(value, str) else None
    if not m or depth > 8:
        return value
    node = tokens
    for k in m.group(1).split('.'):
        node = node.get(k) if isinstance(node, dict) else None
        if node is None:
            return None
    return resolve(tokens, node, depth + 1)


def chromatic(h):
    return h and HEX.match(h) and bt.oklch(h)[1] > 0.04


def from_tokens(path):
    t = json.loads(Path(path).read_text(encoding='utf-8'))
    sem = t.get('semantic', {})
    col = sem.get('color', {})
    get = lambda node, k: resolve(t, node.get(k)) if node.get(k) is not None else None  # noqa: E731
    out = {'accent': get(col, 'primary')}
    for k in ('accent', 'secondary'):              # the second accent: the first of these with real colour
        v = get(col, k)
        if chromatic(v) and v != out['accent']:
            out['accent_2'] = v
            break
    out['light'] = {'bg': get(col, 'background'), 'ink': get(col, 'foreground')}
    dcol = t.get('dark', {}).get('semantic', {}).get('color', {})
    out['dark'] = {'bg': get(dcol, 'background'), 'ink': get(dcol, 'foreground')}
    font = sem.get('typography', {}).get('font', {})
    out['display'] = first_family(get(font, 'heading'))
    out['body'] = first_family(get(font, 'body'))
    out['mono'] = first_family(get(font, 'mono'))
    return {k: v for k, v in out.items() if v}, None


def from_brand(path):
    text = Path(path).read_text(encoding='utf-8')
    out = {}
    row = lambda label: re.search(label + r'\s*\*{0,2}\s*\|\s*(#[0-9A-Fa-f]{6})\b', text, re.I)  # noqa: E731
    for key, label in (('accent', r'Primary Colou?r'), ('accent_2', r'(?:Accent|Secondary) Colou?r')):
        m = row(label)
        if m:
            out[key] = m.group(1)
    for key, heading in (('accent', 'Primary'), ('accent_2', 'Accent'), ('accent_2', 'Secondary')):
        if out.get(key):
            continue
        sec = re.search(r'### %s Colou?rs[\s\S]*?(?=\n###|\Z)' % heading, text, re.I)
        for m in re.finditer(r'\|\s*\*{0,2}([^*|]+?)\*{0,2}\s*\|\s*(#[0-9A-Fa-f]{6})\b', sec.group(0) if sec else ''):
            if not re.search(r'dark|light', m.group(1), re.I):
                out[key] = m.group(2)
                break
    for key, label in (('bg', r'Background'), ('ink', r'Text Primary')):      # the neutral palette, for light mode
        m = row(r'\|\s*\*{0,2}' + label)
        if m:
            out.setdefault('light', {})[key] = m.group(1)
    for key, var in (('display', 'heading'), ('body', 'body'), ('mono', 'mono')):   # a CSS font stack in the guidelines
        m = re.search(r'--font-%s:\s*([^;\n]+)' % var, text)
        if m:
            out[key] = first_family(m.group(1))
    m = re.search(r'Primary Font\s*\*{0,2}\s*\|\s*([^|\n]+?)\s*\|', text, re.I)   # the quick reference's one font
    if m:
        out.setdefault('display', first_family(m.group(1)))
        out.setdefault('body', first_family(m.group(1)))
    for key, label in (('display', r'(?:Heading|Headline|Display) (?:font|typeface)'), ('body', r'Body (?:font|typeface)')):
        m = re.search(r'\|\s*\*{0,2}%s\*{0,2}\s*\|\s*\*{0,2}([A-Za-z][A-Za-z0-9 ]+?)\*{0,2}\s*\|' % label, text, re.I) or \
            re.search(r'\*\*%s:?\*\*:?\s*([A-Z][A-Za-z0-9 ]+?)(?:[,(.\n]| -)' % label, text, re.I)
        if m:
            out[key] = first_family(m.group(1))
    title = re.search(r'^#\s+(.+?)\s+Brand Guidelines\b', text, re.I | re.M)
    return out, title.group(1).strip() if title else None


def nearest(weights, want):
    return min(weights, key=lambda w: (abs(w - want), -w))


def from_logo(path):
    """A logo's two leading colours: the most used chromatic colour, then the next one of a clearly different hue."""
    import math
    from collections import Counter
    path, counts = Path(path), Counter()
    if path.suffix.lower() == '.svg':
        text = path.read_text(encoding='utf-8', errors='replace')
        for h in re.findall(r'(?:fill|stop-color|stroke)\s*[:=]\s*["\']?(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})\b', text):
            h = h if len(h) == 7 else '#' + ''.join(c * 2 for c in h[1:])
            counts[h.upper()] += 1
    else:
        from PIL import Image
        im = Image.open(path).convert('RGBA')
        im.thumbnail((240, 240))
        rgb = Image.new('RGB', im.size, (255, 255, 255))
        rgb.paste(im, mask=im.split()[3])
        mask = [a >= 128 for a in im.split()[3].getdata()]
        q = rgb.quantize(colors=12, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        for idx, keep in zip(q.getdata(), mask):
            if keep:
                counts['#%02X%02X%02X' % tuple(pal[idx * 3:idx * 3 + 3])] += 1
    return {k: v for k, v in zip(('accent', 'accent_2'), pick_accents(h for h, _ in counts.most_common()))}


def chroma_ok(h):
    L, C, _ = bt.oklch(h)
    return C >= 0.05 and 0.15 <= L <= 0.95                 # not near white, black or grey


def pick_accents(colours, n=2):
    """The first chromatic colour, then the next ones of a clearly different hue (35 degrees or more)."""
    import math
    picked = []
    for h in colours:
        if not chroma_ok(h):
            continue
        H = bt.oklch(h)[2]
        if not picked or all(abs(math.remainder(H - bt.oklch(p)[2], math.tau)) > math.radians(35) for p in picked):
            picked.append(h)
        if len(picked) == n:
            break
    return picked


# Families a reference may name, mapped to the nearest family the kit holds. Office, Apple and Adobe faces cannot be
# embedded; a family the kit holds (41, incl. Montserrat, Poppins, Lato, Open Sans, Roboto, Inter, Playfair Display,
# Merriweather, EB Garamond, Oswald, DM Sans, Raleway, Nunito, Lora, Roboto Slab) matches as 'same' before this map.
# For any other Google family a download gives the exact face (ask the user first).
FONT_MAP = {
    'Roboto': 'arial',
    'Inter': 'helvetica helveticaneue neuehaasgrotesk neuehaasgrotesktextpro akzidenzgrotesk sfpro sfprodisplay sfprotext',
    'Archivo': 'franklingothic franklingothicbook franklingothicmedium franklingothicdemi librefranklin bierstadt',
    'Jost': 'futura futurapt twcenmt avenir avenirnext avenirnextltpro questrial urbanist outfit lexend',
    'Poppins': 'centurygothic',
    'Montserrat': 'gotham',
    'Lato': 'calibri calibrilight carlito gillsans gillsansmt gillsansnova',
    'Open Sans': 'segoeui segoeuilight segoeuisemibold trebuchetms trebuchet notosans',
    'Source Sans 3': 'corbel firasans ptsans myriadpro sourcesanspro',
    'Figtree': 'aptos aptosdisplay candara nunitosans tenorite grandview skeena proximanova mulish',
    'Geist': 'manrope plusjakartasans',
    'Schibsted Grotesk': 'spacegrotesk worksans hankengrotesk',
    'Atkinson Hyperlegible Next': 'verdana verdanapro tahoma atkinsonhyperlegible',
    'Barlow': 'din dinpro dinalternate bahnschrift',
    'Oswald': 'impact leaguegothic alternategothic',
    'Barlow Condensed': 'twcenmtcondensed twcenmtcondensedextrabold bebasneue arialnarrow dincondensed aptosnarrow',
    'Merriweather': 'georgia georgiapro',
    'Source Serif 4': 'timesnewroman times cambria constantia ptserif seaford charter sourceserifpro notoserif',
    'Newsreader': 'bookantiqua palatino palatinolinotype baskerville baskervilleoldface librebaskerville '
                  'crimsontext crimsonpro minionpro',
    'EB Garamond': 'garamond adobegaramondpro',
    'Cormorant Garamond': 'cormorant',
    'Playfair Display': 'didot bodoni72 bodonimt',
    'Instrument Serif': 'dmserifdisplay abrilfatface',
    'Fraunces': 'cooperblack recoleta youngserif',
    'Roboto Slab': 'rockwell rockwellcondensed arvo zillaslab',
    'IBM Plex Mono': 'couriernew courier sourcecodepro robotomono',
    'Geist Mono': 'consolas menlo monaco sfmono jetbrainsmono firacode cascadiacode',
    'Caveat': 'comicsansms segoeprint dancingscript kalam patrickhand inkfree',
    'Pinyon Script': 'segoescript brushscriptmt edwardianscriptitc greatvibes allura',
}
FONT_NEAR = {k: fam for fam, keys in FONT_MAP.items() for k in keys.split()}


def font_key(name):
    """'ABCDEF+OpenSans-SemiBold' -> opensans; 'TimesNewRomanPSMT' -> timesnewroman; 'Calibri Light' -> calibrilight"""
    name = re.sub(r'^[A-Z]{6}\+', '', name or '').split(',')[0].split('-')[0]
    return re.sub(r'(psmt|mt|ps)$', '', re.sub(r'[^a-z0-9]', '', name.lower())) or re.sub(r'[^a-z0-9]', '', name.lower())


def match_font(name):
    """The held family for a font name, and how: 'same', 'nearest' or 'guess'."""
    held = {font_key(f): f for f in held_fonts()}
    k = font_key(name)
    if k in held:
        return held[k], 'same'
    for key in (k, re.sub(r'(light|regular|medium|semibold|bold|black|book|display|text)$', '', k)):
        if key in FONT_NEAR:
            return FONT_NEAR[key], 'nearest'
        if key in held:
            return held[key], 'same'
    for pat, fam in ((r'mono|code|courier|consol', 'IBM Plex Mono'), (r'script|brush|callig', 'Pinyon Script'),
                     (r'hand|marker|comic', 'Caveat'), (r'condensed|narrow|compressed', 'Barlow Condensed'),
                     (r'slab', 'Roboto Slab'),
                     (r'(?<!sans)serif|garamond|times|roman|antiqua|georgia|minion|caslon|bodoni|didot|baskerville',
                      'Source Serif 4')):
        if re.search(pat, k):
            return fam, 'guess'
    return 'Source Sans 3', 'guess'


OFFICE = Path('/Applications/Microsoft PowerPoint.app/Contents/Resources/Office Themes')


def office_theme(name):
    """office:Ion -> the Ion theme that PowerPoint for Mac installs (39 of them)."""
    for p in OFFICE.glob('*.thmx'):
        if p.stem.lower() == name.lower():
            return p
    have = ', '.join(sorted(p.stem for p in OFFICE.glob('*.thmx'))) or 'none (PowerPoint is not installed here)'
    sys.exit('No Office theme %r. Office themes on this computer: %s' % (name, have))


def from_reference(path):
    """Colours, fonts and mode from a reference: a PowerPoint theme or file, a PDF of a deck, or a picture of one."""
    if str(path).lower().startswith('office:'):
        path = office_theme(str(path)[7:])
    path = Path(path).expanduser()
    if not path.is_file():
        sys.exit('No such file: %s' % path)
    ext = path.suffix.lower()
    if ext in ('.thmx', '.pptx', '.potx', '.pptm', '.potm', '.ppsx'):
        return from_powerpoint(path)
    if ext == '.pdf':
        return from_pdf(path)
    if ext in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'):
        got = from_logo(path)
        if ext != '.svg':
            from PIL import Image
            im = Image.open(path).convert('RGB')
            im.thumbnail((240, 240))
            q = im.quantize(colors=12, method=Image.Quantize.MEDIANCUT)
            idx = max(set(q.getdata()), key=list(q.getdata()).count)
            set_ground(got, '#%02X%02X%02X' % tuple(q.getpalette()[idx * 3:idx * 3 + 3]))
        got['ref_name'] = path.stem
        return got
    sys.exit('A reference is a PowerPoint theme or file (.thmx, .potx, .pptx), a PDF, or a picture (PNG, JPEG, WebP, SVG)')


def set_ground(got, bg):
    """The reference's background colour sets the default mode, and the background itself when it suits that mode."""
    mode = 'dark' if bt.is_dark(bg) else 'light'
    got['mode'] = mode
    L = bt.oklch(bg)[0]
    if (mode == 'light' and L >= 0.9) or (mode == 'dark' and L <= 0.3):
        got.setdefault(mode, {})['bg'] = bg
    got['ground'] = bg


def zip_rel(z, part, rid):
    """Where relationship rid of a package part points, as a path inside the zip."""
    import posixpath
    d, f = posixpath.split(part)
    rels = d + '/_rels/' + f + '.rels'
    if rels not in z.namelist():
        return None
    m = re.search(r'<Relationship\b[^>]*Id="%s"[^>]*>' % re.escape(rid), z.read(rels).decode('utf-8', 'replace'))
    t = m and re.search(r'Target="([^"]+)"', m.group(0))
    return posixpath.normpath(posixpath.join(d, t.group(1))) if t else None


def scheme_of(xml):
    m = re.search(r'<a:clrScheme\b[^>]*?name="([^"]*)"[^>]*>(.*?)</a:clrScheme>', xml, re.S)
    if not m:
        return None, {}
    cols = re.findall(r'<a:(dk1|lt1|dk2|lt2|accent[1-6])>\s*<a:(?:srgbClr val|sysClr [^>]*?lastClr)="([0-9A-Fa-f]{6})"', m.group(2))
    return m.group(1), {k: '#' + v.upper() for k, v in cols}


def from_powerpoint(path):
    import io
    import zipfile
    z = zipfile.ZipFile(path)
    names = z.namelist()
    master = next((n for n in sorted(names) if re.search(r'(^|/)slideMasters/slideMaster1\.xml$', n)
                   and not n.startswith('themeVariants/')), None)
    mxml = z.read(master).decode('utf-8', 'replace') if master else ''
    rid = re.search(r'<Relationship\b[^>]*Type="[^"]*/theme"[^>]*>', z.read(master.replace('slideMasters/', 'slideMasters/_rels/') + '.rels').decode()) if master else None
    tpath = None
    if rid:
        tpath = zip_rel(z, master, re.search(r'Id="([^"]+)"', rid.group(0)).group(1))
    tpath = tpath or next(n for n in sorted(names) if re.search(r'theme/theme\d*\.xml$', n) and not n.startswith('themeVariants/'))
    txml = z.read(tpath).decode('utf-8', 'replace')
    sname, cols = scheme_of(txml)
    accents = [cols[k] for k in ('accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6') if k in cols]
    got = {k: v for k, v in zip(('accent', 'accent_2'), pick_accents(accents))}
    got['chart'] = [c for c in accents if chroma_ok(c)]
    fonts = dict(re.findall(r'<a:(majorFont|minorFont)>\s*<a:latin typeface="([^"]*)"', txml))
    got['ref_fonts'] = {'display': fonts.get('majorFont'), 'body': fonts.get('minorFont')}
    got['ref_name'] = (re.search(r'<a:theme\b[^>]*name="([^"]*)"', txml) or [None, sname or path.stem])[1]
    if path.suffix.lower() in ('.pptx', '.potx', '.pptm', '.potm', '.ppsx') or got['ref_name'].startswith('Office Theme'):
        got['ref_name'] = path.stem

    # The master's background: a colour from the scheme (through the master's colour map), or a picture
    cmap = dict(re.findall(r'\b(bg1|tx1|bg2|tx2)="(\w+)"', (re.search(r'<p:clrMap\b[^>]*>', mxml) or [''])[0] if mxml else ''))
    alias = {'bg1': 'lt1', 'tx1': 'dk1', 'bg2': 'lt2', 'tx2': 'dk2'}
    bgx = (re.search(r'<p:bg>(.*?)</p:bg>', mxml, re.S) or [None, ''])[1]
    ground, pic = None, None
    sc = re.search(r'<a:schemeClr val="(\w+)"', bgx)
    if sc:
        v = sc.group(1)
        ground = cols.get(cmap.get(v, alias.get(v, v)), cols.get(v))
    rgb = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', bgx)
    if rgb and '<a:blip' not in bgx:
        ground = '#' + rgb.group(1).upper()
    ref = re.search(r'<p:bgRef idx="(\d+)"', bgx)
    if ref and int(ref.group(1)) >= 1001:
        fills = re.search(r'<a:bgFillStyleLst>(.*?)</a:bgFillStyleLst>', txml, re.S)
        items = re.findall(r'<a:(solidFill|gradFill|blipFill|pattFill|noFill)\b.*?(?:</a:\1>|/>)', fills.group(1), re.S) if fills else []
        k = int(ref.group(1)) - 1001
        if k < len(items) and items[k] == 'blipFill':
            blips = [m.group(0) for m in re.finditer(r'<a:blipFill\b.*?</a:blipFill>', fills.group(1), re.S)]
            nb = items[:k].count('blipFill')
            emb = re.search(r'r:embed="([^"]+)"', blips[nb]) if nb < len(blips) else None
            pic = emb and zip_rel(z, tpath, emb.group(1))
    emb = re.search(r'<a:blip\b[^>]*r:embed="([^"]+)"', bgx)
    if emb:
        pic = zip_rel(z, master, emb.group(1))
    if pic and pic in names:
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(z.read(pic))).convert('RGBA')
            under = Image.new('RGBA', im.size, ground or '#FFFFFF')   # a see-through texture sits on the scheme colour
            im = Image.alpha_composite(under, im).convert('RGB').resize((1, 1), Image.Resampling.BOX)
            ground = '#%02X%02X%02X' % im.getpixel((0, 0))
            got['ref_picture'] = True
        except Exception:                                  # HD Photo (.wdp) and the like: keep the scheme colour
            pass
    if ground:
        set_ground(got, ground)
    dk2 = cols.get('dk2')
    if dk2 and chroma_ok(dk2) and bt.contrast(dk2, '#FFFFFF') >= 8 and not (got.get('dark') or {}).get('bg'):
        got.setdefault('dark', {})['bg'] = dk2

    # Office themes carry colour variants: each becomes a palette
    extra = []
    for vt in sorted(n for n in names if re.match(r'themeVariants/variant\d+/theme/theme/theme\d*\.xml$', n)):
        vname, vcols = scheme_of(z.read(vt).decode('utf-8', 'replace'))
        pair = pick_accents([vcols[k] for k in ('accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6') if k in vcols])
        if pair and pair[0] != got.get('accent') and all(pair[0] != e[1] for e in extra):
            if not vname or vname == got['ref_name'] or any(vname == e[0] for e in extra):
                vname = '%s, variant %s' % (got['ref_name'], re.search(r'variant(\d+)', vt).group(1))
            extra.append((vname, pair[0], pair[1] if len(pair) > 1 else None))
    got['more_palettes'] = extra[:4]
    return got


def from_pdf(path):
    """Fonts from a PDF's text (the biggest is the display face, the most used the body face), colours from its pages."""
    from collections import Counter
    import fitz
    from PIL import Image
    doc = fitz.open(path)
    size, chars = Counter(), Counter()
    for page in doc.pages(0, min(len(doc), 12)):
        for b in page.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                for s in ln['spans']:
                    n = len(s['text'].strip())
                    if n:
                        chars[s['font']] += n
                        size[s['font']] = max(size[s['font']], s['size'])
    got = {'ref_name': path.stem}
    if chars:
        got['ref_fonts'] = {'display': max(size, key=size.get), 'body': chars.most_common(1)[0][0]}
    counts = Counter()
    for page in doc.pages(0, min(len(doc), 8)):
        pix = page.get_pixmap(matrix=fitz.Matrix(160 / page.rect.width, 160 / page.rect.width))
        q = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).quantize(colors=12, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        for idx in q.getdata():
            counts['#%02X%02X%02X' % tuple(pal[idx * 3:idx * 3 + 3])] += 1
    got.update({k: v for k, v in zip(('accent', 'accent_2'), pick_accents(h for h, _ in counts.most_common()))})
    if counts:
        set_ground(got, counts.most_common(1)[0][0])
    return got


def make(a):
    ref = from_reference(a.reference) if a.reference else None
    if ref and ref.get('ref_fonts'):
        ref['fonts_held'] = {r: match_font(f) for r, f in ref['ref_fonts'].items() if f}
    if not a.base:                                 # a serif reference sits best on Folio's layout, the rest on Meridian's
        disp = ((ref or {}).get('fonts_held') or {}).get('display')
        a.base = 'folio' if disp and generic_of().get(disp[0]) == 'serif' else 'meridian'
    base_dir = THEMES / a.base
    if not (base_dir / 'theme.json').exists():
        sys.exit('No theme %r to build on. Built themes: %s' % (a.base, ', '.join(sorted(p.parent.name for p in THEMES.glob('*/theme.json')))))
    if not re.fullmatch(r'[a-z][a-z0-9-]{1,23}', a.id):
        sys.exit('The id is lower case letters, digits and hyphens, 2 to 24 characters')
    out_dir = THEMES / a.id
    if (out_dir / 'theme.json').exists() and not json.loads((out_dir / 'theme.json').read_text(encoding='utf-8')).get('custom'):
        sys.exit('%s is one of the kit\'s own themes: choose another id' % a.id)
    base = json.loads((base_dir / 'theme.json').read_text(encoding='utf-8'))
    got, title = {}, None
    if a.tokens:
        got, _ = from_tokens(a.tokens)
    if a.brand:
        more, title = from_brand(a.brand)
        got.update(more)
    if a.logo:
        more = from_logo(a.logo)
        if not more:
            print('The logo has no colour apart from white, black and grey: give --accent')
        else:
            print('From the logo: %s' % ', '.join('%s %s' % (k.replace('_', ' '), v) for k, v in more.items()))
        got.update(more)
    if ref:
        held = ref.get('fonts_held') or {}
        for role in ('display', 'body'):
            if role in held:
                got[role] = held[role][0]
        for k in ('accent', 'accent_2', 'chart', 'light', 'dark', 'more_palettes'):
            if ref.get(k):
                got[k] = ref[k]
        title = title or ref.get('ref_name')
        said = ['%s %s' % (k.replace('_', ' '), ref[k]) for k in ('accent', 'accent_2') if ref.get(k)]
        for role, (fam, how) in held.items():
            said.append('%s font %s%s' % ('title' if role == 'display' else 'text', ref['ref_fonts'][role],
                                          '' if how == 'same' else ' -> %s (%s the kit holds)' % (fam, 'nearest' if how == 'nearest' else 'a guess at the nearest')))
        if ref.get('ground'):
            said.append('%s background %s%s' % (ref['mode'], ref['ground'], ' (a picture)' if ref.get('ref_picture') else ''))
        if ref.get('more_palettes'):
            said.append('%d more palettes from its colour variants' % len(ref['more_palettes']))
        print('From the reference (%s): %s' % (ref.get('ref_name'), '; '.join(said)))
        if any(how != 'same' for _, how in held.values()):
            print('  A face the kit lacks is matched to the nearest held family. For the exact face, if it is a Google font, ask the user to download it.')
    for k in ('accent', 'accent_2', 'display', 'body', 'mono', 'radius'):
        if getattr(a, k, None):
            got[k] = getattr(a, k)
    for mode in ('light', 'dark'):
        for k in ('bg', 'ink'):
            v = getattr(a, '%s_%s' % (mode, k), None)
            if v:
                got.setdefault(mode, {})[k] = v
    if not got.get('accent'):
        sys.exit('No brand colour found: give --accent, or a --tokens or --brand file that has one')
    for k in ('accent', 'accent_2'):
        if got.get(k) and not HEX.match(got[k]):
            sys.exit('%s must be a colour like #2F54EB, not %r' % (k, got[k]))
    name = a.name or title or a.id.replace('-', ' ').title()
    warn = []

    theme = json.loads(json.dumps(base))
    theme['name'] = name
    theme['summary'] = '%s colours and type on the %s layout: %s' % (name, base['name'], base['summary'][0].lower() + base['summary'][1:])
    theme['custom'] = {'base': a.base, 'source': ', '.join(str(p) for p in (a.tokens, a.brand, a.logo, a.reference) if p) or 'flags'}

    # Fonts: held families only, each role at the held weight nearest the base theme's
    fonts, gen = held_fonts(), generic_of()
    roles = {'display': got.get('display'), 'body': got.get('body'), 'mono': got.get('mono')}
    fam_of = lambda r: base['fonts'].get(r, [None])[0]  # noqa: E731
    for r in ('stat', 'label', 'quote'):           # roles that share the display or body face in the base share it here
        roles[r] = roles['display'] if fam_of(r) == fam_of('display') else roles['body'] if fam_of(r) == fam_of('body') else None
    for role, fam in roles.items():
        if not fam or role not in theme['fonts']:
            continue
        if fam not in fonts:
            line = ('%r is not in the kit, so the %s fonts stay. A new family is a download: ask the user (name, source, size), '
                    'then add it with tools/fetch_assets.py' % (fam, base['name']))
            if line not in warn:
                warn.append(line)
            continue
        theme['fonts'][role] = [fam, gen.get(fam, 'mono' if role == 'mono' else 'sans')]
        held = sorted({f['weight'] for f in fonts[fam]['faces'] if f['style'] == 'normal'})
        for tok in WEIGHTS.get(role, ()):
            if tok in theme['tokens'] and held:
                theme['tokens'][tok] = str(nearest(held, int(theme['tokens'][tok])))
    if got.get('radius'):
        theme['tokens']['--radius'] = got['radius']
        theme['tokens']['--radius-sm'] = '%gpx' % round(float(got['radius'][:-2]) * .66)

    # Neutrals the brand sets
    for mode in ('light', 'dark'):
        for k, v in (got.get(mode) or {}).items():
            if v and HEX.match(v):
                if bt.is_dark(v) != (mode == 'dark') and k == 'bg':
                    warn.append('%s background %s is not a %s colour: left out' % (mode, v, mode))
                    continue
                theme['modes'][mode][k] = v
        bg, given = theme['modes'][mode]['bg'], got.get(mode) or {}
        if given.get('bg') and len(given) == 1:    # only a background given: tint the base's other neutrals to it
            m, toward = theme['modes'][mode], ('#FFFFFF' if mode == 'dark' else '#000000')
            steps = {'bg_alt': .04, 'surface_2': .09, 'line': .16} if mode == 'dark' else {'bg_alt': .03, 'surface_2': .05, 'line': .1}
            for k, t in steps.items():
                m[k] = bt.mix(bg, toward, t)
            m['surface'] = bt.mix(bg, toward, .06) if mode == 'dark' else (bg if bt.oklch(bg)[0] > .97 else bt.mix(bg, '#FFFFFF', .6))
            m['letterbox'] = bt.mix(bg, '#000000', .55)
            if isinstance(m.get('alt'), dict):
                m['alt'] = {'surface': bt.mix(bg, toward, .09), 'surface_2': bt.mix(bg, toward, .13)}

    # The brand palette: the accents as given in light mode, moved lighter to read on the dark background
    acc, acc2 = got['accent'], got.get('accent_2')
    pal = {'name': name, 'light': {'accent': acc}, 'dark': {'accent': bt.reach(acc, [theme['modes']['dark']['bg']], 3.0)}}
    if acc2:
        pal['light']['accent_2'] = acc2
        pal['dark']['accent_2'] = bt.reach(acc2, [theme['modes']['dark']['bg']], 3.0)
    else:
        first = base['palettes'][base['defaults']['palette']]
        pal['light']['accent_2'] = first['light'].get('accent_2', first['light']['accent'])
        pal['dark']['accent_2'] = first['dark'].get('accent_2', first['dark']['accent'])
    theme['palettes'] = {'brand': pal}
    if acc2:
        theme['palettes']['brand-2'] = {'name': name + ', second colour first',
                                        'light': {'accent': acc2, 'accent_2': acc},
                                        'dark': {'accent': pal['dark']['accent_2'], 'accent_2': pal['dark']['accent']}}
    for vname, v1, v2 in got.get('more_palettes', []):
        v2 = v2 or acc
        pid = re.sub(r'[^a-z0-9]+', '-', vname.lower()).strip('-')[-24:].strip('-') or 'variant'
        if pid in theme['palettes']:
            pid = 'variant-%d' % len(theme['palettes'])
        theme['palettes'][pid] = {'name': vname, 'light': {'accent': v1, 'accent_2': v2},
                                  'dark': {'accent': bt.reach(v1, [theme['modes']['dark']['bg']], 3.0),
                                           'accent_2': bt.reach(v2, [theme['modes']['dark']['bg']], 3.0)}}
    theme['defaults'] = {'mode': a.mode or got.get('mode') or base['defaults']['mode'], 'palette': 'brand'}
    for mode in ('light', 'dark'):                 # chart colours: the brand's first, then the base's that differ enough
        lead = [pal[mode]['accent']] + ([pal[mode]['accent_2']] if acc2 else [])
        for c in got.get('chart', []):             # a reference's own chart colours next
            c = c if mode == 'light' else bt.reach(c, [theme['modes']['dark']['bg']], 3.0)
            if all(bt.far_enough(c, x) for x in lead):
                lead.append(c)
        rest = [c for c in base['chart'][mode] if all(bt.far_enough(c, x) for x in lead)]
        theme['chart'][mode] = (lead + rest)[:max(6, len(base['chart'][mode]))]

    if a.credit:                                   # the base's own credit stays: its layout and artwork remain in use
        theme['credit'] = '; '.join(c for c in (a.credit, base.get('credit')) if c)

    out_dir.mkdir(exist_ok=True)
    art_css = ''
    if a.art:
        if not a.reference or Path(str(a.reference)).suffix.lower() not in PPT_EXT and not str(a.reference).lower().startswith('office:'):
            sys.exit('--art needs --reference to be a PowerPoint theme, template or file (.thmx, .potx, .pptx) or office:<name>')
        art_css, art_mode = template_art(theme, a.id, a.reference, out_dir, warn)
        if art_mode:
            if a.mode and a.mode != art_mode:
                warn.append('--art: the template\'s artwork is %s, so it shows only in %s mode; --mode %s keeps %s\'s art'
                            % (art_mode, art_mode, a.mode, base['name']))
            theme['defaults']['mode'] = a.mode or art_mode
    (out_dir / 'theme.json').write_text(json.dumps(theme, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    copy_art(base_dir, a.base, out_dir, a.id, name, base['name'])
    if art_css:
        with open(out_dir / 'theme.css', 'a', encoding='utf-8') as f:
            f.write(art_css)
    print('Wrote %s and theme.css (%s on %s; palettes %s)' % (out_dir / 'theme.json', name, base['name'], ', '.join(theme['palettes'])))
    for w in warn:
        print('  ! ' + w)
    r = subprocess.run([sys.executable, str(KIT / 'tools' / 'build_themes.py'), a.id, '--verbose'], capture_output=True, text=True)
    print('\n'.join(l for l in r.stdout.splitlines() if l.startswith((a.id, '   ')) or 'FAIL' in l))
    if r.returncode:
        print(r.stderr[-800:])
        return r.returncode
    if a.no_check:
        print('Not checked (--no-check): decks in it will not publish until python3 tools/make_theme.py --check %s passes.' % a.id)
        return 0
    return check_theme(a.id)


def copy_art(base_dir, base_id, out_dir, tid, name, base_name):
    """The base theme's theme.css and doc.css (its artwork for slides and documents), aimed at the new id."""
    head = '/* %s: a custom theme made by tools/make_theme.py from %s. Remake it rather than editing it. */\n' % (name, base_name)
    for fn in ('theme.css', 'doc.css'):
        if (base_dir / fn).is_file():
            art = (base_dir / fn).read_text(encoding='utf-8').replace('data-theme="%s"' % base_id, 'data-theme="%s"' % tid)
            (out_dir / fn).write_text(head + art, encoding='utf-8')
        elif (out_dir / fn).is_file():
            (out_dir / fn).unlink()


PPT_EXT = ('.thmx', '.pptx', '.potx', '.pptm', '.potm', '.ppsx')
ART_FORMATS = {1.7778: '16x9', 1.3333: '4x3'}
ART_KINDS = {'content': '.pc-slide:not(.pc-cover, .pc-closing, .pc-section, .pc-statement, .pc-bleed)',
             'cover': '.pc-slide:is(.pc-cover, .pc-closing)', 'section': '.pc-slide:is(.pc-section, .pc-statement)'}
ON_BASE = ':is(:not([data-surface]), [data-surface="base"])'   # alt, accent and inverse slides keep their own colours


def avg_colour(img, box=None):
    from PIL import Image, ImageStat
    im = Image.open(img).convert('RGB')
    if box:
        w, h = im.size
        im = im.crop((int(w * box[0]), int(h * box[1]), int(w * (box[0] + box[2])), int(h * (box[1] + box[3]))))
    return '#%02X%02X%02X' % tuple(int(v) for v in ImageStat.Stat(im).mean)


def ground(img, box, mode, worst=.15):
    """The ground text must read on inside a box of a layout picture: its light end in dark mode (light text), its dark
    end in light mode, so a gradient or a pattern is judged where it is hardest, not by its average."""
    from PIL import Image
    im = Image.open(img).convert('RGB')
    if box:
        w, h = im.size
        im = im.crop((int(w * box[0]), int(h * box[1]), int(w * (box[0] + box[2])), int(h * (box[1] + box[3]))))
    im.thumbnail((96, 96))
    px = sorted(im.getdata(), key=lambda c: bt.lum('#%02X%02X%02X' % c))
    return '#%02X%02X%02X' % px[int(len(px) * (1 - worst if mode == 'dark' else worst))]


def text_room(boxes, kind):
    """Padding that keeps a slide's text inside the template's own text boxes (fractions of the slide), never inside
    the kit's margins; and for a cover, the title placed high, centred or low as the template has it."""
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[0] + b[2] for b in boxes), max(b[1] + b[3] for b in boxes)
    out = []
    for side, v, var, dim in (('left', x0, '--mx', '--W'), ('right', 1 - x1, '--mx', '--W'),
                              ('top', y0, '--mt', '--H'), ('bottom', 1 - y1, '--mb', '--H')):
        if 0 < v < .35:
            out.append('padding-%s: max(var(%s), calc(var(%s) * %.4f));' % (side, var, dim, v))
    if kind == 'cover':
        mid = (y0 + y1) / 2
        out.append('justify-content: %s; --cover-w: 100%%;' % ('flex-start' if mid < .4 else 'center' if mid < .62 else 'flex-end'))
    return ' '.join(out)


def template_art(theme, tid, ref, out_dir, warn):
    """--art: a PowerPoint template's own slide artwork (tools/template_art.py draws its title, content and section
    layouts) behind the slides of its format, in its mode, in place of the base theme's art there. Slide text keeps
    to the template's text boxes. A layout whose text area is too busy or too light or dark for the theme's text is
    left out. Returns (css, the artwork's mode), or ('', None)."""
    import template_art as ta
    if str(ref).lower().startswith('office:'):
        ref = office_theme(str(ref)[7:])
    folder = out_dir / 'art'
    info = ta.render(Path(ref).expanduser(), folder)
    fmt = ART_FORMATS.get(round(info['ratio'], 4))
    if not fmt:
        warn.append('--art: the template\'s slides are %s to 1, not 16:9 or 4:3, so its artwork is left out' % info['ratio'])
        return '', None
    lay = info['layouts']
    lead = lay.get('content') or next(iter(lay.values()))
    mode = 'dark' if bt.is_dark(avg_colour(folder / lead['file'])) else 'light'
    ink = theme['modes'][mode]['ink']
    # the mode's background becomes the hardest ground under the content layout's text, so tools/build_themes.py
    # tunes the text, label and chart colours against the artwork itself, not the master's flat colour
    was = theme['modes'][mode]['bg']
    theme['modes'][mode]['bg'] = ground(folder / lead['file'], lead.get('body') or lead.get('title'), mode)
    deck = '.pc-deck[data-theme="%s"][data-mode="%s"][data-format="%s"]' % (tid, mode, fmt)
    css, used = ['\n/* The template\'s own artwork (make_theme.py --art, from %s): %s, %s mode only. */\n' % (info['source'], fmt, mode)], []
    for kind, sel in ART_KINDS.items():
        L = lay.get(kind)
        if not L:
            continue
        boxes = [L[k] for k in ('title', 'body') if L.get(k)]
        low = [(k, ground(folder / L['file'], L.get(k), mode), need) for k, need in (('title', 3.0), ('body', 4.5)) if L.get(k)] \
            or [('slide', ground(folder / L['file'], None, mode), 4.5)]
        bad = [(k, g, need) for k, g, need in low if bt.contrast(ink, g) < need]
        if bad:
            warn.append('--art: the %s layout (%s) is left out: its %s text would sit on %s, %.1f:1 against the %s text colour'
                        % (kind, L['layout'], bad[0][0], bad[0][1], bt.contrast(ink, bad[0][1]), mode))
            continue
        s = '%s %s%s' % (deck, sel, ON_BASE)
        css.append('%s { background: var(--bg) url("art/%s") center / cover no-repeat; }\n' % (s, L['file']))
        css.append('%s::before, %s::after { content: none; }\n' % (s, s))
        room = text_room(boxes, kind) if boxes else ''
        if room:
            css.append('%s:not(.pc-split) { %s }\n' % (s, room))
            # the page number moves in with the text, and to the left foot if the art fills the right one
            x0, x1 = min(b[0] for b in boxes), max(b[0] + b[2] for b in boxes)
            spots = [('right', 'right: max(var(--mx), calc(var(--W) * %.4f));' % (1 - x1), [max(.02, x1 - .012), .95, .012, .025]),
                     ('left', 'left: max(var(--mx), calc(var(--W) * %.4f)); right: auto;' % x0, [x0, .95, .012, .025])]
            for side, rule, spot in spots:
                num = theme['modes'][mode].get('ink_3') or ink   # page numbers print in --ink-3
                if bt.contrast(num, ground(folder / L['file'], spot, mode, worst=.02)) >= 4.5:   # a small mark: its worst pixel counts
                    css.append('%s:not(.pc-split) > .pc-num { %s }\n' % (s, rule))
                    break
        used.append(kind)
    if used and was != theme['modes'][mode]['bg']:
        print('Template artwork: %s background %s -> %s, the hardest ground under its text' % (mode, was, theme['modes'][mode]['bg']))
    if not used:
        theme['modes'][mode]['bg'] = was
        return '', None
    print('Template artwork (%s, %s mode): %s, in themes/%s/art/' % (fmt, mode, ', '.join(used), tid))
    return ''.join(css), mode


def merge(base, over):
    """over laid on base: nested objects merge key by key, except palettes and the art recipe, which replace."""
    out = dict(base)
    for k, v in over.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) and k not in ('palettes', 'art') else v
    return out


def read_shape(p, name):
    """A one-colour SVG (paths, circles, rects) as [view box, body] for a recipe's own shape."""
    try:
        svg = p.resolve().read_text(encoding='utf-8')
    except OSError as e:
        sys.exit('art.shapes.%s: cannot read %s: %s' % (name, p, e))
    view = re.search(r'viewBox="([^"]+)"', svg)
    if not view or re.search(r'<(mask|clipPath|use|image|text)\b', svg):
        sys.exit('art.shapes.%s: %s needs a viewBox and one-colour paths only (tools/mark.py save_shape writes one)' % (name, p))
    els = re.findall(r'<(?:path|circle|rect)\b[^>]*?/?>', svg)
    drop = r'\s(?:fill(?!="none")|style|class|id|opacity|fill-opacity)="[^"]*"'   # the recipe gives the colour
    body = ''.join(re.sub(r'\s*/?>$', '/>', re.sub(drop, '', e)) for e in els)
    if not body:
        sys.exit('art.shapes.%s: %s has no path, circle or rect' % (name, p))
    return [' '.join(view.group(1).replace(',', ' ').split()), body]


def make_spec(a):
    """A theme from a style spec (a theme.json in part, with an optional art recipe) laid over a built theme."""
    src = Path(a.spec).expanduser().resolve()
    try:
        spec = json.loads(src.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        sys.exit('Cannot read the spec %s: %s' % (src, e))
    out_dir = Path(a.out).expanduser().resolve() if a.out else None
    tid = a.id or spec.get('id') or (out_dir.name.lower() if out_dir else None)
    if not tid or not re.fullmatch(r'[a-z][a-z0-9-]{1,23}', tid):
        sys.exit('The theme id (the spec\'s "id", the id argument or the --out folder name) is lower case letters, digits and hyphens, 2 to 24 characters')
    base_id = a.base or spec.get('base') or 'meridian'
    base_dir = THEMES / base_id
    if not (base_dir / 'theme.json').is_file():
        sys.exit('No theme %r to build on. Built themes: %s' % (base_id, ', '.join(sorted(p.parent.name for p in THEMES.glob('*/theme.json')))))
    if out_dir is None:
        out_dir = THEMES / tid
        if (out_dir / 'theme.json').is_file() and not json.loads((out_dir / 'theme.json').read_text(encoding='utf-8')).get('custom'):
            sys.exit('%s is one of the kit\'s own themes: choose another id' % tid)
    elif (THEMES / tid / 'theme.json').is_file():
        sys.exit('%s is already a theme in themes/: give the style another id' % tid)
    base = json.loads((base_dir / 'theme.json').read_text(encoding='utf-8'))
    theme = merge(base, {k: v for k, v in spec.items() if k not in ('id', 'base', 'custom', 'extra', 'extra_doc')})
    theme['name'] = spec.get('name') or tid.replace('-', ' ').title()
    if 'summary' not in spec:
        theme['summary'] = '%s, on the %s layout' % (theme['name'], base['name'])
    if out_dir != THEMES / tid:
        theme['id'] = tid
    fonts = held_fonts()
    missing = sorted({f[0] for f in theme['fonts'].values() if f and f[0] not in fonts})
    if missing:
        sys.exit('The kit does not hold %s. Use held families (--fonts lists them); a new family is a download: ask the user '
                 '(name, source, size), then add it with tools/fetch_assets.py' % ', '.join(missing))
    for pid, p in theme['palettes'].items():
        for mode in ('light', 'dark'):
            for k, v in (p.get(mode) or {}).items():
                if isinstance(v, str) and v.startswith('#') and not HEX.match(v):
                    sys.exit('Palette %s, %s %s: %r is not a colour like #2F54EB' % (pid, mode, k, v))
    if theme['defaults'].get('palette') not in theme['palettes']:
        theme['defaults']['palette'] = next(iter(theme['palettes']))
    shapes = (theme.get('art') or {}).get('shapes') or {}
    for name, v in list(shapes.items()):   # drawn shapes (tools/mark.py save_shape) come in as [view box, body]
        if isinstance(v, str):
            shapes[name] = read_shape(src.parent / v, name)
    theme['custom'] = {'base': base_id, 'source': os.path.relpath(src, out_dir)}   # relative: no home folder in shared files
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'theme.json').write_text(json.dumps(theme, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    for key, fn in (('extra', 'extra.css'), ('extra_doc', 'extra-doc.css')):   # the style's own touches, next to the spec
        if spec.get(key):
            p = (src.parent / spec[key]).resolve()
            if not p.is_file():
                sys.exit('The spec\'s %s file is not there: %s' % (key, p))
            (out_dir / fn).write_text(p.read_text(encoding='utf-8'), encoding='utf-8')
        elif (out_dir / fn).is_file():
            (out_dir / fn).unlink()
    if not theme.get('art'):
        copy_art(base_dir, base_id, out_dir, tid, theme['name'], base['name'])
    print('Wrote %s (%s on %s; palettes %s%s)' % (out_dir / 'theme.json', theme['name'], base['name'], ', '.join(theme['palettes']),
                                                 '; art from its recipe' if theme.get('art') else '; art from ' + base['name']))
    args = [sys.executable, str(KIT / 'tools' / 'build_themes.py')] + (['--theme-dir', str(out_dir)] if out_dir != THEMES / tid else [tid])
    r = subprocess.run(args + ['--verbose'], capture_output=True, text=True)
    print('\n'.join(l for l in r.stdout.splitlines() if l.startswith((tid, '   ')) or 'FAIL' in l))
    if r.returncode:
        print(r.stderr[-800:])
        return r.returncode
    if a.no_check:
        print('Not checked (--no-check): decks in it will not publish until python3 tools/make_theme.py --check %s passes.'
              % (out_dir if out_dir != THEMES / tid else tid))
        return 0
    return check_theme(tid if out_dir == THEMES / tid else str(out_dir), a.formats or 'all')


def check_theme(tid, formats='all'):
    """QC the showcase deck in the theme in every format, an outline deck in it, and a PowerPoint of it; record the result."""
    import time
    outside = (Path(tid).expanduser() / 'theme.json').is_file()   # a style folder outside themes/
    if outside:
        tid = bt.add_dir(tid)
    f = bt.folder(tid) / 'theme.json'
    theme = json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}
    if not theme.get('custom'):
        sys.exit('%s is not a custom theme' % tid)
    out = bt.folder(tid) / 'check' if outside else KIT / 'selftest' / ('theme-' + tid)   # a job's style keeps its results: the kit never changes with use
    print('Checking %s: the showcase in %s formats in light and dark mode, an outline deck and a PowerPoint (a few minutes)'
          % (tid, formats), flush=True)
    r = subprocess.run([sys.executable, str(KIT / 'tools' / 'selftest.py'), '--themes', tid, '--formats', formats, '--modes', 'light,dark',
                        '-o', str(out)] + (['--theme-dir', str(bt.folder(tid))] if outside else []),
                       capture_output=True, text=True)
    print('\n'.join(l for l in r.stdout.splitlines() if l.startswith(('ok ', 'FAIL'))))
    passed = r.returncode == 0
    theme['custom']['checked'] = {'on': time.strftime('%Y-%m-%d %H:%M'), 'passed': passed, 'formats': formats,
                                  'results': 'check' if outside else str(out.relative_to(KIT))}
    f.write_text(json.dumps(theme, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    if passed:
        print('Passed. Now look at %s and the contact sheets in %s before using the theme: QC finds overflow, '
              'contrast and missing fonts, not a theme that looks wrong.' % (out / 'overview.png', out))
        return 0
    print('The check found issues: read %s and the .log file for each failed line, then remake the theme (other colours, '
          'fonts or --base) and it checks again. Decks in it will not publish until it passes.' % (out / 'summary.txt'))
    return 1


def main():
    ap = argparse.ArgumentParser(description='Make a custom theme from brand colours and fonts.')
    ap.add_argument('id', nargs='?', help='the new theme id, e.g. acme')
    ap.add_argument('--fonts', action='store_true', help='list the font families the kit holds')
    ap.add_argument('--name', help='the theme name (default: the brand title, or the id)')
    ap.add_argument('--base', help='the built theme whose layout and artwork it uses (default meridian, or folio for a serif reference)')
    ap.add_argument('--reference', help='copy the colours, fonts and mode of a PowerPoint theme or file (.thmx, .potx, .pptx), '
                                        'a PDF of a deck, a picture of a slide, or office:<name> (see --office)')
    ap.add_argument('--art', action='store_true', help='with a PowerPoint --reference: use its own slide artwork (title, '
                    'content and section layouts) in its format and mode, in place of the base theme\'s')
    ap.add_argument('--credit', help='a credit line for the theme (a template\'s licence, e.g. "Template: Name by Author, CC BY 4.0"): '
                    'kept in theme.json and a hidden comment in built files, never shown in the work')
    ap.add_argument('--no-check', action='store_true', help='skip the check after making the theme (decks in it will not publish until it passes)')
    ap.add_argument('--check', metavar='ID', help='check a custom theme again (an id, or a style folder): the showcase in every format, an outline deck, a PowerPoint')
    ap.add_argument('--spec', help='a style spec (JSON: a theme.json in part, with an art recipe) to build a theme from')
    ap.add_argument('--out', help='with --spec: the folder to write the theme to (a job\'s style folder) instead of themes/<id>')
    ap.add_argument('--formats', help='with --spec or --check: the formats to check, comma-separated (default all)')
    ap.add_argument('--office', action='store_true', help='list the Office themes PowerPoint installed on this computer')
    ap.add_argument('--tokens', help='a design-tokens JSON file (design-system format)')
    ap.add_argument('--brand', help='a brand guidelines Markdown file (brand skill format)')
    ap.add_argument('--logo', help='a logo (PNG, JPEG, WebP or SVG) to take the brand colours from')
    ap.add_argument('--accent', help='the main brand colour, #RRGGBB')
    ap.add_argument('--accent-2', dest='accent_2', help='a second brand colour')
    ap.add_argument('--display', help='font family for titles and figures')
    ap.add_argument('--body', help='font family for text')
    ap.add_argument('--mono', help='font family for code')
    ap.add_argument('--radius', help='corner radius, e.g. 8px')
    ap.add_argument('--mode', choices=('light', 'dark'), help='the default mode (default: the base theme\'s)')
    for mode in ('light', 'dark'):
        for k in ('bg', 'ink'):
            ap.add_argument('--%s-%s' % (mode, k), dest='%s_%s' % (mode, k), help='%s mode %s colour' % (mode, 'background' if k == 'bg' else 'text'))
    a = ap.parse_args()
    if a.office:
        for p in sorted(OFFICE.glob('*.thmx')):
            r = from_powerpoint(p)
            fh = {k: match_font(v)[0] for k, v in (r.get('ref_fonts') or {}).items() if v}
            print('%-22s %-5s %s %s  %s / %s' % (p.stem, r.get('mode', '?'), r.get('accent', ''), r.get('accent_2', ''),
                                                 fh.get('display', '?'), fh.get('body', '?')))
        print('Use one: python3 tools/make_theme.py <id> --reference "office:<name>"' if OFFICE.exists() else 'PowerPoint is not installed here.')
        return 0
    if a.check:
        return check_theme(a.check, a.formats or 'all')
    if a.spec:
        return make_spec(a)
    if a.fonts:
        gen = generic_of()
        for fam, info in sorted(held_fonts().items()):
            ws = sorted({f['weight'] for f in info['faces'] if f['style'] == 'normal'})
            print('%-28s %-6s %s%s' % (fam, gen.get(fam, '?'), ' '.join(map(str, ws)), ', italic' if any(f['style'] == 'italic' for f in info['faces']) else ''))
        return 0
    if not a.id:
        ap.error('give the new theme id, or --fonts')
    return make(a)


if __name__ == '__main__':
    sys.exit(main())
