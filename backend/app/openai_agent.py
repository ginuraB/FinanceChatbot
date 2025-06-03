import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from app.db import execute_query
from app.utils import get_stock_price_from_api, get_currency_exchange_rate_from_api
import json
import re
from jsonschema import validate, ValidationError

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- System Prompt Definition (CRITICAL for AI behavior) ---
# This prompt instructs the AI on how to format its output.
# It MUST be very precise.
SYSTEM_PROMPT = """
You are a personal finance chatbot. Your current user ID is {user_id}.
Your primary goal is to help users manage their finances by providing direct, structured, and concise answers.

**CRITICAL RULE: Always prioritize direct action. Do NOT engage in conversational filler or ask for confirmation if an action is clear.**

**CATEGORY 1: DATABASE ACTIONS (MUST respond with JSON object)**
When the user's request clearly indicates an action related to their **personal financial database** (expenses, budgets, or retrieving summaries from this database), you MUST respond with a JSON object.
The JSON object must contain an "action" key and other keys for its arguments.
Here are the actions and their required JSON formats for database interactions:

1.  To add an expense:
    {{"action": "add_expense", "amount": <float>, "category": "<string>", "description": "<string>", "expense_date": "<YYYY-MM-DD>"}}
    Example: {{"action": "add_expense", "amount": 25.50, "category": "Food", "description": "Lunch", "expense_date": "2025-05-30"}}

2.  To set a budget:
    {{"action": "set_budget", "category": "<string>", "amount": <float>, "start_date": "<YYYY-MM-DD>", "end_date": "<YYYY-MM-DD>"}}
    Example: {{"action": "set_budget", "category": "Groceries", "amount": 300.00, "start_date": "2025-06-01", "end_date": "2025-06-30"}}

3.  To get a summary of expenses from the database:
    {{"action": "get_expenses_summary", "category": "<string, optional>", "start_date": "<YYYY-MM-DD, optional>", "end_date": "<YYYY-MM-DD, optional>"}}
    Example: {{"action": "get_expenses_summary", "category": "Food", "start_date": "2025-05-01"}}
    Example: {{"action": "get_expenses_summary"}}

4.  To get a summary of budget status from the database:
    {{"action": "get_budget_status_summary", "category": "<string, optional>"}}
    Example: {{"action": "get_budget_status_summary", "category": "Groceries"}}
    Example: {{"action": "get_budget_status_summary"}}

**CATEGORY 2: EXTERNAL DATA ACTIONS (JSON for direct API, Plain Text for Search Tools)**

5.  To get stock price:
    {{"action": "get_stock_price", "symbol": "<string>"}}
    Example: {{"action": "get_stock_price", "symbol": "AAPL"}}

6.  To get currency exchange rate:
    {{"action": "get_currency_exchange_rate", "from_currency": "<string>", "to_currency": "<string>"}}
    Example: {{"action": "get_currency_exchange_rate", "from_currency": "EUR", "to_currency": "USD"}}

7.  For **real-time financial news, current economic situations, market updates, or general financial tips that require up-to-date information from the internet**, you MUST respond with **ONLY the web search query as plain text**. You MUST NOT include any introductory phrases, questions, or conversational filler. The system will automatically perform the web search based on this text.
    Example: "latest economic situation in Sri Lanka"

8.  For **information from your saved financial documents, past reports, or historical data that you have access to locally**, you MUST respond with **ONLY the file search query as plain text**. You MUST NOT include any other text or questions. The system will automatically perform the file search based on this text.
    Example: "summarize my Q1 financial report"

If the user's request does not clearly map to one of these actions (JSON output) or search types (plain text query for web/file search), or if you need more information to fulfill the request, ask clarifying questions in plain text.
Always use the provided user_id ({user_id}) when performing actions.
"""

# --- JSON Schemas for AI Output Validation (for parsing AI's generated JSON) ---
ADD_EXPENSE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "add_expense"},
        "amount": {"type": "number"},
        "category": {"type": "string"},
        "description": {"type": "string"},
        "expense_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
    },
    "required": ["action", "amount", "category", "expense_date"],
    "additionalProperties": False
}

SET_BUDGET_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "set_budget"},
        "category": {"type": "string"},
        "amount": {"type": "number"},
        "start_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        "end_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
    },
    "required": ["action", "category", "amount", "start_date", "end_date"],
    "additionalProperties": False
}

GET_STOCK_PRICE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "get_stock_price"},
        "symbol": {"type": "string"}
    },
    "required": ["action", "symbol"],
    "additionalProperties": False
}

GET_CURRENCY_RATE_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "get_currency_exchange_rate"},
        "from_currency": {"type": "string"},
        "to_currency": {"type": "string"}
    },
    "required": ["action", "from_currency", "to_currency"],
    "additionalProperties": False
}

GET_EXPENSES_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "get_expenses_summary"},
        "category": {"type": "string"},
        "start_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        "end_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
    },
    "required": ["action"], # Only 'action' is strictly required, others are optional
    "additionalProperties": False
}

GET_BUDGET_STATUS_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "const": "get_budget_status_summary"},
        "category": {"type": "string"}
    },
    "required": ["action"],
    "additionalProperties": False
}

# --- Custom Function Implementations (these are called by our Python code, not AI directly) ---

def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
    logger.info("Custom tool: add_expense called with user_id=%s, amount=%s, category=%s, date=%s",
                user_id, amount, category, expense_date)
    try:
        query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
        execute_query(query, (user_id, amount, category, description, expense_date))
        return {"status": "success", "message": f"Expense of {amount} in {category} added for user {user_id}."}
    except Exception as e:
        logger.exception("Error in add_expense_tool:")
        return {"status": "error", "message": f"Failed to add expense: {str(e)}"}

def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
    logger.info("Custom tool: set_budget called with user_id=%s, category=%s, amount=%s, start=%s, end=%s",
                user_id, category, amount, start_date, end_date)
    try:
        query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
        execute_query(query, (user_id, category, amount, start_date, end_date))
        return {"status": "success", "message": f"Budget of {amount} for {category} set for user {user_id}."}
    except Exception as e:
        logger.exception("Error in set_budget_tool:")
        return {"status": "error", "message": f"Failed to set budget: {str(e)}"}

def get_expenses_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
    logger.info("Custom tool: get_expenses called for user %s, category=%s, start=%s, end=%s",
                user_id, category, start_date, end_date)
    try:
        sql_query = "SELECT expense_id, user_id, amount, category, description, expense_date FROM T_SNG_Expenses WHERE user_id = ?"
        params = [user_id]
        
        if category:
            sql_query += " AND category = ?"
            params.append(category)
        if start_date:
            sql_query += " AND expense_date >= ?"
            params.append(start_date)
        if end_date:
            sql_query += " AND expense_date <= ?"
            params.append(end_date)
        
        expenses = execute_query(sql_query, tuple(params), fetch_type='all')
        if expenses:
            for exp in expenses:
                if 'expense_date' in exp and isinstance(exp['expense_date'], (type(None), type(exp['expense_date']))):
                    exp['expense_date'] = exp['expense_date'].isoformat() if exp['expense_date'] else None
            logger.info("Fetched %d expenses for user %s.", len(expenses), user_id)
            return {"status": "success", "data": expenses}
        else:
            logger.info("No expenses found for user %s with given filters.", user_id)
            return {"status": "success", "data": [], "message": "No expenses found."}
    except Exception as e:
        logger.exception("Error in get_expenses_tool:")
        return {"status": "error", "message": f"Failed to retrieve expenses: {str(e)}"}

def get_budget_status_tool(user_id: int, category: str = None):
    """
    Retrieves the budget status for a user, optionally by category.
    Shows budgeted, actual spent, and remaining amounts.
    Args:
        user_id (int): The ID of the user.
        category (str, optional): Filter budget status by category.
    Returns:
        list: A list of budget status dictionaries.
    """
    logger.info("Custom tool: get_budget_status called for user %s, category=%s", user_id, category)
    try:
        sql_query = """
        SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
        FROM V_SNG_BudgetStatus_L1
        WHERE user_id = ?
        """
        params = [user_id]
        if category:
            sql_query += " AND category = ?"
            params.append(category)
        
        budgets = execute_query(sql_query, tuple(params), fetch_type='all')
        if budgets:
            for bgt in budgets:
                if 'start_date' in bgt and isinstance(bgt['start_date'], (type(None), type(bgt['start_date']))):
                    bgt['start_date'] = bgt['start_date'].isoformat() if bgt['start_date'] else None
                if 'end_date' in bgt and isinstance(bgt['end_date'], (type(None), type(bgt['end_date']))):
                    bgt['end_date'] = bgt['end_date'].isoformat() if bgt['end_date'] else None
            logger.info("Fetched %d budgets for user %s.", len(budgets), user_id)
            return {"status": "success", "data": budgets}
        else:
            logger.info("No budgets found for user %s with given filters.", user_id)
            return {"status": "success", "data": [], "message": "No budgets found."}
    except Exception as e:
        logger.exception("Error in get_budget_status_tool:")
        return {"status": "error", "message": f"Failed to retrieve budget status: {str(e)}"}

def get_stock_price_tool(symbol: str): # This function will be called by our parsing logic
    """
    Retrieves the current stock price for a given symbol.
    """
    logger.info("Custom tool: get_stock_price_tool (wrapper) called for symbol: %s", symbol)
    return get_stock_price_from_api(symbol) # Call the actual API function

def get_currency_exchange_rate_tool(from_currency: str, to_currency: str): # This function will be called by our parsing logic
    """
    Retrieves the current exchange rate between two currencies.
    """
    logger.info("Custom tool: get_currency_exchange_rate_tool (wrapper) called from %s to %s", from_currency, to_currency)
    return get_currency_exchange_rate_from_api(from_currency, to_currency) # Call the actual API function

# --- OpenAI Agent Orchestration ---

def chat_with_agent(user_message: str, user_id: int):
    """
    Sends a user message to the OpenAI agent and gets a response.
    The agent is instructed to output JSON for custom actions,
    or plain text for web/file search.
    Args:
        user_message (str): The message from the user.
        user_id (int): The ID of the current user.
    Returns:
        str: The agent's response.
    """
    logger.info("Chat with agent: User %s message: %s", user_id, user_message)

    # The full system prompt with instructions for AI-generated JSON
    full_system_prompt = SYSTEM_PROMPT.format(user_id=user_id)

    # Define the tools available to the Responses API call
    # IMPORTANT: Only native OpenAI tools (web_search_preview, file_search, code_interpreter)
    # can be directly passed to client.responses.create in this manner.
    # Our custom functions are NOT listed here.
    all_native_openai_tools = [
        {"type": "web_search_preview"}, # As per documentation
        {"type": "file_search", "vector_store_ids": ["vs_6836df8f306881919cf54b2d7e654e4f"]} # As per documentation
    ]

    try:
        # Step 1: Call the Responses API. The AI processes the user message and system prompt.
        # It will either generate plain text or the instructed JSON.
        response_obj = client.responses.create(
            model="gpt-4o-mini", # Use a model that supports these tools
            input=f"{full_system_prompt}\nUser: {user_message}", # Combine prompt and user message
            tools=all_native_openai_tools, # Only native tools here
            tool_choice="auto" # Allow the model to choose native tools or respond directly
        )

        final_response_content = "I couldn't generate a response." # Default error message

        # Step 2: Process the outputs from the Responses API
        for output_item in response_obj.output:
            if output_item.type == "message" and output_item.role == "assistant":
                ai_generated_text = output_item.content[0].text
                logger.info("AI generated raw text: %s", ai_generated_text)

                # --- Attempt to parse AI's text output as a custom function call (the workaround) ---
                try:
                    # Use regex to find a potential JSON object in the AI's response
                    # This regex tries to find the first JSON-like string starting with { and ending with }
                    json_match = re.search(r'\{[^{}]*?\}', ai_generated_text, re.DOTALL)
                    
                    if json_match:
                        potential_json = json_match.group(0)
                        ai_action = json.loads(potential_json)
                        logger.info("Attempted to parse AI output as JSON action: %s", ai_action)

                        # Map parsed action to our internal Python functions
                        # and validate against schema
                        action_type = ai_action.get("action")
                        
                        if action_type == "add_expense":
                            validate(instance=ai_action, schema=ADD_EXPENSE_SCHEMA)
                            # Pass only relevant args, excluding 'action'
                            result = add_expense_tool(user_id=user_id, **{k: v for k, v in ai_action.items() if k != 'action'})
                            if result.get('status') == 'success':
                                final_response_content = f"Expense added successfully! {result.get('message', '')}"
                            else:
                                final_response_content = f"Error adding expense: {result.get('message', 'Unknown error')}"

                        elif action_type == "set_budget":
                            validate(instance=ai_action, schema=SET_BUDGET_SCHEMA)
                            result = set_budget_tool(user_id=user_id, **{k: v for k, v in ai_action.items() if k != 'action'})
                            if result.get('status') == 'success':
                                final_response_content = f"Budget set successfully! {result.get('message', '')}"
                            else:
                                final_response_content = f"Error setting budget: {result.get('message', 'Unknown error')}"

                        elif action_type == "get_stock_price":
                            validate(instance=ai_action, schema=GET_STOCK_PRICE_SCHEMA)
                            result = get_stock_price_tool(**{k: v for k, v in ai_action.items() if k != 'action'})
                            if result.get('error'):
                                final_response_content = f"Could not get stock price: {result['error']}"
                            else:
                                final_response_content = f"The current price of {result['symbol']} is {result['price']} {result['currency']}."

                        elif action_type == "get_currency_exchange_rate":
                            validate(instance=ai_action, schema=GET_CURRENCY_RATE_SCHEMA)
                            result = get_currency_exchange_rate_tool(**{k: v for k, v in ai_action.items() if k != 'action'})
                            if result.get('error'):
                                final_response_content = f"Could not get exchange rate: {result['error']}"
                            else:
                                final_response_content = f"The exchange rate from {result['from']} to {result['to']} is {result['rate']}."
                        
                        # --- Handle get_expenses_summary ---
                        elif action_type == "get_expenses_summary":
                            validate(instance=ai_action, schema=GET_EXPENSES_SUMMARY_SCHEMA)
                            # Extract optional filters
                            summary_category = ai_action.get('category')
                            summary_start_date = ai_action.get('start_date')
                            summary_end_date = ai_action.get('end_date')

                            # Call the underlying tool function
                            result = get_expenses_tool(
                                user_id=user_id,
                                category=summary_category,
                                start_date=summary_start_date,
                                end_date=summary_end_date
                            )
                            
                            if result.get('status') == 'success' and result.get('data'):
                                expenses_data = result['data']
                                total_spent = sum(float(exp['amount']) for exp in expenses_data)
                                
                                # Group by category for a better summary
                                category_summary = {}
                                for exp in expenses_data:
                                    cat = exp['category']
                                    amount = float(exp['amount'])
                                    category_summary[cat] = category_summary.get(cat, 0.0) + amount
                                
                                markdown_summary = f"## Your Expenses Summary\n\n"
                                if summary_category:
                                    markdown_summary += f"**Category:** {summary_category}\n"
                                if summary_start_date and summary_end_date:
                                    markdown_summary += f"**Period:** {summary_start_date} to {summary_end_date}\n"
                                elif summary_start_date:
                                    markdown_summary += f"**Starting from:** {summary_start_date}\n"
                                
                                markdown_summary += f"**Total Spent:** ${total_spent:.2f}\n\n"
                                
                                if category_summary:
                                    markdown_summary += "**Breakdown by Category:**\n"
                                    for cat, amount in category_summary.items():
                                        markdown_summary += f"* {cat}: ${amount:.2f}\n"
                                
                                markdown_summary += "\n**Recent Transactions:**\n"
                                if expenses_data:
                                    # Limit to top 5 recent transactions for brevity
                                    for exp in expenses_data[:5]:
                                        markdown_summary += f"* **{exp['category']}**: ${float(exp['amount']):.2f} on {exp['expense_date']} - {exp['description']}\n"
                                else:
                                    markdown_summary += "* No recent transactions found for the specified criteria.\n"

                                final_response_content = markdown_summary
                            else:
                                final_response_content = f"No expenses found for user {user_id} with the specified criteria."
                                if result.get('message'):
                                    final_response_content += f" ({result['message']})"

                        # --- Handle get_budget_status_summary ---
                        elif action_type == "get_budget_status_summary":
                            validate(instance=ai_action, schema=GET_BUDGET_STATUS_SUMMARY_SCHEMA)
                            summary_category = ai_action.get('category')

                            result = get_budget_status_tool(
                                user_id=user_id,
                                category=summary_category
                            )

                            if result.get('status') == 'success' and result.get('data'):
                                budgets_data = result['data']
                                markdown_summary = "## Your Budget Status Summary\n\n"
                                
                                if summary_category:
                                    markdown_summary += f"**Category:** {summary_category}\n\n"
                                    
                                if budgets_data:
                                    for bgt in budgets_data:
                                        markdown_summary += f"### {bgt['category']} Budget\n"
                                        markdown_summary += f"* **Budgeted:** ${float(bgt['budgeted_amount']):.2f}\n"
                                        markdown_summary += f"* **Spent:** ${float(bgt['actual_spent']):.2f}\n"
                                        markdown_summary += f"* **Remaining:** ${float(bgt['remaining_amount']):.2f}\n"
                                        markdown_summary += f"* **Period:** {bgt['start_date']} to {bgt['end_date']}\n\n"
                                else:
                                    markdown_summary += "* No budget found for the specified category.\n"
                                
                                final_response_content = markdown_summary
                            else:
                                final_response_content = f"No budgets found for user {user_id} with the specified criteria."
                                if result.get('message'):
                                    final_response_content += f" ({result['message']})"

                        else:
                            # If it's JSON but not a recognized action, treat as plain text
                            final_response_content = ai_generated_text
                    else:
                        # No JSON found, treat as plain text
                        final_response_content = ai_generated_text

                except (json.JSONDecodeError, ValidationError) as parse_error:
                    logger.warning("AI did not output valid JSON for action or schema mismatch. Raw AI response: '%s' | Error: %s", ai_generated_text, parse_error)
                    final_response_content = f"I received an unexpected format from the AI. Please try rephrasing your request for custom actions. Original AI response: '{ai_generated_text}'"
                except Exception as e:
                    logger.exception("Error during custom action execution after AI parse:")
                    final_response_content = f"An internal error occurred while processing your request: {str(e)}. Please try again."

                # Handle citations from native tools if present in output_item.content[0].annotations
                if output_item.content[0].annotations:
                    citations = []
                    for annotation in output_item.content[0].annotations:
                        if annotation.type == 'url_citation' and annotation.url:
                            citations.append(f" [Source: {annotation.title or annotation.url}]")
                        elif annotation.type == 'file_citation' and annotation.filename:
                            citations.append(f" [File: {annotation.filename}]")
                    if citations:
                        final_response_content += "".join(citations)
                
                break # Processed the main message, exit loop

            # Log native tool calls made by OpenAI (for debugging)
            elif output_item.type == "web_search_call":
                logger.info("Web search tool called by OpenAI. Status: %s", output_item.status)
            elif output_item.type == "file_search_call":
                logger.info("File search tool called by OpenAI. Status: %s", output_item.status)
        
        return final_response_content

    except Exception as e:
        logger.exception("Error in chat_with_agent (top level):")
        return f"I'm sorry, I encountered a critical error: {str(e)}. Please try again."