from pathlib import Path
from typing import Optional, List, Dict, Any
from ..models.story_bible import StoryBible, Character, Foreshadowing, Relationship, World, Timeline
from .file_service import FileService


class BibleService:
    def __init__(self, file_service: FileService):
        self.fs = file_service
        self._cache: Optional[StoryBible] = None
    
    def load_bible(self, reload: bool = False) -> StoryBible:
        if self._cache and not reload:
            return self._cache
        
        data = self.fs.read_yaml("project/story_bible/bible.yaml")
        if not data:
            self._cache = StoryBible()
            return self._cache
        
        self._cache = StoryBible(**data)
        return self._cache
    
    def save_bible(self, bible: StoryBible) -> None:
        self.fs.write_yaml("project/story_bible/bible.yaml", bible.model_dump())
        self._cache = bible
    
    def get_character(self, char_id: str) -> Optional[Character]:
        bible = self.load_bible()
        return bible.get_character(char_id)
    
    def get_all_characters(self) -> List[Character]:
        return self.load_bible().characters
    
    def get_protagonist(self) -> Optional[Character]:
        for c in self.load_bible().characters:
            if c.role == "protagonist":
                return c
        return None
    
    def add_character(self, character: Character) -> None:
        bible = self.load_bible()
        existing = bible.get_character(character.id)
        if existing:
            idx = bible.characters.index(existing)
            bible.characters[idx] = character
        else:
            bible.characters.append(character)
        self.save_bible(bible)
    
    def update_character_state(self, char_id: str, state_updates: Dict[str, Any]) -> None:
        bible = self.load_bible()
        char = bible.get_character(char_id)
        if char:
            char.current_state.update(state_updates)
            self.save_bible(bible)
    
    def get_active_foreshadowings(self) -> List[Foreshadowing]:
        return self.load_bible().get_active_foreshadowings()
    
    def add_foreshadowing(self, foreshadowing: Foreshadowing) -> None:
        bible = self.load_bible()
        bible.foreshadowings.append(foreshadowing)
        self.save_bible(bible)
    
    def update_foreshadowing_status(self, f_id: str, status: str) -> None:
        bible = self.load_bible()
        for f in bible.foreshadowings:
            if f.id == f_id:
                f.status = status
                break
        self.save_bible(bible)
    
    def add_hint_to_foreshadowing(self, f_id: str, chapter: int, content: str) -> None:
        bible = self.load_bible()
        for f in bible.foreshadowings:
            if f.id == f_id:
                f.hints.append({"chapter": chapter, "content": content})
                break
        self.save_bible(bible)
    
    def get_relationships(self, char_id: str) -> List[Relationship]:
        bible = self.load_bible()
        return [r for r in bible.relationships if r.source == char_id or r.target == char_id]
    
    def add_relationship(self, relationship: Relationship) -> None:
        bible = self.load_bible()
        bible.relationships.append(relationship)
        self.save_bible(bible)
    
    def add_timeline_event(self, timeline: Timeline) -> None:
        bible = self.load_bible()
        bible.timeline.append(timeline)
        bible.timeline.sort(key=lambda x: x.chapter)
        self.save_bible(bible)
    
    def get_timeline_up_to(self, chapter: int) -> List[Timeline]:
        bible = self.load_bible()
        return [t for t in bible.timeline if t.chapter <= chapter]
    
    def load_world(self) -> World:
        data = self.fs.read_yaml("project/story_bible/world.yaml")
        if data:
            return World(**data)
        return World()
    
    def save_world(self, world: World) -> None:
        self.fs.write_yaml("project/story_bible/world.yaml", world.model_dump())
