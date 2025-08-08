from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

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



# Configuração de templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/playground", response_class=HTMLResponse)
async def get_playground(request: Request):
    """Serve a página do playground de testes."""
    return templates.TemplateResponse("playground.html", {"request": request})

from app.services.agent_manager import agent_manager

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, user_id: str, instance_id: str):
    await websocket.accept()
    try:
        team = await agent_manager.get_or_create_team(user_id, instance_id)
        team.session_id = f"{user_id}-{instance_id}-playground"

        while True:
            data = await websocket.receive_text()
            response = team.run(data)
            await websocket.send_text(response.content)
            
    except WebSocketDisconnect:
        print(f"Cliente desconectado: {user_id}-{instance_id}")
    except Exception as e:
        await websocket.send_text(f"Ocorreu um erro: {e}")
        await websocket.close()

# Inclui as rotas
app.include_router(agent_router)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root():
    """Retorna uma landing page moderna em HTML."""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agno Multi-Agent API</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <style>
            body {
                background-color: #1a202c;
                color: #e2e8f0;
            }
            .header, .footer {
                background-color: #2d3748;
            }
            .card {
                background-color: #2d3748;
                border: 1px solid #4a5568;
            }
            .code-block {
                background-color: #0d1117;
                border: 1px solid #30363d;
            }
            .btn {
                background-color: #4a5568;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #718096;
            }
        </style>
    </head>
    <body class="font-sans">

        <!-- Cabeçalho -->
        <header class="header shadow-md">
            <div class="container mx-auto px-6 py-4">
                <h1 class="text-3xl font-bold text-gray-200">Agno Multi-Agent API</h1>
                <p class="text-gray-400 mt-2">Sua solução para orquestração de agentes de IA dinâmicos e multi-usuário.</p>
            </div>
        </header>

        <!-- Conteúdo Principal -->
        <main class="container mx-auto px-6 py-12">
            
            <!-- Seção de Introdução -->
            <section class="text-center">
                <h2 class="text-4xl font-extrabold text-white mb-4">Orquestração de IA Simplificada</h2>
                <p class="text-lg text-gray-400 max-w-3xl mx-auto">
                    A Agno API oferece uma plataforma robusta para criar, gerenciar e coordenar equipes de agentes de IA. 
                    Construa sistemas complexos onde múltiplos agentes colaboram para resolver tarefas, tudo através de uma API RESTful intuitiva.
                </p>
                <div class="mt-8">
                    <a href="/playground" class="btn text-white font-bold py-3 px-6 rounded-lg shadow-lg">
                        Acessar Playground
                    </a>
                </div>
            </section>

            <!-- Seção de Exemplo de Uso -->
            <section class="mt-16">
                <h3 class="text-2xl font-semibold text-white mb-6 text-center">Exemplo de Uso: Chat com um Agente</h3>
                <div class="card rounded-lg p-6 shadow-lg max-w-4xl mx-auto">
                    <p class="text-gray-400 mb-4">
                        Para interagir com uma equipe de agentes, envie uma requisição POST para o endpoint 
                        <code class="bg-gray-700 text-sm rounded px-2 py-1">/agent/chat</code>. 
                        A API gerencia a sessão e a memória da conversa, garantindo a continuidade.
                    </p>
                    <div class="code-block rounded-lg overflow-hidden">
                        <pre><code class="language-python">
# Exemplo de requisição usando Python
import requests
import json

api_url = "http://localhost:8000/agent/chat"

payload = {
  "user_id": "user-123",
  "instance_id": "instance-abc",
  "whatsapp_number": "+5511999998888",
  "username": "Carlos",
  "message": "Qual a cotação atual das ações da NVIDIA?"
}

headers = {
  "Content-Type": "application/json"
}

response = requests.post(api_url, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    print("Resposta do Agente:", response.json())
else:
    print("Erro:", response.status_code, response.text)
                        </code></pre>
                    </div>
                </div>
            </section>

            <!-- Seção de Criação de Equipe -->
            <section class="mt-16">
                <h3 class="text-2xl font-semibold text-white mb-6 text-center">Como Criar e Configurar uma Equipe</h3>
                <div class="card rounded-lg p-6 shadow-lg max-w-4xl mx-auto">
                    <p class="text-gray-400 mb-4">
                        A criação e atualização de equipes de agentes é feita através do endpoint 
                        <code class="bg-gray-700 text-sm rounded px-2 py-1">/agent/hierarchy</code> usando o método PUT. 
                        Você pode definir a estrutura da equipe, os agentes membros, seus modelos, ferramentas e instruções específicas.
                    </p>
                    <div class="code-block rounded-lg overflow-hidden">
                        <pre><code class="language-json">
# Exemplo de payload para criar/atualizar uma equipe
{
  "user_id": "user-123",
  "instance_id": "instance-abc",
  "router_instructions": "Você é um roteador inteligente. Delegue a tarefa para o especialista adequado.",
  "agents": [
    {
      "name": "Analista Financeiro",
      "role": "Especialista em análise de ações e dados financeiros.",
      "model_provider": "GEMINI",
      "model_id": "gemini-1.5-flash",
      "tools": [
        {
          "type": "YFINANCE",
          "config": { "stock_price": true, "company_news": true }
        }
      ]
    },
    {
      "name": "Pesquisador Web",
      "role": "Especialista em buscar informações na web.",
      "model_provider": "GEMINI",
      "model_id": "gemini-1.5-flash",
      "tools": [
        { "type": "DUCKDUCKGO" }
      ]
    }
  ]
}
                        </code></pre>
                    </div>
                </div>
            </section>

        </main>

        <!-- Rodapé -->
        <footer class="footer mt-12 py-6">
            <div class="container mx-auto text-center text-gray-500">
                <p>&copy; 2024 Agno Systems. Todos os direitos reservados.</p>
            </div>
        </footer>

        <script>
            hljs.highlightAll();
        </script>
    </body>
    </html>
    """
    return html_content

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
