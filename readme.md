Real-Time IoT Data Pipeline
1. Architecture and Design
This project implements a scalable real-time data pipeline designed to monitor, ingest, validate, and store IoT telemetry data.

The pipeline architecture consists of the following components:


Data Ingestion & Monitoring: A Python watchdog script continuously monitors a local data/ directory for incoming CSV files containing raw sensor data. The directory is polled regularly to trigger processing immediately upon file detection.



Data Validation & Transformation: Incoming data is strictly validated against defined quality standards. The criteria require no null values in key fields, correct numeric data types, and acceptable ranges for specific sensor readings (e.g., temperature between -50°C and 50°C).



Quarantine Mechanism: Any row that fails validation is separated and moved to a quarantine/ folder for further inspection, preventing bad data from entering the database.


Data Analysis: Validated data undergoes processing to calculate aggregated metrics for each sensor type per device. These metrics include the minimum, maximum, average, and standard deviation.


Database Storage: Both the raw validated data and the calculated aggregated metrics are stored in a PostgreSQL relational database. The schema includes indexes optimized for time-series querying.


2. Local Setup and Execution Instructions
Follow these steps to set up and run the pipeline locally.

Dependencies
Python 3.8+

PostgreSQL * Python packages: pandas, sqlalchemy, psycopg2-binary

Setup Steps
Clone the repository: Create a local folder for the project and ensure it contains the pipeline scripts.

Set up the directories: The script will automatically create the necessary data/, processed/, quarantine/, and logs/ folders upon execution.

Install Python dependencies: Run the following command in your terminal:

Bash
pip install pandas sqlalchemy psycopg2-binary
Configure the Database:

Open your PostgreSQL interface (e.g., pgAdmin).

Create a new database named iot_sensor_db.

Execute the provided schema.sql file within this database to create the iot_raw_data and sensor_aggregates tables.

Update Database Credentials: Open pipeline.py and update the DB_CONNECTION string with your actual PostgreSQL password.

Running the Pipeline
Open a terminal, navigate to the project directory, and start the pipeline:

Bash
python pipeline.py
Open a second terminal and start the data generator to simulate incoming IoT data:

Bash
python generate_data.py
Monitor the terminal logs and check your PostgreSQL database to verify data ingestion.

I have used the data set from kaggle https://www.kaggle.com/datasets/garystafford/environmental-sensor-data-132k
and also uploaded a small dataset file from the same with some errors named Test_with _error

3. Scalability for Production
While this solution processes files in a single local folder, it can be redesigned to scale horizontally to handle millions of files or data points per day.

To achieve production-grade scalability, I recommend the following architecture upgrades:


Distributed Message Queues: Instead of a simple Python loop monitoring a folder, the ingestion layer should be replaced with a distributed event streaming platform like Apache Kafka or a managed cloud service like Google Cloud Pub/Sub. This decouples data producers from consumers.


Distributed Processing Frameworks: The validation and aggregation logic currently handled by pandas should be migrated to Apache Spark (via PySpark) or stream processing services like AWS Lambda. This allows the processing workload to be distributed across multiple worker nodes simultaneously.


Storage Optimization: For high-volume data ingestion, storing every raw data point in a traditional relational database becomes a bottleneck. In a production environment, raw data should land in a Data Lake for cost-effective storage, while only the aggregated metrics are pushed to PostgreSQL or a specialized time-series database for fast querying.

Fault Tolerance & Orchestration: The pipeline should be containerized using Docker and orchestrated via Kubernetes to ensure high availability. Tools like Apache Airflow can be introduced to manage retry mechanisms and monitor pipeline health automatically.
