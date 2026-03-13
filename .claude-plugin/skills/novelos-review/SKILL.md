# NovelOS Review Skill

对章节进行多维度评审。

## 使用方式

```
/novelos-review 28                    # 完整评审第28章
/novelos-review 28 --type consistency # 仅一致性评审
/novelos-review 28 --type pacing      # 仅节奏评审
/novelos-review 28 --type prose       # 仅文风评审
```

## 评审类型

### 1. 一致性评审 (consistency)

检查：
- 角色人设是否偏移
- 说话口吻是否符合角色
- 修为/能力是否合理
- 世界规则是否被违反
- 时间线是否正确
- 地点/物品/人物状态是否矛盾
- 是否提前暴露不该暴露的信息
- 伏笔推进是否合理

**Prompt 模板**: `app/prompts/review/consistency_review.md.j2`

**输出格式**:
```json
{
  "review_type": "consistency",
  "chapter": 28,
  "overall_score": 8.5,
  "issues": [
    {
      "severity": "major",
      "category": "character_ooc",
      "location": "第3段",
      "description": "林墨的说话方式过于直接，与其隐忍性格不符",
      "suggestion": "改为更含蓄的表达方式"
    }
  ]
}
```

### 2. 节奏评审 (pacing)

检查：
- 是否有足够推进
- 是否有注水感
- 铺垫是否过度
- 高潮是否突兀
- 对话是否有信息增量
- 描写是否有情绪价值
- 章末钩子是否有效

**Prompt 模板**: `app/prompts/review/pacing_review.md.j2`

### 3. 文风评审 (prose)

检查：
- 高频重复词或句式
- 模板化情绪表达
- 空泛描写
- AI 常见表达残留
- 句子节奏是否呆板
- 感官维度是否单一

**Prompt 模板**: `app/prompts/review/prose_review.md.j2`

## 执行流程

### Step 1: 读取章节草稿

```python
draft_path = f"project/chapters/drafts/chapter_{chapter:04d}.md"
chapter_text = read_file(draft_path)
```

### Step 2: 读取上下文

```python
story_bible = bible_service.load_bible()
recent_summaries = context_service.get_recent_summaries(chapter)
character_states = bible_service.get_character_states(chapter)
```

### Step 3: 执行各项评审

```python
reviews = []
for review_type in ["consistency", "pacing", "prose"]:
    prompt = build_review_prompt(review_type, chapter_text, context)
    result = call_ai(prompt)
    review = parse_review_result(result)
    reviews.append(review)
    save_review(review)
```

### Step 4: 合并评审结果

```python
merged = merge_reviews(reviews)
save_merged_review(chapter, merged)
```

### Step 5: 输出报告

```
📊 第28章评审报告

┌─────────────────────────────────────┐
│ 总体评分: 7.8/10                    │
├─────────────────────────────────────┤
│ 一致性: 8.5/10                      │
│ 节  奏: 7.5/10                      │
│ 文  风: 7.3/10                      │
├─────────────────────────────────────┤
│ 问题总数: 5                         │
│ 严重问题: 1                         │
│ 重要问题: 2                         │
└─────────────────────────────────────┘

🔴 严重问题:
  - [一致性] 林墨说话方式不符合人设

🟡 重要问题:
  - [节奏] 中段对话信息增量不足
  - [文风] "眼中闪过一丝" 出现3次

📝 建议: 运行 /novelos-revise 28 进行修订
```

## 评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 9-10 | 优秀 | 几乎无问题，可直接定稿 |
| 7-8 | 良好 | 有小问题，建议修订 |
| 5-6 | 一般 | 有明显问题，必须修订 |
| 1-4 | 较差 | 有严重问题，需要重写 |

## 注意事项

- 评审前确保故事圣经完善
- 评审结果保存为 JSON，便于后续处理
- 如果有严重问题，建议立即修订
