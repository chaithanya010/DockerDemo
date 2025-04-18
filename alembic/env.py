# alembic/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from dotenv import load_dotenv
load_dotenv()
print(f"\nDATABASE_URL: {os.getenv('DATABASE_URL')}")
# Add the 'app' directory to the Python path
# This allows alembic to import modules from 'app'
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Import your Base model and any specific models needed for metadata detection
from app.db.base import Base
# --->>> *** ADD THIS LINE TO IMPORT YOUR MODEL(S) *** <<<---
import app.models.employee  # Ensure models are imported so Base.metadata is populated

# Import settings if you centralize DB URL there (alternative to alembic.ini's %)
# from app.core.config import settings # Example if using Pydantic settings

# --- End of added block ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Modify this line ---
# Set the target metadata *after* models are imported
# Use the metadata from your Base model
target_metadata = Base.metadata
# target_metadata = None # Original line (make sure this is commented out or removed)

# --- End of modification ---

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """Return the database URL."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # If DATABASE_URL isn't set, try constructing from components
        # This adds robustness if .env loading fails but individual vars are set
        pg_user = os.getenv("POSTGRES_USER", "appuser")
        pg_pass = os.getenv("POSTGRES_PASSWORD", "apppassword")
        pg_host = os.getenv("POSTGRES_HOST", "db")
        pg_port = os.getenv("POSTGRES_PORT", "5432") # Use the internal port
        pg_db = os.getenv("POSTGRES_DB", "appdb")
        db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        # Still raise error if construction is impossible (though defaults make it unlikely)
        if not all([pg_user, pg_pass, pg_host, pg_port, pg_db]):
             raise ValueError("DATABASE_URL environment variable not set, and could not construct from components.")
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # --- Modify this block ---
    url = get_url() # Use our function to get the URL
    context.configure(
        url=url,
        target_metadata=target_metadata, # target_metadata should now be populated
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    # --- End of modification ---

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # --- Revised Block (Handles potential interpolation issue and uses correct URL) ---
    connectable_config = config.get_section(config.config_ini_section)
    connectable_config["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        connectable_config, # Use the modified dictionary
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # --- End of Revised Block ---

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata # target_metadata should now be populated
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()