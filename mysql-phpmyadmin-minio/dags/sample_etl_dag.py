# dags/sample_etl_dag.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3ListOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'sample_etl_pipeline',
    default_args=default_args,
    description='Sample ETL pipeline with Spark and MinIO',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['etl', 'spark', 'minio'],
)

def check_minio_connection():
    """Test MinIO connection"""
    from minio import Minio
    import logging
    
    client = Minio(
        endpoint='minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )
    
    # List buckets to test connection
    buckets = client.list_buckets()
    logging.info(f"Available buckets: {[bucket.name for bucket in buckets]}")
    return True

def create_sample_data():
    """Create sample data in MinIO"""
    import pandas as pd
    from minio import Minio
    import io
    
    # Create sample data
    data = {
        'id': range(1, 1001),
        'name': [f'Customer_{i}' for i in range(1, 1001)],
        'age': [20 + (i % 50) for i in range(1, 1001)],
        'city': ['Bangkok', 'Chiang Mai', 'Phuket'] * 333 + ['Bangkok'],
        'salary': [30000 + (i * 100) for i in range(1, 1001)]
    }
    
    df = pd.DataFrame(data)
    
    # Convert to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # Upload to MinIO
    client = Minio(
        endpoint='minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )
    
    client.put_object(
        bucket_name='data-lake',
        object_name='raw/customers.csv',
        data=io.BytesIO(csv_buffer.getvalue().encode()),
        length=len(csv_buffer.getvalue()),
        content_type='text/csv'
    )
    
    return True

# Task 1: Check MinIO connection
check_connection_task = PythonOperator(
    task_id='check_minio_connection',
    python_callable=check_minio_connection,
    dag=dag,
)

# Task 2: Create sample data
create_data_task = PythonOperator(
    task_id='create_sample_data',
    python_callable=create_sample_data,
    dag=dag,
)

# Task 3: Process data with Spark
process_data_task = SparkSubmitOperator(
    task_id='process_data_with_spark',
    application='/opt/spark/jobs/sample_etl_job.py',
    conn_id='spark_default',
    application_args=[
        '--input-path', 's3a://data-lake/raw/customers.csv',
        '--output-path', 's3a://data-lake/processed/customers_processed'
    ],
    packages='org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.367,io.delta:delta-core_2.12:2.4.0',
    conf={
        'spark.master': 'spark://spark-master:7077',
        
        # set Spark driver and executor memory
        'spark.driver.memory': '2g',
        'spark.executor.memory': '2g',
        'spark.executor.cores': '2',

        # Config for connecting to MinIO S3 bucket with Spark
        'spark.hadoop.fs.s3a.endpoint': 'http://minio:9000',
        'spark.hadoop.fs.s3a.access.key': 'minioadmin',
        'spark.hadoop.fs.s3a.secret.key': 'minioadmin',
        'spark.hadoop.fs.s3a.path.style.access': 'true',
        'spark.hadoop.fs.s3a.impl': 'org.apache.hadoop.fs.s3a.S3AFileSystem',
        'spark.hadoop.fs.s3a.connection.ssl.enabled': 'false',
        'spark.sql.extensions': 'io.delta.sql.DeltaSparkSessionExtension',
        'spark.sql.catalog.spark_catalog': 'org.apache.spark.sql.delta.catalog.DeltaCatalog'
    },
    dag=dag,
)

# Task 4: Data quality check
def data_quality_check():
    """Check data quality after processing"""
    from minio import Minio
    import logging
    
    client = Minio(
        endpoint='minio:9000',
        access_key='minioadmin',
        secret_key='minioadmin',
        secure=False
    )
    
    # Check if processed data exists
    objects = list(client.list_objects('data-lake', prefix='processed/customers_processed/', recursive=True))
    
    if not objects:
        raise ValueError("No processed data found!")
    
    logging.info(f"Found {len(objects)} processed files")
    return True

quality_check_task = PythonOperator(
    task_id='data_quality_check',
    python_callable=data_quality_check,
    dag=dag,
)

# Set task dependencies
check_connection_task >> create_data_task >> process_data_task >> quality_check_task