import uuid
from flask import Blueprint, render_template, request
from services.orchestrator import ADKOrchestrator

chat_bp = Blueprint('chat_bp', __name__)
orchestrator = ADKOrchestrator()

@chat_bp.route('/', methods=['GET', 'POST'])
def chat():
    output = None
    if request.method == "POST":
        user_query = request.form.get("requirement", "")
        if user_query:
            # Agent routing logic
            if any(char.isdigit() for char in user_query):
                agent_to_call = "calculator_agent"
            elif "flight" in user_query.lower():
                agent_to_call = "flight_agent"
            else:
                agent_to_call = "extractor_agent"
            
            # FIXED: Don't pass session_id - it's generated internally
            output = orchestrator.run(
                agent_name=agent_to_call,
                user_input=user_query,
                user_id="web_user_1"
            )
            
    return render_template('index.html', output=output)