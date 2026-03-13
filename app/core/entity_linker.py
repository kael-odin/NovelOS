#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity Linker - Entity disambiguation helper module.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .config import get_config
from .index_manager import IndexManager


@dataclass
class DisambiguationResult:
    mention: str
    entity_id: Optional[str]
    confidence: float
    candidates: List[str] = field(default_factory=list)
    adopted: bool = False
    warning: Optional[str] = None


class EntityLinker:
    def __init__(self, config=None):
        self.config = config or get_config()
        self._index_manager = IndexManager(self.config)

    def register_alias(self, entity_id: str, alias: str, entity_type: str = "角色") -> bool:
        if not alias or not entity_id:
            return False
        return self._index_manager.register_alias(alias, entity_id, entity_type)

    def lookup_alias(self, mention: str, entity_type: str = None) -> Optional[str]:
        entries = self._index_manager.get_entities_by_alias(mention)
        if not entries:
            return None

        if entity_type:
            for entry in entries:
                if entry.get("type") == entity_type:
                    return entry.get("id")
            return None
        else:
            return entries[0].get("id") if entries else None

    def lookup_alias_all(self, mention: str) -> List[Dict]:
        entries = self._index_manager.get_entities_by_alias(mention)
        return [{"type": e.get("type"), "id": e.get("id")} for e in entries]

    def get_all_aliases(self, entity_id: str, entity_type: str = None) -> List[str]:
        return self._index_manager.get_entity_aliases(entity_id)

    def evaluate_confidence(self, confidence: float) -> Tuple[str, bool, Optional[str]]:
        high_threshold = getattr(self.config, 'extraction_confidence_high', 0.9)
        medium_threshold = getattr(self.config, 'extraction_confidence_medium', 0.7)

        if confidence >= high_threshold:
            return ("auto", True, None)
        elif confidence >= medium_threshold:
            return ("warn", True, f"中置信度匹配 (confidence: {confidence:.2f})")
        else:
            return ("manual", False, f"需人工确认 (confidence: {confidence:.2f})")

    def process_uncertain(
        self,
        mention: str,
        candidates: List[str],
        suggested: str,
        confidence: float,
        context: str = ""
    ) -> DisambiguationResult:
        action, adopt, warning = self.evaluate_confidence(confidence)

        result = DisambiguationResult(
            mention=mention,
            entity_id=suggested if adopt else None,
            confidence=confidence,
            candidates=candidates,
            adopted=adopt,
            warning=warning
        )

        return result

    def process_extraction_result(
        self,
        uncertain_items: List[Dict]
    ) -> Tuple[List[DisambiguationResult], List[str]]:
        results = []
        warnings = []

        for item in uncertain_items:
            result = self.process_uncertain(
                mention=item.get("mention", ""),
                candidates=item.get("candidates", []),
                suggested=item.get("suggested", ""),
                confidence=item.get("confidence", 0.0),
                context=item.get("context", "")
            )
            results.append(result)

            if result.warning:
                warnings.append(f"{result.mention} → {result.entity_id}: {result.warning}")

        return results, warnings

    def register_new_entities(
        self,
        new_entities: List[Dict]
    ) -> List[str]:
        registered = []

        for entity in new_entities:
            entity_id = entity.get("suggested_id") or entity.get("id")
            if not entity_id or entity_id == "NEW":
                continue

            entity_type = entity.get("type", "角色")

            name = entity.get("name", "")
            if name:
                self.register_alias(entity_id, name, entity_type)

            for mention in entity.get("mentions", []):
                if mention and mention != name:
                    self.register_alias(entity_id, mention, entity_type)

            registered.append(entity_id)

        return registered
