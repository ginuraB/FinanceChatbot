# import pytest
# from app.main import app
# from app.db import execute_query # Import execute_query for cleanup
# import json # For working with JSON data in requests

# # Fixture to create a test client for the Flask app
# @pytest.fixture
# def client():
#     """
#     Configures the Flask app for testing and provides a test client.
#     """
#     app.config['TESTING'] = True # Enable testing mode
#     with app.test_client() as client:
#         yield client # Yields the client to the test function
#     # Clean up any test data after the test runs
#     # This is a simple cleanup, for complex scenarios, consider a dedicated test database
#     execute_query("DELETE FROM T_SNG_Users WHERE username LIKE 'test_user_%'")
#     execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username LIKE 'test_user_%')")
#     execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username LIKE 'test_user_%')")


# # Helper function to create a test user
# def create_test_user(client, username="test_user_api", email="api@example.com", password="password"):
#     """
#     Helper to create a user via API for testing other endpoints.
#     Returns the user_id if successful.
#     """
#     user_data = {
#         "username": username,
#         "email": email,
#         "password_hash": password
#     }
#     response = client.post('/users', json=user_data)
#     assert response.status_code == 201
#     # Fetch the user_id after creation
#     user = execute_query("SELECT user_id FROM T_SNG_Users WHERE username = ?", (username,), fetch_type='one')
#     return user.user_id if user else None

# # Test the home route
# def test_home_route(client):
#     """
#     Tests the basic home route to ensure the app is running.
#     """
#     response = client.get('/')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {"message": "Welcome to the Finance Chatbot Backend!"}

# # --- User API Tests ---
# def test_create_user(client):
#     """
#     Tests creating a new user via the API.
#     """
#     user_data = {
#         "username": "test_user_create",
#         "email": "create@example.com",
#         "password_hash": "securepass"
#     }
#     response = client.post('/users', json=user_data)
#     assert response.status_code == 201
#     assert "User created successfully" in json.loads(response.data)['message']

#     # Verify in DB
#     user = execute_query("SELECT username FROM T_SNG_Users WHERE username = ?", ("test_user_create",), fetch_type='one')
#     assert user is not None
#     assert user.username == "test_user_create"

# def test_create_user_missing_data(client):
#     """
#     Tests creating a user with missing required data.
#     """
#     response = client.post('/users', json={"username": "incomplete"})
#     assert response.status_code == 400
#     assert "Missing user data" in json.loads(response.data)['error']

# def test_create_user_duplicate_username(client):
#     """
#     Tests creating a user with a username that already exists.
#     """
#     # Create user first
#     create_test_user(client, username="duplicate_user")

#     # Try creating again with same username
#     user_data = {
#         "username": "duplicate_user",
#         "email": "duplicate@example.com",
#         "password_hash": "pass"
#     }
#     response = client.post('/users', json=user_data)
#     assert response.status_code == 409 # Conflict
#     assert "Username already exists" in json.loads(response.data)['error']

# def test_get_all_users(client):
#     """
#     Tests retrieving all users.
#     """
#     # Ensure at least one user exists
#     create_test_user(client, username="test_get_all_users_1")
#     create_test_user(client, username="test_get_all_users_2")

#     response = client.get('/users')
#     assert response.status_code == 200
#     users = json.loads(response.data)
#     assert isinstance(users, list)
#     assert len(users) >= 2 # Should contain at least the two test users

#     # Check if the test users are in the list
#     usernames = [u['username'] for u in users]
#     assert "test_get_all_users_1" in usernames
#     assert "test_get_all_users_2" in usernames

# def test_get_user_by_id(client):
#     """
#     Tests retrieving a single user by their ID.
#     """
#     user_id = create_test_user(client, username="test_user_by_id")
#     assert user_id is not None

#     response = client.get(f'/users/{user_id}')
#     assert response.status_code == 200
#     user_data = json.loads(response.data)
#     assert user_data['username'] == "test_user_by_id"
#     assert user_data['user_id'] == user_id

# def test_get_user_by_id_not_found(client):
#     """
#     Tests retrieving a user with a non-existent ID.
#     """
#     response = client.get('/users/99999999') # Assuming this ID doesn't exist
#     assert response.status_code == 404
#     assert "User not found" in json.loads(response.data)['message']


# # --- Expense API Tests ---
# def test_add_expense(client):
#     """
#     Tests adding a new expense.
#     """
#     user_id = create_test_user(client)
#     assert user_id is not None

#     expense_data = {
#         "user_id": user_id,
#         "amount": 50.75,
#         "category": "Food",
#         "description": "Lunch with colleagues",
#         "expense_date": "2025-05-29"
#     }
#     response = client.post('/expenses', json=expense_data)
#     assert response.status_code == 201
#     assert "Expense added successfully" in json.loads(response.data)['message']

#     # Verify in DB (using the view)
#     expenses = execute_query(f"SELECT amount, category FROM V_SNG_UserExpenses_L1 WHERE user_id = ? AND category = 'Food'", (user_id,), fetch_type='all')
#     assert any(e['amount'] == 50.75 for e in expenses)

# def test_add_expense_missing_data(client):
#     """
#     Tests adding an expense with missing data.
#     """
#     user_id = create_test_user(client)
#     response = client.post('/expenses', json={"user_id": user_id, "amount": 10.0}) # Missing category, date
#     assert response.status_code == 400
#     assert "Missing expense data" in json.loads(response.data)['error']

# def test_add_expense_invalid_date(client):
#     """
#     Tests adding an expense with an invalid date format.
#     """
#     user_id = create_test_user(client)
#     expense_data = {
#         "user_id": user_id,
#         "amount": 25.0,
#         "category": "Transport",
#         "description": "Bus fare",
#         "expense_date": "29-05-2025" # Invalid format
#     }
#     response = client.post('/expenses', json=expense_data)
#     assert response.status_code == 400
#     assert "Invalid date format" in json.loads(response.data)['error']

# def test_get_expenses_by_user(client):
#     """
#     Tests retrieving expenses for a specific user.
#     """
#     user_id_1 = create_test_user(client, username="user_for_expenses_1")
#     user_id_2 = create_test_user(client, username="user_for_expenses_2")

#     # Add expenses for user 1
#     client.post('/expenses', json={"user_id": user_id_1, "amount": 100, "category": "Rent", "description": "Monthly rent", "expense_date": "2025-05-01"})
#     client.post('/expenses', json={"user_id": user_id_1, "amount": 20, "category": "Coffee", "description": "Morning coffee", "expense_date": "2025-05-02"})
#     # Add expense for user 2
#     client.post('/expenses', json={"user_id": user_id_2, "amount": 50, "category": "Books", "description": "New book", "expense_date": "2025-05-03"})

#     response = client.get(f'/expenses?user_id={user_id_1}')
#     assert response.status_code == 200
#     expenses = json.loads(response.data)
#     assert isinstance(expenses, list)
#     assert len(expenses) >= 2 # Should get at least the two expenses for user_id_1
#     for expense in expenses:
#         assert expense['user_id'] == user_id_1
#         assert 'expense_date' in expense # Check if date is converted to string

# # --- Budget API Tests ---
# def test_create_budget(client):
#     """
#     Tests creating a new budget.
#     """
#     user_id = create_test_user(client, username="user_for_budget")
#     assert user_id is not None

#     budget_data = {
#         "user_id": user_id,
#         "category": "Groceries",
#         "amount": 300.00,
#         "start_date": "2025-06-01",
#         "end_date": "2025-06-30"
#     }
#     response = client.post('/budgets', json=budget_data)
#     assert response.status_code == 201
#     assert "Budget created successfully" in json.loads(response.data)['message']

#     # Verify in DB (using the view)
#     budgets = execute_query(f"SELECT budgeted_amount, category FROM V_SNG_BudgetStatus_L1 WHERE user_id = ? AND category = 'Groceries'", (user_id,), fetch_type='all')
#     assert any(b['budgeted_amount'] == 300.00 for b in budgets)

# def test_create_budget_missing_data(client):
#     """
#     Tests creating a budget with missing data.
#     """
#     user_id = create_test_user(client)
#     response = client.post('/budgets', json={"user_id": user_id, "category": "Travel"}) # Missing amount, dates
#     assert response.status_code == 400
#     assert "Missing budget data" in json.loads(response.data)['error']

# def test_create_budget_invalid_date(client):
#     """
#     Tests creating a budget with an invalid date format.
#     """
#     user_id = create_test_user(client)
#     budget_data = {
#         "user_id": user_id,
#         "category": "Utilities",
#         "amount": 150.00,
#         "start_date": "01/07/2025", # Invalid format
#         "end_date": "31/07/2025"
#     }
#     response = client.post('/budgets', json=budget_data)
#     assert response.status_code == 400
#     assert "Invalid date format" in json.loads(response.data)['error']

# def test_get_budgets_by_user(client):
#     """
#     Tests retrieving budgets for a specific user, including budget status.
#     """
#     user_id = create_test_user(client, username="user_for_budgets_test")

#     # Add a budget
#     client.post('/budgets', json={"user_id": user_id, "category": "Food", "amount": 200, "start_date": "2025-05-01", "end_date": "2025-05-31"})
#     # Add an expense within that budget period
#     client.post('/expenses', json={"user_id": user_id, "amount": 50, "category": "Food", "description": "Dinner", "expense_date": "2025-05-15"})

#     response = client.get(f'/budgets?user_id={user_id}')
#     assert response.status_code == 200
#     budgets = json.loads(response.data)
#     assert isinstance(budgets, list)
#     assert len(budgets) >= 1

#     food_budget = next((b for b in budgets if b['category'] == 'Food'), None)
#     assert food_budget is not None
#     assert food_budget['budgeted_amount'] == 200.00
#     assert food_budget['actual_spent'] == 50.00 # Should reflect the expense
#     assert food_budget['remaining_amount'] == 150.00
#     assert 'start_date' in food_budget # Check if dates are converted to string
#     assert 'end_date' in food_budget

























# import pytest
# from app.main import app
# from app.db import execute_query # Import execute_query for cleanup
# import json # For working with JSON data in requests

# # Fixture to create a test client for the Flask app
# @pytest.fixture
# def client():
#     """
#     Configures the Flask app for testing and provides a test client.
#     """
#     app.config['TESTING'] = True # Enable testing mode
#     with app.test_client() as client:
#         yield client # Yields the client to the test function
#     # Clean up any test data after the test runs
#     # This is a simple cleanup, for complex scenarios, consider a dedicated test database
#     # CRITICAL: Delete expenses and budgets FIRST, then users, due to foreign key constraints
#     execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username LIKE 'test_user_%')")
#     execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username LIKE 'test_user_%')")
#     execute_query("DELETE FROM T_SNG_Users WHERE username LIKE 'test_user_%'")


# # Helper function to create a test user
# def create_test_user(client, username="test_user_api", email="api@example.com", password="password"):
#     """
#     Helper to create a user via API for testing other endpoints.
#     Returns the user_id if successful.
#     """
#     user_data = {
#         "username": username,
#         "email": email,
#         "password_hash": password
#     }
#     response = client.post('/users', json=user_data)
#     # If the user already exists (e.g., from a previous failed run), we'll get a 409.
#     # For tests, we can tolerate this and proceed, or clean up more aggressively before each test.
#     # For now, let's just assert success, and rely on the fixture's cleanup.
#     assert response.status_code in [201, 409], f"Expected 201 or 409, got {response.status_code}: {response.data}"

#     # Fetch the user_id after creation (or if it already existed)
#     user = execute_query("SELECT user_id FROM T_SNG_Users WHERE username = ?", (username,), fetch_type='one')
#     return user['user_id'] if user else None # Access as dictionary now


# # Test the home route
# def test_home_route(client):
#     """
#     Tests the basic home route to ensure the app is running.
#     """
#     response = client.get('/')
#     assert response.status_code == 200
#     assert json.loads(response.data) == {"message": "Welcome to the Finance Chatbot Backend!"}

# # --- User API Tests ---
# def test_create_user(client):
#     """
#     Tests creating a new user via the API.
#     """
#     user_data = {
#         "username": "test_user_create",
#         "email": "create@example.com",
#         "password_hash": "securepass"
#     }
#     response = client.post('/users', json=user_data)
#     assert response.status_code == 201
#     assert "User created successfully" in json.loads(response.data)['message']

#     # Verify in DB
#     user = execute_query("SELECT username FROM T_SNG_Users WHERE username = ?", ("test_user_create",), fetch_type='one')
#     assert user is not None
#     assert user['username'] == "test_user_create" # Access as dictionary now

# def test_create_user_missing_data(client):
#     """
#     Tests creating a user with missing required data.
#     """
#     response = client.post('/users', json={"username": "incomplete"})
#     assert response.status_code == 400
#     assert "Missing user data" in json.loads(response.data)['error']

# def test_create_user_duplicate_username(client):
#     """
#     Tests creating a user with a username that already exists.
#     """
#     # Create user first
#     create_test_user(client, username="duplicate_user")

#     # Try creating again with same username
#     user_data = {
#         "username": "duplicate_user",
#         "email": "duplicate@example.com",
#         "password_hash": "pass"
#     }
#     response = client.post('/users', json=user_data)
#     assert response.status_code == 409 # Conflict
#     assert "Username already exists" in json.loads(response.data)['error']

# def test_get_all_users(client):
#     """
#     Tests retrieving all users.
#     """
#     # Ensure at least one user exists
#     create_test_user(client, username="test_get_all_users_1")
#     create_test_user(client, username="test_get_all_users_2")

#     response = client.get('/users')
#     assert response.status_code == 200
#     users = json.loads(response.data)
#     assert isinstance(users, list)
#     assert len(users) >= 2 # Should contain at least the two test users

#     # Check if the test users are in the list
#     usernames = [u['username'] for u in users]
#     assert "test_get_all_users_1" in usernames
#     assert "test_get_all_users_2" in usernames

# def test_get_user_by_id(client):
#     """
#     Tests retrieving a single user by their ID.
#     """
#     user_id = create_test_user(client, username="test_user_by_id")
#     assert user_id is not None

#     response = client.get(f'/users/{user_id}')
#     assert response.status_code == 200
#     user_data = json.loads(response.data)
#     assert user_data['username'] == "test_user_by_id"
#     assert user_data['user_id'] == user_id

# def test_get_user_by_id_not_found(client):
#     """
#     Tests retrieving a user with a non-existent ID.
#     """
#     response = client.get('/users/99999999') # Assuming this ID doesn't exist
#     assert response.status_code == 404
#     assert "User not found" in json.loads(response.data)['message']


# # --- Expense API Tests ---
# def test_add_expense(client):
#     """
#     Tests adding a new expense.
#     """
#     user_id = create_test_user(client, username="test_user_for_expense_add") # Ensure unique user for this test
#     assert user_id is not None

#     expense_data = {
#         "user_id": user_id,
#         "amount": 50.75,
#         "category": "Food",
#         "description": "Lunch with colleagues",
#         "expense_date": "2025-05-29"
#     }
#     response = client.post('/expenses', json=expense_data)
#     assert response.status_code == 201
#     assert "Expense added successfully" in json.loads(response.data)['message']

#     # Verify in DB (using the view)
#     expenses = execute_query(f"SELECT amount, category FROM V_SNG_UserExpenses_L1 WHERE user_id = ? AND category = 'Food'", (user_id,), fetch_type='all')
#     assert any(float(e['amount']) == 50.75 for e in expenses) # Convert to float for comparison

# def test_add_expense_missing_data(client):
#     """
#     Tests adding an expense with missing data.
#     """
#     user_id = create_test_user(client, username="test_user_expense_missing")
#     response = client.post('/expenses', json={"user_id": user_id, "amount": 10.0}) # Missing category, date
#     assert response.status_code == 400
#     assert "Missing expense data" in json.loads(response.data)['error']

# def test_add_expense_invalid_date(client):
#     """
#     Tests adding an expense with an invalid date format.
#     """
#     user_id = create_test_user(client, username="test_user_expense_invalid_date")
#     expense_data = {
#         "user_id": user_id,
#         "amount": 25.0,
#         "category": "Transport",
#         "description": "Bus fare",
#         "expense_date": "29-05-2025" # Invalid format
#     }
#     response = client.post('/expenses', json=expense_data)
#     assert response.status_code == 400
#     assert "Invalid date format" in json.loads(response.data)['error']

# def test_get_expenses_by_user(client):
#     """
#     Tests retrieving expenses for a specific user.
#     """
#     user_id_1 = create_test_user(client, username="user_for_expenses_1")
#     user_id_2 = create_test_user(client, username="user_for_expenses_2")

#     # Add expenses for user 1
#     client.post('/expenses', json={"user_id": user_id_1, "amount": 100, "category": "Rent", "description": "Monthly rent", "expense_date": "2025-05-01"})
#     client.post('/expenses', json={"user_id": user_id_1, "amount": 20, "category": "Coffee", "description": "Morning coffee", "expense_date": "2025-05-02"})
#     # Add expense for user 2
#     client.post('/expenses', json={"user_id": user_id_2, "amount": 50, "category": "Books", "description": "New book", "expense_date": "2025-05-03"})

#     response = client.get(f'/expenses?user_id={user_id_1}')
#     assert response.status_code == 200
#     expenses = json.loads(response.data)
#     assert isinstance(expenses, list)
#     assert len(expenses) >= 2 # Should get at least the two expenses for user_id_1
#     for expense in expenses:
#         assert expense['user_id'] == user_id_1
#         assert 'expense_date' in expense # Check if date is converted to string

# # --- Budget API Tests ---
# def test_create_budget(client):
#     """
#     Tests creating a new budget.
#     """
#     user_id = create_test_user(client, username="user_for_budget_create") # Ensure unique user for this test
#     assert user_id is not None

#     budget_data = {
#         "user_id": user_id,
#         "category": "Groceries",
#         "amount": 300.00,
#         "start_date": "2025-06-01",
#         "end_date": "2025-06-30"
#     }
#     response = client.post('/budgets', json=budget_data)
#     assert response.status_code == 201
#     assert "Budget created successfully" in json.loads(response.data)['message']

#     # Verify in DB (using the view)
#     budgets = execute_query(f"SELECT budgeted_amount, category FROM V_SNG_BudgetStatus_L1 WHERE user_id = ? AND category = 'Groceries'", (user_id,), fetch_type='all')
#     assert any(float(b['budgeted_amount']) == 300.00 for b in budgets) # Convert to float for comparison

# def test_create_budget_missing_data(client):
#     """
#     Tests creating a budget with missing data.
#     """
#     user_id = create_test_user(client, username="user_for_budget_missing")
#     response = client.post('/budgets', json={"user_id": user_id, "category": "Travel"}) # Missing amount, dates
#     assert response.status_code == 400
#     assert "Missing budget data" in json.loads(response.data)['error']

# def test_create_budget_invalid_date(client):
#     """
#     Tests creating a budget with an invalid date format.
#     """
#     user_id = create_test_user(client, username="user_for_budget_invalid_date")
#     budget_data = {
#         "user_id": user_id,
#         "category": "Utilities",
#         "amount": 150.00,
#         "start_date": "01/07/2025", # Invalid format
#         "end_date": "31/07/2025"
#     }
#     response = client.post('/budgets', json=budget_data)
#     assert response.status_code == 400
#     assert "Invalid date format" in json.loads(response.data)['error']

# def test_get_budgets_by_user(client):
#     """
#     Tests retrieving budgets for a specific user, including budget status.
#     """
#     user_id = create_test_user(client, username="user_for_budgets_test")

#     # Add a budget
#     client.post('/budgets', json={"user_id": user_id, "category": "Food", "amount": 200, "start_date": "2025-05-01", "end_date": "2025-05-31"})
#     # Add an expense within that budget period
#     client.post('/expenses', json={"user_id": user_id, "amount": 50, "category": "Food", "description": "Dinner", "expense_date": "2025-05-15"})

#     response = client.get(f'/budgets?user_id={user_id}')
#     assert response.status_code == 200
#     budgets = json.loads(response.data)
#     assert isinstance(budgets, list)
#     assert len(budgets) >= 1

#     food_budget = next((b for b in budgets if b['category'] == 'Food'), None)
#     assert food_budget is not None
#     assert float(food_budget['budgeted_amount']) == 200.00 # Convert to float for comparison
#     assert float(food_budget['actual_spent']) == 50.00 # Should reflect the expense
#     assert float(food_budget['remaining_amount']) == 150.00
#     assert 'start_date' in food_budget # Check if dates are converted to string
#     assert 'end_date' in food_budget




















import pytest
from app.main import app
from app.db import execute_query # Import execute_query for cleanup
import json # For working with JSON data in requests

# Fixture to create a test client for the Flask app
@pytest.fixture
def client():
    """
    Configures the Flask app for testing and provides a test client.
    """
    app.config['TESTING'] = True # Enable testing mode
    with app.test_client() as client:
        yield client # Yields the client to the test function
    # Clean up any test data after the test runs
    # CRITICAL: Delete expenses and budgets FIRST, then users, due to foreign key constraints
    execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username LIKE 'test_user_%' OR username LIKE 'user_for_%')")
    execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username LIKE 'test_user_%' OR username LIKE 'user_for_%')")
    execute_query("DELETE FROM T_SNG_Users WHERE username LIKE 'test_user_%' OR username LIKE 'user_for_%'")


# Helper function to create a test user
def create_test_user(client, username="test_user_api", email="api@example.com", password="password"):
    """
    Helper to create a user via API for testing other endpoints.
    Returns the user_id if successful.
    """
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password
    }
    response = client.post('/users', json=user_data)
    # If the user already exists (e.g., from a previous failed run), we'll get a 409.
    # For tests, we can tolerate this and proceed, or clean up more aggressively before each test.
    # For now, let's just assert success, and rely on the fixture's cleanup.
    assert response.status_code in [201, 409], f"Expected 201 or 409, got {response.status_code}: {response.data}"

    # Fetch the user_id after creation (or if it already existed)
    user = execute_query("SELECT user_id FROM T_SNG_Users WHERE username = ?", (username,), fetch_type='one')
    if user:
        return user['user_id']
    else:
        # If the user wasn't found after creation, something went wrong. Raise an exception.
        raise Exception(f"Failed to retrieve user_id after creating/finding user: {username}")



# Test the home route
def test_home_route(client):
    """
    Tests the basic home route to ensure the app is running.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Welcome to the Finance Chatbot Backend!"}

# --- User API Tests ---
def test_create_user(client):
    """
    Tests creating a new user via the API.
    """
    user_data = {
        "username": "test_user_create",
        "email": "create@example.com",
        "password_hash": "securepass"
    }
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    assert "User created successfully" in json.loads(response.data)['message']

    # Verify in DB
    user = execute_query("SELECT username FROM T_SNG_Users WHERE username = ?", ("test_user_create",), fetch_type='one')
    assert user is not None
    assert user['username'] == "test_user_create" # Access as dictionary now

def test_create_user_missing_data(client):
    """
    Tests creating a user with missing required data.
    """
    # Ensure unique username for this test to avoid conflicts with other tests
    user_id = create_test_user(client, username="test_user_missing_data") 
    response = client.post('/users', json={"username": "incomplete"})
    assert response.status_code == 400
    assert "Missing user data" in json.loads(response.data)['error']

def test_create_user_duplicate_username(client):
    """
    Tests creating a user with a username that already exists.
    """
    # Create user first
    create_test_user(client, username="duplicate_user")

    # Try creating again with same username
    user_data = {
        "username": "duplicate_user",
        "email": "duplicate@example.com",
        "password_hash": "pass"
    }
    response = client.post('/users', json=user_data)
    assert response.status_code == 409 # Conflict
    assert "Username already exists" in json.loads(response.data)['error']

def test_get_all_users(client):
    """
    Tests retrieving all users.
    """
    # Ensure at least one user exists
    create_test_user(client, username="test_get_all_users_1")
    create_test_user(client, username="test_get_all_users_2")

    response = client.get('/users')
    assert response.status_code == 200
    users = json.loads(response.data)
    assert isinstance(users, list)
    assert len(users) >= 2 # Should contain at least the two test users

    # Check if the test users are in the list
    usernames = [u['username'] for u in users]
    assert "test_get_all_users_1" in usernames
    assert "test_get_all_users_2" in usernames

def test_get_user_by_id(client):
    """
    Tests retrieving a single user by their ID.
    """
    user_id = create_test_user(client, username="test_user_by_id")
    assert user_id is not None

    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    user_data = json.loads(response.data)
    assert user_data['username'] == "test_user_by_id"
    assert user_data['user_id'] == user_id

def test_get_user_by_id_not_found(client):
    """
    Tests retrieving a user with a non-existent ID.
    """
    response = client.get('/users/99999999') # Assuming this ID doesn't exist
    assert response.status_code == 404
    assert "User not found" in json.loads(response.data)['message']


# --- Expense API Tests ---
def test_add_expense(client):
    """
    Tests adding a new expense.
    """
    user_id = create_test_user(client, username="test_user_for_expense_add") # Ensure unique user for this test
    assert user_id is not None

    expense_data = {
        "user_id": user_id,
        "amount": 50.75,
        "category": "Food",
        "description": "Lunch with colleagues",
        "expense_date": "2025-05-29"
    }
    response = client.post('/expenses', json=expense_data)
    assert response.status_code == 201
    assert "Expense added successfully" in json.loads(response.data)['message']

    # Verify in DB (using the view)
    expenses = execute_query(f"SELECT amount, category FROM V_SNG_UserExpenses_L1 WHERE user_id = ? AND category = 'Food'", (user_id,), fetch_type='all')
    assert any(float(e['amount']) == 50.75 for e in expenses) # Convert to float for comparison

def test_add_expense_missing_data(client):
    """
    Tests adding an expense with missing data.
    """
    user_id = create_test_user(client, username="test_user_expense_missing")
    response = client.post('/expenses', json={"user_id": user_id, "amount": 10.0}) # Missing category, date
    assert response.status_code == 400
    assert "Missing expense data" in json.loads(response.data)['error']

def test_add_expense_invalid_date(client):
    """
    Tests adding an expense with an invalid date format.
    """
    user_id = create_test_user(client, username="test_user_expense_invalid_date")
    expense_data = {
        "user_id": user_id,
        "amount": 25.0,
        "category": "Transport",
        "description": "Bus fare",
        "expense_date": "29-05-2025" # Invalid format
    }
    response = client.post('/expenses', json=expense_data)
    assert response.status_code == 400
    assert "Invalid date format" in json.loads(response.data)['error']

def test_get_expenses_by_user(client):
    """
    Tests retrieving expenses for a specific user.
    """
    user_id_1 = create_test_user(client, username="user_for_expenses_1")
    user_id_2 = create_test_user(client, username="user_for_expenses_2")

    # Add expenses for user 1
    client.post('/expenses', json={"user_id": user_id_1, "amount": 100, "category": "Rent", "description": "Monthly rent", "expense_date": "2025-05-01"})
    client.post('/expenses', json={"user_id": user_id_1, "amount": 20, "category": "Coffee", "description": "Morning coffee", "expense_date": "2025-05-02"})
    # Add expense for user 2
    client.post('/expenses', json={"user_id": user_id_2, "amount": 50, "category": "Books", "description": "New book", "expense_date": "2025-05-03"})

    response = client.get(f'/expenses?user_id={user_id_1}')
    assert response.status_code == 200
    expenses = json.loads(response.data)
    assert isinstance(expenses, list)
    assert len(expenses) >= 2 # Should get at least the two expenses for user_id_1
    for expense in expenses:
        assert expense['user_id'] == user_id_1
        assert 'expense_date' in expense # Check if date is converted to string

# --- Budget API Tests ---
def test_create_budget(client):
    """
    Tests creating a new budget.
    """
    user_id = create_test_user(client, username="user_for_budget_create") # Ensure unique user for this test
    assert user_id is not None

    budget_data = {
        "user_id": user_id,
        "category": "Groceries",
        "amount": 300.00,
        "start_date": "2025-06-01",
        "end_date": "2025-06-30"
    }
    response = client.post('/budgets', json=budget_data)
    assert response.status_code == 201
    assert "Budget created successfully" in json.loads(response.data)['message']

    # Verify in DB (using the view)
    budgets = execute_query(f"SELECT budgeted_amount, category FROM V_SNG_BudgetStatus_L1 WHERE user_id = ? AND category = 'Groceries'", (user_id,), fetch_type='all')
    assert any(float(b['budgeted_amount']) == 300.00 for b in budgets) # Convert to float for comparison

def test_create_budget_missing_data(client):
    """
    Tests creating a budget with missing data.
    """
    user_id = create_test_user(client, username="user_for_budget_missing")
    response = client.post('/budgets', json={"user_id": user_id, "category": "Travel"}) # Missing amount, dates
    assert response.status_code == 400
    assert "Missing budget data" in json.loads(response.data)['error']

def test_create_budget_invalid_date(client):
    """
    Tests creating a budget with an invalid date format.
    """
    user_id = create_test_user(client, username="user_for_budget_invalid_date")
    budget_data = {
        "user_id": user_id,
        "category": "Utilities",
        "amount": 150.00,
        "start_date": "01/07/2025", # Invalid format
        "end_date": "31/07/2025"
    }
    response = client.post('/budgets', json=budget_data)
    assert response.status_code == 400
    assert "Invalid date format" in json.loads(response.data)['error']

def test_get_budgets_by_user(client):
    """
    Tests retrieving budgets for a specific user, including budget status.
    """
    user_id = create_test_user(client, username="user_for_budgets_test")

    # Add a budget
    client.post('/budgets', json={"user_id": user_id, "category": "Food", "amount": 200, "start_date": "2025-05-01", "end_date": "2025-05-31"})
    # Add an expense within that budget period
    client.post('/expenses', json={"user_id": user_id, "amount": 50, "category": "Food", "description": "Dinner", "expense_date": "2025-05-15"})

    response = client.get(f'/budgets?user_id={user_id}')
    assert response.status_code == 200
    budgets = json.loads(response.data)
    assert isinstance(budgets, list)
    assert len(budgets) >= 1

    food_budget = next((b for b in budgets if b['category'] == 'Food'), None)
    assert food_budget is not None
    assert float(food_budget['budgeted_amount']) == 200.00 # Convert to float for comparison
    assert float(food_budget['actual_spent']) == 50.00 # Should reflect the expense
    assert float(food_budget['remaining_amount']) == 150.00
    assert 'start_date' in food_budget # Check if dates are converted to string
    assert 'end_date' in food_budget
