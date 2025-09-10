#!/usr/bin/env python3
"""
Scan the `data/stamps` directory and write a CSV file with columns:
path,result1,result2,result3

Usage:
  python utils/stamps_csv.py [output_csv]

If `output_csv` is not provided, defaults to `utils/stamps.csv`.
"""
from __future__ import annotations

import csv
import os
import sys
from typing import Iterator


def iter_image_paths(root: str) -> Iterator[str]:
    """Yield relative file paths for files under `root`.

    The paths are returned relative to the repository root (cwd).
    """
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            # skip hidden files
            if fn.startswith("."):
                continue
            yield os.path.join(dirpath, fn)


def write_csv(paths: Iterator[str], out_path: str) -> None:
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "result1", "result2", "result3"])
        for p in paths:
            writer.writerow([p, "", "", ""])


def main(argv: list[str]) -> int:
    out = argv[1] if len(argv) > 1 else "utils/stamps.csv"
    stamps_dir = os.path.join(os.getcwd(), "data", "stamps")
    if not os.path.isdir(stamps_dir):
        print(f"Error: stamps directory not found: {stamps_dir}")
        return 2

    paths = iter_image_paths(stamps_dir)
    write_csv(paths, out)
    print(f"Wrote CSV to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


