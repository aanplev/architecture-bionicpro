from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, date
import clickhouse_connect


def load_to_olap():
    client = clickhouse_connect.get_client(
        host="clickhouse",
        port=8123
    )

    client.command("""
        CREATE TABLE IF NOT EXISTS report_mart (
            user_id UInt64,
            metric UInt32,
            report_date Date
        ) ENGINE = MergeTree()
        ORDER BY user_id
    """)

    rows = [
        (1, 100, date(2024, 1, 1)),
        (2, 200, date(2024, 1, 1)),
    ]

    client.insert(
        "report_mart",
        rows,
        column_names=["user_id", "metric", "report_date"]
    )


with DAG(
    dag_id="crm_telemetry_daily_report",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    PythonOperator(
        task_id="load_to_clickhouse",
        python_callable=load_to_olap
    )
