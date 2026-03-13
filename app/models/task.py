from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    QUEUED = "queued"
    DOING = "doing"
    DRAFTED = "drafted"
    REVIEWED = "reviewed"
    REVISING = "revising"
    APPROVED = "approved"
    FINALIZED = "finalized"
    FAILED = "failed"


class TaskType(str, Enum):
    PLAN_BOOK = "plan_book"
    PLAN_VOLUME = "plan_volume"
    PLAN_CHAPTER = "plan_chapter"
    BUILD_CONTEXT = "build_context"
    GENERATE_CHAPTER = "generate_chapter"
    REVIEW_CONSISTENCY = "review_consistency"
    REVIEW_PACING = "review_pacing"
    REVIEW_PROSE = "review_prose"
    REVIEW_READER = "review_reader"
    MERGE_REVIEWS = "merge_reviews"
    REVISE_CHAPTER = "revise_chapter"
    SUMMARIZE_CHAPTER = "summarize_chapter"
    EXTRACT_CHANGES = "extract_changes"
    UPDATE_BIBLE = "update_bible"
    COMPILE_VOLUME = "compile_volume"
    COMPILE_BOOK = "compile_book"


class Task(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    task_id: str = Field(..., description="任务唯一标识")
    type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(default=TaskStatus.QUEUED, description="任务状态")
    chapter: Optional[int] = Field(default=None, description="关联章节号")
    volume: Optional[int] = Field(default=None, description="关联卷号")
    
    inputs: Dict[str, str] = Field(default_factory=dict, description="输入文件路径")
    outputs: Dict[str, str] = Field(default_factory=dict, description="输出文件路径")
    
    constraints: Dict[str, Any] = Field(default_factory=dict, description="约束条件")
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")
    started_at: Optional[str] = Field(default=None, description="开始时间")
    completed_at: Optional[str] = Field(default=None, description="完成时间")
    
    error_message: Optional[str] = Field(default=None, description="错误信息")
    retry_count: int = Field(default=0, description="重试次数")
