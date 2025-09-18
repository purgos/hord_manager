from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from typing import TYPE_CHECKING
import os, sys

try:
    from alembic import context  # type: ignore
except Exception:  # pragma: no cover
    context = None  # type: ignore

# Add app path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.core.database import Base  # noqa: E402
from backend.app.models import player, gemstone, currency, gm, metal, art, business  # noqa: E402

__all__ = [
    "player",
    "gemstone",
    "currency",
    "gm",
    "metal",
    "art",
    "business",
]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
if context is None:  # Provide clear error if alembic missing when actually running migrations
    raise ImportError("Alembic is not installed. Install with 'pip install alembic' to run migrations.")

context_t = context  # narrow type for type checkers
config = context_t.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context_t.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context_t.begin_transaction():
        context_t.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(
        configuration,  # type: ignore[arg-type]
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context_t.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context_t.begin_transaction():
            context_t.run_migrations()

if context_t.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
