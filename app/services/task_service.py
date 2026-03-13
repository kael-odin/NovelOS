from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from .file_service import FileService
from ..models.task import Task, TaskStatus, TaskType


class TaskService:
    def __init__(self, file_service: FileService):
        self.fs = file_service
    
    def _get_task_path(self, task: Task) -> str:
        status_dir = {
            TaskStatus.QUEUED: "queue",
            TaskStatus.DOING: "doing",
            TaskStatus.DRAFTED: "doing",
            TaskStatus.REVIEWED: "doing",
            TaskStatus.REVISING: "doing",
            TaskStatus.APPROVED: "done",
            TaskStatus.FINALIZED: "done",
            TaskStatus.FAILED: "failed",
        }
        return f"project/tasks/{status_dir.get(task.status, 'queue')}/{task.task_id}.json"
    
    def create_task(self, task: Task) -> Task:
        task.created_at = datetime.now().isoformat()
        task.status = TaskStatus.QUEUED
        self.fs.write_json(self._get_task_path(task), task.model_dump())
        return task
    
    def save_task(self, task: Task) -> None:
        """保存任务（创建或更新）"""
        self.fs.write_json(self._get_task_path(task), task.model_dump())
    
    def load_task(self, task_id: str) -> Optional[Task]:
        for status_dir in ["queue", "doing", "done", "failed"]:
            path = f"project/tasks/{status_dir}/{task_id}.json"
            if self.fs.exists(path):
                data = self.fs.read_json(path)
                return Task(**data)
        return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务（load_task的别名）"""
        return self.load_task(task_id)
    
    def update_task(self, task: Task) -> None:
        old_task = self.load_task(task.task_id)
        if old_task:
            old_path = self._get_task_path(old_task)
            if self.fs.exists(old_path):
                self.fs.delete(old_path)
        
        self.fs.write_json(self._get_task_path(task), task.model_dump())
    
    def move_task(self, task_id: str, new_status: TaskStatus) -> Optional[Task]:
        task = self.load_task(task_id)
        if not task:
            return None
        
        old_path = self._get_task_path(task)
        task.status = new_status
        
        if new_status == TaskStatus.DOING and not task.started_at:
            task.started_at = datetime.now().isoformat()
        elif new_status in [TaskStatus.FINALIZED, TaskStatus.FAILED]:
            task.completed_at = datetime.now().isoformat()
        
        if self.fs.exists(old_path):
            self.fs.delete(old_path)
        
        self.fs.write_json(self._get_task_path(task), task.model_dump())
        return task
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        tasks = []
        for status_dir in ["queue", "doing", "done", "failed"]:
            for path in self.fs.list_files(f"project/tasks/{status_dir}", "*.json"):
                data = self.fs.read_json(path)
                task = Task(**data)
                if status is None or task.status == status:
                    tasks.append(task)
        return sorted(tasks, key=lambda t: t.created_at)
    
    def get_next_task(self) -> Optional[Task]:
        tasks = self.list_tasks(TaskStatus.QUEUED)
        return tasks[0] if tasks else None
    
    def get_chapter_tasks(self, chapter: int) -> List[Task]:
        return [t for t in self.list_tasks() if t.chapter == chapter]
    
    def create_chapter_generation_task(self, chapter: int) -> Task:
        task = Task(
            task_id=f"gen_chapter_{chapter:04d}",
            type=TaskType.GENERATE_CHAPTER,
            chapter=chapter,
            inputs={
                "chapter_plan": f"project/outlines/chapter_plans/chapter_{chapter:04d}.md",
                "context_bundle": f"project/memory/context/chapter_{chapter:04d}_context.md",
            },
            outputs={
                "draft": f"project/chapters/drafts/chapter_{chapter:04d}.md",
            },
            constraints={
                "target_words_min": 2500,
                "target_words_max": 5000,
                "must_have_hook": True,
            },
        )
        return self.create_task(task)
    
    def create_review_task(self, chapter: int, review_type: TaskType = TaskType.REVIEW_CONSISTENCY) -> Task:
        task = Task(
            task_id=f"{review_type.value}_chapter_{chapter:04d}",
            type=review_type,
            chapter=chapter,
            inputs={
                "chapter": f"project/chapters/drafts/chapter_{chapter:04d}.md",
            },
            outputs={
                "review": f"project/reviews/{review_type.value}_chapter_{chapter:04d}.json",
            },
        )
        return self.create_task(task)
