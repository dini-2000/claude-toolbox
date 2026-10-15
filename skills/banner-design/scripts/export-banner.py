#!/usr/bin/env python3
"""
export-banner.py - export HTML banners to images at exact pixel sizes with headless Chrome

Uses an installed Chrome, Chromium or Microsoft Edge; Python 3 standard library only, nothing to install.
The browser opens each banner in a fresh temporary profile, waits for fonts and images, and captures the
top-left WIDTH x HEIGHT of the page, so build each banner at its platform size with body margin 0.

Usage:
  python3 scripts/export-banner.py banner.html --width 1500 --height 500 -o assets/banners/launch/minimalist-1500x500.png
  python3 scripts/export-banner.py assets/banners/launch/*-1500x500.html --out-dir assets/banners/launch
  python3 scripts/export-banner.py http://localhost:8765/hero.html --width 1920 --height 600 --scale 2

Options:
  --width/--height  Size in CSS pixels. Without them, the size is read from the file name ("gradient-1500x500.html").
  --scale N         Device pixel ratio: 2 doubles the pixels for sharp retina or print output (default 1).
  --format          png (default), jpeg or webp; -o with a .jpg or .webp name sets it too.
  --max-size MB     Size limit (default 5). A PNG over it is exported again as JPEG; anything still over is reported.
  --wait MS         Time the page gets to load fonts and images before capture (default 5000).
  --chrome PATH     Browser to use; the CHROME environment variable works too.

Each export prints its path, format, pixel size and file size, and the script checks the pixel size it got.
On Windows, run it with `python` or `py -3` instead of `python3`.
"""

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

EXT = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}


def find_browser(explicit=None):
    """Chrome, Chromium or Edge: --chrome, then $CHROME, then the usual install places, then PATH."""
    for c in (explicit, os.environ.get("CHROME")):
        if c:
            if Path(c).exists() or shutil.which(c):
                return shutil.which(c) or c
            sys.exit(f"Browser not found: {c}")
    places = []
    if sys.platform == "darwin":
        for app in ("Google Chrome", "Chromium", "Microsoft Edge"):
            for root in ("/Applications", str(Path.home() / "Applications")):
                places.append(f"{root}/{app}.app/Contents/MacOS/{app}")
    elif os.name == "nt":
        for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(env)
            if base:
                places += [os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                           os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe")]
    for p in places:
        if Path(p).exists():
            return p
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge", "microsoft-edge"):
        if shutil.which(name):
            return shutil.which(name)
    sys.exit("No Chrome, Chromium or Edge found. Install one, or pass its path with --chrome.")


def image_size(path):
    """(width, height) of a PNG, JPEG or WebP file, read from its header."""
    b = Path(path).read_bytes()
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            marker, length = b[i + 1], struct.unpack(">H", b[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return w, h
            i += 2 + length
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            v = int.from_bytes(b[21:25], "little")
            return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    return None


def to_url(src):
    if re.match(r"^[a-z]+://", src, re.I):
        return src
    p = Path(src).resolve()
    if not p.exists():
        sys.exit(f"Not found: {src}")
    return p.as_uri()


def capture(browser, url, out, width, height, scale, wait):
    """One headless screenshot; the format follows the output's extension."""
    profile = tempfile.mkdtemp(prefix="export-banner-")
    cmd = [browser, "--headless", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
           "--disable-extensions", f"--user-data-dir={profile}", f"--window-size={width},{height}",
           f"--force-device-scale-factor={scale}", f"--virtual-time-budget={wait}",
           f"--screenshot={Path(out).resolve()}", url]
    try:
        if Path(out).exists():
            Path(out).unlink()
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=wait / 1000 + 90)
    except subprocess.TimeoutExpired:
        return "the browser did not finish in time"
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not Path(out).exists():
        return "the browser wrote no file"
    return None


def main():
    ap = argparse.ArgumentParser(description="Export HTML banners to PNG, JPEG or WebP at exact pixel sizes with headless Chrome.")
    ap.add_argument("inputs", nargs="+", help="HTML files or URLs")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("-o", "--output", help="output file (one input only)")
    ap.add_argument("--out-dir", help="folder for the exports (default: beside each HTML file, or the working folder for URLs)")
    ap.add_argument("--scale", type=float, default=1)
    ap.add_argument("--format", choices=sorted(EXT))
    ap.add_argument("--max-size", type=float, default=5, help="MB")
    ap.add_argument("--wait", type=int, default=5000, help="milliseconds")
    ap.add_argument("--chrome")
    a = ap.parse_args()
    if a.output and len(a.inputs) > 1:
        ap.error("-o takes one input; use --out-dir for several")
    if (a.width is None) != (a.height is None):
        ap.error("give both --width and --height, or neither")
    browser = find_browser(a.chrome)
    failed = 0

    for src in a.inputs:
        name = Path(re.sub(r"[?#].*$", "", src)).name or "banner"
        if a.width:
            width, height = a.width, a.height
        else:
            m = re.search(r"(\d{2,5})x(\d{2,5})", name)
            if not m:
                print(f"SKIPPED {src}: no size in the name; pass --width and --height")
                failed += 1
                continue
            width, height = int(m.group(1)), int(m.group(2))
        fmt = a.format
        if a.output:
            out = Path(a.output)
            named = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}.get(out.suffix.lower())
            fmt = fmt or named or "png"
            if named != fmt:  # the browser picks the format from the extension
                out = out.with_suffix(EXT[fmt])
        else:
            fmt = fmt or "png"
            stem = Path(name).stem
            if not re.search(r"\d+x\d+", stem):
                stem = f"{stem}-{width}x{height}"
            folder = Path(a.out_dir) if a.out_dir else (Path(src).resolve().parent if not re.match(r"^[a-z]+://", src, re.I) else Path.cwd())
            out = folder / (stem + EXT[fmt])
        out.parent.mkdir(parents=True, exist_ok=True)

        url = to_url(src)
        err = capture(browser, url, out, width, height, a.scale, a.wait)
        if not err and fmt == "png" and out.stat().st_size > a.max_size * 1024 * 1024:
            jpg = out.with_suffix(".jpg")
            print(f"{out}: {out.stat().st_size / 1048576:.1f} MB is over {a.max_size:g} MB; exporting {jpg.name} instead")
            err = capture(browser, url, jpg, width, height, a.scale, a.wait)
            if not err:
                out.unlink()
                out, fmt = jpg, "jpeg"
        if err:
            print(f"FAILED {src}: {err}")
            failed += 1
            continue

        want = (round(width * a.scale), round(height * a.scale))
        got = image_size(out)
        mb = out.stat().st_size / 1048576
        note = "" if got == want else f"  WRONG SIZE: expected {want[0]}x{want[1]}"
        if mb > a.max_size:
            note += f"  OVER {a.max_size:g} MB: lower --scale or simplify the background image"
        print(f"{out}  {fmt}  {got[0] if got else '?'}x{got[1] if got else '?'}  {mb * 1024:.0f} KB{note}")
        failed += bool(note)

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
