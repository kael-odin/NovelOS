from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from .file_service import FileService
from .review_service import ReviewService


class RevisionService:
    def __init__(self, file_service: FileService, review_service: ReviewService):
        self.fs = file_service
        self.review = review_service
    
    def get_chapter_draft(self, chapter: int) -> Optional[str]:
        path = f"project/chapters/drafts/chapter_{chapter:04d}.md"
        return self.fs.read_text(path) or None
    
    def save_revised_chapter(self, chapter: int, content: str) -> None:
        path = f"project/chapters/revised/chapter_{chapter:04d}.md"
        self.fs.write_text(path, content)
    
    def finalize_chapter(self, chapter: int) -> None:
        revised_path = f"project/chapters/revised/chapter_{chapter:04d}.md"
        final_path = f"project/chapters/final/chapter_{chapter:04d}.md"
        
        if self.fs.exists(revised_path):
            content = self.fs.read_text(revised_path)
            self.fs.write_text(final_path, content)
    
    def create_revision_task(self, chapter: int) -> Dict[str, Any]:
        merged = self.review.load_merged_review(chapter)
        if not merged:
            return {"error": "未找到评审记录"}
        
        draft = self.get_chapter_draft(chapter)
        if not draft:
            return {"error": "未找到草稿"}
        
        return {
            "chapter": chapter,
            "draft_path": f"project/chapters/drafts/chapter_{chapter:04d}.md",
            "output_path": f"project/chapters/revised/chapter_{chapter:04d}.md",
            "issues": merged.get("issues", []),
            "preserve_points": self._extract_preserve_points(draft, merged),
        }
    
    def _extract_preserve_points(self, draft: str, merged: Dict[str, Any]) -> List[str]:
        preserve = []
        highlights = merged.get("reviews", [])
        for r in highlights:
            for h in r.get("highlights", []):
                preserve.append(h)
        return preserve
    
    def apply_revision(self, chapter: int, revised_content: str, notes: str = "") -> None:
        self.save_revised_chapter(chapter, revised_content)
        
        revision_log = {
            "chapter": chapter,
            "revised_at": datetime.now().isoformat(),
            "notes": notes,
        }
        path = f"project/chapters/revised/chapter_{chapter:04d}_revision_log.json"
        self.fs.write_json(path, revision_log)
    
    def needs_revision(self, chapter: int) -> bool:
        merged = self.review.load_merged_review(chapter)
        if not merged:
            return False
        return merged.get("critical_count", 0) > 0 or merged.get("overall_score", 10) < 7.5
