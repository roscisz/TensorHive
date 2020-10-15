from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import click
import os
import subprocess

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Schema metadata
from tensorhive.database import Base
from tensorhive.models.User import User
from tensorhive.models.Reservation import Reservation
from tensorhive.models.RevokedToken import RevokedToken
from tensorhive.models.Role import Role
from tensorhive.models.Task import Task
target_metadata = Base.metadata

# Configuration
from tensorhive.config import DB
config.set_main_option('sqlalchemy.url', DB.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

if click.confirm('Would you like to generate a new diagram for this version of the database?', default=False):
    subprocess.Popen([os.path.join(os.path.dirname(__file__), 'generate_rdb.js'),
                      config.get_main_option("sqlalchemy.url")], stdout=subprocess.PIPE)
