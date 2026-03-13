from pathlib import Path
from typing import Optional, List, Dict, Any
from .file_service import FileService
from ..models.review import Review, ReviewType, ReviewIssue, Severity


class ReviewService:
    def __init__(self, file_service: FileService):
        self.fs = file_service
    
    def save_review(self, review: Review) -> None:
        path = f"project/reviews/{review.review_type}_chapter_{review.chapter:04d}.json"
        self.fs.write_json(path, review.model_dump())
    
    def load_review(self, chapter: int, review_type: ReviewType) -> Optional[Review]:
        path = f"project/reviews/{review_type.value}_chapter_{chapter:04d}.json"
        if not self.fs.exists(path):
            return None
        data = self.fs.read_json(path)
        return Review(**data)
    
    def list_reviews(self, chapter: int) -> List[Review]:
        reviews = []
        for rt in ReviewType:
            review = self.load_review(chapter, rt)
            if review:
                reviews.append(review)
        return reviews
    
    def merge_reviews(self, chapter: int) -> Dict[str, Any]:
        reviews = self.list_reviews(chapter)
        
        all_issues = []
        for r in reviews:
            all_issues.extend(r.issues)
        
        all_issues.sort(key=lambda x: {
            Severity.CRITICAL: 0,
            Severity.MAJOR: 1,
            Severity.MINOR: 2,
            Severity.SUGGESTION: 3,
        }.get(Severity(x.severity), 4))
        
        avg_score = sum(r.overall_score for r in reviews) / len(reviews) if reviews else 0
        
        return {
            "chapter": chapter,
            "overall_score": round(avg_score, 2),
            "total_issues": len(all_issues),
            "critical_count": len([i for i in all_issues if i.severity == Severity.CRITICAL]),
            "major_count": len([i for i in all_issues if i.severity == Severity.MAJOR]),
            "issues": [i.model_dump() for i in all_issues],
            "reviews": [r.model_dump() for r in reviews],
        }
    
    def save_merged_review(self, chapter: int, merged: Dict[str, Any]) -> None:
        path = f"project/reviews/merged_chapter_{chapter:04d}.json"
        self.fs.write_json(path, merged)
    
    def load_merged_review(self, chapter: int) -> Optional[Dict[str, Any]]:
        path = f"project/reviews/merged_chapter_{chapter:04d}.json"
        if not self.fs.exists(path):
            return None
        return self.fs.read_json(path)
    
    def has_critical_issues(self, chapter: int) -> bool:
        merged = self.load_merged_review(chapter)
        if not merged:
            return False
        return merged.get("critical_count", 0) > 0
    
    def get_review_summary(self, chapter: int) -> str:
        merged = self.load_merged_review(chapter)
        if not merged:
            return "未找到评审记录"
        
        lines = [
            f"# 第{chapter}章评审汇总",
            "",
            f"- 总体评分：{merged['overall_score']}/10",
            f"- 问题总数：{merged['total_issues']}",
            f"- 严重问题：{merged['critical_count']}",
            f"- 重要问题：{merged['major_count']}",
            "",
            "## 问题列表",
            "",
        ]
        
        for issue in merged.get("issues", [])[:10]:
            lines.append(f"- [{issue['severity']}] {issue['category']}: {issue['description']}")
            if issue.get("suggestion"):
                lines.append(f"  - 建议：{issue['suggestion']}")
        
        return "\n".join(lines)
