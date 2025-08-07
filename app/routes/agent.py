from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.agent_manager import agent_manager
from app.models.instance import HierarchicalAgentConfig # Importa o modelo atualizado

router = APIRouter(prefix="/agent", tags=["agent"])

class ChatRequest(BaseModel):
    user_id: str
    instance_id: str
    session_id: str  # ID único da conversa (ex: número do WhatsApp do cliente)
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    success: bool

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Endpoint principal para conversar com a equipe de agentes."""
    try:
        team = await agent_manager.get_or_create_team(
            user_id=request.user_id,
            instance_id=request.instance_id
        )
        
        team.session_id = request.session_id
        
        response = team.run(request.message)
        
        return ChatResponse(
            response=response.content,
            session_id=team.session_id,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HierarchyUpdateRequest(BaseModel):
    user_id: str
    instance_id: str
    router_instructions: Optional[str] = None
    agents: Optional[List[HierarchicalAgentConfig]] = None

@router.put("/hierarchy")
async def update_agent_hierarchy(request: HierarchyUpdateRequest):
    """Cria ou atualiza a hierarquia de agentes de uma instância."""
    update_data = request.dict(exclude_unset=True, exclude={'user_id', 'instance_id'})
    
    success = await agent_manager.update_instance_hierarchy(
        user_id=request.user_id,
        instance_id=request.instance_id,
        hierarchy_updates=update_data
    )
    
    if not success:
        # Esta condição pode não ser mais alcançada devido à lógica de upsert
        raise HTTPException(status_code=404, detail="Instance could not be created or updated")
    
    return {"message": "Hierarchy configuration updated successfully"}

@router.get("/instances/{user_id}")
async def get_user_instances(user_id: str):
    """Lista todas as instâncias de um usuário."""
    from app.models.instance import AgentInstance
    instances = await AgentInstance.find(AgentInstance.user_id == user_id).to_list()
    return {"instances": instances}
