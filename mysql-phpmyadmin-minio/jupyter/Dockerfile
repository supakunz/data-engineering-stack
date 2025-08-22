# jupyter/Dockerfile
FROM jupyter/pyspark-notebook:spark-3.4.0

USER root

# Install system packages
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create a "jars" directory and give user permissions
RUN mkdir -p $SPARK_HOME/jars \
    && chown -R $NB_UID:$NB_GID $SPARK_HOME/jars

# Install Python packages
USER $NB_UID
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Download JARs for MinIO/S3 connectivity
USER root
RUN cd $SPARK_HOME/jars \
    && curl -sSL -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    && curl -sSL -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.367/aws-java-sdk-bundle-1.12.367.jar \
    && curl -sSL -O https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar \
    && curl -sSL -O https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar \
    && chown -R $NB_UID:$NB_GID $SPARK_HOME/jars

# Give back user permissions
USER $NB_UID

# Setup Spark for Delta + MinIO
ENV SPARK_OPTS="--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"

# Copy spark-defaults.conf (if any)
COPY spark-defaults.conf $SPARK_HOME/conf/
