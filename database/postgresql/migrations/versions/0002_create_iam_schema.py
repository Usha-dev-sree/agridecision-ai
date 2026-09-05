"""Create IAM schema tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-23

AgriDecision AI — Migration 0002
Tables: iam.user, iam.user_profile, iam.user_session,
        iam.consent_record, iam.subscription, iam.payment_record
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB

revision: str = "0002"
down_revision: str = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── iam.user ──────────────────────────────────────────────────────────
    op.create_table(
        "user",
        sa.Column("id",                              UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("phone_number",                    sa.String(15),      nullable=False),
        sa.Column("email",                           sa.String(320),     nullable=True),
        sa.Column("national_id_hash",                sa.String(64),      nullable=True),
        sa.Column("full_name",                       sa.String(200),     nullable=False),
        sa.Column("role",                            sa.Text(),          nullable=False, server_default="FARMER"),
        sa.Column("account_status",                  sa.Text(),          nullable=False, server_default="PENDING"),
        sa.Column("has_verified_phone",              sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("has_verified_agronomist_credential", sa.Boolean(),    nullable=False, server_default="false"),
        sa.Column("preferred_language",              sa.Text(),          nullable=False, server_default="en"),
        sa.Column("state_code",                      sa.String(10),      nullable=False),
        sa.Column("district_name",                   sa.String(100),     nullable=True),
        sa.Column("farmer_type",                     sa.Text(),          nullable=True),
        sa.Column("referral_code",                   sa.String(20),      nullable=True),
        sa.Column("referred_by_user_id",             UUID(as_uuid=True), nullable=True),
        sa.Column("last_login_at",                   sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at",                      sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",                      sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at",                      sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["referred_by_user_id"], ["iam.user.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("referral_code"),
        schema="iam",
    )
    # Cast text columns to proper enum types:
    # Must drop server defaults first, cast, then re-apply enum defaults.
    op.execute("ALTER TABLE iam.user ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE iam.user ALTER COLUMN role TYPE iam.user_role_enum USING role::iam.user_role_enum")
    op.execute("ALTER TABLE iam.user ALTER COLUMN role SET DEFAULT 'FARMER'")

    op.execute("ALTER TABLE iam.user ALTER COLUMN account_status DROP DEFAULT")
    op.execute("ALTER TABLE iam.user ALTER COLUMN account_status TYPE iam.account_status_enum USING account_status::iam.account_status_enum")
    op.execute("ALTER TABLE iam.user ALTER COLUMN account_status SET DEFAULT 'PENDING'")

    op.execute("ALTER TABLE iam.user ALTER COLUMN preferred_language DROP DEFAULT")
    op.execute("ALTER TABLE iam.user ALTER COLUMN preferred_language TYPE iam.language_code_enum USING preferred_language::iam.language_code_enum")
    op.execute("ALTER TABLE iam.user ALTER COLUMN preferred_language SET DEFAULT 'en'")

    op.execute("ALTER TABLE iam.user ALTER COLUMN farmer_type TYPE iam.farmer_type_enum USING farmer_type::iam.farmer_type_enum")

    # Indexes
    op.create_index("idx_user_phone",    "user", ["phone_number"],   schema="iam")
    op.create_index("idx_user_role",     "user", ["role"],           schema="iam")
    op.create_index("idx_user_status",   "user", ["account_status"], schema="iam")
    op.create_index("idx_user_state",    "user", ["state_code"],     schema="iam")
    op.execute("CREATE UNIQUE INDEX uq_phone_active ON iam.user (phone_number, deleted_at)")
    op.execute("CREATE INDEX idx_user_deleted  ON iam.user (deleted_at) WHERE deleted_at IS NULL")
    op.execute("CREATE INDEX idx_user_referral ON iam.user (referral_code) WHERE referral_code IS NOT NULL")

    # Auto-update trigger
    op.execute("CREATE TRIGGER trg_iam_user_updated_at BEFORE UPDATE ON iam.user FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── iam.user_profile ──────────────────────────────────────────────────
    op.create_table(
        "user_profile",
        sa.Column("id",                      UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",                 UUID(as_uuid=True), nullable=False),
        sa.Column("avatar_url",              sa.Text(),          nullable=True),
        sa.Column("bio",                     sa.Text(),          nullable=True),
        sa.Column("land_holding_ha",         sa.Numeric(10, 3),  nullable=True),
        sa.Column("years_of_farming",        sa.SmallInteger(),  nullable=True),
        sa.Column("education_level",         sa.String(50),      nullable=True),
        sa.Column("bank_account_hash",       sa.String(64),      nullable=True),
        sa.Column("agronomist_reg_no",       sa.String(50),      nullable=True),
        sa.Column("agronomist_state",        sa.String(10),      nullable=True),
        sa.Column("agronomist_verified_at",  sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at",              sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",              sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["iam.user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
        schema="iam",
    )
    op.execute("ALTER TABLE iam.user_profile ADD CONSTRAINT chk_land_holding CHECK (land_holding_ha >= 0)")
    op.execute("ALTER TABLE iam.user_profile ADD CONSTRAINT chk_years_farming CHECK (years_of_farming BETWEEN 0 AND 99)")
    op.execute("CREATE TRIGGER trg_iam_user_profile_updated_at BEFORE UPDATE ON iam.user_profile FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── iam.user_session ──────────────────────────────────────────────────
    op.create_table(
        "user_session",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",             UUID(as_uuid=True), nullable=False),
        sa.Column("refresh_token_hash",  sa.String(64),      nullable=False),
        sa.Column("device_fingerprint",  sa.String(200),     nullable=True),
        sa.Column("device_platform",     sa.String(20),      nullable=True),
        sa.Column("ip_address",          INET(),             nullable=True),
        sa.Column("user_agent",          sa.Text(),          nullable=True),
        sa.Column("is_active",           sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("expires_at",          sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("last_used_at",        sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["iam.user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("refresh_token_hash"),
        schema="iam",
    )
    op.execute("ALTER TABLE iam.user_session ADD CONSTRAINT chk_device_platform CHECK (device_platform IN ('ANDROID','IOS','WEB'))")
    op.create_index("idx_session_user_id", "user_session", ["user_id"],               schema="iam")
    op.create_index("idx_session_expires", "user_session", ["expires_at"],             schema="iam")
    op.execute("CREATE INDEX idx_session_active ON iam.user_session (user_id, is_active) WHERE is_active = TRUE")

    # ── iam.consent_record ────────────────────────────────────────────────
    op.create_table(
        "consent_record",
        sa.Column("id",           UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",      UUID(as_uuid=True), nullable=False),
        sa.Column("consent_type", sa.String(50),      nullable=False),
        sa.Column("version",      sa.String(20),      nullable=False),
        sa.Column("is_granted",   sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("granted_at",   sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at",   sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("ip_address",   INET(),             nullable=True),
        sa.Column("metadata",     JSONB(),            nullable=True, server_default="{}"),
        sa.Column("created_at",   sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["iam.user.id"], ondelete="CASCADE"),
        schema="iam",
    )
    op.create_index("idx_consent_user",    "consent_record", ["user_id"],                    schema="iam")
    op.create_index("idx_consent_type",    "consent_record", ["user_id", "consent_type"],    schema="iam")
    op.create_index("idx_consent_granted", "consent_record", ["user_id", "consent_type", "is_granted"], schema="iam")

    # ── iam.subscription ──────────────────────────────────────────────────
    op.create_table(
        "subscription",
        sa.Column("id",                         UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",                    UUID(as_uuid=True), nullable=False),
        sa.Column("plan",                       sa.Text(),          nullable=False, server_default="FREE"),
        sa.Column("max_farm_plots",             sa.SmallInteger(),  nullable=False, server_default="2"),
        sa.Column("max_diagnoses_per_month",    sa.SmallInteger(),  nullable=False, server_default="5"),
        sa.Column("has_market_access",          sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("has_voice_advisory",         sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("has_api_access",             sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("billing_period_start",       sa.Date(),          nullable=True),
        sa.Column("billing_period_end",         sa.Date(),          nullable=True),
        sa.Column("auto_renew",                 sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("created_at",                 sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",                 sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"], ["iam.user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id"),
        schema="iam",
    )
    op.execute("ALTER TABLE iam.subscription ALTER COLUMN plan DROP DEFAULT")
    op.execute("ALTER TABLE iam.subscription ALTER COLUMN plan TYPE iam.subscription_plan_enum USING plan::iam.subscription_plan_enum")
    op.execute("ALTER TABLE iam.subscription ALTER COLUMN plan SET DEFAULT 'FREE'")
    op.execute("ALTER TABLE iam.subscription ADD CONSTRAINT chk_billing_period CHECK (billing_period_end > billing_period_start)")
    op.create_index("idx_sub_user_id", "subscription", ["user_id"], schema="iam")
    op.create_index("idx_sub_plan",    "subscription", ["plan"],    schema="iam")
    op.execute("CREATE TRIGGER trg_iam_subscription_updated_at BEFORE UPDATE ON iam.subscription FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── iam.payment_record ────────────────────────────────────────────────
    op.create_table(
        "payment_record",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",             UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id",     UUID(as_uuid=True), nullable=False),
        sa.Column("gateway_order_id",    sa.String(100),     nullable=False),
        sa.Column("gateway_payment_id",  sa.String(100),     nullable=True),
        sa.Column("gateway_name",        sa.String(30),      nullable=False, server_default="RAZORPAY"),
        sa.Column("amount_inr",          sa.Numeric(10, 2),  nullable=False),
        sa.Column("currency",            sa.CHAR(3),         nullable=False, server_default="INR"),
        sa.Column("status",              sa.Text(),          nullable=False, server_default="PENDING"),
        sa.Column("plan_purchased",      sa.Text(),          nullable=False),
        sa.Column("idempotency_key",     UUID(as_uuid=True), nullable=False),
        sa.Column("gateway_response",    JSONB(),            nullable=True, server_default="{}"),
        sa.Column("paid_at",             sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["user_id"],         ["iam.user.id"],         ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subscription_id"], ["iam.subscription.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("gateway_order_id"),
        sa.UniqueConstraint("idempotency_key"),
        schema="iam",
    )
    op.execute("ALTER TABLE iam.payment_record ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE iam.payment_record ALTER COLUMN status TYPE iam.payment_status_enum USING status::iam.payment_status_enum")
    op.execute("ALTER TABLE iam.payment_record ALTER COLUMN status SET DEFAULT 'PENDING'")
    op.execute("ALTER TABLE iam.payment_record ALTER COLUMN plan_purchased TYPE iam.subscription_plan_enum USING plan_purchased::iam.subscription_plan_enum")
    op.execute("ALTER TABLE iam.payment_record ADD CONSTRAINT chk_amount_positive CHECK (amount_inr >= 0)")
    op.create_index("idx_payment_user_id",    "payment_record", ["user_id"],           schema="iam")
    op.create_index("idx_payment_status",     "payment_record", ["status"],            schema="iam")
    op.create_index("idx_payment_gateway_id", "payment_record", ["gateway_payment_id"],schema="iam")


def downgrade() -> None:
    for table in ["payment_record", "subscription", "consent_record", "user_session", "user_profile", "user"]:
        op.drop_table(table, schema="iam")
