#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexManager - 核心索引管理器

整合自 webnovel-writer/scripts/data_modules/index_manager.py
管理 index.db (SQLite) 的读写操作
"""
from __future__ import annotations

import json
import sqlite3
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager

from .config import get_config, CoreConfig
from .index_chapter_mixin import IndexChapterMixin
from .index_entity_mixin import IndexEntityMixin

logger = logging.getLogger(__name__)


@dataclass
class EntityMeta:
    id: str
    type: str
    canonical_name: str
    tier: str = "装饰"
    desc: str = ""
    current: Dict = field(default_factory=dict)
    first_appearance: int = 0
    last_appearance: int = 0
    is_protagonist: bool = False
    is_archived: bool = False


@dataclass
class StateChangeMeta:
    entity_id: str
    field: str
    old_value: str
    new_value: str
    reason: str
    chapter: int


@dataclass
class RelationshipMeta:
    from_entity: str
    to_entity: str
    type: str
    description: str
    chapter: int


@dataclass
class RelationshipEventMeta:
    from_entity: str
    to_entity: str
    type: str
    chapter: int
    action: str = "update"
    polarity: int = 0
    strength: float = 0.5
    description: str = ""
    scene_index: int = 0
    evidence: str = ""
    confidence: float = 1.0


class IndexManager(IndexChapterMixin, IndexEntityMixin):
    """索引管理器 - 整合章节、实体、状态变化、关系等索引"""

    def __init__(self, config: CoreConfig = None):
        self.config = config or get_config()
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        self.config.ensure_dirs()

        with self._get_conn() as conn:
            cursor = conn.cursor()

            # 章节表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    chapter INTEGER PRIMARY KEY,
                    title TEXT,
                    location TEXT,
                    word_count INTEGER,
                    characters TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 场景表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter INTEGER,
                    scene_index INTEGER,
                    start_line INTEGER,
                    end_line INTEGER,
                    location TEXT,
                    summary TEXT,
                    characters TEXT,
                    UNIQUE(chapter, scene_index)
                )
            """)

            # 出场记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appearances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT,
                    chapter INTEGER,
                    mentions TEXT,
                    confidence REAL,
                    UNIQUE(entity_id, chapter)
                )
            """)

            # 实体表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    canonical_name TEXT NOT NULL,
                    tier TEXT DEFAULT '装饰',
                    desc TEXT,
                    current_json TEXT,
                    first_appearance INTEGER DEFAULT 0,
                    last_appearance INTEGER DEFAULT 0,
                    is_protagonist INTEGER DEFAULT 0,
                    is_archived INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 别名表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aliases (
                    alias TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (alias, entity_id, entity_type)
                )
            """)

            # 状态变化表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS state_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL,
                    field TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    reason TEXT,
                    chapter INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 关系表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_entity TEXT NOT NULL,
                    to_entity TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    chapter INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(from_entity, to_entity, type)
                )
            """)

            # 关系事件表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationship_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_entity TEXT NOT NULL,
                    to_entity TEXT NOT NULL,
                    type TEXT NOT NULL,
                    action TEXT NOT NULL DEFAULT 'update',
                    polarity INTEGER DEFAULT 0,
                    strength REAL DEFAULT 0.5,
                    description TEXT,
                    chapter INTEGER NOT NULL,
                    scene_index INTEGER DEFAULT 0,
                    evidence TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scenes_chapter ON scenes(chapter)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_appearances_entity ON appearances(entity_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_appearances_chapter ON appearances(chapter)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_tier ON entities(tier)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_protagonist ON entities(is_protagonist)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_aliases_entity ON aliases(entity_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_state_changes_entity ON state_changes(entity_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_state_changes_chapter ON state_changes(chapter)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_entity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_chapter ON relationships(chapter)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_events_chapter ON relationship_events(chapter)")

            conn.commit()

    @contextmanager
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.config.index_db))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _row_to_dict(self, row: sqlite3.Row, parse_json_fields: List[str] = None) -> Dict:
        """将 sqlite3.Row 转换为字典， 并解析 JSON 字段"""
        result = dict(row)
        parse_json_fields = parse_json_fields or []
        for field_name in parse_json_fields:
            if field_name in result and result[field_name]:
                try:
                    result[field_name] = json.loads(result[field_name])
                except json.JSONDecodeError as exc:
                    logger.warning(
                        "failed to parse JSON in field %s: %s",
                        field_name,
                        exc
                    )
        return result

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self._get_conn() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM chapters")
            chapters = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM entities")
            entities = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM state_changes")
            changes = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM relationships")
            relationships = cursor.fetchone()[0] or 0

            cursor.execute("SELECT MAX(chapter) FROM chapters")
            max_chapter = cursor.fetchone()[0] or 0

            return {
                "chapters": chapters,
                "entities": entities,
                "state_changes": changes,
                "relationships": relationships,
                "max_chapter": max_chapter
            }
