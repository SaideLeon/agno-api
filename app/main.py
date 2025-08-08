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

        if not team.members:
            await websocket.send_text(
                "A equipe de agentes ainda não foi configurada. "
                "Por favor, use o painel de configuração para definir os agentes e, "
                "em seguida, clique em 'Criar/Atualizar Equipe'."
            )
            await websocket.close()
            return

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
        <link href="https://cdnjs.cloudflare.com/ajax/libs/heroicons/2.1.1/24/outline/rocket-launch.svg" rel="preload" as="image">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <style>
            body {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            .bg-gradient-header {
                background: linear-gradient(145deg, #161b22, #0d1117);
            }
            .card {
                background-color: #161b22;
                border: 1px solid #30363d;
            }
            .code-block {
                background-color: #010409;
                border: 1px solid #30363d;
            }
            .btn-primary {
                background-color: #238636;
                transition: background-color 0.3s;
            }
            .btn-primary:hover {
                background-color: #2ea043;
            }
            .btn-secondary {
                background-color: #21262d;
                border: 1px solid #30363d;
                transition: all 0.3s;
            }
            .btn-secondary:hover {
                background-color: #30363d;
                border-color: #8b949e;
            }
            .feature-icon {
                filter: invert(75%) sepia(10%) saturate(1000%) hue-rotate(180deg);
            }
        </style>
    </head>
    <body class="font-sans">

        <header class="bg-gradient-header shadow-lg sticky top-0 z-10">
            <div class="container mx-auto px-6 py-4 flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-200">Agno API</h1>
                <nav>
                    <a href="/docs" class="btn-secondary text-white font-bold py-2 px-4 rounded-lg">API Docs</a>
                </nav>
            </div>
        </header>

        <main class="container mx-auto px-6 py-16">
            
            <section class="text-center">
                <h2 class="text-5xl font-extrabold text-white mb-4">Orquestração de Agentes de IA, Simplificada</h2>
                <p class="text-lg text-gray-400 max-w-3xl mx-auto">
                    Uma plataforma robusta para criar, gerenciar e coordenar equipes de agentes de IA dinâmicos e com memória, através de uma API RESTful intuitiva e um playground interativo.
                </p>
                <div class="mt-8">
                    <a href="/playground" class="btn-primary text-white font-bold py-3 px-8 rounded-lg shadow-lg text-lg">Acessar Playground</a>
                </div>
            </section>

            <section class="mt-24">
                <h3 class="text-3xl font-bold text-white mb-12 text-center">Funcionalidades Principais</h3>
                <div class="grid md:grid-cols-3 gap-8">
                    <!-- Feature 1 -->
                    <div class="card p-6 rounded-lg">
                        <h4 class="font-bold text-xl mb-2">Hierarquia Dinâmica</h4>
                        <p class="text-gray-400">Crie e atualize equipes com agentes especialistas e um roteador inteligente em tempo real via API.</p>
                    </div>
                    <!-- Feature 2 -->
                    <div class="card p-6 rounded-lg">
                        <h4 class="font-bold text-xl mb-2">Memória Persistente</h4>
                        <p class="text-gray-400">As conversas são salvas no MongoDB, garantindo continuidade e contexto em cada interação.</p>
                    </div>
                    <!-- Feature 3 -->
                    <div class="card p-6 rounded-lg">
                        <h4 class="font-bold text-xl mb-2">Playground Interativo</h4>
                        <p class="text-gray-400">Teste e configure suas equipes de agentes em tempo real com uma interface web via WebSockets.</p>
                    </div>
                </div>
            </section>

            <section class="mt-24">
                <h3 class="text-3xl font-bold text-white mb-12 text-center">Endpoints Essenciais</h3>
                <div class="grid md:grid-cols-2 gap-8">
                    
                    <div class="card rounded-lg p-6">
                        <h4 class="font-semibold text-xl mb-4">Configuração de Equipes</h4>
                        <p class="text-gray-400 mb-4">Use o endpoint <code class="bg-gray-700 text-sm rounded px-2 py-1">PUT /agent/hierarchy</code> para definir a estrutura da sua equipe.</p>
                        <div class="code-block rounded-lg overflow-hidden">
                            <pre><code class="language-json">{
  "user_id": "user-123",
  "instance_id": "finance-team",
  "agents": [...] 
}</code></pre>
                        </div>
                    </div>

                    <div class="card rounded-lg p-6">
                        <h4 class="font-semibold text-xl mb-4">Chat via API</h4>
                        <p class="text-gray-400 mb-4">Interaja com sua equipe através do endpoint <code class="bg-gray-700 text-sm rounded px-2 py-1">POST /agent/chat</code>.</p>
                        <div class="code-block rounded-lg overflow-hidden">
                            <pre><code class="language-json">{
  "user_id": "user-123",
  "instance_id": "finance-team",
  "whatsapp_number": "+123...",
  "message": "..."
}</code></pre>
                        </div>
                    </div>

                    <div class="card rounded-lg p-6">
                        <h4 class="font-semibold text-xl mb-4">Listar Sessões</h4>
                        <p class="text-gray-400 mb-4">Filtre e liste sessões de conversa com <code class="bg-gray-700 text-sm rounded px-2 py-1">GET /agent/sessions</code>.</p>
                        <div class="code-block rounded-lg overflow-hidden">
                            <pre><code class="language-bash"># Exemplo de chamada
curl "/agent/sessions?instance_id=finance-team"</code></pre>
                        </div>
                    </div>

                    <div class="card rounded-lg p-6">
                        <h4 class="font-semibold text-xl mb-4">Obter Conversa</h4>
                        <p class="text-gray-400 mb-4">Recupere o histórico completo de uma sessão com <code class="bg-gray-700 text-sm rounded px-2 py-1">GET /agent/sessions/{session_id}/conversation</code>.</p>
                        <div class="code-block rounded-lg overflow-hidden">
                            <pre><code class="language-bash"># Exemplo de chamada
curl "/agent/sessions/whatsapp:+123.../conversation"</code></pre>
                        </div>
                    </div>

                </div>
            </section>

        </main>

        <footer class="border-t border-gray-800 mt-16 py-8">
            <div class="container mx-auto text-center text-gray-500">
                <p>&copy; 2024 Agno Systems. Todos os direitos reservados.</p>
                <p class="mt-2">Repositório: <a href="https://github.com/SaideLeon/agno-api.git" class="hover:text-white">https://github.com/SaideLeon/agno-api.git</a></p>
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
