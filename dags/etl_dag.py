from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="transaction_data_etl_dbt",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    run_etl = BashOperator(
        task_id="run_etl",
        bash_command="python /opt/airflow/etl/etl_script.py",
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt run --profiles-dir /opt/airflow/dbt"
        ),
    )

    run_etl >> run_dbt