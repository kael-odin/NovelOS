#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS revise prompt builder."""

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


def build_revise_prompt(project_root: Path, chapter: int, revise_type: str) -> Path:
    chapter_path = project_root / "project" / "chapters" / "drafts" / f"chapter_{chapter:03d}.md"
    merged_review_path = project_root / "project" / "reviews" / "merged" / f"chapter_{chapter:03d}_merged.md"
    prompt_path = project_root / "app" / "prompts" / "revision" / f"{revise_type}.md.j2"

    chapter_text = _read_text(chapter_path).strip()
    merged_text = _read_text(merged_review_path).strip()
    prompt_text = _read_text(prompt_path).strip()

    output_text = "\n".join(
        [
            f"# Revise ({revise_type})",
            "",
            "## Revision Prompt",
            prompt_text or "(missing)",
            "",
            "## Chapter Text",
            chapter_text or "(missing)",
            "",
            "## Merged Review",
            merged_text or "(missing)",
            "",
        ]
    ).strip()

    out_dir = project_root / "project" / "revisions" / f"chapter_{chapter:03d}"
    output = out_dir / f"chapter_{chapter:03d}_{revise_type}.prompt.md"
    _write_text(output, output_text + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS revise")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--type", required=True, choices=["revise_by_review", "de_ai_flavor"])
    args = parser.parse_args()

    path = build_revise_prompt(Path(args.project_root), args.chapter, args.type)
    print(str(path))


if __name__ == "__main__":
    main()
