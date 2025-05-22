from minio import Minio
from minio.error import S3Error
import io
import uuid # For generating random names
import random # For generating random content
import string # For character sets for random content

# MinIO Connection Details
# IMPORTANT: Ensure these details match your MinIO setup and Kubernetes secrets.
# The MINIO_ENDPOINT should be the URL that routes to your MinIO API (port 9000 via Ingress).
MINIO_ENDPOINT = "minio-api.vanir-proxmox.duckdns.org" # Hostname for MinIO API
# The MinIO client typically handles http/https and port based on the `secure` flag and endpoint string.
# If your Ingress serves HTTP on port 80 for minio.api.teste.local, this is fine.
# If it's a different port, include it: "minio.api.teste.local:PORT"
# MINIO_ACCESS_KEY = "Rodrigo"  # Replace with the value from your 'minio-secrets' (key: root-user)
# MINIO_SECRET_KEY = ""  # Replace with the value from your 'minio-secrets' (key: root-password)
MINIO_ACCESS_KEY = "Renato"  # Replace with the value from your 'minio-secrets' (key: root-user)
MINIO_SECRET_KEY = ""  # Replace with the value from your 'minio-secrets' (key: root-password)
# Set USE_SSL to True if your MinIO endpoint (via Ingress) is configured for HTTPS.
# Assuming HTTP based on previous context.
USE_SSL = False

# --- Generate Random Bucket, Object, and Content Details ---
# Generate a unique bucket name (MinIO bucket names have specific rules, e.g., lowercase, no underscores)
# We'll create a short UUID and ensure it's valid.
BUCKET_NAME = f"bucket-{uuid.uuid4().hex[:12]}"
OBJECT_NAME = f"file-{uuid.uuid4().hex[:8]}.txt"

def generate_random_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation + " "
    return ''.join(random.choice(characters) for i in range(length))

SAMPLE_DATA = f"Hello from Python to MinIO!\nThis is a random test file: {OBJECT_NAME}\n" \
              f"Random content: {generate_random_string(random.randint(50, 200))}"

def main():
    # Initialize MinIO client
    try:
        # Construct the endpoint string for the client
        # The client prepends http:// or https:// based on the secure flag.
        client = Minio(
            MINIO_ENDPOINT, # e.g., "minio.api.teste.local" or "minio.api.teste.local:80"
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=USE_SSL
        )
        print(f"Attempting to connect to MinIO at endpoint: {MINIO_ENDPOINT}, secure={USE_SSL}")
    except Exception as e:
        print(f"Error initializing MinIO client: {e}")
        return

    try:
        # --- Create Bucket and Upload Data ---
        print(f"Checking if bucket '{BUCKET_NAME}' exists...")
        found = client.bucket_exists(BUCKET_NAME)
        if not found:
            print(f"Bucket '{BUCKET_NAME}' not found. Creating...")
            client.make_bucket(BUCKET_NAME)
            print(f"Bucket '{BUCKET_NAME}' created successfully.")
        else:
            print(f"Bucket '{BUCKET_NAME}' already exists.")

        data_bytes = SAMPLE_DATA.encode('utf-8')
        data_stream = io.BytesIO(data_bytes)
        data_len = len(data_bytes)

        print(f"Uploading '{OBJECT_NAME}' to bucket '{BUCKET_NAME}'...")
        client.put_object(
            BUCKET_NAME,
            OBJECT_NAME,
            data_stream,
            data_len,
            content_type="text/plain"
        )
        print(f"'{OBJECT_NAME}' uploaded successfully to bucket '{BUCKET_NAME}'.")

        # --- Retrieve Data ---
        print(f"\nRetrieving '{OBJECT_NAME}' from bucket '{BUCKET_NAME}'...")
        retrieved_object = client.get_object(BUCKET_NAME, OBJECT_NAME)
        retrieved_data_bytes = retrieved_object.read()
        retrieved_data_string = retrieved_data_bytes.decode('utf-8')
        # It's good practice to close the response object
        retrieved_object.close()
        retrieved_object.release_conn()

        print(f"Content of '{OBJECT_NAME}':")
        print("------------------------------------")
        print(retrieved_data_string)
        print("------------------------------------")
        print(f"'{OBJECT_NAME}' retrieved and read successfully.")

        # --- Clean up (Optional: Delete object and bucket) ---
        # print(f"\nCleaning up: Deleting '{OBJECT_NAME}' from bucket '{BUCKET_NAME}'...")
        # client.remove_object(BUCKET_NAME, OBJECT_NAME)
        # print(f"'{OBJECT_NAME}' deleted successfully.")
        # print(f"Cleaning up: Deleting bucket '{BUCKET_NAME}'...")
        # client.remove_bucket(BUCKET_NAME)
        # print(f"Bucket '{BUCKET_NAME}' deleted successfully.")


    except S3Error as exc:
        print(f"MinIO S3 Error occurred: {exc}")
        # More detailed error for connection issues
        if "Failed to establish a new connection" in str(exc) or \
           "Name or service not known" in str(exc) or \
           "Connection refused" in str(exc) or \
           "nodename nor servname provided" in str(exc).lower(): # Added for getaddrinfo like errors
            print(f"Hint: Check if MINIO_ENDPOINT ('{MINIO_ENDPOINT}') is correct and reachable, "
                  f"and if the MinIO service and Ingress are correctly routing to the API port (default 9000).")
            print(f"Hint: Also ensure '{MINIO_ENDPOINT}' is resolvable (e.g., in your local hosts file if not public DNS).")
            if USE_SSL:
                print("Hint: Also verify SSL/TLS certificates if USE_SSL is True.")
            else:
                print("Hint: Ensure your Ingress is listening on HTTP for this endpoint if USE_SSL is False.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # This check is for placeholder values.
    # If "admin" and "super-secret" are your actual credentials, this check will pass.
    if MINIO_ACCESS_KEY == "YOUR_MINIO_ROOT_USER" or MINIO_SECRET_KEY == "YOUR_MINIO_ROOT_PASSWORD":
        print("ERROR: Please update MINIO_ACCESS_KEY and MINIO_SECRET_KEY in the script "
              "with your actual credentials from your 'minio-secrets' Kubernetes secret.")
    else:
        main()
