import re
from typing import List, Dict, Any, Optional


def extract_headings(text: str, level: int = 2) -> List[Dict[str, Any]]:
    pattern = r"^(#{%d})\s+(.+)$" % level
    matches = re.findall(pattern, text, re.MULTILINE)
    return [{"level": level, "title": m[1]} for m in matches]


def extract_sections(text: str) -> List[Dict[str, Any]]:
    pattern = r"^(#{1,6})\s+(.+?)$\n([\s\S]*?)(?=^#{1,6}\s|\Z)"
    matches = re.findall(pattern, text, re.MULTILINE)
    return [
        {"level": len(m[0]), "title": m[1].strip(), "content": m[2].strip()}
        for m in matches
    ]


def extract_frontmatter(text: str) -> Dict[str, Any]:
    if not text.startswith("---"):
        return {}
    
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    
    import yaml
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    if match:
        return text[match.end():]
    return text


def add_frontmatter(text: str, metadata: Dict[str, Any]) -> str:
    import yaml
    frontmatter = yaml.dump(metadata, allow_unicode=True, default_flow_style=False)
    return f"---\n{frontmatter}---\n\n{text}"


def extract_links(text: str) -> List[Dict[str, str]]:
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    matches = re.findall(pattern, text)
    return [{"text": m[0], "url": m[1]} for m in matches]


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    pattern = r"```(\w*)\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    return [{"language": m[0] or "text", "code": m[1]} for m in matches]


def word_count(text: str) -> int:
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return chinese_chars + english_words


def estimate_reading_time(text: str, wpm: int = 300) -> int:
    words = word_count(text)
    return max(1, words // wpm)
