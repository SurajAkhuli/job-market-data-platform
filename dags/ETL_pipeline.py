from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import duckdb
import os

BASE = "/opt/airflow/data"
BRONZE = f"{BASE}/bronze"
SILVER = f"{BASE}/silver"
GOLD = f"{BASE}/gold"

date= datetime.today().strftime("%Y_%m_%d")
# date="2026_02_22"

# --------------------
# Task 1: Bronze
# --------------------
def ingest():
    from pipelines.ingest_pipeline import run_ingestion
    run_ingestion()

# --------------------
# Task 2: Silver
# --------------------
def transform():
    from pipelines.bronze_to_silver import bronze_to_silver_conversion
    bronze_to_silver_conversion(date)
    

# --------------------
# Task 3: Gold
# --------------------
def task3():
    from pipelines.incremental_gold import gold_base_create
    gold_base_create(date)


# --------------------
# Task 4  
# --------------------
def task4():
    from pipelines.gold_pipeline import gold_pipeline
    gold_pipeline()


# --------------------
# Task 5  
# --------------------
def task5():
    from pipelines.gold_skill_demand import gold_skill_demand_table
    gold_skill_demand_table()

# def check_date():
#     from datetime import datetime
#     print(datetime.now())

# --------------------
# DAG
# --------------------
with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    t1 = PythonOperator(task_id="data_ingestion", python_callable=ingest)
    t2 = PythonOperator(task_id="bronze_to_silver_conversion", python_callable=transform)
    t3 = PythonOperator(task_id="gold_base_create", python_callable=task3)
    t4 = PythonOperator(task_id="gold_pipeline", python_callable=task4)
    t5 = PythonOperator(task_id="gold_skill_demand_table", python_callable=task5)

t1>>t2 >> t3 >> t4 >> t5



    # task = PythonOperator(task_id="date_check", python_callable=check_date)