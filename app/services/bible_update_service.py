"""
故事圣经更新服务
根据状态变化自动更新故事圣经
"""

import copy
from typing import Dict, List, Any, Optional
from pathlib import Path

from .file_service import FileService
from .extraction_service import ExtractionService, StateChange, ChangeType


class BibleUpdateService:
    """故事圣经更新服务"""
    
    def __init__(self, project_path: str = "project"):
        self.fs = FileService(project_path)
        self.project_root = Path(project_path)
        self.extraction = ExtractionService(project_path)
    
    def update_from_changes(self, changes: List[StateChange]) -> Dict[str, Any]:
        """根据状态变化更新故事圣经"""
        bible = self._load_bible()
        updates = []
        
        for change in changes:
            update_result = self._apply_change(bible, change)
            if update_result:
                updates.append(update_result)
        
        if updates:
            self._save_bible(bible)
        
        return {
            "updates_count": len(updates),
            "updates": updates,
        }
    
    def update_from_chapter(self, chapter: int, content: str) -> Dict[str, Any]:
        """从章节内容更新故事圣经"""
        # 1. 提取状态变化
        changes = self.extraction.extract_from_chapter(chapter, content)
        
        # 2. 保存状态变化
        self.extraction.save_changes(chapter, changes)
        
        # 3. 更新故事圣经
        return self.update_from_changes(changes)
    
    def _apply_change(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """应用单个状态变化到故事圣经"""
        if change.change_type == ChangeType.CHARACTER_STATUS:
            return self._update_character_status(bible, change)
        elif change.change_type == ChangeType.CHARACTER_LOCATION:
            return self._update_character_location(bible, change)
        elif change.change_type == ChangeType.CHARACTER_RELATIONSHIP:
            return self._update_character_relationship(bible, change)
        elif change.change_type == ChangeType.CHARACTER_ABILITY:
            return self._update_character_ability(bible, change)
        elif change.change_type == ChangeType.TIME_PASSAGE:
            return self._update_timeline(bible, change)
        elif change.change_type == ChangeType.FORESHADOWING_PLANTED:
            return self._add_foreshadowing(bible, change)
        elif change.change_type == ChangeType.FORESHADOWING_RESOLVED:
            return self._resolve_foreshadowing(bible, change)
        
        return None
    
    def _update_character_status(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """更新角色状态"""
        characters = bible.get("characters", [])
        
        for char in characters:
            if char.get("name") == change.entity_name or char.get("id") == change.entity_id:
                old_status = char.get("current_state", {}).get("status", "alive")
                char.setdefault("current_state", {})["status"] = change.new_value
                char["current_state"]["last_updated_chapter"] = change.chapter
                
                return {
                    "type": "character_status",
                    "character": change.entity_name,
                    "old": old_status,
                    "new": change.new_value,
                    "chapter": change.chapter,
                }
        
        return None
    
    def _update_character_location(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """更新角色位置"""
        characters = bible.get("characters", [])
        
        for char in characters:
            if char.get("name") == change.entity_name or char.get("id") == change.entity_id:
                old_location = char.get("current_state", {}).get("location", "")
                char.setdefault("current_state", {})["location"] = change.new_value
                char["current_state"]["last_updated_chapter"] = change.chapter
                
                return {
                    "type": "character_location",
                    "character": change.entity_name,
                    "old": old_location,
                    "new": change.new_value,
                    "chapter": change.chapter,
                }
        
        return None
    
    def _update_character_relationship(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """更新角色关系"""
        relationships = bible.get("relationships", [])
        
        # 解析关系中的两个角色
        parts = change.entity_name.split("和")
        if len(parts) != 2:
            return None
        
        char1, char2 = parts[0], parts[1]
        
        # 查找现有关系
        for rel in relationships:
            if (rel.get("source") == char1 and rel.get("target") == char2) or \
               (rel.get("source") == char2 and rel.get("target") == char1):
                old_type = rel.get("current_status", "")
                rel["current_status"] = change.new_value
                rel["latest_update_chapter"] = change.chapter
                
                return {
                    "type": "relationship",
                    "characters": change.entity_name,
                    "old": old_type,
                    "new": change.new_value,
                    "chapter": change.chapter,
                }
        
        # 创建新关系
        new_rel = {
            "source": char1,
            "target": char2,
            "type": change.new_value,
            "current_status": change.new_value,
            "latest_update_chapter": change.chapter,
        }
        relationships.append(new_rel)
        bible["relationships"] = relationships
        
        return {
            "type": "relationship_new",
            "characters": change.entity_name,
            "new": change.new_value,
            "chapter": change.chapter,
        }
    
    def _update_character_ability(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """更新角色能力"""
        characters = bible.get("characters", [])
        
        for char in characters:
            if char.get("name") == change.entity_name or char.get("id") == change.entity_id:
                abilities = char.get("current_state", {}).get("abilities", [])
                if change.new_value not in abilities:
                    abilities.append(change.new_value)
                    char.setdefault("current_state", {})["abilities"] = abilities
                    char["current_state"]["last_updated_chapter"] = change.chapter
                    
                    return {
                        "type": "character_ability",
                        "character": change.entity_name,
                        "new_ability": change.new_value,
                        "chapter": change.chapter,
                    }
        
        return None
    
    def _update_timeline(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """更新时间线"""
        timeline = bible.get("timeline", [])
        
        # 添加时间线事件
        new_event = {
            "chapter": change.chapter,
            "event": change.description,
            "time_marker": change.new_value,
        }
        timeline.append(new_event)
        bible["timeline"] = timeline
        
        return {
            "type": "timeline",
            "chapter": change.chapter,
            "event": change.description,
        }
    
    def _add_foreshadowing(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """添加伏笔"""
        foreshadowings = bible.get("foreshadowings", [])
        
        # 检查是否已存在
        for f in foreshadowings:
            if f.get("description") == change.description:
                return None
        
        new_foreshadowing = {
            "id": change.entity_id,
            "title": change.entity_name,
            "description": change.description,
            "planted_at": change.chapter,
            "status": "planted",
            "confidence": change.confidence,
        }
        foreshadowings.append(new_foreshadowing)
        bible["foreshadowings"] = foreshadowings
        
        return {
            "type": "foreshadowing_planted",
            "description": change.description[:50],
            "chapter": change.chapter,
        }
    
    def _resolve_foreshadowing(self, bible: Dict[str, Any], change: StateChange) -> Optional[Dict[str, Any]]:
        """解决伏笔"""
        foreshadowings = bible.get("foreshadowings", [])
        
        for f in foreshadowings:
            if f.get("id") == change.entity_id or f.get("title") == change.entity_name:
                f["status"] = "resolved"
                f["resolved_at"] = change.chapter
                
                return {
                    "type": "foreshadowing_resolved",
                    "id": change.entity_id,
                    "chapter": change.chapter,
                }
        
        return None
    
    def _load_bible(self) -> Dict[str, Any]:
        """加载故事圣经"""
        path = "story_bible/bible.yaml"
        if not self.fs.exists(path):
            return {}
        
        return self.fs.read_yaml(path) or {}
    
    def _save_bible(self, bible: Dict[str, Any]) -> None:
        """保存故事圣经"""
        path = "story_bible/bible.yaml"
        self.fs.write_yaml(path, bible)
    
    def get_character_state(self, character_id: str) -> Optional[Dict[str, Any]]:
        """获取角色当前状态"""
        bible = self._load_bible()
        characters = bible.get("characters", [])
        
        for char in characters:
            if char.get("id") == character_id or char.get("name") == character_id:
                return char.get("current_state", {})
        
        return None
    
    def get_active_foreshadowings(self) -> List[Dict[str, Any]]:
        """获取未解决的伏笔"""
        bible = self._load_bible()
        foreshadowings = bible.get("foreshadowings", [])
        
        return [f for f in foreshadowings if f.get("status") != "resolved"]
    
    def generate_update_report(self, chapter: int) -> str:
        """生成更新报告"""
        changes = self.extraction.load_changes(chapter)
        
        if not changes:
            return f"# 第{chapter}章故事圣经更新报告\n\n无更新"
        
        lines = [
            f"# 第{chapter}章故事圣经更新报告",
            "",
            f"共 {len(changes)} 个状态变化",
            "",
        ]
        
        # 按类型分组
        by_type = {}
        for change in changes:
            t = change.change_type.value
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(change)
        
        for change_type, type_changes in by_type.items():
            lines.append(f"## {change_type}")
            for change in type_changes:
                lines.append(f"- **{change.entity_name}**: {change.description}")
            lines.append("")
        
        return "\n".join(lines)
