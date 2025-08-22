#!/bin/bash
# setup.sh

set -e

echo "🚀 Setting up Data Engineering Stack..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are available${NC}"

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p dags logs plugins
mkdir -p spark/jobs spark/data
mkdir -p notebooks
mkdir -p airflow jupyter

# Set proper permissions for Airflow
echo -e "${YELLOW}🔐 Setting up permissions...${NC}"
echo "AIRFLOW_UID=$(id -u)" > .env
cat >> .env << EOF
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow123

# Database
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Spark
SPARK_VERSION=3.4.0
HADOOP_VERSION=3

# Jupyter
JUPYTER_TOKEN=

# Network
COMPOSE_PROJECT_NAME=data-engineering
EOF

# Create sample notebook
echo -e "${YELLOW}📓 Creating sample notebook...${NC}"
cat > notebooks/01_spark_minio_example.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Spark with MinIO Example\n",
    "\n",
    "This notebook demonstrates how to use Spark with MinIO object storage."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "from pyspark.sql import SparkSession\n",
    "from pyspark.sql.functions import *\n",
    "\n",
    "# Create Spark session with MinIO configuration\n",
    "spark = SparkSession.builder \\\n",
    "    .appName(\"MinIO Example\") \\\n",
    "    .config(\"spark.hadoop.fs.s3a.endpoint\", \"http://minio:9000\") \\\n",
    "    .config(\"spark.hadoop.fs.s3a.access.key\", \"minioadmin\") \\\n",
    "    .config(\"spark.hadoop.fs.s3a.secret.key\", \"minioadmin\") \\\n",
    "    .config(\"spark.hadoop.fs.s3a.path.style.access\", \"true\") \\\n",
    "    .config(\"spark.hadoop.fs.s3a.impl\", \"org.apache.hadoop.fs.s3a.S3AFileSystem\") \\\n",
    "    .config(\"spark.hadoop.fs.s3a.connection.ssl.enabled\", \"false\") \\\n",
    "    .getOrCreate()\n",
    "\n",
    "print(\"Spark session created!\")\n",
    "print(f\"Spark version: {spark.version}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create sample data\n",
    "data = [(1, \"Alice\", 25), (2, \"Bob\", 30), (3, \"Charlie\", 35)]\n",
    "columns = [\"id\", \"name\", \"age\"]\n",
    "\n",
    "df = spark.createDataFrame(data, columns)\n",
    "df.show()\n",
    "\n",
    "# Save to MinIO\n",
    "df.write.mode(\"overwrite\").parquet(\"s3a://data-lake/sample-data/\")\n",
    "print(\"Data saved to MinIO!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Read from MinIO\n",
    "df_read = spark.read.parquet(\"s3a://data-lake/sample-data/\")\n",
    "df_read.show()\n",
    "print(\"Data read from MinIO!\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

# Initialize Airflow
echo -e "${YELLOW}🔧 Initializing Airflow...${NC}"
docker-compose up airflow-init

echo -e "${GREEN}✅ Setup completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Quick Start Guide:${NC}"
echo "1. Start all services: ${GREEN}docker-compose up -d${NC}"
echo "2. Access Airflow UI: ${GREEN}http://localhost:8080${NC} (airflow/airflow123)"
echo "3. Access Spark Master UI: ${GREEN}http://localhost:8081${NC}"
echo "4. Access MinIO Console: ${GREEN}http://localhost:9001${NC} (minioadmin/minioadmin)"
echo "5. Access Jupyter Lab: ${GREEN}http://localhost:8888${NC}"
echo ""
echo -e "${YELLOW}🛠️ Useful Commands:${NC}"
echo "- View logs: ${GREEN}docker-compose logs -f [service-name]${NC}"
echo "- Stop all services: ${GREEN}docker-compose down${NC}"
echo "- Stop and remove volumes: ${GREEN}docker-compose down -v${NC}"
echo "- Rebuild services: ${GREEN}docker-compose up --build${NC}"