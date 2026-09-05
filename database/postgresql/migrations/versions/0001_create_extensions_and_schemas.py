"""Create extensions and all schema namespaces.

Revision ID: 0001
Revises: None
Create Date: 2026-07-23

AgriDecision AI — Migration 0001
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Extensions ─────────────────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"postgis\"")
    op.execute("""
        DO $$ BEGIN
            CREATE EXTENSION IF NOT EXISTS "timescaledb";
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'timescaledb extension not available on this server, skipping.';
        END $$;
    """)
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pg_trgm\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"btree_gist\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\"")

    # ── Schemas ────────────────────────────────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS iam")
    op.execute("CREATE SCHEMA IF NOT EXISTS farm")
    op.execute("CREATE SCHEMA IF NOT EXISTS advisory")
    op.execute("CREATE SCHEMA IF NOT EXISTS market")
    op.execute("CREATE SCHEMA IF NOT EXISTS platform")
    op.execute("CREATE SCHEMA IF NOT EXISTS reference")
    op.execute("CREATE SCHEMA IF NOT EXISTS timeseries")

    # ── IAM Enum Types ─────────────────────────────────────────────────────
    op.execute("CREATE TYPE iam.account_status_enum AS ENUM ('PENDING','ACTIVE','SUSPENDED','DELETED')")
    op.execute("CREATE TYPE iam.farmer_type_enum AS ENUM ('SUBSISTENCE','SMALL_COMMERCIAL','MEDIUM_COMMERCIAL','LARGE_COMMERCIAL')")
    op.execute("CREATE TYPE iam.user_role_enum AS ENUM ('FARMER','AGRONOMIST','ENTERPRISE_USER','PLATFORM_ADMIN','RESEARCHER')")
    op.execute("CREATE TYPE iam.subscription_plan_enum AS ENUM ('FREE','SILVER','GOLD','PLATINUM','ENTERPRISE')")
    op.execute("CREATE TYPE iam.payment_status_enum AS ENUM ('PENDING','SUCCESS','FAILED','REFUNDED')")
    op.execute("CREATE TYPE iam.language_code_enum AS ENUM ('en','hi','mr','te','ta','kn','pa','gu','bn','or')")

    # ── Farm Enum Types ────────────────────────────────────────────────────
    op.execute("CREATE TYPE farm.soil_data_source_enum AS ENUM ('LAB_TESTED','USER_ENTERED','MODEL_ESTIMATED','SOILGRIDS_API')")
    op.execute("""CREATE TYPE farm.texture_class_enum AS ENUM (
        'SANDY','LOAMY_SAND','SANDY_LOAM','LOAM','SILT_LOAM','SILT',
        'CLAY_LOAM','SANDY_CLAY_LOAM','SILTY_CLAY_LOAM','SANDY_CLAY','SILTY_CLAY','CLAY')""")
    op.execute("CREATE TYPE farm.irrigation_type_enum AS ENUM ('RAINFED','CANAL','BOREWELL','DRIP','SPRINKLER','FLOOD')")
    op.execute("CREATE TYPE farm.crop_season_enum AS ENUM ('KHARIF','RABI','ZAID','ANNUAL','PERENNIAL')")
    op.execute("CREATE TYPE farm.season_status_enum AS ENUM ('PLANNED','ACTIVE','HARVESTED','ABANDONED')")
    op.execute("CREATE TYPE farm.device_type_enum AS ENUM ('SOIL_MOISTURE_SENSOR','WEATHER_STATION','DRONE_CONTROLLER','IRRIGATION_CONTROLLER','GENERIC_IOT')")
    op.execute("CREATE TYPE farm.device_status_enum AS ENUM ('PROVISIONED','ACTIVE','OFFLINE','DECOMMISSIONED')")

    # ── Advisory Enum Types ────────────────────────────────────────────────
    op.execute("CREATE TYPE advisory.recommendation_status_enum AS ENUM ('DRAFT','ACTIVE','SUPERSEDED','ARCHIVED')")
    op.execute("CREATE TYPE advisory.confidence_tier_enum AS ENUM ('HIGH','MEDIUM','LOW','INSUFFICIENT_DATA')")
    op.execute("CREATE TYPE advisory.irrigation_basis_enum AS ENUM ('WEATHER_DRIVEN','SENSOR_DRIVEN','SCHEDULE_DRIVEN','MANUAL')")
    op.execute("CREATE TYPE advisory.diagnosis_status_enum AS ENUM ('PENDING_AI','AI_COMPLETE','PENDING_REVIEW','AGRONOMIST_VERIFIED','DISPUTED','CLOSED')")
    op.execute("CREATE TYPE advisory.prescription_type_enum AS ENUM ('BASAL','TOP_DRESSING_1','TOP_DRESSING_2','FOLIAR_SPRAY','SOIL_AMENDMENT')")

    # ── Market Enum Types ──────────────────────────────────────────────────
    op.execute("CREATE TYPE market.forecast_horizon_enum AS ENUM ('D7','D30','D60','D90')")
    op.execute("CREATE TYPE market.referral_status_enum AS ENUM ('INITIATED','SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED','DISBURSED')")
    op.execute("CREATE TYPE market.product_type_enum AS ENUM ('KISAN_CREDIT_CARD','TERM_LOAN','CROP_INSURANCE','WEATHER_INSURANCE','LIVESTOCK_INSURANCE')")

    # ── Platform Enum Types ────────────────────────────────────────────────
    op.execute("CREATE TYPE platform.event_category_enum AS ENUM ('AUTH','ADMIN','DATA','AI_MODEL','SECURITY','BILLING')")
    op.execute("CREATE TYPE platform.webhook_status_enum AS ENUM ('PENDING','DELIVERED','FAILED','RETRYING')")
    op.execute("CREATE TYPE platform.config_data_type_enum AS ENUM ('STRING','INTEGER','BOOLEAN','NUMERIC','JSON')")

    # ── updated_at auto-trigger function ──────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)


def downgrade() -> None:
    # Drop enum types in reverse dependency order
    for enum in [
        "platform.config_data_type_enum", "platform.webhook_status_enum", "platform.event_category_enum",
        "market.product_type_enum", "market.referral_status_enum", "market.forecast_horizon_enum",
        "advisory.prescription_type_enum", "advisory.diagnosis_status_enum",
        "advisory.irrigation_basis_enum", "advisory.confidence_tier_enum", "advisory.recommendation_status_enum",
        "farm.device_status_enum", "farm.device_type_enum", "farm.season_status_enum",
        "farm.crop_season_enum", "farm.irrigation_type_enum", "farm.texture_class_enum",
        "farm.soil_data_source_enum", "iam.language_code_enum", "iam.payment_status_enum",
        "iam.subscription_plan_enum", "iam.user_role_enum", "iam.farmer_type_enum",
        "iam.account_status_enum",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum} CASCADE")

    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column CASCADE")

    for schema in ["timeseries", "reference", "platform", "market", "advisory", "farm", "iam"]:
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
