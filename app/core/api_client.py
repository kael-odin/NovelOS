#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Client - Embedding and Rerank API Client

Supports OpenAI-compatible APIs for embeddings and reranking.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .config import get_config


@dataclass
class APIStats:
    total_calls: int = 0
    total_time: float = 0.0
    errors: int = 0


class EmbeddingAPIClient:
    def __init__(self, config=None):
        self.config = config or get_config()
        self.sem = asyncio.Semaphore(getattr(self.config, 'embed_concurrency', 10))
        self.stats = APIStats()
        self._warmed_up = False
        self._session: Optional[aiohttp.ClientSession] = None
        self.last_error_status: Optional[int] = None
        self.last_error_message: str = ""

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _build_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = getattr(self.config, 'embed_api_key', None)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _build_url(self) -> str:
        base_url = getattr(self.config, 'embed_base_url', 'https://api.openai.com/v1').rstrip("/")
        if not base_url.endswith("/embeddings"):
            if base_url.endswith("/v1"):
                return f"{base_url}/embeddings"
            return f"{base_url}/v1/embeddings"
        return base_url

    def _build_payload(self, texts: List[str]) -> Dict[str, Any]:
        return {
            "input": texts,
            "model": getattr(self.config, 'embed_model', 'text-embedding-3-small'),
            "encoding_format": "float"
        }

    def _parse_response(self, data: Dict[str, Any]) -> Optional[List[List[float]]]:
        if "data" in data:
            sorted_data = sorted(data["data"], key=lambda x: x.get("index", 0))
            return [item["embedding"] for item in sorted_data]
        return None

    async def embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        if not texts:
            return []

        max_retries = getattr(self.config, 'api_max_retries', 3)
        base_delay = getattr(self.config, 'api_retry_delay', 1.0)
        timeout = getattr(self.config, 'normal_timeout', 30)

        async with self.sem:
            start = time.time()
            session = await self._get_session()

            for attempt in range(max_retries):
                try:
                    url = self._build_url()
                    headers = self._build_headers()
                    payload = self._build_payload(texts)

                    async with session.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            import json as json_module
                            data = json_module.loads(text)
                            embeddings = self._parse_response(data)

                            if embeddings:
                                self.stats.total_calls += 1
                                self.stats.total_time += time.time() - start
                                self._warmed_up = True
                                self.last_error_status = None
                                self.last_error_message = ""
                                return embeddings

                        if resp.status in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            await asyncio.sleep(delay)
                            continue

                        self.stats.errors += 1
                        err_text = await resp.text()
                        self.last_error_status = int(resp.status)
                        self.last_error_message = str(err_text[:200])
                        return None

                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    self.stats.errors += 1
                    self.last_error_message = f"Timeout after {max_retries} attempts"
                    return None

                except Exception as e:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    self.stats.errors += 1
                    self.last_error_message = str(e)
                    return None

            return None

    async def embed_batch(
        self, texts: List[str], *, skip_failures: bool = True
    ) -> List[Optional[List[float]]]:
        if not texts:
            return []

        all_embeddings: List[Optional[List[float]]] = []
        batch_size = getattr(self.config, 'embed_batch_size', 100)

        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        tasks = [self.embed(batch) for batch in batches]
        results = await asyncio.gather(*tasks)

        for batch_idx, result in enumerate(results):
            actual_batch_size = len(batches[batch_idx])
            if result and len(result) == actual_batch_size:
                all_embeddings.extend(result)
            else:
                if not skip_failures:
                    return []
                all_embeddings.extend([None] * actual_batch_size)

        return all_embeddings[:len(texts)]

    async def warmup(self):
        await self.embed(["test"])
        self._warmed_up = True


class RerankAPIClient:
    def __init__(self, config=None):
        self.config = config or get_config()
        self.sem = asyncio.Semaphore(getattr(self.config, 'rerank_concurrency', 5))
        self.stats = APIStats()
        self._warmed_up = False
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _build_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = getattr(self.config, 'rerank_api_key', None)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _build_url(self) -> str:
        base_url = getattr(self.config, 'rerank_base_url', 'https://api.jina.ai/v1').rstrip("/")
        if not base_url.endswith("/rerank"):
            if base_url.endswith("/v1"):
                return f"{base_url}/rerank"
            return f"{base_url}/v1/rerank"
        return base_url

    def _build_payload(self, query: str, documents: List[str], top_n: Optional[int]) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "query": query,
            "documents": documents,
            "model": getattr(self.config, 'rerank_model', 'jina-reranker-v2-base-multilingual')
        }
        if top_n:
            payload["top_n"] = top_n
        return payload

    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        if not documents:
            return []

        max_retries = getattr(self.config, 'api_max_retries', 3)
        base_delay = getattr(self.config, 'api_retry_delay', 1.0)
        timeout = getattr(self.config, 'normal_timeout', 30)

        async with self.sem:
            start = time.time()
            session = await self._get_session()

            for attempt in range(max_retries):
                try:
                    url = self._build_url()
                    headers = self._build_headers()
                    payload = self._build_payload(query, documents, top_n)

                    async with session.post(
                        url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.stats.total_calls += 1
                            self.stats.total_time += time.time() - start
                            self._warmed_up = True
                            return data.get("results", [])

                        if resp.status in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            await asyncio.sleep(delay)
                            continue

                        self.stats.errors += 1
                        return None

                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    self.stats.errors += 1
                    return None

                except Exception:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    self.stats.errors += 1
                    return None

            return None

    async def warmup(self):
        await self.rerank("test", ["doc1", "doc2"])
        self._warmed_up = True


class APIClient:
    def __init__(self, config=None):
        self.config = config or get_config()
        self._embed_client = EmbeddingAPIClient(self.config)
        self._rerank_client = RerankAPIClient(self.config)

    @property
    def stats(self) -> Dict[str, APIStats]:
        return {
            "embed": self._embed_client.stats,
            "rerank": self._rerank_client.stats
        }

    async def close(self):
        await self._embed_client.close()
        await self._rerank_client.close()

    async def warmup(self):
        tasks = [self._embed_client.warmup(), self._rerank_client.warmup()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        return await self._embed_client.embed(texts)

    async def embed_batch(
        self, texts: List[str], *, skip_failures: bool = True
    ) -> List[Optional[List[float]]]:
        return await self._embed_client.embed_batch(texts, skip_failures=skip_failures)

    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        return await self._rerank_client.rerank(query, documents, top_n)

    def print_stats(self):
        for name, stats in self.stats.items():
            if stats.total_calls > 0:
                avg_time = stats.total_time / stats.total_calls
                print(f"  {name.upper()}: {stats.total_calls} calls, "
                      f"{stats.total_time:.1f}s total, "
                      f"{avg_time:.2f}s avg, "
                      f"{stats.errors} errors")


_client: Optional[APIClient] = None


def get_client(config=None) -> APIClient:
    global _client
    if _client is None or config is not None:
        _client = APIClient(config)
    return _client
