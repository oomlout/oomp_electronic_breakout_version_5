"""Download the exact manufacturer assets linked by the captured research pages."""

import concurrent.futures
import hashlib
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1] / "research" / "microcontrollers"


def fetch(**kwargs):
    url = kwargs["url"]
    destination = kwargs["destination"]
    if not destination.exists():
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
    return {
        "url": url,
        "local_file": destination.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }


def main(**kwargs):
    jobs = {}
    for path in ROOT.glob("*.json"):
        page = json.loads(path.read_text(encoding="utf-8"))
        if "links" not in page:
            continue
        for link in page["links"]:
            url = link["url"]
            title = link["title"].lower()
            if url.lower().endswith((".pdf", ".dxf", ".zip")) and any(word in title for word in ("dimension", "schematic", "kicad", "bottom pad")):
                destination = ROOT / path.stem / (url.split("/")[-1].replace("%20", " ").replace("&", "_"))
                jobs[url] = destination
    repositories = {}
    repositories["qtpy_c3"] = "Adafruit-QT-Py-ESP32-C3-PCB"
    repositories["qtpy_s3"] = "Adafruit-QT-Py-ESP32-S3-PCB"
    repositories["huzzah32"] = "Adafruit-HUZZAH32-ESP32-Feather-PCB"
    repositories["feather_s3"] = "Adafruit-Feather-ESP32-S3-PCB"
    for key, repository in repositories.items():
        response = requests.get(f"https://api.github.com/repos/adafruit/{repository}/contents/", timeout=30)
        response.raise_for_status()
        for item in response.json():
            if item["name"].endswith((".brd", ".sch")):
                jobs[item["download_url"]] = ROOT / key / item["name"]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for url, destination in jobs.items():
            futures.append(pool.submit(fetch, url=url, destination=destination))
        for future in futures:
            try:
                result = future.result()
                results.append(result)
                print(result["local_file"])
            except Exception as error:
                print(type(error).__name__, str(error))
    (ROOT / "downloads.json").write_text(json.dumps(results, indent=4) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
