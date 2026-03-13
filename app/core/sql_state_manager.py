#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL State Manager - SQLite 状态管理模块

整合自 webnovel-writer/scripts/data_modules/sql_state_manager.py
基于 IndexManager 扩展，提供高级接口
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .index_manager import (
    IndexManager,
    EntityMeta,
    StateChangeMeta,
    RelationshipMeta,
    RelationshipEventMeta,
)
from .config import get_config, CoreConfig


@dataclass
class EntityData:
    """实体数据（用于 Data Agent 输入）"""
    id: str
    type: str
    name: str
    tier: str = "装饰"
    desc: str = ""
    current: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    first_appearance: int = 0
    last_appearance: int = 0
    is_protagonist: bool = False


class SQLStateManager:
    """
    SQLite 状态管理器

    提供与 StateManager 兼容的接口，数据存储在 SQLite (index.db) 中。
    """

    ENTITY_TYPES = ["角色", "地点", "物品", "势力", "招式"]

    def __init__(self, config: CoreConfig = None):
        self.config = config or get_config()
        self._index_manager = IndexManager(config)

    def upsert_entity(self, entity: EntityData) -> bool:
        """
        插入或更新实体

        返回: 是否为新实体
        """
        meta = EntityMeta(
            id=entity.id,
            type=entity.type,
            canonical_name=entity.name,
            tier=entity.tier,
            desc=entity.desc,
            current=entity.current,
            first_appearance=entity.first_appearance,
            last_appearance=entity.last_appearance,
            is_protagonist=entity.is_protagonist,
            is_archived=False
        )

        is_new = self._index_manager.upsert_entity(meta)

        self._index_manager.register_alias(entity.name, entity.id, entity.type)

        for alias in entity.aliases:
            if alias and alias != entity.name:
                self._index_manager.register_alias(alias, entity.id, entity.type)

        return is_new

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """获取实体详情"""
        entity = self._index_manager.get_entity(entity_id)
        if entity:
            entity["aliases"] = self._index_manager.get_entity_aliases(entity_id)
        return entity

    def get_entities_by_type(self, entity_type: str, include_archived: bool = False) -> List[Dict]:
        """按类型获取实体"""
        entities = self._index_manager.get_entities_by_type(entity_type, include_archived)
        for e in entities:
            e["aliases"] = self._index_manager.get_entity_aliases(e["id"])
        return entities

    def get_core_entities(self) -> List[Dict]:
        """获取核心实体（用于 Context Agent 全量加载）"""
        entities = self._index_manager.get_core_entities()
        for e in entities:
            e["aliases"] = self._index_manager.get_entity_aliases(e["id"])
        return entities

    def get_protagonist(self) -> Optional[Dict]:
        """获取主角实体"""
        protagonist = self._index_manager.get_protagonist()
        if protagonist:
            protagonist["aliases"] = self._index_manager.get_entity_aliases(protagonist["id"])
        return protagonist

    def update_entity_current(self, entity_id: str, updates: Dict) -> bool:
        """增量更新实体的 current 字段"""
        return self._index_manager.update_entity_current(entity_id, updates)

    def resolve_alias(self, alias: str) -> List[Dict]:
        """根据别名解析实体（一对多）"""
        return self._index_manager.get_entities_by_alias(alias)

    def register_alias(self, alias: str, entity_id: str, entity_type: str) -> bool:
        """注册别名"""
        return self._index_manager.register_alias(alias, entity_id, entity_type)

    def record_state_change(
        self,
        entity_id: str,
        field: str,
        old_value: Any,
        new_value: Any,
        reason: str,
        chapter: int
    ) -> int:
        """记录状态变化"""
        change = StateChangeMeta(
            entity_id=entity_id,
            field=field,
            old_value=str(old_value) if old_value is not None else "",
            new_value=str(new_value),
            reason=reason,
            chapter=chapter
        )
        return self._index_manager.record_state_change(change)

    def get_entity_state_changes(self, entity_id: str, limit: int = 20) -> List[Dict]:
        """获取实体的状态变化历史"""
        return self._index_manager.get_entity_state_changes(entity_id, limit)

    def get_recent_state_changes(self, limit: int = 50) -> List[Dict]:
        """获取最近的状态变化"""
        return self._index_manager.get_recent_state_changes(limit)

    def get_chapter_state_changes(self, chapter: int) -> List[Dict]:
        """获取某章的所有状态变化"""
        return self._index_manager.get_chapter_state_changes(chapter)

    def upsert_relationship(
        self,
        from_entity: str,
        to_entity: str,
        type: str,
        description: str,
        chapter: int
    ) -> bool:
        """插入或更新关系"""
        rel = RelationshipMeta(
            from_entity=from_entity,
            to_entity=to_entity,
            type=type,
            description=description,
            chapter=chapter
        )
        return self._index_manager.upsert_relationship(rel)

    def get_entity_relationships(self, entity_id: str, direction: str = "both") -> List[Dict]:
        """获取实体的关系"""
        return self._index_manager.get_entity_relationships(entity_id, direction)

    def get_relationship_between(self, entity1: str, entity2: str) -> List[Dict]:
        """获取两个实体之间的所有关系"""
        return self._index_manager.get_relationship_between(entity1, entity2)

    def get_recent_relationships(self, limit: int = 30) -> List[Dict]:
        """获取最近建立的关系"""
        return self._index_manager.get_recent_relationships(limit)

    def process_chapter_entities(
        self,
        chapter: int,
        entities_appeared: List[Dict],
        entities_new: List[Dict],
        state_changes: List[Dict],
        relationships_new: List[Dict]
    ) -> Dict[str, int]:
        """
        处理章节的实体数据（Data Agent 主入口）

        返回: 写入统计
        """
        stats = {
            "entities_updated": 0,
            "entities_created": 0,
            "state_changes": 0,
            "relationships": 0,
            "aliases": 0
        }

        for entity in entities_appeared:
            entity_id = entity.get("id")
            if not entity_id:
                continue

            self._index_manager.update_entity_current(entity_id, {})
            existing = self._index_manager.get_entity(entity_id)
            if existing:
                self._update_last_appearance(entity_id, chapter)
                stats["entities_updated"] += 1

            self._index_manager.record_appearance(
                entity_id=entity_id,
                chapter=chapter,
                mentions=entity.get("mentions", []),
                confidence=entity.get("confidence", 1.0)
            )

        for entity in entities_new:
            suggested_id = entity.get("suggested_id") or entity.get("id")
            if not suggested_id:
                continue

            entity_data = EntityData(
                id=suggested_id,
                type=entity.get("type", "角色"),
                name=entity.get("name", suggested_id),
                tier=entity.get("tier", "装饰"),
                desc=entity.get("desc", ""),
                current=entity.get("current", {}),
                aliases=entity.get("aliases", []),
                first_appearance=chapter,
                last_appearance=chapter,
                is_protagonist=entity.get("is_protagonist", False)
            )
            is_new = self.upsert_entity(entity_data)
            if is_new:
                stats["entities_created"] += 1
            else:
                stats["entities_updated"] += 1

            stats["aliases"] += 1 + len(entity_data.aliases)

            mentions = entity.get("mentions", [])
            if not mentions:
                mentions = [entity_data.name]
            self._index_manager.record_appearance(
                entity_id=suggested_id,
                chapter=chapter,
                mentions=mentions,
                confidence=entity.get("confidence", 1.0)
            )

        for change in state_changes:
            entity_id = change.get("entity_id")
            if not entity_id:
                continue

            self.record_state_change(
                entity_id=entity_id,
                field=change.get("field", ""),
                old_value=change.get("old", change.get("old_value", "")),
                new_value=change.get("new", change.get("new_value", "")),
                reason=change.get("reason", ""),
                chapter=chapter
            )
            stats["state_changes"] += 1

            field_name = change.get("field")
            new_value = change.get("new", change.get("new_value"))
            if field_name and new_value is not None:
                self._index_manager.update_entity_current(entity_id, {field_name: new_value})

        for rel in relationships_new:
            from_entity = rel.get("from", rel.get("from_entity"))
            to_entity = rel.get("to", rel.get("to_entity"))
            if not from_entity or not to_entity:
                continue
            rel_type = rel.get("type", "相识")
            description = rel.get("description", "")

            self._index_manager.record_relationship_event(
                RelationshipEventMeta(
                    from_entity=from_entity,
                    to_entity=to_entity,
                    type=rel_type,
                    chapter=chapter,
                    action=rel.get("action", "update"),
                    polarity=rel.get("polarity", 0),
                    strength=rel.get("strength", 0.5),
                    description=description,
                    scene_index=rel.get("scene_index", 0),
                    evidence=rel.get("evidence", ""),
                    confidence=rel.get("confidence", 1.0),
                )
            )

            self.upsert_relationship(
                from_entity=from_entity,
                to_entity=to_entity,
                type=rel_type,
                description=description,
                chapter=chapter
            )
            stats["relationships"] += 1

        return stats

    def _update_last_appearance(self, entity_id: str, chapter: int):
        """更新实体的 last_appearance"""
        with self._index_manager._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE entities SET
                    last_appearance = MAX(last_appearance, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (chapter, entity_id))
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._index_manager.get_stats()

    def export_to_entities_v3_format(self) -> Dict[str, Dict[str, Dict]]:
        """导出为 entities_v3 格式"""
        result = {t: {} for t in self.ENTITY_TYPES}

        for entity_type in self.ENTITY_TYPES:
            entities = self.get_entities_by_type(entity_type, include_archived=True)
            for e in entities:
                entity_dict = {
                    "canonical_name": e.get("canonical_name"),
                    "name": e.get("canonical_name"),
                    "tier": e.get("tier", "装饰"),
                    "aliases": e.get("aliases", []),
                    "desc": e.get("desc", ""),
                    "current": e.get("current_json", {}),
                    "history": [],
                    "first_appearance": e.get("first_appearance", 0),
                    "last_appearance": e.get("last_appearance", 0)
                }
                if e.get("is_protagonist"):
                    entity_dict["is_protagonist"] = True
                result[entity_type][e["id"]] = entity_dict

        return result

    def export_to_alias_index_format(self) -> Dict[str, List[Dict[str, str]]]:
        """导出为 alias_index 格式"""
        result = {}

        with self._index_manager._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT alias, entity_id, entity_type FROM aliases")
            for row in cursor.fetchall():
                alias = row["alias"]
                if alias not in result:
                    result[alias] = []
                result[alias].append({
                    "type": row["entity_type"],
                    "id": row["entity_id"]
                })

        return result
