"""Affianca top e bottom del placement in un PNG (alternativa a rsvg-convert + ImageMagick): python3 png_placement.py top.pdf bot.pdf out.png"""
import os
import subprocess
import sys
import tempfile
from PIL import Image, ImageChops

tiles = []
with tempfile.TemporaryDirectory() as d:
    for i, pdf in enumerate(sys.argv[1:3]):
        base = os.path.join(d, f"p{i}")
        subprocess.run(["pdftoppm", "-r", "400", "-png", "-singlefile", pdf, base], check=True)
        im = Image.open(base + ".png").convert("RGB")
        bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        im = im.crop(bbox)
        im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
        tiles.append(im)
b = 20
h = max(t.height for t in tiles)
out = Image.new("RGB", (sum(t.width for t in tiles) + b * 2 * len(tiles), h + 2 * b), "white")
x = b
for t in tiles:
    out.paste(t, (x, b))
    x += t.width + 2 * b
out.save(sys.argv[3])
print("png:", out.size)
