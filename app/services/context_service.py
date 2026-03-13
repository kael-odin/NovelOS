from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .file_service import FileService
from .bible_service import BibleService


class ContextService:
    def __init__(self, file_service: FileService, bible_service: BibleService):
        self.fs = file_service
        self.bible = bible_service
    
    def build_context(self, chapter: int) -> Dict[str, Any]:
        context = {
            "meta": {
                "chapter": chapter,
                "created_at": datetime.now().isoformat(),
            },
            "writing_goal": self._build_writing_goal(chapter),
            "placement": self._build_placement(chapter),
            "recent_summaries": self._load_recent_summaries(chapter, window=3),
            "character_states": self._build_character_states(chapter),
            "active_foreshadowings": self._build_active_foreshadowings(chapter),
            "consistency_warnings": self._build_consistency_warnings(chapter),
            "scene_suggestions": self._build_scene_suggestions(chapter),
            "style_instructions": self._build_style_instructions(),
        }
        return context
    
    def save_context(self, chapter: int, context: Dict[str, Any]) -> None:
        path = f"project/memory/context/chapter_{chapter:04d}_context.md"
        content = self._render_context_markdown(context)
        self.fs.write_text(path, content)
    
    def load_context(self, chapter: int) -> Optional[Dict[str, Any]]:
        path = f"project/memory/context/chapter_{chapter:04d}_context.md"
        if not self.fs.exists(path):
            return None
        content = self.fs.read_text(path)
        return {"raw": content, "chapter": chapter}
    
    def _build_writing_goal(self, chapter: int) -> Dict[str, Any]:
        chapter_plan = self._load_chapter_plan(chapter)
        return {
            "chapter": chapter,
            "plan": chapter_plan,
            "must_advance": [],
            "must_not_reveal": [],
        }
    
    def _build_placement(self, chapter: int) -> Dict[str, Any]:
        return {
            "volume": (chapter - 1) // 50 + 1,
            "position_in_volume": (chapter - 1) % 50 + 1,
            "stage": self._get_story_stage(chapter),
            "rhythm": "building" if chapter % 10 < 7 else "climax",
        }
    
    def _get_story_stage(self, chapter: int) -> str:
        if chapter <= 30:
            return "opening"
        elif chapter <= 100:
            return "rising"
        elif chapter <= 200:
            return "development"
        else:
            return "climax"
    
    def _load_chapter_plan(self, chapter: int) -> str:
        path = f"project/outlines/chapter_plans/chapter_{chapter:04d}.md"
        return self.fs.read_text(path)
    
    def _load_recent_summaries(self, chapter: int, window: int = 3) -> List[Dict[str, Any]]:
        summaries = []
        for ch in range(max(1, chapter - window), chapter):
            path = f"project/memory/chapter_summaries/chapter_{ch:04d}.md"
            if self.fs.exists(path):
                summaries.append({
                    "chapter": ch,
                    "summary": self.fs.read_text(path)[:500],
                })
        return summaries
    
    def _build_character_states(self, chapter: int) -> List[Dict[str, Any]]:
        characters = self.bible.get_all_characters()
        states = []
        for char in characters[:10]:
            states.append({
                "id": char.id,
                "name": char.name,
                "role": char.role,
                "current_state": char.current_state,
                "speech_style": char.speech_style,
            })
        return states
    
    def _build_active_foreshadowings(self, chapter: int) -> List[Dict[str, Any]]:
        foreshadowings = self.bible.get_active_foreshadowings()
        relevant = []
        for f in foreshadowings:
            if f.planted_at <= chapter:
                if f.planned_resolution.get("chapter", 999) >= chapter:
                    relevant.append({
                        "id": f.id,
                        "title": f.title,
                        "description": f.description,
                        "importance": f.importance,
                        "hints": f.hints,
                    })
        return relevant[:5]
    
    def _build_consistency_warnings(self, chapter: int) -> List[str]:
        warnings = []
        protagonist = self.bible.get_protagonist()
        if protagonist:
            state = protagonist.current_state
            if state.get("realm"):
                warnings.append(f"主角当前境界：{state.get('realm')}")
            if state.get("location"):
                warnings.append(f"主角当前位置：{state.get('location')}")
        return warnings
    
    def _build_scene_suggestions(self, chapter: int) -> List[str]:
        return [
            "开场：建立场景与氛围",
            "发展：推进剧情与冲突",
            "高潮：本章核心事件",
            "收尾：章末钩子",
        ]
    
    def _build_style_instructions(self) -> Dict[str, Any]:
        return {
            "tone": "自然流畅",
            "avoid": [
                "恐怖的气息",
                "可怕的力量",
                "眼中闪过一丝",
                "心中一凛",
                "不由得",
            ],
            "prefer": [
                "具体动作描写",
                "环境反馈",
                "感官细节",
            ],
        }
    
    def _render_context_markdown(self, context: Dict[str, Any]) -> str:
        lines = [
            f"# Chapter {context['meta']['chapter']} Context Bundle",
            "",
            "## 1. Writing Goal",
        ]
        
        goal = context.get("writing_goal", {})
        if goal.get("plan"):
            lines.append(f"- 章节计划：{goal['plan'][:200]}...")
        
        lines.extend([
            "",
            "## 2. Placement in Overall Structure",
        ])
        placement = context.get("placement", {})
        lines.append(f"- 当前卷：第{placement.get('volume', 1)}卷")
        lines.append(f"- 故事阶段：{placement.get('stage', 'unknown')}")
        
        lines.extend([
            "",
            "## 3. Recent Chapter Summaries",
        ])
        for s in context.get("recent_summaries", []):
            lines.append(f"### Chapter {s['chapter']}")
            lines.append(s["summary"][:300] + "...")
        
        lines.extend([
            "",
            "## 4. Current Character States",
        ])
        for c in context.get("character_states", []):
            lines.append(f"### {c['name']}")
            state = c.get("current_state", {})
            for k, v in state.items():
                lines.append(f"- {k}: {v}")
        
        lines.extend([
            "",
            "## 5. Active Foreshadowings",
        ])
        for f in context.get("active_foreshadowings", []):
            lines.append(f"- [{f['importance']}] {f['title']}: {f['description'][:100]}")
        
        lines.extend([
            "",
            "## 6. Consistency Warnings",
        ])
        for w in context.get("consistency_warnings", []):
            lines.append(f"- {w}")
        
        lines.extend([
            "",
            "## 7. Style Instructions",
        ])
        style = context.get("style_instructions", {})
        lines.append(f"- 避免：{', '.join(style.get('avoid', []))}")
        lines.append(f"- 推荐：{', '.join(style.get('prefer', []))}")
        
        return "\n".join(lines)
