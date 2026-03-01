# Pipeline Schedule

The ingestion pipeline will run automatically every day at:

08:00 AM IST

Workflow each day:

1. Ingest API data (pipelines/ingest_api.py)
2. Store raw data in:
   data/bronze/raw_jobs_YYYY_MM_DD.json

3. Upload raw file to:
   Google Drive/job-market-data-lake/data/bronze/

This job will be automated using Airflow in:
dags/ETL_pipeline.py
