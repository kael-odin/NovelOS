import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime


class FileService:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        dirs = [
            "project/story_bible",
            "project/outlines/chapter_plans",
            "project/chapters/drafts",
            "project/chapters/revised",
            "project/chapters/final",
            "project/memory/chapter_summaries",
            "project/memory/context",
            "project/reviews",
            "project/tasks/queue",
            "project/tasks/doing",
            "project/tasks/done",
            "project/tasks/failed",
            ".novelos",
        ]
        for d in dirs:
            (self.project_root / d).mkdir(parents=True, exist_ok=True)
    
    def read_yaml(self, path: Union[str, Path]) -> Dict[str, Any]:
        full_path = self.project_root / path
        if not full_path.exists():
            return {}
        with open(full_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    def write_yaml(self, path: Union[str, Path], data: Dict[str, Any]) -> None:
        full_path = self.project_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def read_json(self, path: Union[str, Path]) -> Dict[str, Any]:
        full_path = self.project_root / path
        if not full_path.exists():
            return {}
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def write_json(self, path: Union[str, Path], data: Dict[str, Any]) -> None:
        full_path = self.project_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def read_text(self, path: Union[str, Path]) -> str:
        full_path = self.project_root / path
        if not full_path.exists():
            return ""
        return full_path.read_text(encoding="utf-8")
    
    def write_text(self, path: Union[str, Path], content: str) -> None:
        full_path = self.project_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
    
    def exists(self, path: Union[str, Path]) -> bool:
        return (self.project_root / path).exists()
    
    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> list[Path]:
        dir_path = self.project_root / directory
        if not dir_path.exists():
            return []
        return sorted(dir_path.glob(pattern))
    
    def delete(self, path: Union[str, Path]) -> bool:
        full_path = self.project_root / path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    def backup(self, path: Union[str, Path], suffix: Optional[str] = None) -> Optional[Path]:
        full_path = self.project_root / path
        if not full_path.exists():
            return None
        suffix = suffix or datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = full_path.with_suffix(f".{suffix}.bak")
        backup_path.write_text(full_path.read_text(encoding="utf-8"), encoding="utf-8")
        return backup_path
