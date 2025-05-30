from flask import Blueprint, request, jsonify
from app.openai_agent import chat_with_agent
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    API endpoint for interacting with the personal finance chatbot agent.
    Expects JSON data: {"user_id": ..., "message": "..."}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('message')

    if not user_id or not user_message:
        logger.error("Missing user_id or message in chat request: %s", data)
        return jsonify({"error": "Missing user_id or message"}), 400

    try:
        # Call the OpenAI agent function
        agent_response = chat_with_agent(user_message, user_id)
        logger.info("Agent responded to user %s: %s", user_id, agent_response)
        return jsonify({"response": agent_response}), 200
    except Exception as e:
        logger.exception("Error during chat interaction for user %s:", user_id)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

