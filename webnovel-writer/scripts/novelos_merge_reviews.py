#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge NovelOS reviews for a chapter."""

from __future__ import annotations

import argparse
from pathlib import Path


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def merge_reviews(project_root: Path, chapter: int) -> Path:
    review_dir = project_root / "project" / "reviews"
    parts = []
    for review_type in ["consistency", "pacing", "prose", "reader"]:
        path = review_dir / review_type / f"chapter_{chapter:03d}_{review_type}.prompt.md"
        text = _read_text(path).strip()
        if text:
            parts.append(f"## {review_type.title()} Review\n\n{text}\n")
    if not parts:
        parts.append("(no reviews found)\n")

    merged = "# Merged Reviews\n\n" + "\n".join(parts)
    out_path = review_dir / "merged" / f"chapter_{chapter:03d}_merged.md"
    _write_text(out_path, merged.strip() + "\n")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS merge reviews")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--chapter", type=int, required=True)
    args = parser.parse_args()

    path = merge_reviews(Path(args.project_root), args.chapter)
    print(str(path))


if __name__ == "__main__":
    main()
