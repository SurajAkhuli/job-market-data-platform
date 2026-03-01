# Job Market Data Platform

A production-style data engineering pipeline that ingests, processes, and analyzes global job market data to generate actionable insights.

---

## Problem

Raw data from APIs is often:
- inconsistent
- incomplete
- difficult to analyze

Without proper pipelines, this leads to unreliable insights.

---

## Solution

This project implements a structured data platform using a Medallion Architecture:

Bronze → Raw ingestion  
Silver → Cleaned and validated data  
Gold → Analytics-ready datasets  

---

## Key Capabilities

- Multi-country job data ingestion via API
- Strong data quality enforcement layer
- Incremental data loading (no full reloads)
- Currency normalization for cross-country analysis
- Role standardization using rule-based classification
- Skill demand extraction from job descriptions
- Automated orchestration using Apache Airflow

---

## Example Insights Generated

- Role demand distribution (Data Engineer vs Scientist vs Analyst)
- Salary trends across countries
- Skill demand (Python, SQL, Spark, etc.)
- Country-level hiring patterns

---

## Architecture

Adzuna API  
→ Bronze (JSON)  
→ Silver (Parquet + Data Quality)  
→ Gold (DuckDB + Analytics Tables)

---

## Why This Matters

This project reflects real-world data engineering challenges:

- Handling unreliable external data
- Enforcing data quality before analytics
- Designing incremental pipelines
- Building maintainable data layers

---

## Tech Stack

- Python (Pandas, PyArrow)
- Apache Airflow
- DuckDB
- Docker

---

## Future Improvements

- Cloud storage (S3/GCS)
- Data partitioning
- Monitoring & alerting
- Schema versioning