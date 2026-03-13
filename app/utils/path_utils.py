from pathlib import Path
from typing import Optional, List


def ensure_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_project_root(start: Optional[Path] = None) -> Optional[Path]:
    if start is None:
        start = Path.cwd()
    
    current = Path(start).resolve()
    
    while current != current.parent:
        if (current / "novel.yaml").exists():
            return current
        if (current / ".novelos").exists():
            return current
        current = current.parent
    
    return None


def get_chapter_path(chapter: int, status: str = "drafts") -> str:
    return f"project/chapters/{status}/chapter_{chapter:04d}.md"


def get_context_path(chapter: int) -> str:
    return f"project/memory/context/chapter_{chapter:04d}_context.md"


def get_summary_path(chapter: int) -> str:
    return f"project/memory/chapter_summaries/chapter_{chapter:04d}.md"


def get_review_path(chapter: int, review_type: str) -> str:
    return f"project/reviews/{review_type}_chapter_{chapter:04d}.json"


def get_task_path(task_id: str, status: str = "queue") -> str:
    return f"project/tasks/{status}/{task_id}.json"


def get_chapter_plan_path(chapter: int) -> str:
    return f"project/outlines/chapter_plans/chapter_{chapter:04d}.md"


def normalize_path(path: str) -> str:
    return str(Path(path).as_posix())


def is_valid_chapter_number(chapter: int, max_chapters: int = 10000) -> bool:
    return 1 <= chapter <= max_chapters


def list_chapter_files(directory: str, project_root: Path) -> List[int]:
    chapters = []
    dir_path = project_root / directory
    
    if not dir_path.exists():
        return chapters
    
    for path in dir_path.glob("chapter_*.md"):
        try:
            chapter_num = int(path.stem.split("_")[1])
            chapters.append(chapter_num)
        except (IndexError, ValueError):
            continue
    
    return sorted(chapters)
