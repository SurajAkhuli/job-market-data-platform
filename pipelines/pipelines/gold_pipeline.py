from pathlib import Path
import duckdb
from pipelines.utils.logger import get_logger
logger = get_logger(__name__)

# BASE_DIR = Path(__file__).resolve().parent.parent

def gold_pipeline(): 
    BASE_DIR = Path("/opt/airflow")

    logger.info("Connecting to database.. ")
    conn = duckdb.connect("data/data.db")

    GOLD_FILE_PATH = BASE_DIR / "data" / "gold"

    conn.execute("BEGIN;")

    # conn.execute(f"""
    # COPY (
    #     ALTER TABLE gold_jobs_base
    #     DROP COLUMN description, title, company, posted_date
    # )
    # TO '{(GOLD_FILE_PATH / "gold_base.parquet").as_posix()}'
    # (FORMAT PARQUET)
    # """)

    logger.info("Start table creation for gold tables")
    conn.execute(f"""
    COPY (
        SELECT * FROM gold_jobs_base
    )
    TO '{(GOLD_FILE_PATH / "gold_base.parquet").as_posix()}'
    (FORMAT PARQUET)
    """)


    conn.execute(f"""
    COPY(
        SELECT standardized_title as role, count(*) as job_count
        FROM gold_jobs_base
        GROUP BY standardized_title
        order by job_count desc
        ) to '{(GOLD_FILE_PATH / "gold_role_distribution.parquet").as_posix()}'
                (FORMAT PARQUET)
    """)


    conn.execute(f"""
    COPY(
        SELECT standardized_title as role, 
                min(salary_min) as min_salary, 
                max(salary_max) as max_salary, 
                ((min(salary_min) + max(salary_max))/2) as avg_salary  
        FROM gold_jobs_base
        GROUP BY standardized_title
        ) to '{(GOLD_FILE_PATH / "gold_salary_distribution_role.parquet").as_posix()}'
                (FORMAT PARQUET)
    """)

    conn.execute(f"""
    COPY(
        SELECT country, count(*) as job_count,
                ((min(salary_min) + max(salary_max))/2) as avg_salary
        FROM gold_jobs_base
        GROUP BY country
        ) to '{(GOLD_FILE_PATH / "gold_country_overview.parquet").as_posix()}'
                (FORMAT PARQUET)
    """)
    logger.info("gold_base, gold_role_distribution, gold_salary_distribution_role tables are created and stored as parquet")

    # conn.execute(f"""
    # COPY(
    #     SELECT city, country, count(*) as job_count
    #     FROM gold_jobs_base
    #     GROUP BY city
    #     ) to '{(GOLD_FILE_PATH / "gold_jobs_by_city.parquet").as_posix()}'
    #              (FORMAT PARQUET)
    # """)

    conn.execute("COMMIT;")
    conn.close()

#     print("successfully all gold tables are created")

