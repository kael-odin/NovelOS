#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS CLI (MVP scaffolding)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_script(script_name: str, argv: List[str]) -> int:
    script_path = _scripts_dir() / script_name
    if not script_path.is_file():
        raise FileNotFoundError(f"未找到脚本: {script_path}")
    proc = subprocess.run([sys.executable, str(script_path), *argv])
    return int(proc.returncode or 0)


def _not_implemented(name: str) -> int:
    print(f"NovelOS command not implemented yet: {name}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化 NovelOS 项目")
    p_init.add_argument("args", nargs=argparse.REMAINDER)

    p_plan = sub.add_parser("plan", help="规划相关命令")
    p_plan.add_argument("args", nargs=argparse.REMAINDER)

    p_context = sub.add_parser("context", help="上下文构建相关命令")
    p_context.add_argument("args", nargs=argparse.REMAINDER)

    p_task = sub.add_parser("task", help="任务相关命令")
    p_task.add_argument("args", nargs=argparse.REMAINDER)

    p_generate = sub.add_parser("generate", help="生成相关命令")
    p_generate.add_argument("args", nargs=argparse.REMAINDER)

    p_review = sub.add_parser("review", help="评审相关命令")
    p_review.add_argument("args", nargs=argparse.REMAINDER)

    p_revise = sub.add_parser("revise", help="修订相关命令")
    p_revise.add_argument("args", nargs=argparse.REMAINDER)

    p_summarize = sub.add_parser("summarize", help="摘要相关命令")
    p_summarize.add_argument("args", nargs=argparse.REMAINDER)

    p_extract = sub.add_parser("extract", help="提取相关命令")
    p_extract.add_argument("args", nargs=argparse.REMAINDER)

    p_apply = sub.add_parser("apply", help="应用变更相关命令")
    p_apply.add_argument("args", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if args.command == "init":
        raise SystemExit(_run_script("novelos_init.py", list(args.args or [])))

    rest = list(args.args or [])

    if args.command == "plan":
        if rest[:1] == ["chapter"]:
            raise SystemExit(_run_script("novelos_plan.py", rest[1:]))
        raise SystemExit(_not_implemented("plan"))

    if args.command == "context":
        if rest[:1] == ["build"]:
            raise SystemExit(_run_script("novelos_context.py", rest[1:]))
        raise SystemExit(_not_implemented("context"))

    if args.command == "task":
        if rest[:1] in (["create"], ["move"]):
            raise SystemExit(_run_script("novelos_task.py", rest))
        raise SystemExit(_not_implemented("task"))

    if args.command == "generate":
        if rest[:1] == ["chapter"]:
            raise SystemExit(_run_script("novelos_generate.py", rest[1:]))
        raise SystemExit(_not_implemented("generate"))

    if args.command == "review":
        if rest[:1] in (["consistency"], ["pacing"], ["prose"], ["reader"], ["merge"]):
            review_type = rest[0]
            if review_type == "merge":
                raise SystemExit(_run_script("novelos_merge_reviews.py", rest[1:]))
            raise SystemExit(_run_script("novelos_review.py", ["--type", review_type, *rest[1:]]))
        raise SystemExit(_not_implemented("review"))

    if args.command == "revise":
        if rest[:1] in (["chapter"], ["de-ai"]):
            revise_type = rest[0]
            mapped = "revise_by_review" if revise_type == "chapter" else "de_ai_flavor"
            raise SystemExit(_run_script("novelos_revise.py", ["--type", mapped, *rest[1:]]))
        raise SystemExit(_not_implemented("revise"))

    if args.command == "summarize":
        raise SystemExit(_run_script("novelos_summarize.py", rest))

    if args.command == "extract":
        if rest[:1] == ["changes"]:
            raise SystemExit(_run_script("novelos_extract.py", rest[1:]))
        raise SystemExit(_run_script("novelos_extract.py", rest))

    if args.command == "apply":
        if rest[:1] == ["changes"]:
            raise SystemExit(_run_script("novelos_apply.py", rest[1:]))
        raise SystemExit(_run_script("novelos_apply.py", rest))

    raise SystemExit(_not_implemented(args.command))


if __name__ == "__main__":
    main()
