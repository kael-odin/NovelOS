#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build NovelOS context bundle for a chapter."""

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


def _safe_read(path: Path, fallback: str) -> str:
    text = _read_text(path).strip()
    return text if text else fallback


def build_context(project_root: Path, chapter: int) -> Path:
    outlines_dir = project_root / "project" / "outlines"
    bible_dir = project_root / "project" / "story_bible"
    memory_dir = project_root / "project" / "memory"

    chapter_plan = outlines_dir / "chapter_plans" / f"chapter_{chapter:03d}.md"
    recent_summaries_dir = memory_dir / "chapter_summaries"
    context_dir = memory_dir / "context"

    # Gather context sections
    writing_goal = _safe_read(chapter_plan, "- 本章目标：\n- 必须推进：\n- 不可推进：")

    recent_summaries = []
    for i in range(max(1, chapter - 3), chapter):
        summary_path = recent_summaries_dir / f"chapter_{i:03d}.md"
        summary_text = _read_text(summary_path).strip()
        if summary_text:
            recent_summaries.append(f"### Chapter {i:03d}\n{summary_text}\n")

    character_states = _safe_read(bible_dir / "characters.yaml", "characters: []")
    foreshadowings = _safe_read(bible_dir / "foreshadowings.yaml", "foreshadowings: []")

    content = "\n".join(
        [
            f"# Chapter {chapter:03d} Context Bundle",
            "",
            "## 1. Writing Goal",
            writing_goal,
            "",
            "## 2. Recent Chapter Summaries",
            "\n".join(recent_summaries) if recent_summaries else "- (暂无)\n",
            "",
            "## 3. Current Character States",
            "```yaml",
            character_states.strip(),
            "```",
            "",
            "## 4. Active Foreshadowings",
            "```yaml",
            foreshadowings.strip(),
            "```",
        ]
    ).strip()
    output_path = context_dir / f"chapter_{chapter:03d}_context.md"
    _write_text(output_path, content + "\n")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS context builder")
    parser.add_argument("--project-root", required=True, help="NovelOS project root")
    parser.add_argument("--chapter", type=int, required=True)
    args = parser.parse_args()

    path = build_context(Path(args.project_root), args.chapter)
    print(str(path))


if __name__ == "__main__":
    main()
