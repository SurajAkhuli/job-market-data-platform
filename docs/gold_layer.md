
---
# Gold Layer (Analytical Modeling)

## Purpose

Serve analytics-ready datasets optimized for querying and reporting.

---

## Base Table

`gold_jobs_base`

Acts as:
- Single source of truth
- Incrementally updated dataset

---

## Aggregations

### Role Distribution
Job count per standardized role

---

### Salary Distribution
Min / Max / Avg salary per role

---

### Country Overview
Job demand + salary trends by country

---

### Skill Demand
Extracted using keyword matching on descriptions

---

## Engine

DuckDB:
- In-memory + disk hybrid
- Optimized for analytical workloads

---

## Design Insight

Gold layer is **read-optimized**, while Silver is **write-optimized**.