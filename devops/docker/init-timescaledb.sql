-- Enable TimescaleDB Extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create IoT telemetry hypertable
CREATE TABLE IF NOT EXISTS iot_telemetry_reading (
    time TIMESTAMPTZ NOT NULL,
    device_id UUID NOT NULL,
    plot_id UUID NOT NULL,
    soil_moisture_10cm NUMERIC(5,2),
    soil_moisture_30cm NUMERIC(5,2),
    soil_moisture_60cm NUMERIC(5,2),
    soil_temperature_c NUMERIC(5,2),
    ambient_temp_c NUMERIC(5,2),
    humidity_percent NUMERIC(5,2),
    solar_radiation NUMERIC(7,2)
);

-- Convert standard table into a hypertable partitioned by time
SELECT create_hypertable('iot_telemetry_reading', 'time', if_not_exists => TRUE);
