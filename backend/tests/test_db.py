import pytest
from app.db import get_db_connection, execute_query
import os
from dotenv import load_dotenv

# Load environment variables for tests as well
load_dotenv()

# Define a fixture for database connection for tests
@pytest.fixture(scope='module')
def db_connection():
    """
    Fixture to provide a database connection for tests.
    Ensures connection is closed after all tests in the module.
    """
    conn = get_db_connection()
    yield conn
    conn.close()

# Test the database connection
def test_get_db_connection():
    """
    Tests if a database connection can be established successfully.
    """
    conn = None
    try:
        conn = get_db_connection()
        assert conn is not None
        # Removed: assert conn.connected # pyodbc.Connection object has no 'connected' attribute
    finally:
        if conn:
            conn.close()

# Test execute_query for DML (INSERT/DELETE)
def test_execute_query_dml(db_connection):
    """
    Tests if DML operations (INSERT, DELETE) can be executed.
    Inserts a test user and then deletes it.
    """
    # Ensure a unique username for testing
    test_username = "test_user_for_dml_query"
    test_email = "dml_test@example.com"
    test_password = "dml_password"

    # Clean up any previous test data related to this specific test user
    execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (test_username,))
    execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (test_username,))
    execute_query("DELETE FROM T_SNG_Users WHERE username = ?", (test_username,))

    # Test INSERT
    insert_query = "INSERT INTO T_SNG_Users (username, email, password_hash) VALUES (?, ?, ?)"
    execute_query(insert_query, (test_username, test_email, test_password))

    # Verify insertion by fetching
    fetch_query = "SELECT username FROM T_SNG_Users WHERE username = ?"
    result = execute_query(fetch_query, (test_username,), fetch_type='one')
    assert result is not None
    assert result['username'] == test_username # Access as dictionary

    # Test DELETE
    delete_query = "DELETE FROM T_SNG_Users WHERE username = ?"
    execute_query(delete_query, (test_username,))

    # Verify deletion
    result = execute_query(fetch_query, (test_username,), fetch_type='one')
    assert result is None


# Test execute_query for SELECT (fetch_one)
def test_execute_query_fetch_one(db_connection):
    """
    Tests if fetch_one correctly retrieves a single row.
    Inserts a user, fetches it, and then deletes it.
    """
    test_username = "test_user_fetch_one"
    test_email = "fetch_one@example.com"
    test_password = "fetch_one_password"

    # Clean up any previous test data related to this specific test user
    execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (test_username,))
    execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (test_username,))
    execute_query("DELETE FROM T_SNG_Users WHERE username = ?", (test_username,))
    
    execute_query("INSERT INTO T_SNG_Users (username, email, password_hash) VALUES (?, ?, ?)",
                  (test_username, test_email, test_password))

    query = "SELECT user_id, username, email FROM T_SNG_Users WHERE username = ?"
    user = execute_query(query, (test_username,), fetch_type='one')

    assert user is not None
    assert user['username'] == test_username # Access as dictionary
    assert user['email'] == test_email # Access as dictionary
    assert 'user_id' in user # Check if user_id attribute exists

    # Clean up
    execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (test_username,))
    execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (test_username,))
    execute_query("DELETE FROM T_SNG_Users WHERE username = ?", (test_username,))


# Test execute_query for SELECT (fetch_all)
def test_execute_query_fetch_all(db_connection):
    """
    Tests if fetch_all correctly retrieves multiple rows as a list of dictionaries.
    Inserts two users, fetches all, and then deletes them.
    """
    test_users = [
        ("test_user_fetch_all_1", "all1@example.com", "pass1"),
        ("test_user_fetch_all_2", "all2@example.com", "pass2")
    ]

    # Clean up any previous test data related to these specific test users
    for user_data in test_users:
        execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (user_data[0],))
        execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (user_data[0],))
        execute_query("DELETE FROM T_SNG_Users WHERE username = ?", (user_data[0],))

    # Insert test users
    insert_query = "INSERT INTO T_SNG_Users (username, email, password_hash) VALUES (?, ?, ?)"
    for user_data in test_users:
        execute_query(insert_query, user_data)

    query = "SELECT username, email FROM T_SNG_Users WHERE username LIKE 'test_user_fetch_all_%'"
    users = execute_query(query, fetch_type='all')

    assert isinstance(users, list)
    assert len(users) >= 2 # May include other users if database isn't fully isolated
    # Check if the inserted users are present and are dictionaries
    found_count = 0
    for user_dict in users:
        if user_dict['username'] in [u[0] for u in test_users]:
            assert isinstance(user_dict, dict)
            found_count += 1
    assert found_count == 2

    # Clean up
    for user_data in test_users:
        execute_query("DELETE FROM T_SNG_Expenses WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (user_data[0],))
        execute_query("DELETE FROM T_SNG_Budgets WHERE user_id IN (SELECT user_id FROM T_SNG_Users WHERE username = ?)", (user_data[0],))
        execute_query("DELETE FROM T_SNG_Users WHERE username = ?", (user_data[0],))
