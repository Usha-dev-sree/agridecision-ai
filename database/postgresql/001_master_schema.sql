-- ============================================================
-- AgriDecision AI — Master Database DDL
-- PostgreSQL 16 + TimescaleDB 2.15 + PostGIS 3.4
-- ============================================================
-- Execution Order:
--   1. Extensions
--   2. Schemas
--   3. Enum Types
--   4. Reference Schema (lookup tables)
--   5. IAM Schema (identity & access)
--   6. Farm Schema (plots & soil)
--   7. Advisory Schema (recommendations)
--   8. Market Schema (prices & finance)
--   9. Platform Schema (admin & audit)
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- SECTION 1: EXTENSIONS
-- ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Trigram indexes for fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gist";      -- GiST indexes for exclusion constraints
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ────────────────────────────────────────────────────────────
-- SECTION 2: SCHEMAS
-- ────────────────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS iam;
CREATE SCHEMA IF NOT EXISTS farm;
CREATE SCHEMA IF NOT EXISTS advisory;
CREATE SCHEMA IF NOT EXISTS market;
CREATE SCHEMA IF NOT EXISTS platform;
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS timeseries;

-- ────────────────────────────────────────────────────────────
-- SECTION 3: ENUM TYPES
-- ────────────────────────────────────────────────────────────

-- IAM Enums
CREATE TYPE iam.account_status_enum   AS ENUM ('PENDING', 'ACTIVE', 'SUSPENDED', 'DELETED');
CREATE TYPE iam.farmer_type_enum      AS ENUM ('SUBSISTENCE', 'SMALL_COMMERCIAL', 'MEDIUM_COMMERCIAL', 'LARGE_COMMERCIAL');
CREATE TYPE iam.user_role_enum        AS ENUM ('FARMER', 'AGRONOMIST', 'ENTERPRISE_USER', 'PLATFORM_ADMIN', 'RESEARCHER');
CREATE TYPE iam.subscription_plan_enum AS ENUM ('FREE', 'SILVER', 'GOLD', 'PLATINUM', 'ENTERPRISE');
CREATE TYPE iam.payment_status_enum   AS ENUM ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED');
CREATE TYPE iam.language_code_enum    AS ENUM ('en', 'hi', 'mr', 'te', 'ta', 'kn', 'pa', 'gu', 'bn', 'or');

-- Farm Enums
CREATE TYPE farm.soil_data_source_enum   AS ENUM ('LAB_TESTED', 'USER_ENTERED', 'MODEL_ESTIMATED', 'SOILGRIDS_API');
CREATE TYPE farm.texture_class_enum      AS ENUM ('SANDY', 'LOAMY_SAND', 'SANDY_LOAM', 'LOAM', 'SILT_LOAM',
                                                   'SILT', 'CLAY_LOAM', 'SANDY_CLAY_LOAM', 'SILTY_CLAY_LOAM',
                                                   'SANDY_CLAY', 'SILTY_CLAY', 'CLAY');
CREATE TYPE farm.irrigation_type_enum    AS ENUM ('RAINFED', 'CANAL', 'BOREWELL', 'DRIP', 'SPRINKLER', 'FLOOD');
CREATE TYPE farm.crop_season_enum        AS ENUM ('KHARIF', 'RABI', 'ZAID', 'ANNUAL', 'PERENNIAL');
CREATE TYPE farm.season_status_enum      AS ENUM ('PLANNED', 'ACTIVE', 'HARVESTED', 'ABANDONED');
CREATE TYPE farm.device_type_enum        AS ENUM ('SOIL_MOISTURE_SENSOR', 'WEATHER_STATION', 'DRONE_CONTROLLER',
                                                   'IRRIGATION_CONTROLLER', 'GENERIC_IOT');
CREATE TYPE farm.device_status_enum      AS ENUM ('PROVISIONED', 'ACTIVE', 'OFFLINE', 'DECOMMISSIONED');

-- Advisory Enums
CREATE TYPE advisory.recommendation_status_enum AS ENUM ('DRAFT', 'ACTIVE', 'SUPERSEDED', 'ARCHIVED');
CREATE TYPE advisory.confidence_tier_enum       AS ENUM ('HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT_DATA');
CREATE TYPE advisory.irrigation_basis_enum      AS ENUM ('WEATHER_DRIVEN', 'SENSOR_DRIVEN', 'SCHEDULE_DRIVEN', 'MANUAL');
CREATE TYPE advisory.diagnosis_status_enum      AS ENUM ('PENDING_AI', 'AI_COMPLETE', 'PENDING_REVIEW',
                                                          'AGRONOMIST_VERIFIED', 'DISPUTED', 'CLOSED');
CREATE TYPE advisory.prescription_type_enum     AS ENUM ('BASAL', 'TOP_DRESSING_1', 'TOP_DRESSING_2',
                                                          'FOLIAR_SPRAY', 'SOIL_AMENDMENT');

-- Market Enums
CREATE TYPE market.forecast_horizon_enum  AS ENUM ('D7', 'D30', 'D60', 'D90');
CREATE TYPE market.referral_status_enum   AS ENUM ('INITIATED', 'SUBMITTED', 'UNDER_REVIEW',
                                                    'APPROVED', 'REJECTED', 'DISBURSED');
CREATE TYPE market.product_type_enum      AS ENUM ('KISAN_CREDIT_CARD', 'TERM_LOAN', 'CROP_INSURANCE',
                                                    'WEATHER_INSURANCE', 'LIVESTOCK_INSURANCE');

-- Platform Enums
CREATE TYPE platform.event_category_enum  AS ENUM ('AUTH', 'ADMIN', 'DATA', 'AI_MODEL', 'SECURITY', 'BILLING');
CREATE TYPE platform.webhook_status_enum  AS ENUM ('PENDING', 'DELIVERED', 'FAILED', 'RETRYING');
CREATE TYPE platform.config_data_type_enum AS ENUM ('STRING', 'INTEGER', 'BOOLEAN', 'NUMERIC', 'JSON');

-- ────────────────────────────────────────────────────────────
-- SECTION 4: REFERENCE SCHEMA (Lookup / Seed Tables)
-- ────────────────────────────────────────────────────────────

CREATE TABLE reference.agro_ecological_zone (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_code       VARCHAR(20)     NOT NULL UNIQUE,
    zone_name       VARCHAR(100)    NOT NULL,
    region          VARCHAR(50)     NOT NULL,
    state_codes     TEXT[]          NOT NULL DEFAULT '{}',
    rainfall_mm_avg NUMERIC(8,2),
    temp_avg_c      NUMERIC(5,2),
    soil_types      TEXT[]          DEFAULT '{}',
    geometry        GEOMETRY(MULTIPOLYGON, 4326),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_aez_zone_code      ON reference.agro_ecological_zone (zone_code);
CREATE INDEX idx_aez_state_codes    ON reference.agro_ecological_zone USING GIN (state_codes);
CREATE INDEX idx_aez_geometry       ON reference.agro_ecological_zone USING GIST (geometry);

COMMENT ON TABLE reference.agro_ecological_zone IS
    'FAO/ICAR Agro-Ecological Zone reference data. 127 zones covering India.';


CREATE TABLE reference.crop_variety (
    id                      UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_code               VARCHAR(20)     NOT NULL,         -- e.g. ZEA_MAYS
    variety_code            VARCHAR(30)     NOT NULL,         -- e.g. DKC_9144
    common_name             VARCHAR(100)    NOT NULL,
    scientific_name         VARCHAR(150),
    local_names             JSONB           NOT NULL DEFAULT '{}', -- {"hi":"मक्का","mr":"मका"}
    season                  farm.crop_season_enum NOT NULL,
    duration_days_min       SMALLINT        CHECK (duration_days_min > 0),
    duration_days_max       SMALLINT        CHECK (duration_days_max > 0),
    water_requirement_mm    NUMERIC(8,2),
    nitrogen_kg_per_ha      NUMERIC(8,2),
    phosphorus_kg_per_ha    NUMERIC(8,2),
    potassium_kg_per_ha     NUMERIC(8,2),
    suitable_aez_codes      TEXT[]          DEFAULT '{}',
    suitable_soil_types     farm.texture_class_enum[] DEFAULT '{}',
    ph_min                  NUMERIC(4,2)    CHECK (ph_min BETWEEN 0 AND 14),
    ph_max                  NUMERIC(4,2)    CHECK (ph_max BETWEEN 0 AND 14),
    government_notified     BOOLEAN         NOT NULL DEFAULT FALSE,
    msp_inr_per_quintal     NUMERIC(10,2),
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (crop_code, variety_code)
);

CREATE INDEX idx_crop_code          ON reference.crop_variety (crop_code);
CREATE INDEX idx_crop_season        ON reference.crop_variety (season);
CREATE INDEX idx_crop_aez_codes     ON reference.crop_variety USING GIN (suitable_aez_codes);
CREATE INDEX idx_crop_local_names   ON reference.crop_variety USING GIN (local_names jsonb_path_ops);

COMMENT ON TABLE reference.crop_variety IS
    'Government-notified and common crop varieties. 140+ records seeded from ICAR database.';


CREATE TABLE reference.pest_disease (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    pest_code           VARCHAR(30)     NOT NULL UNIQUE,
    common_name         VARCHAR(100)    NOT NULL,
    scientific_name     VARCHAR(150),
    local_names         JSONB           NOT NULL DEFAULT '{}',
    category            VARCHAR(20)     NOT NULL CHECK (category IN ('FUNGAL', 'BACTERIAL', 'VIRAL',
                                                                      'INSECT', 'NEMATODE', 'WEED',
                                                                      'NUTRIENT_DEFICIENCY', 'ABIOTIC')),
    affected_crops      TEXT[]          DEFAULT '{}',         -- crop_codes
    symptoms            TEXT,
    management_organic  TEXT,
    management_chemical JSONB           DEFAULT '[]',         -- [{active_ingredient, dose, waiting_period_days}]
    image_class_label   VARCHAR(50),                          -- Triton model class label
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pest_code          ON reference.pest_disease (pest_code);
CREATE INDEX idx_pest_category      ON reference.pest_disease (category);
CREATE INDEX idx_pest_crops         ON reference.pest_disease USING GIN (affected_crops);

COMMENT ON TABLE reference.pest_disease IS
    'Pest and disease knowledge base. Class labels match Triton disease_classifier_v2 output classes.';


CREATE TABLE reference.input_product (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_code        VARCHAR(30)     NOT NULL UNIQUE,
    product_name        VARCHAR(150)    NOT NULL,
    manufacturer        VARCHAR(100),
    category            VARCHAR(30)     NOT NULL CHECK (category IN ('FERTILIZER', 'PESTICIDE',
                                                                      'HERBICIDE', 'SEED', 'BIOSTIMULANT')),
    active_ingredient   VARCHAR(100),
    formulation         VARCHAR(50),
    unit_of_measure     VARCHAR(20)     NOT NULL DEFAULT 'KG',
    mrp_inr             NUMERIC(10,2),
    is_organic          BOOLEAN         NOT NULL DEFAULT FALSE,
    cib_registration_no VARCHAR(50),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_input_category  ON reference.input_product (category);

-- ────────────────────────────────────────────────────────────
-- SECTION 5: IAM SCHEMA
-- ────────────────────────────────────────────────────────────

CREATE TABLE iam.user (
    id                              UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number                    VARCHAR(15)                 NOT NULL,     -- E.164 format, CLE encrypted
    email                           VARCHAR(320),                             -- CLE encrypted
    national_id_hash                VARCHAR(64),                              -- SHA-256 of Aadhaar (irreversible)
    full_name                       VARCHAR(200)                NOT NULL,
    role                            iam.user_role_enum          NOT NULL DEFAULT 'FARMER',
    account_status                  iam.account_status_enum     NOT NULL DEFAULT 'PENDING',
    has_verified_phone              BOOLEAN                     NOT NULL DEFAULT FALSE,
    has_verified_agronomist_credential BOOLEAN                  NOT NULL DEFAULT FALSE,
    preferred_language              iam.language_code_enum      NOT NULL DEFAULT 'en',
    state_code                      VARCHAR(10)                 NOT NULL,     -- ISO 3166-2 e.g. IN-MH
    district_name                   VARCHAR(100),
    farmer_type                     iam.farmer_type_enum        DEFAULT 'SUBSISTENCE',
    referral_code                   VARCHAR(20)                 UNIQUE,
    referred_by_user_id             UUID                        REFERENCES iam.user(id) ON DELETE SET NULL,
    last_login_at                   TIMESTAMPTZ,
    created_at                      TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    deleted_at                      TIMESTAMPTZ,                              -- Soft delete for GDPR erasure
    CONSTRAINT uq_phone_active UNIQUE (phone_number, deleted_at)             -- Allow re-registration after deletion
);

CREATE INDEX idx_user_phone         ON iam.user (phone_number);
CREATE INDEX idx_user_role          ON iam.user (role);
CREATE INDEX idx_user_status        ON iam.user (account_status);
CREATE INDEX idx_user_state         ON iam.user (state_code);
CREATE INDEX idx_user_deleted       ON iam.user (deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_user_referral      ON iam.user (referral_code) WHERE referral_code IS NOT NULL;

COMMENT ON TABLE iam.user IS
    'Core user identity table. phone_number and email columns contain AES-256-GCM CLE ciphertext.';
COMMENT ON COLUMN iam.user.phone_number IS 'AES-256-GCM CLE encrypted. Format: v1:aes256:gcm:<base64_ciphertext>';
COMMENT ON COLUMN iam.user.email       IS 'AES-256-GCM CLE encrypted. Nullable.';


CREATE TABLE iam.user_profile (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID            NOT NULL UNIQUE REFERENCES iam.user(id) ON DELETE CASCADE,
    avatar_url          TEXT,
    bio                 TEXT,
    land_holding_ha     NUMERIC(10,3)   CHECK (land_holding_ha >= 0),
    years_of_farming    SMALLINT        CHECK (years_of_farming BETWEEN 0 AND 99),
    education_level     VARCHAR(50),
    bank_account_hash   VARCHAR(64),    -- SHA-256 of account number (for deduplication only)
    agronomist_reg_no   VARCHAR(50),    -- Government agronomist registration number
    agronomist_state    VARCHAR(10),    -- State of agronomist registration
    agronomist_verified_at TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE iam.user_profile IS 'Extended user profile data. One-to-one with iam.user.';


CREATE TABLE iam.user_session (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID            NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    refresh_token_hash  VARCHAR(64)     NOT NULL UNIQUE,  -- SHA-256 of refresh token
    device_fingerprint  VARCHAR(200),
    device_platform     VARCHAR(20)     CHECK (device_platform IN ('ANDROID', 'IOS', 'WEB')),
    ip_address          INET,
    user_agent          TEXT,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    expires_at          TIMESTAMPTZ     NOT NULL,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_used_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_session_user_id    ON iam.user_session (user_id);
CREATE INDEX idx_session_active     ON iam.user_session (user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_session_expires    ON iam.user_session (expires_at);

COMMENT ON TABLE iam.user_session IS
    'Active JWT refresh token registry. refresh_token_hash is SHA-256 of the raw token.';


CREATE TABLE iam.consent_record (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID            NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    consent_type        VARCHAR(50)     NOT NULL, -- e.g. PLATFORM_TOS, DATA_SHARING_BANK, RESEARCH_ANONYMIZED
    version             VARCHAR(20)     NOT NULL, -- Consent document version
    is_granted          BOOLEAN         NOT NULL DEFAULT FALSE,
    granted_at          TIMESTAMPTZ,
    revoked_at          TIMESTAMPTZ,
    ip_address          INET,
    metadata            JSONB           DEFAULT '{}', -- Partner name, data fields shared
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consent_user       ON iam.consent_record (user_id);
CREATE INDEX idx_consent_type       ON iam.consent_record (user_id, consent_type);
CREATE INDEX idx_consent_granted    ON iam.consent_record (user_id, consent_type, is_granted);

COMMENT ON TABLE iam.consent_record IS
    'Immutable consent audit trail. DPDP Act 2023 compliant. Records are never deleted.';


CREATE TABLE iam.subscription (
    id                      UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID                        NOT NULL UNIQUE REFERENCES iam.user(id) ON DELETE CASCADE,
    plan                    iam.subscription_plan_enum  NOT NULL DEFAULT 'FREE',
    max_farm_plots          SMALLINT                    NOT NULL DEFAULT 2,
    max_diagnoses_per_month SMALLINT                    NOT NULL DEFAULT 5,
    has_market_access       BOOLEAN                     NOT NULL DEFAULT FALSE,
    has_voice_advisory      BOOLEAN                     NOT NULL DEFAULT FALSE,
    has_api_access          BOOLEAN                     NOT NULL DEFAULT FALSE,
    billing_period_start    DATE,
    billing_period_end      DATE,
    auto_renew              BOOLEAN                     NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_billing_period CHECK (billing_period_end > billing_period_start)
);

CREATE INDEX idx_sub_user_id    ON iam.subscription (user_id);
CREATE INDEX idx_sub_plan       ON iam.subscription (plan);

COMMENT ON TABLE iam.subscription IS
    'User subscription tier and entitlement flags. Updated by payment webhook handler.';


CREATE TABLE iam.payment_record (
    id                  UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID                        NOT NULL REFERENCES iam.user(id) ON DELETE RESTRICT,
    subscription_id     UUID                        NOT NULL REFERENCES iam.subscription(id) ON DELETE RESTRICT,
    gateway_order_id    VARCHAR(100)                NOT NULL UNIQUE,
    gateway_payment_id  VARCHAR(100),
    gateway_name        VARCHAR(30)                 NOT NULL DEFAULT 'RAZORPAY',
    amount_inr          NUMERIC(10,2)               NOT NULL CHECK (amount_inr >= 0),
    currency            CHAR(3)                     NOT NULL DEFAULT 'INR',
    status              iam.payment_status_enum     NOT NULL DEFAULT 'PENDING',
    plan_purchased      iam.subscription_plan_enum  NOT NULL,
    idempotency_key     UUID                        NOT NULL UNIQUE,
    gateway_response    JSONB                       DEFAULT '{}',
    paid_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ                 NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_user_id    ON iam.payment_record (user_id);
CREATE INDEX idx_payment_status     ON iam.payment_record (status);
CREATE INDEX idx_payment_gateway_id ON iam.payment_record (gateway_payment_id);

-- ────────────────────────────────────────────────────────────
-- SECTION 6: FARM SCHEMA
-- ────────────────────────────────────────────────────────────

CREATE TABLE farm.farm_plot (
    id                      UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID                        NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    plot_name               VARCHAR(100)                NOT NULL,
    area_hectares           NUMERIC(10,4)               NOT NULL CHECK (area_hectares > 0 AND area_hectares <= 10000),
    centroid_latitude       NUMERIC(10,7)               NOT NULL CHECK (centroid_latitude BETWEEN -90 AND 90),
    centroid_longitude      NUMERIC(10,7)               NOT NULL CHECK (centroid_longitude BETWEEN -180 AND 180),
    centroid_geom           GEOMETRY(POINT, 4326)       GENERATED ALWAYS AS
                                (ST_SetSRID(ST_MakePoint(centroid_longitude, centroid_latitude), 4326)) STORED,
    state_code              VARCHAR(10)                 NOT NULL,
    district_name           VARCHAR(100)                NOT NULL,
    taluka_name             VARCHAR(100),
    village_name            VARCHAR(100),
    aez_zone_code           VARCHAR(20)                 REFERENCES reference.agro_ecological_zone(zone_code),
    irrigation_type         farm.irrigation_type_enum   NOT NULL DEFAULT 'RAINFED',
    land_ownership          VARCHAR(20)                 CHECK (land_ownership IN ('OWNED', 'LEASED', 'SHARECROPPED')),
    is_active               BOOLEAN                     NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    deleted_at              TIMESTAMPTZ
);

CREATE INDEX idx_plot_user_id       ON farm.farm_plot (user_id);
CREATE INDEX idx_plot_state         ON farm.farm_plot (state_code);
CREATE INDEX idx_plot_aez           ON farm.farm_plot (aez_zone_code);
CREATE INDEX idx_plot_centroid      ON farm.farm_plot USING GIST (centroid_geom);
CREATE INDEX idx_plot_active        ON farm.farm_plot (user_id, is_active) WHERE is_active = TRUE AND deleted_at IS NULL;

COMMENT ON TABLE farm.farm_plot IS
    'Core farm plot entity. centroid_geom is auto-computed from lat/lon for spatial queries.';


CREATE TABLE farm.plot_boundary (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id        UUID            NOT NULL UNIQUE REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    boundary_geom       GEOMETRY(POLYGON, 4326) NOT NULL,
    computed_area_ha    NUMERIC(10,4),           -- Computed by PostGIS ST_Area on insert
    vertex_count        SMALLINT        NOT NULL CHECK (vertex_count >= 3),
    source              VARCHAR(30)     NOT NULL DEFAULT 'USER_DRAWN'
                                        CHECK (source IN ('USER_DRAWN', 'SATELLITE_DERIVED', 'GPS_SURVEY')),
    accuracy_meters     NUMERIC(8,2),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_boundary_plot_id   ON farm.plot_boundary (farm_plot_id);
CREATE INDEX idx_boundary_geom      ON farm.plot_boundary USING GIST (boundary_geom);

COMMENT ON TABLE farm.plot_boundary IS
    'Polygon boundary geometry for farm plots. One-to-one with farm_plot. PostGIS GIST indexed.';


CREATE TABLE farm.soil_profile (
    id                      UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id            UUID                        NOT NULL UNIQUE REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    data_source             farm.soil_data_source_enum  NOT NULL DEFAULT 'MODEL_ESTIMATED',
    texture_class           farm.texture_class_enum,
    ph_value                NUMERIC(4,2)                CHECK (ph_value BETWEEN 3.0 AND 11.0),
    organic_carbon_pct      NUMERIC(6,4)                CHECK (organic_carbon_pct BETWEEN 0 AND 20),
    nitrogen_kg_ha          NUMERIC(8,2)                CHECK (nitrogen_kg_ha >= 0),
    phosphorus_kg_ha        NUMERIC(8,2)                CHECK (phosphorus_kg_ha >= 0),
    potassium_kg_ha         NUMERIC(8,2)                CHECK (potassium_kg_ha >= 0),
    calcium_ppm             NUMERIC(8,2),
    magnesium_ppm           NUMERIC(8,2),
    sulfur_ppm              NUMERIC(8,2),
    zinc_ppm                NUMERIC(8,2),
    boron_ppm               NUMERIC(8,2),
    cec_meq                 NUMERIC(8,2),               -- Cation Exchange Capacity
    field_capacity_pct      NUMERIC(5,2),               -- Soil moisture at field capacity
    wilting_point_pct       NUMERIC(5,2),               -- Permanent wilting point
    bulk_density_g_cm3      NUMERIC(5,3),
    lab_test_date           DATE,
    soil_health_card_no     VARCHAR(30),
    raw_lab_report_url      TEXT,
    created_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_wilting_lt_capacity CHECK (wilting_point_pct < field_capacity_pct OR wilting_point_pct IS NULL OR field_capacity_pct IS NULL)
);

COMMENT ON TABLE farm.soil_profile IS
    'Soil chemical and physical properties per plot. Single authoritative record per plot.';


CREATE TABLE farm.crop_season (
    id                  UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id        UUID                        NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    crop_code           VARCHAR(20)                 NOT NULL,
    variety_code        VARCHAR(30),
    season_type         farm.crop_season_enum       NOT NULL,
    season_year         SMALLINT                    NOT NULL CHECK (season_year BETWEEN 2000 AND 2100),
    season_label        VARCHAR(30)                 NOT NULL, -- e.g. "Kharif 2026"
    sowing_date         DATE,
    expected_harvest_date DATE,
    actual_harvest_date DATE,
    status              farm.season_status_enum     NOT NULL DEFAULT 'PLANNED',
    target_yield_kg_ha  NUMERIC(10,2),
    actual_yield_kg_ha  NUMERIC(10,2),
    notes               TEXT,
    created_at          TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_plot_season UNIQUE (farm_plot_id, season_type, season_year),
    CONSTRAINT chk_harvest_after_sowing CHECK (actual_harvest_date >= sowing_date OR actual_harvest_date IS NULL)
);

CREATE INDEX idx_season_plot_id     ON farm.crop_season (farm_plot_id);
CREATE INDEX idx_season_crop_code   ON farm.crop_season (crop_code);
CREATE INDEX idx_season_status      ON farm.crop_season (status);
CREATE INDEX idx_season_year        ON farm.crop_season (season_year);

COMMENT ON TABLE farm.crop_season IS
    'Crop season enrollment per plot. Unique per plot per season/year. Unique constraint prevents duplicate season rows.';


CREATE TABLE farm.iot_device (
    id                  UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id        UUID                        NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    user_id             UUID                        NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    device_type         farm.device_type_enum       NOT NULL,
    device_status       farm.device_status_enum     NOT NULL DEFAULT 'PROVISIONED',
    serial_number       VARCHAR(100)                NOT NULL UNIQUE,
    firmware_version    VARCHAR(30),
    installation_date   DATE,
    last_heartbeat_at   TIMESTAMPTZ,
    location_geom       GEOMETRY(POINT, 4326),      -- Specific device location within plot
    metadata            JSONB                       DEFAULT '{}',
    created_at          TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ                 NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_device_plot_id     ON farm.iot_device (farm_plot_id);
CREATE INDEX idx_device_status      ON farm.iot_device (device_status);
CREATE INDEX idx_device_heartbeat   ON farm.iot_device (last_heartbeat_at);

-- ────────────────────────────────────────────────────────────
-- SECTION 7: ADVISORY SCHEMA
-- ────────────────────────────────────────────────────────────

CREATE TABLE advisory.crop_recommendation (
    id                      UUID                                PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id            UUID                                NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    crop_season_id          UUID                                REFERENCES farm.crop_season(id) ON DELETE SET NULL,
    season_label            VARCHAR(30)                         NOT NULL,
    generated_at            TIMESTAMPTZ                         NOT NULL DEFAULT NOW(),
    model_version           VARCHAR(30)                         NOT NULL,     -- e.g. crop_selector_v3:3.1.0
    feature_vector_hash     VARCHAR(64),                                       -- SHA-256 of input feature vector
    status                  advisory.recommendation_status_enum NOT NULL DEFAULT 'ACTIVE',
    confidence_tier         advisory.confidence_tier_enum       NOT NULL,
    explanation_text        TEXT,                                              -- EAL generated human-readable text
    explanation_metadata    JSONB                               DEFAULT '{}', -- SHAP values, feature importances
    agronomist_override     BOOLEAN                             NOT NULL DEFAULT FALSE,
    agronomist_user_id      UUID                                REFERENCES iam.user(id) ON DELETE SET NULL,
    agronomist_override_at  TIMESTAMPTZ,
    agronomist_notes        TEXT,
    created_at              TIMESTAMPTZ                         NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rec_plot_id        ON advisory.crop_recommendation (farm_plot_id);
CREATE INDEX idx_rec_season         ON advisory.crop_recommendation (season_label);
CREATE INDEX idx_rec_status         ON advisory.crop_recommendation (status);
CREATE INDEX idx_rec_generated_at   ON advisory.crop_recommendation (generated_at DESC);
CREATE INDEX idx_rec_model_ver      ON advisory.crop_recommendation (model_version);

COMMENT ON TABLE advisory.crop_recommendation IS
    'Top-level crop recommendation record per plot per season. Contains EAL explanation metadata.';


CREATE TABLE advisory.recommendation_item (
    id                      UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    recommendation_id       UUID            NOT NULL REFERENCES advisory.crop_recommendation(id) ON DELETE CASCADE,
    rank                    SMALLINT        NOT NULL CHECK (rank BETWEEN 1 AND 10),
    crop_code               VARCHAR(20)     NOT NULL,
    variety_code            VARCHAR(30),
    probability_score       NUMERIC(5,4)    NOT NULL CHECK (probability_score BETWEEN 0 AND 1),
    expected_yield_kg_ha    NUMERIC(10,2),
    expected_revenue_inr_ha NUMERIC(12,2),
    risk_score              NUMERIC(5,4)    CHECK (risk_score BETWEEN 0 AND 1),
    intercrop_with          VARCHAR(20),    -- Companion crop code
    feature_contributions   JSONB           DEFAULT '{}',
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (recommendation_id, rank)
);

CREATE INDEX idx_rec_item_rec_id    ON advisory.recommendation_item (recommendation_id);
CREATE INDEX idx_rec_item_crop      ON advisory.recommendation_item (crop_code);


CREATE TABLE advisory.irrigation_schedule (
    id                      UUID                            PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id            UUID                            NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    crop_season_id          UUID                            REFERENCES farm.crop_season(id) ON DELETE SET NULL,
    schedule_date           DATE                            NOT NULL,
    eto_mm                  NUMERIC(8,3)                    NOT NULL,   -- Reference ETo (Penman-Monteith)
    kc_coefficient          NUMERIC(5,3)                    NOT NULL,   -- Crop coefficient
    etc_mm                  NUMERIC(8,3)                    NOT NULL,   -- Crop ETo = ETo * Kc
    effective_rainfall_mm   NUMERIC(8,3)                    NOT NULL DEFAULT 0,
    soil_moisture_deficit_mm NUMERIC(8,3)                   NOT NULL,
    irrigation_required     BOOLEAN                         NOT NULL,
    recommended_depth_mm    NUMERIC(8,3),                   -- Irrigation depth to apply
    drip_runtime_minutes    NUMERIC(8,2),                   -- Converted based on emitter specs
    irrigation_basis        advisory.irrigation_basis_enum  NOT NULL DEFAULT 'WEATHER_DRIVEN',
    model_version           VARCHAR(30),
    created_at              TIMESTAMPTZ                     NOT NULL DEFAULT NOW(),
    UNIQUE (farm_plot_id, schedule_date)
);

CREATE INDEX idx_irr_plot_date      ON advisory.irrigation_schedule (farm_plot_id, schedule_date DESC);
CREATE INDEX idx_irr_required       ON advisory.irrigation_schedule (farm_plot_id, irrigation_required);

COMMENT ON TABLE advisory.irrigation_schedule IS
    'Daily irrigation schedule computed by Penman-Monteith ETo model. One row per plot per day.';


CREATE TABLE advisory.fertilizer_plan (
    id                      UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id            UUID            NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    crop_season_id          UUID            NOT NULL REFERENCES farm.crop_season(id) ON DELETE CASCADE,
    crop_code               VARCHAR(20)     NOT NULL,
    model_version           VARCHAR(30),
    total_nitrogen_kg_ha    NUMERIC(8,2)    NOT NULL CHECK (total_nitrogen_kg_ha >= 0),
    total_phosphorus_kg_ha  NUMERIC(8,2)    NOT NULL CHECK (total_phosphorus_kg_ha >= 0),
    total_potassium_kg_ha   NUMERIC(8,2)    NOT NULL CHECK (total_potassium_kg_ha >= 0),
    plan_metadata           JSONB           DEFAULT '{}',
    generated_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (farm_plot_id, crop_season_id)
);

CREATE INDEX idx_fert_plan_plot     ON advisory.fertilizer_plan (farm_plot_id);
CREATE INDEX idx_fert_plan_season   ON advisory.fertilizer_plan (crop_season_id);


CREATE TABLE advisory.fertilizer_application (
    id                      UUID                            PRIMARY KEY DEFAULT uuid_generate_v4(),
    fertilizer_plan_id      UUID                            NOT NULL REFERENCES advisory.fertilizer_plan(id) ON DELETE CASCADE,
    prescription_type       advisory.prescription_type_enum NOT NULL,
    scheduled_date          DATE                            NOT NULL,
    days_after_sowing       SMALLINT                        NOT NULL CHECK (days_after_sowing >= 0),
    crop_growth_stage       VARCHAR(50),
    product_code            VARCHAR(30)                     REFERENCES reference.input_product(product_code),
    nitrogen_kg_ha          NUMERIC(8,2),
    phosphorus_kg_ha        NUMERIC(8,2),
    potassium_kg_ha         NUMERIC(8,2),
    recommended_dose_kg_ha  NUMERIC(8,2)                   NOT NULL,
    application_method      VARCHAR(30),
    is_applied              BOOLEAN                         NOT NULL DEFAULT FALSE,
    applied_at              DATE,
    actual_dose_kg_ha       NUMERIC(8,2),
    notes                   TEXT,
    created_at              TIMESTAMPTZ                     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fert_app_plan      ON advisory.fertilizer_application (fertilizer_plan_id);
CREATE INDEX idx_fert_app_date      ON advisory.fertilizer_application (scheduled_date);
CREATE INDEX idx_fert_app_applied   ON advisory.fertilizer_application (fertilizer_plan_id, is_applied);


CREATE TABLE advisory.image_diagnosis_record (
    id                      UUID                            PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_plot_id            UUID                            NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    user_id                 UUID                            NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    crop_season_id          UUID                            REFERENCES farm.crop_season(id) ON DELETE SET NULL,
    image_s3_key            TEXT                            NOT NULL,       -- S3 object key (not URL)
    image_mime_type         VARCHAR(30)                     NOT NULL DEFAULT 'image/jpeg',
    image_quality_score     NUMERIC(8,4),                                   -- Laplacian variance
    image_rejected          BOOLEAN                         NOT NULL DEFAULT FALSE,
    rejection_reason        VARCHAR(50)
                                CHECK (rejection_reason IN ('BLUR', 'UNDEREXPOSURE', 'OVEREXPOSURE',
                                                            'NO_LEAF_DETECTED', 'FILE_TOO_LARGE')),
    model_version           VARCHAR(30),
    ai_primary_class        VARCHAR(50),                                    -- Pest code from reference.pest_disease
    ai_primary_confidence   NUMERIC(5,4)                   CHECK (ai_primary_confidence BETWEEN 0 AND 1),
    ai_top_predictions      JSONB                           DEFAULT '[]',  -- [{class, confidence, lime_region_url}]
    lime_explanation_url    TEXT,                                           -- S3 key to LIME superpixel overlay
    status                  advisory.diagnosis_status_enum  NOT NULL DEFAULT 'PENDING_AI',
    assigned_agronomist_id  UUID                            REFERENCES iam.user(id) ON DELETE SET NULL,
    verified_class          VARCHAR(50),                                    -- Agronomist-confirmed pest code
    verified_at             TIMESTAMPTZ,
    treatment_recommendation TEXT,
    created_at              TIMESTAMPTZ                     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ                     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_diag_plot_id       ON advisory.image_diagnosis_record (farm_plot_id);
CREATE INDEX idx_diag_user_id       ON advisory.image_diagnosis_record (user_id);
CREATE INDEX idx_diag_status        ON advisory.image_diagnosis_record (status);
CREATE INDEX idx_diag_agronomist    ON advisory.image_diagnosis_record (assigned_agronomist_id) WHERE assigned_agronomist_id IS NOT NULL;
CREATE INDEX idx_diag_created       ON advisory.image_diagnosis_record (created_at DESC);

COMMENT ON TABLE advisory.image_diagnosis_record IS
    'Foliar photo upload, AI model inference result, and agronomist verification record.';


CREATE TABLE advisory.agronomist_assignment (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    farmer_user_id      UUID            NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    agronomist_user_id  UUID            NOT NULL REFERENCES iam.user(id) ON DELETE CASCADE,
    state_code          VARCHAR(10)     NOT NULL,
    cohort_name         VARCHAR(100),
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    assigned_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    unassigned_at       TIMESTAMPTZ,
    UNIQUE (farmer_user_id, agronomist_user_id, is_active)
);

CREATE INDEX idx_assign_farmer      ON advisory.agronomist_assignment (farmer_user_id, is_active);
CREATE INDEX idx_assign_agronomist  ON advisory.agronomist_assignment (agronomist_user_id, is_active);

-- ────────────────────────────────────────────────────────────
-- SECTION 8: MARKET SCHEMA
-- ────────────────────────────────────────────────────────────

CREATE TABLE market.mandi_profile (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    mandi_code          VARCHAR(20)     NOT NULL UNIQUE,  -- AGMARKNET market code
    mandi_name          VARCHAR(100)    NOT NULL,
    state_code          VARCHAR(10)     NOT NULL,
    district_name       VARCHAR(100)    NOT NULL,
    market_type         VARCHAR(30)     CHECK (market_type IN ('APMC', 'PRIVATE', 'COOPERATIVE', 'DIRECT_MARKETING')),
    location_geom       GEOMETRY(POINT, 4326),
    contact_phone       VARCHAR(15),
    operating_days      TEXT[],         -- e.g. ['MONDAY','TUESDAY','WEDNESDAY']
    primary_crops       TEXT[],         -- crop_codes of main commodities traded
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mandi_state        ON market.mandi_profile (state_code);
CREATE INDEX idx_mandi_location     ON market.mandi_profile USING GIST (location_geom);
CREATE INDEX idx_mandi_crops        ON market.mandi_profile USING GIN (primary_crops);

COMMENT ON TABLE market.mandi_profile IS
    '7,000+ AGMARKNET wholesale market profiles. Seeded from government AGMARKNET database.';


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
) PARTITION BY RANGE (price_date);

-- Create monthly partitions for commodity prices (2024 onwards)
CREATE TABLE market.commodity_price_2024 PARTITION OF market.commodity_price
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE market.commodity_price_2025 PARTITION OF market.commodity_price
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE market.commodity_price_2026 PARTITION OF market.commodity_price
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE market.commodity_price_2027 PARTITION OF market.commodity_price
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE INDEX idx_price_mandi_crop   ON market.commodity_price (mandi_code, crop_code, price_date DESC);
CREATE INDEX idx_price_date         ON market.commodity_price (price_date DESC);
CREATE INDEX idx_price_crop         ON market.commodity_price (crop_code, price_date DESC);

COMMENT ON TABLE market.commodity_price IS
    'Daily AGMARKNET market price data. Range-partitioned by year for performance.';


CREATE TABLE market.price_forecast (
    id                      UUID                            PRIMARY KEY DEFAULT uuid_generate_v4(),
    mandi_code              VARCHAR(20)                     NOT NULL REFERENCES market.mandi_profile(mandi_code),
    crop_code               VARCHAR(20)                     NOT NULL,
    forecast_generated_at   TIMESTAMPTZ                     NOT NULL DEFAULT NOW(),
    model_version           VARCHAR(30)                     NOT NULL,
    horizon                 market.forecast_horizon_enum    NOT NULL,
    target_date             DATE                            NOT NULL,
    q10_price_inr           NUMERIC(10,2)                   NOT NULL, -- Pessimistic (10th percentile)
    q50_price_inr           NUMERIC(10,2)                   NOT NULL, -- Modal (50th percentile)
    q90_price_inr           NUMERIC(10,2)                   NOT NULL, -- Optimistic (90th percentile)
    prediction_interval_low NUMERIC(10,2),
    prediction_interval_high NUMERIC(10,2),
    input_features_hash     VARCHAR(64),
    created_at              TIMESTAMPTZ                     NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_forecast_quantiles CHECK (q10_price_inr <= q50_price_inr AND q50_price_inr <= q90_price_inr)
);

CREATE INDEX idx_forecast_mandi     ON market.price_forecast (mandi_code, crop_code, target_date DESC);
CREATE INDEX idx_forecast_target    ON market.price_forecast (target_date DESC);


CREATE TABLE market.financial_referral (
    id                      UUID                        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID                        NOT NULL REFERENCES iam.user(id) ON DELETE RESTRICT,
    product_type            market.product_type_enum    NOT NULL,
    partner_name            VARCHAR(100)                NOT NULL,
    partner_application_id  VARCHAR(100),                           -- Partner's internal reference
    amount_requested_inr    NUMERIC(14,2)               CHECK (amount_requested_inr > 0),
    status                  market.referral_status_enum NOT NULL DEFAULT 'INITIATED',
    consent_record_id       UUID                        NOT NULL REFERENCES iam.consent_record(id),
    data_fields_shared      TEXT[]                      NOT NULL DEFAULT '{}',
    partner_response        JSONB                       DEFAULT '{}',
    idempotency_key         UUID                        NOT NULL UNIQUE,
    initiated_at            TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ                 NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_referral_user_id   ON market.financial_referral (user_id);
CREATE INDEX idx_referral_status    ON market.financial_referral (status);
CREATE INDEX idx_referral_partner   ON market.financial_referral (partner_name);

-- ────────────────────────────────────────────────────────────
-- SECTION 9: PLATFORM SCHEMA
-- ────────────────────────────────────────────────────────────

CREATE TABLE platform.system_config (
    id              UUID                            PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key      VARCHAR(100)                    NOT NULL UNIQUE,
    config_value    TEXT                            NOT NULL,
    data_type       platform.config_data_type_enum  NOT NULL DEFAULT 'STRING',
    description     TEXT,
    is_editable     BOOLEAN                         NOT NULL DEFAULT TRUE,
    last_modified_by UUID                           REFERENCES iam.user(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ                     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ                     NOT NULL DEFAULT NOW()
);

INSERT INTO platform.system_config (config_key, config_value, data_type, description, is_editable) VALUES
    ('weather_sync_interval_mins',  '60',     'INTEGER', 'Meteorological API ingestion interval (minutes)', TRUE),
    ('satellite_ndvi_scan_days',    '10',     'INTEGER', 'Sentinel-2 NDVI tile download frequency (days)', TRUE),
    ('free_tier_max_plots',         '2',      'INTEGER', 'Maximum farm plots for Free tier users', TRUE),
    ('image_blur_threshold',        '100.00', 'NUMERIC', 'Laplacian variance blur detection threshold', TRUE),
    ('model_fallback_mode',         'false',  'BOOLEAN', 'Force crop recommendations to use rule-based fallback', TRUE),
    ('diagnosis_confidence_threshold', '0.70','NUMERIC', 'AI confidence below which agronomist review is triggered', TRUE),
    ('max_otp_attempts',            '3',      'INTEGER', 'Maximum failed OTP attempts before lockout', FALSE),
    ('otp_expiry_seconds',          '300',    'INTEGER', 'OTP TTL in Redis (seconds)', FALSE),
    ('kafka_retry_max_attempts',    '5',      'INTEGER', 'Maximum Kafka consumer retry attempts before DLQ', TRUE),
    ('agronomist_cohort_max_size',  '500',    'INTEGER', 'Maximum farmers per agronomist cohort', TRUE);

COMMENT ON TABLE platform.system_config IS
    'Dynamic runtime configuration. Values are hot-reloaded by Kong gateway and application services.';


CREATE TABLE platform.audit_log (
    id                  BIGSERIAL       NOT NULL,
    occurred_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    event_category      platform.event_category_enum NOT NULL,
    event_type          VARCHAR(80)     NOT NULL,
    actor_user_id       UUID            REFERENCES iam.user(id) ON DELETE SET NULL,
    actor_ip            INET,
    target_resource_id  UUID,
    target_resource_type VARCHAR(50),
    action_description  TEXT,
    before_state        JSONB,
    after_state         JSONB,
    metadata            JSONB           DEFAULT '{}',
    PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE platform.audit_log_2025 PARTITION OF platform.audit_log
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE platform.audit_log_2026 PARTITION OF platform.audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE platform.audit_log_2027 PARTITION OF platform.audit_log
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE INDEX idx_audit_occurred     ON platform.audit_log (occurred_at DESC);
CREATE INDEX idx_audit_category     ON platform.audit_log (event_category, occurred_at DESC);
CREATE INDEX idx_audit_actor        ON platform.audit_log (actor_user_id, occurred_at DESC);
CREATE INDEX idx_audit_resource     ON platform.audit_log (target_resource_id, target_resource_type);

COMMENT ON TABLE platform.audit_log IS
    'Immutable, partitioned audit trail. Records are never deleted. Archived to S3 after 2 years.';


CREATE TABLE platform.api_key (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_name         VARCHAR(100)    NOT NULL,
    tenant_type         VARCHAR(30)     NOT NULL CHECK (tenant_type IN ('ENTERPRISE', 'FINANCIAL_PARTNER',
                                                                         'RESEARCH', 'GOVERNMENT')),
    key_hash            VARCHAR(128)    NOT NULL UNIQUE,  -- SHA-512 of raw API key
    key_prefix          VARCHAR(8)      NOT NULL,         -- First 8 chars for lookup display
    scopes              TEXT[]          NOT NULL DEFAULT '{}',
    allowed_cidrs       INET[]          NOT NULL DEFAULT '{}',
    rate_limit_per_min  INTEGER         NOT NULL DEFAULT 1000,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    last_used_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    created_by          UUID            REFERENCES iam.user(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_key_hash       ON platform.api_key (key_hash);
CREATE INDEX idx_api_key_prefix     ON platform.api_key (key_prefix);
CREATE INDEX idx_api_key_tenant     ON platform.api_key (tenant_name);
CREATE INDEX idx_api_key_active     ON platform.api_key (is_active) WHERE is_active = TRUE;

COMMENT ON TABLE platform.api_key IS
    'B2B enterprise API key registry. Raw key shown once; only SHA-512 hash is stored.';


CREATE TABLE platform.webhook_config (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_key_id          UUID            NOT NULL REFERENCES platform.api_key(id) ON DELETE CASCADE,
    target_url          TEXT            NOT NULL,
    signing_secret_hash VARCHAR(128)    NOT NULL,   -- SHA-512 of HMAC signing secret
    event_types         TEXT[]          NOT NULL DEFAULT '{}',
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    max_retries         SMALLINT        NOT NULL DEFAULT 5,
    timeout_seconds     SMALLINT        NOT NULL DEFAULT 30,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_webhook_api_key    ON platform.webhook_config (api_key_id);
CREATE INDEX idx_webhook_active     ON platform.webhook_config (is_active) WHERE is_active = TRUE;


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
) PARTITION BY RANGE (delivered_at);

CREATE TABLE platform.webhook_delivery_log_2026 PARTITION OF platform.webhook_delivery_log
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE platform.webhook_delivery_log_2027 PARTITION OF platform.webhook_delivery_log
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE INDEX idx_wdl_webhook_config ON platform.webhook_delivery_log (webhook_config_id, delivered_at DESC);
CREATE INDEX idx_wdl_status         ON platform.webhook_delivery_log (status, next_retry_at) WHERE status = 'RETRYING';
CREATE INDEX idx_wdl_idempotency    ON platform.webhook_delivery_log (idempotency_key);

-- ────────────────────────────────────────────────────────────
-- SECTION 10: AUTO-UPDATE TRIGGERS (updated_at)
-- ────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    t RECORD;
BEGIN
    FOR t IN
        SELECT table_schema, table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
          AND table_schema IN ('iam', 'farm', 'advisory', 'market', 'platform', 'reference')
    LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_%s_updated_at
             BEFORE UPDATE ON %I.%I
             FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()',
            t.table_schema, t.table_name, t.table_schema, t.table_name
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column IS
    'Auto-updates updated_at timestamp on any table row modification.';
