# Airflow Parameterization Strategy

## Current Approach

This pipeline uses PythonOperator, where parameters (like date) are passed directly inside Python functions instead of CLI arguments.

Example:

- DAG generates date using:
  datetime.today().strftime("%Y_%m_%d")

- Passed to:
  transform_bronze_to_silver(date)
  load_gold_base_incremental(date)

---

## Why Not BashOperator

BashOperator + argparse is useful when:
- Running standalone scripts
- Passing CLI arguments

In this project:
- Code is modular Python
- Executed within Airflow runtime
- No need for CLI parsing

---

## When Jinja is Useful

Jinja templating is useful when:
- Using Airflow execution date (`{{ ds }}`)
- Dynamic runtime parameters

Example:
{{ ds }} → execution date

---

## Current Limitation

The pipeline uses:
datetime.today()

Instead of:
Airflow execution date

This means:
- Backfills are not accurate
- Runs are tied to system time

---

## Future Improvement

Replace:

datetime.today()

With:

Airflow context (`{{ ds }}` or context variables)

To support:
- Backfills
- Reproducibility