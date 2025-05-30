from flask import Blueprint, request, jsonify
from app.db import execute_query
import datetime

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['POST'])
def add_expense():
    """
    API endpoint to add a new expense.
    Expects JSON data: {"user_id": ..., "amount": ..., "category": "...", "description": "...", "expense_date": "YYYY-MM-DD"}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    category = data.get('category')
    description = data.get('description')
    expense_date_str = data.get('expense_date')

    if not all([user_id, amount, category, expense_date_str]):
        return jsonify({"error": "Missing expense data (user_id, amount, category, expense_date are required)"}), 400

    try:
        # Convert date string to datetime.date object
        expense_date = datetime.datetime.strptime(expense_date_str, '%Y-%m-%d').date()

        query = """
        INSERT INTO T_SNG_Expenses (user_id, amount, category, description, expense_date)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (user_id, amount, category, description, expense_date))
        return jsonify({"message": "Expense added successfully", "user_id": user_id, "amount": amount}), 201
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@expenses_bp.route('/expenses', methods=['GET'])
def get_expenses():
    """
    API endpoint to retrieve expenses.
    Can filter by user_id (query parameter: /expenses?user_id=1).
    """
    user_id = request.args.get('user_id', type=int)

    try:
        if user_id:
            # Using the view for user-specific expenses
            query = "SELECT expense_id, user_id, amount, category, description, expense_date, expense_month FROM V_SNG_UserExpenses_L1 WHERE user_id = ?"
            expenses = execute_query(query, (user_id,), fetch_type='all')
        else:
            # Get all expenses (for testing, be cautious in production)
            query = "SELECT expense_id, user_id, amount, category, description, expense_date, expense_month FROM V_SNG_UserExpenses_L1"
            expenses = execute_query(query, fetch_type='all')

        # Convert date objects to string for JSON serialization
        for expense in expenses:
            if 'expense_date' in expense and isinstance(expense['expense_date'], datetime.date):
                expense['expense_date'] = expense['expense_date'].isoformat() # YYYY-MM-DD format

        return jsonify(expenses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

