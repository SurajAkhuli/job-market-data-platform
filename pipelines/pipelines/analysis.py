import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PATH = BASE_DIR / "data" / "gold" / "gold_skill_demand.parquet"

# duckdb.sql(f"""
# -- SELECT count(*) FROM read_parquet('{PATH}');
# SELECT * FROM read_parquet('{PATH}');
# """).show()
con = duckdb.connect("data.db")
con.sql("select count(*) from gold_jobs_base").show()

# con = duckdb.connect("data.db")
# # con.sql("select count(*) as count from gold_jobs_base").show()
# con.sql("show tables").show()
# con.close()
# print(PATH)

# duckdb.sql(f"select *from read_parquet('{PATH}')").show()