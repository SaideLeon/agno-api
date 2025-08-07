from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.models.instance import AgentInstance
from app.models.memory import AgentMemory
from app.routes.agent import router as agent_router

app = FastAPI(
    title="Agno Multi-Agent API",
    description="API para gerenciar agentes Agno dinâmicos multi-usuário",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Inicializa conexão com MongoDB e Beanie"""
    from pymongo import uri_parser

    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    
    db_name = None
    if mongodb_url:
        try:
            # Tenta extrair o nome do banco de dados da URL
            parsed_uri = uri_parser.parse_uri(mongodb_url)
            db_name = parsed_uri.get('database')
        except Exception:
            # Ignora erros de parsing, o fallback será usado
            pass
    
    if not db_name:
        # Se não estiver na URL, busca da variável de ambiente ou usa o padrão
        db_name = os.getenv("MONGODB_DATABASE", "agno_agents")

    # Conecta ao MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    database = client[db_name]
    
    # Inicializa Beanie
    await init_beanie(
        database=database,
        document_models=[AgentInstance, AgentMemory]
    )

# Inclui as rotas
app.include_router(agent_router)

@app.get("/")
async def root():
    return {"message": "Agno Multi-Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
