#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovelOS 项目初始化脚本

目标：
- 生成符合 NovelOS 规范的目录结构
- 写入 novel.yaml / AGENTS.md / CLAUDE.md / .cursorrules
- 生成基础 prompts 模板与空白 story_bible
- 生成 .novelos 运行时目录

说明：
- 仅在目标文件不存在时写入，避免覆盖用户已有内容
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


def _write_text_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def _write_json_if_missing(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _novel_yaml(
    name: str,
    slug: str,
    language: str,
    genre: str,
    target_words: int,
    target_chapters: int,
    target_volumes: int,
) -> str:
    return (
        "project:\n"
        f"  name: \"{name}\"\n"
        f"  slug: \"{slug}\"\n"
        f"  language: \"{language}\"\n"
        f"  genre: [{genre}]\n"
        f"  target_words: {target_words}\n"
        f"  target_chapters: {target_chapters}\n"
        f"  target_volumes: {target_volumes}\n\n"
        "writing:\n"
        "  chapter_word_range: [2500, 5000]\n"
        "  scene_per_chapter_range: [3, 6]\n"
        "  pov_mode: \"limited-third-person\"\n"
        "  style_goal: \"自然流畅、情绪真实、减少AI味、兼顾网文爽点与人物成长\"\n"
        "  hook_requirement: true\n"
        "  revision_rounds: 2\n\n"
        "workflow:\n"
        "  summary_after_each_chapter: true\n"
        "  consistency_check_after_each_chapter: true\n"
        "  global_check_every_n_chapters: 20\n"
        "  volume_review_every_n_chapters: 50\n\n"
        "adapters:\n"
        "  default: \"manual_agent\"\n"
        "  available:\n"
        "    - \"manual_agent\"\n"
        "    - \"prompt_file\"\n"
        "    - \"cursor\"\n"
        "    - \"claude_code\"\n"
        "    - \"codex\"\n"
        "    - \"api\"\n\n"
        "quality:\n"
        "  minimum_review_score: 7.5\n"
        "  reject_if_character_broken: true\n"
        "  reject_if_world_rule_conflict: true\n"
        "  reject_if_ai_flavor_high: true\n\n"
        "paths:\n"
        "  project_root: \"./project\"\n"
        "  prompts_root: \"./app/prompts\"\n"
    )


def init_project(
    project_dir: str,
    name: str,
    slug: str,
    language: str,
    genre: str,
    target_words: int,
    target_chapters: int,
    target_volumes: int,
) -> None:
    project_root = Path(project_dir).expanduser().resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    # 基础目录
    dirs = [
        "docs",
        "app/models",
        "app/services",
        "app/adapters",
        "app/prompts/planning",
        "app/prompts/generation",
        "app/prompts/review",
        "app/prompts/revision",
        "app/prompts/extraction",
        "app/prompts/system",
        "app/utils",
        "scripts",
        "project/story_bible",
        "project/outlines/chapter_plans",
        "project/chapters/drafts",
        "project/chapters/revised",
        "project/chapters/final",
        "project/chapters/compiled",
        "project/memory/chapter_summaries",
        "project/memory/volume_summaries",
        "project/memory/context",
        "project/memory/event_index",
        "project/memory/entity_state",
        "project/memory/retrieval_cache",
        "project/memory/semantic_index",
        "project/reviews/consistency",
        "project/reviews/pacing",
        "project/reviews/prose",
        "project/reviews/reader",
        "project/reviews/foreshadowing",
        "project/reviews/merged",
        "project/revisions",
        "project/tasks/queue",
        "project/tasks/doing",
        "project/tasks/done",
        "project/tasks/failed",
        "project/exports/txt",
        "project/exports/epub",
        "project/exports/md",
        "project/reports/consistency_reports",
        "project/reports/pacing_reports",
        "project/reports/style_reports",
        "project/reports/progress",
        ".novelos/logs",
        ".novelos/checkpoints",
        ".novelos/cache",
    ]
    for d in dirs:
        (project_root / d).mkdir(parents=True, exist_ok=True)

    # 配置与协作文件
    _write_text_if_missing(project_root / "novel.yaml", _novel_yaml(name, slug, language, genre, target_words, target_chapters, target_volumes))

    _write_text_if_missing(
        project_root / "AGENTS.md",
        """# AGENTS.md\n\n你是本仓库中的小说工程代理，不是随意聊天助手。\n\n## 你的职责\n你需要根据仓库中的文件和任务，协助完成长篇小说的规划、生成、评审、修订和状态更新。\n\n## 基本原则\n1. 任何正文生成前，必须先阅读：\n   - project/story_bible/\n   - 当前章节计划\n   - 最近章节摘要\n   - 当前章节上下文包\n2. 不能跳过一致性约束。\n3. 不能擅自修改世界规则和角色核心设定，除非任务明确要求。\n4. 每次生成后必须：\n   - 产出章节摘要\n   - 提取状态变化\n   - 更新相关索引或状态文件\n5. 所有修订必须基于 reviews/ 中的反馈，不要无目的大改。\n6. 优先保持人物稳定、情节清晰、语言自然，而不是盲目堆砌辞藻。\n7. 禁止为了“像小说”而过度使用套话、空话和夸张修饰。\n\n## 写作要求\n- 章节必须有明确推进，不能原地踏步\n- 对话必须区分角色口吻\n- 人物情绪应通过动作、停顿、细节来体现，不要只做抽象说明\n- 章末尽量保留推动读者继续阅读的钩子\n- 避免常见 AI 套路句式和高频模板表达\n\n## 评审要求\n评审时要具体指出：\n- 哪一段有问题\n- 问题类型是什么\n- 为什么有问题\n- 如何修改更好\n\n## 修改要求\n修改时优先：\n1. 修复设定错误\n2. 修复人设偏差\n3. 修复节奏拖沓\n4. 修复 AI 味\n5. 提升可读性\n\n## 输出要求\n- 尽量写入指定文件\n- 使用仓库已有格式\n- 保持文件命名和目录规范统一\n""",
    )

    _write_text_if_missing(
        project_root / "CLAUDE.md",
        """# CLAUDE.md\n\n这是一个长篇小说工程仓库。\n\n你在本项目中的身份不是单纯写作者，而是“小说工程协作代理”。\n\n## 先读这些文件\n1. AGENTS.md\n2. novel.yaml\n3. docs/architecture.md\n4. project/story_bible/*\n5. 当前任务文件\n6. 当前章节 context bundle\n\n## 工作模式\n- 按任务执行\n- 生成前先理解结构\n- 修改前先看评审\n- 更新前先提取变化\n- 所有结果写回文件\n\n## 注意事项\n- 保持世界观和人物一致性\n- 不要自己发明没有依据的重要设定\n- 如果上下文不够，优先生成“需要补充信息”的说明，而不是胡写\n- 如果发现已有文件冲突，必须显式指出\n\n## 风格底线\n- 不要过度 AI 化表达\n- 不要堆“震惊、恐怖、可怕、磅礴、仿佛、宛如”这类空泛词\n- 不要把所有角色写成同一种说话方式\n- 多写具体动作、环境反馈、心理张力\n""",
    )

    _write_text_if_missing(
        project_root / ".cursorrules",
        """You are working inside a long-form novel engineering repository.\n\nRules:\n1. Always inspect project/story_bible, current chapter plan, and memory context before generating text.\n2. Never alter world rules or character core traits without explicit instruction.\n3. Treat every chapter as part of a large evolving system, not a standalone story.\n4. When revising, preserve valid content and only change what is necessary.\n5. Prefer concrete sensory details over vague dramatic adjectives.\n6. Avoid repetitive AI-style phrases and overused transition patterns.\n7. After generating a chapter, also generate:\n   - chapter summary\n   - state changes\n   - possible foreshadowing updates\n8. If context is insufficient, say so explicitly and propose the missing files needed.\n""",
    )

    # 基础 prompts（来自 NovelOS 规范）
    prompts = {
        "app/prompts/planning/book_planner.md.j2": """你是一位资深长篇小说架构师，需要为一部长篇中文小说设计全书结构。\n\n# 项目信息\n- 作品类型：{{ genre }}\n- 目标字数：{{ target_words }}\n- 目标章节数：{{ target_chapters }}\n- 目标卷数：{{ target_volumes }}\n- 风格目标：{{ style_goal }}\n\n# 已知故事设定\n{{ story_bible_summary }}\n\n# 任务\n请输出一份完整的全书规划，内容包括：\n\n1. 核心主题\n2. 主线冲突\n3. 主角成长主轴\n4. 主要角色关系主轴\n5. 全书三到八个关键转折点\n6. 分卷思路\n7. 全书节奏设计\n8. 爽点、压抑、爆发、揭秘的大致分布\n9. 至少 10 条伏笔主线\n10. 结局方向（开放式/封闭式/阶段性完结）\n\n# 输出格式\n请使用 Markdown，包含：\n- 全书概述\n- 分卷规划\n- 主线与支线\n- 节奏曲线说明\n- 伏笔总表\n- 风险提醒（容易崩的地方）\n""",
        "app/prompts/planning/volume_planner.md.j2": """你是一位资深小说架构师，请为当前长篇小说设计某一卷的大纲。\n\n# 全书信息\n{{ book_outline }}\n\n# 当前卷次\n第 {{ volume_number }} 卷\n\n# 故事圣经摘要\n{{ story_bible_summary }}\n\n# 任务\n请输出本卷大纲，包括：\n\n1. 本卷主题\n2. 本卷开端状态\n3. 本卷核心冲突\n4. 本卷主要角色出场安排\n5. 本卷要推进或埋下的伏笔\n6. 本卷至少 5-10 个关键章节节点\n7. 本卷结尾钩子\n8. 本卷节奏建议（快慢分布）\n9. 本卷最容易写崩的风险点\n\n请保持与全书主线一致，不要脱离故事核心。\n""",
        "app/prompts/planning/chapter_planner.md.j2": """你现在要为长篇小说规划一个具体章节。\n\n# 当前卷大纲\n{{ volume_outline }}\n\n# 最近章节摘要\n{{ recent_summaries }}\n\n# 当前角色状态\n{{ character_states }}\n\n# 当前活跃伏笔\n{{ active_foreshadowings }}\n\n# 本章编号\n第 {{ chapter_number }} 章\n\n# 任务\n请输出本章规划，内容包括：\n\n1. 本章目标\n2. 本章在整卷中的作用\n3. 本章核心冲突\n4. 本章场景分解（3-6 个场景）\n5. 每个场景的情绪标签\n6. 哪些角色必须出场\n7. 哪些信息可以推进，哪些不能暴露\n8. 本章结尾钩子\n9. 一致性提醒\n10. 文风和节奏建议\n\n请用 Markdown 输出。\n""",
        "app/prompts/planning/scene_planner.md.j2": """你现在要为长篇小说规划一个具体场景。\n\n# 章节规划\n{{ chapter_plan }}\n\n# 本场景编号\n第 {{ scene_number }} 场\n\n# 任务\n请输出本场景规划，内容包括：\n\n1. 场景目标\n2. 场景冲突\n3. 场景情绪标签\n4. 出场角色\n5. 必须推进的信息\n6. 禁止暴露的信息\n7. 场景结束钩子\n\n请用 Markdown 输出。\n""",
        "app/prompts/generation/scene_generator.md.j2": """你现在要写一个长篇小说中的具体场景，而不是整章乱写。\n\n# 场景规划\n{{ scene_plan }}\n\n# 当前章节上下文\n{{ chapter_context }}\n\n# 当前角色状态\n{{ character_states }}\n\n# 风格要求\n{{ style_rules }}\n\n# 写作要求\n1. 只写这个场景，不要抢写后面的内容\n2. 场景必须有明确目标和变化\n3. 对话要区分角色口吻\n4. 多用具体动作、环境反馈、感官细节\n5. 避免空泛形容和常见 AI 套话\n6. 不要违反世界规则、人设和时间线\n7. 输出为可直接并入正文的自然小说文本\n\n请直接输出正文，不要解释。\n""",
        "app/prompts/generation/chapter_generator.md.j2": """你现在要撰写一部长篇中文小说的一个章节初稿。\n\n# 当前章节计划\n{{ chapter_plan }}\n\n# 上下文包\n{{ context_bundle }}\n\n# 风格规则\n{{ writing_rules }}\n\n# 任务要求\n1. 按章节计划完成本章\n2. 字数范围：{{ min_words }} - {{ max_words }}\n3. 必须有剧情推进，不可空转\n4. 必须保持角色一致性\n5. 必须遵守世界规则\n6. 避免高频 AI 表达和重复套话\n7. 章末需要有钩子，但不要强行悬浮\n8. 战斗、冲突、情感、信息推进都要具体，不空泛\n\n# 特别要求\n- 不要使用过多“仿佛、宛如、恐怖的、可怕的、眼中闪过一丝、心中一凛、不由得”等模板化表达\n- 多通过细节来让情绪成立\n- 不要让所有角色说话方式一样\n- 如果有爽点，要确保有铺垫和释放过程\n\n请直接输出章节正文，不要加说明。\n""",
        "app/prompts/review/consistency_review.md.j2": """你是一位严格的长篇小说一致性编辑。\n\n# 当前章节正文\n{{ chapter_text }}\n\n# 当前故事圣经摘要\n{{ story_bible_summary }}\n\n# 最近章节摘要\n{{ recent_summaries }}\n\n# 当前角色状态\n{{ character_states }}\n\n# 当前活跃伏笔\n{{ active_foreshadowings }}\n\n# 任务\n请严格检查本章是否存在以下问题：\n\n1. 角色人设偏移\n2. 说话口吻不符合角色\n3. 修为/能力/世界规则冲突\n4. 时间线错误\n5. 地点、物品、人物状态矛盾\n6. 提前暴露不该暴露的信息\n7. 伏笔推进不合理\n8. 忘记承接上一章后果\n\n# 输出格式\n请用 Markdown 输出：\n- 总体评价\n- 问题清单（按严重程度排序）\n- 每个问题对应的原文片段\n- 问题原因\n- 修改建议\n- 最终一致性评分（1-10）\n""",
        "app/prompts/review/pacing_review.md.j2": """你是一位擅长网文与长篇叙事节奏的编辑。\n\n# 当前章节正文\n{{ chapter_text }}\n\n# 章节计划\n{{ chapter_plan }}\n\n# 当前章节在全书中的位置\n{{ chapter_position }}\n\n# 任务\n请从节奏角度审查本章：\n\n1. 是否推进足够\n2. 是否有注水感\n3. 是否有过度铺垫\n4. 是否高潮来得太突兀\n5. 是否对话太多但无信息增量\n6. 是否描写太多但无情绪/剧情价值\n7. 章末钩子是否有效\n8. 爽点是否铺垫和释放到位\n\n# 输出格式\n- 总评\n- 节奏问题\n- 可以删减的段落\n- 可以增强的段落\n- 建议的修订方向\n- 节奏评分（1-10）\n""",
        "app/prompts/review/prose_review.md.j2": """你是一位中文小说文风编辑，请识别文本中的 AI 味、重复表达、文风问题。\n\n# 当前章节正文\n{{ chapter_text }}\n\n# 任务\n请检查：\n\n1. 是否存在高频重复词或句式\n2. 是否存在模板化情绪表达\n3. 是否存在空泛描写而缺乏具体细节\n4. 是否所有角色说话像同一个人\n5. 是否存在“为了像小说而像小说”的虚浮语言\n6. 是否有明显的 AI 常见表达残留\n7. 句子节奏是否过于平均、呆板\n8. 感官维度是否单一\n\n# 输出格式\n- 总评\n- 高风险 AI 味表达列表\n- 重复词/句式统计\n- 具体问题片段\n- 去 AI 味建议\n- 文风评分（1-10）\n""",
        "app/prompts/review/reader_review.md.j2": """你现在扮演一位有丰富网文阅读经验的真实读者。\n\n# 当前章节正文\n{{ chapter_text }}\n\n# 背景\n- 这是长篇小说中的连续章节\n- 读者已经看过前文\n- 读者期待既有剧情推进，也有人物情绪与爽点回报\n\n# 请从读者视角回答\n1. 这一章最吸引人的地方是什么\n2. 哪些地方会让人出戏\n3. 哪些地方会让人觉得水\n4. 哪些地方最有追更欲\n5. 章末是否足够让人继续看下一章\n6. 读者最可能吐槽的点是什么\n7. 如果打分，愿意给多少分（1-10）\n\n请使用真实读者口吻，具体直接，不要空泛夸奖。\n""",
        "app/prompts/revision/revise_by_review.md.j2": """你现在要根据评审意见修订一章长篇小说正文。\n\n# 原章节正文\n{{ chapter_text }}\n\n# 评审汇总\n{{ merged_review }}\n\n# 必须保留的内容\n{{ preserve_points }}\n\n# 任务要求\n1. 优先修复严重一致性问题\n2. 修复人设偏差与口吻不稳\n3. 删除或压缩注水段落\n4. 降低 AI 味和重复表达\n5. 保留原有有效剧情推进\n6. 保持章节整体可读性与自然性\n7. 修订后不要明显变成另一种风格\n8. 不要为了润色而引入新设定\n\n请输出修订后的完整章节正文，不要解释修改过程。\n""",
        "app/prompts/revision/de_ai_flavor.md.j2": """你现在的任务不是重写剧情，而是“去 AI 味”。\n\n# 当前章节正文\n{{ chapter_text }}\n\n# 已识别问题\n{{ ai_flavor_issues }}\n\n# 任务\n请在不改变剧情事实、人物关系、章节结构的前提下：\n\n1. 降低模板化表达\n2. 删除或替换重复套话\n3. 增加更自然的句子节奏变化\n4. 让人物说话更像具体的人\n5. 用更具体的动作和细节替代空泛描述\n6. 保持中文网络小说的流畅阅读感\n\n注意：\n- 不要把文字改得过于文艺或晦涩\n- 不要改变情节推进\n- 不要删掉必要信息\n\n请直接输出修订后的完整正文。\n""",
        "app/prompts/extraction/summarize_chapter.md.j2": """请将以下长篇小说章节总结为结构化摘要。\n\n# 章节正文\n{{ chapter_text }}\n\n# 输出要求\n请输出：\n1. 本章发生了什么（100-200字）\n2. 本章关键事件列表\n3. 本章人物状态变化\n4. 本章关系变化\n5. 本章推进的伏笔\n6. 本章新增疑问或悬念\n7. 章末状态\n\n请用 Markdown 输出，便于后续检索。\n""",
        "app/prompts/extraction/extract_state_changes.md.j2": """请从以下章节中提取结构化状态变化。\n\n# 章节正文\n{{ chapter_text }}\n\n# 已知角色与设定\n{{ story_bible_summary }}\n\n# 任务\n请提取：\n1. 角色状态变化\n   - 境界\n   - 伤势\n   - 情绪\n   - 位置\n   - 已知信息变化\n2. 关系变化\n3. 物品状态变化\n4. 伏笔推进\n5. 时间线推进\n6. 新出现的关键事实\n\n# 输出格式\n请严格输出为 YAML。\n""",
        "app/prompts/system/agent_general.md": """你是 NovelOS 系统中的执行代理。\n\n- 以任务为单位执行\n- 所有状态必须文件化、可追踪、可恢复\n- 严格遵守故事圣经与上下文包约束\n- 输出尽量写入指定文件\n""",
        "app/prompts/system/writing_rules.md": """写作规则：\n1. 先读上下文包和章节计划\n2. 不得引入未经批准的新设定\n3. 不得破坏人设与世界规则\n4. 以具体动作与细节替代空泛描写\n5. 减少 AI 套话与重复句式\n""",
        "app/prompts/system/review_rules.md": """评审规则：\n1. 指出具体问题段落\n2. 说明问题类型与原因\n3. 给出可执行的修改建议\n4. 输出评分与风险提示\n""",
        "app/prompts/system/repository_rules.md": """仓库规则：\n1. 不直接修改世界观核心设定\n2. 所有变更需落文件并可追踪\n3. 修订必须基于评审反馈\n4. 不得跳过任务状态流转\n""",
    }
    for rel, content in prompts.items():
        _write_text_if_missing(project_root / rel, content)

    # Story Bible 空白结构
    story_bible_files = {
        "project/story_bible/world.yaml": "world: []\n",
        "project/story_bible/rules.yaml": "rules: []\n",
        "project/story_bible/timeline.yaml": "timeline: []\n",
        "project/story_bible/factions.yaml": "factions: []\n",
        "project/story_bible/locations.yaml": "locations: []\n",
        "project/story_bible/characters.yaml": "characters: []\n",
        "project/story_bible/relationships.yaml": "relationships: []\n",
        "project/story_bible/items.yaml": "items: []\n",
        "project/story_bible/mysteries.yaml": "mysteries: []\n",
        "project/story_bible/foreshadowings.yaml": "foreshadowings: []\n",
        "project/story_bible/themes.yaml": "themes: []\n",
    }
    for rel, content in story_bible_files.items():
        _write_text_if_missing(project_root / rel, content)

    # Outline 与示例章节计划
    _write_text_if_missing(project_root / "project/outlines/book_outline.md", "# 全书大纲\n\n- 待补充\n")
    _write_text_if_missing(project_root / "project/outlines/volume_01.md", "# 第一卷大纲\n\n- 待补充\n")
    _write_text_if_missing(project_root / "project/outlines/chapter_plans/chapter_001.md", "# 第 1 章 规划\n\n- 目标：\n- 冲突：\n- 场景：\n")

    # app 代码骨架
    app_stubs = {
        "app/__init__.py": """\"\"\"NovelOS application package.\"\"\"\n""",
        "app/cli.py": """#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n\"\"\"NovelOS CLI (placeholder).\n\n后续将迁移为 Typer/Click 实现。\n\"\"\"\n\nimport argparse\n\n\ndef main() -> None:\n    parser = argparse.ArgumentParser(description=\"NovelOS CLI\")\n    parser.add_argument(\"command\", nargs=\"?\", default=\"help\")\n    args = parser.parse_args()\n    print(f\"NovelOS CLI not implemented yet. Command: {args.command}\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "app/config.py": """#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n\"\"\"配置读取占位。后续改为 Pydantic schema。\"\"\"\n\nfrom pathlib import Path\n\n\nclass Config:\n    def __init__(self, project_root: str | Path) -> None:\n        self.project_root = Path(project_root)\n\n""",
        "app/constants.py": """# 常量占位\nPROJECT_ROOT_KEY = \"NOVEL_PROJECT_ROOT\"\n""",
        "app/models/__init__.py": """# models package\n""",
        "app/services/__init__.py": """# services package\n""",
        "app/adapters/__init__.py": """# adapters package\n""",
        "app/utils/__init__.py": """# utils package\n""",
    }
    for rel, content in app_stubs.items():
        _write_text_if_missing(project_root / rel, content)

    # scripts 目录占位
    script_stubs = {
        "scripts/init_project.py": """# NovelOS init script placeholder\n""",
        "scripts/build_context.py": """# NovelOS build context placeholder\n""",
        "scripts/create_task.py": """# NovelOS create task placeholder\n""",
        "scripts/apply_changes.py": """# NovelOS apply changes placeholder\n""",
        "scripts/check_consistency.py": """# NovelOS consistency check placeholder\n""",
        "scripts/check_style.py": """# NovelOS style check placeholder\n""",
        "scripts/compile_book.py": """# NovelOS compile book placeholder\n""",
        "scripts/progress_report.py": """# NovelOS progress report placeholder\n""",
        "scripts/rebuild_index.py": """# NovelOS rebuild index placeholder\n""",
        "scripts/migrate_project.py": """# NovelOS migrate project placeholder\n""",
    }
    for rel, content in script_stubs.items():
        _write_text_if_missing(project_root / rel, content)

    # .novelos 状态文件
    _write_json_if_missing(
        project_root / ".novelos/state.json",
        {
            "project": {
                "name": name,
                "slug": slug,
                "language": language,
                "genre": [g.strip() for g in genre.split(",") if g.strip()],
            },
            "progress": {
                "current_chapter": 0,
                "current_volume": 1,
            },
        },
    )

    print(f"NovelOS project initialized at: {project_root}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NovelOS init")
    parser.add_argument("project_dir", help="Project directory")
    parser.add_argument("--name", default="示例长篇小说")
    parser.add_argument("--slug", default="demo_long_novel")
    parser.add_argument("--language", default="zh-CN")
    parser.add_argument("--genre", default="\"玄幻\", \"成长\", \"热血\", \"群像\"")
    parser.add_argument("--target-words", type=int, default=2_000_000)
    parser.add_argument("--target-chapters", type=int, default=800)
    parser.add_argument("--target-volumes", type=int, default=8)
    args = parser.parse_args()

    init_project(
        args.project_dir,
        args.name,
        args.slug,
        args.language,
        args.genre,
        args.target_words,
        args.target_chapters,
        args.target_volumes,
    )


if __name__ == "__main__":
    main()
