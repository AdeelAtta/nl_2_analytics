from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from alembic import context
from app.core.config import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.postgres_dsn_sync)

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using sync engine."""
    connectable = context.config.attributes.get("connection", None)
    if connectable is None:
        connectable = create_engine(settings.postgres_dsn_sync, poolclass=pool.NullPool)
        with connectable.connect() as connection:
            do_run_migrations(connection)
        connectable.dispose()
    else:
        do_run_migrations(connectable)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
