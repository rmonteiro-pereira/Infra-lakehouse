import redis
import os
from dotenv import load_dotenv

load_dotenv(override=True)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_ADMIN_PASSWORD = os.getenv("REDIS_PASSWORD")  # Admin password
REDIS_USER = "Renato"  # The user you want to create/update
REDIS_USER_PASSWORD = os.getenv("RenatoPassword")  # Set a strong password

def create_or_update_redis_user():
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_ADMIN_PASSWORD,
        decode_responses=True,
        ssl=True,                # Set to True if your Redis uses TLS
        ssl_cert_reqs=None       # For self-signed/auto-generated certs
    )
    try:
        # Create or update user with all permissions (admin)
        acl_command = f"ACL SETUSER {REDIS_USER} on >{REDIS_USER_PASSWORD} allcommands allkeys"
        print(f"Executing: {acl_command.replace(REDIS_USER_PASSWORD, '********')}")
        r.execute_command(acl_command)
        print(f"User '{REDIS_USER}' created/updated with admin privileges.")
    except redis.exceptions.ResponseError as e:
        print(f"Redis Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    create_or_update_redis_user()