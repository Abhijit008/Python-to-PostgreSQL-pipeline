-- Table creation for raw data
CREATE TABLE IF NOT EXISTS iot_raw_data (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    device VARCHAR(50) NOT NULL,
    co DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    light BOOLEAN,
    lpg DOUBLE PRECISION,
    motion BOOLEAN,
    smoke DOUBLE PRECISION,
    temp DOUBLE PRECISION,
    source_file VARCHAR(255),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index creation
CREATE INDEX idx_iot_device_time ON iot_raw_data (device, ts);

--table creation
CREATE TABLE IF NOT EXISTS sensor_aggregates (
    id SERIAL PRIMARY KEY,
    device VARCHAR(50),
    sensor_type VARCHAR(20),
    metric_window_start TIMESTAMP,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    avg_value DOUBLE PRECISION,
    std_dev_value DOUBLE PRECISION,
    source_file VARCHAR(255),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);