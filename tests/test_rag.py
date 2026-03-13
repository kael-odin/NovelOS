import pytest
from pathlib import Path
from app.services.rag_service import RAGService


class TestRAGService:
    def test_init_db(self, tmp_path):
        rag = RAGService(tmp_path)
        assert (tmp_path / ".novelos" / "vectors.db").exists()
    
    def test_index_chapter(self, tmp_path):
        rag = RAGService(tmp_path)
        content = "林墨站在青云宗外门广场上，心中满是苦涩。考核失败的结果如同一记重锤，狠狠砸在他的心头。"
        chunk_id = rag.index_chapter(1, content, "scene")
        assert chunk_id == "ch0001_scene"
    
    def test_index_summary(self, tmp_path):
        rag = RAGService(tmp_path)
        summary = "第一章：林墨考核失败，被分配为杂役，但玉佩首次异动。"
        chunk_id = rag.index_summary(1, summary)
        assert chunk_id == "ch0001_summary"
    
    def test_bm25_search(self, tmp_path):
        rag = RAGService(tmp_path)
        
        rag.index_chapter(1, "林墨站在青云宗外门广场上，心中满是苦涩。", "scene")
        rag.index_chapter(2, "苏瑶从内门走来，目光冷淡地扫过林墨。", "scene")
        rag.index_summary(1, "林墨考核失败，被分配为杂役。")
        
        results = rag.bm25_search("林墨", top_k=3)
        assert len(results) >= 1
        assert any("林墨" in r.content for r in results)
    
    def test_search(self, tmp_path):
        rag = RAGService(tmp_path)
        
        rag.index_chapter(1, "林墨站在青云宗外门广场上。", "scene")
        rag.index_chapter(2, "苏瑶从内门走来。", "scene")
        
        results = rag.search("林墨", top_k=5)
        assert len(results) >= 1
    
    def test_get_context_for_chapter(self, tmp_path):
        rag = RAGService(tmp_path)
        
        rag.index_summary(1, "第一章摘要：林墨入宗失败。")
        rag.index_summary(2, "第二章摘要：林墨开始杂役生活。")
        rag.index_summary(3, "第三章摘要：玉佩异动。")
        
        context = rag.get_context_for_chapter(4, window=3)
        assert context["chapter"] == 4
        assert len(context["recent_summaries"]) >= 1
    
    def test_get_stats(self, tmp_path):
        rag = RAGService(tmp_path)
        
        rag.index_chapter(1, "测试内容一", "scene")
        rag.index_chapter(2, "测试内容二", "scene")
        
        stats = rag.get_stats()
        assert stats["total_chunks"] == 2
        assert stats["max_chapter"] == 2
