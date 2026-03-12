#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS task creation and movement helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_task(project_root: Path, task_type: str, chapter: int) -> Path:
    tasks_dir = project_root / "project" / "tasks" / "queue"
    task_id = f"{task_type}_{chapter:03d}"
    data = {
        "task_id": task_id,
        "type": task_type,
        "status": "queued",
        "chapter": chapter,
        "inputs": {
            "chapter_plan": f"project/outlines/chapter_plans/chapter_{chapter:03d}.md",
            "context_bundle": f"project/memory/context/chapter_{chapter:03d}_context.md",
            "rules": "app/prompts/system/writing_rules.md",
        },
        "outputs": {
            "draft": f"project/chapters/drafts/chapter_{chapter:03d}.md"
        },
        "constraints": {
            "target_words_min": 3000,
            "target_words_max": 4500,
            "must_have_hook": True,
            "must_preserve_character_consistency": True,
        },
    }
    path = tasks_dir / f"task_{task_id}.json"
    _write_json(path, data)
    return path


def move_task(project_root: Path, task_id: str, status: str) -> Path:
    base = project_root / "project" / "tasks"
    src_paths = list(base.rglob(f"task_{task_id}.json"))
    if not src_paths:
        raise FileNotFoundError(f"Task not found: {task_id}")
    src = src_paths[0]
    dest_dir = base / status
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    if src != dest:
        src.unlink(missing_ok=True)
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS tasks")
    parser.add_argument("--project-root", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--type", required=True)
    p_create.add_argument("--chapter", type=int, required=True)

    p_move = sub.add_parser("move")
    p_move.add_argument("--id", required=True)
    p_move.add_argument("--status", required=True)

    args = parser.parse_args()
    root = Path(args.project_root)

    if args.command == "create":
        path = create_task(root, args.type, args.chapter)
        print(str(path))
        return

    if args.command == "move":
        path = move_task(root, args.id, args.status)
        print(str(path))
        return


if __name__ == "__main__":
    main()
