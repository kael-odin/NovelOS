import pytest
from pathlib import Path
from app.models import Task, TaskStatus, TaskType, Character, StoryBible
from app.services.file_service import FileService


class TestTaskModel:
    def test_task_creation(self, tmp_path):
        task = Task(
            task_id="test_001",
            type=TaskType.GENERATE_CHAPTER,
            chapter=1,
        )
        assert task.task_id == "test_001"
        assert task.status == TaskStatus.QUEUED
        assert task.chapter == 1

    def test_task_status_values(self):
        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.DOING.value == "doing"
        assert TaskStatus.FINALIZED.value == "finalized"


class TestFileService:
    def test_ensure_dirs(self, tmp_path):
        fs = FileService(tmp_path)
        assert (tmp_path / "project" / "story_bible").exists()
        assert (tmp_path / "project" / "chapters" / "drafts").exists()

    def test_write_and_read_yaml(self, tmp_path):
        fs = FileService(tmp_path)
        data = {"test": "value", "nested": {"key": 123}}
        fs.write_yaml("test.yaml", data)
        result = fs.read_yaml("test.yaml")
        assert result == data

    def test_write_and_read_json(self, tmp_path):
        fs = FileService(tmp_path)
        data = {"test": "value", "list": [1, 2, 3]}
        fs.write_json("test.json", data)
        result = fs.read_json("test.json")
        assert result == data

    def test_write_and_read_text(self, tmp_path):
        fs = FileService(tmp_path)
        content = "# Test Content\n\nThis is a test."
        fs.write_text("test.md", content)
        result = fs.read_text("test.md")
        assert result == content
    
    def test_exists(self, tmp_path):
        fs = FileService(tmp_path)
        assert not fs.exists("nonexistent.yaml")
        fs.write_text("test.md", "content")
        assert fs.exists("test.md")
    
    def test_list_files(self, tmp_path):
        fs = FileService(tmp_path)
        fs.write_text("test1.md", "content1")
        fs.write_text("test2.md", "content2")
        files = list(fs.list_files(".", "*.md"))
        assert len(files) == 2


class TestStoryBible:
    def test_story_bible_creation(self):
        bible = StoryBible(
            project_name="Test Novel",
            genre=["玄幻"],
        )
        assert bible.project_name == "Test Novel"
        assert "玄幻" in bible.genre

    def test_character_model(self):
        char = Character(
            id="char_001",
            name="Test Character",
            role="protagonist",
        )
        assert char.id == "char_001"
        assert char.name == "Test Character"
        assert char.role == "protagonist"
    
    def test_get_character(self):
        char = Character(id="char_001", name="Test", role="protagonist")
        bible = StoryBible(characters=[char])
        result = bible.get_character("char_001")
        assert result is not None
        assert result.name == "Test"
    
    def test_get_active_foreshadowings(self):
        from app.models.story_bible import Foreshadowing
        
        f1 = Foreshadowing(id="f1", title="Test 1", planted_at=1, status="active")
        f2 = Foreshadowing(id="f2", title="Test 2", planted_at=2, status="resolved")
        bible = StoryBible(foreshadowings=[f1, f2])
        
        active = bible.get_active_foreshadowings()
        assert len(active) == 1
        assert active[0].id == "f1"


class TestTaskService:
    def test_create_task(self, tmp_path):
        fs = FileService(tmp_path)
        from app.services.task_service import TaskService
        
        ts = TaskService(fs)
        task = Task(
            task_id="gen_001",
            type=TaskType.GENERATE_CHAPTER,
            chapter=1,
        )
        created = ts.create_task(task)
        assert created.status == TaskStatus.QUEUED

    def test_list_tasks(self, tmp_path):
        fs = FileService(tmp_path)
        from app.services.task_service import TaskService
        
        ts = TaskService(fs)
        task = Task(
            task_id="gen_002",
            type=TaskType.GENERATE_CHAPTER,
            chapter=2,
        )
        ts.create_task(task)
        
        tasks = ts.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].task_id == "gen_002"


class TestBibleService:
    def test_load_bible(self, tmp_path):
        fs = FileService(tmp_path)
        from app.services.bible_service import BibleService
        
        bs = BibleService(fs)
        bible = bs.load_bible()
        assert bible is not None
    
    def test_save_bible(self, tmp_path):
        fs = FileService(tmp_path)
        from app.services.bible_service import BibleService
        
        bs = BibleService(fs)
        bible = StoryBible(project_name="Test", genre=["玄幻"])
        bs.save_bible(bible)
        
        loaded = bs.load_bible()
        assert loaded.project_name == "Test"
