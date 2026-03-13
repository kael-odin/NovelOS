from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class Character(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "char_linmo",
            "name": "林墨",
            "role": "protagonist",
            "gender": "male",
            "age_start": 16,
            "personality_core": ["隐忍", "重情", "倔强"],
            "flaws": ["不愿轻易求助"],
            "growth_arc": "从边缘少年成长为真正能承担责任的人",
            "current_state": {
                "realm": "炼气九层",
                "location": "青云宗外门",
                "emotion": "压抑但有韧劲"
            }
        }
    })
    
    id: str = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    role: str = Field(default="supporting", description="角色类型: protagonist/heroine/antagonist/supporting")
    gender: Optional[str] = Field(default=None, description="性别")
    age_start: Optional[int] = Field(default=None, description="初始年龄")
    
    personality_core: List[str] = Field(default_factory=list, description="核心性格")
    flaws: List[str] = Field(default_factory=list, description="性格缺陷")
    growth_arc: str = Field(default="", description="成长弧线")
    
    speech_style: Dict[str, Any] = Field(default_factory=dict, description="说话风格")
    secrets: List[str] = Field(default_factory=list, description="秘密")
    
    current_state: Dict[str, Any] = Field(default_factory=dict, description="当前状态")
    first_appearance: int = Field(default=0, description="首次出场章节")
    status: str = Field(default="alive", description="状态: alive/dead/missing")


class Foreshadowing(BaseModel):
    id: str = Field(..., description="伏笔ID")
    title: str = Field(..., description="伏笔标题")
    planted_at: int = Field(..., description="埋下章节")
    description: str = Field(default="", description="伏笔描述")
    thread_type: str = Field(default="subplot", description="主线类型: main_mystery/subplot/identity")
    importance: str = Field(default="medium", description="重要程度: high/medium/low")
    status: str = Field(default="active", description="状态: active/resolved/abandoned")
    
    hints: List[Dict[str, Any]] = Field(default_factory=list, description="提示记录")
    planned_resolution: Dict[str, Any] = Field(default_factory=dict, description="计划收束")


class Timeline(BaseModel):
    chapter: int = Field(..., description="章节号")
    date_marker: str = Field(default="", description="时间标记")
    event: str = Field(default="", description="事件描述")


class Relationship(BaseModel):
    source: str = Field(..., description="源角色ID")
    target: str = Field(..., description="目标角色ID")
    type: str = Field(..., description="关系类型")
    current_status: str = Field(default="", description="当前状态")
    arc: str = Field(default="", description="关系弧线")
    latest_update_chapter: int = Field(default=0, description="最近更新章节")


class World(BaseModel):
    name: str = Field(default="", description="世界名称")
    core_rules: List[str] = Field(default_factory=list, description="核心规则")
    power_system: Dict[str, Any] = Field(default_factory=dict, description="力量体系")
    factions: List[Dict[str, Any]] = Field(default_factory=list, description="势力")
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="地点")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="物品")
    mysteries: List[Dict[str, Any]] = Field(default_factory=list, description="谜团")


class StoryBible(BaseModel):
    project_name: str = Field(default="", description="项目名称")
    genre: List[str] = Field(default_factory=list, description="题材")
    
    world: World = Field(default_factory=World, description="世界观")
    characters: List[Character] = Field(default_factory=list, description="角色")
    relationships: List[Relationship] = Field(default_factory=list, description="关系")
    foreshadowings: List[Foreshadowing] = Field(default_factory=list, description="伏笔")
    timeline: List[Timeline] = Field(default_factory=list, description="时间线")
    themes: List[str] = Field(default_factory=list, description="主题")
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def get_character(self, char_id: str) -> Optional[Character]:
        for c in self.characters:
            if c.id == char_id:
                return c
        return None
    
    def get_active_foreshadowings(self) -> List[Foreshadowing]:
        return [f for f in self.foreshadowings if f.status == "active"]
