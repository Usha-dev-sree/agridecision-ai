-- ============================================================
-- AgriDecision AI — TimescaleDB Hypertables & Aggregates
-- PostgreSQL 16 + TimescaleDB 2.15
-- ============================================================
-- Run AFTER 001_master_schema.sql
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- SECTION 1: TIMESERIES SCHEMA TABLES
-- ────────────────────────────────────────────────────────────

CREATE TABLE timeseries.weather_observations (
    time                TIMESTAMPTZ     NOT NULL,
    farm_plot_id        UUID            NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    source              VARCHAR(30)     NOT NULL DEFAULT 'OPENWEATHER'
                                        CHECK (source IN ('OPENWEATHER', 'IMD', 'IOT_STATION', 'MANUAL')),
    grid_lat            NUMERIC(8,5)    NOT NULL,
    grid_lon            NUMERIC(8,5)    NOT NULL,
    temp_c              NUMERIC(6,3),   -- Air temperature (°C)
    temp_min_c          NUMERIC(6,3),
    temp_max_c          NUMERIC(6,3),
    humidity_pct        NUMERIC(5,2)    CHECK (humidity_pct BETWEEN 0 AND 100),
    wind_speed_ms       NUMERIC(7,3)    CHECK (wind_speed_ms >= 0),
    wind_direction_deg  SMALLINT        CHECK (wind_direction_deg BETWEEN 0 AND 360),
    rainfall_mm         NUMERIC(8,3)    NOT NULL DEFAULT 0 CHECK (rainfall_mm >= 0),
    solar_radiation_mj  NUMERIC(8,4),   -- MJ/m² per day
    sunshine_hours      NUMERIC(5,2),
    evapotranspiration_mm NUMERIC(8,4), -- Computed ETo
    dew_point_c         NUMERIC(6,3),
    visibility_km       NUMERIC(8,3),
    cloud_cover_pct     NUMERIC(5,2),
    uv_index            NUMERIC(5,2),
    raw_api_response    JSONB           DEFAULT '{}'
);

-- Convert to hypertable partitioned by time (7-day chunks)
SELECT create_hypertable(
    'timeseries.weather_observations',
    'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- Add space partitioning by farm_plot_id (4 partitions for parallel queries)
SELECT add_dimension(
    'timeseries.weather_observations',
    by_hash('farm_plot_id', 4)
);

CREATE INDEX idx_weather_plot_time  ON timeseries.weather_observations (farm_plot_id, time DESC);
CREATE INDEX idx_weather_source     ON timeseries.weather_observations (source, time DESC);
CREATE INDEX idx_weather_grid       ON timeseries.weather_observations (grid_lat, grid_lon, time DESC);

COMMENT ON TABLE timeseries.weather_observations IS
    'TimescaleDB hypertable. 7-day chunks + 4-partition hash by farm_plot_id. Auto-retains 5 years.';


CREATE TABLE timeseries.ndvi_observations (
    time                TIMESTAMPTZ     NOT NULL,
    farm_plot_id        UUID            NOT NULL REFERENCES farm.farm_plot(id) ON DELETE CASCADE,
    satellite_source    VARCHAR(20)     NOT NULL DEFAULT 'SENTINEL2'
                                        CHECK (satellite_source IN ('SENTINEL2', 'LANDSAT8', 'MODIS')),
    cloud_cover_pct     NUMERIC(5,2)    CHECK (cloud_cover_pct BETWEEN 0 AND 100),
    ndvi_mean           NUMERIC(6,4)    CHECK (ndvi_mean BETWEEN -1 AND 1),
    ndvi_std            NUMERIC(6,4),
    ndvi_min            NUMERIC(6,4),
    ndvi_max            NUMERIC(6,4),
    ndre_mean           NUMERIC(6,4),   -- Red Edge NDVI
    evi_mean            NUMERIC(6,4),   -- Enhanced Vegetation Index
    lai_estimate        NUMERIC(6,4),   -- Leaf Area Index estimate
    tile_id             VARCHAR(30),    -- Sentinel-2 tile identifier
    tile_s3_key         TEXT,           -- S3 key to GeoTIFF tile
    processing_level    VARCHAR(10)     DEFAULT 'L2A'
);

SELECT create_hypertable(
    'timeseries.ndvi_observations',
    'time',
    chunk_time_interval => INTERVAL '30 days',
    if_not_exists => TRUE
);

CREATE INDEX idx_ndvi_plot_time     ON timeseries.ndvi_observations (farm_plot_id, time DESC);

COMMENT ON TABLE timeseries.ndvi_observations IS
    'Sentinel-2 derived vegetation indices per plot. 30-day chunks (matches satellite revisit time).';


CREATE TABLE timeseries.sensor_readings (
    time                TIMESTAMPTZ     NOT NULL,
    device_id           UUID            NOT NULL REFERENCES farm.iot_device(id) ON DELETE CASCADE,
    farm_plot_id        UUID            NOT NULL,
    metric_name         VARCHAR(50)     NOT NULL, -- e.g. SOIL_MOISTURE_10CM, SOIL_TEMP_10CM
    metric_value        NUMERIC(12,6)   NOT NULL,
    unit                VARCHAR(20)     NOT NULL,
    battery_level_pct   NUMERIC(5,2),
    signal_strength_db  SMALLINT,
    raw_payload         JSONB           DEFAULT '{}'
);

SELECT create_hypertable(
    'timeseries.sensor_readings',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

SELECT add_dimension('timeseries.sensor_readings', by_hash('device_id', 8));

CREATE INDEX idx_sensor_device_time ON timeseries.sensor_readings (device_id, metric_name, time DESC);
CREATE INDEX idx_sensor_plot_time   ON timeseries.sensor_readings (farm_plot_id, time DESC);

COMMENT ON TABLE timeseries.sensor_readings IS
    'IoT device sensor telemetry. 1-day chunks + 8-partition hash by device_id for high write throughput.';

-- ────────────────────────────────────────────────────────────
-- SECTION 2: CONTINUOUS AGGREGATES
-- ────────────────────────────────────────────────────────────

-- Daily weather summary per plot
CREATE MATERIALIZED VIEW timeseries.weather_daily_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time)     AS bucket,
    farm_plot_id,
    AVG(temp_c)                    AS avg_temp_c,
    MIN(temp_min_c)                AS min_temp_c,
    MAX(temp_max_c)                AS max_temp_c,
    AVG(humidity_pct)              AS avg_humidity_pct,
    SUM(rainfall_mm)               AS total_rainfall_mm,
    AVG(wind_speed_ms)             AS avg_wind_speed_ms,
    AVG(solar_radiation_mj)        AS avg_solar_radiation_mj,
    AVG(evapotranspiration_mm)     AS avg_eto_mm,
    COUNT(*)                       AS observation_count
FROM timeseries.weather_observations
GROUP BY bucket, farm_plot_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'timeseries.weather_daily_summary',
    start_offset => INTERVAL '2 days',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

CREATE INDEX idx_weather_daily_plot ON timeseries.weather_daily_summary (farm_plot_id, bucket DESC);

-- Monthly weather summary per plot
CREATE MATERIALIZED VIEW timeseries.weather_monthly_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 month', bucket)  AS month_bucket,
    farm_plot_id,
    AVG(avg_temp_c)                 AS avg_temp_c,
    SUM(total_rainfall_mm)          AS total_rainfall_mm,
    AVG(avg_humidity_pct)           AS avg_humidity_pct,
    SUM(avg_eto_mm)                 AS total_eto_mm,
    SUM(observation_count)          AS total_observations
FROM timeseries.weather_daily_summary
GROUP BY month_bucket, farm_plot_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'timeseries.weather_monthly_summary',
    start_offset => INTERVAL '2 months',
    end_offset   => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);

-- Daily commodity price summary per crop+state
CREATE MATERIALIZED VIEW timeseries.price_daily_state_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', NOW()::TIMESTAMPTZ)  AS bucket,
    m.state_code,
    cp.crop_code,
    AVG(cp.modal_price_inr)                   AS avg_modal_price_inr,
    MIN(cp.min_price_inr)                      AS min_price_inr,
    MAX(cp.max_price_inr)                      AS max_price_inr,
    SUM(cp.arrivals_tonnes)                    AS total_arrivals_tonnes,
    COUNT(DISTINCT cp.mandi_code)              AS mandi_count
FROM market.commodity_price cp
JOIN market.mandi_profile m ON m.mandi_code = cp.mandi_code
GROUP BY bucket, m.state_code, cp.crop_code
WITH NO DATA;

-- ────────────────────────────────────────────────────────────
-- SECTION 3: DATA RETENTION POLICIES
-- ────────────────────────────────────────────────────────────

-- Retain raw weather observations for 5 years
SELECT add_retention_policy(
    'timeseries.weather_observations',
    INTERVAL '5 years'
);

-- Retain raw NDVI observations for 7 years (research value)
SELECT add_retention_policy(
    'timeseries.ndvi_observations',
    INTERVAL '7 years'
);

-- Retain raw sensor readings for 2 years (high volume)
SELECT add_retention_policy(
    'timeseries.sensor_readings',
    INTERVAL '2 years'
);

-- ────────────────────────────────────────────────────────────
-- SECTION 4: COMPRESSION POLICIES
-- ────────────────────────────────────────────────────────────

-- Enable compression on weather_observations (chunks older than 30 days)
ALTER TABLE timeseries.weather_observations SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'farm_plot_id, source',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy(
    'timeseries.weather_observations',
    INTERVAL '30 days'
);

-- Enable compression on sensor_readings (chunks older than 7 days)
ALTER TABLE timeseries.sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id, metric_name',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy(
    'timeseries.sensor_readings',
    INTERVAL '7 days'
);
