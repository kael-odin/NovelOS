#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS planning helpers (placeholders for now)."""

from __future__ import annotations

import argparse
from pathlib import Path


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def plan_chapter(project_root: Path, chapter: int) -> Path:
    plan_path = project_root / "project" / "outlines" / "chapter_plans" / f"chapter_{chapter:03d}.md"
    if not plan_path.exists():
        _write_text(
            plan_path,
            "\n".join(
                [
                    f"# 第 {chapter} 章 规划",
                    "",
                    "- 本章目标：",
                    "- 本章在整卷中的作用：",
                    "- 本章核心冲突：",
                    "- 场景分解：",
                    "  1. ",
                    "  2. ",
                    "  3. ",
                    "- 出场角色：",
                    "- 可推进信息：",
                    "- 禁止暴露信息：",
                    "- 章末钩子：",
                    "- 一致性提醒：",
                    "- 文风/节奏建议：",
                    "",
                ]
            ),
        )
    return plan_path


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS planning")
    parser.add_argument("--project-root", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    p_chapter = sub.add_parser("chapter")
    p_chapter.add_argument("--chapter", type=int, required=True)

    args = parser.parse_args()
    root = Path(args.project_root)

    if args.command == "chapter":
        path = plan_chapter(root, args.chapter)
        print(str(path))
        return


if __name__ == "__main__":
    main()
