# NovelOS Context Skill

构建章节上下文包。

## 使用方式

```
/novelos-context build 28    # 构建第28章上下文
/novelos-context show 28     # 显示第28章上下文
```

## 上下文包结构

```markdown
# Chapter 28 Context Bundle

## 1. Writing Goal
- 章节计划摘要
- 必须推进的内容
- 不能暴露的信息

## 2. Placement in Overall Structure
- 当前卷：第1卷
- 卷内位置：第28章/50章
- 故事阶段：rising
- 节奏建议：building

## 3. Recent Chapter Summaries
### Chapter 27
[摘要内容...]

### Chapter 26
[摘要内容...]

## 4. Current Character States
### 林墨
- 境界: 炼气九层
- 位置: 青云宗外门
- 情绪: 压抑但有韧劲

### 苏瑶
- 境界: 筑基初期
- 位置: 青云宗内门
- 情绪: 对林墨保持观察

## 5. Active Foreshadowings
- [high] 神秘玉佩的异动 (planted: ch1)
- [medium] 外门长老异样 (planted: ch12)

## 6. Consistency Warnings
- 主角当前境界：炼气九层
- 主角当前位置：青云宗外门
- 玉佩的秘密不能在本章揭示

## 7. Style Instructions
- 避免：恐怖的气息、可怕的力量、眼中闪过一丝...
- 推荐：具体动作描写、环境反馈、感官细节
```

## 执行流程

### Step 1: 收集数据

```python
# 章节规划
chapter_plan = outline_service.get_chapter_plan(chapter)

# 最近摘要
recent_summaries = []
for ch in range(max(1, chapter - 3), chapter):
    summary = read_file(f"project/memory/chapter_summaries/chapter_{ch:04d}.md")
    if summary:
        recent_summaries.append({"chapter": ch, "summary": summary})

# 角色状态
bible = bible_service.load_bible()
character_states = [
    {
        "id": c.id,
        "name": c.name,
        "current_state": c.current_state
    }
    for c in bible.characters[:10]
]

# 活跃伏笔
active_foreshadowings = bible.get_active_foreshadowings()

# 一致性警告
consistency_warnings = build_consistency_warnings(bible, chapter)
```

### Step 2: 构建上下文

```python
context = {
    "meta": {"chapter": chapter, "created_at": datetime.now().isoformat()},
    "writing_goal": {...},
    "placement": {...},
    "recent_summaries": recent_summaries,
    "character_states": character_states,
    "active_foreshadowings": [...],
    "consistency_warnings": consistency_warnings,
    "style_instructions": {...}
}
```

### Step 3: 渲染 Markdown

```python
markdown = render_context_markdown(context)
```

### Step 4: 保存上下文包

```python
write_file(f"project/memory/context/chapter_{chapter:04d}_context.md", markdown)
```

## 一致性警告生成

```python
def build_consistency_warnings(bible, chapter):
    warnings = []
    
    protagonist = bible.get_protagonist()
    if protagonist:
        state = protagonist.current_state
        if state.get("realm"):
            warnings.append(f"主角当前境界：{state['realm']}")
        if state.get("location"):
            warnings.append(f"主角当前位置：{state['location']}")
    
    for f in bible.foreshadowings:
        if f.status == "active" and f.importance == "high":
            if f.planned_resolution.get("chapter", 999) > chapter:
                warnings.append(f"伏笔「{f.title}」不能在本章揭示")
    
    return warnings
```

## 注意事项

- 上下文包是章节生成的关键输入
- 确保所有数据都是最新的
- 如果缺少摘要，提示用户先生成
