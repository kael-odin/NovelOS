"""
状态变化提取服务
从章节内容中提取状态变化，用于更新故事圣经
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .file_service import FileService


class ChangeType(Enum):
    CHARACTER_LOCATION = "character_location"
    CHARACTER_STATE = "character_state"
    CHARACTER_RELATIONSHIP = "character_relationship"
    CHARACTER_ABILITY = "character_ability"
    CHARACTER_STATUS = "character_status"  # alive, dead, injured, etc.
    WORLD_EVENT = "world_event"
    ITEM_TRANSFER = "item_transfer"
    LOCATION_STATE = "location_state"
    FORESHADOWING_PLANTED = "foreshadowing_planted"
    FORESHADOWING_RESOLVED = "foreshadowing_resolved"
    TIME_PASSAGE = "time_passage"


@dataclass
class StateChange:
    change_type: ChangeType
    entity_id: str
    entity_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: str = ""
    chapter: int = 0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExtractionService:
    """状态变化提取服务"""
    
    def __init__(self, project_path: str = "project"):
        self.fs = FileService(project_path)
        self.project_root = Path(project_path)
    
    def extract_from_chapter(self, chapter: int, content: str) -> List[StateChange]:
        """从章节内容中提取状态变化"""
        changes = []
        
        # 1. 提取角色状态变化
        changes.extend(self._extract_character_state_changes(content, chapter))
        
        # 2. 提取位置变化
        changes.extend(self._extract_location_changes(content, chapter))
        
        # 3. 提取关系变化
        changes.extend(self._extract_relationship_changes(content, chapter))
        
        # 4. 提取能力变化
        changes.extend(self._extract_ability_changes(content, chapter))
        
        # 5. 提取时间变化
        changes.extend(self._extract_time_changes(content, chapter))
        
        # 6. 提取伏笔
        changes.extend(self._extract_foreshadowing(content, chapter))
        
        return changes
    
    def _extract_character_state_changes(self, content: str, chapter: int) -> List[StateChange]:
        """提取角色状态变化"""
        changes = []
        
        # 死亡模式
        death_patterns = [
            r"(\w+)死了",
            r"(\w+)倒下[了，]",
            r"(\w+)不再动弹",
            r"(\w+)停止了呼吸",
            r"(\w+)牺牲了",
        ]
        
        for pattern in death_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                changes.append(StateChange(
                    change_type=ChangeType.CHARACTER_STATUS,
                    entity_id=match,
                    entity_name=match,
                    old_value="alive",
                    new_value="dead",
                    description=f"{match}死亡",
                    chapter=chapter,
                ))
        
        # 受伤模式
        injury_patterns = [
            r"(\w+)受了伤",
            r"(\w+)被(\w+)伤",
            r"(\w+)的(\w+)被(\w+)",
        ]
        
        for pattern in injury_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    char_name = match[0]
                else:
                    char_name = match
                changes.append(StateChange(
                    change_type=ChangeType.CHARACTER_STATE,
                    entity_id=char_name,
                    entity_name=char_name,
                    old_value="healthy",
                    new_value="injured",
                    description=f"{char_name}受伤",
                    chapter=chapter,
                ))
        
        return changes
    
    def _extract_location_changes(self, content: str, chapter: int) -> List[StateChange]:
        """提取位置变化"""
        changes = []
        
        # 移动模式
        move_patterns = [
            r"(\w+)来到(\w+)",
            r"(\w+)到达(\w+)",
            r"(\w+)进入(\w+)",
            r"(\w+)离开(\w+)",
            r"(\w+)前往(\w+)",
        ]
        
        for pattern in move_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    char_name, location = match[0], match[1]
                    changes.append(StateChange(
                        change_type=ChangeType.CHARACTER_LOCATION,
                        entity_id=char_name,
                        entity_name=char_name,
                        new_value=location,
                        description=f"{char_name}移动到{location}",
                        chapter=chapter,
                    ))
        
        return changes
    
    def _extract_relationship_changes(self, content: str, chapter: int) -> List[StateChange]:
        """提取关系变化"""
        changes = []
        
        # 关系变化模式
        relationship_patterns = [
            (r"(\w+)和(\w+)成为(朋友|敌人|盟友)", "friend"),
            (r"(\w+)背叛了(\w+)", "enemy"),
            (r"(\w+)救了(\w+)", "ally"),
            (r"(\w+)和(\w+)确认了感情", "romance"),
            (r"(\w+)爱上了(\w+)", "romance"),
        ]
        
        for pattern, rel_type in relationship_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    char1, char2 = match[0], match[1]
                    changes.append(StateChange(
                        change_type=ChangeType.CHARACTER_RELATIONSHIP,
                        entity_id=f"{char1}-{char2}",
                        entity_name=f"{char1}和{char2}",
                        new_value=rel_type,
                        description=f"{char1}和{char2}关系变为{rel_type}",
                        chapter=chapter,
                    ))
        
        return changes
    
    def _extract_ability_changes(self, content: str, chapter: int) -> List[StateChange]:
        """提取能力变化"""
        changes = []
        
        # 能力觉醒模式
        ability_patterns = [
            r"(\w+)觉醒了(\w+)",
            r"(\w+)获得了(\w+)",
            r"(\w+)的能力(\w+)",
            r"(\w+)进化为(\w+)",
        ]
        
        for pattern in ability_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    char_name, ability = match[0], match[1]
                    changes.append(StateChange(
                        change_type=ChangeType.CHARACTER_ABILITY,
                        entity_id=char_name,
                        entity_name=char_name,
                        new_value=ability,
                        description=f"{char_name}获得能力{ability}",
                        chapter=chapter,
                    ))
        
        return changes
    
    def _extract_time_changes(self, content: str, chapter: int) -> List[StateChange]:
        """提取时间变化"""
        changes = []
        
        # 时间模式
        time_patterns = [
            r"(\d+)天后",
            r"(\d+)年后",
            r"第(\d+)天",
            r"过了(\w+)",
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                changes.append(StateChange(
                    change_type=ChangeType.TIME_PASSAGE,
                    entity_id="timeline",
                    entity_name="时间线",
                    new_value=match if isinstance(match, str) else str(match),
                    description=f"时间流逝: {match}",
                    chapter=chapter,
                ))
        
        return changes
    
    def _extract_foreshadowing(self, content: str, chapter: int) -> List[StateChange]:
        """提取伏笔"""
        changes = []
        
        # 伏笔模式（简化版，实际需要更复杂的逻辑）
        foreshadowing_patterns = [
            r"(\w+)想起(\w+)",
            r"(\w+)记得(\w+)",
            r"(\w+)发现(\w+)",
        ]
        
        for pattern in foreshadowing_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    char_name, hint = match[0], match[1]
                    changes.append(StateChange(
                        change_type=ChangeType.FORESHADOWING_PLANTED,
                        entity_id=f"hint_{chapter}_{len(changes)}",
                        entity_name=hint[:20],
                        description=f"伏笔: {char_name}想起/发现 {hint[:30]}",
                        chapter=chapter,
                        confidence=0.5,  # 伏笔检测置信度较低
                    ))
        
        return changes
    
    def save_changes(self, chapter: int, changes: List[StateChange]) -> None:
        """保存状态变化"""
        changes_data = []
        for change in changes:
            changes_data.append({
                "change_type": change.change_type.value,
                "entity_id": change.entity_id,
                "entity_name": change.entity_name,
                "old_value": change.old_value,
                "new_value": change.new_value,
                "description": change.description,
                "chapter": change.chapter,
                "confidence": change.confidence,
                "metadata": change.metadata,
            })
        
        path = f"memory/state_changes/chapter_{chapter:04d}.json"
        self.fs.write_json(path, changes_data)
    
    def load_changes(self, chapter: int) -> List[StateChange]:
        """加载状态变化"""
        path = f"memory/state_changes/chapter_{chapter:04d}.json"
        if not self.fs.exists(path):
            return []
        
        data = self.fs.read_json(path)
        changes = []
        for item in data:
            changes.append(StateChange(
                change_type=ChangeType(item["change_type"]),
                entity_id=item["entity_id"],
                entity_name=item["entity_name"],
                old_value=item.get("old_value"),
                new_value=item.get("new_value"),
                description=item.get("description", ""),
                chapter=item.get("chapter", 0),
                confidence=item.get("confidence", 1.0),
                metadata=item.get("metadata", {}),
            ))
        
        return changes
    
    def get_all_changes(self) -> List[StateChange]:
        """获取所有状态变化"""
        all_changes = []
        
        # 遍历所有章节的状态变化文件
        path = self.project_root / "memory" / "state_changes"
        if not path.exists():
            return all_changes
        
        for f in sorted(path.glob("chapter_*.json")):
            match = re.search(r"chapter_(\d+)", f.name)
            if match:
                chapter = int(match.group(1))
                all_changes.extend(self.load_changes(chapter))
        
        return all_changes
    
    def generate_change_report(self, chapter: int) -> str:
        """生成状态变化报告"""
        changes = self.load_changes(chapter)
        
        if not changes:
            return f"# 第{chapter}章状态变化报告\n\n无状态变化"
        
        lines = [
            f"# 第{chapter}章状态变化报告",
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
                lines.append(f"- {change.description}")
                if change.old_value and change.new_value:
                    lines.append(f"  - {change.old_value} → {change.new_value}")
            lines.append("")
        
        return "\n".join(lines)
