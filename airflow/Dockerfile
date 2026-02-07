FROM apache/airflow:2.8.1

USER airflow

RUN pip uninstall -y clickhouse-connect || true \
 && pip install --no-cache-dir --force-reinstall "clickhouse-connect==0.5.25"
