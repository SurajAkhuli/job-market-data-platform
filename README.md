# Global Job Market Data Pipeline

## Overview

This project builds an end-to-end data pipeline that ingests job market data from the Adzuna API and transforms it into analytical datasets.

---

## Key Features

- Automated ingestion using API
- Data quality validation layer
- Medallion architecture (Bronze → Silver → Gold)
- Incremental processing
- Analytical dataset generation using DuckDB
- Orchestration via Apache Airflow

---

## Tech Stack

- Python
- Apache Airflow
- DuckDB
- Pandas / PyArrow
- Docker

---

## Pipeline Flow

1. Ingestion → fetch job data
2. Bronze → raw JSON storage
3. Silver → cleaned + validated data
4. Gold → analytical tables

---

## Data Quality

The pipeline includes:
- schema validation
- null handling
- salary validation
- duplicate removal
- rejected data tracking

---

## How to Run

```bash
docker-compose up --build