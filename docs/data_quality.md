# Data Quality Layer

## Purpose
The data quality layer ensures that only valid and consistent data moves from Bronze to Silver.

This prevents:
- invalid records
- schema issues
- inconsistent values
- downstream corruption

---

## Location in Pipeline
Implemented in:
pipelines/bronze_to_silver.py

Executed immediately after reading raw JSON.

---

## Validation Rules

### 1. Schema Validation
Ensures required columns are present:
- job_id
- title
- company
- city
- country
- salary fields
- description
- posted_date
- ingestion_date

If missing → pipeline fails.

---

### 2. Null Validation
Critical columns:
- job_id
- title
- country

Rows with null values are rejected.

---

### 3. Salary Validation
Condition:
salary_min <= salary_max

Invalid rows are rejected.

---

### 4. Duplicate Handling
Duplicate job_id entries are removed (keeping latest).

---

### 5. Description Quality
Rows with description length < 30 are rejected.

---

### 6. Country Validation
Allowed:
IN, US, AU, GB, CA

Invalid values are rejected.

---

## Output

### Valid Data
Saved to:
data/silver/jobs_cleaned_YYYY_MM_DD.parquet

---

### Rejected Data
Saved to:
data/silver_rejected/rejected_YYYY_MM_DD.parquet

---

## Summary Logging
Each run logs:

- total rows
- valid rows
- rejected rows
- reason counts