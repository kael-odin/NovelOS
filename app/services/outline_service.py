from pathlib import Path
from typing import Optional, List, Dict, Any
from .file_service import FileService


class OutlineService:
    def __init__(self, file_service: FileService):
        self.fs = file_service
    
    def get_book_outline(self) -> str:
        return self.fs.read_text("project/outlines/book_outline.md")
    
    def save_book_outline(self, content: str) -> None:
        self.fs.write_text("project/outlines/book_outline.md", content)
    
    def get_volume_outline(self, volume: int) -> str:
        return self.fs.read_text(f"project/outlines/volume_{volume:02d}.md")
    
    def save_volume_outline(self, volume: int, content: str) -> None:
        self.fs.write_text(f"project/outlines/volume_{volume:02d}.md", content)
    
    def get_chapter_plan(self, chapter: int) -> str:
        return self.fs.read_text(f"project/outlines/chapter_plans/chapter_{chapter:04d}.md")
    
    def save_chapter_plan(self, chapter: int, content: str) -> None:
        self.fs.write_text(f"project/outlines/chapter_plans/chapter_{chapter:04d}.md", content)
    
    def list_chapter_plans(self) -> List[int]:
        chapters = []
        for path in self.fs.list_files("project/outlines/chapter_plans", "chapter_*.md"):
            filename = path.stem
            try:
                chapter_num = int(filename.split("_")[1])
                chapters.append(chapter_num)
            except (IndexError, ValueError):
                continue
        return sorted(chapters)
    
    def get_next_unplanned_chapter(self, target_chapters: int) -> Optional[int]:
        planned = set(self.list_chapter_plans())
        for ch in range(1, target_chapters + 1):
            if ch not in planned:
                return ch
        return None
