#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS chapter generation prompt builder."""

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


def build_generate_prompt(project_root: Path, chapter: int) -> Path:
    plan_path = project_root / "project" / "outlines" / "chapter_plans" / f"chapter_{chapter:03d}.md"
    context_path = project_root / "project" / "memory" / "context" / f"chapter_{chapter:03d}_context.md"
    rules_path = project_root / "app" / "prompts" / "system" / "writing_rules.md"

    plan_text = _read_text(plan_path).strip()
    context_text = _read_text(context_path).strip()
    rules_text = _read_text(rules_path).strip()

    prompt = "\n".join(
        [
            "# NovelOS Chapter Generation",
            "",
            "## Chapter Plan",
            plan_text or "(missing)",
            "",
            "## Context Bundle",
            context_text or "(missing)",
            "",
            "## Writing Rules",
            rules_text or "(missing)",
            "",
        ]
    ).strip()

    output = project_root / "project" / "chapters" / "drafts" / f"chapter_{chapter:03d}.prompt.md"
    _write_text(output, prompt + "\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS generate")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--chapter", type=int, required=True)
    args = parser.parse_args()

    path = build_generate_prompt(Path(args.project_root), args.chapter)
    print(str(path))


if __name__ == "__main__":
    main()
