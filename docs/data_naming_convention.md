# Data Naming Convention & Ingestion Plan

## Countries to collect
- United States (US)
- United Kingdom (UK)
- Australia (AU)

Reason:
These are major English-speaking tech job markets.

## Job roles to collect
I will search for:
- "Data Engineer"
- "Analytics Engineer"
- "Data Platform Engineer"

## Daily ingestion target
Target: 250 jobs per day (Adzuna free limit)

Expected split:
- US: 120 jobs
- UK: 70 jobs
- AU: 60 jobs

## File naming rule (Bronze layer)

Every day I will create one file named:

data/bronze/raw_jobs_YYYY_MM_DD.json

Example:
data/bronze/raw_jobs_2026_01_20.json

This file will contain jobs from ALL three countries combined.

## Cloud storage (Google Drive)

Google Drive structure will be:

Google Drive/
 └── data/
     ├── bronze/
     ├── silver/
     └── gold/

Each day, the raw file will be uploaded to:
Google Drive/data/bronze/
