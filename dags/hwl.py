from airflow.decorators import dag, task
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG using the @dag decorator
@dag(
    dag_id='single_file_simple_pipeline',
    default_args=default_args,
    description='A simple, single-file DAG example',
    schedule=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example'],
)
def simple_pipeline():
    
    @task()
    def extract():
        print("Extracting data...")
        return {"data": 100}

    @task()
    def transform(data_dict: dict):
        print("Transforming data...")
        return data_dict["data"] * 10

    @task()
    def load(final_data: int):
        print(f"Loading {final_data} to destination...")

    # Set dependencies
    data = extract()
    transformed_data = transform(data)
    load(transformed_data)

# Instantiate the DAG
simple_pipeline()
