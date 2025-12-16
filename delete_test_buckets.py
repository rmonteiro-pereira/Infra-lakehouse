from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MINIO_ENDPOINT = "minio-api.vanir-proxmox.duckdns.org"
MINIO_ACCESS_KEY = "Rodrigo"
MINIO_SECRET_KEY = os.getenv("RodrigoPassword")
USE_SSL = False

print(MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
# Check if credentials are loaded
if not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
    print("Error: MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set in .env file")
    exit(1)

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=USE_SSL,
)

try:
    print("Connecting to MinIO and listing buckets...")
    buckets_deleted = 0
    
    for bucket in client.list_buckets():
        if bucket.name.startswith("bucket-"):
            print(f"Deleting bucket: {bucket.name}")
            # Remove all objects in the bucket first
            objects = client.list_objects(bucket.name, recursive=True)
            for obj in objects:
                client.remove_object(bucket.name, obj.object_name)
                print(f"  Removed object: {obj.object_name}")
            # Now remove the bucket
            client.remove_bucket(bucket.name)
            print(f"Successfully deleted bucket: {bucket.name}")
            buckets_deleted += 1
    
    if buckets_deleted == 0:
        print("No test buckets found (buckets starting with 'bucket-')")
    else:
        print(f"Total buckets deleted: {buckets_deleted}")
        
except Exception as e:
    print(f"Error: {e}")