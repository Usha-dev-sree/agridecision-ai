"""Create advisory schema tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-23

AgriDecision AI — Migration 0004
Tables: advisory.crop_recommendation, advisory.recommendation_item,
        advisory.irrigation_schedule, advisory.fertilizer_plan,
        advisory.fertilizer_application, advisory.image_diagnosis_record,
        advisory.agronomist_assignment
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "0004"
down_revision: str = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── advisory.crop_recommendation ──────────────────────────────────────
    op.create_table(
        "crop_recommendation",
        sa.Column("id",                     UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",            UUID(as_uuid=True), nullable=False),
        sa.Column("crop_season_id",          UUID(as_uuid=True), nullable=True),
        sa.Column("season_label",            sa.String(30),      nullable=False),
        sa.Column("generated_at",            sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("model_version",           sa.String(30),      nullable=False),
        sa.Column("feature_vector_hash",     sa.String(64),      nullable=True),
        sa.Column("status",                  sa.Text(),          nullable=False, server_default="ACTIVE"),
        sa.Column("confidence_tier",         sa.Text(),          nullable=False),
        sa.Column("explanation_text",        sa.Text(),          nullable=True),
        sa.Column("explanation_metadata",    JSONB(),            nullable=True, server_default="{}"),
        sa.Column("agronomist_override",     sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("agronomist_user_id",      UUID(as_uuid=True), nullable=True),
        sa.Column("agronomist_override_at",  sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("agronomist_notes",        sa.Text(),          nullable=True),
        sa.Column("created_at",              sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"],       ["farm.farm_plot.id"],      ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_season_id"],     ["farm.crop_season.id"],    ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["agronomist_user_id"], ["iam.user.id"],            ondelete="SET NULL"),
        schema="advisory",
    )
    op.execute("ALTER TABLE advisory.crop_recommendation ALTER COLUMN status TYPE advisory.recommendation_status_enum USING status::advisory.recommendation_status_enum")
    op.execute("ALTER TABLE advisory.crop_recommendation ALTER COLUMN confidence_tier TYPE advisory.confidence_tier_enum USING confidence_tier::advisory.confidence_tier_enum")
    op.create_index("idx_rec_plot_id",     "crop_recommendation", ["farm_plot_id"],   schema="advisory")
    op.create_index("idx_rec_status",      "crop_recommendation", ["status"],         schema="advisory")
    op.create_index("idx_rec_model_ver",   "crop_recommendation", ["model_version"],  schema="advisory")
    op.execute("CREATE INDEX idx_rec_generated_at ON advisory.crop_recommendation (generated_at DESC)")

    # ── advisory.recommendation_item ──────────────────────────────────────
    op.create_table(
        "recommendation_item",
        sa.Column("id",                       UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("recommendation_id",        UUID(as_uuid=True), nullable=False),
        sa.Column("rank",                     sa.SmallInteger(),  nullable=False),
        sa.Column("crop_code",                sa.String(20),      nullable=False),
        sa.Column("variety_code",             sa.String(30),      nullable=True),
        sa.Column("probability_score",        sa.Numeric(5, 4),   nullable=False),
        sa.Column("expected_yield_kg_ha",     sa.Numeric(10, 2),  nullable=True),
        sa.Column("expected_revenue_inr_ha",  sa.Numeric(12, 2),  nullable=True),
        sa.Column("risk_score",               sa.Numeric(5, 4),   nullable=True),
        sa.Column("intercrop_with",           sa.String(20),      nullable=True),
        sa.Column("feature_contributions",    JSONB(),            nullable=True, server_default="{}"),
        sa.Column("created_at",               sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["recommendation_id"], ["advisory.crop_recommendation.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("recommendation_id", "rank"),
        schema="advisory",
    )
    op.execute("ALTER TABLE advisory.recommendation_item ADD CONSTRAINT chk_rank CHECK (rank BETWEEN 1 AND 10)")
    op.execute("ALTER TABLE advisory.recommendation_item ADD CONSTRAINT chk_probability CHECK (probability_score BETWEEN 0 AND 1)")
    op.execute("ALTER TABLE advisory.recommendation_item ADD CONSTRAINT chk_risk CHECK (risk_score BETWEEN 0 AND 1 OR risk_score IS NULL)")
    op.create_index("idx_rec_item_rec_id", "recommendation_item", ["recommendation_id"], schema="advisory")
    op.create_index("idx_rec_item_crop",   "recommendation_item", ["crop_code"],         schema="advisory")

    # ── advisory.irrigation_schedule ──────────────────────────────────────
    op.create_table(
        "irrigation_schedule",
        sa.Column("id",                       UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",             UUID(as_uuid=True), nullable=False),
        sa.Column("crop_season_id",           UUID(as_uuid=True), nullable=True),
        sa.Column("schedule_date",            sa.Date(),          nullable=False),
        sa.Column("eto_mm",                   sa.Numeric(8, 3),   nullable=False),
        sa.Column("kc_coefficient",           sa.Numeric(5, 3),   nullable=False),
        sa.Column("etc_mm",                   sa.Numeric(8, 3),   nullable=False),
        sa.Column("effective_rainfall_mm",    sa.Numeric(8, 3),   nullable=False, server_default="0"),
        sa.Column("soil_moisture_deficit_mm", sa.Numeric(8, 3),   nullable=False),
        sa.Column("irrigation_required",      sa.Boolean(),       nullable=False),
        sa.Column("recommended_depth_mm",     sa.Numeric(8, 3),   nullable=True),
        sa.Column("drip_runtime_minutes",     sa.Numeric(8, 2),   nullable=True),
        sa.Column("irrigation_basis",         sa.Text(),          nullable=False, server_default="WEATHER_DRIVEN"),
        sa.Column("model_version",            sa.String(30),      nullable=True),
        sa.Column("created_at",               sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"],   ["farm.farm_plot.id"],   ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_season_id"], ["farm.crop_season.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("farm_plot_id", "schedule_date"),
        schema="advisory",
    )
    op.execute("ALTER TABLE advisory.irrigation_schedule ALTER COLUMN irrigation_basis TYPE advisory.irrigation_basis_enum USING irrigation_basis::advisory.irrigation_basis_enum")
    op.execute("CREATE INDEX idx_irr_plot_date ON advisory.irrigation_schedule (farm_plot_id, schedule_date DESC)")
    op.execute("CREATE INDEX idx_irr_required  ON advisory.irrigation_schedule (farm_plot_id, irrigation_required)")

    # ── advisory.fertilizer_plan ──────────────────────────────────────────
    op.create_table(
        "fertilizer_plan",
        sa.Column("id",                     UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",           UUID(as_uuid=True), nullable=False),
        sa.Column("crop_season_id",         UUID(as_uuid=True), nullable=False),
        sa.Column("crop_code",              sa.String(20),      nullable=False),
        sa.Column("model_version",          sa.String(30),      nullable=True),
        sa.Column("total_nitrogen_kg_ha",   sa.Numeric(8, 2),   nullable=False),
        sa.Column("total_phosphorus_kg_ha", sa.Numeric(8, 2),   nullable=False),
        sa.Column("total_potassium_kg_ha",  sa.Numeric(8, 2),   nullable=False),
        sa.Column("plan_metadata",          JSONB(),            nullable=True, server_default="{}"),
        sa.Column("generated_at",           sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"],   ["farm.farm_plot.id"],   ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_season_id"], ["farm.crop_season.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("farm_plot_id", "crop_season_id"),
        schema="advisory",
    )
    op.execute("ALTER TABLE advisory.fertilizer_plan ADD CONSTRAINT chk_n_positive CHECK (total_nitrogen_kg_ha >= 0)")
    op.execute("ALTER TABLE advisory.fertilizer_plan ADD CONSTRAINT chk_p_positive CHECK (total_phosphorus_kg_ha >= 0)")
    op.execute("ALTER TABLE advisory.fertilizer_plan ADD CONSTRAINT chk_k_positive CHECK (total_potassium_kg_ha >= 0)")
    op.create_index("idx_fert_plan_plot",   "fertilizer_plan", ["farm_plot_id"],   schema="advisory")
    op.create_index("idx_fert_plan_season", "fertilizer_plan", ["crop_season_id"], schema="advisory")

    # ── advisory.fertilizer_application ──────────────────────────────────
    op.create_table(
        "fertilizer_application",
        sa.Column("id",                     UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("fertilizer_plan_id",     UUID(as_uuid=True), nullable=False),
        sa.Column("prescription_type",      sa.Text(),          nullable=False),
        sa.Column("scheduled_date",         sa.Date(),          nullable=False),
        sa.Column("days_after_sowing",      sa.SmallInteger(),  nullable=False),
        sa.Column("crop_growth_stage",      sa.String(50),      nullable=True),
        sa.Column("product_code",           sa.String(30),      nullable=True),
        sa.Column("nitrogen_kg_ha",         sa.Numeric(8, 2),   nullable=True),
        sa.Column("phosphorus_kg_ha",       sa.Numeric(8, 2),   nullable=True),
        sa.Column("potassium_kg_ha",        sa.Numeric(8, 2),   nullable=True),
        sa.Column("recommended_dose_kg_ha", sa.Numeric(8, 2),   nullable=False),
        sa.Column("application_method",     sa.String(30),      nullable=True),
        sa.Column("is_applied",             sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("applied_at",             sa.Date(),          nullable=True),
        sa.Column("actual_dose_kg_ha",      sa.Numeric(8, 2),   nullable=True),
        sa.Column("notes",                  sa.Text(),          nullable=True),
        sa.Column("created_at",             sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["fertilizer_plan_id"], ["advisory.fertilizer_plan.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_code"], ["reference.input_product.product_code"]),
        schema="advisory",
    )
    op.execute("ALTER TABLE advisory.fertilizer_application ALTER COLUMN prescription_type TYPE advisory.prescription_type_enum USING prescription_type::advisory.prescription_type_enum")
    op.execute("ALTER TABLE advisory.fertilizer_application ADD CONSTRAINT chk_das CHECK (days_after_sowing >= 0)")
    op.create_index("idx_fert_app_plan",    "fertilizer_application", ["fertilizer_plan_id"], schema="advisory")
    op.create_index("idx_fert_app_date",    "fertilizer_application", ["scheduled_date"],     schema="advisory")
    op.execute("CREATE INDEX idx_fert_app_applied ON advisory.fertilizer_application (fertilizer_plan_id, is_applied)")

    # ── advisory.image_diagnosis_record ───────────────────────────────────
    op.create_table(
        "image_diagnosis_record",
        sa.Column("id",                      UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",            UUID(as_uuid=True), nullable=False),
        sa.Column("user_id",                 UUID(as_uuid=True), nullable=False),
        sa.Column("crop_season_id",          UUID(as_uuid=True), nullable=True),
        sa.Column("image_s3_key",            sa.Text(),          nullable=False),
        sa.Column("image_mime_type",         sa.String(30),      nullable=False, server_default="image/jpeg"),
        sa.Column("image_quality_score",     sa.Numeric(8, 4),   nullable=True),
        sa.Column("image_rejected",          sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("rejection_reason",        sa.String(50),      nullable=True),
        sa.Column("model_version",           sa.String(30),      nullable=True),
        sa.Column("ai_primary_class",        sa.String(50),      nullable=True),
        sa.Column("ai_primary_confidence",   sa.Numeric(5, 4),   nullable=True),
        sa.Column("ai_top_predictions",      JSONB(),            nullable=True, server_default="[]"),
        sa.Column("lime_explanation_url",    sa.Text(),          nullable=True),
        sa.Column("status",                  sa.Text(),          nullable=False, server_default="PENDING_AI"),
        sa.Column("assigned_agronomist_id",  UUID(as_uuid=True), nullable=True),
        sa.Column("verified_class",          sa.String(50),      nullable=True),
        sa.Column("verified_at",             sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("treatment_recommendation",sa.Text(),          nullable=True),
        sa.Column("created_at",              sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",              sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"],           ["farm.farm_plot.id"],   ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"],                ["iam.user.id"],         ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_season_id"],         ["farm.crop_season.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_agronomist_id"], ["iam.user.id"],         ondelete="SET NULL"),
        schema="advisory",
    )
    op.execute("ALTER TABLE advisory.image_diagnosis_record ALTER COLUMN status TYPE advisory.diagnosis_status_enum USING status::advisory.diagnosis_status_enum")
    op.execute("""ALTER TABLE advisory.image_diagnosis_record ADD CONSTRAINT chk_rejection_reason
                  CHECK (rejection_reason IN ('BLUR','UNDEREXPOSURE','OVEREXPOSURE','NO_LEAF_DETECTED','FILE_TOO_LARGE'))""")
    op.execute("ALTER TABLE advisory.image_diagnosis_record ADD CONSTRAINT chk_ai_confidence CHECK (ai_primary_confidence BETWEEN 0 AND 1 OR ai_primary_confidence IS NULL)")
    op.create_index("idx_diag_plot_id",    "image_diagnosis_record", ["farm_plot_id"],         schema="advisory")
    op.create_index("idx_diag_user_id",    "image_diagnosis_record", ["user_id"],              schema="advisory")
    op.create_index("idx_diag_status",     "image_diagnosis_record", ["status"],               schema="advisory")
    op.execute("CREATE INDEX idx_diag_agronomist ON advisory.image_diagnosis_record (assigned_agronomist_id) WHERE assigned_agronomist_id IS NOT NULL")
    op.execute("CREATE INDEX idx_diag_created    ON advisory.image_diagnosis_record (created_at DESC)")
    op.execute("CREATE TRIGGER trg_advisory_image_diagnosis_record_updated_at BEFORE UPDATE ON advisory.image_diagnosis_record FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── advisory.agronomist_assignment ────────────────────────────────────
    op.create_table(
        "agronomist_assignment",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farmer_user_id",      UUID(as_uuid=True), nullable=False),
        sa.Column("agronomist_user_id",  UUID(as_uuid=True), nullable=False),
        sa.Column("state_code",          sa.String(10),      nullable=False),
        sa.Column("cohort_name",         sa.String(100),     nullable=True),
        sa.Column("is_active",           sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("assigned_at",         sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("unassigned_at",       sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["farmer_user_id"],     ["iam.user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["agronomist_user_id"], ["iam.user.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("farmer_user_id", "agronomist_user_id", "is_active"),
        schema="advisory",
    )
    op.execute("CREATE INDEX idx_assign_farmer     ON advisory.agronomist_assignment (farmer_user_id, is_active)")
    op.execute("CREATE INDEX idx_assign_agronomist ON advisory.agronomist_assignment (agronomist_user_id, is_active)")


def downgrade() -> None:
    tables = [
        "agronomist_assignment", "image_diagnosis_record",
        "fertilizer_application", "fertilizer_plan",
        "irrigation_schedule", "recommendation_item", "crop_recommendation",
    ]
    for table in tables:
        op.drop_table(table, schema="advisory")
