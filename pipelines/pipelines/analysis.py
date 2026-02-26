import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PATH = BASE_DIR / "data" / "gold" / "result.parquet"

duckdb.sql(f"select count(*) from read_parquet('{PATH}')").show()
duckdb.sql(f"select * from read_parquet('{PATH}')").show()

# duckdb.sql("""
# select round(10.236599,2) 
# """).show()