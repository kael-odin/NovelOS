#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovelOS Core Config - 核心配置模块

整合自 webnovel-writer/scripts/data_modules/config.py
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


def _get_user_config_root() -> Path:
    raw = os.environ.get("NOVELOS_CONFIG_HOME") or os.environ.get("CLAUDE_HOME")
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path.home() / ".novelos").resolve()


def _load_dotenv_file(env_path: Path, *, override: bool = False) -> bool:
    if not env_path.exists():
        return False
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if not key:
                        continue
                    if override or key not in os.environ:
                        os.environ[key] = value
        return True
    except Exception:
        return False


def _load_dotenv():
    _load_dotenv_file(Path.cwd() / ".env", override=False)
    global_env = _get_user_config_root() / ".env"
    _load_dotenv_file(global_env, override=False)


_load_dotenv()


@dataclass
class CoreConfig:
    project_root: Path = field(default_factory=lambda: Path.cwd())

    @property
    def novelos_dir(self) -> Path:
        return self.project_root / ".novelos"

    @property
    def webnovel_dir(self) -> Path:
        return self.project_root / ".webnovel"

    @property
    def state_file(self) -> Path:
        return self.novelos_dir / "state.json"

    @property
    def index_db(self) -> Path:
        return self.novelos_dir / "index.db"

    @property
    def vector_db(self) -> Path:
        return self.novelos_dir / "vectors.db"

    @property
    def chapters_dir(self) -> Path:
        return self.project_root / "chapters"

    @property
    def drafts_dir(self) -> Path:
        return self.chapters_dir / "drafts"

    @property
    def final_dir(self) -> Path:
        return self.chapters_dir / "final"

    @property
    def story_bible_dir(self) -> Path:
        return self.project_root / "story_bible"

    @property
    def outlines_dir(self) -> Path:
        return self.project_root / "outlines"

    @property
    def memory_dir(self) -> Path:
        return self.project_root / "memory"

    @property
    def summaries_dir(self) -> Path:
        return self.memory_dir / "summaries"

    embed_api_type: str = "openai"
    embed_base_url: str = field(default_factory=lambda: os.getenv("EMBED_BASE_URL", "https://api-inference.modelscope.cn/v1"))
    embed_model: str = field(default_factory=lambda: os.getenv("EMBED_MODEL", "Qwen/Qwen3-Embedding-8B"))
    embed_api_key: str = field(default_factory=lambda: os.getenv("EMBED_API_KEY", ""))

    rerank_api_type: str = "openai"
    rerank_base_url: str = field(default_factory=lambda: os.getenv("RERANK_BASE_URL", "https://api.jina.ai/v1"))
    rerank_model: str = field(default_factory=lambda: os.getenv("RERANK_MODEL", "jina-reranker-v3"))
    rerank_api_key: str = field(default_factory=lambda: os.getenv("RERANK_API_KEY", ""))

    embed_concurrency: int = 64
    rerank_concurrency: int = 32
    embed_batch_size: int = 64

    cold_start_timeout: int = 300
    normal_timeout: int = 180
    api_max_retries: int = 3
    api_retry_delay: float = 1.0

    vector_top_k: int = 30
    bm25_top_k: int = 20
    rerank_top_n: int = 10
    rrf_k: int = 60

    vector_full_scan_max_vectors: int = 500
    vector_prefilter_bm25_candidates: int = 200
    vector_prefilter_recent_candidates: int = 200

    graph_rag_enabled: bool = False
    graph_rag_expand_hops: int = 1
    graph_rag_max_expanded_entities: int = 30
    graph_rag_candidate_limit: int = 150
    graph_rag_boost_same_entity: float = 0.2
    graph_rag_boost_related_entity: float = 0.1
    graph_rag_boost_recency: float = 0.05

    extraction_confidence_high: float = 0.8
    extraction_confidence_medium: float = 0.5

    max_disambiguation_warnings: int = 500
    max_disambiguation_pending: int = 1000
    max_state_changes: int = 2000

    context_recent_summaries_window: int = 3
    context_recent_meta_window: int = 3
    context_alerts_slice: int = 10
    context_max_appearing_characters: int = 10
    context_max_urgent_foreshadowing: int = 5
    context_story_skeleton_interval: int = 20
    context_story_skeleton_max_samples: int = 5
    context_story_skeleton_snippet_chars: int = 400
    context_extra_section_budget: int = 800
    context_ranker_enabled: bool = True
    context_ranker_recency_weight: float = 0.7
    context_ranker_frequency_weight: float = 0.3
    context_ranker_hook_bonus: float = 0.2
    context_ranker_length_bonus_cap: float = 0.2
    context_reader_signal_enabled: bool = True
    context_reader_signal_recent_limit: int = 5
    context_reader_signal_window_chapters: int = 20
    context_reader_signal_review_window: int = 5
    context_reader_signal_include_debt: bool = False
    context_genre_profile_enabled: bool = True
    context_genre_profile_max_refs: int = 8
    context_genre_profile_fallback: str = "shuangwen"
    context_compact_text_enabled: bool = True
    context_compact_min_budget: int = 120
    context_compact_head_ratio: float = 0.65
    context_writing_guidance_enabled: bool = True
    context_writing_guidance_max_items: int = 6
    context_writing_guidance_low_score_threshold: float = 75.0
    context_writing_guidance_hook_diversify: bool = True
    context_methodology_enabled: bool = True
    context_methodology_genre_whitelist: tuple = ("*",)
    context_methodology_label: str = "digital-serial-v1"
    context_writing_checklist_enabled: bool = True
    context_writing_checklist_min_items: int = 3
    context_writing_checklist_max_items: int = 6
    context_writing_checklist_default_weight: float = 1.0
    context_writing_score_persist_enabled: bool = True
    context_writing_score_include_reader_trend: bool = True
    context_writing_score_trend_window: int = 10
    context_rag_assist_enabled: bool = True
    context_rag_assist_top_k: int = 4
    context_rag_assist_min_outline_chars: int = 40
    context_rag_assist_max_query_chars: int = 120
    context_dynamic_budget_enabled: bool = True
    context_dynamic_budget_early_chapter: int = 30
    context_dynamic_budget_late_chapter: int = 120
    context_dynamic_budget_early_core_bonus: float = 0.08
    context_dynamic_budget_early_scene_bonus: float = 0.04
    context_dynamic_budget_late_global_bonus: float = 0.08
    context_dynamic_budget_late_scene_penalty: float = 0.06
    context_genre_profile_support_composite: bool = True
    context_genre_profile_max_genres: int = 2
    context_genre_profile_separators: tuple = ("+", "/", "|", ",", "，", "、")

    export_recent_changes_slice: int = 20
    export_disambiguation_slice: int = 20

    query_recent_chapters_limit: int = 10
    query_scenes_by_location_limit: int = 20
    query_entity_appearances_limit: int = 50
    query_recent_appearances_limit: int = 20

    foreshadowing_urgency_pending_high: int = 100
    foreshadowing_urgency_pending_medium: int = 50
    foreshadowing_urgency_target_proximity: int = 5
    foreshadowing_urgency_score_high: int = 100
    foreshadowing_urgency_score_medium: int = 60
    foreshadowing_urgency_score_target: int = 80
    foreshadowing_urgency_score_low: int = 20
    foreshadowing_urgency_threshold_show: int = 60

    foreshadowing_tier_weight_core: float = 3.0
    foreshadowing_tier_weight_sub: float = 2.0
    foreshadowing_tier_weight_decor: float = 1.0

    character_absence_warning: int = 30
    character_absence_critical: int = 100
    character_candidates_limit: int = 800

    strand_quest_max_consecutive: int = 5
    strand_fire_max_gap: int = 10
    strand_constellation_max_gap: int = 15

    strand_quest_ratio_min: int = 55
    strand_quest_ratio_max: int = 65
    strand_fire_ratio_min: int = 20
    strand_fire_ratio_max: int = 30
    strand_constellation_ratio_min: int = 10
    strand_constellation_ratio_max: int = 20

    pacing_segment_size: int = 100
    pacing_words_per_point_excellent: int = 1000
    pacing_words_per_point_good: int = 1500
    pacing_words_per_point_acceptable: int = 2000

    def ensure_dirs(self):
        self.novelos_dir.mkdir(parents=True, exist_ok=True)
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        self.final_dir.mkdir(parents=True, exist_ok=True)
        self.story_bible_dir.mkdir(parents=True, exist_ok=True)
        self.outlines_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> "CoreConfig":
        root = Path(project_root).expanduser().resolve()
        _load_dotenv_file(root / ".env", override=False)
        return cls(project_root=root)


_default_config: Optional[CoreConfig] = None


def get_config(project_root: Optional[Path] = None) -> CoreConfig:
    global _default_config
    if project_root is not None:
        return CoreConfig.from_project_root(project_root)
    if _default_config is None:
        root = _resolve_project_root()
        _default_config = CoreConfig.from_project_root(root)
    return _default_config


def _resolve_project_root() -> Path:
    env_root = os.environ.get("NOVELOS_PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    
    cwd = Path.cwd()
    for p in [cwd] + list(cwd.parents):
        if (p / ".novelos").exists() or (p / "novel.yaml").exists():
            return p
    
    return cwd


def set_project_root(project_root: str | Path):
    global _default_config
    _default_config = CoreConfig.from_project_root(project_root)
