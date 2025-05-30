import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details from environment variables
DB_SERVER = os.getenv('DB_SERVER')
DB_DATABASE = os.getenv('DB_DATABASE')
# DB_USERNAME and DB_PASSWORD are not needed for Trusted_Connection=yes

def get_db_connection():
    """
    Establishes and returns a connection to the SQL Server database using Windows Authentication.
    Ensures that environment variables for connection details are loaded.
    """
    try:
        # Construct the connection string for Windows Authentication
        # The DRIVER might need to be adjusted based on your SQL Server ODBC driver.
        # Common drivers:
        # - '{ODBC Driver 17 for SQL Server}' (most common and recommended)
        # - '{SQL Server}' (older driver)
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"Trusted_Connection=yes;" # This enables Windows Authentication
        )
        conn = pyodbc.connect(conn_str)
        conn.autocommit = True # Set autocommit to True for simpler operations
        print("Database connection successful!")
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database connection failed: {sqlstate}")
        # In a real application, you might want to log this error more formally
        raise # Re-raise the exception to indicate connection failure

def execute_query(query, params=None, fetch_type='none'):
    """
    Executes a SQL query and optionally fetches results.

    Args:
        query (str): The SQL query string.
        params (tuple or list, optional): Parameters for the query. Defaults to None.
        fetch_type (str): 'none' for DDL/DML, 'one' for single row, 'all' for multiple rows.

    Returns:
        list or dict or None: Fetched data based on fetch_type, or None for DDL/DML.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params if params is not None else ())

        if fetch_type == 'one':
            row = cursor.fetchone()
            if row:
                # Fetch column names and create a dictionary for the single row
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row)) # THIS IS THE CRITICAL CONVERSION
            return None # No row found
        elif fetch_type == 'all':
            # Fetch column names for dictionary mapping
            columns = [column[0] for column in cursor.description]
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            return rows
        else:
            return None # For DDL/DML operations
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error executing query: {query} with params {params}. Error: {sqlstate}")
        raise # Re-raise the exception
    finally:
        if conn:
            conn.close()

# Example usage (for testing purposes, will be removed later)
if __name__ == '__main__':
    try:
        # Test connection
        conn = get_db_connection()
        if conn:
            print("Successfully connected to the database.")
            conn.close()

        # Test inserting a user
        print("\nAttempting to insert a test user...")
        insert_user_query = "INSERT INTO T_SNG_Users (username, email, password_hash) VALUES (?, ?, ?)"
        execute_query(insert_user_query, ('testuser_123', 'test@example.com', 'hashedpassword123'))
        print("Test user inserted (if not exists).")

        # Test fetching a user
        print("\nAttempting to fetch the test user...")
        fetch_user_query = "SELECT user_id, username, email FROM T_SNG_Users WHERE username = ?"
        user = execute_query(fetch_user_query, ('testuser_123',), fetch_type='one')
        if user:
            print(f"Fetched user: {user['username']}, {user['email']}") # Access as dictionary
        else:
            print("Test user not found.")

        # Test fetching all users
        print("\nAttempting to fetch all users...")
        all_users = execute_query("SELECT user_id, username, email FROM T_SNG_Users", fetch_type='all')
        if all_users:
            print("All users:")
            for u in all_users:
                print(f"  ID: {u['user_id']}, Username: {u['username']}, Email: {u['email']}")
        else:
            print("No users found.")

        # Clean up the test user
        print("\nAttempting to delete the test user...")
        delete_user_query = "DELETE FROM T_SNG_Users WHERE username = ?"
        execute_query(delete_user_query, ('testuser_123',))
        print("Test user deleted.")

    except Exception as e:
        print(f"An error occurred during db.py self-test: {e}")
