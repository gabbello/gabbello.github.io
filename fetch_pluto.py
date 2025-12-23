#!/usr/bin/env python3
"""Fetch https://nocords.xyz/pluto/epg.xml and save as pluto.xml in the repo root.

This script uses only the standard library so it has no extra dependencies.
"""
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

URL = "https://nocords.xyz/pluto/epg.xml"
DEST = Path(__file__).resolve().parent / "pluto.xml"
TMP = DEST.with_suffix(".xml.tmp")

def fetch(url: str = URL, dest: Path = DEST) -> int:
    req = Request(url, headers={"User-Agent": "fetch-pluto/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
    except (HTTPError, URLError) as e:
        print(f"ERROR: failed to fetch {url}: {e}", file=sys.stderr)
        return 1

    try:
        TMP.write_bytes(data)
        TMP.replace(dest)
    except Exception as e:
        print(f"ERROR: failed to write {dest}: {e}", file=sys.stderr)
        return 2

    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(fetch())
