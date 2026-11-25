"""Render all exported SVGs into contact sheets for visual inspection.

Optional research/QA dependencies: cairosvg and Pillow.
"""

import io
import json
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main(**kwargs):
    manifest = json.loads((ROOT / "catalogue/microcontrollers/manifest.json").read_text(encoding="utf-8"))
    folder = ROOT / "catalogue/microcontrollers/review"
    folder.mkdir(parents=True, exist_ok=True)
    sheet = None
    for index, board in enumerate(manifest["boards"]):
        if index % 6 == 0:
            sheet = Image.new("RGB", (1800, 1800), "#e9eef0")
        image = Image.open(io.BytesIO(cairosvg.svg2png(url=str(ROOT / board["svg"]), scale=3)))
        image.thumbnail((870, 555))
        tile = Image.new("RGB", (880, 560), "white")
        if image.mode == "RGBA":
            tile.paste(image, ((880 - image.width) // 2, (560 - image.height) // 2), image)
        else:
            tile.paste(image, ((880 - image.width) // 2, (560 - image.height) // 2))
        x = index % 2 * 900 + 10
        y = index % 6 // 2 * 600 + 30
        sheet.paste(tile, (x, y))
        ImageDraw.Draw(sheet).text((x + 5, y - 20), str(index + 1) + ". " + board["name"], fill="#203b44")
        if index % 6 == 5 or index == len(manifest["boards"]) - 1:
            path = folder / ("sheet_" + str(index // 6 + 1) + ".png")
            sheet.save(path)
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
