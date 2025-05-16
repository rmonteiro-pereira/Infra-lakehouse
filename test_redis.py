import redis
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Redis connection details from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") # Can be None if Redis has no password

def main():
    try:
        print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
        # Note: decode_responses=True makes redis-py return Python strings instead of bytes
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True, # Automatically decode responses to strings
            socket_connect_timeout=5 # Timeout for connection in seconds
        )

        # Check connection
        r.ping()
        print("Connected to Redis successfully!")

        # Generate a random key and value for testing
        test_key = f"test_key_{uuid.uuid4().hex[:8]}"
        test_value = f"Hello from Python to Redis! UUID: {uuid.uuid4().hex}"

        # --- SET operation ---
        print(f"Setting key '{test_key}' with value '{test_value}'...")
        r.set(test_key, test_value)
        print(f"Key '{test_key}' set successfully.")

        # --- GET operation ---
        print(f"Getting key '{test_key}'...")
        retrieved_value = r.get(test_key)
        if retrieved_value is not None:
            print(f"Value for '{test_key}': {retrieved_value}")
            if retrieved_value == test_value:
                print("Value matches what was set. Test successful!")
            else:
                print("ERROR: Retrieved value does not match the set value.")
        else:
            print(f"ERROR: Key '{test_key}' not found after setting.")

        # --- DELETE operation ---
        print(f"Deleting key '{test_key}'...")
        delete_result = r.delete(test_key)
        if delete_result == 1:
            print(f"Key '{test_key}' deleted successfully.")
        else:
            print(f"Warning: Key '{test_key}' might not have been deleted (delete returned {delete_result}).")

        # Verify deletion
        retrieved_after_delete = r.get(test_key)
        if retrieved_after_delete is None:
            print(f"Key '{test_key}' successfully verified as deleted.")
        else:
            print(f"ERROR: Key '{test_key}' still exists after attempting deletion.")

    except redis.exceptions.ConnectionError as e:
        print(f"Redis Connection Error: {e}")
        print(f"Hint: Check if REDIS_HOST ('{REDIS_HOST}') and REDIS_PORT ('{REDIS_PORT}') are correct and reachable.")
        print("Hint: Also verify your Redis service is running and accessible, and password (if any) is correct.")
    except redis.exceptions.AuthenticationError as e:
        print(f"Redis Authentication Error: {e}")
        print("Hint: Check if REDIS_PASSWORD is correct or if Redis requires authentication.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if not REDIS_HOST or (REDIS_PASSWORD is None and os.getenv("REDIS_AUTH_EXPECTED", "false").lower() == "true"):
        # A simple check, you might want more robust validation
        print("Warning: REDIS_HOST is not set, or REDIS_PASSWORD is not set while auth might be expected.")
        print("Please ensure REDIS_HOST, REDIS_PORT, and REDIS_PASSWORD are correctly set in your .env file.")
    main()