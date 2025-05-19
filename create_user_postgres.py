import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# --- Configuration for the new/target admin user ---
NEW_ADMIN_USERNAME = "vanir"
# Get password from .env, otherwise use a placeholder.
# The script will only attempt to SET this password if "RenatoPassword" is in .env
NEW_ADMIN_PASSWORD_FROM_ENV = os.getenv("PG_PASSWORD")
NEW_ADMIN_PASSWORD_DEFAULT = "ReplaceWithAStrongPassword123!"
NEW_ADMIN_PASSWORD = NEW_ADMIN_PASSWORD_FROM_ENV if NEW_ADMIN_PASSWORD_FROM_ENV is not None else NEW_ADMIN_PASSWORD_DEFAULT
# --- ---

def create_or_update_admin_user():
    """
    Connects to PostgreSQL using superuser credentials from .env.
    Creates a new user with SUPERUSER privileges if they don't exist.
    If the user exists, grants SUPERUSER and updates their password
    if 'RenatoPassword' is set in the .env file.
    """
    # Database connection parameters from .env file
    # The user connecting here (db_user) MUST be a superuser.
    db_host = os.getenv("PG_HOST")
    db_port = os.getenv("PG_PORT", "5432")
    db_name = os.getenv("PG_DB") # Connect to a specific DB, e.g., 'postgres' or the app DB
    db_super_user = os.getenv("PG_SUPER_USER")
    db_super_password = os.getenv("PG_SUPER_PASSWORD")

    if not all([db_host, db_name, db_super_user, db_super_password]):
        print("Error: Ensure PG_HOST, PG_DB, PG_SUPER_USER, and PG_SUPER_PASSWORD are set in your .env file.")
        return

    # Security check for default password if we intend to use it for a new user
    # or if RenatoPassword was explicitly set to the default in .env
    if NEW_ADMIN_PASSWORD == NEW_ADMIN_PASSWORD_DEFAULT:
        print(f"SECURITY WARNING: The password for '{NEW_ADMIN_USERNAME}' is the default placeholder.")
        if NEW_ADMIN_PASSWORD_FROM_ENV is None:
            print("This is because 'RenatoPassword' is not set in your .env file.")
        else:
            print("This is because 'RenatoPassword' in your .env file is set to the default placeholder.")
        
        proceed = input(f"Do you want to proceed using this default password for '{NEW_ADMIN_USERNAME}'? (yes/no): ").lower()
        if proceed != 'yes':
            print("Aborted.")
            return

    conn = None
    try:
        print(f"Connecting to PostgreSQL database '{db_name}' on {db_host}:{db_port} as superuser '{db_super_user}'...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_super_user,
            password=db_super_password
        )
        conn.autocommit = True  # Enable autocommit for DDL statements
        cur = conn.cursor()
        print("Successfully connected as superuser.")

        # Check if the user already exists
        cur.execute("SELECT rolsuper FROM pg_roles WHERE rolname = %s;", (NEW_ADMIN_USERNAME,))
        user_exists_row = cur.fetchone()

        if user_exists_row:
            print(f"User '{NEW_ADMIN_USERNAME}' already exists.")
            current_is_superuser = user_exists_row[0]

            # Grant SUPERUSER if not already a superuser
            if not current_is_superuser:
                sql_alter_superuser = f"ALTER USER {NEW_ADMIN_USERNAME} SUPERUSER;"
                print(f"Attempting to grant SUPERUSER to '{NEW_ADMIN_USERNAME}'...")
                print(f"Executing: {sql_alter_superuser}")
                cur.execute(sql_alter_superuser)
                print(f"User '{NEW_ADMIN_USERNAME}' granted SUPERUSER privileges.")
            else:
                print(f"User '{NEW_ADMIN_USERNAME}' already has SUPERUSER privileges.")

            # Update password if RenatoPassword was explicitly set in .env
            if NEW_ADMIN_PASSWORD_FROM_ENV is not None:
                sql_alter_password = f"ALTER USER {NEW_ADMIN_USERNAME} WITH PASSWORD '{NEW_ADMIN_PASSWORD}';"
                print(f"Attempting to update password for '{NEW_ADMIN_USERNAME}'...")
                print(f"Executing: {sql_alter_password.replace(NEW_ADMIN_PASSWORD, '********')}")
                cur.execute(sql_alter_password)
                print(f"Password for user '{NEW_ADMIN_USERNAME}' updated successfully.")
            else:
                print(f"Password for '{NEW_ADMIN_USERNAME}' not changed (RenatoPassword not set in .env).")

        else:
            # User does not exist, create them
            sql_create_user = f"CREATE USER {NEW_ADMIN_USERNAME} WITH PASSWORD '{NEW_ADMIN_PASSWORD}' SUPERUSER;"
            print(f"User '{NEW_ADMIN_USERNAME}' does not exist. Attempting to create...")
            print(f"Executing: {sql_create_user.replace(NEW_ADMIN_PASSWORD, '********')}")
            cur.execute(sql_create_user)
            print(f"User '{NEW_ADMIN_USERNAME}' created successfully with SUPERUSER privileges and specified password.")

        cur.close()

    except psycopg2.Error as e:
        print(f"PostgreSQL Error: {e}")
        if "password authentication failed" in str(e).lower():
            print(f"Hint: Check if the credentials for superuser '{db_super_user}' are correct in your .env file.")
        elif "permission denied" in str(e).lower() and db_super_user != 'postgres': # Generic check
             print(f"Hint: The user '{db_super_user}' may not have sufficient privileges (e.g., CREATEROLE or SUPERUSER). Ensure it's a true superuser.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_or_update_admin_user()