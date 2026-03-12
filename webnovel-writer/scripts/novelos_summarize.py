#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS summarize prompt generator."""

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


def build_summary_prompt(project_root: Path, chapter: int) -> Path:
    chapter_path = project_root / "project" / "chapters" / "drafts" / f"chapter_{chapter:03d}.md"
    chapter_text = _read_text(chapter_path).strip()

    prompt = "\n".join(
        [
            "# Chapter Summary",
            "",
            "## Chapter Text",
            chapter_text or "(missing)",
            "",
        ]
    ).strip()

    output = project_root / "project" / "memory" / "chapter_summaries" / f"chapter_{chapter:03d}.md"
    _write_text(output, prompt + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS summarize")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--chapter", type=int, required=True)
    args = parser.parse_args()

    path = build_summary_prompt(Path(args.project_root), args.chapter)
    print(str(path))


if __name__ == "__main__":
    main()
