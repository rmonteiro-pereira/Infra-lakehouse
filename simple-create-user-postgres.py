import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(override=True)

PG_HOST = os.getenv("PG_HOST")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_ADMIN_USER = os.getenv("PG_SUPER_USER", "postgres")
PG_ADMIN_PASSWORD = os.getenv("PG_SUPER_PASSWORD")
AIRFLOW_DB = "airflow"
AIRFLOW_USER = "airflow"
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "ChangeMeAirflow123")

def main():
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname="postgres",
        user=PG_ADMIN_USER,
        password=PG_ADMIN_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Create database
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (AIRFLOW_DB,))
    if not cur.fetchone():
        print(f"Creating database '{AIRFLOW_DB}'...")
        cur.execute(f"CREATE DATABASE {AIRFLOW_DB};")
    else:
        print(f"Database '{AIRFLOW_DB}' already exists.")

    # Create user
    cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = %s", (AIRFLOW_USER,))
    if not cur.fetchone():
        print(f"Creating user '{AIRFLOW_USER}'...")
        cur.execute(f"CREATE USER {AIRFLOW_USER} WITH PASSWORD %s;", (AIRFLOW_PASSWORD,))
    else:
        print(f"User '{AIRFLOW_USER}' already exists. Updating password...")
        cur.execute(f"ALTER USER {AIRFLOW_USER} WITH PASSWORD %s;", (AIRFLOW_PASSWORD,))

    # Grant privileges
    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {AIRFLOW_DB} TO {AIRFLOW_USER};")
    print(f"Granted all privileges on '{AIRFLOW_DB}' to '{AIRFLOW_USER}'.")

    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()