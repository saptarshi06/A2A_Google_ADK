from google.adk import Agent

class FlightBookingAgent:
    def __init__(self, card_data):
        self.name = card_data['name']
        self.instructions = card_data['instructions']

    def get_adk_agent(self):
        return Agent(
            name=self.name,
            instruction=self.instructions
        )