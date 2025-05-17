import psycopg2
import os
from dotenv import load_dotenv
import uuid

load_dotenv(override=True) # Ensure your .env has PG_USER, PG_DB, PG_PASSWORD

# PG_HOST = "postgres.vanir-proxmox.duckdns.org"
PG_HOST = os.getenv("PG_HOST")
print(f"PG_HOST: {PG_HOST}\n")
PG_PORT = 5432
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")


def main():
    try:
        print(f"Connecting to PostgreSQL at {PG_HOST}:{PG_PORT} as user '{PG_USER}'...")
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        conn.set_client_encoding('UTF8')
        conn.autocommit = True
        cur = conn.cursor()
        print("Connected successfully.")

        # Create a test table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id UUID PRIMARY KEY,
                content TEXT NOT NULL
            );
        """)
        print("Table 'test_table' ensured.")
        print("OI")
        # Insert a random row
        test_id = str(uuid.uuid4())
        test_content = f"Hello from Python! UUID: {test_id}"
        cur.execute("INSERT INTO test_table (id, content) VALUES (%s, %s);", (test_id, test_content))
        print(f"Inserted row with id={test_id}")

        # Read it back
        cur.execute("SELECT content FROM test_table WHERE id = %s;", (test_id,))
        row = cur.fetchone()
        if row:
            print("Type of row[0]:", type(row[0]))
            print("Read from DB:", row[0])
        else:
            print("No data found.")

        # Clean up (optional)
        # cur.execute("DROP TABLE test_table;")
        # print("Dropped test_table.")

        cur.close()
        conn.close()
        print("Connection closed.")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()