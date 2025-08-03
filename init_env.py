import secrets
from typing import Optional

def input_with_default(prompt: str, default: str) -> str:
    """
    Prompts the user for input with a default value.
    Returns the user's input if provided, otherwise the default.
    """
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default

def generate_secret_key() -> str:
    """
    Generates a secure random secret key for Django.
    """
    return secrets.token_urlsafe(50)

print("Choose environment mode:")
print("1) Development (dev)")
print("2) Production (deployment)")
env_choice = input("Enter choice (1 or 2) [default: 1]: ").strip()

ENVIRONMENT = "production" if env_choice == "2" else "dev"
print(f"Selected environment: {ENVIRONMENT}")

# Common settings
SECRET_KEY = input_with_default("Django Secret Key", generate_secret_key())
ALLOWED_HOSTS = input_with_default("Allowed Hosts (comma separated)", "localhost,127.0.0.1")
CORS_ALLOWED_ORIGINS = input_with_default("CORS Allowed Origins (comma separated)", "http://localhost:3000,http://127.0.0.1:3000")

# Development-specific settings
DEBUG = input_with_default("Debug Mode (True/False)", "True" if ENVIRONMENT == "dev" else "False")
POSTGRES_DB_DEV = input_with_default("Development PostgreSQL Database Name", "powerBI")
POSTGRES_USER_DEV = input_with_default("Development PostgreSQL User", "postgres")
POSTGRES_PASSWORD_DEV = input_with_default("Development PostgreSQL Password", "password")
POSTGRES_HOST_DEV = input_with_default("Development PostgreSQL Host", "host.docker.internal")
POSTGRES_PORT_DEV = input_with_default("Development PostgreSQL Port", "5432")
MONGO_DB_DEV = input_with_default("Development MongoDB Database Name", "powerBI")
MONGO_HOST_DEV = input_with_default("Development MongoDB Host", "host.docker.internal")
MONGO_PORT_DEV = input_with_default("Development MongoDB Port", "27017")
REDIS_HOST_DEV = input_with_default("Development Redis Host", "localhost")
REDIS_PORT_DEV = input_with_default("Development Redis Port", "6379")

# Production-specific settings
POSTGRES_DB_PROD = input_with_default("Production PostgreSQL Database Name", "form_handler_prod")
POSTGRES_USER_PROD = input_with_default("Production PostgreSQL User", "postgres")
POSTGRES_PASSWORD_PROD = input_with_default("Production PostgreSQL Password", "password")
POSTGRES_HOST_PROD = input_with_default("Production PostgreSQL Host", "host.docker.internal")
POSTGRES_PORT_PROD = input_with_default("Production PostgreSQL Port", "5432")
MONGO_DB_PROD = input_with_default("Production MongoDB Database Name", "form_handler_prod")
MONGO_HOST_PROD = input_with_default("Production MongoDB Host", "host.docker.internal")
MONGO_PORT_PROD = input_with_default("Production MongoDB Port", "27017")
REDIS_HOST_PROD = input_with_default("Production Redis Host", "host.docker.internal")
REDIS_PORT_PROD = input_with_default("Production Redis Port", "6379")
SECURE_SSL_REDIRECT = input_with_default("Production Secure SSL Redirect (True/False)", "True")
SESSION_COOKIE_SECURE = input_with_default("Production Session Cookie Secure (True/False)", "True")
CSRF_COOKIE_SECURE = input_with_default("Production CSRF Cookie Secure (True/False)", "True")

# Write to .env file
with open(".env", "w") as f:
    f.write("# Django Settings\n")
    f.write(f"ENVIRONMENT={ENVIRONMENT}\n")
    f.write(f"SECRET_KEY={SECRET_KEY}\n")
    f.write(f"ALLOWED_HOSTS={ALLOWED_HOSTS}\n")
    f.write(f"CORS_ALLOWED_ORIGINS={CORS_ALLOWED_ORIGINS}\n\n")

    if ENVIRONMENT == "dev":
        f.write("# Development Settings\n")
        f.write(f"DEBUG={DEBUG}\n")
        f.write(f"POSTGRES_DB={POSTGRES_DB_DEV}\n")
        f.write(f"POSTGRES_USER={POSTGRES_USER_DEV}\n")
        f.write(f"POSTGRES_PASSWORD={POSTGRES_PASSWORD_DEV}\n")
        f.write(f"POSTGRES_HOST={POSTGRES_HOST_DEV}\n")
        f.write(f"POSTGRES_PORT={POSTGRES_PORT_DEV}\n")
        f.write(f"MONGO_DB={MONGO_DB_DEV}\n")
        f.write(f"MONGO_HOST={MONGO_HOST_DEV}\n")
        f.write(f"MONGO_PORT={MONGO_PORT_DEV}\n")
        f.write(f"REDIS_HOST={REDIS_HOST_DEV}\n")
        f.write(f"REDIS_PORT={REDIS_PORT_DEV}\n")
    else:
        f.write("# Production Settings\n")
        f.write(f"DEBUG={DEBUG}\n")
        f.write(f"POSTGRES_DB={POSTGRES_DB_PROD}\n")
        f.write(f"POSTGRES_USER={POSTGRES_USER_PROD}\n")
        f.write(f"POSTGRES_PASSWORD={POSTGRES_PASSWORD_PROD}\n")
        f.write(f"POSTGRES_HOST={POSTGRES_HOST_PROD}\n")
        f.write(f"POSTGRES_PORT={POSTGRES_PORT_PROD}\n")
        f.write(f"MONGO_DB={MONGO_DB_PROD}\n")
        f.write(f"MONGO_HOST={MONGO_HOST_PROD}\n")
        f.write(f"MONGO_PORT={MONGO_PORT_PROD}\n")
        f.write(f"REDIS_HOST={REDIS_HOST_PROD}\n")
        f.write(f"REDIS_PORT={REDIS_PORT_PROD}\n")
        f.write(f"SECURE_SSL_REDIRECT={SECURE_SSL_REDIRECT}\n")
        f.write(f"SESSION_COOKIE_SECURE={SESSION_COOKIE_SECURE}\n")
        f.write(f"CSRF_COOKIE_SECURE={CSRF_COOKIE_SECURE}\n")

print("\n✅ .env file created with your settings.\n")