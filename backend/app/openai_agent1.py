# import os
# import logging
# from openai import OpenAI
# from dotenv import load_dotenv
# import json
# from datetime import datetime
# import time

# # --- Basic Setup ---
# load_dotenv()
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Initialize OpenAI Client
# try:
#     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# except Exception as e:
#     logger.error(f"Failed to initialize OpenAI client: {e}")
#     exit()

# # --- Session State Management ---
# # This dictionary holds information for the current interactive session.
# session_context = {
#     "user_id": None,
# }

# # --- JSON Database Functions (Replaces SQL) ---
# DB_PATH = "db"

# def read_json_db(file_name: str):
#     """Reads data from a JSON file in the db directory."""
#     path = os.path.join(DB_PATH, file_name)
#     if not os.path.exists(path) or os.path.getsize(path) == 0:
#         return []
#     try:
#         with open(path, 'r') as f:
#             return json.load(f)
#     except json.JSONDecodeError:
#         logger.warning(f"Could not decode JSON from {file_name}. Returning empty list.")
#         return []

# def write_json_db(file_name: str, data: list):
#     """Writes data to a JSON file in the db directory."""
#     os.makedirs(DB_PATH, exist_ok=True)
#     path = os.path.join(DB_PATH, file_name)
#     with open(path, 'w') as f:
#         json.dump(data, f, indent=4)

# # --- Tool Function Implementations (Using JSON DB) ---
# # The function names and docstrings are CRITICAL for the AI to use them correctly.

# def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
#     """Adds a new expense record to the user's account."""
#     logger.info(f"Tool called: add_expense_tool for user {user_id}")
#     try:
#         expenses = read_json_db('expenses.json')
#         new_expense = {"expense_id": len(expenses) + 1, "user_id": user_id, "amount": amount, "category": category, "description": description, "expense_date": expense_date}
#         expenses.append(new_expense)
#         write_json_db('expenses.json', expenses)
#         return f"Success: Expense of {amount} in {category} for '{description}' was added."
#     except Exception as e:
#         return f"Error: Failed to add expense due to {str(e)}"

# def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
#     """Sets a new budget for a specific category and time period for the user."""
#     logger.info(f"Tool called: set_budget_tool for user {user_id}")
#     try:
#         budgets = read_json_db('budgets.json')
#         budgets = [b for b in budgets if not (b['user_id'] == user_id and b['category'].lower() == category.lower())]
#         new_budget = {"budget_id": len(budgets) + 1, "user_id": user_id, "category": category, "amount": amount, "start_date": start_date, "end_date": end_date}
#         budgets.append(new_budget)
#         write_json_db('budgets.json', budgets)
#         return f"Success: Budget for {category} set to {amount} from {start_date} to {end_date}."
#     except Exception as e:
#         return f"Error: Failed to set budget due to {str(e)}"

# def get_expenses_summary_tool(user_id: int, category: str = None):
#     """Retrieves a summary of expenses, which can be filtered by category."""
#     logger.info(f"Tool called: get_expenses_summary_tool for user {user_id}")
#     try:
#         expenses = read_json_db('expenses.json')
#         user_expenses = [exp for exp in expenses if exp['user_id'] == user_id]
#         if category:
#             user_expenses = [exp for exp in user_expenses if exp['category'].lower() == category.lower()]
#         return json.dumps(user_expenses) if user_expenses else "No expenses found."
#     except Exception as e:
#         return f"Error: Could not get expenses due to {str(e)}"

# def get_budget_status_summary_tool(user_id: int, category: str = None):
#     """Checks the status of budgets against actual spending."""
#     logger.info(f"Tool called: get_budget_status_summary_tool for user {user_id}")
#     try:
#         budgets = read_json_db('budgets.json')
#         expenses = read_json_db('expenses.json')
#         user_budgets = [b for b in budgets if b['user_id'] == user_id]
#         if category:
#             user_budgets = [b for b in user_budgets if b['category'].lower() == category.lower()]
#         if not user_budgets:
#             return "No budgets found for the specified criteria."
        
#         summary = []
#         for b in user_budgets:
#             spent = sum(exp['amount'] for exp in expenses if exp['user_id'] == user_id and exp['category'].lower() == b['category'].lower())
#             summary.append({"category": b['category'], "budgeted": b['amount'], "spent": spent, "remaining": b['amount'] - spent})
#         return json.dumps(summary)
#     except Exception as e:
#         return f"Error: Could not get budget status due to {str(e)}"

# def get_stock_price_tool(symbol: str):
#     """Gets the current stock price for a given ticker symbol."""
#     logger.info(f"Tool called: get_stock_price_tool for symbol {symbol}")
#     # Mock response. In a real app, you would call an external API.
#     price = round(150 + (hash(symbol) % 50) + float(str(time.time())[-2:]), 2)
#     return json.dumps({"symbol": symbol, "price": price, "currency": "USD"})

# def get_currency_exchange_rate_tool(from_currency: str, to_currency: str):
#     """Gets the exchange rate between two currencies."""
#     logger.info(f"Tool called: get_currency_exchange_rate for {from_currency} to {to_currency}")
#     # Mock response.
#     rate = round(1.08 + (hash(from_currency + to_currency) % 10) / 100, 4)
#     return json.dumps({"from": from_currency, "to": to_currency, "rate": rate})


# # --- Main Agent Logic ---

# def chat_with_agent(user_message: str):
#     """Handles the conversation flow, tool execution, and state management."""
#     if not session_context["user_id"]:
#         try:
#             potential_id = int(user_message.strip())
#             session_context["user_id"] = potential_id
#             return f"Thank you! Your User ID is set to {potential_id}. How can I assist you with your finances?"
#         except (ValueError, TypeError):
#             return "Welcome to your Personal Finance Bot. To begin, please provide your numeric User ID."

#     # Define all available function tools for the AI
#     tools = [
#         {"type": "function", "function": {"name": "add_expense_tool", "description": "Adds a new expense record.", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}, "amount": {"type": "number"}, "category": {"type": "string"}, "description": {"type": "string"}, "expense_date": {"type": "string", "description": "Date in YYYY-MM-DD format."}}, "required": ["user_id", "amount", "category", "description", "expense_date"]}}},
#         {"type": "function", "function": {"name": "set_budget_tool", "description": "Sets a new budget for a category.", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}, "category": {"type": "string"}, "amount": {"type": "number"}, "start_date": {"type": "string"}, "end_date": {"type": "string"}}, "required": ["user_id", "category", "amount", "start_date", "end_date"]}}},
#         {"type": "function", "function": {"name": "get_expenses_summary_tool", "description": "Retrieves a summary of expenses.", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}, "category": {"type": "string"}}, "required": ["user_id"]}}},
#         {"type": "function", "function": {"name": "get_budget_status_summary_tool", "description": "Checks budget status against spending.", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}, "category": {"type": "string"}}, "required": ["user_id"]}}},
#         {"type": "function", "function": {"name": "get_stock_price_tool", "description": "Gets the stock price for a symbol.", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}}},
#         {"type": "function", "function": {"name": "get_currency_exchange_rate_tool", "description": "Gets the exchange rate between currencies.", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string"}, "to_currency": {"type": "string"}}, "required": ["from_currency", "to_currency"]}}},
#     ]
    
#     available_functions = {
#         "add_expense_tool": add_expense_tool,
#         "set_budget_tool": set_budget_tool,
#         "get_expenses_summary_tool": get_expenses_summary_tool,
#         "get_budget_status_summary_tool": get_budget_status_summary_tool,
#         "get_stock_price_tool": get_stock_price_tool,
#         "get_currency_exchange_rate_tool": get_currency_exchange_rate_tool,
#     }

#     try:
#         system_message = f"You are a helpful financial assistant. The current user's ID is {session_context['user_id']}. Today's date is {datetime.now().strftime('%Y-%m-%d')}. Always use the current user's ID when calling tools that require it."

#         # === Step 1: Send user message and tools to AI ===
#         response = client.responses.create(
#             model="gpt-4o-mini",
#             tools=tools,
#             tool_choice="auto",
#             input=[
#                 {"type": "message", "role": "system", "content": system_message},
#                 {"type": "message", "role": "user", "content": user_message}
#             ]
#         )

#         tool_outputs = []
#         # === Step 2: Check for tool calls and execute them ===
#         for item in response.output:
#             if item.type == "function_call":
#                 function_name = item.function.name
#                 function_to_call = available_functions[function_name]
#                 function_args = json.loads(item.function.arguments)
                
#                 logger.info(f"AI wants to call {function_name} with args: {function_args}")
                
#                 function_response = function_to_call(**function_args)
                
#                 tool_outputs.append({
#                     "type": "function_call_output", "call_id": item.call_id, "output": function_response
#                 })

#         # === Step 3: Send tool results back to AI for final response ===
#         if tool_outputs:
#             followup_response = client.responses.create(
#                 model="gpt-4o-mini", input=tool_outputs, previous_response_id=response.id
#             )
#             return followup_response.output_text
        
#         return response.output_text

#     except Exception as e:
#         logger.exception("An error occurred in chat_with_agent:")
#         return f"I'm sorry, I encountered an error: {str(e)}"

# # --- Main Interactive Execution Block ---
# # --- Main Interactive Execution Block ---
# if __name__ == "__main__":
#     print("="*50)
#     print("🤖 Personal Finance Assistant Initialized.")
#     print("   Type 'exit' or 'quit' to end the session.")
#     print("="*50)
    
#     while True:
#         # Get user input, handling potential EOFError if script is piped
#         try:
#             user_input = input("You: ")
#         except EOFError:
#             print("\n🤖 No more input detected. Goodbye!")
#             break

#         if user_input.lower() in ['exit', 'quit']:
#             print("🤖 Goodbye! Have a great day.")
#             break
        
#         # CORRECTED LINE: The function now only takes one argument.
#         assistant_response = chat_with_agent(user_input) 
#         print(f"🤖 Assistant: {assistant_response}")















































































import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from app.db import execute_query # For SQL Server interaction
from app.utils import get_stock_price_from_api, get_currency_exchange_rate_from_api # For external API calls
import json
import re
from jsonschema import validate, ValidationError
from datetime import datetime

# --- Basic Setup ---
load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize OpenAI Client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not client.api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
        # In a production app, you might raise an exception or exit more gracefully.
        client = None
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# --- Configuration: Hardcoded User ID ---
# For a single-user application as requested, the user_id is fixed.
# This ID will be automatically used for all database operations.
FIXED_USER_ID = 1 # As typically used by the frontend

# --- System Prompt Definition (CRITICAL for AI behavior) ---
# This prompt instructs the AI on how to format its output.
# It MUST be very precise.
SYSTEM_PROMPT = """
You are a personal finance chatbot. Your current user ID is {user_id}.
Your primary goal is to help users manage their finances by providing direct, structured, and concise answers.

**CRITICAL RULE: Always prioritize direct action. Do NOT engage in conversational filler or ask for confirmation if an action is clear.**
**ALWAYS use the user ID {user_id} when responding with a JSON action.**

**CATEGORY 1: DATABASE ACTIONS (MUST respond with JSON object)**
When the user's request clearly indicates an action related to their **personal financial database** (expenses or budgets), you MUST respond with a JSON object. This JSON object will be parsed by the system to execute a backend tool.
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

**CATEGORY 2: EXTERNAL DATA ACTIONS (JSON for direct API calls, Plain Text for Search Tools)**
When the user's request involves external information (stock prices, currency rates, news, or documents), you MUST respond as follows:

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
"""

# --- JSON Schemas for AI Output Validation (for parsing AI's generated JSON) ---
# These schemas validate the JSON output generated by the AI based on SYSTEM_PROMPT instructions.
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
    "required": ["action"],
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

# --- Custom Function Implementations (These interact with SQL DB or external APIs) ---
# These functions will be called by our Python code after parsing AI's JSON output.

def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
    """
    Adds a new personal expense record for a user to the SQL Server database.
    """
    logger.info(f"Custom tool: add_expense called with user_id={user_id}, amount={amount}, category={category}, date={expense_date}")
    try:
        query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
        execute_query(query, (user_id, amount, category, description, expense_date))
        return f"Success: Expense of ${amount:.2f} in {category} for '{description}' on {expense_date} was added to your database."
    except Exception as e:
        logger.exception("Error in add_expense_tool:")
        return f"Error: Failed to add expense due to a database issue. Details: {str(e)}"

def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
    """
    Sets or updates a budget for a specific category and time period for the user in the SQL Server database.
    """
    logger.info(f"Custom tool: set_budget called with user_id={user_id}, category={category}, amount={amount}, period={start_date} to {end_date}")
    try:
        existing_budget = execute_query(
            "SELECT budget_id FROM T_SNG_Budgets WHERE user_id = ? AND category = ?",
            (user_id, category),
            fetch_type='one'
        )
        
        if existing_budget:
            query = "UPDATE T_SNG_Budgets SET amount = ?, start_date = ?, end_date = ? WHERE budget_id = ?"
            execute_query(query, (amount, start_date, end_date, existing_budget['budget_id']))
            return f"Success: Budget for {category} was updated to ${amount:.2f} for {start_date} to {end_date}."
        else:
            query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
            execute_query(query, (user_id, category, amount, start_date, end_date))
            return f"Success: New budget for {category} set to ${amount:.2f} from {start_date} to {end_date}."
    except Exception as e:
        logger.exception("Error in set_budget_tool:")
        return f"Error: Failed to set budget due to a database issue. Details: {str(e)}"

def get_expenses_summary_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
    """
    Retrieves a detailed summary of the user's expenses from the SQL Server database, formatted in Markdown.
    """
    logger.info(f"Custom tool: get_expenses_summary_tool for user {user_id}, category {category}, start {start_date}, end {end_date}")
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
            total_spent = sum(float(exp['amount']) for exp in expenses)
            
            category_summary = {}
            for exp in expenses:
                cat = exp['category']
                amount = float(exp['amount'])
                category_summary[cat] = category_summary.get(cat, 0.0) + amount
            
            markdown_summary = f"## Your Expenses Summary\n\n"
            if category:
                markdown_summary += f"**Category:** {category}\n"
            if start_date and end_date:
                markdown_summary += f"**Period:** {start_date} to {end_date}\n"
            elif start_date:
                markdown_summary += f"**Starting from:** {start_date}\n"
            
            markdown_summary += f"**Total Spent:** ${total_spent:.2f}\n\n"
            
            if category_summary:
                markdown_summary += "**Breakdown by Category:**\n"
                for cat, amount in category_summary.items():
                    markdown_summary += f"* {cat}: ${amount:.2f}\n"
            
            markdown_summary += "\n**Recent Transactions (max 5):**\n"
            # Sort by date descending and limit to top 5 for display
            sorted_expenses = sorted(expenses, key=lambda x: x['expense_date'], reverse=True)
            for exp in sorted_expenses[:5]:
                markdown_summary += f"* **{exp['category']}**: ${float(exp['amount']):.2f} on {exp['expense_date']} - {exp['description']}\n"
            
            return markdown_summary
        else:
            return "No expenses found for the specified criteria. Try adding some expenses first!"
    except Exception as e:
        logger.exception("Error in get_expenses_summary_tool:")
        return f"Error: Could not retrieve expense summary due to a database issue. Details: {str(e)}"

def get_budget_status_summary_tool(user_id: int, category: str = None):
    """
    Retrieves the status of budgets from the SQL Server database, formatted in Markdown.
    """
    logger.info(f"Custom tool: get_budget_status_summary_tool for user {user_id}, category {category}")
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
        
        budgets_data = execute_query(sql_query, tuple(params), fetch_type='all')

        if budgets_data:
            markdown_summary = "## Your Budget Status Summary\n\n"
            
            if category: # Use the 'category' from the tool call arguments
                markdown_summary += f"**Category Filter:** {category}\n\n"
                
            for bgt in budgets_data:
                markdown_summary += f"### {bgt['category']} Budget\n"
                markdown_summary += f"* **Budgeted:** ${float(bgt['budgeted_amount']):.2f}\n"
                markdown_summary += f"* **Spent:** ${float(bgt['actual_spent']):.2f}\n"
                markdown_summary += f"* **Remaining:** ${float(bgt['remaining_amount']):.2f}\n"
                markdown_summary += f"* **Period:** {bgt['start_date']} to {bgt['end_date']}\n\n"
            
            return markdown_summary
        else:
            return "No budgets found for the specified criteria. Try setting some budgets first!"
    except Exception as e:
        logger.exception("Error in get_budget_status_summary_tool:")
        return f"Error: Could not retrieve budget status due to a database issue. Details: {str(e)}"


def get_stock_price_tool(symbol: str):
    """
    Gets the current stock price for a given ticker symbol (e.g., AAPL, GOOGL, MSFT) using an external API.
    Returns the symbol, price, and currency.
    """
    logger.info(f"Custom tool: get_stock_price_tool called for symbol {symbol}")
    result = get_stock_price_from_api(symbol) # Call the real API function from app.utils
    if result.get('error'):
        return f"Error: Could not get stock price for {symbol.upper()}. Details: {result['error']}"
    return f"Success: The current price of {result['symbol']} is ${result['price']:.2f} {result['currency']}."

def get_currency_exchange_rate_tool(from_currency: str, to_currency: str):
    """
    Gets the exchange rate between two currency codes (e.g., USD, EUR, LKR) using an external API.
    Returns the source currency, target currency, and the exchange rate.
    """
    logger.info(f"Custom tool: get_currency_exchange_rate_tool called for {from_currency} to {to_currency}")
    result = get_currency_exchange_rate_from_api(from_currency, to_currency) # Call the real API function from app.utils
    if result.get('error'):
        return f"Error: Could not get exchange rate for {from_currency.upper()} to {to_currency.upper()}. Details: {result['error']}"
    return f"Success: The exchange rate from {result['from']} to {result['to']} is {result['rate']:.4f}."

# --- Wrapper functions for OpenAI's Native Tools (called by our Python code, execute client.responses.create internally) ---
# These are NOT in the 'tools' list for the AI; they are called by our manual parsing if the AI outputs a search query.

def web_search_tool_internal(query: str):
    """
    Performs a web search using OpenAI's native web_search_preview tool.
    This function is called internally when the AI indicates a web search is needed.
    """
    logger.info(f"Internal web search tool triggered for query: {query}")
    try:
        if client is None:
            return "Error: OpenAI client not initialized for native tools."
        
        # Make the actual client.responses.create call for the native web search tool
        response_from_native_tool = client.responses.create(
            model="gpt-4o-mini", # Model that supports web search
            input=query, # The actual query for the web search tool
            tools=[{"type": "web_search_preview"}],
            tool_choice={"type": "web_search_preview"} # Force the native web search tool
        )
        
        # Extract the message content which should contain the web search results
        # The AI is prompted to return this directly, formatted as Markdown.
        for output_item in response_from_native_tool.output:
            if output_item.type == "message" and output_item.role == "assistant":
                content = output_item.content[0].text
                citations = []
                if output_item.content[0].annotations:
                    for annotation in output_item.content[0].annotations:
                        if annotation.type == 'url_citation' and annotation.url:
                            citations.append(f" [Source: {annotation.title or annotation.url}]")
                
                formatted_content = f"### Web Search Results for '{query}'\n\n"
                formatted_content += content # AI is prompted to return structured content itself
                if citations:
                    formatted_content += "\n\n**Sources:**\n" + "\n".join(citations)

                return formatted_content
        return f"No direct web search results found for '{query}'."

    except Exception as e:
        logger.exception(f"Error during native web search for query '{query}':")
        return f"Error: Failed to perform web search. Details: {str(e)}. Please check your OpenAI API key."

def file_search_tool_internal(query: str, vector_store_ids: list):
    """
    Searches saved financial documents using OpenAI's native file_search tool.
    This function is called internally when the AI indicates a file search is needed.
    """
    logger.info(f"Internal file search tool triggered for query: {query}, stores: {vector_store_ids}")
    try:
        if client is None:
            return "Error: OpenAI client not initialized for native tools."

        # Make the actual client.responses.create call for the native file search tool
        response_from_native_tool = client.responses.create(
            model="gpt-4o-mini", # Model that supports file search
            input=query, # The actual query for the file search tool
            tools=[{
                "type": "file_search",
                "vector_store_ids": vector_store_ids
            }],
            tool_choice={"type": "file_search"} # Force the native file search tool
        )

        # Extract the message content which should contain the file search results
        # The AI is prompted to return this directly, formatted as Markdown.
        for output_item in response_from_native_tool.output:
            if output_item.type == "message" and output_item.role == "assistant":
                content = output_item.content[0].text
                citations = []
                if output_item.content[0].annotations:
                    for annotation in output_item.content[0].annotations:
                        if annotation.type == 'file_citation' and annotation.filename:
                            citations.append(f" [File: {annotation.filename}]")
                
                formatted_content = f"### File Search Results for '{query}'\n\n"
                formatted_content += content # AI is prompted to return structured content itself
                if citations:
                    formatted_content += "\n\n**Sources:**\n" + "\n".join(citations)
                return formatted_content
        return f"No direct file search results found for '{query}' in the specified vector stores."

    except Exception as e:
        logger.exception(f"Error during native file search for query '{query}':")
        return f"Error: Failed to perform file search. Details: {str(e)}. Please check your vector store ID and file availability."

# --- Main Agent Logic ---

def chat_with_agent(user_message: str, current_user_id: int = FIXED_USER_ID):
    """
    Handles the conversation flow, custom tool execution (via JSON parsing),
    and native OpenAI tool execution (web/file search).
    All AI output is processed to extract actions or returned as plain text.
    """
    if client is None:
        return "AI agent is not initialized. Please check backend logs for OpenAI API key issues."

    # Use the hardcoded/provided user ID for all operations
    user_id_for_tools = current_user_id

    # The full system prompt with instructions for AI-generated JSON or plain text queries
    # The user_id is injected into the prompt.
    full_system_prompt_formatted = SYSTEM_PROMPT.format(user_id=user_id_for_tools)

    # All API calls will use client.responses.create.
    # The 'tools' parameter here is ONLY for OpenAI's native tools.
    # Our custom Python functions are NOT directly listed here.
    all_native_openai_tools_for_responses_api = [
        {"type": "web_search_preview"}, # As per documentation
        {"type": "file_search", "vector_store_ids": ["vs_6836df8f306881919cf54b2d7e654e4f"]} # Replace with your actual vector store ID
    ]

    try:
        # Step 1: Call the Responses API. The AI processes the user message and system prompt.
        # It will either generate JSON for custom actions, a plain text query for native search,
        # or a natural language response.
        response_obj = client.responses.create(
            model="gpt-4o-mini", # Using gpt-4o-mini as it supports web/file search and is cheaper
            input=f"{full_system_prompt_formatted}\nUser: {user_message}",
            tools=all_native_openai_tools_for_responses_api, # Pass only native tools here
            tool_choice="auto" # Let AI decide if it needs native tools or just text
        )

        final_response_content = "I couldn't generate a response." # Default fallback message

        # Step 2: Process the outputs from the Responses API
        # The AI's primary output for us to interpret comes in a "message" item.
        for output_item in response_obj.output:
            if output_item.type == "message" and output_item.role == "assistant":
                ai_generated_text = output_item.content[0].text
                logger.info("AI generated raw text from Response API message: %s", ai_generated_text)

                # --- Attempt to parse AI's text output for custom function calls (the workaround) ---
                try:
                    # Regex to find a potential JSON object in the AI's response.
                    # This regex is specifically looking for content that starts with { and ends with }
                    # and contains a recognizable "action" key.
                    json_match = re.search(r'\{.*?"action":\s*"(add_expense|set_budget|get_expenses_summary|get_budget_status_summary|get_stock_price|get_currency_exchange_rate)".*?\}', ai_generated_text, re.DOTALL)
                    
                    if json_match:
                        potential_json_string = json_match.group(0)
                        ai_action = json.loads(potential_json_string)
                        logger.info("Parsed AI output as JSON action: %s", ai_action)

                        # Map parsed action to our internal Python functions and validate against schema
                        action_type = ai_action.get("action")
                        
                        # --- Dispatch to Custom Functions (Database & External API Wrappers) ---
                        if action_type == "add_expense":
                            validate(instance=ai_action, schema=ADD_EXPENSE_SCHEMA)
                            # Pass user_id explicitly and unpack other arguments
                            result = add_expense_tool(user_id=user_id_for_tools, **{k: v for k, v in ai_action.items() if k != 'action'})
                            final_response_content = result # Function returns string message
                        
                        elif action_type == "set_budget":
                            validate(instance=ai_action, schema=SET_BUDGET_SCHEMA)
                            result = set_budget_tool(user_id=user_id_for_tools, **{k: v for k, v in ai_action.items() if k != 'action'})
                            final_response_content = result
                        
                        elif action_type == "get_stock_price":
                            validate(instance=ai_action, schema=GET_STOCK_PRICE_SCHEMA)
                            result = get_stock_price_tool(**{k: v for k, v in ai_action.items() if k != 'action'})
                            final_response_content = result
                        
                        elif action_type == "get_currency_exchange_rate":
                            validate(instance=ai_action, schema=GET_CURRENCY_RATE_SCHEMA)
                            result = get_currency_exchange_rate_tool(**{k: v for k, v in ai_action.items() if k != 'action'})
                            final_response_content = result
                        
                        elif action_type == "get_expenses_summary":
                            validate(instance=ai_action, schema=GET_EXPENSES_SUMMARY_SCHEMA)
                            # Extract optional filters for expenses summary
                            params = {k: v for k, v in ai_action.items() if k != 'action'}
                            result = get_expenses_summary_tool(user_id=user_id_for_tools, **params)
                            final_response_content = result # This function already returns Markdown
                        
                        elif action_type == "get_budget_status_summary":
                            validate(instance=ai_action, schema=GET_BUDGET_STATUS_SUMMARY_SCHEMA)
                            # Extract optional filters for budget summary
                            params = {k: v for k, v in ai_action.items() if k != 'action'}
                            result = get_budget_status_summary_tool(user_id=user_id_for_tools, **params)
                            final_response_content = result # This function already returns Markdown
                        
                        else:
                            # Fallback if JSON is valid but action is not recognized
                            logger.warning(f"AI generated unrecognized JSON action: {ai_action}")
                            final_response_content = "I understood a JSON command, but it was for an unrecognized action. Please ensure your request maps to a defined financial action."
                    else:
                        # --- If no JSON action is found, treat the AI's output as a search query or general text ---
                        # In this setup, for web/file search, AI is prompted to return ONLY the query.
                        # So, we pass it directly to the internal search wrappers.
                        query_for_search = ai_generated_text.strip()
                        
                        # Heuristic: If the query sounds like a search, use the wrapper tools.
                        # This is the fragile part where AI's plain text output is interpreted.
                        # Improved heuristic: If it's not a JSON action, assume it's a search query based on prompt.
                        if "financial news" in query_for_search.lower() or \
                           "economic situation" in query_for_search.lower() or \
                           "market updates" in query_for_search.lower() or \
                           "tip" in query_for_search.lower() or \
                           "latest" in query_for_search.lower():
                            # It's a web search
                            final_response_content = web_search_tool_internal(query_for_search)
                        elif "summarize" in query_for_search.lower() and ("report" in query_for_search.lower() or "document" in query_for_search.lower()):
                            # It's a file search (assuming a default vector store ID)
                            final_response_content = file_search_tool_internal(query_for_search, ["vs_6836df8f306881919cf54b2d7e654e4f"]) # Hardcode your vector store ID
                        else:
                            # Default: if no JSON action and no clear search query, just return AI's text
                            final_response_content = ai_generated_text

                except (json.JSONDecodeError, ValidationError) as parse_error:
                    # This means AI tried to output JSON but it was invalid or didn't match a schema
                    logger.warning("AI outputted invalid JSON or schema mismatch for action. Raw AI response: '%s' | Error: %s", ai_generated_text, parse_error)
                    final_response_content = f"I received an unexpected format from the AI. Please try rephrasing your request. (Error details: {parse_error})"
                except Exception as e:
                    # Catch any other errors during custom action execution
                    logger.exception("Error during custom action execution after AI parse:")
                    final_response_content = f"An internal error occurred while processing your action: {str(e)}. Please try again."

                # Handle citations from native tools if present in output_item.content[0].annotations
                # These citations are part of the 'message' content, not separate output_items.
                if output_item.content[0].annotations:
                    citations = []
                    for annotation in output_item.content[0].annotations:
                        if annotation.type == 'url_citation' and annotation.url:
                            citations.append(f" [Source: {annotation.title or annotation.url}]")
                        elif annotation.type == 'file_citation' and annotation.filename:
                            citations.append(f" [File: {annotation.filename}]")
                    if citations:
                        # Append citations to the already formatted content
                        final_response_content += "\n\n" + "".join(citations)
                
                break # Processed the main message, exit loop (we only expect one 'message' output item)

            # Log native tool calls made by OpenAI (for debugging)
            # These output_items indicate that OpenAI's *internal* web/file search was triggered.
            # Their results are expected to be integrated into the 'message' output_item.
            elif output_item.type == "web_search_call":
                logger.info("Responses API native web search tool triggered internally by OpenAI. Status: %s", output_item.status)
                # No action needed here, as the results are expected in the 'message' output_item.
            elif output_item.type == "file_search_call":
                logger.info("Responses API native file search tool triggered internally by OpenAI. Status: %s", output_item.status)
                # No action needed here, as the results are expected in the 'message' output_item.
        
        return final_response_content

    except Exception as e:
        logger.exception("Error in chat_with_agent (top level):")
        return f"I'm sorry, I encountered a critical error: {str(e)}. Please try again."

# --- Main Interactive Execution Block (for direct script testing, if needed) ---
if __name__ == "__main__":
    print("="*50)
    print("🤖 Personal Finance Assistant (openai_agent1.py) Initialized.")
    print(f"    Using fixed User ID: {FIXED_USER_ID}")
    print("    Type 'exit' or 'quit' to end the session.")
    print("="*50)
    
    # Initialize session_context for this direct script run if it wasn't already
    if "messages" not in session_context:
        session_context["messages"] = []

    # Initial greeting
    print(f"🤖 Assistant: Welcome to your Personal Finance Bot. I'm ready to help you with User ID {FIXED_USER_ID}.")

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            print("\n🤖 No more input detected. Goodbye!")
            break

        if user_input.lower() in ['exit', 'quit']:
            print("🤖 Goodbye! Have a great day.")
            break
        
        # Pass the hardcoded user ID to the agent function
        assistant_response = chat_with_agent(user_input, FIXED_USER_ID)
        print(f"🤖 Assistant: {assistant_response}")










