#!/usr/bin/env python3
"""
Read `presentation/data/stamps.csv`, add an `info` column with a short
heuristic description (country and type when detectable), and write a new
CSV `presentation/data/stamps_with_info.csv`.

Usage:
  python utils/add_info_to_stamps.py [input_csv] [output_csv]

If paths are not provided, defaults are used.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from typing import Optional
from urllib.parse import unquote


DEFAULT_INPUT = os.path.join("presentation", "data", "stamps.csv")
DEFAULT_OUTPUT = os.path.join("presentation", "data", "stamps_with_info.csv")

TYPE_KEYWORDS = {
    "entry": {"entry", "arrive", "arrival", "in", "entrance", "entry"},
    "exit": {"exit", "depart", "departure", "out", "salida", "saida"},
}

REMOVE_TOKENS = {
    "stamp",
    "passport",
    "immigration",
    "airport",
    "arrival",
    "departure",
    "entry",
    "exit",
    "entrance",
    "departure",
    "arrive",
    "arr",
    "dep",
    "250px",
    "200px",
    "lossless",
    "page1",
    "jpg",
    "jpeg",
    "png",
    "tif",
    "tiff",
    "_",
}


def detect_type(tokens: list[str]) -> Optional[str]:
    tokset = set(tokens)
    if tokset & TYPE_KEYWORDS["entry"]:
        return "entry"
    if tokset & TYPE_KEYWORDS["exit"]:
        return "exit"
    return None


def clean_tokens(name: str) -> list[str]:
    # Decode percent-encodings and replace separators with spaces
    s = unquote(name)
    s = re.sub(r"[\-\_\(\)]+", " ", s)

    # Strip file extension
    s = re.sub(r"\.[A-Za-z0-9]+$", "", s)

    # Normalize whitespace and split
    parts = re.split(r"[\s]+", s)
    tokens: list[str] = []
    for p in parts:
        p = p.strip().lower()
        if not p:
            continue
        # Remove common numeric dimensions, years, and short garbage
        if re.fullmatch(r"\d{2,4}", p):
            continue
        # Remove tokens that are purely punctuation or short garbage
        if len(p) <= 1 and not p.isalpha():
            continue
        tokens.append(p)
    return tokens


def extract_country(tokens: list[str], detected_type: Optional[str]) -> Optional[str]:
    # Remove known noise tokens and type tokens
    filtered = [t for t in tokens if t not in REMOVE_TOKENS]
    if detected_type:
        filtered = [t for t in filtered if t != detected_type]

    # Remove tokens that look like file dimensions or common words
    filtered = [t for t in filtered if not re.fullmatch(r"\d{2,4}", t)]

    if not filtered:
        return None

    # Heuristic: prefer the longest token (likely a country name with underscores removed)
    candidate = max(filtered, key=len)

    # Clean punctuation
    candidate = re.sub(r"[^a-z0-9 ]", " ", candidate)
    candidate = " ".join(w for w in candidate.split() if w and len(w) > 1)
    if not candidate:
        return None

    # Title case the candidate
    return candidate.title()


def build_info(path: str) -> str:
    # Use the basename to extract info
    base = os.path.basename(path)
    tokens = clean_tokens(base)
    typ = detect_type(tokens)
    country = extract_country(tokens, typ)

    parts = []
    if country:
        parts.append(f"country={country}")
    if typ:
        parts.append(f"type={typ}")
    if not parts:
        return ""
    return "; ".join(parts)


def add_info_column(in_csv: str, out_csv: str) -> int:
    if not os.path.exists(in_csv):
        print(f"Input CSV not found: {in_csv}")
        return 2

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    with open(in_csv, newline="", encoding="utf-8") as infh, open(out_csv, "w", newline="", encoding="utf-8") as outfh:
        reader = csv.reader(infh)
        writer = csv.writer(outfh)

        try:
            header = next(reader)
        except StopIteration:
            print("Input CSV is empty")
            return 1

        # Insert 'info' as second column after 'path' if present, otherwise append
        if header and header[0].strip().lower() == "path":
            new_header = [header[0], "info"] + header[1:]
        else:
            new_header = header + ["info"]

        writer.writerow(new_header)

        for row in reader:
            if not row:
                continue
            path = row[0]
            info = build_info(path)
            # insert info after path
            new_row = [path, info] + row[1:]
            writer.writerow(new_row)

    print(f"Wrote output CSV to {out_csv}")
    return 0


def main(argv: list[str]) -> int:
    inp = argv[1] if len(argv) > 1 else DEFAULT_INPUT
    out = argv[2] if len(argv) > 2 else DEFAULT_OUTPUT
    return add_info_column(inp, out)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
