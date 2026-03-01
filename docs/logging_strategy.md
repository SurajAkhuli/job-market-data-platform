# Logging Strategy

## Design

Centralized logging via custom logger:

- File logging
- Console logging (Airflow UI)

---

## Log Format
[timestamp] [level] [module] message


---

## Coverage

- Ingestion events
- Data quality checks
- Transformation steps
- Gold loading
- Aggregations

---

## Example
[INFO] [INGEST] country=US page=2 jobs_fetched=50
[DQ] rejected_rows=120
[GOLD][INSERT] rows_inserted=2000


---

## Purpose

- Debugging
- Monitoring pipeline health
- Observability for failures