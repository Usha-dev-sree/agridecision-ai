"""Create reference and farm schema tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-23

AgriDecision AI — Migration 0003
Tables: reference.agro_ecological_zone, reference.crop_variety,
        reference.pest_disease, reference.input_product,
        farm.farm_plot, farm.plot_boundary, farm.soil_profile,
        farm.crop_season, farm.iot_device
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision: str = "0003"
down_revision: str = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── reference.agro_ecological_zone ───────────────────────────────────
    op.create_table(
        "agro_ecological_zone",
        sa.Column("id",              UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("zone_code",       sa.String(20),      nullable=False),
        sa.Column("zone_name",       sa.String(100),     nullable=False),
        sa.Column("region",          sa.String(50),      nullable=False),
        sa.Column("state_codes",     sa.Text(),          nullable=False, server_default="{}"),
        sa.Column("rainfall_mm_avg", sa.Numeric(8, 2),   nullable=True),
        sa.Column("temp_avg_c",      sa.Numeric(5, 2),   nullable=True),
        sa.Column("soil_types",      sa.Text(),          nullable=True, server_default="{}"),
        sa.Column("geometry",        sa.Text(),          nullable=True),  # PostGIS geometry managed by raw SQL
        sa.Column("created_at",      sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("zone_code"),
        schema="reference",
    )
    # Cast state_codes and soil_types to PostgreSQL TEXT[]
    op.execute("ALTER TABLE reference.agro_ecological_zone ALTER COLUMN state_codes TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("ALTER TABLE reference.agro_ecological_zone ALTER COLUMN soil_types TYPE TEXT[] USING '{}'::TEXT[]")
    # Add PostGIS geometry column
    op.execute("ALTER TABLE reference.agro_ecological_zone DROP COLUMN geometry")
    op.execute("SELECT AddGeometryColumn('reference','agro_ecological_zone','geometry',4326,'MULTIPOLYGON',2)")
    op.create_index("idx_aez_zone_code", "agro_ecological_zone", ["zone_code"], schema="reference")
    op.execute("CREATE INDEX idx_aez_state_codes ON reference.agro_ecological_zone USING GIN (state_codes)")
    op.execute("CREATE INDEX idx_aez_geometry    ON reference.agro_ecological_zone USING GIST (geometry)")

    # ── reference.crop_variety ────────────────────────────────────────────
    op.create_table(
        "crop_variety",
        sa.Column("id",                   UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("crop_code",            sa.String(20),      nullable=False),
        sa.Column("variety_code",         sa.String(30),      nullable=False),
        sa.Column("common_name",          sa.String(100),     nullable=False),
        sa.Column("scientific_name",      sa.String(150),     nullable=True),
        sa.Column("local_names",          JSONB(),            nullable=False, server_default="{}"),
        sa.Column("season",               sa.Text(),          nullable=False),
        sa.Column("duration_days_min",    sa.SmallInteger(),  nullable=True),
        sa.Column("duration_days_max",    sa.SmallInteger(),  nullable=True),
        sa.Column("water_requirement_mm", sa.Numeric(8, 2),   nullable=True),
        sa.Column("nitrogen_kg_per_ha",   sa.Numeric(8, 2),   nullable=True),
        sa.Column("phosphorus_kg_per_ha", sa.Numeric(8, 2),   nullable=True),
        sa.Column("potassium_kg_per_ha",  sa.Numeric(8, 2),   nullable=True),
        sa.Column("suitable_aez_codes",   sa.Text(),          nullable=True, server_default="{}"),
        sa.Column("suitable_soil_types",  sa.Text(),          nullable=True, server_default="{}"),
        sa.Column("ph_min",               sa.Numeric(4, 2),   nullable=True),
        sa.Column("ph_max",               sa.Numeric(4, 2),   nullable=True),
        sa.Column("government_notified",  sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("msp_inr_per_quintal",  sa.Numeric(10, 2),  nullable=True),
        sa.Column("created_at",           sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",           sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("crop_code", "variety_code"),
        schema="reference",
    )
    op.execute("ALTER TABLE reference.crop_variety ALTER COLUMN season TYPE farm.crop_season_enum USING season::farm.crop_season_enum")
    op.execute("ALTER TABLE reference.crop_variety ALTER COLUMN suitable_aez_codes TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("ALTER TABLE reference.crop_variety ALTER COLUMN suitable_soil_types TYPE farm.texture_class_enum[] USING '{}'::farm.texture_class_enum[]")
    op.execute("ALTER TABLE reference.crop_variety ADD CONSTRAINT chk_ph_range CHECK (ph_min BETWEEN 0 AND 14 AND ph_max BETWEEN 0 AND 14)")
    op.create_index("idx_crop_code",       "crop_variety", ["crop_code"],  schema="reference")
    op.create_index("idx_crop_season",     "crop_variety", ["season"],     schema="reference")
    op.execute("CREATE INDEX idx_crop_aez_codes   ON reference.crop_variety USING GIN (suitable_aez_codes)")
    op.execute("CREATE INDEX idx_crop_local_names ON reference.crop_variety USING GIN (local_names jsonb_path_ops)")
    op.execute("CREATE TRIGGER trg_reference_crop_variety_updated_at BEFORE UPDATE ON reference.crop_variety FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── reference.pest_disease ────────────────────────────────────────────
    op.create_table(
        "pest_disease",
        sa.Column("id",                    UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("pest_code",             sa.String(30),      nullable=False),
        sa.Column("common_name",           sa.String(100),     nullable=False),
        sa.Column("scientific_name",       sa.String(150),     nullable=True),
        sa.Column("local_names",           JSONB(),            nullable=False, server_default="{}"),
        sa.Column("category",              sa.String(20),      nullable=False),
        sa.Column("affected_crops",        sa.Text(),          nullable=True, server_default="{}"),
        sa.Column("symptoms",              sa.Text(),          nullable=True),
        sa.Column("management_organic",    sa.Text(),          nullable=True),
        sa.Column("management_chemical",   JSONB(),            nullable=True, server_default="[]"),
        sa.Column("image_class_label",     sa.String(50),      nullable=True),
        sa.Column("created_at",            sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("pest_code"),
        schema="reference",
    )
    op.execute("ALTER TABLE reference.pest_disease ALTER COLUMN affected_crops TYPE TEXT[] USING '{}'::TEXT[]")
    op.execute("""ALTER TABLE reference.pest_disease ADD CONSTRAINT chk_pest_category
                  CHECK (category IN ('FUNGAL','BACTERIAL','VIRAL','INSECT','NEMATODE','WEED','NUTRIENT_DEFICIENCY','ABIOTIC'))""")
    op.create_index("idx_pest_code",     "pest_disease", ["pest_code"], schema="reference")
    op.create_index("idx_pest_category", "pest_disease", ["category"],  schema="reference")
    op.execute("CREATE INDEX idx_pest_crops ON reference.pest_disease USING GIN (affected_crops)")

    # ── reference.input_product ───────────────────────────────────────────
    op.create_table(
        "input_product",
        sa.Column("id",                 UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("product_code",       sa.String(30),      nullable=False),
        sa.Column("product_name",       sa.String(150),     nullable=False),
        sa.Column("manufacturer",       sa.String(100),     nullable=True),
        sa.Column("category",           sa.String(30),      nullable=False),
        sa.Column("active_ingredient",  sa.String(100),     nullable=True),
        sa.Column("formulation",        sa.String(50),      nullable=True),
        sa.Column("unit_of_measure",    sa.String(20),      nullable=False, server_default="KG"),
        sa.Column("mrp_inr",            sa.Numeric(10, 2),  nullable=True),
        sa.Column("is_organic",         sa.Boolean(),       nullable=False, server_default="false"),
        sa.Column("cib_registration_no",sa.String(50),      nullable=True),
        sa.Column("created_at",         sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("product_code"),
        schema="reference",
    )
    op.execute("""ALTER TABLE reference.input_product ADD CONSTRAINT chk_product_category
                  CHECK (category IN ('FERTILIZER','PESTICIDE','HERBICIDE','SEED','BIOSTIMULANT'))""")
    op.create_index("idx_input_category", "input_product", ["category"], schema="reference")

    # ── farm.farm_plot ────────────────────────────────────────────────────
    op.create_table(
        "farm_plot",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id",             UUID(as_uuid=True), nullable=False),
        sa.Column("plot_name",           sa.String(100),     nullable=False),
        sa.Column("area_hectares",       sa.Numeric(10, 4),  nullable=False),
        sa.Column("centroid_latitude",   sa.Numeric(10, 7),  nullable=False),
        sa.Column("centroid_longitude",  sa.Numeric(10, 7),  nullable=False),
        sa.Column("state_code",          sa.String(10),      nullable=False),
        sa.Column("district_name",       sa.String(100),     nullable=False),
        sa.Column("taluka_name",         sa.String(100),     nullable=True),
        sa.Column("village_name",        sa.String(100),     nullable=True),
        sa.Column("aez_zone_code",       sa.String(20),      nullable=True),
        sa.Column("irrigation_type",     sa.Text(),          nullable=False, server_default="RAINFED"),
        sa.Column("land_ownership",      sa.String(20),      nullable=True),
        sa.Column("is_active",           sa.Boolean(),       nullable=False, server_default="true"),
        sa.Column("created_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at",          sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"],       ["iam.user.id"],                             ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["aez_zone_code"], ["reference.agro_ecological_zone.zone_code"]),
        schema="farm",
    )
    op.execute("ALTER TABLE farm.farm_plot ALTER COLUMN irrigation_type TYPE farm.irrigation_type_enum USING irrigation_type::farm.irrigation_type_enum")
    op.execute("ALTER TABLE farm.farm_plot ADD CONSTRAINT chk_area_range CHECK (area_hectares > 0 AND area_hectares <= 10000)")
    op.execute("ALTER TABLE farm.farm_plot ADD CONSTRAINT chk_lat_range CHECK (centroid_latitude BETWEEN -90 AND 90)")
    op.execute("ALTER TABLE farm.farm_plot ADD CONSTRAINT chk_lon_range CHECK (centroid_longitude BETWEEN -180 AND 180)")
    op.execute("ALTER TABLE farm.farm_plot ADD CONSTRAINT chk_ownership CHECK (land_ownership IN ('OWNED','LEASED','SHARECROPPED'))")
    # Add generated centroid geometry column
    op.execute("SELECT AddGeometryColumn('farm','farm_plot','centroid_geom',4326,'POINT',2)")
    op.execute("CREATE INDEX idx_plot_user_id  ON farm.farm_plot (user_id)")
    op.execute("CREATE INDEX idx_plot_state    ON farm.farm_plot (state_code)")
    op.execute("CREATE INDEX idx_plot_aez      ON farm.farm_plot (aez_zone_code)")
    op.execute("CREATE INDEX idx_plot_centroid ON farm.farm_plot USING GIST (centroid_geom)")
    op.execute("CREATE INDEX idx_plot_active   ON farm.farm_plot (user_id, is_active) WHERE is_active = TRUE AND deleted_at IS NULL")
    op.execute("CREATE TRIGGER trg_farm_farm_plot_updated_at BEFORE UPDATE ON farm.farm_plot FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── farm.plot_boundary ────────────────────────────────────────────────
    op.create_table(
        "plot_boundary",
        sa.Column("id",               UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",     UUID(as_uuid=True), nullable=False),
        sa.Column("computed_area_ha", sa.Numeric(10, 4),  nullable=True),
        sa.Column("vertex_count",     sa.SmallInteger(),  nullable=False),
        sa.Column("source",           sa.String(30),      nullable=False, server_default="USER_DRAWN"),
        sa.Column("accuracy_meters",  sa.Numeric(8, 2),   nullable=True),
        sa.Column("created_at",       sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",       sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"], ["farm.farm_plot.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("farm_plot_id"),
        schema="farm",
    )
    # Add PostGIS boundary geometry column
    op.execute("SELECT AddGeometryColumn('farm','plot_boundary','boundary_geom',4326,'POLYGON',2)")
    op.execute("ALTER TABLE farm.plot_boundary ALTER COLUMN boundary_geom SET NOT NULL")
    op.execute("ALTER TABLE farm.plot_boundary ADD CONSTRAINT chk_vertex_count CHECK (vertex_count >= 3)")
    op.execute("ALTER TABLE farm.plot_boundary ADD CONSTRAINT chk_source CHECK (source IN ('USER_DRAWN','SATELLITE_DERIVED','GPS_SURVEY'))")
    op.execute("CREATE INDEX idx_boundary_plot_id ON farm.plot_boundary (farm_plot_id)")
    op.execute("CREATE INDEX idx_boundary_geom    ON farm.plot_boundary USING GIST (boundary_geom)")
    op.execute("CREATE TRIGGER trg_farm_plot_boundary_updated_at BEFORE UPDATE ON farm.plot_boundary FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── farm.soil_profile ─────────────────────────────────────────────────
    op.create_table(
        "soil_profile",
        sa.Column("id",                    UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",          UUID(as_uuid=True), nullable=False),
        sa.Column("data_source",           sa.Text(),          nullable=False, server_default="MODEL_ESTIMATED"),
        sa.Column("texture_class",         sa.Text(),          nullable=True),
        sa.Column("ph_value",              sa.Numeric(4, 2),   nullable=True),
        sa.Column("organic_carbon_pct",    sa.Numeric(6, 4),   nullable=True),
        sa.Column("nitrogen_kg_ha",        sa.Numeric(8, 2),   nullable=True),
        sa.Column("phosphorus_kg_ha",      sa.Numeric(8, 2),   nullable=True),
        sa.Column("potassium_kg_ha",       sa.Numeric(8, 2),   nullable=True),
        sa.Column("calcium_ppm",           sa.Numeric(8, 2),   nullable=True),
        sa.Column("magnesium_ppm",         sa.Numeric(8, 2),   nullable=True),
        sa.Column("sulfur_ppm",            sa.Numeric(8, 2),   nullable=True),
        sa.Column("zinc_ppm",              sa.Numeric(8, 2),   nullable=True),
        sa.Column("boron_ppm",             sa.Numeric(8, 2),   nullable=True),
        sa.Column("cec_meq",               sa.Numeric(8, 2),   nullable=True),
        sa.Column("field_capacity_pct",    sa.Numeric(5, 2),   nullable=True),
        sa.Column("wilting_point_pct",     sa.Numeric(5, 2),   nullable=True),
        sa.Column("bulk_density_g_cm3",    sa.Numeric(5, 3),   nullable=True),
        sa.Column("lab_test_date",         sa.Date(),          nullable=True),
        sa.Column("soil_health_card_no",   sa.String(30),      nullable=True),
        sa.Column("raw_lab_report_url",    sa.Text(),          nullable=True),
        sa.Column("created_at",            sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",            sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"], ["farm.farm_plot.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("farm_plot_id"),
        schema="farm",
    )
    op.execute("ALTER TABLE farm.soil_profile ALTER COLUMN data_source TYPE farm.soil_data_source_enum USING data_source::farm.soil_data_source_enum")
    op.execute("ALTER TABLE farm.soil_profile ALTER COLUMN texture_class TYPE farm.texture_class_enum USING texture_class::farm.texture_class_enum")
    op.execute("ALTER TABLE farm.soil_profile ADD CONSTRAINT chk_ph CHECK (ph_value BETWEEN 3.0 AND 11.0)")
    op.execute("ALTER TABLE farm.soil_profile ADD CONSTRAINT chk_wilting_lt_capacity CHECK (wilting_point_pct < field_capacity_pct OR wilting_point_pct IS NULL OR field_capacity_pct IS NULL)")
    op.execute("CREATE TRIGGER trg_farm_soil_profile_updated_at BEFORE UPDATE ON farm.soil_profile FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── farm.crop_season ──────────────────────────────────────────────────
    op.create_table(
        "crop_season",
        sa.Column("id",                    UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",          UUID(as_uuid=True), nullable=False),
        sa.Column("crop_code",             sa.String(20),      nullable=False),
        sa.Column("variety_code",          sa.String(30),      nullable=True),
        sa.Column("season_type",           sa.Text(),          nullable=False),
        sa.Column("season_year",           sa.SmallInteger(),  nullable=False),
        sa.Column("season_label",          sa.String(30),      nullable=False),
        sa.Column("sowing_date",           sa.Date(),          nullable=True),
        sa.Column("expected_harvest_date", sa.Date(),          nullable=True),
        sa.Column("actual_harvest_date",   sa.Date(),          nullable=True),
        sa.Column("status",                sa.Text(),          nullable=False, server_default="PLANNED"),
        sa.Column("target_yield_kg_ha",    sa.Numeric(10, 2),  nullable=True),
        sa.Column("actual_yield_kg_ha",    sa.Numeric(10, 2),  nullable=True),
        sa.Column("notes",                 sa.Text(),          nullable=True),
        sa.Column("created_at",            sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",            sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"], ["farm.farm_plot.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("farm_plot_id", "season_type", "season_year", name="uq_plot_season"),
        schema="farm",
    )
    op.execute("ALTER TABLE farm.crop_season ALTER COLUMN season_type TYPE farm.crop_season_enum USING season_type::farm.crop_season_enum")
    op.execute("ALTER TABLE farm.crop_season ALTER COLUMN status TYPE farm.season_status_enum USING status::farm.season_status_enum")
    op.execute("ALTER TABLE farm.crop_season ADD CONSTRAINT chk_season_year CHECK (season_year BETWEEN 2000 AND 2100)")
    op.execute("ALTER TABLE farm.crop_season ADD CONSTRAINT chk_harvest_after_sowing CHECK (actual_harvest_date >= sowing_date OR actual_harvest_date IS NULL)")
    op.create_index("idx_season_plot_id",  "crop_season", ["farm_plot_id"], schema="farm")
    op.create_index("idx_season_crop_code","crop_season", ["crop_code"],    schema="farm")
    op.create_index("idx_season_status",   "crop_season", ["status"],       schema="farm")
    op.execute("CREATE TRIGGER trg_farm_crop_season_updated_at BEFORE UPDATE ON farm.crop_season FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")

    # ── farm.iot_device ───────────────────────────────────────────────────
    op.create_table(
        "iot_device",
        sa.Column("id",                  UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("farm_plot_id",        UUID(as_uuid=True), nullable=False),
        sa.Column("user_id",             UUID(as_uuid=True), nullable=False),
        sa.Column("device_type",         sa.Text(),          nullable=False),
        sa.Column("device_status",       sa.Text(),          nullable=False, server_default="PROVISIONED"),
        sa.Column("serial_number",       sa.String(100),     nullable=False),
        sa.Column("firmware_version",    sa.String(30),      nullable=True),
        sa.Column("installation_date",   sa.Date(),          nullable=True),
        sa.Column("last_heartbeat_at",   sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("metadata",            JSONB(),            nullable=True, server_default="{}"),
        sa.Column("created_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at",          sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["farm_plot_id"], ["farm.farm_plot.id"],  ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"],      ["iam.user.id"],        ondelete="CASCADE"),
        sa.UniqueConstraint("serial_number"),
        schema="farm",
    )
    op.execute("ALTER TABLE farm.iot_device ALTER COLUMN device_type TYPE farm.device_type_enum USING device_type::farm.device_type_enum")
    op.execute("ALTER TABLE farm.iot_device ALTER COLUMN device_status TYPE farm.device_status_enum USING device_status::farm.device_status_enum")
    # Add location_geom PostGIS point
    op.execute("SELECT AddGeometryColumn('farm','iot_device','location_geom',4326,'POINT',2)")
    op.create_index("idx_device_plot_id",  "iot_device", ["farm_plot_id"],   schema="farm")
    op.create_index("idx_device_status",   "iot_device", ["device_status"],  schema="farm")
    op.create_index("idx_device_heartbeat","iot_device", ["last_heartbeat_at"], schema="farm")
    op.execute("CREATE TRIGGER trg_farm_iot_device_updated_at BEFORE UPDATE ON farm.iot_device FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()")


def downgrade() -> None:
    for table in ["iot_device", "crop_season", "soil_profile", "plot_boundary", "farm_plot"]:
        op.drop_table(table, schema="farm")
    for table in ["input_product", "pest_disease", "crop_variety", "agro_ecological_zone"]:
        op.drop_table(table, schema="reference")
