# NovelOS Revise Skill

根据评审意见修订章节。

## 使用方式

```
/novelos-revise 28           # 修订第28章
/novelos-revise 28 --round 2 # 第二轮修订
```

## 前置条件

1. 章节草稿已存在: `project/chapters/drafts/chapter_0028.md`
2. 评审结果已存在: `project/reviews/merged_chapter_0028.json`

如果评审不存在，自动执行：
- `/novelos-review 28`

## 执行流程

### Step 1: 读取输入

```python
draft = read_file(f"project/chapters/drafts/chapter_{chapter:04d}.md")
merged_review = read_json(f"project/reviews/merged_chapter_{chapter:04d}.json")
```

### Step 2: 提取保留点

从评审中提取亮点和高分段落，修订时保留。

### Step 3: 构建 Prompt

使用模板 `app/prompts/revision/revise_by_review.md.j2`：

```jinja2
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
...
```

### Step 4: 调用 AI 修订

将 Prompt 发送给 AI，获取修订后的正文。

### Step 5: 保存修订稿

```python
revised_path = f"project/chapters/revised/chapter_{chapter:04d}.md"
write_file(revised_path, revised_content)
```

### Step 6: 更新任务状态

```python
task_service.move_task(f"gen_chapter_{chapter:04d}", TaskStatus.REVISING)
```

### Step 7: 输出确认

```
✅ 第28章已修订！

📄 文件: project/chapters/revised/chapter_0028.md
📊 字数: 3,389 字 (原: 3,456 字)

🔧 修改摘要:
   - 修复: 林墨说话方式
   - 删减: 中段注水对话
   - 优化: AI 味表达

📝 下一步:
   1. 运行 /novelos-review 28 重新评审
   2. 或运行 /novelos-finalize 28 定稿
```

## 修订策略

### 优先级排序

1. **Critical**: 必须修复
   - 设定冲突
   - 人设崩坏
   - 逻辑漏洞

2. **Major**: 应该修复
   - 节奏拖沓
   - 信息重复
   - 表达生硬

3. **Minor**: 建议修复
   - 用词优化
   - 细节润色

### 保留原则

- 高分段落保留
- 有效剧情保留
- 独特表达保留

## 多轮修订

如果修订后评分仍低于 7.5：
1. 重新评审
2. 针对新问题修订
3. 最多 2 轮修订

## 注意事项

- 修订时不要引入新问题
- 保持章节整体风格一致
- 不要为了润色而改变剧情
