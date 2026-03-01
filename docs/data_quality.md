# Data Quality Framework

## Objective

Ensure only high-integrity data propagates to analytical layers.

---

## Validation Stages

### 1. Schema Validation
Strict enforcement of required fields:

- job_id
- title
- company
- city
- country
- salary_min / salary_max
- description
- posted_date
- ingestion_date

Failure → pipeline stops

---

### 2. Null Handling

Critical fields:
- job_id
- title
- country

Invalid rows → rejected dataset

---

### 3. Salary Integrity

Constraint:
salary_min <= salary_max


---

### 4. Deduplication

- Based on `job_id`
- Keeps latest record

---

### 5. Text Quality

- Description length ≥ 30

---

### 6. Domain Validation

Allowed countries: IN, US, AU, GB, CA


---

## Outputs

| Type      | Location |
|----------|--------|
| Valid    | Silver layer |
| Rejected | silver_rejected |

---

## Observability

Each run logs:

- raw row count
- valid row count
- rejected row count
- rule-level failures

---

## Design Insight

This layer acts as a **contract enforcement boundary** between ingestion and analytics.