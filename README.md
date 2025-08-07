# Agno Multi-Agent API

Esta é uma API robusta construída com FastAPI para criar, gerenciar e interagir com equipes de agentes de IA dinâmicos, hierárquicos e multiusuário, utilizando o framework Agno. O sistema é projetado para ser flexível, permitindo que cada usuário possua múltiplas "instâncias" de equipes de agentes, cada uma com sua própria configuração, especialistas e memória persistente.

## ✨ Principais Funcionalidades

- **Arquitetura Multi-Usuário**: Cada chamada de API é isolada por `user_id` e `instance_id`, garantindo que os dados e as configurações dos agentes de um usuário não se misturem com os de outros.
- **Hierarquia de Agentes Dinâmica**: Crie e atualize equipes de agentes em tempo real através de um endpoint de API. Você pode definir múltiplos agentes especialistas e um "roteador" inteligente que delega tarefas para o membro mais adequado da equipe.
- **Memória Persistente por Sessão**: Cada conversa com uma equipe de agentes tem seu próprio estado e histórico, identificado por um `session_id`. A memória é armazenada no MongoDB, permitindo que as conversas sejam contínuas e com estado.
- **Suporte a Múltiplos Provedores de LLM**: Configure facilmente agentes para usar modelos do OpenAI, Gemini, Claude ou Groq.
- **Sistema de Ferramentas Extensível**: Adicione ferramentas (como `DuckDuckGo` para pesquisa na web ou `YFinance` para dados financeiros) a cada agente individualmente através da configuração da hierarquia.
- **Cache de Desempenho**: As equipes de agentes são mantidas em um cache em memória para respostas rápidas, e o cache é invalidado automaticamente quando a configuração de uma equipe é atualizada.

## 🏗️ Arquitetura do Sistema

O projeto é construído sobre uma base de tecnologias modernas de Python:

- **FastAPI**: Para a criação de APIs de alta performance, com documentação automática (Swagger UI e ReDoc).
- **Agno**: O framework principal para a criação dos agentes, equipes (`Team`) e gerenciamento de interações.
- **MongoDB**: Atua como o banco de dados principal para armazenar as configurações das instâncias de agentes (`AgentInstance`) e a memória de cada sessão de conversa (`AgentMemory`).
- **Beanie ODM**: Um Object-Document Mapper (ODM) assíncrono para MongoDB, que facilita a interação com o banco de dados usando modelos Pydantic.
- **Pydantic**: Usado para validação de dados em toda a aplicação, desde os requests da API até os modelos do banco de dados.

### 📂 Estrutura dos Diretórios

```
/
├── app/
│   ├── main.py             # Ponto de entrada da aplicação FastAPI
│   ├── models/
│   │   ├── instance.py     # Modelo de dados para a configuração da equipe (AgentInstance)
│   │   └── memory.py       # Modelo de dados para a memória do agente (AgentMemory)
│   ├── routes/
│   │   └── agent.py        # Endpoints da API para interagir com os agentes
│   └── services/
│       └── agent_manager.py  # Lógica de negócio para criar, gerenciar e cachear equipes
├── requirements.txt        # Dependências do projeto
└── .env.example            # Arquivo de exemplo para variáveis de ambiente
```

## 🚀 Como Funciona

1.  **Configuração da Hierarquia**: Um usuário define a estrutura de sua equipe de agentes através do endpoint `PUT /agent/hierarchy`. Isso inclui:
    - As instruções para o agente "roteador" (`router_instructions`).
    - Uma lista de agentes especialistas (`agents`), cada um com seu nome, função (`role`), modelo de linguagem e ferramentas.
    - Esta configuração é salva na coleção `agent_instances` no MongoDB.

2.  **Início da Conversa**: Uma aplicação cliente inicia uma conversa enviando uma mensagem para o endpoint `POST /agent/chat`. O request deve incluir `user_id`, `instance_id`, uma `session_id` única para a conversa e a mensagem do usuário.

3.  **Criação Dinâmica da Equipe**:
    - O `AgentManager` recebe a requisição.
    - Ele verifica se uma equipe para o `user_id` e `instance_id` já existe no cache.
    - Se não existir, ele busca a configuração da `AgentInstance` no MongoDB.
    - Com base na configuração, ele cria dinamicamente cada `Agent` especialista e os agrupa em uma `Team` do Agno.
    - A equipe é configurada no modo `route`, usando as `router_instructions` para decidir qual especialista deve responder.
    - Um `MongoDbStorage` é associado à equipe, usando um nome de coleção único baseado em `user_id`, `instance_id` e `session_id`, para garantir a persistência da memória.

4.  **Execução e Resposta**:
    - A mensagem do usuário é passada para a equipe (`team.run(message)`).
    - O agente roteador da equipe analisa a mensagem e a delega para o agente especialista mais apropriado.
    - O agente especialista processa a mensagem (usando suas ferramentas, se necessário) e gera uma resposta.
    - A resposta é retornada ao cliente, e o estado da conversa é salvo automaticamente no MongoDB.

## Endpoints da API

A API é exposta sob o prefixo `/agent`.

### `POST /agent/chat`

Endpoint principal para interagir com uma equipe de agentes.

-   **Request Body**:
    ```json
    {
      "user_id": "string",
      "instance_id": "string",
      "session_id": "string",
      "message": "string"
    }
    ```
-   **Response**:
    ```json
    {
      "response": "string",
      "session_id": "string",
      "success": true
    }
    ```

### `PUT /agent/hierarchy`

Cria ou atualiza a configuração de uma equipe de agentes (instância). Se a `instance_id` não existir para o `user_id`, ela será criada (lógica de *upsert*).

-   **Request Body**:
    ```json
    {
      "user_id": "string",
      "instance_id": "string",
      "router_instructions": "Você é um roteador inteligente...",
      "agents": [
        {
          "name": "Analista Financeiro",
          "role": "Especialista em análise de ações e dados financeiros.",
          "model_provider": "gemini",
          "model_id": "gemini-1.5-pro-latest",
          "tools": [
            {
              "type": "YFINANCE",
              "config": {"stock_price": true}
            }
          ]
        },
        {
          "name": "Pesquisador Web",
          "role": "Especialista em encontrar informações na internet.",
          "tools": [
            {
              "type": "DUCKDUCKGO"
            }
          ]
        }
      ]
    }
    ```
-   **Response**:
    ```json
    {
      "message": "Hierarchy configuration updated successfully"
    }
    ```

### `GET /agent/instances/{user_id}`

Lista todas as instâncias (configurações de equipes) de um determinado usuário.

-   **Response**:
    ```json
    {
      "instances": [
        {
          "user_id": "string",
          "instance_id": "string",
          "router_instructions": "string",
          "agents": [],
          "created_at": "datetime",
          "updated_at": "datetime"
        }
      ]
    }
    ```

## ⚙️ Instalação e Execução

1.  **Clone o repositório**:
    ```bash
    git clone <url-do-repositorio>
    cd agno-api
    ```

2.  **Crie e ative um ambiente virtual**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente**:
    Crie um arquivo `.env` na raiz do projeto (você pode copiar o `.env.example`) e defina as seguintes variáveis:
    ```env
    # URL de conexão do seu servidor MongoDB
    MONGODB_URL="mongodb://localhost:27017/"
    # Nome do banco de dados que será usado
    MONGODB_DATABASE="agno_agents"

    # Chaves de API para os provedores de LLM (adicione as que for usar)
    OPENAI_API_KEY="sk-..."
    GOOGLE_API_KEY="..."
    ANTHROPIC_API_KEY="..."
    GROQ_API_KEY="..."

    # Configurações da API (opcional)
    API_HOST="0.0.0.0"
    API_PORT=8000
    ```

5.  **Execute a aplicação**:
    ```bash
    uvicorn app.main:app --reload
    ```

6.  **Acesse a documentação interativa**:
    Abra seu navegador e acesse `http://localhost:8000/docs` para ver a documentação da API gerada pelo Swagger e interagir com os endpoints.
