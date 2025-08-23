# spark/Dockerfile

# Build from Debian 12-slim, base OS ใหม่ที่มี Python 3.11
FROM debian:12-slim

# Set base Environment Variables
ENV SPARK_VERSION=3.4.0
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYSPARK_PYTHON=/usr/bin/python3.11

# Install all necessary dependencies (including Java 17 and Python 3.11)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    bash \
    procps \
    python3.11 \
    python3.11-venv \
    python3.11-distutils \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Download and install Spark from the Official Apache Archive
RUN cd /tmp \
    && curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /opt/ \
    && mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Download necessary JARs for S3/MinIO connectivity
RUN cd ${SPARK_HOME}/jars \
    && curl -O https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    && curl -O https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.367/aws-java-sdk-bundle-1.12.367.jar \
    && curl -O https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar \
    && curl -O https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar

# Create a user to run Spark for security
RUN groupadd -r spark --gid 1001 && useradd -r -g spark --uid 1001 spark

# Change ownership of Spark directory to spark user
RUN chown -R spark:spark ${SPARK_HOME}

# Switch to the spark user
USER spark

# Set WORKDIR and ENTRYPOINT for running Spark
WORKDIR ${SPARK_HOME}
ENTRYPOINT [ "/opt/spark/bin/spark-class" ]
