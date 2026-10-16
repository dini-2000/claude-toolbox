#!/usr/bin/env python3
"""Add font families already on this Mac to the kit: copy their files into fonts/<Family>/ and register them in
fonts/fonts.json, the way fetch_assets.py does for Google Fonts.

The source folder holds files named <Family>-<Style>.ttf (Regular, Italic, Medium, Bold, BoldItalic and so on) and a
<Family>-OFL.txt licence per family, as in Anthropic's canvas-design skill:

    python3 tools/add_fonts.py ~/.claude/skills/canvas-design/canvas-fonts --source "Anthropic canvas-design skill"

Families the kit already holds are left alone. Only families with an OFL licence file beside them are added.
"""
import argparse
import json
import re
import shutil
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
FONTS = KIT / 'fonts'
STYLES = {'Thin': (100, 'normal'), 'ExtraLight': (200, 'normal'), 'Light': (300, 'normal'), 'Regular': (400, 'normal'),
          'Medium': (500, 'normal'), 'SemiBold': (600, 'normal'), 'Bold': (700, 'normal'), 'ExtraBold': (800, 'normal'),
          'Black': (900, 'normal'), 'Italic': (400, 'italic')}
STYLES.update({k + 'Italic': (w, 'italic') for k, (w, _) in list(STYLES.items()) if k not in ('Regular', 'Italic')})
NAMES = {'JetBrainsMono': 'JetBrains Mono'}   # names the CamelCase rule would split wrongly


def family_name(camel):
    if camel in NAMES:
        return NAMES[camel]
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', camel)
    return re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', help='folder of <Family>-<Style>.ttf files and <Family>-OFL.txt licences')
    ap.add_argument('--source', default='a local folder', help='where the files came from, recorded in fonts.json')
    ap.add_argument('--only', help='comma-separated CamelCase family names to add (default: every family found)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    src = Path(a.src).expanduser()
    manifest = json.loads((FONTS / 'fonts.json').read_text(encoding='utf-8'))
    found = {}
    for f in sorted(src.glob('*.ttf')):
        camel, _, style = f.stem.partition('-')
        if style in STYLES:
            found.setdefault(camel, []).append((f, *STYLES[style]))
    only = set(a.only.split(',')) if a.only else None
    added = []
    for camel, files in sorted(found.items()):
        fam = family_name(camel)
        lic = src / (camel + '-OFL.txt')
        if (only and camel not in only) or fam in manifest:
            continue
        if not lic.is_file() or 'Open Font License' not in lic.read_text(encoding='utf-8', errors='replace'):
            print('skipped %s: no OFL licence beside it' % fam)
            continue
        d, base = FONTS / fam, fam.replace(' ', '')
        faces = []
        for f, weight, style in files:
            name = '%s-%d%s.ttf' % (base, weight, 'i' if style == 'italic' else '')
            faces.append({'bytes': f.stat().st_size, 'file': '%s/%s' % (fam, name), 'style': style, 'weight': weight})
            if not a.dry_run:
                d.mkdir(exist_ok=True)
                shutil.copyfile(f, d / name)
        if not a.dry_run:
            shutil.copyfile(lic, d / 'OFL.txt')
        manifest[fam] = {'faces': sorted(faces, key=lambda x: (x['style'], x['weight'])), 'licence': 'SIL Open Font License 1.1',
                         'licence_file': '%s/OFL.txt' % fam, 'source': a.source}
        added.append('%s (%s)' % (fam, ', '.join('%d%s' % (x['weight'], 'i' if x['style'] == 'italic' else '') for x in manifest[fam]['faces'])))
    if added and not a.dry_run:
        (FONTS / 'fonts.json').write_text(json.dumps(dict(sorted(manifest.items())), indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%s %d families%s' % ('Would add' if a.dry_run else 'Added', len(added), ':\n  ' + '\n  '.join(added) if added else ''))


if __name__ == '__main__':
    main()
