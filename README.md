# Agno Multi-Agent API

**Repositório GitHub**: [https://github.com/SaideLeon/agno-api.git](https://github.com/SaideLeon/agno-api.git)

Esta é uma API robusta construída com FastAPI para criar, gerenciar e interagir com equipes de agentes de IA dinâmicos, hierárquicos e multiusuário, utilizando o framework Agno. O sistema é projetado para ser flexível, permitindo que cada usuário possua múltiplas "instâncias" de equipes de agentes, cada uma com sua própria configuração, especialistas e memória persistente.

## ✨ Principais Funcionalidades

- **Arquitetura Multi-Usuário**: Cada chamada de API é isolada por `user_id` e `instance_id`, garantindo que os dados e as configurações dos agentes de um usuário não se misturem com os de outros.
- **Hierarquia de Agentes Dinâmica**: Crie e atualize equipes de agentes em tempo real através de um endpoint de API. Você pode definir múltiplos agentes especialistas e um "roteador" inteligente que delega tarefas para o membro mais adequado da equipe.
- **Memória Persistente por Sessão**: Cada conversa com uma equipe de agentes tem seu próprio estado e histórico. A memória é armazenada no MongoDB e ativada por padrão, permitindo que as conversas sejam contínuas e com estado.
- **Suporte a Múltiplos Provedores de LLM**: Configure facilmente agentes para usar modelos do Gemini (padrão), OpenAI, Claude ou Groq.
- **Sistema de Ferramentas Extensível**: Adicione ferramentas (como `DuckDuckGo` para pesquisa na web ou `YFinance` para dados financeiros) a cada agente individualmente através da configuração da hierarquia.
- **Playground Interativo**: Uma interface web (`/playground`) para configurar equipes e conversar com elas em tempo real via WebSockets.
- **Landing Page e Health Check**: Inclui uma página inicial (`/`) e um endpoint de verificação de saúde (`/health`).

## 🏗️ Arquitetura do Sistema

O projeto é construído sobre uma base de tecnologias modernas de Python:

- **FastAPI**: Para a criação de APIs de alta performance, com documentação automática (Swagger UI e ReDoc).
- **Agno**: O framework principal para a criação dos agentes, equipes (`Team`) e gerenciamento de interações.
- **MongoDB**: Atua como o banco de dados principal para armazenar as configurações das instâncias de agentes (`AgentInstance`) e a memória de cada sessão de conversa (`AgentMemory`).
- **Beanie ODM**: Um Object-Document Mapper (ODM) assíncrono para MongoDB, que facilita a interação com o banco de dados usando modelos Pydantic.
- **Pydantic**: Usado para validação de dados em toda a aplicação.

### 📂 Estrutura dos Diretórios

```
/
├── app/
│   ├── main.py             # Ponto de entrada da aplicação FastAPI, incluindo rotas e WebSockets
│   ├── models/             # Modelos de dados Pydantic e Beanie
│   ├── routes/             # Endpoints da API
│   ├── services/           # Lógica de negócio para gerenciamento de agentes
│   └── templates/
│       └── playground.html # Interface de usuário para o playground
├── requirements.txt        # Dependências do projeto
└── .env.example            # Arquivo de exemplo para variáveis de ambiente
```

## 🚀 Como Funciona

1.  **Configuração da Hierarquia**: Um usuário define a estrutura de sua equipe de agentes através do endpoint `PUT /agent/hierarchy` ou da interface no `/playground`.
2.  **Início da Conversa**: Uma aplicação cliente pode interagir de duas formas:
    - **Via API REST**: Enviando uma mensagem para `POST /agent/chat`.
    - **Via Playground**: Conectando-se ao endpoint WebSocket em `/ws/chat` após configurar a equipe.
3.  **Criação Dinâmica da Equipe**: O `AgentManager` cria ou recupera do cache a equipe de agentes com base no `user_id` e `instance_id`, carregando sua configuração e memória do MongoDB.
4.  **Execução e Resposta**: A mensagem do usuário é processada pela equipe, que utiliza seu roteador interno para delegar a tarefa ao especialista adequado. A resposta é retornada e o estado da conversa é salvo.

## Endpoints da API

A API principal é exposta sob o prefixo `/agent`.

### `POST /agent/chat`

Endpoint para interagir com uma equipe de agentes via REST.

-   **Request Body**:
    ```json
    {
      "user_id": "string",
      "instance_id": "string",
      "whatsapp_number": "string",
      "username": "string",
      "message": "string"
    }
    ```

### `PUT /agent/hierarchy`

Cria ou atualiza a configuração de uma equipe de agentes (instância).

-   **Request Body**: (Veja o exemplo detalhado na documentação do Swagger em `/docs`)

### `GET /agent/instances/{user_id}`

Lista todas as instâncias de um determinado usuário.

### Outros Endpoints

- **`/`**: Landing page da aplicação.
- **`/playground`**: Playground interativo para testes.
- **`/health`**: Endpoint de verificação de saúde.
- **`/ws/chat`**: Endpoint WebSocket para comunicação em tempo real no playground.

## ⚙️ Instalação e Execução

1.  **Clone o repositório**.
2.  **Crie e ative um ambiente virtual**.
3.  **Instale as dependências**: `pip install -r requirements.txt`
4.  **Configure as variáveis de ambiente**: Crie um arquivo `.env` a partir do `.env.example` e adicione suas chaves de API (pelo menos `GOOGLE_API_KEY`) e a URL do MongoDB.
5.  **Execute a aplicação**: `uvicorn app.main:app --reload`
6.  **Acesse a aplicação**:
    - **Landing Page**: `http://localhost:8000`
    - **Playground**: `http://localhost:8000/playground`
    - **Documentação da API**: `http://localhost:8000/docs`