#!/usr/bin/env python3
"""Download and merge EPG XML files from epgshare01.online.

Downloads all EPG files (MN1, AE1, PL1, TR1, CZ1), extracts them, and merges into a single XML.GZ.
Channel entries are deduplicated by default (first occurrence kept).

Usage:
  python download_epg.py
  python download_epg.py --output epg_all.xml.gz
  python download_epg.py --output epg_all.xml.gz --overwrite
"""
from __future__ import annotations

import argparse
import gzip
import os
import sys
import urllib.request
import urllib.error
from io import BytesIO
from typing import List, Optional, Set
import xml.etree.ElementTree as ET

EPG_URLS = [
    "https://epgshare01.online/epgshare01/epg_ripper_MN1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_AE1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_PL1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CZ1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
]


def download_bytes(url: str, timeout: int = 30) -> Optional[bytes]:
    try:
        print(f"Downloading: {url}")
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            if getattr(resp, "status", 200) >= 400:
                print(f"HTTP error: {getattr(resp, 'status', '')} {getattr(resp, 'reason', '')}")
                return None
            buf = BytesIO()
            chunk_size = 16 * 1024
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                buf.write(chunk)
            return buf.getvalue()
    except urllib.error.HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"URL error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected download error: {e}")
        return None


def extract_gzip(data: bytes) -> Optional[bytes]:
    try:
        return gzip.decompress(data)
    except Exception as e:
        print(f"Failed to decompress gzip: {e}")
        return None


def unify_xml_bytes_list(xml_bytes_list: List[bytes], output_path: str, overwrite: bool = False, dedupe_channels: bool = False) -> int:
    # Force .gz output
    if not output_path.endswith(".gz"):
        output_path += ".gz"

    gz_path = output_path

    if os.path.exists(gz_path) and not overwrite:
        print(f"Error: output file '{gz_path}' exists. Use --overwrite to replace.")
        return 2

    out_dir = os.path.dirname(os.path.abspath(gz_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    written_channel_ids: Set[str] = set()

    # Try to copy root attributes from first XML
    root_attribs = {}
    try:
        if xml_bytes_list and xml_bytes_list[0]:
            first_tree = ET.parse(BytesIO(xml_bytes_list[0]))
            root_attribs = dict(first_tree.getroot().attrib)
    except Exception:
        pass

    try:
        with gzip.open(gz_path, "wb") as f_out:
            f_out.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode("utf-8"))
            attrs = "".join(f' {k}="{v}"' for k, v in root_attribs.items())
            f_out.write(f"<tv{attrs}>\n".encode("utf-8"))

            for idx, data in enumerate(xml_bytes_list):
                if not data:
                    continue
                buf = BytesIO(data)
                try:
                    tree = ET.parse(buf)
                    root = tree.getroot()

                    for elem in root.findall("channel"):
                        ch_id = elem.get("id", "")
                        if dedupe_channels and ch_id:
                            if ch_id in written_channel_ids:
                                continue
                            written_channel_ids.add(ch_id)
                        f_out.write(ET.tostring(elem, encoding="utf-8"))
                        f_out.write(b"\n")

                    for elem in root.findall("programme"):
                        f_out.write(ET.tostring(elem, encoding="utf-8"))
                        f_out.write(b"\n")

                except ET.ParseError as e:
                    print(f"XML parse error in input #{idx}: {e}")
                    continue

            f_out.write(b"</tv>\n")

        print(f"Wrote merged gzip XML to: {gz_path}")
        return 0
    except Exception as e:
        print(f"Failed to write gzip '{gz_path}': {e}")
        return 1


def download_and_unify(urls: List[str], output_path: str, timeout: int = 30, overwrite: bool = False, dedupe_channels: bool = False) -> int:
    xml_bytes_list: List[bytes] = []
    for url in urls:
        raw = download_bytes(url, timeout=timeout)
        if raw is None:
            print(f"Skipping URL due to download error: {url}")
            continue
        extracted = extract_gzip(raw)
        if extracted is None:
            print(f"Skipping URL due to decompression error: {url}")
            continue
        xml_bytes_list.append(extracted)

    if not xml_bytes_list:
        print("No XML data downloaded successfully.")
        return 1

    return unify_xml_bytes_list(xml_bytes_list, output_path, overwrite=overwrite, dedupe_channels=dedupe_channels)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download and merge EPG XML files from epgshare01.online")
    p.add_argument("--output", "-o", default="epg_all.xml.gz", help="Output merged gzip XML path")
    p.add_argument("--timeout", type=int, default=30, help="Network timeout in seconds")
    p.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    return download_and_unify(EPG_URLS, args.output, timeout=args.timeout, overwrite=args.overwrite, dedupe_channels=True)


if __name__ == "__main__":
    raise SystemExit(main())
