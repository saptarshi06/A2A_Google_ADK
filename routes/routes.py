import uuid
from flask import Blueprint, render_template, request, json
from services.orchestrator import ADKOrchestrator
import re

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
            
            output = orchestrator.run(
                agent_name=agent_to_call,
                user_input=user_query,
                user_id="web_user_1"
            )

    # clean = re.sub(r"```json|```", "", output).strip()
    # data = json.loads(clean)
    # summary = data["summary"]

    # match = re.search(r"\{.*\}", output, re.DOTALL)
    # if match:
    #     clean = match.group(0)
    #     data = json.loads(clean)
    #     summary = data.get("summary", "")
    # else:
    #     summary = "No JSON found"

    return render_template('index.html', output=output)