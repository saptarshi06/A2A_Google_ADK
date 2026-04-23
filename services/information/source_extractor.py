from google.adk import Agent
#from google.adk.tools import google_search

class InfoAgent:
    def __init__(self, card_data):
        self.name = card_data['name']
        self.instructions = card_data['instructions']

    def get_adk_agent(self):
        return Agent(
            name=self.name,
            instruction=self.instructions,
            #tools=[google_search]
        )