from minio import Minio
from minio.error import S3Error
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MINIO_ENDPOINT = "minio-api.vanir-proxmox.duckdns.org"
MINIO_ACCESS_KEY = "Rodrigo"
MINIO_SECRET_KEY = os.getenv("RodrigoPassword")
USE_SSL = False

def delete_bucket_contents(bucket_name):
    """Delete all objects in the specified bucket"""
    
    # Check if credentials are loaded
    if not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
        print("Error: MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set in .env file")
        return False

    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=USE_SSL,
    )

    try:
        # Check if bucket exists
        if not client.bucket_exists(bucket_name):
            print(f"Error: Bucket '{bucket_name}' does not exist")
            return False
            
        print(f"Connecting to MinIO and deleting all objects in bucket: {bucket_name}")
        objects_deleted = 0
        
        # List all objects in the bucket (including in subdirectories)
        objects = client.list_objects(bucket_name, recursive=True)
        
        for obj in objects:
            try:
                client.remove_object(bucket_name, obj.object_name)
                print(f"  Deleted object: {obj.object_name}")
                objects_deleted += 1
            except Exception as e:
                print(f"  Error deleting object {obj.object_name}: {e}")
        
        if objects_deleted == 0:
            print(f"Bucket '{bucket_name}' is already empty")
        else:
            print(f"Successfully deleted {objects_deleted} objects from bucket '{bucket_name}'")
            
        return True
        
    except S3Error as e:
        print(f"MinIO S3 Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python delete_bucket_contents.py <bucket_name>")
        print("Example: python delete_bucket_contents.py my-bucket")
        sys.exit(1)
    
    bucket_name = sys.argv[1]
    
    # Confirm deletion
    response = input(f"Are you sure you want to delete ALL objects in bucket '{bucket_name}'? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled")
        sys.exit(0)
    
    success = delete_bucket_contents(bucket_name)
    if success:
        print(f"All objects in bucket '{bucket_name}' have been deleted successfully")
    else:
        print(f"Failed to delete objects from bucket '{bucket_name}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
