# Data Engineering Stack

Modern data engineering stack with Apache Airflow, Apache Spark, and MinIO object storage, all containerized with Docker.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Apache        │    │   Apache Spark   │    │     MinIO       │
│   Airflow       │◄──►│     Cluster      │◄──►│  Object Storage │
│                 │    │                  │    │                 │
│ - Scheduler     │    │ - Master         │    │ - S3 Compatible │
│ - Webserver     │    │ - Worker 1       │    │ - Data Lake     │
│ - Workers       │    │ - Worker 2       │    │ - Buckets       │
│ - Triggerer     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               │
         │              ┌──────────────────┐             │
         └─────────────►│    PostgreSQL    │◄────────────┘
                        │     Database     │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │      Redis       │
                        │  Message Broker  │
                        │    (Optional)    │
                        └──────────────────┘
```

## 🚀 Services

- **Apache Airflow 2.8.0**: Workflow orchestration
- **Apache Spark 3.4.0**: Big data processing
- **MinIO**: S3-compatible object storage
- **PostgreSQL 14**: Metadata database
- **Redis 7.2**: Message broker
- **Jupyter Lab**: Development environment

## 📋 Compatible Versions

| Service | Version | Notes |
|---------|---------|--------|
| Airflow | 2.8.0 | Latest stable with Python 3.11 |
| Spark | 3.4.0 | With Hadoop 3.x compatibility |
| MinIO | RELEASE.2023-12-02T10-51-33Z | Latest LTS |
| PostgreSQL | 14 | Airflow metadata database |
| Redis | 7.2-alpine | Celery message broker |
| Python | 3.11 | Runtime for Airflow and Spark |
| Java | 17 | JRE for Spark |

### Key Dependencies

- **PySpark**: 3.4.0 (matches Spark version)
- **Delta Lake**: 2.4.0 (Spark 3.4 compatible)
- **Hadoop AWS**: 3.3.4 (S3A filesystem)
- **AWS Java SDK**: 1.12.367 (S3 connectivity)

## 🛠️ Prerequisites

- Docker 20.x or later
- Docker Compose 2.x or later  
- At least 8GB RAM available for Docker
- At least 2 CPU cores

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd data-engineering-stack

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### 2. Start Services

```bash
# Start all services in background
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access Web Interfaces

| Service | URL | Credentials |
|---------|-----|------------|
| Airflow | http://localhost:8080 | airflow / airflow123 |
| Spark Master | http://localhost:8081 | No auth |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| Jupyter Lab | http://localhost:8888 | No token |

## 📁 Project Structure

```
data-engineering-stack/
├── docker-compose.yml          # Main orchestration file
├── .env                       # Environment variables
├── setup.sh                   # Setup script
│
├── airflow/                   # Airflow configuration
│   ├── Dockerfile
│   └── requirements.txt
│
├── jupyter/                   # Jupyter configuration  
│   ├── Dockerfile
│   ├── requirements.txt
│   └── spark-defaults.conf
│
├── dags/                      # Airflow DAGs
│   └── sample_etl_dag.py
│
├── spark/
│   ├── jobs/                  # Spark applications
│   │   └── sample_etl_job.py
│   └── data/                  # Spark data directory
│
├── notebooks/                 # Jupyter notebooks
│   └── 01_spark_minio_example.ipynb
│
├── logs/                      # Airflow logs
└── plugins/                   # Airflow plugins
```

## 🔧 Configuration

### MinIO Configuration

Default buckets created automatically:
- `data-lake`: Main data storage
- `spark-logs`: Spark application logs  
- `airflow-logs`: Airflow task logs

### Spark Configuration

Key settings in `spark-defaults.conf`:
- S3A filesystem for MinIO connectivity
- Delta Lake extensions enabled
- Adaptive query execution enabled
- Dynamic allocation configured

### Airflow Configuration

- **Executor**: CeleryExecutor (scalable)
- **Database**: PostgreSQL
- **Broker**: Redis
- **Authentication**: Basic auth enabled

## 💡 Usage Examples

### 1. Running the Sample DAG

The included sample DAG demonstrates:
- MinIO connectivity testing
- Sample data creation
- Spark job submission
- Data quality checks

Enable and trigger the DAG:
1. Go to Airflow UI (http://localhost:8080)
2. Find `sample_etl_pipeline` DAG
3. Toggle it ON
4. Click "Trigger DAG"

### 2. Spark Job Development

Create Spark jobs in `spark/jobs/`:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("My ETL Job") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .getOrCreate()

# Read from MinIO
df = spark.read.parquet("s3a://data-lake/input/")

# Process data
result = df.groupBy("category").count()

# Write back to MinIO  
result.write.mode("overwrite").parquet("s3a://data-lake/output/")
```

### 3. Using Jupyter for Development

Access Jupyter Lab at http://localhost:8888 and use the sample notebook to:
- Test Spark connectivity
- Experiment with data transformations
- Develop new ETL logic

## 🔍 Monitoring & Debugging

### Service Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs -f airflow-webserver
docker-compose logs -f spark-master
docker-compose logs -f minio
```

### Spark Monitoring

- **Spark Master UI**: http://localhost:8081
- **Application History**: Available after jobs complete
- **Worker Logs**: Accessible through Master UI

### Airflow Monitoring

- **Web UI**: http://localhost:8080
- **Task Logs**: Available in UI and `logs/` directory
- **System Health**: Admin → System Health

## 🛡️ Security Considerations

⚠️ **This setup is for development only**

For production:
- Change default passwords
- Enable TLS/SSL
- Configure proper authentication
- Set up network security
- Enable audit logging
- Use secrets management

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8080
   
   # Modify ports in docker-compose.yml
   ```

2. **Memory Issues**
   ```bash
   # Reduce memory allocation
   # Edit SPARK_WORKER_MEMORY in docker-compose.yml
   ```

3. **Permission Issues**
   ```bash
   # Fix Airflow permissions
   sudo chown -R $(id -u):$(id -g) logs/ dags/ plugins/
   ```

4. **MinIO Connectivity**
   ```bash
   # Test MinIO connection
   docker-compose exec minio mc admin info minio
   ```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
./setup.sh
docker-compose up -d
```

## 📚 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [MinIO Documentation](https://docs.min.io/)
- [Delta Lake Documentation](https://docs.delta.io/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly  
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.