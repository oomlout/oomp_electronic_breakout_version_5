"""Capture manufacturer pin tables and document links for the catalogue audit.

This is a research aid, not a runtime dependency of the populate files.
"""

import concurrent.futures
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def collect(**kwargs):
    key = kwargs["key"]
    url = kwargs["url"]
    response = requests.get(url, timeout=45)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html5lib")
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = []
            for cell in row.find_all(["td", "th"], recursive=False):
                cells.append(cell.get_text(" ", strip=True))
            rows.append(cells)
        tables.append(rows)
    links = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(url, anchor["href"])
        label = anchor.get_text(" ", strip=True)
        if any(token in (href + " " + label).lower() for token in (".pdf", ".dxf", ".zip", "github.com", "dimension", "schematic")):
            links.append({"title": label, "url": href})
    item = {
        "url": response.url,
        "accessed": "2026-10-22",
        "tables": tables,
        "links": links,
    }
    folder = ROOT / "research" / "microcontrollers"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (key + ".json")).write_text(json.dumps(item, indent=4) + "\n", encoding="utf-8")
    return key, len(tables), len(links)


def main(**kwargs):
    pages = {}
    for family, name in (("esp32", "esp32-devkitc"), ("esp32", "esp32-pico-kit"), ("esp32c3", "esp32-c3-devkitc-02"), ("esp32c3", "esp32-c3-devkitm-1"), ("esp32s3", "esp32-s3-devkitc-1"), ("esp32s2", "esp32-s2-devkitc-1"), ("esp32c6", "esp32-c6-devkitc-1"), ("esp32c6", "esp32-c6-devkitm-1")):
        guide = "user_guide_v1.1.html" if family == "esp32s3" else "user_guide.html"
        pages[name] = f"https://docs.espressif.com/projects/esp-dev-kits/en/latest/{family}/{name}/{guide}"
    for family, name in (("c3", "c3_mini"), ("s2", "s2_mini"), ("s3", "s3_mini"), ("d32", "d32"), ("d32", "d32_pro")):
        pages[name] = f"https://www.wemos.cc/en/latest/{family}/{name}.html"
    pages["xiao_c3"] = "https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/"
    pages["xiao_s3"] = "https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/"
    pages["xiao_c6"] = "https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/"
    pages["stamp_c3u"] = "https://docs.m5stack.com/en/core/Stamp-C3U"
    for key, name in (("qtpy_c3", "adafruit-qt-py-esp32-c3-wifi-dev-board"), ("qtpy_s3", "adafruit-qt-py-esp32-s3"), ("huzzah32", "adafruit-huzzah32-esp32-feather"), ("feather_s3", "adafruit-esp32-s3-feather")):
        pages[key] = f"https://learn.adafruit.com/{name}/downloads"
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for key, url in pages.items():
            futures.append(pool.submit(collect, key=key, url=url))
        for future in futures:
            try:
                print(future.result())
            except Exception as error:
                print(type(error).__name__, str(error))


if __name__ == "__main__":
    main()
