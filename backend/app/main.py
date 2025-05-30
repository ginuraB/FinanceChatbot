from flask import Flask, jsonify
from flask_cors import CORS
from app.api.users import users_bp
from app.api.expenses import expenses_bp
from app.api.budgets import budgets_bp
from app.api.chat import chat_bp # Import the new chat blueprint

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for all routes, allowing frontend to make requests
CORS(app)

# Register Blueprints for different API routes
app.register_blueprint(users_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(budgets_bp)
app.register_blueprint(chat_bp) # Register the new chat blueprint

@app.route('/')
def home():
    """
    A simple home route to confirm the backend is running.
    """
    return jsonify({"message": "Welcome to the Finance Chatbot Backend!"})

if __name__ == '__main__':
    # Run the Flask development server
    # In production, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)
