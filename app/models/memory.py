from beanie import Document
from pydantic import Field
from typing import List, Dict, Any
from datetime import datetime
import pymongo
from pymongo import IndexModel
from pymongo import IndexModel

class AgentMemory(Document):
    user_id: str
    instance_id: str
    session_id: str
    
    # Histórico de mensagens
    messages: List[Dict[str, Any]] = []
    
    # Estado do agente
    agent_state: Dict[str, Any] = {}
    
    # Metadados
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "agent_memories"
        indexes = [
            IndexModel(
                [("user_id", pymongo.ASCENDING), ("instance_id", pymongo.ASCENDING), ("session_id", pymongo.ASCENDING)],
                unique=True
            )
        ]
