# spark/jobs/sample_etl_job.py

import argparse
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta import *

def create_spark_session():
    """Create Spark session with Delta Lake support"""
    return (SparkSession.builder
            .appName("Sample ETL Job")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
            .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
            .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
            .getOrCreate())

def process_customer_data(spark, input_path, output_path):
    """Process customer data"""
    
    # Read CSV data
    print(f"Reading data from: {input_path}")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
    
    # Show original data info
    print("Original data:")
    df.printSchema()
    df.show(10)
    print(f"Total records: {df.count()}")
    
    # Data transformation
    processed_df = (df
                   .withColumn("age_category", 
                             when(col("age") < 30, "Young")
                             .when(col("age") < 50, "Middle")
                             .otherwise("Senior"))
                   .withColumn("salary_category",
                             when(col("salary") < 40000, "Low")
                             .when(col("salary") < 70000, "Medium")
                             .otherwise("High"))
                   .withColumn("processed_date", current_timestamp())
                   .withColumn("year_month", date_format(current_timestamp(), "yyyy-MM")))
    
    # Add aggregated statistics
    city_stats = (processed_df
                 .groupBy("city", "age_category")
                 .agg(
                     count("*").alias("customer_count"),
                     avg("salary").alias("avg_salary"),
                     min("salary").alias("min_salary"),
                     max("salary").alias("max_salary")
                 ))
    
    # Show processed data
    print("Processed data:")
    processed_df.printSchema()
    processed_df.show(10)
    
    print("City statistics:")
    city_stats.show()
    
    # Write processed data as Delta table
    print(f"Writing processed data to: {output_path}")
    (processed_df
     .write
     .format("delta")
     .mode("overwrite")
     .option("mergeSchema", "true")
     .partitionBy("city", "year_month")
     .save(output_path))
    
    # Write city statistics
    stats_output_path = output_path.replace("customers_processed", "city_statistics")
    print(f"Writing city statistics to: {stats_output_path}")
    (city_stats
     .write
     .format("delta")
     .mode("overwrite")
     .save(stats_output_path))
    
    print("ETL job completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Sample ETL Job")
    parser.add_argument("--input-path", required=True, help="Input data path")
    parser.add_argument("--output-path", required=True, help="Output data path")
    
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("INFO")
    
    try:
        # Process data
        process_customer_data(spark, args.input_path, args.output_path)
        
    except Exception as e:
        print(f"Job failed with error: {str(e)}")
        sys.exit(1)
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()