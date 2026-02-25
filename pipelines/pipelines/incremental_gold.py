from pathlib import Path
import duckdb
import sys
from pipelines.utils.logger import get_logger
logger = get_logger(__name__)

# pass silver file or partition path explicitly
# date = sys.argv[1]

def gold_base_create(date):

    BASE_DIR = Path("/opt/airflow")
    filename= "jobs_cleaned_" + date + ".parquet" 
    SILVER_FILE = BASE_DIR / "data" / "silver" / filename

    logger.info("Connecting to database")
    conn = duckdb.connect("data/data.db")

    conn.execute("BEGIN;")

    logger.info("Creating gold base table")
    # delete existing versions
    conn.execute(f"""
    DELETE FROM gold_jobs_base
    WHERE job_id IN (
        SELECT job_id
        FROM read_parquet('{SILVER_FILE}')
    );
    """)

    # direct insert 
    conn.execute(f"""
    INSERT INTO gold_jobs_base
    SELECT job_id, title, company, city, country, salary_min, salary_max, salary_predicted, description, posted_date, ingestion_date, standardized_title
    FROM read_parquet('{SILVER_FILE}');
    """)
    logger.info("Gold base table created and stored in database")

    conn.execute("COMMIT;")
    # What this guarantees? --> Both statements succeed → committed
    #                           Any failure → entire transaction rolls back

    conn.close()


# python3.11 pipelines/4_incremental_gold.py YYYY_MM_DD
