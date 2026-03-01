
---

# ✅ 2. `pipeline_architecture.md` (REWRITE)

```md
# Pipeline Architecture (Production-Level Design)

## System Overview

This pipeline follows a layered Medallion Architecture with clear separation of concerns:

- Bronze → Raw ingestion (immutable)
- Silver → Cleaned, validated, standardized
- Gold → Analytical modeling (query-optimized)

---

## Data Flow

Adzuna API  
→ Bronze (JSON)  
→ Silver (Parquet)  
→ Gold Base Table (DuckDB)  
→ Aggregated Gold Tables  

---

## Layer Details

### Bronze Layer
- Format: JSON
- Nature: Immutable, append-only
- Content: Raw API response (flattened)
- File Pattern:
data/bronze/raw_jobs_YYYY_MM_DD.json


---

### Silver Layer
- Format: Parquet (columnar, compressed)
- Purpose:
- Data cleaning
- Validation
- Standardization

Key transformations:
- Schema enforcement
- Null filtering (critical fields)
- Salary validation
- Currency normalization
- Text cleaning
- Role standardization

Rejected records stored separately:
data/silver_rejected/rejected_YYYY_MM_DD.parquet


---

### Gold Layer

#### 1. Base Table (Incremental)
- Engine: DuckDB
- Table: `gold_jobs_base`
- Strategy:
  - Delete existing job_ids from incoming batch
  - Insert new records
  - Guarantees idempotency

---

#### 2. Aggregated Tables

Generated as Parquet:

- `gold_role_distribution`
- `gold_salary_distribution_role`
- `gold_country_overview`
- `gold_skill_demand`

---

## Orchestration

Managed via Airflow DAG:

`etl_pipeline`

Task dependencies:
ingestion
→ bronze_to_silver
→ incremental_gold_load
→ gold_aggregations
→ skill_demand


---

## Storage

| Layer   | Format   | Location |
|--------|--------|---------|
| Bronze | JSON   | Local FS |
| Silver | Parquet| Local FS |
| Gold   | DuckDB + Parquet | Local FS |

---

## Logging

Centralized logging via custom logger:
- File logs
- Console logs (Airflow UI)
- Structured messages per stage