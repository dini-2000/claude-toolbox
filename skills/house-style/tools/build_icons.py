#!/usr/bin/env python3
"""Turn the Lucide sprite (icons/lucide-sprite.svg) into icons/lucide.js, which sets window.PC_ICONS to
{name: inner SVG markup}. Decks in this folder load the full set while they are being written; tools/build.py
embeds only the icons a deck uses (icon_script(names)).

    python3 tools/build_icons.py            # rebuild icons/lucide.js
    python3 tools/build_icons.py --list     # print every icon name
"""
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
SPRITE = KIT / "icons" / "lucide-sprite.svg"
OUT = KIT / "icons" / "lucide.js"
SYMBOL = re.compile(r'<symbol id="([^"]+)"[^>]*>(.*?)</symbol>', re.S)


def load_icons():
    """{name: inner markup} with whitespace between tags squeezed out."""
    text = SPRITE.read_text(encoding="utf-8")
    icons = {}
    for name, body in SYMBOL.findall(text):
        icons[name] = re.sub(r">\s+<", "><", body.strip()).replace(" />", "/>")
    return icons


def version():
    v = KIT / "icons" / "lucide-version.txt"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "unknown"


def icon_script(names=None):
    """The JS that sets window.PC_ICONS; with names, only those icons (unknown names are skipped)."""
    icons = load_icons()
    if names is not None:
        icons = {n: icons[n] for n in sorted(set(names)) if n in icons}
    body = json.dumps(icons, separators=(",", ":"), ensure_ascii=False)
    return ("/* Lucide " + version() + " (ISC licence, icons/LICENSE-lucide.txt) */\n"
            "window.PC_ICONS=Object.assign(window.PC_ICONS||{}," + body + ");\n")


def main():
    if "--list" in sys.argv:
        print("\n".join(sorted(load_icons())))
        return
    OUT.write_text(icon_script(), encoding="utf-8")
    print(f"{OUT.relative_to(KIT)}: {len(load_icons())} icons, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
