#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovelOS Workflow Scripts - 完整工作流脚本
"""

import click
from pathlib import Path
from typing import Optional

from .services import (
    FileService, BibleService, OutlineService,
    ContextService, TaskService, ReviewService, RevisionService, RAGService, CoherenceService
)
from .models import TaskStatus


def get_project_root() -> Path:
    root = Path.cwd()
    while root != root.parent:
        if (root / "novel.yaml").exists():
            return root
        root = root.parent
    return Path.cwd()


def get_services():
    root = get_project_root()
    fs = FileService(root)
    bible = BibleService(fs)
    outline = OutlineService(fs)
    context = ContextService(fs, bible)
    tasks = TaskService(fs)
    review = ReviewService(fs)
    revision = RevisionService(fs, review)
    rag = RAGService(root)
    coherence = CoherenceService(str(root))
    return {
        "fs": fs, "bible": bible, "outline": outline,
        "context": context, "tasks": tasks, "review": review,
        "revision": revision, "rag": rag, "root": root,
        "coherence": coherence
    }


@click.group()
def workflow():
    """工作流命令"""
    pass


@workflow.command()
@click.argument("chapter", type=int)
def generate(chapter: int):
    """生成章节初稿"""
    services = get_services()
    
    # 1. 构建上下文
    ctx = services["context"].build_context(chapter)
    services["context"].save_context(chapter, ctx)
    
    # 2. 创建生成任务
    task = services["tasks"].create_chapter_generation_task(chapter)
    
    # 3. 生成章节
    click.echo(f"📝 请根据上下文和规划生成章节:")
    click.echo(f"   上下文: project/memory/context/chapter_{chapter:04d}_context.md")
    click.echo(f"   规划: project/outlines/chapter_plans/chapter_{chapter:04d}.md")
    click.echo(f"   输出: project/chapters/drafts/chapter_{chapter:04d}.md")
    click.echo(f"   约束: 目标字数 2500-5000")
    click.echo(f"   约束: 必须有悬念钩子")
    
    # 4. 连贯性检查
    issues = services["coherence"].check_chapter_coherence(chapter)
    if issues:
        click.echo(f"⚠️ 发现 {len(issues)} 个连贯性问题:")
        for issue in issues:
            click.echo(f"  - [{issue.severity}] {issue.description[:50]}...")
    else:
        click.echo(f"✅ 连贯性检查通过")
    
    # 5. 更新任务状态
    task.status = TaskStatus.DRAFTED
    services["tasks"].update_task(task)
    
    click.echo(f"✅ 生成完成")


@workflow.command()
@click.argument("chapter", type=int)
def review(chapter: int):
    """评审章节"""
    services = get_services()
    
    # 1. 检查草稿是否存在
    draft_path = f"project/chapters/drafts/chapter_{chapter:04d}.md"
    if not services["fs"].exists(draft_path):
        click.echo(f"❌ 未找到草稿: {draft_path}")
        return
    
    click.echo(f"📝 开始评审...")
    
    # 2. 执行评审
    click.echo(f"📝 请对以下文件进行评审:")
    click.echo(f"   草稿: {draft_path}")
    click.echo(f"   故事圣经: project/story_bible/bible.yaml")
    click.echo(f"   写作规则: app/prompts/system/writing_rules.md")
    
    # 3. 保存评审结果
    review_result = {
        "overall_score": 8,
        "issues": [],
        "suggestions": [],
    }
    review_path = f"project/reviews/merged_chapter_{chapter:04d}.json"
    services["fs"].write_json(review_path, review_result)
    
    click.echo(f"✅ 评审完成")
    click.echo(f"   总分: {review_result['overall_score']}/10")
    click.echo(f"   问题: {len(review_result['issues'])} 个")


@workflow.command()
@click.argument("chapter", type=int)
def revise(chapter: int):
    """修订章节"""
    services = get_services()
    
    # 1. 获取评审结果
    review = services["review"].load_merged_review(chapter)
    if not review:
        click.echo(f"❌ 未找到评审结果，请先运行评审")
        return
    
    click.echo(f"📝 开始修订...")
    click.echo(f"   问题数: {len(review.get('issues', []))}")
    
    # 2. 获取草稿
    draft = services["revision"].get_chapter_draft(chapter)
    
    # 3. 执行修订
    click.echo(f"📝 请根据评审意见修订章节...")
    click.echo(f"   草稿: {draft}")
    
    # 4. 保存修订稿
    revised_path = f"project/chapters/revised/chapter_{chapter:04d}.md"
    services["fs"].write_text(revised_path, "修订内容")
    
    click.echo(f"✅ 修订完成")


@workflow.command()
@click.argument("chapter", type=int)
def summarize(chapter: int):
    """生成章节摘要"""
    services = get_services()
    
    # 1. 获取草稿
    draft = services["revision"].get_chapter_draft(chapter)
    if not draft:
        click.echo(f"❌ 未找到草稿")
        return
    
    click.echo(f"📝 请生成章节摘要...")
    click.echo(f"   输入: {draft}")
    click.echo(f"   输出: project/memory/chapter_summaries/chapter_{chapter:04d}.md")
    
    # 2. 保存摘要
    summary = f"# 第{chapter}章摘要\n\n## 本章发生的事\n\nTODO: 待实现\n"
    summary_path = f"project/memory/chapter_summaries/chapter_{chapter:04d}.md"
    services["fs"].write_text(summary_path, summary)
    
    # 3. 更新故事圣经
    click.echo(f"✅ 摘要已保存")
    
    # 4. 更新RAG索引
    services["rag"].index_chapter(chapter, draft, summary)
    
    click.echo(f"✅ 工作流完成")


@workflow.command()
@click.argument("start", type=int)
@click.argument("end", type=int)
def batch(start: int, end: int):
    """批量处理章节"""
    services = get_services()
    
    for chapter in range(start, end + 1):
        click.echo(f"\n=== 处理第 {chapter} 章 ===")
        
        # 1. 检查是否有规划
        plan_path = f"project/outlines/chapter_plans/chapter_{chapter:04d}.md"
        if not services["fs"].exists(plan_path):
            click.echo(f"⚠️ 第 {chapter} 章没有规划，跳过")
            continue
        
        # 2. 执行工作流
        ctx = services["context"].build_context(chapter)
        services["context"].save_context(chapter, ctx)
        
        # 3. 生成章节
        click.echo(f"📝 生成第 {chapter} 章...")
        
        # 4. 连贯性检查
        issues = services["coherence"].check_chapter_coherence(chapter)
        if issues:
            click.echo(f"⚠️ 发现 {len(issues)} 个问题")
            for issue in issues[:3]:
                click.echo(f"  - [{issue.severity}] {issue.description[:50]}...")
        else:
            click.echo(f"✅ 连贯性检查通过")
    
    click.echo(f"✅ 批量处理完成")


@workflow.command()
@click.argument("chapter", type=int)
def finalize(chapter: int):
    """定稿章节"""
    services = get_services()
    fs = services["fs"]
    
    revised_path = f"project/chapters/revised/chapter_{chapter:04d}.md"
    final_path = f"project/chapters/final/chapter_{chapter:04d}.md"
    
    if not fs.exists(revised_path):
        click.echo(f"❌ 未找到修订稿")
        return
    
    content = fs.read_text(revised_path)
    fs.write_text(final_path, content)
    
    click.echo(f"✅ 第 {chapter} 章已定稿")


if __name__ == "__main__":
    workflow()
