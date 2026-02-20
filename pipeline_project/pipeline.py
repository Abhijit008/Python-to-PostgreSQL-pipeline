import os
import time
import shutil
import logging
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# --- CONFIGURATION ---
WATCH_DIR = './data'
PROCESSED_DIR = './processed'
QUARANTINE_DIR = './quarantine'
LOG_DIR = './logs'

DB_CONNECTION = 'postgresql://postgres:sql%402026@localhost:5432/iot_sensor_db'

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'pipeline.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

engine = create_engine(DB_CONNECTION)


def validate_and_transform(df, filename):
    # 1. Required Columns Check
    required_cols = ['ts', 'device', 'co', 'humidity', 'light', 'lpg', 'motion', 'smoke', 'temp']
    if not all(col in df.columns for col in required_cols):
        logging.error(f"File {filename} is missing required columns.")
        return pd.DataFrame(), df

        # 2. Data Type Conversion
    try:
        df['ts'] = pd.to_datetime(df['ts'], unit='s')
    except Exception:
        logging.error(f"Timestamp conversion failed for {filename}")
        return pd.DataFrame(), df

    numeric_cols = ['co', 'humidity', 'lpg', 'smoke', 'temp']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Validation Logic
    valid_mask = (
            df['ts'].notnull() &
            df['device'].notnull() &
            (df['temp'].between(-50, 50)) &
            (df['humidity'].between(0, 100)) &
            (df['co'] >= 0) &
            (df['lpg'] >= 0) &
            (df['smoke'] >= 0)
    )

    valid_df = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()

    return valid_df, invalid_df


def process_file(filepath):
    filename = os.path.basename(filepath)
    try:
        logging.info(f"Processing {filename}...")
        df = pd.read_csv(filepath)

        valid_df, invalid_df = validate_and_transform(df, filename)

        # Handle Invalid Data
        if not invalid_df.empty:
            q_path = os.path.join(QUARANTINE_DIR, f"invalid_{filename}")
            invalid_df.to_csv(q_path, index=False)
            logging.warning(f"Quarantined {len(invalid_df)} rows.")

        # Handle Valid Data
        if not valid_df.empty:
            valid_df['source_file'] = filename
            valid_df.to_sql('iot_raw_data', engine, if_exists='append', index=False)

            metric_cols = ['co', 'humidity', 'lpg', 'smoke', 'temp']

            for sensor in metric_cols:
                aggs = valid_df.groupby('device')[sensor].agg(
                    min_value='min',
                    max_value='max',
                    avg_value='mean',
                    std_dev_value='std'
                ).reset_index()

                aggs['sensor_type'] = sensor
                aggs['metric_window_start'] = datetime.now()
                aggs['source_file'] = filename

                aggs.to_sql('sensor_aggregates', engine, if_exists='append', index=False)

            logging.info(f"Success: Processed {len(valid_df)} rows from {filename}")

        # Move processed file
        shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))

    except Exception as e:
        logging.error(f"CRITICAL ERROR processing {filename}: {e}")


def main():
    print(f"Pipeline Running... Monitoring '{WATCH_DIR}' for new CSVs.")
    while True:
        files = [f for f in os.listdir(WATCH_DIR) if f.endswith('.csv')]
        for file in files:
            process_file(os.path.join(WATCH_DIR, file))
        time.sleep(5)


if __name__ == "__main__":
    main()