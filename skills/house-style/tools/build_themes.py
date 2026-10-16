#!/usr/bin/env python3
"""Turn each theme's theme.json into themes/<id>/tokens.css, check its colours, and index the themes.

    python3 tools/build_themes.py              every theme, then themes/themes.json
    python3 tools/build_themes.py chalk pop    only these themes (the index is still rewritten)
    python3 tools/build_themes.py --audit      also print the contrast of every pair for every theme, palette,
                                               mode and surface
    python3 tools/build_themes.py --verbose    also list each colour the contrast rules moved
    python3 tools/build_themes.py --theme-dir DIR   a theme kept outside themes/ (a job's style folder); the index
                                               lists only the kit's own themes

Tools find a theme in themes/<id>, or in a folder named in PC_THEME_DIRS (folders separated by ":"), which
build.py --theme-dir, selftest.py --theme-dir and make_theme.py --spec --out set for themselves and the tools they run.

theme.json holds a theme's fonts, its type and shape tokens, the neutrals of each mode (light and dark) and the
accent of each palette in each mode. A palette may also set its own neutrals for a mode ("neutrals": {"bg": ...}),
which replace the mode's. tokens.css spells every colour out for every mode, palette and surface, so
the contrast audit sees real values and the CSS never remaps a colour with var() (a remap inside one rule makes a
var() cycle). Surfaces: base (the deck's mode), alt (its second background), accent (the accent as background) and
inverse (the other mode, also used by .pc-inverse panels).

Colour rules: --accent fills shapes; --accent-text is the accent for text and icons, moved darker (or lighter on a
dark background) along OKLCH lightness until it reaches 4.5:1 on every background it can sit on; --accent-ink is
text on an accent fill. Body ink aims at 7:1; ink-2, ink-3, status colours and accent text need 4.5:1; chart
colours and the second accent need 3:1. Anything moved is reported, and a pair that still fails stops the build.
Themes never set format tokens (--W, --H, --m*, --gap, --fs-*): those belong to engine/core.css.

Other tools import theme_css(theme, modes=..., palettes=...) to write a deck's tokens for one palette and mode.
"""
import json
import math
import os
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
THEMES = KIT / 'themes'
FONTS = KIT / 'fonts'
MODES = ('light', 'dark')
WHITE, BLACK = '#ffffff', '#000000'

GENERIC = {
    'sans': ['"Noto Sans Sinhala"', '"Noto Sans Tamil"', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
    'serif': ['"Noto Serif Sinhala"', '"Noto Serif Tamil"', 'Georgia', '"Times New Roman"', 'serif'],
    'mono': ['"Noto Sans Sinhala"', '"Noto Sans Tamil"', 'ui-monospace', 'Menlo', 'Consolas', 'monospace'],
    'hand': ['"Noto Sans Sinhala"', '"Noto Sans Tamil"', '"Comic Sans MS"', 'cursive'],
    'script': ['"Noto Serif Sinhala"', '"Noto Serif Tamil"', 'cursive'],
}
NOTO = {'sans': ['Noto Sans Sinhala', 'Noto Sans Tamil'], 'mono': ['Noto Sans Sinhala', 'Noto Sans Tamil'],
        'hand': ['Noto Sans Sinhala', 'Noto Sans Tamil'], 'serif': ['Noto Serif Sinhala', 'Noto Serif Tamil'],
        'script': ['Noto Serif Sinhala', 'Noto Serif Tamil']}
ROLES = ('display', 'body', 'label', 'mono', 'hand', 'script', 'stat', 'quote')
# The Noto fallbacks only ever draw their own script, so the browser fetches them only for Sinhala or Tamil text
RANGES = {'Sinhala': 'U+0D80-0DFF, U+111E0-111FF, U+200C-200D, U+25CC',
          'Tamil': 'U+0B80-0BFF, U+11FC0-11FFF, U+200C-200D, U+25CC'}
FORMAT_TOKEN = re.compile(r'^--(W|H|mx|mt|mb|gap|fs-[\w-]+)$')


# ---------------------------------------------------------------- colour maths (sRGB, WCAG contrast, OKLab/OKLCH)
def rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hexa(c):
    return '#%02x%02x%02x' % tuple(round(min(1, max(0, v)) * 255) for v in c)


def _lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _delin(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def lum(h):
    r, g, b = (_lin(v) for v in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _cbrt(x):
    return math.copysign(abs(x) ** (1 / 3), x)


def oklab(h):
    r, g, b = (_lin(v) for v in rgb(h))
    l_ = _cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m_ = _cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s_ = _cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def _from_oklab(L, a, b):
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, \
        L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def from_oklch(L, C, H):
    """OKLCH to hex, cutting chroma (never lightness or hue) until the colour fits in sRGB."""
    def fits(c):
        lin = _from_oklab(L, c * math.cos(H), c * math.sin(H))
        return all(-1e-4 <= v <= 1 + 1e-4 for v in lin), lin
    ok, lin = fits(C)
    if not ok:
        lo, hi = 0.0, C
        for _ in range(30):
            mid = (lo + hi) / 2
            if fits(mid)[0]:
                lo = mid
            else:
                hi = mid
        lin = fits(lo)[1]
    return hexa(tuple(_delin(min(1, max(0, v))) for v in lin))


def oklch(h):
    L, a, b = oklab(h)
    return L, math.hypot(a, b), math.atan2(b, a)


def mix(a, b, t):
    """t of b into a, in OKLab (smooth, keeps lightness steps even)."""
    A, B = oklab(a), oklab(b)
    lin = _from_oklab(*(x + (y - x) * t for x, y in zip(A, B)))
    return hexa(tuple(_delin(min(1, max(0, v))) for v in lin))


def mix_srgb(a, b, t):
    """As CSS color-mix(in srgb, b t, a): used to check colours the stylesheet mixes itself."""
    return hexa(tuple(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))


def is_dark(h):
    return lum(h) < 0.18


def reach(color, bgs, target):
    """The colour, moved along OKLCH lightness as little as possible, at target:1 or more on every background."""
    bgs = [bgs] if isinstance(bgs, str) else list(bgs)
    if min(contrast(color, b) for b in bgs) >= target:
        return color
    L, C, H = oklch(color)
    darker = not is_dark(bgs[0])
    end = 0.0 if darker else 1.0
    if min(contrast(from_oklch(end, C, H), b) for b in bgs) < target:
        return from_oklch(end, C, H)
    lo, hi = L, end                    # lo fails, hi passes
    for _ in range(40):
        mid = (lo + hi) / 2
        if min(contrast(from_oklch(mid, C, H), b) for b in bgs) >= target:
            hi = mid
        else:
            lo = mid
    return from_oklch(hi, C, H)


def ink_on(fill, dark_ink):
    """Text colour for a fill: white when it reaches 4.5:1, else the theme's darkest ink, else the better of the two."""
    if contrast(WHITE, fill) >= 4.5:
        return WHITE
    if contrast(dark_ink, fill) >= 4.5:
        return dark_ink
    return WHITE if contrast(WHITE, fill) >= contrast(dark_ink, fill) else dark_ink


def far_enough(a, b, d=0.07):
    A, B = oklab(a), oklab(b)
    return math.dist(A, B) > d


# ---------------------------------------------------------------- surfaces
class Notes:
    def __init__(self):
        self.moved, self.fails = [], []


def fill_placeholders(value, tok):
    return re.sub(r'\{([\w-]+)\}', lambda m: tok['--' + m.group(1).replace('_', '-')], value)


def surface(theme, mode, pal, kind, notes, where):
    """Every colour token for one surface of one palette in one mode."""
    if kind == 'inverse':
        return surface(theme, 'dark' if mode == 'light' else 'light', pal, 'base', notes, where)
    N = dict(theme['modes'][mode])
    P = theme['palettes'][pal][mode]
    # A palette may bring its own neutrals for a mode (a background and the inks on it), as Occasion's do
    for k, v in P.get('neutrals', {}).items():
        N[k] = dict(N.get(k, {}), **v) if isinstance(v, dict) else v
    dark_ink = theme['modes']['light']['ink']
    light = not is_dark(N['bg'])
    t = {}

    def moved(name, before, after, bg):
        if before.lower() != after.lower():
            notes.moved.append('%s %s: %s -> %s (%.2f:1 on %s)' % (where, name, before, after, contrast(after, bg), bg))
        return after

    accent = P['accent']
    a_ink = P.get('accent_ink') or ink_on(accent, dark_ink)
    if contrast(a_ink, accent) < 4.5:            # neither ink reads on this fill: move the fill itself
        target_fill = reach(accent, a_ink, 4.6)   # a little over 4.5: a fill tuned to exactly 4.5 prints at 4.4
        accent = moved('--accent (fill)', accent, target_fill, a_ink)

    if kind == 'accent':
        bg = accent
        fg = a_ink
        def toward(tmax, need):
            best = 0.0
            for i in range(1, 41):
                k = tmax * i / 40
                if contrast(mix(fg, bg, k), bg) >= need:
                    best = k
            return mix(fg, bg, best)
        t.update({'--bg': bg, '--bg-alt': mix(bg, fg, .07), '--surface': mix(bg, fg, .10), '--surface-2': mix(bg, fg, .16),
                  '--ink': fg, '--ink-2': toward(.28, 4.6), '--ink-3': toward(.42, 4.6), '--line': mix(bg, fg, .32),
                  '--accent': fg, '--accent-text': fg, '--accent-ink': bg, '--accent-2': toward(.35, 3.0),
                  '--accent-soft': mix(bg, fg, .16), '--positive': fg, '--negative': fg, '--warning': fg, '--info': fg})
        tmax = 0.0
        for i in range(1, 61):
            k = .6 * i / 60
            if contrast(mix(fg, bg, k), bg) >= 3.0:
                tmax = k
        for i in range(6):
            t['--c%d' % (i + 1)] = mix(fg, bg, tmax * i / 5)
        t['--code-bg'], t['--code-ink'] = N['code_bg'], N['code_ink']
        t['--shadow'] = 'none'
    else:
        if kind == 'alt':
            alt = N.get('alt', {})
            N['bg'], N['bg_alt'] = alt.get('bg', N['bg_alt']), alt.get('bg_alt', N['bg'])
            N['surface'] = alt.get('surface', N['surface'])
            N['surface_2'] = alt.get('surface_2', mix(N['bg'], N['ink'], .06))
        bg, s1, s2 = N['bg'], N['surface'], N['surface_2']
        backs = [bg, s1, s2]
        t['--bg'], t['--bg-alt'], t['--surface'], t['--surface-2'] = bg, N['bg_alt'], s1, s2
        t['--ink'] = moved('--ink', N['ink'], reach(N['ink'], backs, 4.5), bg)
        if min(contrast(t['--ink'], b) for b in backs) < 7:
            notes.moved.append('%s --ink: %.2f:1, under the 7:1 aim' % (where, min(contrast(t['--ink'], b) for b in backs)))
        # soft is a mix ratio, or a colour where the mix turns grey (gold into navy, say)
        soft = P.get('soft', .12 if light else .2)
        soft = soft if isinstance(soft, str) else mix(bg, accent, soft)
        # muted text also sits on soft panels (the after panel, highlighted rows); 4.6 leaves room for print rounding
        t['--ink-2'] = moved('--ink-2', N['ink_2'], reach(N['ink_2'], backs + [soft], 4.6), bg)
        t['--ink-3'] = moved('--ink-3', N['ink_3'], reach(N['ink_3'], backs + [soft], 4.6), bg)
        t['--line'] = N['line']
        t['--accent'] = accent
        t['--accent-ink'] = a_ink
        t['--accent-text'] = moved('--accent-text', P.get('accent_text', accent), reach(P.get('accent_text', accent), backs + [soft], 4.6), bg)
        t['--accent-2'] = moved('--accent-2', P.get('accent_2', accent), reach(P.get('accent_2', accent), [bg, s1], 3.0), bg)
        t['--accent-soft'] = soft
        for k in ('positive', 'negative', 'warning'):
            chip = mix_srgb(bg, N[k], .16 if k != 'warning' else .18)
            t['--' + k] = moved('--' + k, N[k], reach(N[k], backs + [chip, soft], 4.5), bg)   # soft: highlighted table rows
        t['--info'] = t['--accent-text']
        series = [accent] + [c for c in (P.get('chart') or theme['chart'][mode]) if far_enough(c, accent)]
        while len(series) < 6:
            series.append(series[len(series) % max(1, len(series))])
        for i, c in enumerate(series[:6]):
            t['--c%d' % (i + 1)] = moved('--c%d' % (i + 1), c, reach(c, [bg, s1], 3.0), bg)
        # Waterfall totals take the accent unless it sits near the gain or loss colour, where a total would read as
        # a gain or a loss; then they take the ink
        def near(a, b):
            (_, ca, ha), (_, cb, hb) = oklch(a), oklch(b)
            return ca > .06 and cb > .06 and abs((math.degrees(ha - hb) + 180) % 360 - 180) < 35
        t['--chart-total'] = t['--ink'] if near(t['--c1'], t['--negative']) or near(t['--c1'], t['--positive']) else t['--c1']
        t['--code-bg'], t['--code-ink'] = N['code_bg'], N['code_ink']
        t['--shadow'] = N.get('shadow', 'none')
    # Code colours keep 4.5:1 on the code panel, whatever its colour
    for k, d in (('k', '#ff8f6b'), ('s', '#9ad48b'), ('c', '#7c8592')):
        t['--code-' + k] = moved('--code-' + k, N.get('code_' + k, d), reach(N.get('code_' + k, d), t['--code-bg'], 4.5), t['--code-bg'])
    t['--mark'] = t['--accent']
    for k, v in N.get('extra', {}).items():
        t[k] = v
    for k, v in P.get('extra', {}).items():
        t[k] = v
    for k in list(t):
        if isinstance(t[k], str) and '{' in t[k]:
            t[k] = fill_placeholders(t[k], t)
    check(t, kind, notes, where)
    return t


def check(t, kind, notes, where):
    pairs = [('--ink', '--bg', 4.5), ('--ink-2', '--bg', 4.5), ('--ink-3', '--bg', 4.5 if kind != 'accent' else 4.5),
             ('--accent-text', '--bg', 4.5), ('--accent-ink', '--accent', 4.5), ('--c1', '--bg', 3.0)]
    if kind != 'accent':
        pairs += [('--ink-2', '--surface-2', 4.5), ('--accent-text', '--accent-soft', 4.5),
                  ('--positive', '--bg', 4.5), ('--negative', '--bg', 4.5), ('--warning', '--bg', 4.5),
                  ('--positive', '--accent-soft', 4.5), ('--negative', '--accent-soft', 4.5)]
    pairs += [('--code-' + k, '--code-bg', 4.5) for k in 'ksc'] + [('--code-ink', '--code-bg', 4.5)]
    pairs += [('--c%d' % i, '--bg', 3.0) for i in range(2, 7)]
    for fg, bg, need in pairs:
        r = contrast(t[fg], t[bg])
        if r < need - 1e-6:
            notes.fails.append('%s %s on %s: %.2f:1, needs %.1f:1' % (where, fg, bg, r, need))


def audit_rows(t, kind):
    rows = [('ink', t['--ink'], t['--bg']), ('ink-2', t['--ink-2'], t['--bg']), ('ink-3', t['--ink-3'], t['--bg']),
            ('accent-text', t['--accent-text'], t['--bg']), ('accent-ink on accent', t['--accent-ink'], t['--accent'])]
    rows += [('c%d' % i, t['--c%d' % i], t['--bg']) for i in range(1, 7)]
    return [(n, round(contrast(a, b), 2)) for n, a, b in rows]


# ---------------------------------------------------------------- CSS
def stack(theme, role):
    spec = theme['fonts'].get(role)
    if not spec:
        return None
    family, kind = spec
    return ', '.join(['"%s"' % family] + GENERIC[kind])


def families(theme):
    """Every family the theme's stacks name, with the Noto fallbacks its font kinds need, in a stable order."""
    out = []
    for role in ROLES:
        spec = theme['fonts'].get(role)
        if spec:
            for f in [spec[0]] + NOTO[spec[1]]:
                if f not in out:
                    out.append(f)
    return out


def font_faces(theme, manifest, base='../../fonts/'):
    rules = []
    for fam in families(theme):
        if fam not in manifest:
            sys.exit('%s: font family %r is not in fonts/fonts.json' % (theme['id'], fam))
        for face in manifest[fam]['faces']:
            url = base + '/'.join(p.replace(' ', '%20') for p in face['file'].split('/'))
            rng = next((r for k, r in RANGES.items() if fam.startswith('Noto') and fam.endswith(k)), None)
            rules.append('@font-face { font-family: "%s"; font-style: %s; font-weight: %d; font-display: block; '
                         'src: url("%s") format("truetype");%s }' % (fam, face['style'], face['weight'], url,
                                                                      ' unicode-range: %s;' % rng if rng else ''))
    return rules


def weight_fails(theme, manifest):
    """Weights the tokens ask of a role's family that the kit holds no face for (Chrome would fake or swap them)."""
    roles = {'display': ('--w-display', '--w-h1', '--w-h2'), 'body': ('--w-body', '--w-strong'), 'label': ('--w-label',),
             'stat': ('--w-stat',)}
    out, tk = [], theme.get('tokens', {})
    for role, keys in roles.items():
        fam = (theme['fonts'].get(role) or [None])[0]
        have = {f['weight'] for f in manifest.get(fam, {}).get('faces', []) if f['style'] == 'normal'}
        out += ['%s %s asks %s of %s, which has %s' % (theme['id'], k, tk[k], fam, sorted(have))
                for k in keys if have and k in tk and int(tk[k]) not in have]
    return out


def italic_warns(theme, manifest):
    """A body face with no italic: documents set font-synthesis none, so emphasis there prints upright."""
    fam = (theme['fonts'].get('body') or [None])[0]
    faces = manifest.get(fam, {}).get('faces', [])
    return ['%s body font %s has no italic, so emphasis in documents prints upright' % (theme['id'], fam)] \
        if faces and not any(f['style'] == 'italic' for f in faces) else []


def write_art(theme, folder):
    """theme.css and doc.css from the theme's art recipe (tools/motifs.py), each followed by the theme's own
    extra.css or extra-doc.css; a theme without a recipe keeps its hand-written files."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import motifs
    deck, doc = motifs.recipe_css(theme)
    for name, css, extra in (('theme.css', deck, 'extra.css'), ('doc.css', doc, 'extra-doc.css')):
        if (folder / extra).is_file():
            css += '\n/* %s */\n' % extra + (folder / extra).read_text(encoding='utf-8')
        (folder / name).write_text(css, encoding='utf-8')
    print('   art: theme.css and doc.css from the recipe (%s)' % ', '.join(motifs.used(theme['art'])))


def write_clips(tid, folder):
    """The clip-path block at the end of theme.css (tools/motifs.py clips_css), rewritten from the theme's pictures."""
    f = folder / 'theme.css'
    if not f.is_file():
        return
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import motifs
    text = f.read_text(encoding='utf-8')
    base = text.split(motifs.CLIPS_START)[0].rstrip('\n') + '\n'
    doc = (folder / 'doc.css').read_text(encoding='utf-8') if (folder / 'doc.css').is_file() else ''
    block = motifs.clips_css(tid, base, doc)
    if base + ('\n' + block if block else '') != text:
        f.write_text(base + ('\n' + block if block else ''), encoding='utf-8')
    if block:
        print('   clips: %s' % ', '.join(re.findall(r'--([a-z0-9.-]+)-clip:', block)))


def sel(theme, mode=None, pal=None):
    s = '.pc-deck[data-theme="%s"]' % theme['id']
    if mode:
        s += ':is([data-mode="%s"], :not([data-mode]))' % mode if mode == theme['defaults']['mode'] else '[data-mode="%s"]' % mode
    if pal:
        s += ':is([data-palette="%s"], :not([data-palette]))' % pal if pal == theme['defaults']['palette'] else '[data-palette="%s"]' % pal
    return s


def block(selector, tokens, scheme=None):
    body = ''.join('\n  %s: %s;' % (k, v) for k, v in tokens.items())
    return '%s {%s%s\n}' % (selector, '\n  color-scheme: %s;' % scheme if scheme else '', body)


def theme_css(theme, manifest, modes=MODES, palettes=None, notes=None, font_base='../../fonts/'):
    notes = notes or Notes()
    palettes = palettes or list(theme['palettes'])
    out = ['/* %s theme tokens. Generated by tools/build_themes.py from themes/%s/theme.json: edit that, then rebuild. */'
           % (theme['name'], theme['id'])]
    out += font_faces(theme, manifest, font_base)
    fixed = {}
    for role in ROLES:
        st = stack(theme, role)
        if st:
            fixed['--font-' + role] = st
    for k, v in theme.get('tokens', {}).items():
        if FORMAT_TOKEN.match(k):
            sys.exit('%s: theme.json sets the format token %s, which belongs to engine/core.css' % (theme['id'], k))
        fixed[k] = v
    out.append(block(sel(theme), fixed))
    for mode in modes:
        for pal in palettes:
            where = '%s/%s/%s' % (theme['id'], pal, mode)
            d = sel(theme, mode, pal)
            base = surface(theme, mode, pal, 'base', notes, where + '/base')
            inv = surface(theme, mode, pal, 'inverse', notes, where + '/inverse')
            other = 'dark' if mode == 'light' else 'light'
            deck = dict(base)
            deck['--letterbox'] = theme['palettes'][pal][mode].get('neutrals', {}).get('letterbox') or theme['modes'][mode].get('letterbox', '#0b0c0f')
            out.append('/* %s, %s */' % (theme['palettes'][pal]['name'], mode))
            out.append(block(d, deck, mode))
            out.append(block('%s .pc-slide[data-surface="alt"]' % d, surface(theme, mode, pal, 'alt', notes, where + '/alt')))
            out.append(block('%s .pc-slide[data-surface="accent"]' % d, surface(theme, mode, pal, 'accent', notes, where + '/accent')))
            out.append(block('%s :is(.pc-slide[data-surface="inverse"], .pc-inverse)' % d, inv, other))
            out.append(block('%s :is(.pc-slide[data-surface="inverse"], .pc-inverse) .pc-inverse' % d, base, mode))
    return '\n'.join(out) + '\n', notes


def summary(theme):
    pals = []
    for pid, p in theme['palettes'].items():
        entry = {'id': pid, 'name': p['name']}
        for mode in MODES:
            t = surface(theme, mode, pid, 'base', Notes(), '')
            entry[mode] = {k.strip('-'): t[k] for k in ('--bg', '--surface', '--ink', '--ink-2', '--accent', '--accent-ink',
                                                         '--accent-text', '--accent-2', '--c1', '--c2', '--c3', '--c4')}
        pals.append(entry)
    return {'id': theme['id'], 'name': theme['name'], 'summary': theme['summary'], 'good_for': theme['good_for'],
            **({'category': theme['category']} if theme.get('category') else {}),
            **({'also': theme['also']} if theme.get('also') else {}),
            **({'credit': theme['credit']} if theme.get('credit') else {}),
            'defaults': theme['defaults'], 'palettes': pals,
            'fonts': {r: theme['fonts'][r][0] for r in ('display', 'body') if theme['fonts'].get(r)},
            **({'custom': theme['custom'].get('base')} if theme.get('custom') else {})}


def outside():
    """Themes kept outside themes/: {id: folder} for each folder in PC_THEME_DIRS that holds a theme.json."""
    found = {}
    for d in filter(None, os.environ.get('PC_THEME_DIRS', '').split(os.pathsep)):
        p = Path(d).expanduser().resolve()
        if (p / 'theme.json').is_file():
            found.setdefault(json.loads((p / 'theme.json').read_text(encoding='utf-8')).get('id') or p.name, p)
    return found


def add_dir(d):
    """Put a theme folder on PC_THEME_DIRS for this process and the tools it runs; returns the theme's id."""
    p = Path(d).expanduser().resolve()
    if not (p / 'theme.json').is_file():
        sys.exit('%s has no theme.json' % p)
    os.environ['PC_THEME_DIRS'] = os.pathsep.join([str(p)] + [x for x in os.environ.get('PC_THEME_DIRS', '').split(os.pathsep) if x])
    return json.loads((p / 'theme.json').read_text(encoding='utf-8')).get('id') or p.name


def folder(tid):
    """Where a theme's files live: a folder from PC_THEME_DIRS, else themes/<id>."""
    return outside().get(tid) or THEMES / tid


def theme_ids():
    """Every theme a build can use: the kit's own and those outside it."""
    return sorted({p.parent.name for p in THEMES.glob('*/theme.json')} | set(outside()))


def load(tid):
    theme = json.loads((folder(tid) / 'theme.json').read_text(encoding='utf-8'))
    theme['id'] = tid
    return theme


def main():
    argv = sys.argv[1:]
    while '--theme-dir' in argv:
        i = argv.index('--theme-dir')
        if i + 1 >= len(argv):
            sys.exit('--theme-dir needs a folder')
        argv[i:i + 2] = [add_dir(argv[i + 1])]
    args = [a for a in argv if not a.startswith('--')]
    audit = '--audit' in sys.argv
    verbose = '--verbose' in sys.argv
    manifest = json.loads((FONTS / 'fonts.json').read_text(encoding='utf-8'))
    all_ids = sorted(p.parent.name for p in THEMES.glob('*/theme.json'))
    todo = args or all_ids
    failed = False
    for tid in todo:
        theme, d = load(tid), folder(tid)
        if not (d / 'theme.json').is_file():
            sys.exit('No theme %r. Themes: %s' % (tid, ', '.join(theme_ids())))
        css, notes = theme_css(theme, manifest, font_base=Path(os.path.relpath(FONTS, d)).as_posix() + '/')
        (d / 'tokens.css').write_text(css, encoding='utf-8')
        print('%s: tokens.css %.0f KB, %d palettes, %d colours moved for contrast' %
              (tid, len(css) / 1024, len(theme['palettes']), len(notes.moved)))
        if theme.get('art'):
            write_art(theme, d)
        write_clips(tid, d)
        for m in notes.moved if verbose else []:
            print('   moved', m)
        for f in notes.fails + weight_fails(theme, manifest):
            print('   FAIL', f)
            failed = True
        for w in italic_warns(theme, manifest):
            print('   warn', w)
        if audit:
            for mode in MODES:
                for pal in theme['palettes']:
                    for kind in ('base', 'alt', 'accent', 'inverse'):
                        rows = audit_rows(surface(theme, mode, pal, kind, Notes(), ''), kind)
                        print('   %-8s %-6s %-8s ' % (pal, mode, kind) + '  '.join('%s %.1f' % r for r in rows))
    index = {'themes': [summary(load(t)) for t in all_ids]}
    (THEMES / 'themes.json').write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding='utf-8')
    print('themes.json: %d themes' % len(all_ids))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
