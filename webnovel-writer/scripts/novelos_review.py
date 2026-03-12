#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS review prompt builder (consistency/pacing/prose/reader)."""

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


def build_review_prompt(project_root: Path, chapter: int, review_type: str) -> Path:
    chapter_path = project_root / "project" / "chapters" / "drafts" / f"chapter_{chapter:03d}.md"
    plan_path = project_root / "project" / "outlines" / "chapter_plans" / f"chapter_{chapter:03d}.md"
    bible_path = project_root / "project" / "story_bible" / "characters.yaml"
    foreshadow_path = project_root / "project" / "story_bible" / "foreshadowings.yaml"
    prompt_path = project_root / "app" / "prompts" / "review" / f"{review_type}_review.md.j2"

    chapter_text = _read_text(chapter_path).strip()
    plan_text = _read_text(plan_path).strip()
    bible_text = _read_text(bible_path).strip()
    foreshadow_text = _read_text(foreshadow_path).strip()
    prompt_text = _read_text(prompt_path).strip()

    output_text = "\n".join(
        [
            f"# {review_type.title()} Review",
            "",
            "## Review Prompt",
            prompt_text or "(missing)",
            "",
            "## Chapter Text",
            chapter_text or "(missing)",
            "",
            "## Chapter Plan",
            plan_text or "(missing)",
            "",
            "## Story Bible (Characters)",
            bible_text or "(missing)",
            "",
            "## Foreshadowings",
            foreshadow_text or "(missing)",
            "",
        ]
    ).strip()

    out_dir = project_root / "project" / "reviews" / review_type
    output = out_dir / f"chapter_{chapter:03d}_{review_type}.prompt.md"
    _write_text(output, output_text + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS review")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--chapter", type=int, required=True)
    parser.add_argument("--type", required=True, choices=["consistency", "pacing", "prose", "reader"])
    args = parser.parse_args()

    path = build_review_prompt(Path(args.project_root), args.chapter, args.type)
    print(str(path))


if __name__ == "__main__":
    main()
