# Global Job Market Data Lake

This project builds an automated data pipeline that:
- Fetches real job data from Adzuna API daily
- Stores raw data in a Bronze layer
- Cleans and transforms data into Silver layer
- Creates analytical Gold tables
- Supports analytics via DuckDB and Power BI
