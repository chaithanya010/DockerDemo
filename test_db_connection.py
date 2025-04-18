import os
import sys
import sqlalchemy
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy import text  # Import text for literal SQL

# --- Configuration ---
# Option 1: Define URL directly (if running inside container network)
DATABASE_URL = "postgresql://appuser:apppassword@db:5432/appdb"

# Option 2: Load from .env (better practice, requires python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")
# if not DATABASE_URL:
#     print("Error: DATABASE_URL not found in environment/.env file.")
#     sys.exit(1)

# Option 3: URL for testing from HOST machine (if port 5432 is mapped in docker-compose)
DATABASE_URL_LOCAL = "postgresql://appuser:apppassword@localhost:5432/appdb"
# Use DATABASE_URL_LOCAL instead of DATABASE_URL below if running directly on host


print(f"Attempting to connect to: {DATABASE_URL_LOCAL}")
print("-" * 30)

engine = None  # Initialize engine variable
try:
    # Create the SQLAlchemy engine
    # connect_args can be used for SSL or other specific driver options if needed
    # echo=True prints SQL statements executed by SQLAlchemy (useful for debugging)
    engine = sqlalchemy.create_engine(DATABASE_URL_LOCAL, echo=False)

    # Try to establish a connection and execute a simple query
    # engine.connect() borrows a connection from the pool
    with engine.connect() as connection:
        print("Connection established. Executing test query (SELECT 1)...")

        # Execute a simple, non-destructive query to verify connection
        result = connection.execute(text("SELECT 1"))

        # Fetch the result to ensure the query actually ran
        value = result.scalar_one() # Gets the single value (1) from the first row

        print(f"Test query successful! Result: {value}")
        print("\n" + "=" * 30)
        print(">>> Database connection successful! <<<")
        print("=" * 30)


except OperationalError as e:
    # Handle specific connection errors (e.g., host not found, db doesn't exist, auth failed)
    print("\n" + "!" * 30)
    print(">>> Connection Error: Could not connect to the database. <<<")
    print(f"Details: {e}")
    print("!" * 30)
    print("\nTroubleshooting Tips:")
    print(f"- Is the PostgreSQL container ('db' service in docker-compose) running? Check with `docker ps`.")
    print(f"- Is this script running where it can resolve the hostname '{engine.url.host}'?")
    print("  (Usually means running inside another Docker container on the same network).")
    print(f"- Are the username ('{engine.url.username}'), password ('*****'), database ('{engine.url.database}'), "
          f"host ('{engine.url.host}'), and port ('{engine.url.port}') correct?")
    print("- Has the database finished its initial startup/initialization?")
    print("- Is there a firewall blocking the connection?")


except SQLAlchemyError as e:
    # Handle other potential SQLAlchemy errors during connection/query
    print("\n" + "!" * 30)
    print(">>> Database Error: An unexpected SQLAlchemy error occurred. <<<")
    print(f"Details: {e}")
    print("!" * 30)


except Exception as e:
    # Catch any other unexpected errors
    print("\n" + "!" * 30)
    print(f">>> An unexpected error occurred: {e} <<<")
    print("!" * 30)


finally:
    # Dispose of the engine's connection pool if the engine was created
    # This closes all idle connections in the pool.
    if engine:
        engine.dispose()
        print("-" * 30)
        print("Engine connection pool disposed.")