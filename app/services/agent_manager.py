from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.storage.mongodb import MongoDbStorage
from typing import Dict, Optional, List, Any
import os
from app.models.instance import AgentInstance, ModelProvider, HierarchicalAgentConfig, ToolConfig, ToolType

from pymongo import uri_parser

class AgentManager:
    def __init__(self):
        self.teams_cache: Dict[str, Team] = {}
        self.mongodb_url = os.getenv("MONGODB_URL")
        
        db_name = None
        if self.mongodb_url:
            try:
                parsed_uri = uri_parser.parse_uri(self.mongodb_url)
                db_name = parsed_uri.get('database')
            except Exception:
                pass
        
        self.mongodb_database = db_name or os.getenv("MONGODB_DATABASE")

    def _get_cache_key(self, user_id: str, instance_id: str) -> str:
        return f"{user_id}:{instance_id}"

    def _create_model(self, provider: ModelProvider, model_id: str):
        if provider == ModelProvider.OPENAI:
            return OpenAIChat(id=model_id)
        elif provider == ModelProvider.CLAUDE:
            return Claude(id=model_id)
        elif provider == ModelProvider.GEMINI:
            return Gemini(id=model_id)
        elif provider == ModelProvider.GROQ:
            return Groq(id=model_id)
        return Gemini(id="gemini-1.5-flash")

    def _create_tools(self, tool_configs: List[ToolConfig]) -> List[Any]:
        """Cria instâncias de ferramentas com base na configuração dinâmica."""
        tools = []
        for tool_config in tool_configs:
            params = tool_config.config or {}
            if tool_config.type == ToolType.DUCKDUCKGO:
                tools.append(DuckDuckGoTools(**params))
            elif tool_config.type == ToolType.YFINANCE:
                # Define padrões se não forem fornecidos
                default_params = {
                    'stock_price': True, 'analyst_recommendations': True,
                    'company_info': True, 'company_news': True
                }
                final_params = {**default_params, **params}
                tools.append(YFinanceTools(**final_params))
            # Adicione lógica para outras ferramentas aqui
        return tools

    async def get_or_create_team(self, user_id: str, instance_id: str) -> Team:
        cache_key = self._get_cache_key(user_id, instance_id)
        if cache_key in self.teams_cache:
            return self.teams_cache[cache_key]

        instance = await AgentInstance.find_one(
            AgentInstance.user_id == user_id,
            AgentInstance.instance_id == instance_id
        )

        if not instance:
            instance = AgentInstance(user_id=user_id, instance_id=instance_id)
            await instance.save()

        members = []
        for agent_config in instance.agents:
            model = self._create_model(agent_config.model_provider, agent_config.model_id)
            tools = self._create_tools(agent_config.tools)
            agent = Agent(
                name=agent_config.name,
                role=agent_config.role,
                model=model,
                tools=tools,
                add_datetime_to_instructions=True,
                markdown=True,
                show_tool_calls=True
            )
            members.append(agent)

        storage = MongoDbStorage(
            collection_name=f"team_sessions_{user_id}_{instance_id}",
            db_url=self.mongodb_url,
            db_name=self.mongodb_database
        )

        team = Team(
            name=f"Team_{instance_id}",
            members=members,
            mode="coordinate",
            model=Gemini(id="gemini-1.5-flash"),
            storage=storage,
            instructions=instance.router_instructions,
            add_history_to_messages=True
        )

        self.teams_cache[cache_key] = team
        return team

    async def update_instance_hierarchy(
        self, 
        user_id: str, 
        instance_id: str, 
        hierarchy_updates: dict
    ) -> bool:
        instance = await AgentInstance.find_one(
            AgentInstance.user_id == user_id,
            AgentInstance.instance_id == instance_id
        )

        if not instance:
            new_instance_data = {
                'user_id': user_id,
                'instance_id': instance_id,
                **hierarchy_updates
            }
            # Os agentes já são objetos HierarchicalAgentConfig, não dicts
            instance = AgentInstance(**new_instance_data)
        else:
            update_data = hierarchy_updates.copy()
            if "agents" in update_data and update_data["agents"] is not None:
                # A lista já contém objetos HierarchicalAgentConfig
                instance.agents = update_data["agents"]
                del update_data["agents"] # Remove para o loop abaixo

            for key, value in update_data.items():
                if hasattr(instance, key) and value is not None:
                    setattr(instance, key, value)
        
        await instance.save()

        cache_key = self._get_cache_key(user_id, instance_id)
        if cache_key in self.teams_cache:
            del self.teams_cache[cache_key]
        
        return True

agent_manager = AgentManager()
