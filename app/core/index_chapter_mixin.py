#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexChapterMixin - 章节索引操作
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IndexChapterMixin:
    def process_chapter_data(
        self,
        chapter: int,
        title: str,
        location: str,
        word_count: int,
        entities: List[str],
        scenes: List[Dict],
    ) -> Dict[str, int]:
        """
        处理章节数据（写入索引）
        
        返回写入统计
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 写入章节元数据
            cursor.execute("""
                INSERT OR REPLACE INTO chapters
                (chapter, title, location, word_count, characters, summary)
                VALUES (?, ?, ?, ?, ?, '')
            """, (chapter, title, location, word_count, json.dumps(entities, ensure_ascii=False)))
            
            # 写入场景
            for scene in scenes:
                cursor.execute("""
                    INSERT OR REPLACE INTO scenes
                    (chapter, scene_index, start_line, end_line, location, summary, characters)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chapter,
                    scene.get("scene_index", 0),
                    scene.get("start_line", 0),
                    scene.get("end_line", 0),
                    scene.get("location", ""),
                    scene.get("summary", ""),
                    json.dumps(scene.get("characters", []), ensure_ascii=False)
                ))
            
            # 写入出场记录
            for entity_id in entities:
                cursor.execute("""
                    INSERT OR REPLACE INTO appearances
                    (entity_id, chapter, mentions, confidence)
                    VALUES (?, ?, '[]', 1.0)
                """, (entity_id, chapter))
            
            conn.commit()
        
        return {
            "chapter": chapter,
            "scenes": len(scenes),
            "entities": len(entities)
        }

    def get_chapter(self, chapter: int) -> Optional[Dict]:
        """获取章节元数据"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chapters WHERE chapter = ?", (chapter,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result.get("characters"):
                    try:
                        result["characters"] = json.loads(result["characters"])
                    except json.JSONDecodeError:
                        result["characters"] = []
                return result
            return None

    def get_recent_chapters(self, limit: int = 10) -> List[Dict]:
        """获取最近的章节列表"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chapters ORDER BY chapter DESC LIMIT ?",
                (limit,)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("characters"):
                    try:
                        result["characters"] = json.loads(result["characters"])
                    except json.JSONDecodeError:
                        result["characters"] = []
                results.append(result)
            return results

    def get_chapter_scenes(self, chapter: int) -> List[Dict]:
        """获取章节的所有场景"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM scenes WHERE chapter = ? ORDER BY scene_index",
                (chapter,)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("characters"):
                    try:
                        result["characters"] = json.loads(result["characters"])
                    except json.JSONDecodeError:
                        result["characters"] = []
                results.append(result)
            return results

    def search_scenes_by_location(self, location: str, limit: int = 20) -> List[Dict]:
        """按地点搜索场景"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM scenes
                WHERE location LIKE ?
                ORDER BY chapter DESC, scene_index
                LIMIT ?
                """,
                (f"%{location}%", limit)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("characters"):
                    try:
                        result["characters"] = json.loads(result["characters"])
                    except json.JSONDecodeError:
                        result["characters"] = []
                results.append(result)
            return results

    # ==================== 出场记录操作 ====================

    def record_appearance(
        self,
        entity_id: str,
        chapter: int,
        mentions: List[str] = None,
        confidence: float = 1.0
    ) -> bool:
        """记录实体出场"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO appearances
                (entity_id, chapter, mentions, confidence)
                VALUES (?, ?, ?, ?)
            """, (
                entity_id,
                chapter,
                json.dumps(mentions or [], ensure_ascii=False),
                confidence
            ))
            conn.commit()
            return True

    def get_entity_appearances(self, entity_id: str, limit: int = 50) -> List[Dict]:
        """获取实体的出场记录"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM appearances
                WHERE entity_id = ?
                ORDER BY chapter DESC
                LIMIT ?
                """,
                (entity_id, limit)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("mentions"):
                    try:
                        result["mentions"] = json.loads(result["mentions"])
                    except json.JSONDecodeError:
                        result["mentions"] = []
                results.append(result)
            return results

    def get_recent_appearances(self, limit: int = 20) -> List[Dict]:
        """获取最近的出场记录"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.*, e.canonical_name, e.type
                FROM appearances a
                LEFT JOIN entities e ON a.entity_id = e.id
                ORDER BY a.chapter DESC
                LIMIT ?
                """,
                (limit,)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("mentions"):
                    try:
                        result["mentions"] = json.loads(result["mentions"])
                    except json.JSONDecodeError:
                        result["mentions"] = []
                results.append(result)
            return results

    def get_chapter_appearances(self, chapter: int) -> List[Dict]:
        """获取某章的所有出场记录"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.*, e.canonical_name, e.type
                FROM appearances a
                LEFT JOIN entities e ON a.entity_id = e.id
                WHERE a.chapter = ?
                """,
                (chapter,)
            )
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get("mentions"):
                    try:
                        result["mentions"] = json.loads(result["mentions"])
                    except json.JSONDecodeError:
                        result["mentions"] = []
                results.append(result)
            return results
