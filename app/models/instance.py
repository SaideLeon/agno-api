from beanie import Document
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import pymongo
from pymongo import IndexModel
from pymongo import IndexModel

class ModelProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROQ = "groq"

class ToolType(str, Enum):
    """Enum para os tipos de ferramentas suportadas."""
    DUCKDUCKGO = "DUCKDUCKGO"
    YFINANCE = "YFINANCE"
    # Adicione outros tipos de ferramentas aqui (ex: DATABASE, API)



from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import pymongo
from pymongo import IndexModel

class ModelProvider(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROQ = "groq"

class ToolType(str, Enum):
    """Enum para os tipos de ferramentas suportadas."""
    DUCKDUCKGO = "DUCKDUCKGO"
    YFINANCE = "YFINANCE"
    # Adicione outros tipos de ferramentas aqui (ex: DATABASE, API)

class ToolConfig(BaseModel):
    """Configuração para uma ferramenta específica."""
    type: ToolType
    # O campo config pode ser usado para passar parâmetros específicos
    # para a inicialização da ferramenta. Ex: {"stock_price": True}
    config: Optional[Dict[str, Any]] = None

class HierarchicalAgentConfig(BaseModel):
    """Configuração para um agente individual dentro de uma hierarquia."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    
    model_provider: ModelProvider = ModelProvider.GEMINI
    model_id: str = "gemini-1.5-flash"
    
    # Lista de ferramentas configuráveis para este agente
    tools: List[ToolConfig] = []
    
    parent_id: Optional[str] = None

    model_config = {"protected_namespaces": ()}


class AgentInstance(Document):
    """Representa uma instância de uma equipe de agentes hierárquicos."""
    user_id: str
    instance_id: str
    
    router_instructions: str = (
        "Você é o coordenador de uma equipe de especialistas. Sua função é analisar a "
        "solicitação do usuário, delegar a tarefa para o membro da equipe mais qualificado e, em seguida, "
        "apresentar a resposta final do especialista de forma clara e direta para o usuário. "
        "Se a solicitação for uma continuação da conversa, leve o histórico em consideração."
    )
    
    agents: List[HierarchicalAgentConfig] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "agent_instances"
        indexes = [
            IndexModel(
                [("user_id", pymongo.ASCENDING), ("instance_id", pymongo.ASCENDING)],
                unique=True
            )
        ]
