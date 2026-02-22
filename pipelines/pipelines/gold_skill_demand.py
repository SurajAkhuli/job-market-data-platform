import duckdb
from pathlib import Path


def gold_skill_demand_table(): 
    # ---------- Paths ----------
    # BASE_DIR = Path(__file__).resolve().parent.parent
    BASE_DIR = Path("/opt/airflow")
    GOLD_DIR = BASE_DIR / "data" / "gold"
    base_table= GOLD_DIR / "gold_base.parquet"
    GOLD_SKILL_TABLE = GOLD_DIR / "gold_skill_demand.parquet"

    # ---------- DuckDB connection ----------
    con = duckdb.connect()

    con.execute("begin;")
    # ---------- Register Silver data ----------
    con.execute(f"""
        CREATE OR REPLACE VIEW silver_jobs AS
        SELECT
            job_id,
            LOWER(description) AS description
        FROM read_parquet('{base_table}')
        WHERE description IS NOT NULL
    """)

    # ---------- Skill list ----------
    skills = [
        "python", "sql", "aws", "azure", "gcp",
        "spark", "airflow", "snowflake",
        "databricks", "kafka", "dbt"
    ]

    # ---------- Build skill detection SQL ----------
    skill_queries = []

    for skill in skills:
        skill_queries.append(f"""
            SELECT
                '{skill}' AS skill,
                COUNT(DISTINCT job_id) AS job_count
            FROM silver_jobs
            WHERE description LIKE '%{skill}%'
        """)

    final_query = " UNION ALL ".join(skill_queries)

    # ---------- Execute & write Gold ----------
    con.execute(f"""
        COPY (
            {final_query}
        )
        TO '{GOLD_SKILL_TABLE}'
        (FORMAT 'parquet', COMPRESSION 'snappy')
    """)
    con.execute("commit;")
    con.close()

    print("Gold skill demand table created:", GOLD_SKILL_TABLE)
