from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class BaseAdapter(ABC):
    @abstractmethod
    def execute(self, prompt: str, context: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass


class ManualAgentAdapter(BaseAdapter):
    def execute(self, prompt: str, context: Dict[str, Any]) -> str:
        return prompt
    
    def is_available(self) -> bool:
        return True


class PromptFileAdapter(BaseAdapter):
    def __init__(self, output_dir: str = ".novelos/prompts"):
        self.output_dir = output_dir
    
    def execute(self, prompt: str, context: Dict[str, Any]) -> str:
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prompt_{timestamp}.md"
        
        (output_path / filename).write_text(prompt, encoding="utf-8")
        
        return f"Prompt written to: {output_path / filename}"
    
    def is_available(self) -> bool:
        return True


class APIAdapter(BaseAdapter):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
    
    def execute(self, prompt: str, context: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("API key not configured")
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的小说写作助手。"},
                    {"role": "user", "content": prompt},
                ],
            )
            
            return response.choices[0].message.content or ""
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def is_available(self) -> bool:
        return self.api_key is not None


def get_adapter(adapter_type: str, **kwargs) -> BaseAdapter:
    adapters = {
        "manual_agent": ManualAgentAdapter,
        "prompt_file": PromptFileAdapter,
        "api": APIAdapter,
    }
    
    adapter_class = adapters.get(adapter_type)
    if not adapter_class:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    return adapter_class(**kwargs)
