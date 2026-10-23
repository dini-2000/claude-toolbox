#!/usr/bin/env python3
"""The Mangrove Return emblem and the shapes its style draws with (tools/mark.py), on a 24-unit grid.

    python3 samples/creative/art/draw.py          writes the SVGs beside this file
    python3 tools/art_loop.py samples/creative/art/seal.svg -o /tmp/loop --word "Mangrove Return" --font "Instrument Sans" --weight 600

The emblem is a sapling with three leaves on two arched roots, standing in water, knocked out of a disc. The style's
art recipe (../style.json) draws it from two one-colour shapes laid on each other: seal-disc in the accent and
seal-tree in the ground colour, so it follows the palette in light and dark.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'tools'))
from mark import Mark, Shape, band, circle, leaf, line, rect, save_shape  # noqa: E402


def tree(top=11.6, y=18.5, w=1.8, length=8.4, spread=55, bulge=.42):
    """Three leaves fanning up from (12, top), a trunk, and two roots arching into the water line at y."""
    s = Shape()
    for a in (-90 - spread, -90, -90 + spread):
        r = math.radians(a)
        s = s + leaf(12, top, 12 + length * math.cos(r), top + length * math.sin(r), bulge)
    s = s + line(12, top - .5, 12, y - 1.2, w, 'butt')         # runs into the roots' join, so no notch shows
    return s + band(9, y, 3, w, 180, 360) + band(15, y, 3, w, 180, 360)


WATER = rect(1, 18.5, 22, 1.8)   # wider than the disc: outside it, the ground colour falls on the ground

if __name__ == '__main__':
    seal = Mark(24).add(circle(12, 12, 11), 'accent').cut(tree() + WATER)
    seal.save(HERE / 'seal.svg', palette={'accent': '#2F6B4F'}, title='Mangrove Return')
    seal.save(HERE / 'seal-mono.svg', mono=True, title='Mangrove Return')
    save_shape(circle(12, 12, 11), HERE / 'seal-disc.svg')
    save_shape(tree() + WATER, HERE / 'seal-tree.svg')
    save_shape(tree(), HERE / 'sapling.svg')
    print('Wrote seal.svg, seal-mono.svg, seal-disc.svg, seal-tree.svg and sapling.svg in', HERE)
