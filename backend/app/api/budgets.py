from flask import Blueprint, request, jsonify
from app.db import execute_query
import datetime

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets', methods=['POST'])
def create_budget():
    """
    API endpoint to create a new budget.
    Expects JSON data: {"user_id": ..., "category": "...", "amount": ..., "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    category = data.get('category')
    amount = data.get('amount')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not all([user_id, category, amount, start_date_str, end_date_str]):
        return jsonify({"error": "Missing budget data (user_id, category, amount, start_date, end_date are required)"}), 400

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

        query = """
        INSERT INTO T_SNG_Budgets (user_id, category, amount, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (user_id, category, amount, start_date, end_date))
        return jsonify({"message": "Budget created successfully", "user_id": user_id, "category": category}), 201
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budgets_bp.route('/budgets', methods=['GET'])
def get_budgets():
    """
    API endpoint to retrieve budgets.
    Can filter by user_id (query parameter: /budgets?user_id=1).
    """
    user_id = request.args.get('user_id', type=int)

    try:
        if user_id:
            # Using the view for budget status
            query = """
            SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
            FROM V_SNG_BudgetStatus_L1
            WHERE user_id = ?
            """
            budgets = execute_query(query, (user_id,), fetch_type='all')
        else:
            # Get all budgets (for testing, be cautious in production)
            query = """
            SELECT user_id, category, budgeted_amount, actual_spent, remaining_amount, start_date, end_date
            FROM V_SNG_BudgetStatus_L1
            """
            budgets = execute_query(query, fetch_type='all')

        # Convert date objects to string for JSON serialization
        for budget in budgets:
            if 'start_date' in budget and isinstance(budget['start_date'], datetime.date):
                budget['start_date'] = budget['start_date'].isoformat()
            if 'end_date' in budget and isinstance(budget['end_date'], datetime.date):
                budget['end_date'] = budget['end_date'].isoformat()

        return jsonify(budgets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

