import re
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher, unified_diff


def split_into_paragraphs(text: str) -> List[str]:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


def split_into_sentences(text: str) -> List[str]:
    pattern = r"[。！？.!?]+"
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]


def find_repeated_phrases(text: str, min_length: int = 4) -> List[Dict[str, Any]]:
    sentences = split_into_sentences(text)
    phrases = []
    
    for i, s1 in enumerate(sentences):
        for j, s2 in enumerate(sentences):
            if i >= j:
                continue
            
            matcher = SequenceMatcher(None, s1, s2)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal" and (i2 - i1) >= min_length:
                    phrase = s1[i1:i2]
                    if len(phrase) >= min_length:
                        phrases.append({
                            "phrase": phrase,
                            "positions": [i, j],
                        })
    
    return phrases


def detect_ai_patterns(text: str) -> List[Dict[str, Any]]:
    patterns = [
        (r"眼中闪过一丝", "眼中闪过一丝"),
        (r"心中一凛", "心中一凛"),
        (r"不由得", "不由得"),
        (r"恐怖的.{0,5}(气息|力量|威压)", "恐怖的X"),
        (r"可怕的.{0,5}(气息|力量|威压)", "可怕的X"),
        (r"仿佛.{0,10}一般", "仿佛X一般"),
        (r"宛如.{0,10}般", "宛如X般"),
        (r"不由分说", "不由分说"),
        (r"令人.{0,5}的是", "令人X的是"),
    ]
    
    findings = []
    for pattern, name in patterns:
        matches = re.findall(pattern, text)
        if matches:
            findings.append({
                "pattern": name,
                "count": len(matches),
                "examples": matches[:3],
            })
    
    return findings


def calculate_similarity(text1: str, text2: str) -> float:
    return SequenceMatcher(None, text1, text2).ratio()


def generate_diff(old_text: str, new_text: str, filename: str = "content") -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    
    diff = unified_diff(old_lines, new_lines, fromfile=f"{filename}.old", tofile=f"{filename}.new")
    return "".join(diff)


def extract_dialogues(text: str) -> List[Dict[str, Any]]:
    pattern = r"[""「『]([^""」』]+)[""」』]"
    matches = re.findall(pattern, text)
    return [{"dialogue": m, "position": text.find(m)} for m in matches]


def analyze_sentence_length(text: str) -> Dict[str, Any]:
    sentences = split_into_sentences(text)
    if not sentences:
        return {"avg": 0, "min": 0, "max": 0, "variance": 0}
    
    lengths = [len(s) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    
    return {
        "avg": round(avg, 2),
        "min": min(lengths),
        "max": max(lengths),
        "variance": round(variance, 2),
        "count": len(sentences),
    }
