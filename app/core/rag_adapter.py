#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Adapter - RAG 检索适配模块

整合自 webnovel-writer/scripts/data_modules/rag_adapter.py
封装向量检索功能
"""
from __future__ import annotations

import sqlite3
import json
import math
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import Counter
from contextlib import contextmanager

from .config import get_config, CoreConfig
from .index_manager import IndexManager

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果"""
    chunk_id: str
    chapter: int
    scene_index: int
    content: str
    score: float
    source: str
    parent_chunk_id: str | None = None
    chunk_type: str | None = None
    source_file: str | None = None


class RAGAdapter:
    """RAG 检索适配器"""

    def __init__(self, config: CoreConfig = None):
        self.config = config or get_config()
        self.index_manager = IndexManager(self.config)
        self._init_db()

    def _init_db(self):
        """初始化向量数据库"""
        self.config.ensure_dirs()

        with self._get_conn() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    chunk_id TEXT PRIMARY KEY,
                    chapter INTEGER,
                    scene_index INTEGER,
                    content TEXT,
                    embedding BLOB,
                    parent_chunk_id TEXT,
                    chunk_type TEXT DEFAULT 'scene',
                    source_file TEXT,
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doc_stats (
                    chunk_id TEXT PRIMARY KEY,
                    doc_length INTEGER
                )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vectors_chapter ON vectors(chapter)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bm25_term ON bm25_index(term)")

            conn.commit()

    @contextmanager
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.config.vector_db))
        try:
            yield conn
        finally:
            conn.close()

    def _tokenize(self, text: str) -> List[str]:
        """简单分词（中文按字符，英文按单词）"""
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        chinese_chars = list("".join(chinese))
        english = re.findall(r'[a-zA-Z]+', text.lower())
        return chinese_chars + english

    def _update_bm25_index(self, cursor, chunk_id: str, content: str):
        """更新 BM25 索引"""
        cursor.execute("DELETE FROM bm25_index WHERE chunk_id = ?", (chunk_id,))
        cursor.execute("DELETE FROM doc_stats WHERE chunk_id = ?", (chunk_id,))

        tokens = self._tokenize(content)
        doc_length = len(tokens)
        tf_counter = Counter(tokens)

        for term, count in tf_counter.items():
            tf = count / doc_length if doc_length > 0 else 0
            cursor.execute("""
                INSERT INTO bm25_index (term, chunk_id, tf)
                VALUES (?, ?, ?)
            """, (term, chunk_id, tf))

        cursor.execute("""
            INSERT INTO doc_stats (chunk_id, doc_length)
            VALUES (?, ?)
        """, (chunk_id, doc_length))

    def store_chunks(self, chunks: List[Dict]) -> int:
        """存储场景切片"""
        if not chunks:
            return 0

        stored = 0
        with self._get_conn() as conn:
            cursor = conn.cursor()

            for chunk in chunks:
                chunk_type = chunk.get("chunk_type") or "scene"
                chunk_id = chunk.get("chunk_id")
                if not chunk_id:
                    if chunk_type == "summary":
                        chunk_id = f"ch{int(chunk['chapter']):04d}_summary"
                    else:
                        chunk_id = f"ch{int(chunk['chapter']):04d}_s{int(chunk['scene_index'])}"

                cursor.execute("""
                    INSERT OR REPLACE INTO vectors
                    (chunk_id, chapter, scene_index, content, parent_chunk_id, chunk_type, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk_id,
                    chunk["chapter"],
                    chunk.get("scene_index", 0) if chunk_type == "scene" else 0,
                    chunk.get("content", ""),
                    chunk.get("parent_chunk_id"),
                    chunk_type,
                    chunk.get("source_file"),
                ))

                self._update_bm25_index(cursor, chunk_id, chunk.get("content", ""))
                stored += 1

            conn.commit()

        return stored

    def bm25_search(
        self,
        query: str,
        top_k: int = 20,
        k1: float = 1.5,
        b: float = 0.75,
        chunk_type: str | None = None,
        chapter: int | None = None,
    ) -> List[SearchResult]:
        """BM25 关键词搜索"""
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        with self._get_conn() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*), AVG(doc_length) FROM doc_stats")
            row = cursor.fetchone()
            total_docs = row[0] or 1
            avg_doc_length = row[1] or 1

            doc_scores = {}

            for term in set(query_terms):
                cursor.execute("""
                    SELECT b.chunk_id, b.tf, d.doc_length
                    FROM bm25_index b
                    JOIN doc_stats d ON b.chunk_id = d.chunk_id
                    WHERE b.term = ?
                """, (term,))

                docs_with_term = cursor.fetchall()
                df = len(docs_with_term)

                if df == 0:
                    continue

                idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)

                for chunk_id, tf, doc_length in docs_with_term:
                    score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_length / avg_doc_length))

                    if chunk_id not in doc_scores:
                        doc_scores[chunk_id] = 0
                    doc_scores[chunk_id] += score

            results = []
            for chunk_id, score in doc_scores.items():
                cursor.execute(
                    """
                    SELECT chapter, scene_index, content, parent_chunk_id, chunk_type, source_file
                    FROM vectors
                    WHERE chunk_id = ?
                """,
                    (chunk_id,),
                )
                row = cursor.fetchone()
                if row:
                    results.append(SearchResult(
                        chunk_id=chunk_id,
                        chapter=row[0],
                        scene_index=row[1],
                        content=row[2],
                        score=score,
                        source="bm25",
                        parent_chunk_id=row[3],
                        chunk_type=row[4],
                        source_file=row[5],
                    ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def get_stats(self) -> Dict[str, int]:
        """获取 RAG 统计"""
        with self._get_conn() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM vectors")
            vectors = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT term) FROM bm25_index")
            terms = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(chapter) FROM vectors")
            max_chapter = cursor.fetchone()[0] or 0

            return {
                "vectors": vectors,
                "terms": terms,
                "max_chapter": max_chapter
            }
