import pytest
from pathlib import Path
from app.services import FileService, ContextService, BibleService
from app.models import StoryBible, Character


class TestContextService:
    def test_build_context(self, tmp_path):
        fs = FileService(tmp_path)
        bible = BibleService(fs)
        context = ContextService(fs, bible)
        
        ctx = context.build_context(1)
        assert ctx["meta"]["chapter"] == 1
        assert "writing_goal" in ctx
        assert "character_states" in ctx
    
    def test_save_and_load_context(self, tmp_path):
        fs = FileService(tmp_path)
        bible = BibleService(fs)
        context = ContextService(fs, bible)
        
        ctx = context.build_context(1)
        context.save_context(1, ctx)
        
        loaded = context.load_context(1)
        assert loaded is not None
        assert loaded["chapter"] == 1
    
    def test_context_with_story_bible(self, tmp_path):
        fs = FileService(tmp_path)
        bible = BibleService(fs)
        
        char = Character(
            id="char_test",
            name="测试角色",
            role="protagonist",
            current_state={"realm": "炼气一层", "location": "测试地点"}
        )
        sb = StoryBible(
            project_name="测试项目",
            characters=[char]
        )
        bible.save_bible(sb)
        
        context = ContextService(fs, bible)
        ctx = context.build_context(1)
        
        assert len(ctx["character_states"]) == 1
        assert ctx["character_states"][0]["name"] == "测试角色"


class TestReviewService:
    def test_merge_empty_reviews(self, tmp_path):
        from app.services import ReviewService
        
        fs = FileService(tmp_path)
        review = ReviewService(fs)
        
        merged = review.merge_reviews(1)
        assert merged["total_issues"] == 0
    
    def test_save_and_load_review(self, tmp_path):
        from app.services import ReviewService
        from app.models import Review, ReviewType
        
        fs = FileService(tmp_path)
        review_svc = ReviewService(fs)
        
        review = Review(
            review_id="test_review_001",
            review_type=ReviewType.CONSISTENCY,
            chapter=1,
            overall_score=8.5,
            summary="测试评审"
        )
        review_svc.save_review(review)
        
        loaded = review_svc.load_review(1, ReviewType.CONSISTENCY)
        assert loaded is not None
        assert loaded.overall_score == 8.5


class TestRevisionService:
    def test_get_chapter_draft(self, tmp_path):
        from app.services import RevisionService, ReviewService
        
        fs = FileService(tmp_path)
        review_svc = ReviewService(fs)
        revision = RevisionService(fs, review_svc)
        
        draft = revision.get_chapter_draft(1)
        assert draft is None
    
    def test_save_revised_chapter(self, tmp_path):
        from app.services import RevisionService, ReviewService
        
        fs = FileService(tmp_path)
        review_svc = ReviewService(fs)
        revision = RevisionService(fs, review_svc)
        
        content = "# 第一章\n\n这是修订后的内容。"
        revision.save_revised_chapter(1, content)
        
        fs.read_text("project/chapters/revised/chapter_0001.md") == content
