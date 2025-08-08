from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .instance import ModelProvider, ToolConfig

class AgentConfigRequest(BaseModel):
    """Configuração para um agente individual dentro de uma hierarquia."""
    name: str
    role: str
    
    model_provider: ModelProvider = ModelProvider.GEMINI
    model_id: str = "gemini-1.5-flash"
    
    tools: List[ToolConfig] = []
    
    parent_id: Optional[str] = None
