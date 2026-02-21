# Logging Strategy

All pipeline errors will be stored in:

logs/ingestion_errors.log

Each log entry must contain:
- Timestamp
- Step of failure (API call, file save, upload, etc.)
- Error message

Example log format:

[2026-01-20 08:00] ERROR in ingest_api.py: API timeout on page 3
