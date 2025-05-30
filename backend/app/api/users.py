from flask import Blueprint, request, jsonify
from app.db import execute_query
import logging # Import the logging module

# Configure logging for this blueprint
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for user-related routes
users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['POST'])
def create_user():
    """
    API endpoint to create a new user.
    Expects JSON data: {"username": "...", "email": "...", "password_hash": "..."}
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password_hash = data.get('password_hash') # In a real app, hash this on the backend!

    if not all([username, email, password_hash]):
        logger.error("Missing user data for create_user: %s", data)
        return jsonify({"error": "Missing user data"}), 400

    try:
        query = "INSERT INTO T_SNG_Users (username, email, password_hash) VALUES (?, ?, ?)"
        execute_query(query, (username, email, password_hash))
        logger.info("User created successfully: %s", username)
        return jsonify({"message": "User created successfully", "username": username}), 201
    except Exception as e:
        # Check for unique constraint violation (username already exists)
        if "UNIQUE KEY constraint" in str(e): # Specific to SQL Server error messages
            logger.warning("Attempt to create duplicate username: %s", username)
            return jsonify({"error": "Username already exists"}), 409
        logger.exception("Error creating user %s:", username) # Log the full traceback
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    API endpoint to retrieve all users.
    (Note: For testing/development. In production, consider authentication/authorization
    and pagination for security and performance.)
    """
    try:
        query = "SELECT user_id, username, email FROM T_SNG_Users"
        users = execute_query(query, fetch_type='all')
        logger.info("Fetched %d users.", len(users))
        return jsonify(users), 200
    except Exception as e:
        logger.exception("Error fetching all users:") # Log the full traceback
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    API endpoint to retrieve a single user by ID.
    """
    try:
        logger.info("Attempting to fetch user with ID: %s", user_id)
        query = "SELECT user_id, username, email FROM T_SNG_Users WHERE user_id = ?"
        user = execute_query(query, (user_id,), fetch_type='one')
        if user:
            logger.info("Successfully fetched user: %s", user['username'])
            return jsonify(user), 200
        else:
            logger.warning("User with ID %s not found.", user_id)
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        logger.exception("Error fetching user by ID %s:", user_id) # Log the full traceback
        return jsonify({"error": str(e)}), 500

