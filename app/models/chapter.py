from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class Scene(BaseModel):
    scene_index: int = Field(..., description="场景序号")
    start_line: Optional[int] = Field(default=None, description="起始行号")
    end_line: Optional[int] = Field(default=None, description="结束行号")
    location: str = Field(default="", description="场景地点")
    summary: str = Field(default="", description="场景摘要")
    characters: List[str] = Field(default_factory=list, description="出场角色")
    emotion_tag: str = Field(default="", description="情绪标签")


class ChapterMeta(BaseModel):
    chapter: int = Field(..., description="章节号")
    title: str = Field(default="", description="章节标题")
    location: str = Field(default="", description="主要地点")
    word_count: int = Field(default=0, description="字数")
    characters: List[str] = Field(default_factory=list, description="出场角色")
    summary: str = Field(default="", description="章节摘要")
    hook_type: str = Field(default="", description="章末钩子类型")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Chapter(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "meta": {
                "chapter": 1,
                "title": "第一章 少年林墨",
                "location": "青云宗外门",
                "word_count": 3500,
                "characters": ["林墨", "陈锋"],
                "summary": "林墨入宗失败后被留作杂役..."
            },
            "content": "# 第一章 少年林墨\n\n...",
            "scenes": []
        }
    })
    
    meta: ChapterMeta = Field(..., description="章节元数据")
    content: str = Field(default="", description="章节正文")
    scenes: List[Scene] = Field(default_factory=list, description="场景列表")
    notes: List[str] = Field(default_factory=list, description="备注")
