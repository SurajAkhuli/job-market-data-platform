# Pipeline Architecture

## Overview

The pipeline follows a Medallion Architecture:

Bronze → Silver → Gold

---

## Bronze Layer
- Raw JSON data from Adzuna API
- Stored as-is
- No transformation

---

## Silver Layer
- Data cleaning and transformation
- Data quality checks applied
- Schema standardization

---

## Gold Layer
- Analytical tables
- Aggregations for reporting
- Optimized for querying

---

## Orchestration

Managed using Apache Airflow:

DAG: etl_pipeline

Task Flow:
1. ingestion
2. bronze_to_silver
3. gold_base
4. gold_aggregation
5. skill_demand

---

## Storage

- Local filesystem (Airflow volume)
- Format: Parquet (Silver & Gold)
- Database: DuckDB

---

## Logging

- Centralized logging via custom logger
- File + console logs
- Structured log format