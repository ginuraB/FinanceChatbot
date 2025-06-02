# import os
# import logging
# from openai import OpenAI
# from dotenv import load_dotenv
# from app.db import execute_query
# from app.utils import get_stock_price, get_currency_exchange_rate
# import json

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # Initialize OpenAI client
# # Ensure OPENAI_API_KEY is set in your .env file
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Define Agent Tools (Python functions that the AI can call) ---

# def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
#     """
#     Adds a new personal expense for a user.
#     Args:
#         user_id (int): The ID of the user.
#         amount (float): The amount of the expense.
#         category (str): The category of the expense (e.g., 'Food', 'Transport', 'Utilities').
#         description (str): A brief description of the expense.
#         expense_date (str): The date of the expense in YYYY-MM-DD format.
#     Returns:
#         dict: A dictionary indicating success or failure.
#     """
#     logger.info("Agent tool: add_expense called with user_id=%s, amount=%s, category=%s, date=%s",
#                 user_id, amount, category, expense_date)
#     try:
#         query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, amount, category, description, expense_date))
#         return {"status": "success", "message": f"Expense of {amount} in {category} added for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in add_expense_tool:")
#         return {"status": "error", "message": f"Failed to add expense: {str(e)}"}

# def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
#     """
#     Sets a new budget for a user in a specific category for a given period.
#     Args:
#         user_id (int): The ID of the user.
#         category (str): The category for the budget (e.g., 'Groceries', 'Entertainment').
#         amount (float): The budgeted amount.
#         start_date (str): The start date of the budget in YYYY-MM-DD format.
#         end_date (str): The end date of the budget in YYYY-MM-DD format.
#     Returns:
#         dict: A dictionary indicating success or failure.
#     """
#     logger.info("Agent tool: set_budget called with user_id=%s, category=%s, amount=%s, start=%s, end=%s",
#                 user_id, category, amount, start_date, end_date)
#     try:
#         # Note: category and amount order in DB schema might differ from function args.
#         # Ensure correct mapping to DB columns.
#         query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, category, amount, start_date, end_date)) 
#         return {"status": "success", "message": f"Budget of {amount} for {category} set for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in set_budget_tool:")
#         return {"status": "error", "message": f"Failed to set budget: {str(e)}"}

# def get_expenses_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
#     """
#     Retrieves a user's expenses, optionally filtered by category and date range.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter expenses by category.
#         start_date (str, optional): Start date for filtering in YYYY-MM-DD format.
#         end_date (str, optional): End date for filtering in YYYY-MM-DD format.
#     Returns:
#         list: A list of expense dictionaries.
#     """
#     logger.info("Agent tool: get_expenses called for user %s, category=%s, start=%s, end=%s",
#                 user_id, category, start_date, end_date)
#     try:
#         sql_query = "SELECT expense_id, user_id, amount, category, description, expense_date FROM T_SNG_Expenses WHERE user_id = ?"
#         params = [user_id]
        
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
#         if start_date:
#             sql_query += " AND expense_date >= ?"
#             params.append(start_date)
#         if end_date:
#             sql_query += " AND expense_date <= ?"
#             params.append(end_date)
        
#         expenses = execute_query(sql_query, tuple(params), fetch_type='all')
#         if expenses:
#             # Convert date objects to string for JSON serialization
#             for exp in expenses:
#                 if 'expense_date' in exp and isinstance(exp['expense_date'], (type(None), type(exp['expense_date']))):
#                     exp['expense_date'] = exp['expense_date'].isoformat() if exp['expense_date'] else None
#             logger.info("Fetched %d expenses for user %s.", len(expenses), user_id)
#             return {"status": "success", "data": expenses}
#         else:
#             logger.info("No expenses found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No expenses found."}
#     except Exception as e:
#         logger.exception("Error in get_expenses_tool:")
#         return {"status": "error", "message": f"Failed to retrieve expenses: {str(e)}"}

# def get_budget_status_tool(user_id: int, category: str = None):
#     """
#     Retrieves the budget status for a user, optionally by category.
#     Shows budgeted, actual spent, and remaining amounts.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter budget status by category.
#     Returns:
#         list: A list of budget status dictionaries.
#     """
#     logger.info("Agent tool: get_budget_status called for user %s, category=%s", user_id, category)
#     try:
#         sql_query = """
#         SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
#         FROM V_SNG_BudgetStatus_L1
#         WHERE user_id = ?
#         """
#         params = [user_id]
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
        
#         budgets = execute_query(sql_query, tuple(params), fetch_type='all')
#         if budgets:
#             # Convert date objects to string for JSON serialization
#             for bgt in budgets:
#                 if 'start_date' in bgt and isinstance(bgt['start_date'], (type(None), type(bgt['start_date']))):
#                     bgt['start_date'] = bgt['start_date'].isoformat() if bgt['start_date'] else None
#                 if 'end_date' in bgt and isinstance(bgt['end_date'], (type(None), type(bgt['end_date']))):
#                     bgt['end_date'] = bgt['end_date'].isoformat() if bgt['end_date'] else None
#             logger.info("Fetched %d budgets for user %s.", len(budgets), user_id)
#             return {"status": "success", "data": budgets}
#         else:
#             logger.info("No budgets found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No budgets found."}
#     except Exception as e:
#         logger.exception("Error in get_budget_status_tool:")
#         return {"status": "error", "message": f"Failed to retrieve budget status: {str(e)}"}

# def get_stock_price_tool(symbol: str):
#     """
#     Retrieves the current stock price for a given stock ticker symbol (e.g., AAPL, GOOGL).
#     Args:
#         symbol (str): The stock ticker symbol.
#     Returns:
#         dict: A dictionary containing the stock symbol, price, and currency, or an error message.
#     """
#     logger.info("Agent tool: get_stock_price_tool called for symbol: %s", symbol)
#     return get_stock_price(symbol)

# def get_currency_exchange_rate_tool(from_currency: str, to_currency: str):
#     """
#     Retrieves the current exchange rate between two currency codes (e.g., USD, EUR, LKR).
#     Args:
#         from_currency (str): The currency code to convert from (e.g., "USD").
#         to_currency (str): The currency code to convert to (e.g., "LKR").
#     Returns:
#         dict: A dictionary containing the 'from' currency, 'to' currency, and the exchange rate, or an error message.
#     """
#     logger.info("Agent tool: get_currency_exchange_rate_tool called from %s to %s", from_currency, to_currency)
#     return get_currency_exchange_rate(from_currency, to_currency)

# # --- OpenAI Agent Orchestration ---

# def chat_with_agent(user_message: str, user_id: int):
#     """
#     Sends a user message to the OpenAI agent and gets a response.
#     The agent uses defined tools to answer queries.
#     Args:
#         user_message (str): The message from the user.
#         user_id (int): The ID of the current user.
#     Returns:
#         str: The agent's response.
#     """
#     logger.info("Chat with agent: User %s message: %s", user_id, user_message)

#     # Define the tools available to the agent
#     # These are the *function* tools that we implement ourselves
#     function_tools_definitions = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "add_expense_tool",
#                 "description": "Adds a new personal expense for a user. Use this when the user wants to record an expense. Requires user_id, amount, category, description, and expense_date (YYYY-MM-DD).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "amount": {"type": "number", "description": "The amount of the expense."},
#                         "category": {"type": "string", "description": "The category of the expense (e.g., 'Food', 'Transport', 'Utilities', 'Rent', 'Shopping')."},
#                         "description": {"type": "string", "description": "A brief description of the expense."},
#                         "expense_date": {"type": "string", "format": "date", "description": "The date of the expense in YYYY-MM-DD format."}
#                     },
#                     "required": ["user_id", "amount", "category", "expense_date"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "set_budget_tool",
#                 "description": "Sets a new budget for a user in a specific category for a given period. Use this when the user wants to set or update a budget. Requires user_id, category, amount, start_date (YYYY-MM-DD), and end_date (YYYY-MM-DD).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "category": {"type": "string", "description": "The category for the budget (e.g., 'Groceries', 'Entertainment', 'Travel', 'Utilities')."},
#                         "amount": {"type": "number", "description": "The budgeted amount."},
#                         "start_date": {"type": "string", "format": "date", "description": "The start date of the budget in YYYY-MM-DD format."},
#                         "end_date": {"type": "string", "format": "date", "description": "The end date of the budget in YYYY-MM-DD format."}
#                     },
#                     "required": ["user_id", "category", "amount", "start_date", "end_date"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_expenses_tool",
#                 "description": "Retrieves a user's expenses, optionally filtered by category and date range. Use this when the user asks about their spending or expense history. Can filter by user_id, category, start_date (YYYY-MM-DD), and end_date (YYYY-MM-DD).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "category": {"type": "string", "description": "Optional: Filter expenses by category."},
#                         "start_date": {"type": "string", "format": "date", "description": "Optional: Start date for filtering in YYYY-MM-DD format."},
#                         "end_date": {"type": "string", "format": "date", "description": "Optional: End date for filtering in YYYY-MM-DD format."}
#                     },
#                     "required": ["user_id"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_budget_status_tool",
#                 "description": "Retrieves the budget status for a user, showing budgeted, actual spent, and remaining amounts for a given category or all categories. Use this when the user asks about their budget status or how much they have left in a budget. Requires user_id, can optionally filter by category.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "category": {"type": "string", "description": "Optional: Filter budget status by category."}
#                     },
#                     "required": ["user_id"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_stock_price_tool",
#                 "description": "Retrieves the current stock price for a given stock ticker symbol (e.g., AAPL for Apple, GOOGL for Google, MSFT for Microsoft).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "symbol": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOGL')."}
#                     },
#                     "required": ["symbol"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_currency_exchange_rate_tool",
#                 "description": "Retrieves the current exchange rate between two currency codes (e.g., USD, EUR, LKR).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "from_currency": {"type": "string", "description": "The currency code to convert from (e.g., 'USD')."},
#                         "to_currency": {"type": "string", "description": "The currency code to convert to (e.g., 'LKR')."}
#                     },
#                     "required": ["from_currency", "to_currency"]
#                 }
#             }
#         }
#     ]

#     # Combine function tools with OpenAI's native tools (web_search_preview, file_search)
#     # IMPORTANT: Replace "your_vector_store_id" with your actual vector store ID
#     all_tools_for_openai = [
#         *function_tools_definitions,
#         {"type": "web_search_preview"}, # As per documentation
#         {"type": "file_search", "vector_store_ids": ["vs_6836df8f306881919cf54b2d7e654e4f"]} # As per documentation
#     ]

#     messages = [
#         {"role": "system", "content": f"You are a personal finance chatbot. Your current user ID is {user_id}. Always use the provided user_id when calling tools. Provide concise and helpful responses. If a tool returns an error, inform the user. If you need more information (like a user ID, or specific dates/categories), ask the user for it. For financial news or tips, use web search. For information from saved documents, use file search."},
#         {"role": "user", "content": user_message}
#     ]

#     try:
#         # First call: ask the model to generate a response or call a tool
#         # Using client.responses.create as per documentation for web_search_preview and file_search
#         response_obj = client.responses.create(
#             model="gpt-4o-mini", # Or "gpt-4o", "gpt-3.5-turbo" depending on your access and needs
#             messages=messages,
#             tools=all_tools_for_openai,
#             tool_choice="auto" # Allow the model to choose a tool or respond directly
#         )

#         # Process the outputs from the Responses API
#         final_response_content = ""
#         tool_outputs_to_send_back = []

#         for output_item in response_obj.output:
#             if output_item.type == "message" and output_item.role == "assistant":
#                 # This is the model's direct text response
#                 final_response_content = output_item.content[0].text
#                 # Handle citations if present in output_item.content[0].annotations
#                 if output_item.content[0].annotations:
#                     citations = []
#                     for annotation in output_item.content[0].annotations:
#                         if annotation.type == 'url_citation' and annotation.url:
#                             citations.append(f" [Source: {annotation.title or annotation.url}]")
#                         elif annotation.type == 'file_citation' and annotation.filename:
#                             citations.append(f" [File: {annotation.filename}]")
#                     if citations:
#                         final_response_content += "".join(citations)

#             elif output_item.type == "tool_code" and output_item.tool_code.name: # For function calls
#                 function_name = output_item.tool_code.name
#                 function_args = json.loads(output_item.tool_code.arguments)
                
#                 available_functions = {
#                     "add_expense_tool": add_expense_tool,
#                     "set_budget_tool": set_budget_tool,
#                     "get_expenses_tool": get_expenses_tool,
#                     "get_budget_status_tool": get_budget_status_tool,
#                     "get_stock_price_tool": get_stock_price_tool,
#                     "get_currency_exchange_rate_tool": get_currency_exchange_rate_tool,
#                 }
                
#                 if function_name in available_functions:
#                     function_to_call = available_functions[function_name]
#                     # Pass user_id explicitly if the tool function expects it
#                     # Note: The tool calls from Responses API are structured differently than Chat Completions.
#                     # We need to ensure function_args align with our Python function signatures.
#                     tool_output_result = function_to_call(**function_args)
                    
#                     tool_outputs_to_send_back.append({
#                         "tool_code_id": output_item.tool_code.id, # Use tool_code_id for Responses API
#                         "output": json.dumps(tool_output_result)
#                     })
#                     logger.info("Function tool %s executed. Output: %s", function_name, tool_output_result)
#                 else:
#                     tool_outputs_to_send_back.append({
#                         "tool_code_id": output_item.tool_code.id,
#                         "output": json.dumps({"status": "error", "message": f"Function tool '{function_name}' not found."})
#                     })
#                     logger.warning("Function tool %s not found in available_functions.", function_name)
            
#             elif output_item.type == "web_search_call":
#                 # The web_search_preview tool is handled by OpenAI directly.
#                 # Its results will typically be incorporated into the assistant's message.
#                 logger.info("Web search tool called by OpenAI. Status: %s", output_item.status)
#                 # If you needed to process raw search results, you'd check output_item.search_results
#                 # and potentially add them to tool_outputs_to_send_back if you were doing a multi-turn tool use.
#                 # For Responses API, the model usually integrates results into its next message.
            
#             elif output_item.type == "file_search_call":
#                 # The file_search tool is handled by OpenAI directly.
#                 logger.info("File search tool called by OpenAI. Status: %s", output_item.status)
#                 # Similar to web search, results are typically integrated into the assistant's message.

#         # If there were function tool calls that need results sent back to the model
#         if tool_outputs_to_send_back:
#             # This is the second call to the API, sending tool outputs back
#             second_response_obj = client.responses.create(
#                 model="gpt-4o-mini",
#                 messages=messages, # Original messages
#                 tool_outputs=tool_outputs_to_send_back, # Send the results of our function calls
#                 tools=all_tools_for_openai # Still provide the tools
#             )
#             # Find the final message from the second response
#             for item in second_response_obj.output:
#                 if item.type == "message" and item.role == "assistant":
#                     final_response_content = item.content[0].text
#                     if item.content[0].annotations:
#                         citations = []
#                         for annotation in item.content[0].annotations:
#                             if annotation.type == 'url_citation' and annotation.url:
#                                 citations.append(f" [Source: {annotation.title or annotation.url}]")
#                             elif annotation.type == 'file_citation' and annotation.filename:
#                                 citations.append(f" [File: {annotation.filename}]")
#                         if citations:
#                             final_response_content += "".join(citations)
#                     break # Found the final message, exit loop
        
#         return final_response_content if final_response_content else "I couldn't generate a response."

#     except Exception as e:
#         logger.exception("Error in chat_with_agent:")
#         return f"I'm sorry, I encountered an error: {str(e)}. Please try again."















































# import os
# import logging
# from openai import OpenAI
# from dotenv import load_dotenv
# from app.db import execute_query
# from app.utils import get_stock_price, get_currency_exchange_rate
# import json # Ensure this is imported

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # Initialize OpenAI client
# # Ensure OPENAI_API_KEY is set in your .env file
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Define Agent Tools (Python functions that the AI can call) ---

# def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
#     """
#     Adds a new personal expense for a user.
#     Args:
#         user_id (int): The ID of the user.
#         amount (float): The amount of the expense.
#         category (str): The category of the expense (e.g., 'Food', 'Transport', 'Utilities').
#         description (str): A brief description of the expense.
#         expense_date (str): The date of the expense in YYYY-MM-DD format.
#     Returns:
#         dict: A dictionary indicating success or failure.
#     """
#     logger.info("Agent tool: add_expense called with user_id=%s, amount=%s, category=%s, date=%s",
#                 user_id, amount, category, expense_date)
#     try:
#         query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, amount, category, description, expense_date))
#         return {"status": "success", "message": f"Expense of {amount} in {category} added for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in add_expense_tool:")
#         return {"status": "error", "message": f"Failed to add expense: {str(e)}"}

# def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
#     """
#     Sets a new budget for a user in a specific category for a given period.
#     Args:
#         user_id (int): The ID of the user.
#         category (str): The category for the budget (e.g., 'Groceries', 'Entertainment').
#         amount (float): The budgeted amount.
#         start_date (str): The start date of the budget in YYYY-MM-DD format.
#         end_date (str): The end date of the budget in YYYY-MM-DD format.
#     Returns:
#         dict: A dictionary indicating success or failure.
#     """
#     logger.info("Agent tool: set_budget called with user_id=%s, category=%s, amount=%s, start=%s, end=%s",
#                 user_id, category, amount, start_date, end_date)
#     try:
#         query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, category, amount, start_date, end_date))
#         return {"status": "success", "message": f"Budget of {amount} for {category} set for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in set_budget_tool:")
#         return {"status": "error", "message": f"Failed to set budget: {str(e)}"}

# def get_expenses_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
#     """
#     Retrieves a user's expenses, optionally filtered by category and date range.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter expenses by category.
#         start_date (str, optional): Start date for filtering in YYYY-MM-DD format.
#         end_date (str, optional): End date for filtering in YYYY-MM-DD format.
#     Returns:
#         list: A list of expense dictionaries.
#     """
#     logger.info("Agent tool: get_expenses called for user %s, category=%s, start=%s, end=%s",
#                 user_id, category, start_date, end_date)
#     try:
#         sql_query = "SELECT expense_id, user_id, amount, category, description, expense_date FROM T_SNG_Expenses WHERE user_id = ?"
#         params = [user_id]
        
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
#         if start_date:
#             sql_query += " AND expense_date >= ?"
#             params.append(start_date)
#         if end_date:
#             sql_query += " AND expense_date <= ?"
#             params.append(end_date)
        
#         expenses = execute_query(sql_query, tuple(params), fetch_type='all')
#         if expenses:
#             for exp in expenses:
#                 if 'expense_date' in exp and isinstance(exp['expense_date'], (type(None), type(exp['expense_date']))): # Check if it's a date object
#                     exp['expense_date'] = exp['expense_date'].isoformat() if exp['expense_date'] else None
#             logger.info("Fetched %d expenses for user %s.", len(expenses), user_id)
#             return {"status": "success", "data": expenses}
#         else:
#             logger.info("No expenses found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No expenses found."}
#     except Exception as e:
#         logger.exception("Error in get_expenses_tool:")
#         return {"status": "error", "message": f"Failed to retrieve expenses: {str(e)}"}

# def get_budget_status_tool(user_id: int, category: str = None):
#     """
#     Retrieves the budget status for a user, optionally by category.
#     Shows budgeted, actual spent, and remaining amounts.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter budget status by category.
#     Returns:
#         list: A list of budget status dictionaries.
#     """
#     logger.info("Agent tool: get_budget_status called for user %s, category=%s", user_id, category)
#     try:
#         sql_query = """
#         SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
#         FROM V_SNG_BudgetStatus_L1
#         WHERE user_id = ?
#         """
#         params = [user_id]
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
        
#         budgets = execute_query(sql_query, tuple(params), fetch_type='all')
#         if budgets:
#             for bgt in budgets:
#                 if 'start_date' in bgt and isinstance(bgt['start_date'], (type(None), type(bgt['start_date']))):
#                     bgt['start_date'] = bgt['start_date'].isoformat() if bgt['start_date'] else None
#                 if 'end_date' in bgt and isinstance(bgt['end_date'], (type(None), type(bgt['end_date']))):
#                     bgt['end_date'] = bgt['end_date'].isoformat() if bgt['end_date'] else None
#             logger.info("Fetched %d budgets for user %s.", len(budgets), user_id)
#             return {"status": "success", "data": budgets}
#         else:
#             logger.info("No budgets found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No budgets found."}
#     except Exception as e:
#         logger.exception("Error in get_budget_status_tool:")
#         return {"status": "error", "message": f"Failed to retrieve budget status: {str(e)}"}

# def get_stock_price_tool(symbol: str):
#     """
#     Retrieves the current stock price for a given stock ticker symbol (e.g., AAPL, GOOGL).
#     Args:
#         symbol (str): The stock ticker symbol.
#     Returns:
#         dict: A dictionary containing the stock symbol, price, and currency, or an error message.
#     """
#     logger.info("Agent tool: get_stock_price_tool called for symbol: %s", symbol)
#     return get_stock_price(symbol)

# def get_currency_exchange_rate_tool(from_currency: str, to_currency: str):
#     """
#     Retrieves the current exchange rate between two currency codes (e.g., USD, EUR, LKR).
#     Args:
#         from_currency (str): The currency code to convert from (e.g., "USD").
#         to_currency (str): The currency code to convert to (e.g., "LKR").
#     Returns:
#         dict: A dictionary containing the 'from' currency, 'to' currency, and the exchange rate, or an error message.
#     """
#     logger.info("Agent tool: get_currency_exchange_rate_tool called from %s to %s", from_currency, to_currency)
#     return get_currency_exchange_rate(from_currency, to_currency)

# # --- New Tool Wrapper Functions for OpenAI's Native Tools ---

# def web_search_tool(query: str, user_location: dict = None, search_context_size: str = "medium"):
#     """
#     Searches the web for real-time financial news or relevant tips using OpenAI's web_search_preview.
#     Args:
#         query (str): The search query for financial news or tips.
#         user_location (dict, optional): Approximate user location (e.g., {"country": "US", "city": "New York"}).
#         search_context_size (str, optional): Context size for search results ("low", "medium", "high").
#     Returns:
#         str: The text content of the web search result.
#     """
#     logger.info("Agent tool: web_search_tool called with query: %s", query)
#     try:
#         tools_config = [{"type": "web_search_preview"}]
#         if user_location:
#             tools_config[0]["user_location"] = user_location
#         if search_context_size:
#             tools_config[0]["search_context_size"] = search_context_size

#         response = client.responses.create(
#             model="gpt-4o-mini", # Use a model that supports web search
#             input=query,
#             tools=tools_config,
#             tool_choice={"type": "web_search_preview"} # Force web search
#         )
        
#         # Extract text content from the response
#         for output_item in response.output:
#             if output_item.type == "message" and output_item.role == "assistant":
#                 content = output_item.content[0].text
#                 citations = []
#                 if output_item.content[0].annotations:
#                     for annotation in output_item.content[0].annotations:
#                         if annotation.type == 'url_citation' and annotation.url:
#                             citations.append(f" [Source: {annotation.title or annotation.url}]")
#                 if citations:
#                     content += "".join(citations)
#                 return content
#         return "No relevant web search results found."

#     except Exception as e:
#         logger.exception("Error in web_search_tool:")
#         return f"Error performing web search: {str(e)}"

# def file_search_tool(query: str, vector_store_ids: list, max_num_results: int = None, filters: dict = None):
#     """
#     Searches saved financial documents using OpenAI's file_search tool.
#     Args:
#         query (str): The search query for financial documents.
#         vector_store_ids (list): A list of vector store IDs to search in.
#         max_num_results (int, optional): Maximum number of results to retrieve.
#         filters (dict, optional): Metadata filters for search results.
#     Returns:
#         str: The text content of the file search result.
#     """
#     logger.info("Agent tool: file_search_tool called with query: %s, vector_store_ids: %s", query, vector_store_ids)
#     try:
#         tools_config = [{
#             "type": "file_search",
#             "vector_store_ids": vector_store_ids
#         }]
#         if max_num_results is not None:
#             tools_config[0]["max_num_results"] = max_num_results
#         if filters:
#             tools_config[0]["filters"] = filters

#         response = client.responses.create(
#             model="gpt-4o-mini", # Use a model that supports file search
#             input=query,
#             tools=tools_config,
#             tool_choice={"type": "file_search"} # Force file search
#         )

#         # Extract text content from the response
#         for output_item in response.output:
#             if output_item.type == "message" and output_item.role == "assistant":
#                 content = output_item.content[0].text
#                 citations = []
#                 if output_item.content[0].annotations:
#                     for annotation in output_item.content[0].annotations:
#                         if annotation.type == 'file_citation' and annotation.filename:
#                             citations.append(f" [File: {annotation.filename}]")
#                 if citations:
#                     content += "".join(citations)
#                 return content
#         return "No relevant file search results found."

#     except Exception as e:
#         logger.exception("Error in file_search_tool:")
#         return f"Error performing file search: {str(e)}"

# # --- OpenAI Agent Orchestration ---

# def chat_with_agent(user_message: str, user_id: int):
#     """
#     Sends a user message to the OpenAI agent and gets a response.
#     The agent uses defined tools to answer queries.
#     Args:
#         user_message (str): The message from the user.
#         user_id (int): The ID of the current user.
#     Returns:
#         str: The agent's response.
#     """
#     logger.info("Chat with agent: User %s message: %s", user_id, user_message)

#     # Define the tools available to the agent
#     # These are the *function* tools that we implement ourselves, including wrappers for native OpenAI tools
#     all_function_tools_definitions = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "add_expense_tool",
#                 "description": "Adds a new personal expense for a user. Use this when the user wants to record an expense. Requires user_id, amount, category, description, and expense_date (YYYY-MM-DD).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "amount": {"type": "number", "description": "The amount of the expense."},
#                         "category": {"type": "string", "description": "The category of the expense (e.g., 'Food', 'Transport', 'Utilities', 'Rent', 'Shopping')."},
#                         "description": {"type": "string", "description": "A brief description of the expense."},
#                         "expense_date": {"type": "string", "format": "date", "description": "The date of the expense in YYYY-MM-DD format."}
#                     },
#                     "required": ["user_id", "amount", "category", "expense_date"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "set_budget_tool",
#                 "description": "Sets a new budget for a user in a specific category for a given period. Use this when the user wants to set or update a budget. Requires user_id, category, amount, start_date (YYYY-MM-DD), and end_date (YYYY-MM-DD).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "category": {"type": "string", "description": "The category for the budget (e.g., 'Groceries', 'Entertainment')."},
#                         "amount": {"type": "number", "description": "The budgeted amount."},
#                         "start_date": {"type": "string", "format": "date", "description": "The start date of the budget in YYYY-MM-DD format."},
#                         "end_date": {"type": "string", "format": "date", "description": "The end date of the budget in YYYY-MM-DD format."}
#                     },
#                     "required": ["user_id", "category", "amount", "start_date", "end_date"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_expenses_tool",
#                 "description": "Retrieves a user's expenses, optionally filtered by category and date range. Use this when the user asks about their spending or expense history. Can filter by user_id, category, start_date (YYYY-MM-DD), and end_date (YYYY-MM-DD).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "category": {"type": "string", "description": "Optional: Filter expenses by category."},
#                         "start_date": {"type": "string", "format": "date", "description": "Optional: Start date for filtering in YYYY-MM-DD format."},
#                         "end_date": {"type": "string", "format": "date", "description": "Optional: End date for filtering in YYYY-MM-DD format."}
#                     },
#                     "required": ["user_id"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_budget_status_tool",
#                 "description": "Retrieves the budget status for a user, showing budgeted, actual spent, and remaining amounts for a given category or all categories. Use this when the user asks about their budget status or how much they have left in a budget. Requires user_id, can optionally filter by category.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "user_id": {"type": "integer", "description": "The ID of the user."},
#                         "category": {"type": "string", "description": "Optional: Filter budget status by category."}
#                     },
#                     "required": ["user_id"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_stock_price_tool",
#                 "description": "Retrieves the current stock price for a given stock ticker symbol (e.g., AAPL for Apple, GOOGL for Google, MSFT for Microsoft).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "symbol": {"type": "string", "description": "The stock ticker symbol (e.g., 'AAPL', 'GOOGL')."}
#                     },
#                     "required": ["symbol"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_currency_exchange_rate_tool",
#                 "description": "Retrieves the current exchange rate between two currency codes (e.g., USD, EUR, LKR).",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "from_currency": {"type": "string", "description": "The currency code to convert from (e.g., 'USD')."},
#                         "to_currency": {"type": "string", "description": "The currency code to convert to (e.g., 'LKR')."}
#                     },
#                     "required": ["from_currency", "to_currency"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "web_search_tool",
#                 "description": "Searches the web for real-time financial news or relevant tips. Use this when the user asks for financial news, market updates, or general financial tips.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "query": {"type": "string", "description": "The search query for financial news or tips."},
#                         "user_location": {"type": "object", "description": "Optional: Approximate user location for localized search results (e.g., {\"country\": \"US\", \"city\": \"New York\"})."},
#                         "search_context_size": {"type": "string", "enum": ["low", "medium", "high"], "description": "Optional: Context size for search results ('low', 'medium', 'high'). Defaults to 'medium'."}
#                     },
#                     "required": ["query"]
#                 }
#             }
#         },
#         {
#             "type": "function",
#             "function": {
#                 "name": "file_search_tool",
#                 "description": "Searches saved financial documents (e.g., past budgets, expense reports) for relevant information. Use this when the user asks about historical financial data, summaries from past reports, or details from uploaded documents.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "query": {"type": "string", "description": "The search query for financial documents."},
#                         "vector_store_ids": {"type": "array", "items": {"type": "string"}, "description": "A list of vector store IDs to search in. REQUIRED."},
#                         "max_num_results": {"type": "integer", "description": "Optional: Maximum number of results to retrieve."},
#                         "filters": {"type": "object", "description": "Optional: Metadata filters for search results."}
#                     },
#                     "required": ["query", "vector_store_ids"] # vector_store_ids is required for this tool
#                 }
#             }
#         }
#     ]

#     # Map function names to their actual Python callable objects
#     available_functions = {
#         "add_expense_tool": add_expense_tool,
#         "set_budget_tool": set_budget_tool,
#         "get_expenses_tool": get_expenses_tool,
#         "get_budget_status_tool": get_budget_status_tool,
#         "get_stock_price_tool": get_stock_price_tool,
#         "get_currency_exchange_rate_tool": get_currency_exchange_rate_tool,
#         "web_search_tool": web_search_tool, # Our wrapper function
#         "file_search_tool": file_search_tool # Our wrapper function
#     }

#     # Initial message to the agent
#     messages = [
#         {"role": "system", "content": f"You are a personal finance chatbot. Your current user ID is {user_id}. Always use the provided user_id when calling tools. Provide concise and helpful responses. If a tool returns an error, inform the user. If you need more information (like a user ID, or specific dates/categories), ask the user for it. For financial news or tips, use web search. For information from saved documents, use file search."},
#         {"role": "user", "content": user_message}
#     ]

#     try:
#         # First call: ask the model to generate a response or call a tool
#         # Using client.chat.completions.create for robust function calling
#         response = client.chat.completions.create(
#             model="gpt-4o-mini", # Or "gpt-4o", "gpt-3.5-turbo" depending on your access and needs
#             messages=messages,
#             tools=all_function_tools_definitions, # Pass all our function tools
#             tool_choice="auto" # Allow the model to choose a tool or respond directly
#         )

#         response_message = response.choices[0].message
#         tool_calls = response_message.tool_calls

#         # Step 2: Check if the model wanted to call a tool
#         if tool_calls:
#             # Add the tool call to the messages history
#             messages.append(response_message)

#             # Execute each tool call
#             for tool_call in tool_calls:
#                 function_name = tool_call.function.name
#                 function_args = json.loads(tool_call.function.arguments)
                
#                 if function_name in available_functions:
#                     function_to_call = available_functions[function_name]
                    
#                     # Ensure user_id is passed if the function expects it, but not for web/file search tools
#                     # We'll rely on the tool's signature to correctly accept arguments.
#                     tool_output = function_to_call(**function_args)
                    
#                     messages.append(
#                         {
#                             "tool_call_id": tool_call.id,
#                             "role": "tool",
#                             "name": function_name,
#                             "content": json.dumps(tool_output)
#                         }
#                     )
#                 else:
#                     tool_output = {"status": "error", "message": f"Function tool '{function_name}' not found."}
#                     messages.append(
#                         {
#                             "tool_call_id": tool_call.id,
#                             "role": "tool",
#                             "name": function_name,
#                             "content": json.dumps(tool_output)
#                         }
#                     )
#                 logger.info("Tool %s executed. Output: %s", function_name, tool_output)

#             # Second call: send the conversation and tool output back to the model
#             # and ask it to generate a final response.
#             second_response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=messages # Send the updated messages list
#             )
#             return second_response.choices[0].message.content
#         else:
#             # If no tool call, return the model's direct response
#             return response_message.content

#     except Exception as e:
#         logger.exception("Error in chat_with_agent:")
#         return f"I'm sorry, I encountered an error: {str(e)}. Please try again."





























































# import os
# import logging
# from openai import OpenAI
# from dotenv import load_dotenv
# from app.db import execute_query
# from app.utils import get_stock_price, get_currency_exchange_rate
# import json 

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # Initialize OpenAI client
# # Ensure OPENAI_API_KEY is set in your .env file
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- Define Agent Tools (Python functions - these are NOT directly callable by AI in this setup) ---
# # These functions are here for completeness and could be called by other parts of your backend
# # (e.g., directly by Flask API endpoints from the frontend forms), but not directly by the AI via tool-calling.

# def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
#     """
#     Adds a new personal expense for a user.
#     Args:
#         user_id (int): The ID of the user.
#         amount (float): The amount of the expense.
#         category (str): The category of the expense (e.g., 'Food', 'Transport', 'Utilities').
#         description (str): A brief description of the expense.
#         expense_date (str): The date of the expense inYYYY-MM-DD format.
#     Returns:
#         dict: A dictionary indicating success or failure.
#     """
#     logger.info("Agent tool: add_expense called with user_id=%s, amount=%s, category=%s, date=%s",
#                 user_id, amount, category, expense_date)
#     try:
#         query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, amount, category, description, expense_date))
#         return {"status": "success", "message": f"Expense of {amount} in {category} added for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in add_expense_tool:")
#         return {"status": "error", "message": f"Failed to add expense: {str(e)}"}

# def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
#     """
#     Sets a new budget for a user in a specific category for a given period.
#     Args:
#         user_id (int): The ID of the user.
#         category (str): The category for the budget (e.g., 'Groceries', 'Entertainment').
#         amount (float): The budgeted amount.
#         start_date (str): The start date of the budget inYYYY-MM-DD format.
#         end_date (str): The end date of the budget inYYYY-MM-DD format.
#     Returns:
#         dict: A dictionary indicating success or failure.
#     """
#     logger.info("Agent tool: set_budget called with user_id=%s, category=%s, amount=%s, start=%s, end=%s",
#                 user_id, category, amount, start_date, end_date)
#     try:
#         query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, category, amount, start_date, end_date))
#         return {"status": "success", "message": f"Budget of {amount} for {category} set for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in set_budget_tool:")
#         return {"status": "error", "message": f"Failed to set budget: {str(e)}"}

# def get_expenses_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
#     """
#     Retrieves a user's expenses, optionally filtered by category and date range.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter expenses by category.
#         start_date (str, optional): Start date for filtering inYYYY-MM-DD format.
#         end_date (str, optional): End date for filtering inYYYY-MM-DD format.
#     Returns:
#         list: A list of expense dictionaries.
#     """
#     logger.info("Agent tool: get_expenses called for user %s, category=%s, start=%s, end=%s",
#                 user_id, category, start_date, end_date)
#     try:
#         sql_query = "SELECT expense_id, user_id, amount, category, description, expense_date FROM T_SNG_Expenses WHERE user_id = ?"
#         params = [user_id]
        
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
#         if start_date:
#             sql_query += " AND expense_date >= ?"
#             params.append(start_date)
#         if end_date:
#             sql_query += " AND expense_date <= ?"
#             params.append(end_date)
        
#         expenses = execute_query(sql_query, tuple(params), fetch_type='all')
#         if expenses:
#             for exp in expenses:
#                 if 'expense_date' in exp and isinstance(exp['expense_date'], (type(None), type(exp['expense_date']))): # Check if it's a date object
#                     exp['expense_date'] = exp['expense_date'].isoformat() if exp['expense_date'] else None
#             logger.info("Fetched %d expenses for user %s.", len(expenses), user_id)
#             return {"status": "success", "data": expenses}
#         else:
#             logger.info("No expenses found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No expenses found."}
#     except Exception as e:
#         logger.exception("Error in get_expenses_tool:")
#         return {"status": "error", "message": f"Failed to retrieve expenses: {str(e)}"}

# def get_budget_status_tool(user_id: int, category: str = None):
#     """
#     Retrieves the budget status for a user, optionally by category.
#     Shows budgeted, actual spent, and remaining amounts.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter budget status by category.
#     Returns:
#         list: A list of budget status dictionaries.
#     """
#     logger.info("Agent tool: get_budget_status called for user %s, category=%s", user_id, category)
#     try:
#         sql_query = """
#         SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
#         FROM V_SNG_BudgetStatus_L1
#         WHERE user_id = ?
#         """
#         params = [user_id]
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
        
#         budgets = execute_query(sql_query, tuple(params), fetch_type='all')
#         if budgets:
#             for bgt in budgets:
#                 if 'start_date' in bgt and isinstance(bgt['start_date'], (type(None), type(bgt['start_date']))):
#                     bgt['start_date'] = bgt['start_date'].isoformat() if bgt['start_date'] else None
#                 if 'end_date' in bgt and isinstance(bgt['end_date'], (type(None), type(bgt['end_date']))):
#                     bgt['end_date'] = bgt['end_date'].isoformat() if bgt['end_date'] else None
#             logger.info("Fetched %d budgets for user %s.", len(budgets), user_id)
#             return {"status": "success", "data": budgets}
#         else:
#             logger.info("No budgets found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No budgets found."}
#     except Exception as e:
#         logger.exception("Error in get_budget_status_tool:")
#         return {"status": "error", "message": f"Failed to retrieve budget status: {str(e)}"}

# def get_stock_price_tool(symbol: str):
#     """
#     Retrieves the current stock price for a given stock ticker symbol (e.g., AAPL, GOOGL).
#     Args:
#         symbol (str): The stock ticker symbol.
#     Returns:
#         dict: A dictionary containing the stock symbol, price, and currency, or an error message.
#     """
#     logger.info("Agent tool: get_stock_price_tool called for symbol: %s", symbol)
#     return get_stock_price(symbol)

# def get_currency_exchange_rate_tool(from_currency: str, to_currency: str):
#     """
#     Retrieves the current exchange rate between two currency codes (e.g., USD, EUR, LKR).
#     Args:
#         from_currency (str): The currency code to convert from (e.g., "USD").
#         to_currency (str): The currency code to convert to (e.g., "LKR").
#     Returns:
#         dict: A dictionary containing the 'from' currency, 'to' currency, and the exchange rate, or an error message.
#     """
#     logger.info("Agent tool: get_currency_exchange_rate_tool called from %s to %s", from_currency, to_currency)
#     return get_currency_exchange_rate(from_currency, to_currency)

# # --- OpenAI Agent Orchestration ---

# def chat_with_agent(user_message: str, user_id: int):
#     """
#     Sends a user message to the OpenAI agent and gets a response.
#     The agent uses defined tools to answer queries.
#     Args:
#         user_message (str): The message from the user.
#         user_id (int): The ID of the current user.
#     Returns:
#         str: The agent's response.
#     """
#     logger.info("Chat with agent: User %s message: %s", user_id, user_message)

#     # Define the tools available to the Responses API call
#     # IMPORTANT: Only native OpenAI tools (web_search_preview, file_search, code_interpreter)
#     # can be directly passed to client.responses.create in this manner.
#     # Custom function tools are NOT supported here.
#     all_tools_for_openai = [
#         {"type": "web_search_preview"}, # As per documentation
#         {"type": "file_search", "vector_store_ids": ["vs_6836df8f306881919cf54b2d7e654e4f"]} # As per documentation
#     ]

#     # The 'messages' list is used for the model's internal context and conversation flow.
#     # The 'input' parameter is the specific user query for the current turn.
#     # For client.responses.create, the conversation history is implicitly handled by the model
#     # based on the 'input' and the tools.
#     # We will use the user_message as the primary input.

#     try:
#         # Call the Responses API
#         response_obj = client.responses.create(
#             model="gpt-4o-mini", # Use a model that supports these tools
#             input=user_message, # The explicit input for the current turn
#             tools=all_tools_for_openai,
#             tool_choice="auto" # Allow the model to choose a tool or respond directly
#         )

#         # Process the outputs from the Responses API
#         final_response_content = ""
        
#         # Iterate through the output items to find the assistant's message
#         for output_item in response_obj.output:
#             if output_item.type == "message" and output_item.role == "assistant":
#                 # This is the model's direct text response
#                 final_response_content = output_item.content[0].text
#                 # Handle citations if present in output_item.content[0].annotations
#                 if output_item.content[0].annotations:
#                     citations = []
#                     for annotation in output_item.content[0].annotations:
#                         if annotation.type == 'url_citation' and annotation.url:
#                             citations.append(f" [Source: {annotation.title or annotation.url}]")
#                         elif annotation.type == 'file_citation' and annotation.filename:
#                             citations.append(f" [File: {annotation.filename}]")
#                     if citations:
#                         final_response_content += "".join(citations)
#                 break # Found the final message, exit loop
            
#             # Log tool calls made by OpenAI's native tools (for debugging)
#             elif output_item.type == "web_search_call":
#                 logger.info("Web search tool called by OpenAI. Status: %s", output_item.status)
#             elif output_item.type == "file_search_call":
#                 logger.info("File search tool called by OpenAI. Status: %s", output_item.status)
#             # Note: client.responses.create does not return 'tool_code' for custom functions.
#             # If the model attempts to call a custom function, it won't be executed here.

#         return final_response_content if final_response_content else "I couldn't generate a response."

#     except Exception as e:
#         logger.exception("Error in chat_with_agent:")
#         # Provide a more informative error for the user
#         return f"I'm sorry, I encountered an error: {str(e)}. This might be due to an issue with the AI's tool usage or API configuration. Please try again."










# import os
# import logging
# from openai import OpenAI
# from dotenv import load_dotenv
# from app.db import execute_query
# from app.utils import get_stock_price, get_currency_exchange_rate
# import json
# import re # Import regex module
# from jsonschema import validate, ValidationError # For validating AI's JSON output

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # Initialize OpenAI client
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- System Prompt Definition (CRITICAL for AI behavior) ---
# # This prompt instructs the AI on how to format its output when it wants to call a custom function.
# # It MUST be very precise.
# SYSTEM_PROMPT = """
# You are a personal finance chatbot. Your current user ID is {user_id}.
# Your primary goal is to help users manage their finances.

# When the user asks to perform a specific action, you MUST respond with a JSON object.
# The JSON object must contain an "action" key and other keys for its arguments.
# Here are the actions and their required JSON formats:

# 1.  To add an expense:
#     {{"action": "add_expense", "amount": <float>, "category": "<string>", "description": "<string>", "expense_date": "<YYYY-MM-DD>"}}
#     Example: {{"action": "add_expense", "amount": 25.50, "category": "Food", "description": "Lunch", "expense_date": "2025-05-30"}}

# 2.  To set a budget:
#     {{"action": "set_budget", "category": "<string>", "amount": <float>, "start_date": "<YYYY-MM-DD>", "end_date": "<YYYY-MM-DD>"}}
#     Example: {{"action": "set_budget", "category": "Groceries", "amount": 300.00, "start_date": "2025-06-01", "end_date": "2025-06-30"}}

# 3.  To get stock price:
#     {{"action": "get_stock_price", "symbol": "<string>"}}
#     Example: {{"action": "get_stock_price", "symbol": "AAPL"}}

# 4.  To get currency exchange rate:
#     {{"action": "get_currency_exchange_rate", "from_currency": "<string>", "to_currency": "<string>"}}
#     Example: {{"action": "get_currency_exchange_rate", "from_currency": "EUR", "to_currency": "USD"}}

# 5.  For financial news or general tips (web search):
#     Respond with the original user query as plain text. The system will then perform a web search based on that text.

# 6.  For information from saved documents (file search):
#     Respond with the original user query as plain text. The system will then perform a file search based on that text.

# If the user's request does not clearly map to one of these actions, or if you need more information, ask clarifying questions in plain text.
# Always use the provided user_id ({user_id}) when performing actions.
# """

# # --- JSON Schemas for AI Output Validation (for parsing AI's generated JSON) ---
# ADD_EXPENSE_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "add_expense"},
#         "amount": {"type": "number"},
#         "category": {"type": "string"},
#         "description": {"type": "string"},
#         "expense_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
#     },
#     "required": ["action", "amount", "category", "expense_date"],
#     "additionalProperties": False # Ensure no extra properties are added
# }

# SET_BUDGET_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "set_budget"},
#         "category": {"type": "string"},
#         "amount": {"type": "number"},
#         "start_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
#         "end_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
#     },
#     "required": ["action", "category", "amount", "start_date", "end_date"],
#     "additionalProperties": False
# }

# GET_STOCK_PRICE_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "get_stock_price"},
#         "symbol": {"type": "string"}
#     },
#     "required": ["action", "symbol"],
#     "additionalProperties": False
# }

# GET_CURRENCY_RATE_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "get_currency_exchange_rate"},
#         "from_currency": {"type": "string"},
#         "to_currency": {"type": "string"}
#     },
#     "required": ["action", "from_currency", "to_currency"],
#     "additionalProperties": False
# }

# # --- Custom Function Implementations (these are called by our Python code, not AI directly) ---

# def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
#     logger.info("Custom tool: add_expense called with user_id=%s, amount=%s, category=%s, date=%s",
#                 user_id, amount, category, expense_date)
#     try:
#         query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, amount, category, description, expense_date))
#         return {"status": "success", "message": f"Expense of {amount} in {category} added for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in add_expense_tool:")
#         return {"status": "error", "message": f"Failed to add expense: {str(e)}"}

# def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
#     logger.info("Custom tool: set_budget called with user_id=%s, category=%s, amount=%s, start=%s, end=%s",
#                 user_id, category, amount, start_date, end_date)
#     try:
#         query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, category, amount, start_date, end_date))
#         return {"status": "success", "message": f"Budget of {amount} for {category} set for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in set_budget_tool:")
#         return {"status": "error", "message": f"Failed to set budget: {str(e)}"}

# def get_expenses_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
#     logger.info("Custom tool: get_expenses called for user %s, category=%s, start=%s, end=%s",
#                 user_id, category, start_date, end_date)
#     try:
#         sql_query = "SELECT expense_id, user_id, amount, category, description, expense_date FROM T_SNG_Expenses WHERE user_id = ?"
#         params = [user_id]
        
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
#         if start_date:
#             sql_query += " AND expense_date >= ?"
#             params.append(start_date)
#         if end_date:
#             sql_query += " AND expense_date <= ?"
#             params.append(end_date)
        
#         expenses = execute_query(sql_query, tuple(params), fetch_type='all')
#         if expenses:
#             for exp in expenses:
#                 if 'expense_date' in exp and isinstance(exp['expense_date'], (type(None), type(exp['expense_date']))):
#                     exp['expense_date'] = exp['expense_date'].isoformat() if exp['expense_date'] else None
#             logger.info("Fetched %d expenses for user %s.", len(expenses), user_id)
#             return {"status": "success", "data": expenses}
#         else:
#             logger.info("No expenses found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No expenses found."}
#     except Exception as e:
#         logger.exception("Error in get_expenses_tool:")
#         return {"status": "error", "message": f"Failed to retrieve expenses: {str(e)}"}

# def get_budget_status_tool(user_id: int, category: str = None):
#     logger.info("Custom tool: get_budget_status called for user %s, category=%s", user_id, category)
#     try:
#         sql_query = """
#         SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
#         FROM V_SNG_BudgetStatus_L1
#         WHERE user_id = ?
#         """
#         params = [user_id]
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
        
#         budgets = execute_query(sql_query, tuple(params), fetch_type='all')
#         if budgets:
#             for bgt in budgets:
#                 if 'start_date' in bgt and isinstance(bgt['start_date'], (type(None), type(bgt['start_date']))):
#                     bgt['start_date'] = bgt['start_date'].isoformat() if bgt['start_date'] else None
#                 if 'end_date' in bgt and isinstance(bgt['end_date'], (type(None), type(bgt['end_date']))):
#                     bgt['end_date'] = bgt['end_date'].isoformat() if bgt['end_date'] else None
#             logger.info("Fetched %d budgets for user %s.", len(budgets), user_id)
#             return {"status": "success", "data": budgets}
#         else:
#             logger.info("No budgets found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No budgets found."}
#     except Exception as e:
#         logger.exception("Error in get_budget_status_tool:")
#         return {"status": "error", "message": f"Failed to retrieve budget status: {str(e)}"}

# def get_stock_price_from_util(symbol: str): # Renamed to avoid conflict with tool name
#     """
#     Retrieves the current stock price for a given symbol.
#     This is a MOCK function, called by our parsing logic.
#     """
#     logger.info("Custom tool: get_stock_price_from_util called for symbol: %s", symbol)
#     return get_stock_price(symbol)

# def get_currency_exchange_rate_from_util(from_currency: str, to_currency: str): # Renamed
#     """
#     Retrieves the current exchange rate between two currencies.
#     This is a MOCK function, called by our parsing logic.
#     """
#     logger.info("Custom tool: get_currency_exchange_rate_from_util called from %s to %s", from_currency, to_currency)
#     return get_currency_exchange_rate(from_currency, to_currency)

# # --- OpenAI Agent Orchestration ---

# def chat_with_agent(user_message: str, user_id: int):
#     """
#     Sends a user message to the OpenAI agent and gets a response.
#     The agent is instructed to output JSON for custom actions,
#     or plain text for web/file search.
#     Args:
#         user_message (str): The message from the user.
#         user_id (int): The ID of the current user.
#     Returns:
#         str: The agent's response.
#     """
#     logger.info("Chat with agent: User %s message: %s", user_id, user_message)

#     # The full system prompt with instructions for AI-generated JSON
#     full_system_prompt = SYSTEM_PROMPT.format(user_id=user_id)

#     # Define the tools available to the Responses API call
#     # IMPORTANT: Only native OpenAI tools (web_search_preview, file_search, code_interpreter)
#     # can be directly passed to client.responses.create in this manner.
#     # Our custom functions are NOT listed here.
#     all_native_openai_tools = [
#         {"type": "web_search_preview"}, # As per documentation
#         {"type": "file_search", "vector_store_ids": ["vs_6836df8f306881919cf54b2d7e654e4f"]} # As per documentation
#     ]

#     try:
#         # First call to Responses API: AI processes the user message and system prompt.
#         # It will either generate plain text or the instructed JSON.
#         response_obj = client.responses.create(
#             model="gpt-4o-mini", # Use a model that supports these tools
#             input=f"{full_system_prompt}\nUser: {user_message}", # Combine prompt and user message
#             tools=all_native_openai_tools, # Only native tools here
#             tool_choice="auto" # Allow the model to choose native tools or respond directly
#         )

#         final_response_content = "I couldn't generate a response." # Default error message

#         # Process the outputs from the Responses API
#         for output_item in response_obj.output:
#             if output_item.type == "message" and output_item.role == "assistant":
#                 ai_generated_text = output_item.content[0].text
#                 logger.info("AI generated raw text: %s", ai_generated_text)

#                 # --- Attempt to parse AI's text output as a custom function call (the workaround) ---
#                 try:
#                     # Use regex to find a potential JSON object in the AI's response
#                     json_match = re.search(r'\{.*?\}', ai_generated_text, re.DOTALL)
#                     if json_match:
#                         potential_json = json_match.group(0)
#                         ai_action = json.loads(potential_json)
#                         logger.info("Attempted to parse AI output as JSON action: %s", ai_action)

#                         # Map parsed action to our internal Python functions
#                         # and validate against schema
#                         if ai_action.get("action") == "add_expense":
#                             validate(instance=ai_action, schema=ADD_EXPENSE_SCHEMA)
#                             result = add_expense_tool(user_id=user_id, **{k: v for k, v in ai_action.items() if k != 'action'})
#                             final_response_content = f"Expense added successfully! {result.get('message', '')}"
#                             if result.get('status') == 'error':
#                                 final_response_content = f"Error adding expense: {result.get('message', 'Unknown error')}"

#                         elif ai_action.get("action") == "set_budget":
#                             validate(instance=ai_action, schema=SET_BUDGET_SCHEMA)
#                             result = set_budget_tool(user_id=user_id, **{k: v for k, v in ai_action.items() if k != 'action'})
#                             final_response_content = f"Budget set successfully! {result.get('message', '')}"
#                             if result.get('status') == 'error':
#                                 final_response_content = f"Error setting budget: {result.get('message', 'Unknown error')}"

#                         elif ai_action.get("action") == "get_stock_price":
#                             validate(instance=ai_action, schema=GET_STOCK_PRICE_SCHEMA)
#                             result = get_stock_price_from_util(**{k: v for k, v in ai_action.items() if k != 'action'})
#                             if result.get('error'):
#                                 final_response_content = f"Could not get stock price: {result['error']}"
#                             else:
#                                 final_response_content = f"The current price of {result['symbol']} is {result['price']} {result['currency']}."

#                         elif ai_action.get("action") == "get_currency_exchange_rate":
#                             validate(instance=ai_action, schema=GET_CURRENCY_RATE_SCHEMA)
#                             result = get_currency_exchange_rate_from_util(**{k: v for k, v in ai_action.items() if k != 'action'})
#                             if result.get('error'):
#                                 final_response_content = f"Could not get exchange rate: {result['error']}"
#                             else:
#                                 final_response_content = f"The exchange rate from {result['from']} to {result['to']} is {result['rate']}."
#                         else:
#                             # If it's JSON but not a recognized action, treat as plain text
#                             final_response_content = ai_generated_text
#                     else:
#                         # No JSON found, treat as plain text
#                         final_response_content = ai_generated_text

#                 except (json.JSONDecodeError, ValidationError) as parse_error:
#                     logger.warning("AI did not output valid JSON for action or schema mismatch: %s | Error: %s", ai_generated_text, parse_error)
#                     final_response_content = f"I received an unexpected format from the AI. Please try rephrasing your request for custom actions. Original AI response: {ai_generated_text}"
#                 except Exception as e:
#                     logger.exception("Error during custom action execution after AI parse:")
#                     final_response_content = f"An internal error occurred while processing your request: {str(e)}. Please try again."

#                 # Handle citations from native tools if present in output_item.content[0].annotations
#                 if output_item.content[0].annotations:
#                     citations = []
#                     for annotation in output_item.content[0].annotations:
#                         if annotation.type == 'url_citation' and annotation.url:
#                             citations.append(f" [Source: {annotation.title or annotation.url}]")
#                         elif annotation.type == 'file_citation' and annotation.filename:
#                             citations.append(f" [File: {annotation.filename}]")
#                     if citations:
#                         final_response_content += "".join(citations)
                
#                 break # Processed the main message, exit loop

#             # Log native tool calls made by OpenAI (for debugging)
#             elif output_item.type == "web_search_call":
#                 logger.info("Web search tool called by OpenAI. Status: %s", output_item.status)
#             elif output_item.type == "file_search_call":
#                 logger.info("File search tool called by OpenAI. Status: %s", output_item.status)
        
#         return final_response_content

#     except Exception as e:
#         logger.exception("Error in chat_with_agent (top level):")
#         return f"I'm sorry, I encountered a critical error: {str(e)}. Please try again."























# import os
# import logging
# from openai import OpenAI
# from dotenv import load_dotenv
# from app.db import execute_query
# from app.utils import get_stock_price_from_api, get_currency_exchange_rate_from_api # Corrected imports
# import json
# import re
# from jsonschema import validate, ValidationError

# # Load environment variables
# load_dotenv()

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # Initialize OpenAI client
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # --- System Prompt Definition (CRITICAL for AI behavior) ---
# # This prompt instructs the AI on how to format its output when it wants to call a custom function.
# # It MUST be very precise.
# SYSTEM_PROMPT = """
# You are a personal finance chatbot. Your current user ID is {user_id}.
# Your primary goal is to help users manage their finances.

# When the user asks to perform a specific action, you MUST respond with a JSON object.
# The JSON object must contain an "action" key and other keys for its arguments.
# Here are the actions and their required JSON formats:

# 1.  To add an expense:
#     {{"action": "add_expense", "amount": <float>, "category": "<string>", "description": "<string>", "expense_date": "<YYYY-MM-DD>"}}
#     Example: {{"action": "add_expense", "amount": 25.50, "category": "Food", "description": "Lunch", "expense_date": "2025-05-30"}}

# 2.  To set a budget:
#     {{"action": "set_budget", "category": "<string>", "amount": <float>, "start_date": "<YYYY-MM-DD>", "end_date": "<YYYY-MM-DD>"}}
#     Example: {{"action": "set_budget", "category": "Groceries", "amount": 300.00, "start_date": "2025-06-01", "end_date": "2025-06-30"}}

# 3.  To get stock price:
#     {{"action": "get_stock_price", "symbol": "<string>"}}
#     Example: {{"action": "get_stock_price", "symbol": "AAPL"}}

# 4.  To get currency exchange rate:
#     {{"action": "get_currency_exchange_rate", "from_currency": "<string>", "to_currency": "<string>"}}
#     Example: {{"action": "get_currency_exchange_rate", "from_currency": "EUR", "to_currency": "USD"}}

# 5.  For financial news or general tips (web search):
#     Respond with the original user query as plain text. The system will then perform a web search based on that text.

# 6.  For information from saved documents (file search):
#     Respond with the original user query as plain text. The system will then perform a file search based on that text.

# If the user's request does not clearly map to one of these actions, or if you need more information, ask clarifying questions in plain text.
# Always use the provided user_id ({user_id}) when performing actions.
# """

# # --- JSON Schemas for AI Output Validation (for parsing AI's generated JSON) ---
# ADD_EXPENSE_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "add_expense"},
#         "amount": {"type": "number"},
#         "category": {"type": "string"},
#         "description": {"type": "string"},
#         "expense_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
#     },
#     "required": ["action", "amount", "category", "expense_date"],
#     "additionalProperties": False
# }

# SET_BUDGET_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "set_budget"},
#         "category": {"type": "string"},
#         "amount": {"type": "number"},
#         "start_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
#         "end_date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
#     },
#     "required": ["action", "category", "amount", "start_date", "end_date"],
#     "additionalProperties": False
# }

# GET_STOCK_PRICE_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "get_stock_price"},
#         "symbol": {"type": "string"}
#     },
#     "required": ["action", "symbol"],
#     "additionalProperties": False
# }

# GET_CURRENCY_RATE_SCHEMA = {
#     "type": "object",
#     "properties": {
#         "action": {"type": "string", "const": "get_currency_exchange_rate"},
#         "from_currency": {"type": "string"},
#         "to_currency": {"type": "string"}
#     },
#     "required": ["action", "from_currency", "to_currency"],
#     "additionalProperties": False
# }

# # --- Custom Function Implementations (these are called by our Python code, not AI directly) ---

# def add_expense_tool(user_id: int, amount: float, category: str, description: str, expense_date: str):
#     logger.info("Custom tool: add_expense called with user_id=%s, amount=%s, category=%s, date=%s",
#                 user_id, amount, category, expense_date)
#     try:
#         query = "INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, amount, category, description, expense_date))
#         return {"status": "success", "message": f"Expense of {amount} in {category} added for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in add_expense_tool:")
#         return {"status": "error", "message": f"Failed to add expense: {str(e)}"}

# def set_budget_tool(user_id: int, category: str, amount: float, start_date: str, end_date: str):
#     logger.info("Custom tool: set_budget called with user_id=%s, category=%s, amount=%s, start=%s, end=%s",
#                 user_id, category, amount, start_date, end_date)
#     try:
#         query = "INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)"
#         execute_query(query, (user_id, category, amount, start_date, end_date))
#         return {"status": "success", "message": f"Budget of {amount} for {category} set for user {user_id}."}
#     except Exception as e:
#         logger.exception("Error in set_budget_tool:")
#         return {"status": "error", "message": f"Failed to set budget: {str(e)}"}

# def get_expenses_tool(user_id: int, category: str = None, start_date: str = None, end_date: str = None):
#     logger.info("Custom tool: get_expenses called for user %s, category=%s, start=%s, end=%s",
#                 user_id, category, start_date, end_date)
#     try:
#         sql_query = "SELECT expense_id, user_id, amount, category, description, expense_date FROM T_SNG_Expenses WHERE user_id = ?"
#         params = [user_id]
        
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
#         if start_date:
#             sql_query += " AND expense_date >= ?"
#             params.append(start_date)
#         if end_date:
#             sql_query += " AND expense_date <= ?"
#             params.append(end_date)
        
#         expenses = execute_query(sql_query, tuple(params), fetch_type='all')
#         if expenses:
#             for exp in expenses:
#                 if 'expense_date' in exp and isinstance(exp['expense_date'], (type(None), type(exp['expense_date']))):
#                     exp['expense_date'] = exp['expense_date'].isoformat() if exp['expense_date'] else None
#             logger.info("Fetched %d expenses for user %s.", len(expenses), user_id)
#             return {"status": "success", "data": expenses}
#         else:
#             logger.info("No expenses found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No expenses found."}
#     except Exception as e:
#         logger.exception("Error in get_expenses_tool:")
#         return {"status": "error", "message": f"Failed to retrieve expenses: {str(e)}"}

# def get_budget_status_tool(user_id: int, category: str = None):
#     """
#     Retrieves the budget status for a user, optionally by category.
#     Shows budgeted, actual spent, and remaining amounts.
#     Args:
#         user_id (int): The ID of the user.
#         category (str, optional): Filter budget status by category.
#     Returns:
#         list: A list of budget status dictionaries.
#     """
#     logger.info("Custom tool: get_budget_status called for user %s, category=%s", user_id, category)
#     try:
#         sql_query = """
#         SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
#         FROM V_SNG_BudgetStatus_L1
#         WHERE user_id = ?
#         """
#         params = [user_id]
#         if category:
#             sql_query += " AND category = ?"
#             params.append(category)
        
#         budgets = execute_query(sql_query, tuple(params), fetch_type='all')
#         if budgets:
#             for bgt in budgets:
#                 if 'start_date' in bgt and isinstance(bgt['start_date'], (type(None), type(bgt['start_date']))):
#                     bgt['start_date'] = bgt['start_date'].isoformat() if bgt['start_date'] else None
#                 if 'end_date' in bgt and isinstance(bgt['end_date'], (type(None), type(bgt['end_date']))):
#                     bgt['end_date'] = bgt['end_date'].isoformat() if bgt['end_date'] else None
#             logger.info("Fetched %d budgets for user %s.", len(budgets), user_id)
#             return {"status": "success", "data": budgets}
#         else:
#             logger.info("No budgets found for user %s with given filters.", user_id)
#             return {"status": "success", "data": [], "message": "No budgets found."}
#     except Exception as e:
#         logger.exception("Error in get_budget_status_tool:")
#         return {"status": "error", "message": f"Failed to retrieve budget status: {str(e)}"}

# def get_stock_price_tool(symbol: str): # This function will be called by our parsing logic
#     """
#     Retrieves the current stock price for a given symbol.
#     """
#     logger.info("Custom tool: get_stock_price_tool (wrapper) called for symbol: %s", symbol)
#     return get_stock_price_from_api(symbol) # Call the actual API function

# def get_currency_exchange_rate_tool(from_currency: str, to_currency: str): # This function will be called by our parsing logic
#     """
#     Retrieves the current exchange rate between two currencies.
#     """
#     logger.info("Custom tool: get_currency_exchange_rate_tool (wrapper) called from %s to %s", from_currency, to_currency)
#     return get_currency_exchange_rate_from_api(from_currency, to_currency) # Call the actual API function

# # --- OpenAI Agent Orchestration ---

# def chat_with_agent(user_message: str, user_id: int):
#     """
#     Sends a user message to the OpenAI agent and gets a response.
#     The agent is instructed to output JSON for custom actions,
#     or plain text for web/file search.
#     Args:
#         user_message (str): The message from the user.
#         user_id (int): The ID of the current user.
#     Returns:
#         str: The agent's response.
#     """
#     logger.info("Chat with agent: User %s message: %s", user_id, user_message)

#     # The full system prompt with instructions for AI-generated JSON
#     full_system_prompt = SYSTEM_PROMPT.format(user_id=user_id)

#     # Define the tools available to the Responses API call
#     # IMPORTANT: Only native OpenAI tools (web_search_preview, file_search, code_interpreter)
#     # can be directly passed to client.responses.create in this manner.
#     # Our custom functions are NOT listed here.
#     all_native_openai_tools = [
#         {"type": "web_search_preview"}, # As per documentation
#         {"type": "file_search", "vector_store_ids": ["vs_6836df8f306881919cf54b2d7e654e4f"]} # As per documentation
#     ]

#     try:
#         # Step 1: Call the Responses API. The AI processes the user message and system prompt.
#         # It will either generate plain text or the instructed JSON for custom actions,
#         # or it will trigger native web/file search.
#         response_obj = client.responses.create(
#             model="gpt-4o-mini", # Use a model that supports these tools
#             input=f"{full_system_prompt}\nUser: {user_message}", # Combine prompt and user message
#             tools=all_native_openai_tools, # Only native tools here
#             tool_choice="auto" # Allow the model to choose native tools or respond directly
#         )

#         final_response_content = "I couldn't generate a response." # Default error message

#         # Step 2: Process the outputs from the Responses API
#         for output_item in response_obj.output:
#             if output_item.type == "message" and output_item.role == "assistant":
#                 ai_generated_text = output_item.content[0].text
#                 logger.info("AI generated raw text: %s", ai_generated_text)

#                 # --- Attempt to parse AI's text output as a custom function call (the workaround) ---
#                 try:
#                     # Use regex to find a potential JSON object in the AI's response
#                     # This regex tries to find the first JSON-like string starting with { and ending with }
#                     json_match = re.search(r'\{[^{}]*?\}', ai_generated_text, re.DOTALL)
                    
#                     if json_match:
#                         potential_json = json_match.group(0)
#                         ai_action = json.loads(potential_json)
#                         logger.info("Attempted to parse AI output as JSON action: %s", ai_action)

#                         # Map parsed action to our internal Python functions and validate against schema
#                         action_type = ai_action.get("action")
                        
#                         if action_type == "add_expense":
#                             validate(instance=ai_action, schema=ADD_EXPENSE_SCHEMA)
#                             # Pass only relevant args, excluding 'action'
#                             result = add_expense_tool(user_id=user_id, **{k: v for k, v in ai_action.items() if k != 'action'})
#                             if result.get('status') == 'success':
#                                 final_response_content = f"Expense added successfully! {result.get('message', '')}"
#                             else:
#                                 final_response_content = f"Error adding expense: {result.get('message', 'Unknown error')}"

#                         elif action_type == "set_budget":
#                             validate(instance=ai_action, schema=SET_BUDGET_SCHEMA)
#                             result = set_budget_tool(user_id=user_id, **{k: v for k, v in ai_action.items() if k != 'action'})
#                             if result.get('status') == 'success':
#                                 final_response_content = f"Budget set successfully! {result.get('message', '')}"
#                             else:
#                                 final_response_content = f"Error setting budget: {result.get('message', 'Unknown error')}"

#                         elif action_type == "get_stock_price":
#                             validate(instance=ai_action, schema=GET_STOCK_PRICE_SCHEMA)
#                             result = get_stock_price_tool(**{k: v for k, v in ai_action.items() if k != 'action'})
#                             if result.get('error'):
#                                 final_response_content = f"Could not get stock price: {result['error']}"
#                             else:
#                                 final_response_content = f"The current price of {result['symbol']} is {result['price']} {result['currency']}."

#                         elif action_type == "get_currency_exchange_rate":
#                             validate(instance=ai_action, schema=GET_CURRENCY_RATE_SCHEMA)
#                             result = get_currency_exchange_rate_tool(**{k: v for k, v in ai_action.items() if k != 'action'})
#                             if result.get('error'):
#                                 final_response_content = f"Could not get exchange rate: {result['error']}"
#                             else:
#                                 final_response_content = f"The exchange rate from {result['from']} to {result['to']} is {result['rate']}."
#                         else:
#                             # If it's JSON but not a recognized action, treat as plain text
#                             final_response_content = ai_generated_text
#                     else:
#                         # No JSON found, treat as plain text
#                         final_response_content = ai_generated_text

#                 except (json.JSONDecodeError, ValidationError) as parse_error:
#                     logger.warning("AI did not output valid JSON for action or schema mismatch. Raw AI response: '%s' | Error: %s", ai_generated_text, parse_error)
#                     final_response_content = f"I received an unexpected format from the AI. Please try rephrasing your request for custom actions. Original AI response: '{ai_generated_text}'"
#                 except Exception as e:
#                     logger.exception("Error during custom action execution after AI parse:")
#                     final_response_content = f"An internal error occurred while processing your request: {str(e)}. Please try again."

#                 # Handle citations from native tools if present in output_item.content[0].annotations
#                 if output_item.content[0].annotations:
#                     citations = []
#                     for annotation in output_item.content[0].annotations:
#                         if annotation.type == 'url_citation' and annotation.url:
#                             citations.append(f" [Source: {annotation.title or annotation.url}]")
#                         elif annotation.type == 'file_citation' and annotation.filename:
#                             citations.append(f" [File: {annotation.filename}]")
#                     if citations:
#                         final_response_content += "".join(citations)
                
#                 break # Processed the main message, exit loop

#             # Log native tool calls made by OpenAI (for debugging)
#             elif output_item.type == "web_search_call":
#                 logger.info("Web search tool called by OpenAI. Status: %s", output_item.status)
#             elif output_item.type == "file_search_call":
#                 logger.info("File search tool called by OpenAI. Status: %s", output_item.status)
        
#         return final_response_content

#     except Exception as e:
#         logger.exception("Error in chat_with_agent (top level):")
#         return f"I'm sorry, I encountered a critical error: {str(e)}. Please try again."



























































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
Your primary goal is to help users manage their finances.

When the user asks to perform a specific action that requires a backend tool, you MUST respond with a JSON object.
The JSON object must contain an "action" key and other keys for its arguments.
Here are the actions and their required JSON formats:

1.  To add an expense:
    {{"action": "add_expense", "amount": <float>, "category": "<string>", "description": "<string>", "expense_date": "<YYYY-MM-DD>"}}
    Example: {{"action": "add_expense", "amount": 25.50, "category": "Food", "description": "Lunch", "expense_date": "2025-05-30"}}

2.  To set a budget:
    {{"action": "set_budget", "category": "<string>", "amount": <float>, "start_date": "<YYYY-MM-DD>", "end_date": "<YYYY-MM-DD>"}}
    Example: {{"action": "set_budget", "category": "Groceries", "amount": 300.00, "start_date": "2025-06-01", "end_date": "2025-06-30"}}

3.  To get stock price:
    {{"action": "get_stock_price", "symbol": "<string>"}}
    Example: {{"action": "get_stock_price", "symbol": "AAPL"}}

4.  To get currency exchange rate:
    {{"action": "get_currency_exchange_rate", "from_currency": "<string>", "to_currency": "<string>"}}
    Example: {{"action": "get_currency_exchange_rate", "from_currency": "EUR", "to_currency": "USD"}}

For **real-time financial news, current economic situations, market updates, or general financial tips that require up-to-date information from the internet**, you MUST respond with **ONLY the web search query as plain text**. Do NOT include any other text or questions. The system will automatically perform the web search based on this text.
Example: "latest economic situation in Sri Lanka"

For **information from saved financial documents, past reports, or historical data that you have access to locally**, you MUST respond with **ONLY the file search query as plain text**. Do NOT include any other text or questions. The system will automatically perform the file search based on this text.
Example: "summarize my Q1 financial report"

If the user's request does not clearly map to one of these actions (JSON output) or search types (plain text query for web/file search), or if you need more information, ask clarifying questions in plain text.
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





