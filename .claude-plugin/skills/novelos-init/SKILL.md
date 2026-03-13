# NovelOS Init Skill

初始化一个新的长篇小说项目。

## 使用方式

```
/novelos-init [项目名称]
```

## 功能

1. 创建标准项目目录结构
2. 生成 `novel.yaml` 配置文件
3. 创建故事圣经模板
4. 创建大纲模板
5. 初始化任务队列

## 执行步骤

### Step 1: 确认项目信息

询问用户：
- 项目名称（默认：my_novel）
- 题材类型（默认：玄幻）
- 目标章节数（默认：600）

### Step 2: 创建目录结构

```
project/
├── story_bible/
│   └── bible.yaml
├── outlines/
│   ├── book_outline.md
│   └── chapter_plans/
├── chapters/
│   ├── drafts/
│   ├── revised/
│   └── final/
├── memory/
│   ├── chapter_summaries/
│   └── context/
├── reviews/
└── tasks/
    ├── queue/
    ├── doing/
    ├── done/
    └── failed/
```

### Step 3: 生成配置文件

创建 `novel.yaml`：

```yaml
project:
  name: "{{ project_name }}"
  slug: "{{ slug }}"
  language: "zh-CN"
  genre: ["{{ genre }}"]
  target_words: {{ target_chapters * 3000 }}
  target_chapters: {{ target_chapters }}

writing:
  chapter_word_range: [2500, 5000]
  style_goal: "自然流畅、情绪真实、减少AI味"
  hook_requirement: true

workflow:
  summary_after_each_chapter: true
  consistency_check_after_each_chapter: true
```

### Step 4: 创建初始文件

- `AGENTS.md` - AI Agent 指引
- `CLAUDE.md` - Claude Code 指引
- `.cursorrules` - Cursor 规则

### Step 5: 输出确认

```
✅ 项目初始化完成！

📁 项目位置: {{ project_path }}
📝 下一步:
   1. 编辑 project/story_bible/bible.yaml 定义角色和世界观
   2. 编辑 project/outlines/book_outline.md 规划全书大纲
   3. 运行 /novelos-plan-chapter 1 规划第一章
```

## 注意事项

- 如果目录已存在，询问是否覆盖
- 确保所有文件使用 UTF-8 编码
- 生成的模板包含示例内容，便于用户理解
