"""Create market and platform schema tables.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-23

AgriDecision AI — Migration 0005
Tables: market.mandi_profile, market.commodity_price (partitioned),
        market.price_forecast, market.financial_referral,
        platform.system_config, platform.audit_log (partitioned),
        platform.api_key, platform.webhook_config,
        platform.webhook_delivery_log (partitioned)
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ARRAY

revision: str = "0005"
down_revision: str = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── market.mandi_profile ──────────────────────────────────────────────
    op.create_table(
        "mandi_profile",
        sa.Column("id",             UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("mandi_code",     sa.String(20),      nullable=False),
        sa.Column("mandi_name",     sa.String(100),     nullable=False),
        sa.Column("state_code",     sa.String(10),      nullable=False),
        sa.Column("district_name",  sa.String(100),     nullable=False),
        sa.Column("market_type",    sa.String(30),      nullable=True),
        sa.Column("contact_phone",  sa.String(15),      nullable=True),
        sa.Column("operating_days", sa.Text(),          nullable=True, server_default="{}"),
        sa.Column("primary_crops",  sa.Text(),          nullable=True, server_default="{}"),
        sa.Column("is_active",      sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("created_at",     sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",     sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("mandi_code"),
        schema="market",
    )
    op.execute("ALTER TABLE market.mandi_profile ALTER COLUMN operating_days TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("ALTER TABLE market.mandi_profile ALTER COLUMN primary_crops TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("ALTER TABLE market.mandi_profile ADD CONSTRAINT chk_market_type CHECK (market_type IN ('APMC','PRIVATE','COOPERATIVE','DIRECT_MARKETING'))")
    op.execute("SELECT AddGeometryColumn('market','mandi_profile','location_geom',4326,'POINT',2)")
    op.create_index("idx_mandi_state",    "mandi_profile", ["state_code"], schema="market")
    op.execute("CREATE INDEX idx_mandi_location ON market.mandi_profile USING GIST (location_geom)")
    op.execute("CREATE INDEX idx_mandi_crops    ON market.mandi_profile USING GIN (primary_crops)")
    op.execute("CREATE TRIGGER trg_market_mandi_profile_updated_at BEFORE UPDATE ON market.mandi_profile FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── market.commodity_price (range-partitioned) ────────────────────────
    op.execute("""
        CREATE TABLE market.commodity_price (
            id              BIGSERIAL       NOT NULL,
            mandi_code      VARCHAR(20)     NOT NULL REFERENCES market.mandi_profile(mandi_code),
            crop_code       VARCHAR(20)     NOT NULL,
            variety_code    VARCHAR(30),
            price_date      DATE            NOT NULL,
            min_price_inr   NUMERIC(10,2)   NOT NULL CHECK (min_price_inr >= 0),
            modal_price_inr NUMERIC(10,2)   NOT NULL CHECK (modal_price_inr >= 0),
            max_price_inr   NUMERIC(10,2)   NOT NULL CHECK (max_price_inr >= 0),
            unit            VARCHAR(20)     NOT NULL DEFAULT 'QUINTAL',
            arrivals_tonnes NUMERIC(10,2),
            source          VARCHAR(30)     NOT NULL DEFAULT 'AGMARKNET',
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id, price_date),
            CONSTRAINT chk_price_range CHECK (min_price_inr <= modal_price_inr AND modal_price_inr <= max_price_inr)
        ) PARTITION BY RANGE (price_date)
    """)
    op.execute("CREATE TABLE market.commodity_price_2024 PARTITION OF market.commodity_price FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')")
    op.execute("CREATE TABLE market.commodity_price_2025 PARTITION OF market.commodity_price FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')")
    op.execute("CREATE TABLE market.commodity_price_2026 PARTITION OF market.commodity_price FOR VALUES FROM ('2026-01-01') TO ('2027-01-01')")
    op.execute("CREATE TABLE market.commodity_price_2027 PARTITION OF market.commodity_price FOR VALUES FROM ('2027-01-01') TO ('2028-01-01')")
    op.execute("CREATE INDEX idx_price_mandi_crop ON market.commodity_price (mandi_code, crop_code, price_date DESC)")
    op.execute("CREATE INDEX idx_price_date       ON market.commodity_price (price_date DESC)")
    op.execute("CREATE INDEX idx_price_crop       ON market.commodity_price (crop_code, price_date DESC)")

    # ── market.price_forecast ─────────────────────────────────────────────
    op.create_table(
        "price_forecast",
        sa.Column("id",                       UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("mandi_code",               sa.String(20),      nullable=False),
        sa.Column("crop_code",                sa.String(20),      nullable=False),
        sa.Column("forecast_generated_at",    sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("model_version",            sa.String(30),      nullable=False),
        sa.Column("horizon",                  sa.Text(),          nullable=False),
        sa.Column("target_date",              sa.Date(),          nullable=False),
        sa.Column("q10_price_inr",            sa.Numeric(10, 2),  nullable=False),
        sa.Column("q50_price_inr",            sa.Numeric(10, 2),  nullable=False),
        sa.Column("q90_price_inr",            sa.Numeric(10, 2),  nullable=False),
        sa.Column("prediction_interval_low",  sa.Numeric(10, 2),  nullable=True),
        sa.Column("prediction_interval_high", sa.Numeric(10, 2),  nullable=True),
        sa.Column("input_features_hash",      sa.String(64),      nullable=True),
        sa.Column("created_at",               sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["mandi_code"], ["market.mandi_profile.mandi_code"]),
        schema="market",
    )
    op.execute("ALTER TABLE market.price_forecast ALTER COLUMN horizon TYPE market.forecast_horizon_enum USING horizon::market.forecast_horizon_enum")
    op.execute("ALTER TABLE market.price_forecast ADD CONSTRAINT chk_forecast_quantiles CHECK (q10_price_inr <= q50_price_inr AND q50_price_inr <= q90_price_inr)")
    op.execute("CREATE INDEX idx_forecast_mandi  ON market.price_forecast (mandi_code, crop_code, target_date DESC)")
    op.execute("CREATE INDEX idx_forecast_target ON market.price_forecast (target_date DESC)")

    # ── market.financial_referral ─────────────────────────────────────────
    op.create_table(
        "financial_referral",
        sa.Column("id",                     UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",                UUID(as_uuid=True), nullable=False),
        sa.Column("product_type",           sa.Text(),          nullable=False),
        sa.Column("partner_name",           sa.String(100),     nullable=False),
        sa.Column("partner_application_id", sa.String(100),     nullable=True),
        sa.Column("amount_requested_inr",   sa.Numeric(14, 2),  nullable=True),
        sa.Column("status",                 sa.Text(),          nullable=False, server_default="INITIATED"),
        sa.Column("consent_record_id",      UUID(as_uuid=True), nullable=False),
        sa.Column("data_fields_shared",     sa.Text(),          nullable=False, server_default="{}"),
        sa.Column("partner_response",       JSONB(),            nullable=True, server_default="{}"),
        sa.Column("idempotency_key",        UUID(as_uuid=True), nullable=False),
        sa.Column("initiated_at",           sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",             sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"],          ["iam.user.id"],            ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["consent_record_id"],["iam.consent_record.id"]),
        sa.UniqueConstraint("idempotency_key"),
        schema="market",
    )
    op.execute("ALTER TABLE market.financial_referral ALTER COLUMN product_type TYPE market.product_type_enum USING product_type::market.product_type_enum")
    op.execute("ALTER TABLE market.financial_referral ALTER COLUMN status TYPE market.referral_status_enum USING status::market.referral_status_enum")
    op.execute("ALTER TABLE market.financial_referral ALTER COLUMN data_fields_shared TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("ALTER TABLE market.financial_referral ADD CONSTRAINT chk_amount_positive CHECK (amount_requested_inr > 0 OR amount_requested_inr IS NULL)")
    op.create_index("idx_referral_user_id", "financial_referral", ["user_id"],     schema="market")
    op.create_index("idx_referral_status",  "financial_referral", ["status"],      schema="market")
    op.create_index("idx_referral_partner", "financial_referral", ["partner_name"],schema="market")
    op.execute("CREATE TRIGGER trg_market_financial_referral_updated_at BEFORE UPDATE ON market.financial_referral FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── platform.system_config ────────────────────────────────────────────
    op.create_table(
        "system_config",
        sa.Column("id",               UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("config_key",       sa.String(100),     nullable=False),
        sa.Column("config_value",     sa.Text(),          nullable=False),
        sa.Column("data_type",        sa.Text(),          nullable=False, server_default="STRING"),
        sa.Column("description",      sa.Text(),          nullable=True),
        sa.Column("is_editable",      sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("last_modified_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at",       sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",       sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["last_modified_by"], ["iam.user.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("config_key"),
        schema="platform",
    )
    op.execute("ALTER TABLE platform.system_config ALTER COLUMN data_type TYPE platform.config_data_type_enum USING data_type::platform.config_data_type_enum")
    op.execute("CREATE TRIGGER trg_platform_system_config_updated_at BEFORE UPDATE ON platform.system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # Seed default config values
    op.execute("""
        INSERT INTO platform.system_config (config_key, config_value, data_type, description, is_editable) VALUES
        ('weather_sync_interval_mins',    '60',     'INTEGER', 'IMD/OpenWeather API ingestion interval (minutes)', TRUE),
        ('satellite_ndvi_scan_days',      '10',     'INTEGER', 'Sentinel-2 NDVI tile download frequency (days)', TRUE),
        ('free_tier_max_plots',           '2',      'INTEGER', 'Maximum farm plots for Free tier users', TRUE),
        ('image_blur_threshold',          '100.00', 'NUMERIC', 'Laplacian variance blur detection threshold', TRUE),
        ('model_fallback_mode',           'false',  'BOOLEAN', 'Force crop recommendations to rule-based fallback', TRUE),
        ('diagnosis_confidence_threshold','0.70',   'NUMERIC', 'AI confidence below which agronomist review triggered', TRUE),
        ('max_otp_attempts',              '3',      'INTEGER', 'Maximum failed OTP attempts before lockout', FALSE),
        ('otp_expiry_seconds',            '300',    'INTEGER', 'OTP TTL in Redis (seconds)', FALSE),
        ('kafka_retry_max_attempts',      '5',      'INTEGER', 'Maximum Kafka consumer retry attempts before DLQ', TRUE),
        ('agronomist_cohort_max_size',    '500',    'INTEGER', 'Maximum farmers per agronomist cohort', TRUE)
    """)

    # ── platform.audit_log (range-partitioned) ────────────────────────────
    op.execute("""
        CREATE TABLE platform.audit_log (
            id                   BIGSERIAL       NOT NULL,
            occurred_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            event_category       platform.event_category_enum NOT NULL,
            event_type           VARCHAR(80)     NOT NULL,
            actor_user_id        UUID            REFERENCES iam.user(id) ON DELETE SET NULL,
            actor_ip             INET,
            target_resource_id   UUID,
            target_resource_type VARCHAR(50),
            action_description   TEXT,
            before_state         JSONB,
            after_state          JSONB,
            metadata             JSONB           DEFAULT '{}',
            PRIMARY KEY (id, occurred_at)
        ) PARTITION BY RANGE (occurred_at)
    """)
    op.execute("CREATE TABLE platform.audit_log_2025 PARTITION OF platform.audit_log FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')")
    op.execute("CREATE TABLE platform.audit_log_2026 PARTITION OF platform.audit_log FOR VALUES FROM ('2026-01-01') TO ('2027-01-01')")
    op.execute("CREATE TABLE platform.audit_log_2027 PARTITION OF platform.audit_log FOR VALUES FROM ('2027-01-01') TO ('2028-01-01')")
    op.execute("CREATE INDEX idx_audit_occurred  ON platform.audit_log (occurred_at DESC)")
    op.execute("CREATE INDEX idx_audit_category  ON platform.audit_log (event_category, occurred_at DESC)")
    op.execute("CREATE INDEX idx_audit_actor     ON platform.audit_log (actor_user_id, occurred_at DESC)")
    op.execute("CREATE INDEX idx_audit_resource  ON platform.audit_log (target_resource_id, target_resource_type)")

    # ── platform.api_key ──────────────────────────────────────────────────
    op.create_table(
        "api_key",
        sa.Column("id",                UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("tenant_name",       sa.String(100),     nullable=False),
        sa.Column("tenant_type",       sa.String(30),      nullable=False),
        sa.Column("key_hash",          sa.String(128),     nullable=False),
        sa.Column("key_prefix",        sa.String(8),       nullable=False),
        sa.Column("scopes",            sa.Text(),          nullable=False, server_default="{}"),
        sa.Column("allowed_cidrs",     sa.Text(),          nullable=False, server_default="{}"),
        sa.Column("rate_limit_per_min",sa.Integer(),       nullable=False, server_default="1000"),
        sa.Column("is_active",         sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("last_used_at",      sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at",        sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by",        UUID(as_uuid=True), nullable=True),
        sa.Column("created_at",        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["created_by"], ["iam.user.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("key_hash"),
        schema="platform",
    )
    op.execute("ALTER TABLE platform.api_key ALTER COLUMN scopes TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("ALTER TABLE platform.api_key ALTER COLUMN allowed_cidrs TYPE INET[] USING '{}'::INET[]")
    op.execute("""ALTER TABLE platform.api_key ADD CONSTRAINT chk_tenant_type
                  CHECK (tenant_type IN ('ENTERPRISE','FINANCIAL_PARTNER','RESEARCH','GOVERNMENT'))""")
    op.create_index("idx_api_key_hash",   "api_key", ["key_hash"],    schema="platform")
    op.create_index("idx_api_key_prefix", "api_key", ["key_prefix"],  schema="platform")
    op.create_index("idx_api_key_tenant", "api_key", ["tenant_name"], schema="platform")
    op.execute("CREATE INDEX idx_api_key_active ON platform.api_key (is_active) WHERE is_active = TRUE")
    op.execute("CREATE TRIGGER trg_platform_api_key_updated_at BEFORE UPDATE ON platform.api_key FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── platform.webhook_config ───────────────────────────────────────────
    op.create_table(
        "webhook_config",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("api_key_id",          UUID(as_uuid=True), nullable=False),
        sa.Column("target_url",          sa.Text(),          nullable=False),
        sa.Column("signing_secret_hash", sa.String(128),     nullable=False),
        sa.Column("event_types",         sa.Text(),          nullable=False, server_default="{}"),
        sa.Column("is_active",           sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("max_retries",         sa.SmallInteger(),  nullable=False, server_default="5"),
        sa.Column("timeout_seconds",     sa.SmallInteger(),  nullable=False, server_default="30"),
        sa.Column("created_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["api_key_id"], ["platform.api_key.id"], ondelete="CASCADE"),
        schema="platform",
    )
    op.execute("ALTER TABLE platform.webhook_config ALTER COLUMN event_types TYPE TEXT[] USING '{}'::TEXT[]")
    op.create_index("idx_webhook_api_key", "webhook_config", ["api_key_id"], schema="platform")
    op.execute("CREATE INDEX idx_webhook_active ON platform.webhook_config (is_active) WHERE is_active = TRUE")
    op.execute("CREATE TRIGGER trg_platform_webhook_config_updated_at BEFORE UPDATE ON platform.webhook_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── platform.webhook_delivery_log (range-partitioned) ─────────────────
    op.execute("""
        CREATE TABLE platform.webhook_delivery_log (
            id                  BIGSERIAL       NOT NULL,
            delivered_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            webhook_config_id   UUID            NOT NULL REFERENCES platform.webhook_config(id) ON DELETE CASCADE,
            event_type          VARCHAR(80)     NOT NULL,
            idempotency_key     UUID            NOT NULL,
            payload_hash        VARCHAR(64)     NOT NULL,
            status              platform.webhook_status_enum NOT NULL DEFAULT 'PENDING',
            http_status_code    SMALLINT,
            attempt_number      SMALLINT        NOT NULL DEFAULT 1,
            response_body       TEXT,
            duration_ms         INTEGER,
            next_retry_at       TIMESTAMPTZ,
            PRIMARY KEY (id, delivered_at)
        ) PARTITION BY RANGE (delivered_at)
    """)
    op.execute("CREATE TABLE platform.webhook_delivery_log_2026 PARTITION OF platform.webhook_delivery_log FOR VALUES FROM ('2026-01-01') TO ('2027-01-01')")
    op.execute("CREATE TABLE platform.webhook_delivery_log_2027 PARTITION OF platform.webhook_delivery_log FOR VALUES FROM ('2027-01-01') TO ('2028-01-01')")
    op.execute("CREATE INDEX idx_wdl_webhook_config ON platform.webhook_delivery_log (webhook_config_id, delivered_at DESC)")
    op.execute("CREATE INDEX idx_wdl_status         ON platform.webhook_delivery_log (status, next_retry_at) WHERE status = 'RETRYING'")
    op.execute("CREATE INDEX idx_wdl_idempotency    ON platform.webhook_delivery_log (idempotency_key)")


def downgrade() -> None:
    # Platform
    for table in ["webhook_delivery_log", "webhook_config", "api_key", "audit_log", "system_config"]:
        op.execute(f"DROP TABLE IF EXISTS platform.{table} CASCADE")

    # Market
    for table in ["financial_referral", "price_forecast", "commodity_price", "mandi_profile"]:
        op.execute(f"DROP TABLE IF EXISTS market.{table} CASCADE")
