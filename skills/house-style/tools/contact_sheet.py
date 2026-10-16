#!/usr/bin/env python3
"""Contact sheet of a printed deck: python3 tools/contact_sheet.py deck.pdf sheet.png [columns] [page width px]."""
import sys, fitz
from PIL import Image
pdf, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4; w = int(sys.argv[4]) if len(sys.argv) > 4 else 480
d = fitz.open(pdf); ims = []
for p in d:
    z = w / p.rect.width
    pix = p.get_pixmap(matrix=fitz.Matrix(z, z))
    ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
h = max(i.height for i in ims); rows = (len(ims) + cols - 1) // cols; g = 8
S = Image.new("RGB", (cols * (w + g) + g, rows * (h + g) + g), (120, 120, 120))
for k, im in enumerate(ims): S.paste(im, (g + (k % cols) * (w + g), g + (k // cols) * (h + g)))
S.save(out); print(len(ims), "pages", S.size)
