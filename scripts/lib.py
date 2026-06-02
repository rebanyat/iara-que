"""Shared helpers for the ETL scripts."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

SCRIPTS_DIR = Path(__file__).resolve().parent
PR2_DIR = SCRIPTS_DIR.parent
RAW_DIR = PR2_DIR.parent / "03_Datasets"
CACHE_DIR = SCRIPTS_DIR / ".cache"
DATA_DIR = PR2_DIR / "app" / "static" / "data"

CACHE_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(f"  · {msg}", flush=True)


def banner(title: str) -> None:
    bar = "─" * (len(title) + 4)
    print(f"\n┌{bar}┐\n│  {title}  │\n└{bar}┘", flush=True)


def write_json(payload: Any, dest: Path, *, indent: int | None = None) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=indent)
    log(f"wrote {dest.relative_to(PR2_DIR)} ({dest.stat().st_size / 1024:.1f} KB)")


def require(condition: bool, msg: str) -> None:
    if not condition:
        print(f"  ✗ {msg}", file=sys.stderr, flush=True)
        sys.exit(1)


def first_existing(*candidates: Path) -> Path | None:
    for c in candidates:
        if c.exists():
            return c
    return None


def find_one(parent: Path, patterns: Iterable[str]) -> Path | None:
    for pattern in patterns:
        hits = sorted(parent.glob(pattern))
        if hits:
            return hits[0]
    return None
