"""Generate initial Alembic migration."""

import asyncio
from alembic.config import Config
from alembic import command

from app.database.database import Base
from app.models import *  # noqa: F401, F403


def generate_migration():
    """Generate initial migration."""
    alembic_cfg = Config("alembic.ini")

    # Generate migration
    command.revision(alembic_cfg, autogenerate=True, message="initial_schema")

    # Apply migration
    command.upgrade(alembic_cfg, "head")

    print("Migration generated and applied successfully!")


if __name__ == "__main__":
    generate_migration()
