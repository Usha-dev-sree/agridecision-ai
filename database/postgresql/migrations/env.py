"""Alembic migration environment configuration.

AgriDecision AI — database/postgresql/migrations/env.py
Supports async SQLAlchemy + PostgreSQL 16
"""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to alembic.ini values
# ---------------------------------------------------------------------------
config = context.config

# Bind the DATABASE_URL from environment (overrides alembic.ini sqlalchemy.url)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Set up Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import ALL ORM models so Alembic can detect schema changes
# ---------------------------------------------------------------------------
# NOTE: Import order must respect foreign key dependencies
from backend.common.database import Base  # noqa: F401 — shared declarative base

# IAM
from backend.services.user_service.src.models.user import User, UserProfile  # noqa: F401
from backend.services.user_service.src.models.session import UserSession  # noqa: F401
from backend.services.user_service.src.models.subscription import Subscription, PaymentRecord  # noqa: F401
from backend.services.user_service.src.models.consent import ConsentRecord  # noqa: F401

# Farm
from backend.services.farm_service.src.models.farm_plot import FarmPlot  # noqa: F401
from backend.services.farm_service.src.models.plot_boundary import PlotBoundary  # noqa: F401
from backend.services.farm_service.src.models.soil_profile import SoilProfile  # noqa: F401
from backend.services.farm_service.src.models.crop_season import CropSeason  # noqa: F401
from backend.services.farm_service.src.models.iot_device import IoTDevice  # noqa: F401

# Advisory
try:
    from backend.services.advisory_service.src.models.crop_recommendation import CropRecommendation  # noqa: F401
    from backend.services.advisory_service.src.models.irrigation_schedule import IrrigationSchedule  # noqa: F401
    from backend.services.advisory_service.src.models.image_diagnosis import ImageDiagnosisRecord  # noqa: F401
except ImportError:
    pass

# Market
try:
    from backend.services.market_service.src.models.market_price import CommodityPrice  # noqa: F401
except ImportError:
    pass

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Schema include/exclude filter — only migrate our custom schemas
# ---------------------------------------------------------------------------
MANAGED_SCHEMAS = {"iam", "farm", "advisory", "market", "platform", "reference", "timeseries"}


def include_object(obj, name, type_, reflected, compare_to):
    """Filter Alembic autogenerate to only manage our known schemas."""
    if type_ == "table":
        schema = getattr(obj, "schema", None) or "public"
        return schema in MANAGED_SCHEMAS
    return True


# ---------------------------------------------------------------------------
# Offline migration (without live DB connection)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        include_schemas=True,
        version_table_schema="platform",       # Store alembic_version in platform schema
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (with live async DB connection)
# ---------------------------------------------------------------------------
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        include_schemas=True,
        compare_type=True,                     # Detect column type changes
        compare_server_default=True,           # Detect server default changes
        version_table_schema="platform",
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        # Create managed schemas if they do not exist
        for schema in MANAGED_SCHEMAS:
            await connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
