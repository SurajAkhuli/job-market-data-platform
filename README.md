# Job Market Data Platform

An end-to-end data pipeline that ingests job posting data from the Adzuna API and processes it through a Medallion Architecture (Bronze → Silver → Gold). Orchestrated using Apache Airflow within a Dockerized environment.

---

## Overview

This project builds a structured data pipeline for collecting, cleaning, and analyzing job market data across multiple countries and roles. The pipeline runs inside Docker with Airflow handling task orchestration — no manual script execution is required once the environment is running.

The output is a set of analytics-ready tables in DuckDB, covering role distribution, salary ranges, country-level hiring activity, and keyword-based skill demand.

---

## Problem Statement

Job posting data from public APIs is inconsistent: missing salary fields, duplicate listings, non-standard role titles, and salary figures in different currencies make direct analysis unreliable. Without a structured processing layer, any downstream analysis built on raw API data will produce misleading results.

Manually collecting and cleaning this data across multiple countries and roles is time-consuming and not reproducible.

---

## Solution Approach

The pipeline applies a three-layer Medallion Architecture to progressively refine raw API data into analysis-ready tables:

- **Bronze**: Raw JSON data stored as-is from the API
- **Silver**: Validated, cleaned, and standardized Parquet files
- **Gold**: Aggregated DuckDB tables ready for querying

Each layer is a separate processing stage with its own logic, making the pipeline easy to debug, extend, or rerun independently. Each layer is independently rerunnable and loosely coupled — a failure or change in one layer does not require reprocessing the others.

---

## Architecture

```
Adzuna API
    |
    v
[Bronze Layer]  →  Raw JSON files (one per ingestion date)
    |
    v
[Silver Layer]  →  Parquet files (validated, cleaned, standardized)
    |
    v
[Gold Layer]    →  DuckDB tables (incremental base table + aggregations)
```

### Layer Details

**Bronze**
Stores the raw API response as JSON, exactly as received. No transformations are applied. Preserves the original data for reprocessing if needed.

**Silver**
Applies data quality checks and transformations:
- Schema validation against a fixed column set
- Null filtering on critical fields (job ID, title, country)
- Salary validation (min must be ≤ max)
- Duplicate removal by `job_id`
- Description text normalization
- Country code lowercasing
- Currency normalization using fixed INR multipliers for cross-country comparison
- Role standardization using rule-based keyword matching
- Rejected records written to a separate file for review

**Gold**
Loads validated data into DuckDB and generates aggregation tables:
- `gold_jobs_base` — deduplicated master table, updated incrementally
- Role distribution summary
- Salary distribution per role
- Country-level hiring overview
- Skill demand table (keyword extraction from job descriptions)

---

## Data Pipeline Flow

The Airflow DAG runs 5 tasks in sequence:

```
data_ingestion
    → bronze_to_silver_conversion
        → gold_base_create
            → gold_pipeline
                → gold_skill_demand_table
```

| Task | Description |
|------|-------------|
| `data_ingestion` | Fetches job postings from Adzuna API across 5 countries and 4 roles |
| `bronze_to_silver_conversion` | Validates, cleans, and transforms raw JSON into Parquet |
| `gold_base_create` | Incrementally loads cleaned records into DuckDB base table |
| `gold_pipeline` | Generates role, salary, and country aggregation tables |
| `gold_skill_demand_table` | Extracts skill keywords and generates demand summary |

The DAG has no schedule set (`schedule=None`) and is triggered manually. Tasks are configured with 2 retries and a 5-minute retry delay.

---

## Key Features

- Multi-country ingestion: India (IN), United States (US), Australia (AU), Great Britain (GB), Canada (CA)
- Multi-role coverage: Data Engineer, Data Scientist, Analytics Engineer, Data Platform Engineer
- Pagination handling during API ingestion
- Partial failure tolerance: ingestion errors are logged per country/role combination; the pipeline continues
- Strict schema enforcement at the Silver layer
- Rule-based role classification to standardize inconsistent job titles
- Fixed-multiplier currency normalization for approximate cross-country salary comparison
- Keyword-based skill extraction from job descriptions (Python, SQL, Spark, etc.)
- Centralized logging to both file and console across all pipeline stages

---

## Data Quality Strategy

Data quality is enforced entirely at the Silver layer before any data reaches Gold.

- **Schema validation**: Any record missing required columns is rejected
- **Null filtering**: Records missing `job_id`, `title`, or `country` are dropped
- **Salary validation**: Records where `salary_min > salary_max` are flagged and removed
- **Deduplication**: Records with duplicate `job_id` values within a batch are removed
- **Text normalization**: Job descriptions are stripped of excess whitespace and special characters
- **Rejected records**: All dropped records are written to a separate rejected file, not silently discarded

This approach ensures that Gold layer tables only contain records that have passed all validation checks.

---

## Incremental Processing

The Gold base table (`gold_jobs_base`) uses an upsert-style incremental load rather than a full reload on each run.

The logic works as follows:
1. For each incoming batch, collect all `job_id` values
2. Delete any existing rows in `gold_jobs_base` that match those `job_id` values
3. Insert the new batch

This means re-running the pipeline for the same date will not create duplicate records. It also means the base table accumulates data across multiple pipeline runs without growing redundantly. Aggregation tables are regenerated from the full base table after each incremental load.

---

## Example Insights Generated

The Gold layer produces the following outputs after each pipeline run:

- **Role distribution**: Count of job postings per standardized role (e.g., how many Data Engineer vs Data Scientist postings)
- **Salary by role**: Minimum, maximum, and average salary ranges per role, normalized to a common currency scale
- **Country overview**: Number of job postings per country, with salary summaries
- **Skill demand**: Frequency of skill keywords (Python, SQL, Spark, Kafka, dbt, Airflow, etc.) extracted from job descriptions

Note: Salary data from the Adzuna API is often missing or null, particularly for Indian job postings. Salary-based insights are more reliable for US, GB, and AU records.

---

## Example Record (Silver Layer)

A cleaned and validated record after the Bronze → Silver transformation:

```json
{
  "job_id": "5583490782",
  "title": "data engineer",
  "company": "Zemoso Technologies",
  "city": "Hyderabad, Telangana",
  "country": "in",
  "salary_min": null,
  "salary_max": null,
  "description": "Job Title: Data Engineer Experience: 5 Years Location: Chennai/Hyderabad...",
  "posted_date": "2026-01-14T09:16:45Z",
  "standardized_role": "data engineer"
}
```

Fields applied at this stage: country lowercased, role standardized via keyword matching, description normalized, record passed all null and salary validation checks. Records that fail any check are written to a separate rejected file instead of being silently dropped.

---

## Project Structure

```
job-market-data-platform/
├── dags/                    # Airflow DAG definition (ETL_pipeline.py)
├── pipelines/               # Core pipeline logic
│   ├── ingest_pipeline.py   # Adzuna API ingestion
│   ├── bronze_to_silver.py  # Data quality + transformation
│   ├── incremental_gold.py  # Incremental DuckDB loading
│   ├── gold_pipeline.py     # Aggregation table generation
│   ├── gold_skill_demand.py # Skill keyword extraction
│   └── utils/
│       └── logger.py        # Centralized logging setup
├── config/
│   └── settings.yaml        # Countries, roles, paths, API config
├── docs/                    # Design documentation per layer
├── data/
│   ├── bronze/              # Raw JSON (one file per ingestion date)
│   ├── silver/              # Validated Parquet files
│   └── gold/                # DuckDB database + Parquet exports
├── Dockerfile               # Custom Airflow image with dependencies
├── docker-compose.yaml      # Airflow services (webserver, scheduler, triggerer)
└── requirements.txt         # Python dependencies
```

---

## Design Decisions

- **One JSON file per ingestion date in Bronze**: Simplifies tracking of what was ingested when and makes reprocessing a specific date straightforward.
- **Data quality enforced before analytics (fail-fast)**: All validation happens at Silver. Nothing reaches Gold unless it has passed schema, null, salary, and deduplication checks.
- **Incremental load instead of full refresh**: The Gold base table uses a delete-then-insert pattern per `job_id` batch. This avoids duplicates across runs without requiring a complete table rebuild each time.
- **DuckDB for analytical storage**: Chosen for lightweight, file-based analytical queries without requiring a running database server. Appropriate for local single-node workloads.
- **Pipeline code installed as a package**: The `pipelines/` module is installed into the Airflow container via `pip install`, so DAG tasks import it directly without path hacks or manual file copying.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Orchestration | Apache Airflow 3.1.0 |
| Containerization | Docker + Docker Compose |
| Data Processing | Pandas 3.0, PyArrow 23.0 |
| Analytical Storage | DuckDB 1.4.4 |
| Bronze Storage | JSON (local filesystem) |
| Silver Storage | Parquet (local filesystem) |
| Configuration | PyYAML |
| API Client | Requests |
| Logging | Python `logging` module (file + console) |

---

## How to Run

### Prerequisites

- Docker and Docker Compose installed
- Adzuna API credentials (App ID and API Key) — available at [developer.adzuna.com](https://developer.adzuna.com)
- At least 4 GB of RAM available to Docker

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/surajakhuli/job-market-data-platform.git
cd job-market-data-platform
```

**2. Set environment variables**

Create a `.env` file in the project root:

```env
AIRFLOW_UID=50000
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_api_key
```

**3. Build and start the containers**

```bash
docker compose up --build
```

This will build the custom Airflow image (with all dependencies installed via `requirements.txt`), initialize the Airflow database, and start the scheduler, webserver, and triggerer services.

**4. Access the Airflow UI**

Navigate to `http://localhost:8080` in your browser.

Default credentials:
- Username: `airflow`
- Password: `airflow`

**5. Trigger the pipeline**

In the Airflow UI, locate the `etl_pipeline` DAG and trigger it manually. The pipeline will run all 5 tasks in sequence.

### Data Output Locations (inside container)

| Layer | Path |
|-------|------|
| Bronze | `/opt/airflow/data/bronze/` |
| Silver | `/opt/airflow/data/silver/` |
| Gold | `/opt/airflow/data/gold/` |

---

## Who Can Use This

- **Data analysts** who want structured, query-ready job market data without manual collection
- **Hiring teams** tracking demand trends for specific roles across countries
- **Market researchers** studying compensation patterns or skill demand in data roles
- **Data engineering learners** looking for a concrete end-to-end pipeline implementation with Airflow and DuckDB

---

## What Manual Work This Replaces

Without this pipeline, the equivalent workflow would involve:

- Manually querying the Adzuna API for each country and role combination
- Handling pagination and saving raw responses
- Writing ad-hoc scripts to clean null values, remove duplicates, and standardize fields
- Manually converting salary currencies for cross-country comparison
- Re-running all processing steps from scratch on each new data pull
- Building aggregation queries by hand each time new data is added

This pipeline automates all of the above steps in a single Airflow DAG run.

---

## Limitations

- **Local environment only**: The pipeline runs on a local filesystem. There is no cloud storage, distributed processing, or horizontal scaling. Volume is constrained by available disk space and Docker memory.
- **No scheduling configured**: The DAG must be triggered manually. Automated daily runs require adding a cron schedule to the DAG definition.
- **Salary data coverage**: A large portion of job postings — particularly from India — do not include salary information in the Adzuna API response. Salary-based aggregations reflect only the subset of postings with available data.
- **Currency normalization is approximate**: Salary conversion uses fixed multipliers defined in `settings.yaml`. Exchange rates are not fetched dynamically and will drift over time.
- **Skill extraction is keyword-based**: Skill demand is derived from simple substring matching on job descriptions, not NLP or entity recognition. Results may overcount or miss variants of skill names.
- **Role standardization is rule-based**: Role classification uses keyword matching on job titles. Non-standard or ambiguous titles may be misclassified.
- **No data versioning**: There is no snapshot or versioning mechanism for Silver or Gold outputs. Reprocessing a date overwrites the previous output.
- **No monitoring or alerting**: Task failures are visible in the Airflow UI and logs only. There is no external alerting mechanism.

---

## Future Improvements

The following are concrete, realistic next steps — none of which are currently implemented:

- Add a cron schedule to the DAG for automated daily runs
- Parameterize the DAG to accept ingestion date as a runtime input rather than using `datetime.today()` at import time
- Add dynamic exchange rate fetching to replace fixed currency multipliers
- Partition Silver and Gold Parquet outputs by date for more efficient incremental reads
- Add a data freshness check task at the start of the DAG to skip runs when no new data is available
- Migrate storage to a cloud object store (S3 or GCS) to remove local filesystem dependency
- Add basic pipeline monitoring with email or Slack alerts on task failure