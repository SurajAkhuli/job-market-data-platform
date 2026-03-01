# Pipeline Scheduling

## Current State

The DAG is NOT scheduled.
schedule = None


This means:
- Runs must be triggered manually

---

## Intended Schedule (Future)

Daily run at:
08:00 AM IST

---

## Recommendation

Set:

```python
schedule = "@daily"

and control execution time via Airflow configuration.