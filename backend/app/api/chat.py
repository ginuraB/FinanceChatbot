#-----------for openai_agent1.py-----------

# from flask import Blueprint, request, jsonify
# from app.openai_agent import chat_with_agent
# import logging

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# chat_bp = Blueprint('chat', __name__)

# @chat_bp.route('/chat', methods=['POST'])
# def chat():
#     """
#     API endpoint for interacting with the personal finance chatbot agent.
#     Expects JSON data: {"user_id": ..., "message": "..."}
#     """
#     data = request.get_json()
#     user_id = data.get('user_id')
#     user_message = data.get('message')

#     if not user_id or not user_message:
#         logger.error("Missing user_id or message in chat request: %s", data)
#         return jsonify({"error": "Missing user_id or message"}), 400

#     try:
#         # Call the OpenAI agent function
#         agent_response = chat_with_agent(user_message, user_id)
#         logger.info("Agent responded to user %s: %s", user_id, agent_response)
#         return jsonify({"response": agent_response}), 200
#     except Exception as e:
#         logger.exception("Error during chat interaction for user %s:", user_id)
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500






#-----------for openai_agent1.py and-----------openai_agent1.py----------------------
from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv
import logging # Import logging directly in this module

# Initialize logger for this module
logger = logging.getLogger(__name__)

# IMPORTANT: Define the Blueprint FIRST.
# This ensures 'chat_bp' is available in the module's namespace
# before any other complex imports or conditional logic might cause issues.
chat_bp = Blueprint('chat', __name__)

# Load environment variables to access ACTIVE_AI_AGENT
load_dotenv()

# --- Dynamic Agent Import ---
# This section determines which openai_agent file to import
# based on the ACTIVE_AI_AGENT environment variable.
AGENT_FILE_NAME = os.getenv("ACTIVE_AI_AGENT")

# Define a variable to hold the imported chat_with_agent function
chat_with_agent = None

if AGENT_FILE_NAME == "openai_agent.py":
    try:
        # Import the specific chat_with_agent function
        from app.openai_agent import chat_with_agent as active_chat_agent
        chat_with_agent = active_chat_agent
        logger.info(f"--- Backend: Using openai_agent.py ---")
    except ImportError as e:
        logger.error(f"Error: Could not import chat_with_agent from openai_agent.py: {e}")
        chat_with_agent = None # Ensure it's None if import fails
elif AGENT_FILE_NAME == "openai_agent1.py":
    try:
        # Import the specific chat_with_agent function from openai_agent1.py
        from app.openai_agent1 import chat_with_agent as active_chat_agent
        chat_with_agent = active_chat_agent
        logger.info(f"--- Backend: Using openai_agent1.py ---")
    except ImportError as e:
        logger.error(f"Error: Could not import chat_with_agent from openai_agent1.py: {e}")
        chat_with_agent = None # Ensure it's None if import fails
else:
    logger.error(f"Error: ACTIVE_AI_AGENT environment variable not set or invalid: '{AGENT_FILE_NAME}'. "
                 f"Please set it to 'openai_agent.py' or 'openai_agent1.py'.")
    chat_with_agent = None # Ensure it's None if no valid agent is specified


@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    user_message = data.get('message')

    if not user_id or not user_message:
        return jsonify({"error": "Missing user_id or message"}), 400

    # Check if the chat_with_agent function was successfully loaded
    if chat_with_agent is None:
        return jsonify({"error": "AI Agent not configured or failed to load. Check backend logs for details."}), 500

    try:
        # Call the dynamically loaded chat_with_agent function
        response = chat_with_agent(user_message, user_id)
        return jsonify({"response": response})
    except Exception as e:
        # Log the specific exception to the console
        logger.exception("Error during AI agent execution in chat endpoint:")
        return jsonify({"error": str(e)}), 500

