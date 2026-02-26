from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from pipelines.utils.logger import get_logger

logger = get_logger("airflow_tasks")

BASE = "/opt/airflow/data"
BRONZE = f"{BASE}/bronze"
SILVER = f"{BASE}/silver"
GOLD = f"{BASE}/gold"

date= datetime.today().strftime("%Y_%m_%d")
# date="2026_02_22"

# --------------------
# Task 1: Bronze
# --------------------
def run_ingestion_task():
    from pipelines.ingest_pipeline import run_daily_ingestion
    logger.info("[DAG] Starting ingestion task")
    run_daily_ingestion()

# --------------------
# Task 2: Silver
# --------------------
def run_bronze_to_silver_task():
    from pipelines.bronze_to_silver import transform_bronze_to_silver
    logger.info("[DAG] Starting bronze to silver conversion task")
    transform_bronze_to_silver(date)
    

# --------------------
# Task 3: Gold
# --------------------
def run_gold_base_task():
    from pipelines.incremental_gold import load_gold_base_incremental
    logger.info("[DAG] Starting creation of gold base table task")
    load_gold_base_incremental(date)


# --------------------
# Task 4  
# --------------------
def run_gold_aggregation_task():
    from pipelines.gold_pipeline import generate_gold_aggregations
    logger.info("[DAG] Starting Generating analytical tables task")
    generate_gold_aggregations()


# --------------------
# Task 5  
# --------------------
def run_skill_demand_task():
    from pipelines.gold_skill_demand import generate_skill_demand_table
    logger.info("[DAG] Starting Gold skills vs demand task")
    generate_skill_demand_table()

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

    run_daily_ingestion = PythonOperator(
        task_id="data_ingestion", 
        python_callable=run_ingestion_task
    )
    silver_task = PythonOperator(
        task_id="bronze_to_silver_conversion", 
        python_callable=run_bronze_to_silver_task
    )
    gold_base_task = PythonOperator(
        task_id="gold_base_create", 
        python_callable=run_gold_base_task
    )
    gold_aggregation_task = PythonOperator(
        task_id="gold_pipeline", 
        python_callable=run_gold_aggregation_task
    )
    gold_skill_demand_task = PythonOperator(
        task_id="gold_skill_demand_table", 
        python_callable=run_skill_demand_task
    )


run_daily_ingestion>>silver_task >> gold_base_task >> gold_aggregation_task >> gold_skill_demand_task



    # task = PythonOperator(task_id="date_check", python_callable=check_date)