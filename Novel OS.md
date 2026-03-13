***

# 一、项目总目标

我要构建一个**长篇小说 AI 工程系统**，不是单次文本生成器，而是一个类似代码工程工具的“小说仓库操作系统”。

它的核心目标不是“一次生成整本书”，而是：

1. 支持百万字级长篇小说的规划、生成、评审、修订、记忆管理
2. 支持世界观、人物、人设、时间线、伏笔的结构化管理
3. 支持按“全书 -> 分卷 -> 章节 -> 场景 -> 段落”的分层方式创作
4. 支持每章生成后自动做摘要、提取状态变化、更新故事圣经
5. 支持评审-修订闭环，减少 AI 味、重复句式、人设崩坏、剧情跑偏
6. 能在 Cursor / Claude Code / Trae / Codex 这类 AI IDE / CLI 环境中作为仓库运行
7. 宿主模型可替换，项目核心不依赖某一特定 API
8. 最终形成一个“小说工程系统”，而不是一次性 prompt 脚本

***

# 二、产品定位

这个系统的定位不是“一个写几段文字的小助手”，而是：

## 产品定位

一个面向 AI IDE / CLI Agent 的长篇小说工程操作系统（Novel Engineering OS）。

## 它的本质

- 一个仓库规范
- 一套数据结构
- 一套脚本工具
- 一套任务状态机
- 一套 prompt 模板
- 一套多轮迭代工作流
- 一套可持续扩展的小说生产流水线

## 它不是什么

- 不是一个只能一次性生成短篇的小工具
- 不是一个靠单 prompt 硬写的脚本
- 不是只会“续写一段话”的聊天机器人
- 不是完全绑定某个大模型 API 的 SaaS

***

# 三、核心理念

## 1. 小说不是一次生成，而是工程化迭代

和代码一样，长篇小说必须：

- 先设计结构
- 再拆解任务
- 再逐章生成
- 再评审
- 再修订
- 再归档
- 再更新记忆和状态

## 2. 生成能力不是核心，状态管理才是核心

真正难的不是“能不能写一章”，而是：

- 写到第 200 章是否还记得第 3 章埋的伏笔
- 角色口吻是否一直稳定
- 时间线是否自洽
- 世界规则是否没崩
- 情绪节奏是否能持续

## 3. 模型是执行器，系统才是大脑

Cursor / Claude Code / Trae / Codex 等可以作为执行器，
但真正决定质量的是：

- 上下文构建
- 数据结构
- 工作流
- 评审机制
- 修订机制
- 记忆系统

## 4. 所有状态必须文件化、可追踪、可恢复

避免依赖单个会话的短暂记忆。
每一步都要：

- 落文件
- 留版本
- 可回滚
- 可审计
- 可继续

## 5. 先做“稳定的 20\~50 章”，再追求百万字

先把流程跑通，建立骨架，再不断增强。

***

# 四、项目代号

**NovelOS**

***

# 五、项目能力边界

## 第一阶段必须解决的能力

1. 项目初始化
2. 故事圣经管理
3. 章节规划
4. 上下文构建
5. 初稿生成
6. 自动摘要
7. 状态变化提取
8. 故事圣经更新
9. 一致性检查
10. 风格和 AI 味检查
11. 修订流程
12. 版本管理

## 第二阶段增强能力

1. 角色 agent 化
2. 多卷统筹
3. 伏笔生命周期管理
4. 节奏控制
5. 多版本候选章
6. 读者反馈模拟
7. 热门套路分析
8. 风格蒸馏
9. 可视化管理面板

## 第三阶段高级能力

1. 自动长期编排
2. 多代理协作写作
3. 更细粒度情绪曲线控制
4. 自动爆点检测
5. 自动反套路设计
6. 多模型/多宿主适配
7. 可训练的偏好反馈系统

***

# 六、标准仓库目录结构

以下是建议的**完整仓库结构**。你可以几乎原样使用。

```txt
NovelOS/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ AGENTS.md
├─ CLAUDE.md
├─ .cursorrules
├─ novel.yaml
├─ requirements.txt
├─ pyproject.toml
├─ docs/
│  ├─ architecture.md
│  ├─ workflow.md
│  ├─ prompt_design.md
│  ├─ data_schema.md
│  ├─ roadmap.md
│  └─ style_guidelines.md
├─ app/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ config.py
│  ├─ constants.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ task.py
│  │  ├─ chapter.py
│  │  ├─ story_bible.py
│  │  ├─ character.py
│  │  ├─ foreshadowing.py
│  │  └─ review.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ file_service.py
│  │  ├─ bible_service.py
│  │  ├─ outline_service.py
│  │  ├─ memory_service.py
│  │  ├─ context_service.py
│  │  ├─ task_service.py
│  │  ├─ review_service.py
│  │  ├─ revision_service.py
│  │  ├─ compile_service.py
│  │  └─ index_service.py
│  ├─ adapters/
│  │  ├─ __init__.py
│  │  ├─ base_adapter.py
│  │  ├─ manual_agent_adapter.py
│  │  ├─ prompt_file_adapter.py
│  │  ├─ cursor_adapter.py
│  │  ├─ claude_code_adapter.py
│  │  ├─ codex_adapter.py
│  │  └─ api_adapter.py
│  ├─ prompts/
│  │  ├─ planning/
│  │  │  ├─ book_planner.md.j2
│  │  │  ├─ volume_planner.md.j2
│  │  │  ├─ chapter_planner.md.j2
│  │  │  └─ scene_planner.md.j2
│  │  ├─ generation/
│  │  │  ├─ chapter_generator.md.j2
│  │  │  ├─ scene_generator.md.j2
│  │  │  ├─ dialogue_generator.md.j2
│  │  │  └─ rewrite_generator.md.j2
│  │  ├─ review/
│  │  │  ├─ consistency_review.md.j2
│  │  │  ├─ pacing_review.md.j2
│  │  │  ├─ prose_review.md.j2
│  │  │  ├─ reader_review.md.j2
│  │  │  └─ foreshadowing_review.md.j2
│  │  ├─ revision/
│  │  │  ├─ revise_by_review.md.j2
│  │  │  ├─ de_ai_flavor.md.j2
│  │  │  ├─ tighten_pacing.md.j2
│  │  │  └─ character_voice_fix.md.j2
│  │  ├─ extraction/
│  │  │  ├─ summarize_chapter.md.j2
│  │  │  ├─ extract_state_changes.md.j2
│  │  │  ├─ extract_entities.md.j2
│  │  │  └─ extract_foreshadowing_updates.md.j2
│  │  └─ system/
│  │     ├─ agent_general.md
│  │     ├─ writing_rules.md
│  │     ├─ review_rules.md
│  │     └─ repository_rules.md
│  └─ utils/
│     ├─ __init__.py
│     ├─ yaml_utils.py
│     ├─ markdown_utils.py
│     ├─ text_utils.py
│     ├─ diff_utils.py
│     └─ path_utils.py
├─ scripts/
│  ├─ init_project.py
│  ├─ build_context.py
│  ├─ create_task.py
│  ├─ apply_changes.py
│  ├─ check_consistency.py
│  ├─ check_style.py
│  ├─ compile_book.py
│  ├─ progress_report.py
│  ├─ rebuild_index.py
│  └─ migrate_project.py
├─ project/
│  ├─ story_bible/
│  │  ├─ world.yaml
│  │  ├─ rules.yaml
│  │  ├─ timeline.yaml
│  │  ├─ factions.yaml
│  │  ├─ locations.yaml
│  │  ├─ characters.yaml
│  │  ├─ relationships.yaml
│  │  ├─ items.yaml
│  │  ├─ mysteries.yaml
│  │  ├─ foreshadowings.yaml
│  │  └─ themes.yaml
│  ├─ outlines/
│  │  ├─ book_outline.md
│  │  ├─ volume_01.md
│  │  ├─ volume_02.md
│  │  ├─ volume_03.md
│  │  └─ chapter_plans/
│  │     ├─ chapter_001.md
│  │     ├─ chapter_002.md
│  │     └─ ...
│  ├─ chapters/
│  │  ├─ drafts/
│  │  ├─ revised/
│  │  ├─ final/
│  │  └─ compiled/
│  ├─ memory/
│  │  ├─ chapter_summaries/
│  │  ├─ volume_summaries/
│  │  ├─ context/
│  │  ├─ event_index/
│  │  ├─ entity_state/
│  │  ├─ retrieval_cache/
│  │  └─ semantic_index/
│  ├─ reviews/
│  │  ├─ consistency/
│  │  ├─ pacing/
│  │  ├─ prose/
│  │  ├─ reader/
│  │  ├─ foreshadowing/
│  │  └─ merged/
│  ├─ revisions/
│  │  ├─ chapter_001/
│  │  ├─ chapter_002/
│  │  └─ ...
│  ├─ tasks/
│  │  ├─ queue/
│  │  ├─ doing/
│  │  ├─ done/
│  │  └─ failed/
│  ├─ exports/
│  │  ├─ txt/
│  │  ├─ epub/
│  │  └─ md/
│  └─ reports/
│     ├─ consistency_reports/
│     ├─ pacing_reports/
│     ├─ style_reports/
│     └─ progress/
└─ .novelos/
   ├─ state.json
   ├─ task_index.db
   ├─ logs/
   ├─ checkpoints/
   └─ cache/
```

***

# 七、项目核心数据结构设计

***

## 1. `novel.yaml`

这是项目总配置文件。

```yaml
project:
  name: "示例长篇小说"
  slug: "demo_long_novel"
  language: "zh-CN"
  genre: ["玄幻", "成长", "热血", "群像"]
  target_words: 2000000
  target_chapters: 800
  target_volumes: 8

writing:
  chapter_word_range: [2500, 5000]
  scene_per_chapter_range: [3, 6]
  pov_mode: "limited-third-person"
  style_goal: "自然流畅、情绪真实、减少AI味、兼顾网文爽点与人物成长"
  hook_requirement: true
  revision_rounds: 2

workflow:
  summary_after_each_chapter: true
  consistency_check_after_each_chapter: true
  global_check_every_n_chapters: 20
  volume_review_every_n_chapters: 50

adapters:
  default: "manual_agent"
  available:
    - "manual_agent"
    - "prompt_file"
    - "cursor"
    - "claude_code"
    - "codex"
    - "api"

quality:
  minimum_review_score: 7.5
  reject_if_character_broken: true
  reject_if_world_rule_conflict: true
  reject_if_ai_flavor_high: true

paths:
  project_root: "./project"
  prompts_root: "./app/prompts"
```

***

## 2. `characters.yaml`

```yaml
characters:
  - id: "char_linmo"
    name: "林墨"
    role: "protagonist"
    gender: "male"
    age_start: 16
    personality_core:
      - "隐忍"
      - "重情"
      - "倔强"
      - "自卑中带有强烈自尊"
    flaws:
      - "不愿轻易求助"
      - "面对亲近之人时容易嘴硬"
    growth_arc: "从边缘少年成长为真正能承担责任的人"
    speech_style:
      tone: "平时克制，熟人前略带少年气"
      habits:
        - "少说空话"
        - "压力大时语气更短"
        - "不喜欢夸张表达"
    secrets:
      - "体内封存着与父亲失踪有关的古老印记"
    current_state:
      realm: "炼气九层"
      location: "青云宗外门"
      health: "左臂旧伤未愈"
      emotion: "压抑但有韧劲"
      known_information:
        - "玉佩会在特定危险时发热"
      unknown_information:
        - "玉佩真正来历"
    first_appearance: 1
    status: "alive"

  - id: "char_suyao"
    name: "苏瑶"
    role: "heroine"
    personality_core:
      - "聪慧"
      - "警惕"
      - "表面冷淡内里温软"
    speech_style:
      tone: "简洁，偶尔带讥诮"
    current_state:
      realm: "筑基初期"
      location: "青云宗内门"
      health: "良好"
      emotion: "对林墨保持观察"
    status: "alive"
```

***

## 3. `foreshadowings.yaml`

```yaml
foreshadowings:
  - id: "f001"
    title: "神秘玉佩的异动"
    planted_at: 1
    description: "林墨佩戴的旧玉佩会在危机中微微发热，似乎与失踪的父亲有关。"
    thread_type: "main_mystery"
    importance: "high"
    status: "active"
    hints:
      - chapter: 1
        content: "初次异动，未解释"
      - chapter: 18
        content: "在宗门禁地附近再次发热"
      - chapter: 53
        content: "苏瑶注意到玉佩纹路异常"
    planned_resolution:
      chapter: 180
      description: "玉佩是远古封印钥匙之一"

  - id: "f002"
    title: "外门长老似乎认识林墨父亲"
    planted_at: 12
    description: "长老见到林墨后神情有异，似乎认出了某种特征"
    thread_type: "identity"
    importance: "medium"
    status: "active"
    hints:
      - chapter: 12
        content: "长老盯着林墨看了很久"
      - chapter: 34
        content: "长老提到'你和那个人很像'"
    planned_resolution:
      chapter: 97
      description: "揭示长老曾是林父旧友"
```

***

## 4. `timeline.yaml`

```yaml
timeline:
  - chapter: 1
    date_marker: "青云历 4321年 初春"
    event: "林墨入宗失败后被留作杂役"
  - chapter: 12
    date_marker: "青云历 4321年 春末"
    event: "外门长老第一次注意到林墨"
  - chapter: 28
    date_marker: "青云历 4321年 夏初"
    event: "宗门预选赛开始"
```

***

## 5. `relationships.yaml`

```yaml
relationships:
  - source: "char_linmo"
    target: "char_suyao"
    type: "potential_romance"
    current_status: "互相试探"
    arc: "警惕 -> 信任 -> 生死相依"
    latest_update_chapter: 27

  - source: "char_linmo"
    target: "char_chenfeng"
    type: "rivalry"
    current_status: "轻视与压制"
    arc: "轻视 -> 冲突升级 -> 正面宿敌"
    latest_update_chapter: 26
```

***

# 八、任务状态机设计

任务必须结构化，避免 AI 会话混乱。

## 任务状态

- queued
- doing
- drafted
- reviewed
- revising
- approved
- finalized
- failed

## 任务类型

- plan\_book
- plan\_volume
- plan\_chapter
- build\_context
- generate\_chapter
- review\_consistency
- review\_pacing
- review\_prose
- review\_reader
- merge\_reviews
- revise\_chapter
- summarize\_chapter
- extract\_changes
- update\_bible
- compile\_volume
- compile\_book

## 示例任务文件 `task_gen_028.json`

```json
{
  "task_id": "gen_chapter_028",
  "type": "generate_chapter",
  "status": "queued",
  "chapter": 28,
  "inputs": {
    "chapter_plan": "project/outlines/chapter_plans/chapter_028.md",
    "context_bundle": "project/memory/context/chapter_028_context.md",
    "rules": "app/prompts/system/writing_rules.md"
  },
  "outputs": {
    "draft": "project/chapters/drafts/chapter_028.md"
  },
  "constraints": {
    "target_words_min": 3000,
    "target_words_max": 4500,
    "must_have_hook": true,
    "must_preserve_character_consistency": true
  }
}
```

***

# 九、章节生产总工作流

***

## 总流程概览

### 阶段 1：规划

1. 生成全书大纲
2. 生成分卷大纲
3. 生成章节规划
4. 生成场景规划

### 阶段 2：生成

1. 构建本章上下文
2. 生成本章初稿

### 阶段 3：评审

1. 做一致性评审
2. 做节奏评审
3. 做文风/AI味评审
4. 做读者体验评审
5. 合并评审意见

### 阶段 4：修订

1. 根据评审进行修订
2. 必要时二次评审

### 阶段 5：归档与记忆更新

1. 生成章节摘要
2. 提取状态变化
3. 更新故事圣经
4. 更新关系、时间线、伏笔状态
5. 存档最终版本

### 阶段 6：全局检查

1. 每 20 章做一次全局一致性检查
2. 每卷末做一次卷级回顾和规划修正

***

# 十、Context Bundle 设计规范

这是整个系统里最值钱的组件之一。

## 目标

在生成每章前，将最需要的上下文压缩为一个主文件，供 AI IDE / Agent 读取，减少乱读和漏读。

## 文件路径

`project/memory/context/chapter_028_context.md`

## 标准结构

```md
# Chapter 028 Context Bundle

## 1. Writing Goal
- 本章目标：宗门预选赛首战，林墨首次在公开场合展现真正战斗天赋
- 必须推进：陈锋开始认真审视林墨；苏瑶产生进一步怀疑
- 不可推进过头：不能直接暴露玉佩秘密

## 2. Placement in Overall Structure
- 当前属于：第一卷中段
- 本卷主题：从边缘到被看见
- 当前节奏：由压抑积累进入首次释放
- 本章情绪基调：紧张 -> 压抑 -> 燃 -> 余波

## 3. Recent Chapter Summaries
### Chapter 025
...
### Chapter 026
...
### Chapter 027
...

## 4. Current Character States
### 林墨
- 境界：炼气九层
- 身体：左臂旧伤未愈
- 当前情绪：克制、压抑、不愿再忍
- 本章行为限制：不能显露超出当前合理认知的全部底牌

### 苏瑶
- 境界：筑基初期
- 当前态度：观察林墨
- 本章作用：旁观、起疑、不表态

### 陈锋
- 境界：筑基初期
- 当前态度：轻视林墨
- 本章作用：被种下危机感

## 5. Active Foreshadowings Relevant to This Chapter
- 神秘玉佩：仅允许轻微异动，不可解释
- 外门长老与林父关系：仅允许长老目光异样，不可摊牌
- 左臂旧伤：可在战斗中带来风险或限制

## 6. Consistency Warnings
- 林墨尚不会公开使用焚天诀第三式
- 苏瑶尚不知玉佩秘密
- 宗门内门弟子不能随意插手外门预选赛

## 7. Scene Suggestions
1. 赛前气氛与众人轻视
2. 对手试探与林墨隐忍
3. 冲突升级与短暂被压制
4. 林墨抓住破绽完成逆转
5. 赛后余波与章末钩子

## 8. Style Instructions
- 战斗描写要具体，不堆词
- 对话要有角色差异
- 避免空泛形容如“恐怖的气息”“可怕的力量”
- 多用动作、触觉、环境反馈代替抽象判断
- 减少固定句式，如“不由得”“心中一凛”“眼中闪过一丝”

## 9. Ending Hook
- 长老看向林墨，神色复杂，低声提到“竟然真像……”
```

***

# 十一、AI IDE 协作说明文件

这些文件很重要，能让 Cursor / Claude Code 更懂你的仓库。

***

## 1. `AGENTS.md`

你可以直接复制。

```md
# AGENTS.md

你是本仓库中的小说工程代理，不是随意聊天助手。

## 你的职责
你需要根据仓库中的文件和任务，协助完成长篇小说的规划、生成、评审、修订和状态更新。

## 基本原则
1. 任何正文生成前，必须先阅读：
   - project/story_bible/
   - 当前章节计划
   - 最近章节摘要
   - 当前章节上下文包
2. 不能跳过一致性约束。
3. 不能擅自修改世界规则和角色核心设定，除非任务明确要求。
4. 每次生成后必须：
   - 产出章节摘要
   - 提取状态变化
   - 更新相关索引或状态文件
5. 所有修订必须基于 reviews/ 中的反馈，不要无目的大改。
6. 优先保持人物稳定、情节清晰、语言自然，而不是盲目堆砌辞藻。
7. 禁止为了“像小说”而过度使用套话、空话和夸张修饰。

## 写作要求
- 章节必须有明确推进，不能原地踏步
- 对话必须区分角色口吻
- 人物情绪应通过动作、停顿、细节来体现，不要只做抽象说明
- 章末尽量保留推动读者继续阅读的钩子
- 避免常见 AI 套路句式和高频模板表达

## 评审要求
评审时要具体指出：
- 哪一段有问题
- 问题类型是什么
- 为什么有问题
- 如何修改更好

## 修改要求
修改时优先：
1. 修复设定错误
2. 修复人设偏差
3. 修复节奏拖沓
4. 修复 AI 味
5. 提升可读性

## 输出要求
- 尽量写入指定文件
- 使用仓库已有格式
- 保持文件命名和目录规范统一
```

***

## 2. `CLAUDE.md`

```md
# CLAUDE.md

这是一个长篇小说工程仓库。

你在本项目中的身份不是单纯写作者，而是“小说工程协作代理”。

## 先读这些文件
1. AGENTS.md
2. novel.yaml
3. docs/architecture.md
4. project/story_bible/*
5. 当前任务文件
6. 当前章节 context bundle

## 工作模式
- 按任务执行
- 生成前先理解结构
- 修改前先看评审
- 更新前先提取变化
- 所有结果写回文件

## 注意事项
- 保持世界观和人物一致性
- 不要自己发明没有依据的重要设定
- 如果上下文不够，优先生成“需要补充信息”的说明，而不是胡写
- 如果发现已有文件冲突，必须显式指出

## 风格底线
- 不要过度 AI 化表达
- 不要堆“震惊、恐怖、可怕、磅礴、仿佛、宛如”这类空泛词
- 不要把所有角色写成同一种说话方式
- 多写具体动作、环境反馈、心理张力
```

***

## 3. `.cursorrules`

```md
You are working inside a long-form novel engineering repository.

Rules:
1. Always inspect project/story_bible, current chapter plan, and memory context before generating text.
2. Never alter world rules or character core traits without explicit instruction.
3. Treat every chapter as part of a large evolving system, not a standalone story.
4. When revising, preserve valid content and only change what is necessary.
5. Prefer concrete sensory details over vague dramatic adjectives.
6. Avoid repetitive AI-style phrases and overused transition patterns.
7. After generating a chapter, also generate:
   - chapter summary
   - state changes
   - possible foreshadowing updates
8. If context is insufficient, say so explicitly and propose the missing files needed.
```

***

# 十二、核心提示词模板总集

下面给你一套可以直接保存为模板的 prompt。

***

## 1. 全书规划提示词

文件：`app/prompts/planning/book_planner.md.j2`

```md
你是一位资深长篇小说架构师，需要为一部长篇中文小说设计全书结构。

# 项目信息
- 作品类型：{{ genre }}
- 目标字数：{{ target_words }}
- 目标章节数：{{ target_chapters }}
- 目标卷数：{{ target_volumes }}
- 风格目标：{{ style_goal }}

# 已知故事设定
{{ story_bible_summary }}

# 任务
请输出一份完整的全书规划，内容包括：

1. 核心主题
2. 主线冲突
3. 主角成长主轴
4. 主要角色关系主轴
5. 全书三到八个关键转折点
6. 分卷思路
7. 全书节奏设计
8. 爽点、压抑、爆发、揭秘的大致分布
9. 至少 10 条伏笔主线
10. 结局方向（开放式/封闭式/阶段性完结）

# 输出格式
请使用 Markdown，包含：
- 全书概述
- 分卷规划
- 主线与支线
- 节奏曲线说明
- 伏笔总表
- 风险提醒（容易崩的地方）
```

***

## 2. 分卷规划提示词

文件：`app/prompts/planning/volume_planner.md.j2`

```md
你是一位资深小说架构师，请为当前长篇小说设计某一卷的大纲。

# 全书信息
{{ book_outline }}

# 当前卷次
第 {{ volume_number }} 卷

# 故事圣经摘要
{{ story_bible_summary }}

# 任务
请输出本卷大纲，包括：

1. 本卷主题
2. 本卷开端状态
3. 本卷核心冲突
4. 本卷主要角色出场安排
5. 本卷要推进或埋下的伏笔
6. 本卷至少 5-10 个关键章节节点
7. 本卷结尾钩子
8. 本卷节奏建议（快慢分布）
9. 本卷最容易写崩的风险点

请保持与全书主线一致，不要脱离故事核心。
```

***

## 3. 章节规划提示词

文件：`app/prompts/planning/chapter_planner.md.j2`

```md
你现在要为长篇小说规划一个具体章节。

# 当前卷大纲
{{ volume_outline }}

# 最近章节摘要
{{ recent_summaries }}

# 当前角色状态
{{ character_states }}

# 当前活跃伏笔
{{ active_foreshadowings }}

# 本章编号
第 {{ chapter_number }} 章

# 任务
请输出本章规划，内容包括：

1. 本章目标
2. 本章在整卷中的作用
3. 本章核心冲突
4. 本章场景分解（3-6 个场景）
5. 每个场景的情绪标签
6. 哪些角色必须出场
7. 哪些信息可以推进，哪些不能暴露
8. 本章结尾钩子
9. 一致性提醒
10. 文风和节奏建议

请用 Markdown 输出。
```

***

## 4. 场景生成提示词

文件：`app/prompts/generation/scene_generator.md.j2`

```md
你现在要写一个长篇小说中的具体场景，而不是整章乱写。

# 场景规划
{{ scene_plan }}

# 当前章节上下文
{{ chapter_context }}

# 当前角色状态
{{ character_states }}

# 风格要求
{{ style_rules }}

# 写作要求
1. 只写这个场景，不要抢写后面的内容
2. 场景必须有明确目标和变化
3. 对话要区分角色口吻
4. 多用具体动作、环境反馈、感官细节
5. 避免空泛形容和常见 AI 套话
6. 不要违反世界规则、人设和时间线
7. 输出为可直接并入正文的自然小说文本

请直接输出正文，不要解释。
```

***

## 5. 章节初稿生成提示词

文件：`app/prompts/generation/chapter_generator.md.j2`

```md
你现在要撰写一部长篇中文小说的一个章节初稿。

# 当前章节计划
{{ chapter_plan }}

# 上下文包
{{ context_bundle }}

# 风格规则
{{ writing_rules }}

# 任务要求
1. 按章节计划完成本章
2. 字数范围：{{ min_words }} - {{ max_words }}
3. 必须有剧情推进，不可空转
4. 必须保持角色一致性
5. 必须遵守世界规则
6. 避免高频 AI 表达和重复套话
7. 章末需要有钩子，但不要强行悬浮
8. 战斗、冲突、情感、信息推进都要具体，不空泛

# 特别要求
- 不要使用过多“仿佛、宛如、恐怖的、可怕的、眼中闪过一丝、心中一凛、不由得”等模板化表达
- 多通过细节来让情绪成立
- 不要让所有角色说话方式一样
- 如果有爽点，要确保有铺垫和释放过程

请直接输出章节正文，不要加说明。
```

***

## 6. 一致性评审提示词

文件：`app/prompts/review/consistency_review.md.j2`

```md
你是一位严格的长篇小说一致性编辑。

# 当前章节正文
{{ chapter_text }}

# 当前故事圣经摘要
{{ story_bible_summary }}

# 最近章节摘要
{{ recent_summaries }}

# 当前角色状态
{{ character_states }}

# 当前活跃伏笔
{{ active_foreshadowings }}

# 任务
请严格检查本章是否存在以下问题：

1. 角色人设偏移
2. 说话口吻不符合角色
3. 修为/能力/世界规则冲突
4. 时间线错误
5. 地点、物品、人物状态矛盾
6. 提前暴露不该暴露的信息
7. 伏笔推进不合理
8. 忘记承接上一章后果

# 输出格式
请用 Markdown 输出：
- 总体评价
- 问题清单（按严重程度排序）
- 每个问题对应的原文片段
- 问题原因
- 修改建议
- 最终一致性评分（1-10）
```

***

## 7. 节奏评审提示词

文件：`app/prompts/review/pacing_review.md.j2`

```md
你是一位擅长网文与长篇叙事节奏的编辑。

# 当前章节正文
{{ chapter_text }}

# 章节计划
{{ chapter_plan }}

# 当前章节在全书中的位置
{{ chapter_position }}

# 任务
请从节奏角度审查本章：

1. 是否推进足够
2. 是否有注水感
3. 是否有过度铺垫
4. 是否高潮来得太突兀
5. 是否对话太多但无信息增量
6. 是否描写太多但无情绪/剧情价值
7. 章末钩子是否有效
8. 爽点是否铺垫和释放到位

# 输出格式
- 总评
- 节奏问题
- 可以删减的段落
- 可以增强的段落
- 建议的修订方向
- 节奏评分（1-10）
```

***

## 8. 文风与 AI 味评审提示词

文件：`app/prompts/review/prose_review.md.j2`

```md
你是一位中文小说文风编辑，请识别文本中的 AI 味、重复表达、文风问题。

# 当前章节正文
{{ chapter_text }}

# 任务
请检查：

1. 是否存在高频重复词或句式
2. 是否存在模板化情绪表达
3. 是否存在空泛描写而缺乏具体细节
4. 是否所有角色说话像同一个人
5. 是否存在“为了像小说而像小说”的虚浮语言
6. 是否有明显的 AI 常见表达残留
7. 句子节奏是否过于平均、呆板
8. 感官维度是否单一

# 输出格式
- 总评
- 高风险 AI 味表达列表
- 重复词/句式统计
- 具体问题片段
- 去 AI 味建议
- 文风评分（1-10）
```

***

## 9. 读者体验评审提示词

文件：`app/prompts/review/reader_review.md.j2`

```md
你现在扮演一位有丰富网文阅读经验的真实读者。

# 当前章节正文
{{ chapter_text }}

# 背景
- 这是长篇小说中的连续章节
- 读者已经看过前文
- 读者期待既有剧情推进，也有人物情绪与爽点回报

# 请从读者视角回答
1. 这一章最吸引人的地方是什么
2. 哪些地方会让人出戏
3. 哪些地方会让人觉得水
4. 哪些地方最有追更欲
5. 章末是否足够让人继续看下一章
6. 读者最可能吐槽的点是什么
7. 如果打分，愿意给多少分（1-10）

请使用真实读者口吻，具体直接，不要空泛夸奖。
```

***

## 10. 综合修订提示词

文件：`app/prompts/revision/revise_by_review.md.j2`

```md
你现在要根据评审意见修订一章长篇小说正文。

# 原章节正文
{{ chapter_text }}

# 评审汇总
{{ merged_review }}

# 必须保留的内容
{{ preserve_points }}

# 任务要求
1. 优先修复严重一致性问题
2. 修复人设偏差与口吻不稳
3. 删除或压缩注水段落
4. 降低 AI 味和重复表达
5. 保留原有有效剧情推进
6. 保持章节整体可读性与自然性
7. 修订后不要明显变成另一种风格
8. 不要为了润色而引入新设定

请输出修订后的完整章节正文，不要解释修改过程。
```

***

## 11. 去 AI 味修订提示词

文件：`app/prompts/revision/de_ai_flavor.md.j2`

```md
你现在的任务不是重写剧情，而是“去 AI 味”。

# 当前章节正文
{{ chapter_text }}

# 已识别问题
{{ ai_flavor_issues }}

# 任务
请在不改变剧情事实、人物关系、章节结构的前提下：

1. 降低模板化表达
2. 删除或替换重复套话
3. 增加更自然的句子节奏变化
4. 让人物说话更像具体的人
5. 用更具体的动作和细节替代空泛描述
6. 保持中文网络小说的流畅阅读感

注意：
- 不要把文字改得过于文艺或晦涩
- 不要改变情节推进
- 不要删掉必要信息

请直接输出修订后的完整正文。
```

***

## 12. 章节摘要提取提示词

文件：`app/prompts/extraction/summarize_chapter.md.j2`

```md
请将以下长篇小说章节总结为结构化摘要。

# 章节正文
{{ chapter_text }}

# 输出要求
请输出：
1. 本章发生了什么（100-200字）
2. 本章关键事件列表
3. 本章人物状态变化
4. 本章关系变化
5. 本章推进的伏笔
6. 本章新增疑问或悬念
7. 章末状态

请用 Markdown 输出，便于后续检索。
```

***

## 13. 状态变化提取提示词

文件：`app/prompts/extraction/extract_state_changes.md.j2`

```md
请从以下章节中提取结构化状态变化。

# 章节正文
{{ chapter_text }}

# 已知角色与设定
{{ story_bible_summary }}

# 任务
请提取：
1. 角色状态变化
   - 境界
   - 伤势
   - 情绪
   - 位置
   - 已知信息变化
2. 关系变化
3. 物品状态变化
4. 伏笔推进
5. 时间线推进
6. 新出现的关键事实

# 输出格式
请严格输出为 YAML。
```

***

# 十三、CLI 命令设计

以下是建议的命令体系。即使你一开始不全部实现，也要先定下来。

***

## 初始化

```bash
novelos init
novelos init my_book
```

## 故事圣经

```bash
novelos bible validate
novelos bible show
novelos bible add-character
novelos bible add-thread
novelos bible update --chapter 028
```

## 规划

```bash
novelos plan book
novelos plan volume --volume 1
novelos plan chapter --chapter 28
novelos plan scene --chapter 28 --scene 2
```

## 上下文

```bash
novelos context build --chapter 28
novelos context show --chapter 28
```

## 任务

```bash
novelos task create --type generate_chapter --chapter 28
novelos task create --type review_consistency --chapter 28
novelos task list
novelos task show gen_chapter_028
novelos task move --id gen_chapter_028 --status doing
```

## 生成

```bash
novelos generate chapter --chapter 28
novelos generate scene --chapter 28 --scene 2
```

## 评审

```bash
novelos review consistency --chapter 28
novelos review pacing --chapter 28
novelos review prose --chapter 28
novelos review reader --chapter 28
novelos review merge --chapter 28
```

## 修订

```bash
novelos revise chapter --chapter 28
novelos revise de-ai --chapter 28
```

## 提取与更新

```bash
novelos summarize chapter --chapter 28
novelos extract changes --chapter 28
novelos apply changes --chapter 28
```

## 编译

```bash
novelos compile volume --volume 1
novelos compile book
```

## 报告

```bash
novelos report progress
novelos report consistency
novelos report style
```

***

# 十四、MVP 实现优先级

***

## P0：必须先做

1. 仓库初始化
2. 故事圣经基础 schema
3. 章节计划文件
4. 上下文构建器
5. 任务文件创建
6. 章节初稿工作流
7. 摘要提取
8. 状态变化提取
9. 故事圣经更新
10. 一致性评审
11. 修订流程

## P1：很重要

1. 文风/AI味评审
2. 节奏评审
3. 评审合并
4. 版本管理
5. 卷级摘要和检查
6. 基础索引检索

## P2：后续增强

1. 语义检索
2. 角色 agent
3. 伏笔调度器
4. 热门套路分析
5. 可视化仪表盘
6. 宿主适配层扩展

***

# 十五、推荐开发顺序

***

## 第 1 周

- 定目录结构
- 定 YAML schema
- 写 `novel.yaml`
- 写 `AGENTS.md`
- 写 `README.md`
- 写基础 CLI

## 第 2 周

- 实现 `init`
- 实现 `plan chapter`
- 实现 `context build`
- 实现 `task create`

## 第 3 周

- 实现 `generate chapter`
- 实现 `summarize chapter`
- 实现 `extract changes`
- 实现 `apply changes`

## 第 4 周

- 实现 `review consistency`
- 实现 `review prose`
- 实现 `revise chapter`

## 第 5 周

- 打通完整一章流水线
- 跑 5\~10 章实验
- 修 schema 和 prompt

## 第 6 周以后

- 做卷级检查
- 做语义检索
- 做风格和节奏增强
- 做宿主适配

***

# 十六、README 初稿模板

你也可以直接复制。

```md
# NovelOS

NovelOS 是一个面向 AI IDE / CLI Agent 的长篇小说工程系统。

它不是单次文本生成器，而是一个用于规划、生成、评审、修订、记忆管理和状态追踪的小说仓库操作系统。

## 核心特点
- 长篇小说仓库化管理
- 故事圣经与角色状态跟踪
- 分层规划：全书 / 分卷 / 章节 / 场景
- 章节级上下文构建
- 多轮评审与修订闭环
- 一致性、节奏、文风、读者体验检查
- 可在 Cursor / Claude Code / Trae / Codex 等环境中协作运行
- 宿主无关，可逐步扩展到 API 或本地模型

## 适用场景
- 百万字网文创作
- 长篇小说工程化管理
- AI 辅助作者写作
- 复杂故事世界观维护
- 多角色、多伏笔、多卷结构小说

## 项目理念
生成不是核心，状态管理和迭代闭环才是核心。

## 当前阶段
MVP：先稳定支持 20~50 章连续创作，维持角色、人设、伏笔和世界规则一致。
```

***

# 十七、给 AI 编程助手的“总任务提示词”

下面这个非常重要。\
你可以直接扔给 Cursor / Claude Code / 任何能写代码的 AI，作为总任务说明。

***

## 总任务提示词（建议保存为 `docs/master_prompt.md`）

```md
我需要你作为资深软件架构师和产品工程师，帮我开发一个名为 NovelOS 的项目。

# 项目目标
NovelOS 是一个“长篇小说工程系统”，不是简单的文本生成器。

它需要支持：
1. 故事圣经管理（世界观、人物、关系、时间线、伏笔）
2. 分层规划（全书 -> 分卷 -> 章节 -> 场景）
3. 章节上下文构建
4. 章节生成工作流
5. 章节评审（包括一致性、节奏、文风、读者体验）
6. 修订闭环
7. 摘要与状态变化提取
8. 自动更新故事圣经
9. 文件化任务状态管理
10. 宿主无关的架构设计，可在 Cursor / Claude Code / Codex / Trae 中作为仓库运行

# 核心原则
1. 所有状态必须文件化、可恢复、可追踪
2. 生成只是工作流的一部分，不是全部
3. 长篇小说的核心难题是状态管理和一致性，不是单次生成
4. 项目必须优先支持本地仓库工作流，再考虑外部 API
5. 提示词、脚本、数据结构都要模块化，便于后续升级
6. 必须兼容后续加入不同 adapter

# 你现在需要做的事
请按照以下优先级开发：
1. 项目目录结构
2. 基础 CLI
3. Pydantic 数据模型
4. YAML/Markdown 文件读写工具
5. 项目初始化脚手架
6. 章节计划与上下文构建
7. 任务文件创建和状态流转
8. 章节生成的 prompt 文件输出
9. 章节摘要和状态变化提取的 prompt 文件输出
10. 故事圣经更新逻辑
11. 一致性评审和修订流程

# 技术要求
- Python
- CLI 使用 Typer 或 Click
- 数据模型使用 Pydantic
- 配置和状态优先使用 YAML / JSON / Markdown / SQLite
- 代码结构清晰，可测试，可扩展
- 对于宿主模型适配，先实现 manual_agent_adapter 和 prompt_file_adapter

# 重要要求
1. 先不要过度追求复杂前端
2. 优先把仓库工作流跑通
3. 先实现 MVP 可生成和维护 10~20 章
4. 每个模块都要有清晰职责
5. 写出 README、示例配置、示例 story_bible、示例 chapter_plan
6. 所有代码尽量可直接运行，不要只给伪代码
7. 生成时，先列出开发计划，再按文件逐步创建

请先给出：
1. 整体架构说明
2. 模块拆分
3. 第一阶段要创建的文件清单
4. 然后开始逐文件生成代码
```

***

# 十八、给 AI 的“改造现有 GitHub 项目”提示词

等你找到一个开源底座后，用这个提示词。

```md
我准备基于一个现有 GitHub 开源项目改造成 NovelOS。

你的任务不是简单重命名项目，而是进行系统级重构。

# 改造目标
把当前项目改造成一个“长篇小说工程系统”，支持：
- 故事圣经
- 长篇记忆
- 分层规划
- 章节上下文构建
- 评审与修订闭环
- 状态提取与更新
- 宿主无关 adapter 设计

# 请先做这些事
1. 分析当前仓库结构
2. 识别哪些模块可以保留
3. 识别哪些模块必须重写
4. 给出重构路线图
5. 按照 NovelOS 的架构迁移目录结构
6. 先实现 MVP 必需模块
7. 保持代码可运行，不要只输出概念

# 改造原则
- 保留有价值的基础设施
- 重构不适合长篇小说工程的部分
- 强化数据结构、状态管理、工作流控制
- 先做本地仓库运行能力，再考虑更多模型接入

请先输出：
1. 当前仓库评估报告
2. 保留/重写建议
3. 重构分阶段计划
4. 第一批要修改的文件列表
```

***

# 十九、如何正确使用这整套资料

你现在最好的使用方式不是一次性全扔给 AI 然后等奇迹，而是：

## 方法 1：先喂“总设计”

先给：

- 项目目标
- 仓库结构
- 核心理念
- 数据结构
- 工作流

让 AI 理解全局。

## 方法 2：再喂“具体任务”

比如先让它：

- 建仓库脚手架
- 写 CLI
- 写 schema
- 写 prompt 模板
- 写示例 story\_bible

## 方法 3：最后喂“改造目标”

如果你选了一个 GitHub 项目作为底座，再让 AI 进行迁移。

***

# 二十、你下一步最该做什么

我建议你立刻做 4 件事：

### 1. 新建一个仓库目录

就叫 `NovelOS`

### 2. 把我上面这份内容保存成几个文件

至少保存：

- `docs/master_spec.md`
- `docs/master_prompt.md`
- `AGENTS.md`
- `README.md`

### 3. 先让 AI 帮你做最小骨架

目标不是一次性完成全部，而是先生成：

- 目录结构
- 基础 CLI
- `novel.yaml`
- 示例 story\_bible
- 示例 chapter plan
- context builder

### 4. 先跑通“一章完整流水线”

只要你能做到：

- 规划一章
- 生成一章
- 评审一章
- 修订一章
- 更新故事圣经

这个项目就已经真正起飞了。

***

# 最后一个一句话版总纲

**NovelOS 的核心不是“让 AI 替你写小说”，而是“把长篇小说创作变成一个像软件工程一样可规划、可拆解、可追踪、可评审、可修订、可持续迭代的仓库系统”，而模型只是执行器，不是系统本身。**
