# NovelOS Plan Skill

规划小说大纲和章节。

## 使用方式

```
/novelos-plan book              # 规划全书大纲
/novelos-plan volume 1          # 规划第一卷
/novelos-plan chapter 28        # 规划第28章
```

## 子命令

### book - 全书规划

生成全书总纲，包括：
- 核心主题
- 主线冲突
- 角色成长主轴
- 卷结构规划
- 关键转折点
- 伏笔总表

**输入文件**:
- `project/story_bible/bible.yaml`

**输出文件**:
- `project/outlines/book_outline.md`

**Prompt 模板**: `app/prompts/planning/book_planner.md.j2`

### volume - 分卷规划

生成分卷大纲，包括：
- 本卷主题
- 核心冲突
- 章节节点
- 结尾钩子

**输入文件**:
- `project/outlines/book_outline.md`
- `project/story_bible/bible.yaml`

**输出文件**:
- `project/outlines/volume_XX.md`

**Prompt 模板**: `app/prompts/planning/volume_planner.md.j2`

### chapter - 章节规划

生成章节规划，包括：
- 本章目标
- 核心冲突
- 场景分解
- 出场角色
- 章末钩子
- 一致性提醒

**输入文件**:
- `project/outlines/book_outline.md`
- `project/memory/chapter_summaries/` (最近章节摘要)
- `project/story_bible/bible.yaml`

**输出文件**:
- `project/outlines/chapter_plans/chapter_XXXX.md`

**Prompt 模板**: `app/prompts/planning/chapter_planner.md.j2`

## 执行流程

### Step 1: 收集上下文

根据规划类型，读取相关文件：
- 故事圣经
- 已有大纲
- 最近章节摘要

### Step 2: 构建 Prompt

使用对应的 Jinja2 模板，填充上下文数据。

### Step 3: 调用 AI 生成

将构建好的 Prompt 发送给 AI，获取规划内容。

### Step 4: 保存输出

将生成的内容保存到对应文件。

### Step 5: 更新索引

如果有新的伏笔或角色信息，更新故事圣经。

## 注意事项

- 章节规划前，确保故事圣经已完善
- 分卷规划前，确保全书大纲已完成
- 每次规划后，检查与已有内容的一致性
