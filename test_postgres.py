import psycopg2
import os
from dotenv import load_dotenv

load_dotenv() # Ensure your .env has PG_USER, PG_DB, PG_PASSWORD

PG_HOST = "postgres.vanir-proxmox.duckdns.org"
PG_PORT = 5432
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")

try:
    print(f"Connecting to PostgreSQL at {PG_HOST}:{PG_PORT} as user '{PG_USER}' with SSL...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        sslmode='require'  # Use 'require' for encryption.
                           # For self-signed certs, 'verify-ca' or 'verify-full' would
                           # require you to provide the server's certificate via sslrootcert
                           # and have it trusted by your client system.
    )
    conn.set_client_encoding('UTF8')
    cur = conn.cursor()
    print("Connected successfully using SSL.")

    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("PostgreSQL version:", version)

    cur.close()
    conn.close()
    print("Connection closed.")

except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")