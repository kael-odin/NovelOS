# NovelOS Write Skill

生成章节正文。

## 使用方式

```
/novelos-write 28              # 生成第28章
/novelos-write 28 --force      # 强制重新生成
```

## 前置条件

1. 章节规划已存在: `project/outlines/chapter_plans/chapter_0028.md`
2. 上下文包已构建: `project/memory/context/chapter_0028_context.md`

如果不存在，自动执行：
- `/novelos-plan chapter 28`
- `/novelos-context build 28`

## 执行流程

### Step 1: 检查前置条件

```python
chapter = 28
plan_path = f"project/outlines/chapter_plans/chapter_{chapter:04d}.md"
context_path = f"project/memory/context/chapter_{chapter:04d}_context.md"

if not exists(plan_path):
    run_skill("novelos-plan", ["chapter", str(chapter)])

if not exists(context_path):
    run_skill("novelos-context", ["build", str(chapter)])
```

### Step 2: 读取输入文件

```python
chapter_plan = read_file(plan_path)
context_bundle = read_file(context_path)
writing_rules = read_file("app/prompts/system/writing_rules.md")
```

### Step 3: 构建 Prompt

使用模板 `app/prompts/generation/chapter_generator.md.j2`：

```jinja2
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
...
```

### Step 4: 调用 AI 生成

将 Prompt 发送给 AI，获取章节正文。

### Step 5: 保存草稿

```python
draft_path = f"project/chapters/drafts/chapter_{chapter:04d}.md"
write_file(draft_path, generated_content)
```

### Step 6: 创建任务

```python
task = Task(
    task_id=f"gen_chapter_{chapter:04d}",
    type=TaskType.GENERATE_CHAPTER,
    chapter=chapter,
    status=TaskStatus.DRAFTED
)
task_service.create_task(task)
```

### Step 7: 输出确认

```
✅ 第28章草稿已生成！

📄 文件: project/chapters/drafts/chapter_0028.md
📊 字数: 3,456 字

📝 下一步:
   1. 运行 /novelos-review 28 进行评审
   2. 或直接编辑草稿后运行 /novelos-revise 28
```

## 质量检查

生成后自动检查：
- [ ] 字数是否在目标范围内
- [ ] 是否有明显的 AI 味表达
- [ ] 是否有重复段落
- [ ] 章末是否有钩子

## 注意事项

- 生成前确保故事圣经和章节规划完善
- 生成后建议立即进行评审
- 如果生成质量不佳，可以指定 `--force` 重新生成
