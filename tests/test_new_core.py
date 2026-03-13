#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for new core modules.
"""

import pytest
from app.core import (
    QueryRouter,
    ContextRanker,
    build_methodology_strategy_card,
    build_methodology_guidance_items,
    build_guidance_items,
    build_writing_checklist,
    normalize_genre_token,
    EntityLinker,
    DisambiguationResult,
    normalize_foreshadowing_status,
    normalize_foreshadowing_tier,
    normalize_foreshadowing_item,
    normalize_foreshadowing_list,
    FORESHADOWING_STATUS_PENDING,
    FORESHADOWING_STATUS_RESOLVED,
    FORESHADOWING_TIER_CORE,
    FORESHADOWING_TIER_SUB,
    FORESHADOWING_TIER_DECOR,
    StyleSampler,
    StyleSample,
    SceneType,
)


class TestQueryRouter:
    def test_route_intent_plot(self):
        router = QueryRouter()
        result = router.route_intent("剧情发生了什么")
        assert result["intent"] == "plot"

    def test_route_intent_entity(self):
        router = QueryRouter()
        result = router.route_intent("这个角色是谁")
        assert result["intent"] == "entity"

    def test_route_intent_scene(self):
        router = QueryRouter()
        result = router.route_intent("这个场景在哪里")
        assert result["intent"] == "scene"

    def test_route_intent_relationship(self):
        router = QueryRouter()
        result = router.route_intent("他们之间的关系是什么")
        assert result["intent"] == "relationship"

    def test_extract_entities(self):
        router = QueryRouter()
        result = router.route_intent("张三和李四的关系")
        assert len(result["entities"]) > 0

    def test_extract_time_scope_single(self):
        router = QueryRouter()
        result = router.route_intent("第10章发生了什么")
        assert result["time_scope"]["from_chapter"] == 10
        assert result["time_scope"]["to_chapter"] == 10

    def test_extract_time_scope_range(self):
        router = QueryRouter()
        result = router.route_intent("第10-20章发生了什么")
        assert result["time_scope"]["from_chapter"] == 10
        assert result["time_scope"]["to_chapter"] == 20

    def test_plan_subqueries_default(self):
        router = QueryRouter()
        intent = router.route_intent("发生了什么")
        steps = router.plan_subqueries(intent)
        assert len(steps) == 1
        assert steps[0]["strategy"] == "hybrid"

    def test_plan_subqueries_relationship(self):
        router = QueryRouter()
        intent = router.route_intent("张三和李四的关系")
        steps = router.plan_subqueries(intent)
        assert len(steps) == 2

    def test_split_query(self):
        router = QueryRouter()
        parts = router.split("张三，李四，王五")
        assert len(parts) == 3


class TestContextRanker:
    def test_rank_pack(self):
        ranker = ContextRanker()
        pack = {
            "core": {
                "recent_summaries": [
                    {"chapter": 1, "summary": "测试摘要"},
                    {"chapter": 2, "summary": "测试摘要2"},
                ],
                "recent_meta": [],
            },
            "scene": {
                "appearing_characters": [],
            },
            "story_skeleton": [],
            "alerts": {},
        }
        ranked = ranker.rank_pack(pack, 3)
        assert "meta" in ranked
        assert ranked["meta"]["ranker"]["enabled"] is True

    def test_rank_recent_summaries(self):
        ranker = ContextRanker()
        items = [
            {"chapter": 1, "summary": "旧摘要"},
            {"chapter": 3, "summary": "新摘要"},
        ]
        ranked = ranker.rank_recent_summaries(items, 4)
        assert ranked[0]["chapter"] == 3

    def test_rank_appearances(self):
        ranker = ContextRanker()
        items = [
            {"name": "角色A", "last_chapter": 1, "total": 5},
            {"name": "角色B", "last_chapter": 3, "total": 10},
        ]
        ranked = ranker.rank_appearances(items, 4)
        assert ranked[0]["name"] == "角色B"

    def test_recency_score(self):
        ranker = ContextRanker()
        assert ranker._recency_score(3, 4) > ranker._recency_score(1, 4)

    def test_frequency_score(self):
        ranker = ContextRanker()
        assert ranker._frequency_score(10) > ranker._frequency_score(5)


class TestWritingGuidance:
    def test_normalize_genre_token(self):
        assert normalize_genre_token("仙侠") == "xianxia"
        assert normalize_genre_token("都市") == "urban-power"
        assert normalize_genre_token("言情") == "romance"

    def test_build_methodology_strategy_card(self):
        reader_signal = {
            "hook_type_usage": {"suspense": 5, "cliffhanger": 3},
            "pattern_usage": {"power_up": 4},
            "review_trend": {"overall_avg": 80},
            "low_score_ranges": [],
        }
        genre_profile = {"genre": "仙侠"}
        card = build_methodology_strategy_card(
            chapter=10,
            reader_signal=reader_signal,
            genre_profile=genre_profile,
        )
        assert card["enabled"] is True
        assert card["genre_profile_key"] == "xianxia"
        assert "emotion_anchor" in card

    def test_build_methodology_guidance_items(self):
        strategy_card = {
            "enabled": True,
            "chapter_stage": "build_up",
            "genre_profile_key": "xianxia",
            "observability": {"next_reason_clarity": 75.0},
            "signals": {"risk_flags": []},
        }
        items = build_methodology_guidance_items(strategy_card)
        assert len(items) > 0
        assert any("方法论策略" in item for item in items)

    def test_build_guidance_items(self):
        reader_signal = {
            "low_score_ranges": [],
            "hook_type_usage": {},
            "pattern_usage": {},
            "review_trend": {"overall_avg": 80},
        }
        genre_profile = {"genre": "仙侠"}
        result = build_guidance_items(
            chapter=10,
            reader_signal=reader_signal,
            genre_profile=genre_profile,
            low_score_threshold=75.0,
            hook_diversify_enabled=True,
        )
        assert "guidance" in result
        assert len(result["guidance"]) > 0

    def test_build_writing_checklist(self):
        reader_signal = {
            "low_score_ranges": [],
            "hook_type_usage": {},
            "pattern_usage": {},
            "review_trend": {"overall_avg": 80},
        }
        genre_profile = {"genre": "仙侠"}
        items = build_writing_checklist(
            guidance_items=["测试指导"],
            reader_signal=reader_signal,
            genre_profile=genre_profile,
            min_items=3,
            max_items=10,
            default_weight=1.0,
        )
        assert len(items) >= 3


class TestEntityLinker:
    def test_evaluate_confidence_high(self):
        linker = EntityLinker()
        action, adopt, warning = linker.evaluate_confidence(0.95)
        assert action == "auto"
        assert adopt is True
        assert warning is None

    def test_evaluate_confidence_medium(self):
        linker = EntityLinker()
        action, adopt, warning = linker.evaluate_confidence(0.75)
        assert action == "warn"
        assert adopt is True
        assert warning is not None

    def test_evaluate_confidence_low(self):
        linker = EntityLinker()
        action, adopt, warning = linker.evaluate_confidence(0.3)
        assert action == "manual"
        assert adopt is False
        assert warning is not None

    def test_process_uncertain(self):
        linker = EntityLinker()
        result = linker.process_uncertain(
            mention="张三",
            candidates=["角色A", "角色B"],
            suggested="角色A",
            confidence=0.85,
        )
        assert result.mention == "张三"
        assert result.adopted is True

    def test_process_extraction_result(self):
        linker = EntityLinker()
        uncertain_items = [
            {"mention": "张三", "candidates": ["A", "B"], "suggested": "A", "confidence": 0.8},
        ]
        results, warnings = linker.process_extraction_result(uncertain_items)
        assert len(results) == 1


class TestStateValidator:
    def test_normalize_foreshadowing_status_pending(self):
        assert normalize_foreshadowing_status("未回收") == FORESHADOWING_STATUS_PENDING
        assert normalize_foreshadowing_status("待回收") == FORESHADOWING_STATUS_PENDING
        assert normalize_foreshadowing_status("pending") == FORESHADOWING_STATUS_PENDING

    def test_normalize_foreshadowing_status_resolved(self):
        assert normalize_foreshadowing_status("已回收") == FORESHADOWING_STATUS_RESOLVED
        assert normalize_foreshadowing_status("完成") == FORESHADOWING_STATUS_RESOLVED
        assert normalize_foreshadowing_status("resolved") == FORESHADOWING_STATUS_RESOLVED

    def test_normalize_foreshadowing_tier(self):
        assert normalize_foreshadowing_tier("核心") == FORESHADOWING_TIER_CORE
        assert normalize_foreshadowing_tier("主线") == FORESHADOWING_TIER_CORE
        assert normalize_foreshadowing_tier("装饰") == FORESHADOWING_TIER_DECOR
        assert normalize_foreshadowing_tier("支线") == FORESHADOWING_TIER_SUB

    def test_normalize_foreshadowing_item(self):
        item = {
            "content": "测试伏笔",
            "status": "未回收",
            "tier": "核心",
            "planted_chapter": 10,
            "target_chapter": 50,
        }
        normalized = normalize_foreshadowing_item(item)
        assert normalized["status"] == FORESHADOWING_STATUS_PENDING
        assert normalized["tier"] == FORESHADOWING_TIER_CORE
        assert normalized["planted_chapter"] == 10
        assert normalized["target_chapter"] == 50

    def test_normalize_foreshadowing_list(self):
        items = [
            {"content": "伏笔1", "status": "未回收"},
            {"content": "伏笔2", "status": "已回收"},
        ]
        normalized = normalize_foreshadowing_list(items)
        assert len(normalized) == 2
        assert normalized[0]["status"] == FORESHADOWING_STATUS_PENDING
        assert normalized[1]["status"] == FORESHADOWING_STATUS_RESOLVED


class TestStyleSampler:
    def test_scene_type_enum(self):
        assert SceneType.BATTLE.value == "战斗"
        assert SceneType.DIALOGUE.value == "对话"
        assert SceneType.DESCRIPTION.value == "描写"

    def test_style_sample_creation(self):
        sample = StyleSample(
            id="ch1_s1",
            chapter=1,
            scene_type="战斗",
            content="测试内容",
            score=0.9,
            tags=["战斗", "修炼"],
        )
        assert sample.id == "ch1_s1"
        assert sample.chapter == 1
        assert sample.score == 0.9

    def test_classify_scene_type(self):
        sampler = StyleSampler(config=None)
        battle_scene = {"summary": "战斗场景", "content": "他一拳打过去"}
        assert sampler._classify_scene_type(battle_scene) == SceneType.BATTLE.value

        dialogue_scene = {"summary": "对话场景", "content": "他说道：你好"}
        assert sampler._classify_scene_type(dialogue_scene) == SceneType.DIALOGUE.value

    def test_extract_tags(self):
        sampler = StyleSampler(config=None)
        tags = sampler._extract_tags("这是一场激烈的战斗，他正在修炼")
        assert "战斗" in tags
        assert "修炼" in tags

    def test_infer_scene_types(self):
        sampler = StyleSampler(config=None)
        types = sampler._infer_scene_types("这是一场激烈的战斗对决")
        assert SceneType.BATTLE.value in types

        types = sampler._infer_scene_types("他们坐下来对话商议")
        assert SceneType.DIALOGUE.value in types
