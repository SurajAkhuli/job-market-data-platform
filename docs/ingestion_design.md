# Ingestion Pipeline Design

## Data Source

Adzuna Job Search API

---

## Extraction Strategy

For each:
- country
- role
- page

We fetch:
countries × roles × pages


---

## Pagination

- Max ~50 jobs per page
- Configurable page depth (currently 6)

---

## Failure Handling

- Retry logic (implicit via loop)
- Errors logged per page
- Pipeline continues (partial success allowed)

---

## Data Model (Bronze)

```json
{
  "ingestion_date": "YYYY-MM-DD",
  "source": "adzuna",
  "jobs": [...]
}
Each job is flattened into structured fields.