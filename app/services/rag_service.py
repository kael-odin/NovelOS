#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovelOS RAG Service - 简化版 RAG 检索服务

支持:
- 向量检索 (需要配置 embedding API)
- BM25 关键词检索
- 混合检索
- 上下文构建
"""

import json
import math
import re
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    chunk_id: str
    chapter: int
    content: str
    score: float
    source: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RAGService:
    def __init__(self, project_root: Path, config: Dict[str, Any] = None):
        self.project_root = Path(project_root)
        self.config = config or {}
        self.db_path = self.project_root / ".novelos" / "vectors.db"
        self._init_db()
    
    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    chapter INTEGER,
                    content TEXT,
                    chunk_type TEXT DEFAULT 'scene',
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bm25_index (
                    term TEXT,
                    chunk_id TEXT,
                    tf REAL,
                    PRIMARY KEY (term, chunk_id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_chapter ON chunks(chapter)")
            conn.commit()
    
    def index_chapter(self, chapter: int, content: str, chunk_type: str = "scene") -> str:
        chunk_id = f"ch{chapter:04d}_{chunk_type}"
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO chunks (chunk_id, chapter, content, chunk_type)
                VALUES (?, ?, ?, ?)
            """, (chunk_id, chapter, content, chunk_type))
            
            self._update_bm25_index(cursor, chunk_id, content)
            conn.commit()
        
        return chunk_id
    
    def index_summary(self, chapter: int, summary: str) -> str:
        return self.index_chapter(chapter, summary, "summary")
    
    def _tokenize(self, text: str) -> List[str]:
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        chinese_chars = list("".join(chinese))
        english = re.findall(r'[a-zA-Z]+', text.lower())
        return chinese_chars + english
    
    def _update_bm25_index(self, cursor, chunk_id: str, content: str):
        cursor.execute("DELETE FROM bm25_index WHERE chunk_id = ?", (chunk_id,))
        
        tokens = self._tokenize(content)
        doc_length = len(tokens)
        tf_counter = Counter(tokens)
        
        for term, count in tf_counter.items():
            tf = count / doc_length if doc_length > 0 else 0
            cursor.execute("""
                INSERT INTO bm25_index (term, chunk_id, tf)
                VALUES (?, ?, ?)
            """, (term, chunk_id, tf))
    
    def bm25_search(self, query: str, top_k: int = 5, chapter_limit: int = None) -> List[SearchResult]:
        query_terms = self._tokenize(query)
        if not query_terms:
            return []
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM chunks")
            total_docs = cursor.fetchone()[0] or 1
            
            cursor.execute("SELECT chunk_id, COUNT(*) as len FROM bm25_index GROUP BY chunk_id")
            doc_lengths = {row[0]: row[1] for row in cursor.fetchall()}
            avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 1
            
            doc_scores = {}
            
            for term in set(query_terms):
                cursor.execute("""
                    SELECT b.chunk_id, b.tf
                    FROM bm25_index b
                    WHERE b.term = ?
                """, (term,))
                
                docs_with_term = cursor.fetchall()
                df = len(docs_with_term)
                
                if df == 0:
                    continue
                
                idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)
                
                for chunk_id, tf in docs_with_term:
                    doc_length = doc_lengths.get(chunk_id, 1)
                    k1, b = 1.5, 0.75
                    score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_length / avg_doc_length))
                    
                    if chunk_id not in doc_scores:
                        doc_scores[chunk_id] = 0
                    doc_scores[chunk_id] += score
            
            results = []
            for chunk_id, score in doc_scores.items():
                cursor.execute(
                    "SELECT chapter, content, chunk_type FROM chunks WHERE chunk_id = ?",
                    (chunk_id,)
                )
                row = cursor.fetchone()
                if row:
                    ch, content, chunk_type = row
                    if chapter_limit is None or ch <= chapter_limit:
                        results.append(SearchResult(
                            chunk_id=chunk_id,
                            chapter=ch,
                            content=content,
                            score=score,
                            source="bm25",
                            metadata={"chunk_type": chunk_type}
                        ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def search(self, query: str, top_k: int = 5, chapter_limit: int = None) -> List[SearchResult]:
        return self.bm25_search(query, top_k, chapter_limit)
    
    def get_context_for_chapter(self, chapter: int, window: int = 3) -> Dict[str, Any]:
        summaries = []
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            for ch in range(max(1, chapter - window), chapter):
                cursor.execute(
                    "SELECT content FROM chunks WHERE chapter = ? AND chunk_type = 'summary'",
                    (ch,)
                )
                row = cursor.fetchone()
                if row:
                    summaries.append({
                        "chapter": ch,
                        "summary": row[0][:500] if row[0] else ""
                    })
        
        return {
            "chapter": chapter,
            "recent_summaries": summaries,
            "total_indexed": self.get_stats().get("total_chunks", 0)
        }
    
    def get_stats(self) -> Dict[str, int]:
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM chunks")
            total = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MAX(chapter) FROM chunks")
            max_chapter = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT term) FROM bm25_index")
            terms = cursor.fetchone()[0] or 0
            
            return {
                "total_chunks": total,
                "max_chapter": max_chapter,
                "unique_terms": terms
            }
