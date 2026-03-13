from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewType(str, Enum):
    CONSISTENCY = "consistency"
    PACING = "pacing"
    PROSE = "prose"
    READER = "reader"
    FORESHADOWING = "foreshadowing"


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


class ReviewIssue(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    issue_id: str = Field(..., description="问题ID")
    severity: Severity = Field(..., description="严重程度")
    category: str = Field(..., description="问题类别")
    location: str = Field(default="", description="问题位置（原文片段或行号）")
    description: str = Field(..., description="问题描述")
    reason: str = Field(default="", description="问题原因")
    suggestion: str = Field(default="", description="修改建议")


class Review(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    review_id: str = Field(..., description="评审ID")
    review_type: ReviewType = Field(..., description="评审类型")
    chapter: int = Field(..., description="章节号")
    
    overall_score: float = Field(default=0.0, ge=0, le=10, description="总体评分")
    issues: List[ReviewIssue] = Field(default_factory=list, description="问题列表")
    
    summary: str = Field(default="", description="评审总结")
    highlights: List[str] = Field(default_factory=list, description="亮点")
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def get_critical_issues(self) -> List[ReviewIssue]:
        return [i for i in self.issues if i.severity == Severity.CRITICAL]
    
    def get_major_issues(self) -> List[ReviewIssue]:
        return [i for i in self.issues if i.severity == Severity.MAJOR]
