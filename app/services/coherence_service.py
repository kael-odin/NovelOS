"""
章节连贯性服务
负责检查章节之间的连贯性，防止重复场景、时间线错误等问题
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .file_service import FileService


class CoherenceIssueType(Enum):
    DUPLICATE_SCENE = "duplicate_scene"
    BROKEN_CONTINUITY = "broken_continuity"
    TIMELINE_ERROR = "timeline_error"
    CHARACTER_STATE_MISMATCH = "character_state_mismatch"
    LOCATION_ERROR = "location_error"
    MISSING_TRANSITION = "missing_transition"
    REDUNDANT_CONTENT = "redundant_content"


@dataclass
class CoherenceIssue:
    issue_type: CoherenceIssueType
    severity: str  # critical, major, minor
    description: str
    location: str
    suggestion: str
    related_chapters: List[int] = field(default_factory=list)


class CoherenceService:
    """章节连贯性检查服务"""
    
    def __init__(self, project_path: str = "project"):
        self.fs = FileService(project_path)
        self.project_root = Path(project_path)
        self.similarity_threshold = 0.7  # 相似度阈值
    
    def check_chapter_coherence(self, chapter: int) -> List[CoherenceIssue]:
        """检查指定章节的连贯性"""
        issues = []
        
        chapter_content = self._load_chapter(chapter)
        if not chapter_content:
            return issues
        
        # 1. 检查与上一章的衔接
        prev_chapter = self._load_chapter(chapter - 1)
        if prev_chapter:
            issues.extend(self._check_continuity(prev_chapter, chapter_content, chapter))
        
        # 2. 检查与所有已有章节的重复
        issues.extend(self._check_duplicates(chapter_content, chapter))
        
        # 3. 检查时间线一致性
        issues.extend(self._check_timeline(chapter_content, chapter))
        
        # 4. 检查角色状态一致性
        issues.extend(self._check_character_states(chapter_content, chapter))
        
        return issues
    
    def check_all_chapters(self) -> Dict[int, List[CoherenceIssue]]:
        """检查所有章节的连贯性"""
        all_issues = {}
        
        chapters = self._list_chapters()
        for ch in chapters:
            issues = self.check_chapter_coherence(ch)
            if issues:
                all_issues[ch] = issues
        
        return all_issues
    
    def _check_continuity(self, prev_content: str, curr_content: str, chapter: int) -> List[CoherenceIssue]:
        """检查与上一章的衔接"""
        issues = []
        
        # 获取上一章的结尾
        prev_ending = self._extract_chapter_ending(prev_content)
        # 获取当前章节的开头
        curr_start = self._extract_chapter_start(curr_content)
        
        # 检查场景是否突然跳跃
        if not self._is_smooth_transition(prev_ending, curr_start):
            issues.append(CoherenceIssue(
                issue_type=CoherenceIssueType.MISSING_TRANSITION,
                severity="major",
                description=f"第{chapter-1}章结尾与第{chapter}章开头衔接不自然",
                location=f"第{chapter}章开头",
                suggestion="添加过渡场景或调整章节衔接",
                related_chapters=[chapter - 1, chapter]
            ))
        
        # 检查角色位置是否合理
        prev_location = self._extract_ending_location(prev_content)
        curr_location = self._extract_starting_location(curr_content)
        
        if prev_location and curr_location and prev_location != curr_location:
            # 检查是否有位置变化的描述
            if not self._has_location_transition(curr_content, prev_location, curr_location):
                issues.append(CoherenceIssue(
                    issue_type=CoherenceIssueType.LOCATION_ERROR,
                    severity="major",
                    description=f"位置从'{prev_location}'突然变为'{curr_location}'，缺少过渡",
                    location=f"第{chapter}章开头",
                    suggestion="添加位置变化的描述",
                    related_chapters=[chapter - 1, chapter]
                ))
        
        return issues
    
    def _check_duplicates(self, content: str, chapter: int) -> List[CoherenceIssue]:
        """检查与已有章节的重复内容"""
        issues = []
        
        all_chapters = self._list_chapters()
        for ch in all_chapters:
            if ch >= chapter:
                continue
            
            other_content = self._load_chapter(ch)
            if not other_content:
                continue
            
            # 检查场景重复
            duplicate_scenes = self._find_duplicate_scenes(content, other_content)
            for scene in duplicate_scenes:
                issues.append(CoherenceIssue(
                    issue_type=CoherenceIssueType.DUPLICATE_SCENE,
                    severity="critical",
                    description=f"与第{ch}章存在重复场景：{scene['description'][:50]}...",
                    location=f"第{chapter}章",
                    suggestion="删除或修改重复内容，确保每章有独特内容",
                    related_chapters=[ch, chapter]
                ))
            
            # 检查对话重复
            duplicate_dialogues = self._find_duplicate_dialogues(content, other_content)
            for dialogue in duplicate_dialogues:
                issues.append(CoherenceIssue(
                    issue_type=CoherenceIssueType.REDUNDANT_CONTENT,
                    severity="major",
                    description=f"与第{ch}章存在重复对话",
                    location=f"第{chapter}章",
                    suggestion="修改对话内容或删除重复部分",
                    related_chapters=[ch, chapter]
                ))
        
        return issues
    
    def _check_timeline(self, content: str, chapter: int) -> List[CoherenceIssue]:
        """检查时间线一致性"""
        issues = []
        
        # 获取故事圣经中的时间线
        timeline = self._load_timeline()
        if not timeline:
            return issues
        
        # 检查章节中的时间标记
        time_markers = self._extract_time_markers(content)
        
        for marker in time_markers:
            # 检查是否与时间线一致
            if not self._is_timeline_consistent(marker, timeline, chapter):
                issues.append(CoherenceIssue(
                    issue_type=CoherenceIssueType.TIMELINE_ERROR,
                    severity="major",
                    description=f"时间标记'{marker}'与时间线不一致",
                    location=f"第{chapter}章",
                    suggestion="调整时间标记或更新时间线",
                    related_chapters=[chapter]
                ))
        
        return issues
    
    def _check_character_states(self, content: str, chapter: int) -> List[CoherenceIssue]:
        """检查角色状态一致性"""
        issues = []
        
        # 获取角色状态
        character_states = self._load_character_states()
        if not character_states:
            return issues
        
        # 检查章节中角色的状态
        for char_id, state in character_states.items():
            char_name = state.get("name", char_id)
            
            # 检查角色是否出现在不应该出现的位置
            if char_name in content:
                expected_location = state.get("location", "")
                current_location = self._extract_character_location(content, char_name)
                
                if expected_location and current_location and expected_location != current_location:
                    issues.append(CoherenceIssue(
                        issue_type=CoherenceIssueType.CHARACTER_STATE_MISMATCH,
                        severity="major",
                        description=f"角色'{char_name}'应该在'{expected_location}'，但出现在'{current_location}'",
                        location=f"第{chapter}章",
                        suggestion="调整角色位置或更新角色状态",
                        related_chapters=[chapter]
                    ))
        
        return issues
    
    def _load_chapter(self, chapter: int) -> Optional[str]:
        """加载章节内容"""
        path = f"chapters/drafts/chapter_{chapter:04d}.md"
        if not self.fs.exists(path):
            return None
        try:
            return self.fs.read_text(path)
        except UnicodeDecodeError:
            # 尝试使用不同的编码
            full_path = self.project_root / path
            return full_path.read_text(encoding="utf-8", errors="ignore")
    
    def _list_chapters(self) -> List[int]:
        """列出所有章节"""
        chapters = []
        path = self.project_root / "chapters" / "drafts"
        if not path.exists():
            return chapters
        
        for f in path.glob("chapter_*.md"):
            match = re.search(r"chapter_(\d+)", f.name)
            if match:
                chapters.append(int(match.group(1)))
        
        return sorted(chapters)
    
    def _extract_chapter_ending(self, content: str, lines: int = 20) -> str:
        """提取章节结尾"""
        paragraphs = content.strip().split("\n\n")
        return "\n\n".join(paragraphs[-3:]) if len(paragraphs) >= 3 else content
    
    def _extract_chapter_start(self, content: str, lines: int = 20) -> str:
        """提取章节开头"""
        paragraphs = content.strip().split("\n\n")
        return "\n\n".join(paragraphs[:3]) if len(paragraphs) >= 3 else content
    
    def _is_smooth_transition(self, prev_ending: str, curr_start: str) -> bool:
        """检查章节衔接是否平滑"""
        # 提取上一章结尾的关键信息
        prev_chars = self._extract_characters(prev_ending)
        prev_location = self._extract_location(prev_ending)
        prev_action = self._extract_last_action(prev_ending)
        
        # 提取当前章节开头的关键信息
        curr_chars = self._extract_characters(curr_start)
        curr_location = self._extract_location(curr_start)
        curr_action = self._extract_first_action(curr_start)
        
        # 检查是否有共同元素
        char_overlap = bool(set(prev_chars) & set(curr_chars))
        location_match = prev_location == curr_location if prev_location and curr_location else True
        
        return char_overlap or location_match
    
    def _extract_characters(self, text: str) -> List[str]:
        """提取文本中的角色名"""
        # 简单实现：查找常见的中文名字模式
        pattern = r"[\u4e00-\u9fa5]{2,4}"
        matches = re.findall(pattern, text)
        return list(set(matches))[:10]  # 返回前10个可能的名字
    
    def _extract_location(self, text: str) -> Optional[str]:
        """提取文本中的位置"""
        location_patterns = [
            r"在(.{2,10})(里|中|外|旁)",
            r"来到(.{2,10})",
            r"到达(.{2,10})",
            r"位于(.{2,10})",
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_ending_location(self, content: str) -> Optional[str]:
        """提取章节结尾的位置"""
        ending = self._extract_chapter_ending(content)
        return self._extract_location(ending)
    
    def _extract_starting_location(self, content: str) -> Optional[str]:
        """提取章节开头位置"""
        start = self._extract_chapter_start(content)
        return self._extract_location(start)
    
    def _has_location_transition(self, content: str, from_loc: str, to_loc: str) -> bool:
        """检查是否有位置变化的描述"""
        transition_patterns = [
            f"离开{from_loc}",
            f"前往{to_loc}",
            f"来到{to_loc}",
            f"到达{to_loc}",
            "走", "跑", "移动", "离开", "前往",
        ]
        
        start = self._extract_chapter_start(content)
        for pattern in transition_patterns:
            if pattern in start:
                return True
        
        return False
    
    def _find_duplicate_scenes(self, content1: str, content2: str) -> List[Dict[str, Any]]:
        """查找重复场景"""
        duplicates = []
        
        # 提取场景描述
        scenes1 = self._extract_scenes(content1)
        scenes2 = self._extract_scenes(content2)
        
        for s1 in scenes1:
            for s2 in scenes2:
                similarity = self._calculate_similarity(s1["text"], s2["text"])
                if similarity > self.similarity_threshold:
                    duplicates.append({
                        "description": s1["text"][:100],
                        "similarity": similarity,
                        "location1": s1.get("location", ""),
                        "location2": s2.get("location", ""),
                    })
        
        return duplicates
    
    def _extract_scenes(self, content: str) -> List[Dict[str, Any]]:
        """提取场景"""
        scenes = []
        paragraphs = content.split("\n\n")
        
        for i, p in enumerate(paragraphs):
            if len(p) > 100:  # 只考虑较长的段落
                scenes.append({
                    "text": p,
                    "index": i,
                    "location": f"段落{i+1}",
                })
        
        return scenes
    
    def _find_duplicate_dialogues(self, content1: str, content2: str) -> List[Dict[str, Any]]:
        """查找重复对话"""
        duplicates = []
        
        dialogues1 = self._extract_dialogues(content1)
        dialogues2 = self._extract_dialogues(content2)
        
        for d1 in dialogues1:
            for d2 in dialogues2:
                similarity = self._calculate_similarity(d1, d2)
                if similarity > self.similarity_threshold:
                    duplicates.append({
                        "dialogue": d1[:50],
                        "similarity": similarity,
                    })
        
        return duplicates
    
    def _extract_dialogues(self, text: str) -> List[str]:
        """提取对话"""
        # 支持多种引号格式
        patterns = [
            r"[""「『]([^""」』]+)[""」』]",  # 中文引号
            r'"([^"]+)"',  # 英文引号
        ]
        
        dialogues = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            dialogues.extend([m for m in matches if len(m) > 10])
        
        return dialogues
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _extract_time_markers(self, content: str) -> List[str]:
        """提取时间标记"""
        patterns = [
            r"\d+年",
            r"\d+月",
            r"\d+日",
            r"第\d+天",
            r"[\u4e00-\u9fa5]+历\d+年",
            "今天", "昨天", "明天",
            "早上", "中午", "下午", "晚上", "深夜",
        ]
        
        markers = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            markers.extend(matches)
        
        return list(set(markers))
    
    def _load_timeline(self) -> Optional[Dict[str, Any]]:
        """加载时间线"""
        path = "story_bible/bible.yaml"
        if not self.fs.exists(path):
            return None
        
        content = self.fs.read_yaml(path)
        return content.get("timeline", [])
    
    def _is_timeline_consistent(self, marker: str, timeline: List[Dict], chapter: int) -> bool:
        """检查时间标记是否与时间线一致"""
        # 简单实现：检查时间标记是否在合理范围内
        # 实际实现需要更复杂的时间线逻辑
        return True
    
    def _load_character_states(self) -> Dict[str, Dict]:
        """加载角色状态"""
        path = "story_bible/bible.yaml"
        if not self.fs.exists(path):
            return {}
        
        content = self.fs.read_yaml(path)
        characters = content.get("characters", [])
        
        return {c.get("id", c.get("name", "")): c for c in characters}
    
    def _extract_character_location(self, content: str, char_name: str) -> Optional[str]:
        """提取角色在文本中的位置"""
        # 查找角色名附近的地点描述
        pattern = f"{char_name}.{{0,50}}(里|中|外|旁|来到|到达|位于)"
        match = re.search(pattern, content)
        if match:
            return self._extract_location(match.group(0))
        return None
    
    def _extract_last_action(self, text: str) -> Optional[str]:
        """提取最后一个动作"""
        action_patterns = [
            r"(\w+了)",
            r"(\w+着)",
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[-1]
        
        return None
    
    def _extract_first_action(self, text: str) -> Optional[str]:
        """提取第一个动作"""
        action_patterns = [
            r"(\w+了)",
            r"(\w+着)",
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def generate_coherence_report(self, chapter: int) -> str:
        """生成连贯性报告"""
        issues = self.check_chapter_coherence(chapter)
        
        if not issues:
            return f"# 第{chapter}章连贯性检查报告\n\n✅ 未发现问题"
        
        lines = [
            f"# 第{chapter}章连贯性检查报告",
            "",
            f"发现 {len(issues)} 个问题",
            "",
        ]
        
        # 按严重程度分组
        critical = [i for i in issues if i.severity == "critical"]
        major = [i for i in issues if i.severity == "major"]
        minor = [i for i in issues if i.severity == "minor"]
        
        if critical:
            lines.append("## 🔴 严重问题")
            for issue in critical:
                lines.append(f"- [{issue.issue_type.value}] {issue.description}")
                lines.append(f"  - 位置：{issue.location}")
                lines.append(f"  - 建议：{issue.suggestion}")
            lines.append("")
        
        if major:
            lines.append("## 🟡 重要问题")
            for issue in major:
                lines.append(f"- [{issue.issue_type.value}] {issue.description}")
                lines.append(f"  - 位置：{issue.location}")
                lines.append(f"  - 建议：{issue.suggestion}")
            lines.append("")
        
        if minor:
            lines.append("## 🟢 轻微问题")
            for issue in minor:
                lines.append(f"- [{issue.issue_type.value}] {issue.description}")
            lines.append("")
        
        return "\n".join(lines)
