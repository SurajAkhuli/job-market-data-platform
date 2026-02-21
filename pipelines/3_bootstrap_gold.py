from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
SILVER_PATH = BASE_DIR / "data" / "silver" / "*.parquet"

conn = duckdb.connect("data.db")

# Create table schema
conn.execute(f"""
CREATE TABLE IF NOT EXISTS gold_jobs_base AS
SELECT *
FROM read_parquet('{SILVER_PATH}')
WHERE 1=0;
""")

# drop index column that created by df in data manipulation step (B -> S)
conn.execute("""
ALTER TABLE gold_jobs_base DROP COLUMN IF EXISTS __index_level_0__;
""")

# Initial full load with global deduplication
conn.execute(f"""
INSERT INTO gold_jobs_base
SELECT job_id, title, company, city, country, salary_min, salary_max, salary_predicted, description, posted_date, ingestion_date, standardized_title
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY job_id
               ORDER BY ingestion_date DESC
           ) AS rn
    FROM read_parquet('{SILVER_PATH}')
)
WHERE rn = 1;
""")



conn.close()