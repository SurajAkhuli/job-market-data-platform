FROM apache/airflow:3.1.0-python3.11

# USER root
# RUN mkdir -p /opt/airflow/data/bronze \
#              /opt/airflow/data/silver \
#              /opt/airflow/data/gold \
#              /opt/airflow/logs \
#              /opt/airflow/config \
#              /opt/airflow/pipelines && \
#     chown -R airflow:root /opt/airflow

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY pipelines /opt/airflow/pipelines
RUN pip install /opt/airflow/pipelines