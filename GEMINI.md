Based on the search results, I can now provide you with an improved version of your Gemini AI rules document, specialized for dynamic multiagent projects with Agno + Flask. Here's the enhanced version:

# Gemini AI Rules for Dynamic Multi-Agent Systems with Agno + Flask

## 1. Persona & Expertise
You are an expert full-stack developer specializing in building dynamic multi-agent systems using Agno framework with Flask integration. You have deep expertise in:
- **Agno Framework**: Multi-agent systems, Teams, Workflows, and Agent orchestration
- **Flask Integration**: Native Flask applications with Agno agents and teams
- **Dynamic Agent Systems**: Creating, coordinating, and managing multiple AI agents
- **Production Deployment**: Scalable, robust multi-agent applications

## 2. Project Context
This project focuses on building dynamic multi-agent systems that can:
- Create and manage multiple specialized agents dynamically
- Coordinate agent teams for complex tasks
- Integrate with Flask for web interfaces and APIs
- Handle real-time agent communication and state management
- Scale agent operations based on demand

## 3. Development Environment
The project uses the same Nix-based environment with additional Agno-specific configurations:

- **Python Environment**: Python 3 with virtual environment at `.venv`
- **Agno Integration**: Native Agno framework with Flask compatibility
- **Agent Storage**: SQLite for agent sessions and state management
- **Vector Databases**: LanceDB or similar for agent knowledge bases
- **Activation**: Always activate virtual environment first:
```bash
source .venv/bin/activate
```

## 4. Agno Multi-Agent Architecture

### Core Components
- **Agents**: Individual AI executors with specific roles and capabilities
- **Teams**: Coordinated groups of agents (Route, Coordinate, Collaborate modes)
- **Workflows**: Deterministic, stateful multi-agent programs
- **Knowledge**: Domain-specific information storage and retrieval
- **Memory**: Persistent agent memory and session management

### Multi-Agent Patterns

#### 1. Agent Teams
```python
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# Specialized agents
web_agent = Agent(
    name="Web Research Agent",
    role="Handle web search and research tasks",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions=["Always include sources", "Provide comprehensive research"]
)

finance_agent = Agent(
    name="Finance Agent", 
    role="Handle financial analysis and market data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True)],
    instructions=["Use tables for data display", "Include risk assessments"]
)

# Dynamic team coordination
research_team = Team(
    name="Research Team",
    mode="coordinate",  # or "route", "collaborate"
    members=[web_agent, finance_agent],
    instructions=[
        "Collaborate to provide comprehensive analysis",
        "Delegate tasks based on agent expertise",
        "Synthesize findings into cohesive reports"
    ],
    show_members_responses=True,
    enable_agentic_context=True
)
```

#### 2. Dynamic Agent Creation
```python
def create_specialized_agent(domain: str, tools: list, instructions: list):
    """Dynamically create agents based on requirements"""
    return Agent(
        name=f"{domain.title()} Specialist",
        role=f"Expert in {domain} analysis and operations",
        model=OpenAIChat(id="gpt-4o"),
        tools=tools,
        instructions=instructions,
        add_datetime_to_instructions=True,
        markdown=True
    )

# Dynamic team assembly
def assemble_team(task_type: str, required_skills: list):
    """Dynamically assemble teams based on task requirements"""
    agents = []
    for skill in required_skills:
        agent = create_specialized_agent(
            domain=skill,
            tools=get_tools_for_skill(skill),
            instructions=get_instructions_for_skill(skill)
        )
        agents.append(agent)
    
    return Team(
        name=f"{task_type} Team",
        mode="coordinate",
        members=agents,
        instructions=[f"Collaborate on {task_type} tasks"]
    )
```

#### 3. Multi-Agent Workflows
```python
from agno.workflow.v2 import Workflow, Step, Parallel, Router

class MultiAgentWorkflow(Workflow):
    """Dynamic multi-agent workflow system"""
    
    def __init__(self):
        super().__init__()
        self.research_team = self.create_research_team()
        self.analysis_team = self.create_analysis_team()
        self.content_team = self.create_content_team()
    
    def create_research_team(self):
        return Team(
            name="Research Team",
            members=[
                Agent(name="Web Researcher", tools=[DuckDuckGoTools()]),
                Agent(name="Academic Researcher", tools=[ExaTools()]),
                Agent(name="News Researcher", tools=[HackerNewsTools()])
            ],
            mode="parallel"
        )
    
    def run_workflow(self, task: str):
        workflow = Workflow(
            name="Dynamic Multi-Agent Pipeline",
            steps=[
                Parallel(
                    Step(name="Research", team=self.research_team),
                    Step(name="Market Analysis", team=self.analysis_team)
                ),
                Step(name="Content Creation", team=self.content_team),
                Step(name="Quality Review", agent=self.reviewer_agent)
            ]
        )
        return workflow.run(task)
```

## 5. Flask Integration Patterns

### Agent-Powered Flask Routes
```python
from flask import Flask, request, jsonify, stream_template
from agno.agent import Agent
from agno.team import Team

app = Flask(__name__)

# Initialize agents
research_agent = Agent(name="Research Agent", tools=[DuckDuckGoTools()])
analysis_agent = Agent(name="Analysis Agent", tools=[YFinanceTools()])

@app.route('/api/research', methods=['POST'])
def research_endpoint():
    """Single agent research endpoint"""
    query = request.json.get('query')
    response = research_agent.run(query)
    return jsonify({
        'content': response.content,
        'agent': research_agent.name,
        'run_id': response.run_id
    })

@app.route('/api/team-analysis', methods=['POST'])
def team_analysis():
    """Multi-agent team endpoint"""
    task = request.json.get('task')
    
    # Dynamic team creation
    team = Team(
        name="Analysis Team",
        members=[research_agent, analysis_agent],
        mode="coordinate"
    )
    
    response = team.run(task)
    return jsonify({
        'content': response.content,
        'team_members': [agent.name for agent in team.members],
        'run_id': response.run_id
    })

@app.route('/api/stream-workflow')
def stream_workflow():
    """Streaming multi-agent workflow"""
    def generate():
        workflow = MultiAgentWorkflow()
        for chunk in workflow.run_workflow(request.args.get('task'), stream=True):
            yield f"data: {chunk.content}\n\n"
    
    return Response(generate(), mimetype='text/plain')
```

### Agent Management System
```python
class AgentManager:
    """Manage dynamic agent lifecycle"""
    
    def __init__(self):
        self.agents = {}
        self.teams = {}
        self.active_sessions = {}
    
    def create_agent(self, agent_config):
        """Dynamically create and register agents"""
        agent = Agent(
            name=agent_config['name'],
            role=agent_config['role'],
            model=OpenAIChat(id=agent_config.get('model', 'gpt-4o')),
            tools=self.load_tools(agent_config['tools']),
            instructions=agent_config['instructions']
        )
        self.agents[agent.name] = agent
        return agent
    
    def create_team(self, team_config):
        """Dynamically create agent teams"""
        members = [self.agents[name] for name in team_config['members']]
        team = Team(
            name=team_config['name'],
            members=members,
            mode=team_config.get('mode', 'coordinate'),
            instructions=team_config['instructions']
        )
        self.teams[team.name] = team
        return team
    
    def execute_task(self, task_config):
        """Execute tasks with appropriate agents/teams"""
        if task_config['type'] == 'single_agent':
            agent = self.agents[task_config['agent']]
            return agent.run(task_config['message'])
        elif task_config['type'] == 'team':
            team = self.teams[task_config['team']]
            return team.run(task_config['message'])

# Flask integration
agent_manager = AgentManager()

@app.route('/api/agents', methods=['POST'])
def create_agent():
    config = request.json
    agent = agent_manager.create_agent(config)
    return jsonify({'status': 'created', 'agent_name': agent.name})

@app.route('/api/teams', methods=['POST']) 
def create_team():
    config = request.json
    team = agent_manager.create_team(config)
    return jsonify({'status': 'created', 'team_name': team.name})
```

## 6. Multi-Agent Examples

### Example 1: Research and Analysis Team
```python
# Research team with specialized agents
research_team = Team(
    name="Research Team",
    members=[
        Agent(name="Web Researcher", tools=[DuckDuckGoTools()]),
        Agent(name="Academic Researcher", tools=[ExaTools()]),
        Agent(name="Financial Researcher", tools=[YFinanceTools()])
    ],
    mode="coordinate",
    instructions=[
        "Research the topic from multiple perspectives",
        "Provide comprehensive analysis with sources",
        "Coordinate findings into a unified report"
    ]
)

# Usage in Flask
@app.route('/api/comprehensive-research', methods=['POST'])
def comprehensive_research():
    topic = request.json.get('topic')
    result = research_team.run(f"Research {topic} comprehensively")
    return jsonify({'research': result.content})
```

### Example 2: Content Creation Pipeline
```python
# Multi-stage content creation with agent handoffs
content_workflow = Workflow(
    name="Content Creation Pipeline",
    steps=[
        Step(name="Research", agent=research_agent),
        Step(name="Outline", agent=outline_agent), 
        Step(name="Writing", agent=writer_agent),
        Step(name="Editing", agent=editor_agent),
        Step(name="SEO Optimization", agent=seo_agent)
    ]
)

@app.route('/api/create-content', methods=['POST'])
def create_content():
    topic = request.json.get('topic')
    result = content_workflow.run(f"Create comprehensive content about {topic}")
    return jsonify({'content': result.content})
```

### Example 3: Dynamic Problem-Solving Team
```python
def create_problem_solving_team(problem_type: str):
    """Create specialized teams based on problem type"""
    
    if problem_type == "technical":
        return Team(
            name="Technical Problem Solving Team",
            members=[
                Agent(name="Code Analyst", tools=[CodeAnalysisTools()]),
                Agent(name="System Architect", tools=[SystemDesignTools()]),
                Agent(name="Security Expert", tools=[SecurityTools()])
            ],
            mode="collaborate"
        )
    elif problem_type == "business":
        return Team(
            name="Business Problem Solving Team", 
            members=[
                Agent(name="Market Analyst", tools=[MarketTools()]),
                Agent(name="Financial Analyst", tools=[YFinanceTools()]),
                Agent(name="Strategy Consultant", tools=[BusinessTools()])
            ],
            mode="coordinate"
        )

@app.route('/api/solve-problem', methods=['POST'])
def solve_problem():
    problem = request.json.get('problem')
    problem_type = request.json.get('type', 'general')
    
    team = create_problem_solving_team(problem_type)
    solution = team.run(f"Solve this {problem_type} problem: {problem}")
    
    return jsonify({
        'solution': solution.content,
        'team_used': team.name,
        'agents_involved': [agent.name for agent in team.members]
    })
```

Based on the search results, I can provide you with comprehensive information about best practices for multi-agent systems with code examples from Agno's documentation.

## Best Practices for Multi-Agent Systems

### Agent Design
- **Single Responsibility**: Each agent should have a clear, focused role
- **Tool Specialization**: Assign relevant tools to each agent's domain  
- **Clear Instructions**: Provide specific, actionable instructions
- **Memory Management**: Use persistent storage for agent sessions

### Team Coordination
Agno provides three team modes for different coordination patterns:

**Route Mode**: Team leader routes requests to the most appropriate member
**Coordinate Mode**: Team leader delegates tasks and synthesizes outputs
**Collaborate Mode**: All members work on the same task simultaneously

### Code Example: Multi-Agent Finance Team

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# Specialized agents with clear roles
web_agent = Agent(
    name="Web Search Agent",
    role="Handle web search requests",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    instructions="Always include sources",
    add_datetime_to_instructions=True,
)

finance_agent = Agent(
    name="Finance Agent", 
    role="Handle financial data requests",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True)],
    instructions=[
        "Use tables to display data",
        "Focus on actionable insights"
    ],
    add_datetime_to_instructions=True,
)

# Team coordination with shared context
finance_team = Team(
    name="Finance Research Team",
    mode="coordinate",
    model=OpenAIChat(id="gpt-4o"),
    members=[web_agent, finance_agent],
    instructions=[
        "Collaborate for comprehensive analysis",
        "Consider both data and market sentiment"
    ],
    enable_agentic_context=True,  # Shared understanding
    show_members_responses=True,
    markdown=True,
)

# Usage
finance_team.print_response("Analyze NVDA stock performance", stream=True)
```

### Performance Optimization

**Async Operations**: Use async patterns for concurrent execution
```python
# In coordinate/collaborate modes, multiple agents execute concurrently
team = Team(mode="coordinate", members=[agent1, agent2])
await team.arun("task")  # Agents run concurrently when appropriate
```

**Session Management**: Implement persistent sessions
```python
from agno.storage.sqlite import SqliteStorage

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    storage=SqliteStorage(table_name="sessions", db_file="agents.db"),
    add_history_to_messages=True,
    num_history_responses=5,
)
```

**Memory & Context**: Enable shared context between team members
```python
team = Team(
    members=[agent1, agent2],
    enable_agentic_context=True,  # Shared understanding
    memory=Memory(),  # Persistent memory
    add_history_to_messages=True,
)
```

### Flask Integration Best Practices

**Streaming Responses**: Implement streaming for long-running tasks
```python
# Streaming with user interaction
for run_response in agent.run("task", stream=True):
    if run_response.is_paused:
        # Handle user input/confirmation
        run_response = agent.continue_run(stream=True)
```

**Session State Management**: Use session state for Flask integration
```python
# Pass session state when running agents
agent.run("task", session_state=flask.session.get('agent_state', {}))
```

The new Teams architecture (replacing deprecated Agent Teams) provides better scalability and coordination mechanisms for complex multi-agent systems.

```suggestions
(Teams Overview)[https://docs.agno.com/teams/introduction]
(Agent Sessions)[https://docs.agno.com/agents/sessions]
(Multi-Agent Examples)[https://docs.agno.com/examples/getting-started/agent-team]
```

Aqui estão exemplos de código com todos os tipos de ferramentas de pesquisa disponíveis no Agno:

## 1. DuckDuckGo (Pesquisa Web Gratuita)
```python
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    tools=[DuckDuckGoTools()], 
    show_tool_calls=True
)
agent.print_response("O que está acontecendo na França?", markdown=True)
```

## 2. Google Search
```python
from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools

agent = Agent(
    tools=[GoogleSearchTools()],
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("Quais são os últimos desenvolvimentos em IA?")
```

## 3. Tavily (Pesquisa Avançada)
```python
from agno.agent import Agent
from agno.tools.tavily import TavilyTools

agent = Agent(
    tools=[TavilyTools()],
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("Pesquise por avanços recentes em computação quântica")
```

## 4. Exa (Pesquisa Inteligente)
```python
from agno.agent import Agent
from agno.tools.exa import ExaTools

agent = Agent(
    tools=[ExaTools(
        include_domains=["cnbc.com", "reuters.com", "bloomberg.com"],
        category="news"
    )],
    show_tool_calls=True,
)
agent.print_response("Pesquise notícias sobre AAPL", markdown=True)
```

## 5. Brave Search
```python
from agno.agent import Agent
from agno.tools.bravesearch import BraveSearchTools

agent = Agent(
    tools=[BraveSearchTools()],
    show_tool_calls=True,
)
agent.print_response("AI Agents", markdown=True)
```

## 6. Baidu Search
```python
from agno.agent import Agent
from agno.tools.baidusearch import BaiduSearchTools

agent = Agent(
    tools=[BaiduSearchTools()],
    show_tool_calls=True,
)
agent.print_response("Quais são os últimos avanços em IA?", markdown=True)
```

## 7. SerpAPI
```python
from agno.agent import Agent
from agno.tools.serpapi import SerpAPITools

agent = Agent(
    tools=[SerpAPITools()],
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("Quais são os principais resultados de pesquisa para 'machine learning'?")
```

## 8. Serper (Múltiplas Funcionalidades)
```python
from agno.agent import Agent
from agno.tools.serper import SerperTools

agent = Agent(
    tools=[SerperTools()],
    show_tool_calls=True,
)
agent.print_response("Pesquise as últimas notícias sobre desenvolvimentos em inteligência artificial", markdown=True)
```

## 9. Linkup (Melhor Pesquisa para IA)
```python
from agno.agent import Agent
from agno.tools.linkup import LinkupTools

agent = Agent(
    tools=[LinkupTools()], 
    show_tool_calls=True
)
agent.print_response("Quais são as últimas notícias na política francesa?", markdown=True)
```

## 10. Pesquisa Híbrida (Combinando Múltiplas Ferramentas)
```python
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools

agent = Agent(
    tools=[
        DuckDuckGoTools(),
        ExaTools(category="news")
    ],
    show_tool_calls=True,
    markdown=True
)
agent.print_response("Pesquise informações abrangentes sobre energia renovável")
```

Cada ferramenta tem suas próprias vantagens: DuckDuckGo é gratuita, Exa é otimizada para IA, Tavily oferece pesquisa avançada, e Google/Serper fornecem resultados abrangentes.

```suggestions
(Guia de Ferramentas)[/agents/tools]
(Todas as Ferramentas Disponíveis)[/tools/toolkits/toolkits]
(Exemplos de Pesquisa)[/examples/concepts/tools/search/duckduckgo]
```

Aqui estão exemplos de código com ferramentas de pesquisa médica e acadêmica no Agno:

## 1. PubMed (Pesquisa Médica)
```python
from agno.agent import Agent
from agno.tools.pubmed import PubMedTools

# Agente para pesquisa médica
medical_agent = Agent(
    tools=[PubMedTools()],
    show_tool_calls=True,
    markdown=True,
)
medical_agent.print_response("Encontre pesquisas recentes sobre vacinas COVID-19")
```

## 2. ArXiv (Pesquisa Acadêmica)
```python
from agno.agent import Agent
from agno.tools.arxiv import ArxivTools

# Agente para pesquisa acadêmica
academic_agent = Agent(
    tools=[ArxivTools()], 
    show_tool_calls=True
)
academic_agent.print_response("Pesquise no arxiv por 'modelos de linguagem'", markdown=True)
```

## 3. Google Scholar via Serper
```python
from agno.agent import Agent
from agno.tools.serper import SerperTools

scholar_agent = Agent(
    tools=[SerperTools()],
    show_tool_calls=True,
)
scholar_agent.print_response(
    "Encontre 2 artigos acadêmicos recentes sobre segurança de modelos de linguagem",
    markdown=True,
)
```

## 4. Agente de Pesquisa Médica Avançado
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.pubmed import PubMedTools
from agno.tools.exa import ExaTools

medical_researcher = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        PubMedTools(max_results=10),
        ExaTools(
            category="research paper",
            include_domains=["pubmed.ncbi.nlm.nih.gov", "nejm.org", "thelancet.com"]
        )
    ],
    description="Especialista em pesquisa médica e análise de literatura científica",
    instructions="""
    1. Pesquise literatura médica relevante no PubMed
    2. Busque artigos complementares em revistas médicas
    3. Analise metodologias e resultados
    4. Forneça resumo com evidências científicas
    5. Cite todas as fontes adequadamente
    """,
    show_tool_calls=True,
    markdown=True
)

medical_researcher.print_response(
    "Analise os tratamentos mais eficazes para diabetes tipo 2 baseados em evidências recentes"
)
```

## 5. Agente de Pesquisa Acadêmica Completo
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.arxiv import ArxivTools
from agno.tools.serper import SerperTools
from agno.tools.exa import ExaTools

academic_researcher = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        ArxivTools(),
        SerperTools(),
        ExaTools(
            category="research paper",
            start_published_date="2024-01-01"
        )
    ],
    description="Pesquisador acadêmico especializado em análise de literatura científica",
    instructions="""
    1. Busque artigos no ArXiv para pesquisas recentes
    2. Use Google Scholar para artigos peer-reviewed
    3. Encontre papers complementares com Exa
    4. Analise metodologias e contribuições
    5. Identifique lacunas de pesquisa
    6. Formate como relatório acadêmico
    """,
    show_tool_calls=True,
    markdown=True
)

academic_researcher.print_response(
    "Faça uma revisão da literatura sobre computação quântica aplicada ao machine learning"
)
```

## 6. Workflow de Pesquisa Médica
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.pubmed import PubMedTools
from agno.tools.duckduckgo import DuckDuckGoTools

clinical_research_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        PubMedTools(email="researcher@hospital.com", max_results=15),
        DuckDuckGoTools()
    ],
    description="Especialista em pesquisa clínica e medicina baseada em evidências",
    instructions="""
    Como pesquisador clínico:
    1. Pesquise evidências no PubMed primeiro
    2. Busque guidelines clínicos atualizados
    3. Analise ensaios clínicos randomizados
    4. Avalie qualidade das evidências
    5. Forneça recomendações baseadas em evidências
    6. Inclua limitações dos estudos
    """,
    expected_output="""
    # Revisão Clínica: {Tópico}
    
    ## Resumo Executivo
    {Principais achados e recomendações}
    
    ## Evidências Científicas
    {Análise dos estudos encontrados}
    
    ## Ensaios Clínicos Relevantes
    {Resultados de RCTs importantes}
    
    ## Recomendações Clínicas
    {Orientações baseadas em evidências}
    
    ## Limitações e Lacunas
    {Áreas que precisam de mais pesquisa}
    
    ## Referências
    {Citações formatadas}
    """,
    show_tool_calls=True,
    markdown=True
)

clinical_research_agent.print_response(
    "Analise as evidências sobre eficácia da telemedicina em cuidados primários"
)
```

## 7. Pesquisa Multidisciplinar
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.pubmed import PubMedTools
from agno.tools.arxiv import ArxivTools
from agno.tools.serper import SerperTools

multidisciplinary_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        PubMedTools(max_results=8),
        ArxivTools(),
        SerperTools()
    ],
    description="Pesquisador multidisciplinar especializado em intersecções entre medicina, tecnologia e ciência",
    instructions="""
    Abordagem multidisciplinar:
    1. PubMed para literatura médica
    2. ArXiv para pesquisas técnicas/computacionais
    3. Google Scholar para estudos interdisciplinares
    4. Identifique conexões entre áreas
    5. Analise aplicações práticas
    6. Destaque inovações emergentes
    """,
    show_tool_calls=True,
    markdown=True
)

multidisciplinary_agent.print_response(
    "Pesquise sobre aplicações de inteligência artificial no diagnóstico médico por imagem"
)
```

Essas ferramentas permitem pesquisa especializada em:
- **PubMed**: Literatura médica e biomédica
- **ArXiv**: Preprints acadêmicos em física, matemática, CS
- **Google Scholar**: Artigos peer-reviewed
- **Exa**: Pesquisa otimizada para IA com filtros acadêmicos

```suggestions
(Ferramentas PubMed)[/tools/toolkits/search/pubmed]
(Ferramentas ArXiv)[/tools/toolkits/search/arxiv]
(Ferramentas Serper)[/tools/toolkits/search/serper]
```