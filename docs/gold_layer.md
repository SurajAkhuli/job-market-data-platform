# Gold Layer Design

## Purpose
The Gold layer provides analytical datasets for reporting and insights.

---

## Tables Generated

### 1. gold_base.parquet
- Full cleaned dataset
- Source for all downstream analysis

---

### 2. gold_role_distribution.parquet
- role vs job_count

---

### 3. gold_salary_distribution_role.parquet
- role vs salary stats:
  - min
  - max
  - avg

---

### 4. gold_country_overview.parquet
- country vs:
  - job_count
  - avg_salary

---

### 5. gold_skill_demand.parquet
- skill vs job_count
- extracted from job descriptions

---

## Processing Engine
DuckDB is used for:
- aggregation
- transformation
- file output