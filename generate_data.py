import pandas as pd
import numpy as np
import time
import os


def generate_iot_csv():
    num_rows = 20
    data = {
        'ts': [time.time()] * num_rows,
        'device': np.random.choice(['b8:27:eb:bf:9d:51', '00:0f:00:70:91:0a', '1c:bf:ce:15:ec:4d'], num_rows),
        'co': np.random.uniform(0.001, 0.01, num_rows),
        'humidity': np.random.uniform(40, 80, num_rows),
        'light': np.random.choice([True, False], num_rows),
        'lpg': np.random.uniform(0.005, 0.01, num_rows),
        'motion': np.random.choice([True, False], num_rows),
        'smoke': np.random.uniform(0.01, 0.03, num_rows),
        'temp': np.random.uniform(15, 30, num_rows)
    }

    df = pd.DataFrame(data)

    # Introduce "Bad Data" to test validation (temp > 50)
    df.loc[0, 'temp'] = 100

    filename = f"pipeline_project/data/iot_readings_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"Generated: {filename}")


if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    print("Generating data every 10 seconds... (Ctrl+C to stop)")
    while True:
        generate_iot_csv()
        time.sleep(10)