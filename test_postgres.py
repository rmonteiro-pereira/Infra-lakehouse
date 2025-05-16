import psycopg2
import uuid
import os # Import the os module
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection details from environment variables
PG_HOST = os.getenv("PG_HOST", "your-default-postgres-host") # Provide a default if needed
PG_PORT = int(os.getenv("PG_PORT", "5432")) # Convert port to integer
PG_DB = os.getenv("PG_DB", "your-default-db")
PG_USER = os.getenv("PG_USER", "your-default-user")
PG_PASSWORD = os.getenv("PG_PASSWORD") # No default for password is safer

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