from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.services.agent_manager import agent_manager
from app.models.instance import HierarchicalAgentConfig, ModelProvider, ToolConfig, ToolType
from app.models.memory import AgentMemory
import uuid
import logging

router = APIRouter(prefix="/agent", tags=["agent"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    user_id: str
    instance_id: str
    whatsapp_number: str
    username: str
    message: str
    session_id: Optional[str] = None

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
        
        team.session_id = request.whatsapp_number
        
        # Adiciona o nome de usuário à mensagem para o agente
        message_with_context = (
            f"O nome do cliente é {request.username}. "
            f"Mensagem do cliente: {request.message}"
        )
        
        response = team.run(message_with_context)
        
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
    agents: Optional[List[dict]] = None  # agora aceita dict cru, não só HierarchicalAgentConfig

def normalize_agent(agent_data: dict) -> dict:
    """Normaliza e valida dados de um agente antes de criar HierarchicalAgentConfig."""
    # Garante agent_id
    if not agent_data.get("agent_id"):
        agent_data["agent_id"] = str(uuid.uuid4())

    # Normaliza provider
    provider = agent_data.get("model_provider", "gemini")
    if isinstance(provider, str):
        provider = provider.lower()
        try:
            agent_data["model_provider"] = ModelProvider(provider)
        except ValueError:
            agent_data["model_provider"] = ModelProvider.gemini
    elif isinstance(provider, ModelProvider):
        agent_data["model_provider"] = provider
    else:
        agent_data["model_provider"] = ModelProvider.gemini

    # Model ID default
    if not agent_data.get("model_id"):
        agent_data["model_id"] = "gemini-1.5-flash"

    # Normaliza tools
    tools = agent_data.get("tools", [])
    normalized_tools = []
    for t in tools:
        if isinstance(t, str):
            try:
                # Ex: "YFINANCE" → ToolConfig(type=ToolType.YFINANCE)
                normalized_tools.append(ToolConfig(type=ToolType[t.upper()]))
            except KeyError:
                logger.warning(f"Tool '{t}' not found in ToolType enum. Skipping.")
        elif isinstance(t, dict):
            # Garante que o type está correto
            t_type = t.get("type")
            if isinstance(t_type, str):
                try:
                    t["type"] = ToolType[t_type.upper()]
                    normalized_tools.append(ToolConfig(**t))
                except KeyError:
                    logger.warning(f"Tool type '{t_type}' not found in ToolType enum. Skipping tool.")
            elif isinstance(t_type, ToolType):
                normalized_tools.append(ToolConfig(**t))
        elif isinstance(t, ToolConfig):
            normalized_tools.append(t)
    agent_data["tools"] = normalized_tools

    return agent_data

@router.put("/hierarchy")
async def update_agent_hierarchy(request: HierarchyUpdateRequest):
    logger.info(f"Recebida requisição para /hierarchy: user_id={request.user_id}, instance_id={request.instance_id}")
    logger.info(f"Payload recebido: {request.dict()}")

    try:
        agents_normalized = None
        if request.agents:
            agents_normalized = [HierarchicalAgentConfig(**normalize_agent(a)) for a in request.agents]

        hierarchy_updates = {
            "router_instructions": request.router_instructions,
            "agents": agents_normalized
        }

        success = await agent_manager.update_instance_hierarchy(
            user_id=request.user_id,
            instance_id=request.instance_id,
            hierarchy_updates=hierarchy_updates
        )

        if not success:
            logger.error("Falha ao criar ou atualizar a instância.")
            raise HTTPException(status_code=404, detail="Instance could not be created or updated")

        logger.info("Hierarquia atualizada com sucesso.")
        return {"message": "Hierarchy configuration updated successfully"}

    except Exception as e:
        logger.exception("Erro ao processar a atualização da hierarquia")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{user_id}")
async def get_user_instances(user_id: str):
    """Lista todas as instâncias de um usuário."""
    from app.models.instance import AgentInstance
    instances = await AgentInstance.find(AgentInstance.user_id == user_id).to_list()
    return {"instances": instances}

@router.get("/sessions")
async def get_sessions(
    instance_id: str = Query(..., description="ID da instância para filtrar as sessões"),
    whatsapp_number: Optional[str] = Query(None, description="Número do WhatsApp (session_id) para filtrar as sessões")
):
    """Lista todas as sessões de conversa, com filtros."""
    query = {"instance_id": instance_id}
    if whatsapp_number:
        query["session_id"] = whatsapp_number
    
    sessions = await AgentMemory.find(query).to_list()
    
    # Retorna um resumo para não sobrecarregar a resposta
    session_summaries = [
        {
            "session_id": s.session_id,
            "user_id": s.user_id,
            "instance_id": s.instance_id,
            "message_count": len(s.messages),
            "created_at": s.created_at,
            "updated_at": s.updated_at
        } for s in sessions
    ]
    return {"sessions": session_summaries}

@router.get("/sessions/{session_id}/conversation")
async def get_conversation(session_id: str):
    """Obtém o histórico completo de mensagens de uma sessão específica."""
    session = await AgentMemory.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    return {"conversation": session.messages}