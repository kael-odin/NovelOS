#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContextManager - 上下文管理模块

整合自 webnovel-writer/scripts/data_modules/context_manager.py
组装上下文包
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import get_config, CoreConfig
from .index_manager import IndexManager

logger = logging.getLogger(__name__)


class ContextManager:
    """上下文管理器"""

    def __init__(self, config: CoreConfig = None):
        self.config = config or get_config()
        self.index_manager = IndexManager(self.config)

    def build_context(
        self,
        chapter: int,
        max_chars: Optional[int] = None,
    ) -> Dict[str, Any]:
        """构建章节上下文"""
        max_chars = max_chars or 8000

        pack = self._build_pack(chapter)
        assembled = self.assemble_context(pack, max_chars=max_chars)

        return assembled

    def assemble_context(
        self,
        pack: Dict[str, Any],
        max_chars: int = 8000,
    ) -> Dict[str, Any]:
        """组装上下文"""
        assembled: Dict[str, Any] = {"meta": pack.get("meta", {}), "sections": {}}

        for name, content in pack.items():
            if name == "meta":
                continue
            text = json.dumps(content, ensure_ascii=False)
            assembled["sections"][name] = {"content": content, "text": text}

        return assembled

    def _build_pack(self, chapter: int) -> Dict[str, Any]:
        """构建上下文包"""
        state = self._load_state()

        core = {
            "chapter_outline": self._load_outline(chapter),
            "protagonist_snapshot": state.get("protagonist_state", {}),
            "recent_summaries": self._load_recent_summaries(chapter, window=3),
        }

        scene = {
            "location_context": state.get("protagonist_state", {}).get("location", {}),
            "appearing_characters": self._load_recent_appearances(limit=10),
        }

        global_ctx = {
            "worldview_skeleton": self._load_setting("世界观"),
            "power_system_skeleton": self._load_setting("力量体系"),
        }

        return {
            "meta": {"chapter": chapter},
            "core": core,
            "scene": scene,
            "global": global_ctx,
        }

    def _load_state(self) -> Dict[str, Any]:
        path = self.config.state_file
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_outline(self, chapter: int) -> str:
        outline_path = self.config.outlines_dir / f"chapter_{chapter:04d}.md"
        if outline_path.exists():
            return outline_path.read_text(encoding="utf-8")
        return ""

    def _load_recent_summaries(self, chapter: int, window: int = 3) -> List[Dict[str, Any]]:
        summaries = []
        for ch in range(max(1, chapter - window), chapter):
            summary = self._load_summary_text(ch)
            if summary:
                summaries.append(summary)
        return summaries

    def _load_summary_text(self, chapter: int) -> Optional[Dict[str, Any]]:
        summary_path = self.config.summaries_dir / f"ch{chapter:04d}.md"
        if not summary_path.exists():
            return None
        text = summary_path.read_text(encoding="utf-8")
        return {"chapter": chapter, "summary": text}

    def _load_recent_appearances(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        appearances = self.index_manager.get_recent_appearances(limit=limit)
        return appearances or []

    def _load_setting(self, keyword: str) -> str:
        settings_dir = self.config.story_bible_dir
        candidates = [
            settings_dir / f"{keyword}.md",
            settings_dir / f"{keyword}.yaml",
        ]
        for path in candidates:
            if path.exists():
                return path.read_text(encoding="utf-8")
        matches = list(settings_dir.glob(f"*{keyword}*.md"))
        if matches:
            return matches[0].read_text(encoding="utf-8")
        return f"[{keyword}设定未找到]"
