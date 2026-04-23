import os
import json
import importlib
import asyncio
import uuid
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
MODEL_NAME = "ollama/phi3:mini"

class ADKOrchestrator:
    def __init__(self, services_dir="services"):
        self.services_dir = services_dir
        self.session_service = InMemorySessionService()
        self.agents = self._discover_and_initialize()

    def _discover_and_initialize(self):
        """Standard ADK discovery: finding agents, importing classes, and initializing."""
        agents = {}
        for root, _, files in os.walk(self.services_dir):
            card_file = next((f for f in files if f.endswith("_card.json")), None)
            py_file = next((f for f in files if f.endswith(".py") and f != "orchestrator.py"), None)
            if card_file and py_file:
                with open(os.path.join(root, card_file), 'r') as f:
                    card = json.load(f)
                
                module_path = root.replace(os.sep, '.') + '.' + py_file[:-3]
                module = importlib.import_module(module_path)
                
                class_name = card.get('class_name')
                agent_class = getattr(module, class_name)
                
                instance = agent_class(card)
                agent = instance.get_adk_agent()
                agent.model = MODEL_NAME
                agents[card['name']] = agent
        return agents

    async def run_async(self, agent_name: str, user_input: str, user_id: str = "default_user", session_id: str = None):
        """Runs the specified agent asynchronously with proper session management."""
        agent = self.agents.get(agent_name)
        if not agent:
            return "Agent not found."
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Await session creation before using it
        await self.session_service.create_session(
            app_name="A2A_Portal",
            user_id=user_id,
            session_id=session_id,
            state={}
        )
        
        runner = Runner(
            agent=agent,
            app_name="A2A_Portal",
            session_service=self.session_service
        )
        
        user_content = types.Content(
            role='user',
            parts=[types.Part.from_text(text=user_input)]
        )
        
        response_text = ""
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                response_text += part.text
        except Exception as e:
            response_text = f"An error occurred during agent execution: {e}"
            
        return response_text.strip() or "Agent completed but provided no text response."

    def run(self, agent_name: str, user_input: str, user_id: str = "default_user"):
        """Synchronous wrapper for run_async - generates session_id internally."""
        session_id = str(uuid.uuid4())
        return asyncio.run(self.run_async(agent_name, user_input, user_id, session_id))