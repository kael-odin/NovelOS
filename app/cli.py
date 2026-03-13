#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NovelOS CLI 入口"""

import click
from pathlib import Path
from typing import Optional

from .services import FileService, BibleService, OutlineService, ContextService, TaskService, ReviewService, RevisionService
from .services.coherence_service import CoherenceService
from .models import Task, TaskStatus, TaskType


from .workflow import workflow as workflow_group


def get_project_root() -> Path:
    root = Path.cwd()
    while root != root.parent:
        if (root / "novel.yaml").exists() or (root / "projects").exists():
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
    revision = RevisionService(fs)
    coherence = CoherenceService(str(root))
    return {
        "fs": fs,
        "bible": bible,
        "outline": outline,
        "context": context,
        "tasks": tasks,
        "review": review,
        "revision": revision,
        "coherence": coherence,
    }


@click.group()
@click.version_option(version="1.0.0", prog_name="NovelOS")
def cli():
    """NovelOS - 长篇小说工程系统"""
    pass


@cli.group()
def init():
    """初始化项目"""
    pass


@init.command()
@click.argument("project_name", required=False, default="my_novel")
@click.option("--genre", "-g", default="玄幻", help="题材类型")
@click.option("--target-chapters", "-c", default=600, help="目标章节数")
def project(project_name: str, genre: str, target_chapters: int):
    """初始化新项目"""
    project_path = Path.cwd() / project_name
    fs = FileService(project_path)
    
    config = {
        "project": {
            "name": project_name,
            "slug": project_name.lower().replace(" ", "_"),
            "language": "zh-CN",
            "genre": [genre],
            "target_words": target_chapters * 3000,
            "target_chapters": target_chapters,
            "target_volumes": (target_chapters - 1) // 50 + 1,
        },
        "writing": {
            "chapter_word_range": [2500, 5000],
            "scene_per_chapter_range": [3, 6],
            "pov_mode": "limited-third-person",
            "style_goal": "自然流畅、情绪真实、减少AI味",
            "hook_requirement": True,
            "revision_rounds": 2,
        },
        "workflow": {
            "summary_after_each_chapter": True,
            "consistency_check_after_each_chapter": True,
            "global_check_every_n_chapters": 20,
        },
    }
    
    fs.write_yaml("novel.yaml", config)
    fs.write_text("project/story_bible/bible.yaml", "# 故事圣经\n")
    fs.write_text("project/outlines/book_outline.md", "# 总纲\n\n## 卷结构\n")
    
    click.echo(f"✅ 项目已初始化: {project_path}")
    click.echo("📝 下一步: 编辑 novel.yaml 和 project/story_bible/")


@cli.group()
def bible():
    """故事圣经管理"""
    pass


@bible.command()
def validate():
    """验证故事圣经"""
    services = get_services()
    b = services["bible"]
    
    issues = b.validate()
    if issues:
        click.echo("⚠️ 发现问题:")
        for issue in issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("✅ 故事圣经验证通过")


@bible.command()
def show():
    """显示故事圣经摘要"""
    services = get_services()
    b = services["bible"]
    
    summary = b.get_summary()
    click.echo(summary)


@cli.group()
def plan():
    """规划命令"""
    pass


@plan.command()
@click.option("--volume", "-v", type=int, help="卷号")
@click.option("--chapter", "-c", type=int, help="章节号")
def generate(volume: Optional[int], chapter: Optional[int]):
    """生成规划"""
    services = get_services()
    
    if chapter:
        click.echo(f"📝 生成第{chapter}章规划...")
        click.echo(f"   输出: project/outlines/chapter_plans/chapter_{chapter:04d}.md")
    elif volume:
        click.echo(f"📝 生成第{volume}卷规划...")
        click.echo(f"   输出: project/outlines/volume_{volume:02d}.md")
    else:
        click.echo("📝 生成全书规划...")
        click.echo("   输出: project/outlines/book_outline.md")


@cli.group()
def context():
    """上下文命令"""
    pass


@context.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def build(chapter: int):
    """构建章节上下文"""
    services = get_services()
    
    click.echo(f"📝 构建第{chapter}章上下文...")
    
    ctx = services["context"].build_context(chapter)
    services["context"].save_context(chapter, ctx)
    
    click.echo(f"✅ 上下文已保存: project/memory/context/chapter_{chapter:04d}_context.md")


@context.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def show(chapter: int):
    """显示章节上下文"""
    services = get_services()
    
    ctx = services["context"].load_context(chapter)
    if ctx:
        click.echo(ctx.get("raw", "未找到上下文"))
    else:
        click.echo(f"⚠️ 未找到第{chapter}章的上下文")


@cli.group()
def task():
    """任务管理"""
    pass


@task.command()
@click.option("--type", "-t", type=click.Choice(["generate", "review", "revise", "summarize"]), required=True, help="任务类型")
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def create(type: str, chapter: int):
    """创建任务"""
    services = get_services()
    
    task_type_map = {
        "generate": TaskType.GENERATE_CHAPTER,
        "review": TaskType.REVIEW_CONSISTENCY,
        "revise": TaskType.REVISE_CHAPTER,
        "summarize": TaskType.SUMMARIZE_CHAPTER,
    }
    
    task = Task(
        task_id=f"{type}_{chapter:04d}",
        task_type=task_type_map[type],
        chapter=chapter,
    )
    
    services["tasks"].save_task(task)
    click.echo(f"✅ 任务已创建: {task.task_id}")


@task.command()
def list():
    """列出所有任务"""
    services = get_services()
    
    tasks = services["tasks"].list_tasks()
    if not tasks:
        click.echo("📭 没有待处理任务")
        return
    
    for task in tasks:
        status_icon = "⏳" if task.status == TaskStatus.QUEUED else "🔄"
        click.echo(f"{status_icon} {task.task_id} [{task.task_type.value}]")


@cli.group()
def generate():
    """生成命令"""
    pass


@generate.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def chapter(chapter: int):
    """生成章节初稿"""
    services = get_services()
    
    click.echo(f"📝 生成第{chapter}章初稿...")
    click.echo(f"   输入: 上下文包、章节规划、写作规则")
    click.echo(f"   输出: project/chapters/drafts/chapter_{chapter:04d}.md")


@cli.group()
def review():
    """评审命令"""
    pass


@review.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
@click.option("--type", "-t", type=click.Choice(["consistency", "pacing", "prose", "all"]), default="all", help="评审类型")
def chapter(chapter: int, type: str):
    """评审章节"""
    services = get_services()
    
    click.echo(f"📝 评审第{chapter}章 ({type})...")
    click.echo(f"   输入: project/chapters/drafts/chapter_{chapter:04d}.md")
    click.echo(f"   输出: project/reviews/")


@review.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def merge(chapter: int):
    """合并评审意见"""
    services = get_services()
    
    merged = services["review"].merge_reviews(chapter)
    
    if not merged:
        click.echo("⚠️ 未找到评审记录")
        return
    
    services["review"].save_merged_review(chapter, merged)
    
    click.echo(f"✅ 评审已合并:")
    click.echo(f"   总分: {merged['overall_score']}/10")
    click.echo(f"   问题: {merged['total_issues']} 个")
    click.echo(f"   严重: {merged['critical_count']} 个")


@cli.group()
def revise():
    """修订命令"""
    pass


@revise.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def chapter(chapter: int):
    """修订章节"""
    services = get_services()
    
    merged = services["review"].load_merged_review(chapter)
    
    if not merged:
        click.echo("⚠️ 请先完成评审")
        return
    
    click.echo(f"📝 请根据评审意见修订章节:")
    click.echo(f"   草稿: project/chapters/drafts/chapter_{chapter:04d}.md")
    click.echo(f"   输出: project/chapters/revised/chapter_{chapter:04d}.md")
    click.echo(f"   问题数: {merged['total_issues']}")


@cli.group()
def summarize():
    """摘要命令"""
    pass


@summarize.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def chapter(chapter: int):
    """生成章节摘要"""
    services = get_services()
    
    draft_path = f"project/chapters/drafts/chapter_{chapter:04d}.md"
    
    if not services["fs"].exists(draft_path):
        click.echo(f"⚠️ 未找到草稿: {draft_path}")
        return
    
    click.echo(f"📝 请生成章节摘要:")
    click.echo(f"   输入: {draft_path}")
    click.echo(f"   输出: project/memory/chapter_summaries/chapter_{chapter:04d}.md")


@cli.group()
def coherence():
    """连贯性检查"""
    pass


@coherence.command()
@click.option("--chapter", "-c", type=int, help="检查指定章节")
@click.option("--all", "-a", is_flag=True, help="检查所有章节")
def check(chapter: Optional[int], all: bool):
    """检查章节连贯性"""
    services = get_services()
    coherence_svc = services["coherence"]
    
    if all:
        click.echo("🔍 检查所有章节连贯性...")
        all_issues = coherence_svc.check_all_chapters()
        
        total_issues = sum(len(issues) for issues in all_issues.values())
        
        if not all_issues:
            click.echo("✅ 所有章节连贯性检查通过")
        else:
            click.echo(f"\n⚠️ 发现 {total_issues} 个连贯性问题:")
            for ch, issues in all_issues.items():
                click.echo(f"\n第{ch}章: {len(issues)} 个问题")
                for issue in issues[:3]:
                    click.echo(f"  - [{issue.severity}] {issue.description[:50]}...")
    elif chapter:
        click.echo(f"🔍 检查第{chapter}章连贯性...")
        issues = coherence_svc.check_chapter_coherence(chapter)
        
        if not issues:
            click.echo(f"✅ 第{chapter}章连贯性检查通过")
        else:
            click.echo(f"\n⚠️ 发现 {len(issues)} 个问题:")
            for issue in issues:
                click.echo(f"\n[{issue.severity}] {issue.issue_type.value}")
                click.echo(f"  描述: {issue.description}")
                click.echo(f"  位置: {issue.location}")
                click.echo(f"  建议: {issue.suggestion}")
    else:
        click.echo("请指定 --chapter 或 --all")


@coherence.command()
@click.option("--chapter", "-c", type=int, required=True, help="章节号")
def report(chapter: int):
    """生成连贯性报告"""
    services = get_services()
    coherence_svc = services["coherence"]
    
    report_text = coherence_svc.generate_coherence_report(chapter)
    click.echo(report_text)


@cli.command()
def status():
    """显示项目状态"""
    services = get_services()
    
    config = services["fs"].read_yaml("novel.yaml")
    project = config.get("project", {})
    
    click.echo(f"📖 项目: {project.get('name', '未命名')}")
    click.echo(f"📚 题材: {', '.join(project.get('genre', []))}")
    click.echo(f"🎯 目标: {project.get('target_chapters', 0)} 章")
    
    drafts = list(services["fs"].list_files("project/chapters/drafts", "*.md"))
    revised = list(services["fs"].list_files("project/chapters/revised", "*.md"))
    final = list(services["fs"].list_files("project/chapters/final", "*.md"))
    
    click.echo(f"\n📊 进度:")
    click.echo(f"   草稿: {len(drafts)} 章")
    click.echo(f"   修订: {len(revised)} 章")
    click.echo(f"   定稿: {len(final)} 章")


cli.add_command(workflow_group, name="workflow")


if __name__ == "__main__":
    cli()


def generate():
    """生成命令入口"""
    pass


def review():
    """评审命令入口"""
    pass


def revise():
    """修订命令入口"""
    pass


def summarize():
    """摘要命令入口"""
    pass


def coherence():
    """连贯性检查命令入口"""
    pass


def bible():
    """故事圣经命令入口"""
    pass


def plan():
    """规划命令入口"""
    pass


def context():
    """上下文命令入口"""
    pass


def task():
    """任务命令入口"""
    pass
