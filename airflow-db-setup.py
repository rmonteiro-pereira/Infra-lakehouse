import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

def get_env_var(var_name, default_value=None, required=False, is_bool=False):
    """Gets an environment variable, with options for default, required, and boolean conversion."""
    value = os.getenv(var_name, default_value)
    if value is not None:
        # Strip leading/trailing whitespace
        value = value.strip()
        # Strip common surrounding quotes
        if len(value) >= 2 and ((value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'"))):
            value = value[1:-1]

    if required and value is None:
        print(f"Error: Environment variable '{var_name}' is required but not set.")
        sys.exit(1)
    
    if is_bool:
        if value is not None:
            return value.lower() in ['true', '1', 't', 'y', 'yes']
        return False # Default for boolean if not set and not required
    return value

def db_exists(cursor, db_name):
    """Checks if a database exists."""
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
    return cursor.fetchone() is not None

def user_exists(cursor, user_name):
    """Checks if a user exists."""
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (user_name,))
    return cursor.fetchone() is not None

def main():
    print("--- Airflow PostgreSQL Setup Script ---")

    # PostgreSQL Admin Connection Details
    pg_admin_host = get_env_var("PG_HOST", "localhost")
    print(f"DEBUG: pg_admin_host = {pg_admin_host}")
    pg_admin_port = get_env_var("PG_PORT", "5432")
    print(f"DEBUG: pg_admin_port = {pg_admin_port}")
    pg_admin_user = get_env_var("PG_SUPER_USER", "postgres")
    print(f"DEBUG: pg_admin_user = {pg_admin_user}")
    pg_admin_password = get_env_var("PG_SUPER_PASSWORD", required=True)
    # For security, avoid printing passwords directly in production logs.
    # For debugging, you can print its presence or length:
    print(f"DEBUG: pg_admin_password is set (length: {len(pg_admin_password) if pg_admin_password else 0})")
    pg_admin_db = get_env_var("PG_DB", "postgres") # DB to connect to for admin tasks
    print(f"DEBUG: pg_admin_db = {pg_admin_db}")

    # Airflow Database and User Details
    airflow_db_name = get_env_var("AIRFLOW_DB_NAME", "airflow")
    print(f"DEBUG: airflow_db_name = {airflow_db_name}")
    airflow_db_user = get_env_var("AIRFLOW_DB_USER", "airflow")
    print(f"DEBUG: airflow_db_user = {airflow_db_user}")
    airflow_db_password = get_env_var("AIRFLOW_PASSWORD", required=True)
    # For security, avoid printing passwords directly in production logs.
    print(f"DEBUG: airflow_db_password is set (length: {len(airflow_db_password) if airflow_db_password else 0})")
    
    # Option to update password if user exists
    update_password_if_exists = get_env_var("UPDATE_AIRFLOW_USER_PASSWORD_IF_EXISTS", "true", required=False, is_bool=True)
    print(f"DEBUG: update_password_if_exists = {update_password_if_exists}")
    
    # Option to update password if user exists
    update_password_if_exists = get_env_var("UPDATE_AIRFLOW_USER_PASSWORD_IF_EXISTS", "true", required=False, is_bool=True)

    print


    conn_admin = None
    try:
        # Connect to the PostgreSQL server as admin
        print(f"\nConnecting to PostgreSQL server at {pg_admin_host}:{pg_admin_port} as user '{pg_admin_user}' to database '{pg_admin_db}'...")
        conn_admin = psycopg2.connect(
            host=pg_admin_host,
            port=pg_admin_port,
            user=pg_admin_user,
            password=pg_admin_password,
            dbname=pg_admin_db
        )
        conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur_admin = conn_admin.cursor()
        print("Successfully connected as admin.")

                # List all databases
        print("\n--- Listing all databases on the server ---")
        cur_admin.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cur_admin.fetchall()
        if databases:
            print("Available databases:")
            for db in databases:
                print(f"- {db[0]}")
        else:
            print("No user databases found (excluding templates).")
        print("--- Finished listing databases ---")

        # 1. Create Airflow Database if it doesn't exist
        print(f"\nChecking if database '{airflow_db_name}' exists...")
        if not db_exists(cur_admin, airflow_db_name):
            print(f"Database '{airflow_db_name}' does not exist. Creating...")
            cur_admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(airflow_db_name)))
            print(f"Database '{airflow_db_name}' created successfully.")
        else:
            print(f"Database '{airflow_db_name}' already exists.")

        # 2. Create Airflow User if it doesn't exist
        print(f"\nChecking if user '{airflow_db_user}' exists...")
        if not user_exists(cur_admin, airflow_db_user):
            print(f"User '{airflow_db_user}' does not exist. Creating...")
            cur_admin.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(airflow_db_user)), (airflow_db_password,))
            print(f"User '{airflow_db_user}' created successfully.")
        else:
            print(f"User '{airflow_db_user}' already exists.")
            if update_password_if_exists:
                print(f"Updating password for user '{airflow_db_user}' as per request...")
                cur_admin.execute(sql.SQL("ALTER USER {} WITH PASSWORD %s").format(sql.Identifier(airflow_db_user)), (airflow_db_password,))
                print(f"Password updated for user '{airflow_db_user}'.")


        # 3. Grant all privileges on the database
        print(f"\nGranting ALL PRIVILEGES on database '{airflow_db_name}' to user '{airflow_db_user}'...")
        cur_admin.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(airflow_db_name),
            sql.Identifier(airflow_db_user)
        ))
        print("Database privileges granted successfully.")
        
        cur_admin.close() # Close admin cursor before potentially opening a new connection

    except psycopg2.Error as e:
        print(f"\nPostgreSQL Error during initial setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred during initial setup: {e}")
        sys.exit(1)
    finally:
        if conn_admin:
            conn_admin.close()
            print("\nAdmin connection for initial setup closed.")

    # 4. Grant schema privileges (especially for PostgreSQL 15+)
    # It's best to connect to the airflow_db for this operation.
    conn_airflow_db = None
    try:
        print(f"\nConnecting to database '{airflow_db_name}' as user '{pg_admin_user}' to grant schema privileges...")
        conn_airflow_db = psycopg2.connect(
            host=pg_admin_host,
            port=pg_admin_port,
            user=pg_admin_user, # Admin user can grant privileges in any DB it can connect to
            password=pg_admin_password,
            dbname=airflow_db_name # Connect to the Airflow database
        )
        cur_airflow_db = conn_airflow_db.cursor()
        
        print(f"Granting ALL ON SCHEMA public in database '{airflow_db_name}' to user '{airflow_db_user}'...")
        cur_airflow_db.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
            sql.Identifier(airflow_db_user)
        ))
        conn_airflow_db.commit() # Commit the grant
        print("SCHEMA public privileges granted successfully.")
        cur_airflow_db.close()

    except psycopg2.Error as e:
        print(f"\nPostgreSQL Error during schema grant: {e}")
        print("This might be okay if not using PostgreSQL 15+ or if permissions are already sufficient.")
        # Depending on the error, you might not want to exit here if the main setup was okay.
    except Exception as e:
        print(f"\nAn unexpected error occurred during schema grant: {e}")
    finally:
        if conn_airflow_db:
            conn_airflow_db.close()
            print(f"Connection to '{airflow_db_name}' for schema grant closed.")

    print("\n--- Airflow PostgreSQL Setup Script Finished ---")

if __name__ == "__main__":
    main()