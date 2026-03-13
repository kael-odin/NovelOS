# NovelOS 架构文档

## 概述

NovelOS 是一个面向 AI IDE / CLI Agent 的长篇小说工程系统。它的核心不是"一次生成整本书"，而是支持百万字级长篇小说的规划、生成、评审、修订、记忆管理和状态追踪。

## 核心设计理念

### 1. 小说是工程，不是单次生成
长篇小说必须像软件工程一样：
- 先设计结构
- 再拆解任务
- 再逐章生成
- 再评审
- 再修订
- 再归档
- 再更新记忆和状态

### 2. 状态管理是核心
真正难的不是"能不能写一章"，而是：
- 写到第 200 章是否还记得第 3 章埋的伏笔
- 角色口吻是否一直稳定
- 时间线是否自洽
- 世界规则是否没崩

### 3. 所有状态必须文件化
避免依赖单个会话的短暂记忆。每一步都要：
- 落文件
- 留版本
- 可回滚
- 可审计
- 可继续

## 目录结构

```
NovelOS/
├── novel.yaml              # 项目配置
├── AGENTS.md               # AI Agent 指引
├── CLAUDE.md               # Claude Code 指引
├── .cursorrules            # Cursor 规则
├── app/                    # 应用代码
│   ├── models/             # Pydantic 数据模型
│   ├── services/           # 服务层
│   ├── adapters/           # 宿主适配器
│   ├── prompts/            # Prompt 模板
│   └── utils/              # 工具函数
├── project/                # 项目数据
│   ├── story_bible/        # 故事圣经
│   ├── outlines/           # 大纲
│   ├── chapters/           # 章节
│   ├── memory/             # 记忆系统
│   ├── reviews/            # 评审记录
│   └── tasks/              # 任务队列
└── .novelos/               # 系统状态
```

## 核心模块

### 1. 数据模型 (app/models/)
- `Task`: 任务模型
- `Chapter`: 章节模型
- `StoryBible`: 故事圣经模型
- `Review`: 评审模型

### 2. 服务层 (app/services/)
- `FileService`: 文件操作
- `BibleService`: 故事圣经管理
- `OutlineService`: 大纲管理
- `ContextService`: 上下文构建
- `TaskService`: 任务管理
- `ReviewService`: 评审管理
- `RevisionService`: 修订管理

### 3. Prompt 模板 (app/prompts/)
- `planning/`: 规划模板
- `generation/`: 生成模板
- `review/`: 评审模板
- `revision/`: 修订模板
- `extraction/`: 提取模板
- `system/`: 系统规则

## 工作流

### 章节生产流程

```
1. 规划
   └─> novelos plan chapter --chapter 28

2. 构建上下文
   └─> novelos context build --chapter 28

3. 生成初稿
   └─> novelos generate chapter --chapter 28

4. 评审
   └─> novelos review consistency --chapter 28
   └─> novelos review pacing --chapter 28
   └─> novelos review prose --chapter 28
   └─> novelos review merge --chapter 28

5. 修订
   └─> novelos revise chapter --chapter 28

6. 摘要与更新
   └─> novelos summarize chapter --chapter 28
```

## 任务状态机

```
queued -> doing -> drafted -> reviewed -> revising -> approved -> finalized
                    │                      │
                    └──────────────────────┴──> failed
```

## Context Bundle 设计

Context Bundle 是章节生成的核心输入，包含：

1. **Writing Goal**: 本章目标
2. **Placement**: 在全书中的位置
3. **Recent Summaries**: 最近章节摘要
4. **Character States**: 当前角色状态
5. **Active Foreshadowings**: 活跃伏笔
6. **Consistency Warnings**: 一致性警告
7. **Style Instructions**: 风格指引

## 与 AI IDE 的协作

NovelOS 设计为与 AI IDE（Cursor / Claude Code / Trae / Codex）协作：

1. **AGENTS.md**: 定义 AI Agent 的职责和规则
2. **CLAUDE.md**: Claude Code 专用指引
3. **.cursorrules**: Cursor 规则文件
4. **Prompt 模板**: Jinja2 模板，供 AI 读取和执行

## 扩展性

### 宿主适配器
支持多种执行环境：
- `manual_agent`: 人工执行
- `prompt_file`: 输出 prompt 文件
- `cursor`: Cursor IDE 集成
- `claude_code`: Claude Code 集成
- `api`: API 调用

### 题材模板
支持多种网文题材：
- 玄幻/修仙
- 都市异能
- 古言
- 悬疑
- 等等
