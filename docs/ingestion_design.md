# Ingestion Pipeline Design
## Pagination Strategy

Rule:
- For each country (US, UK, AU), we will fetch multiple pages.
- Each page returns up to 50 jobs.

Total expected jobs per day: ~250


## Failure Handling Strategy

If an API call fails:
- Wait 5 seconds
- Retry up to 3 times
- If still failing, skip that page and log the error

Example log:
[2026-01-20 08:00] ERROR: Failed to fetch page 2 for US

We prefer partial data over no data.
Meaning: 
If UK fails but US succeeds, we still save US data.


## How data will be merged

- Fetch US jobs → store in list
- Fetch UK jobs → append to same list
- Fetch AU jobs → append to same list
- Save ONE combined file per day:
  data/bronze/raw_jobs_YYYY_MM_DD.json


## Bronze JSON structure
{
  "ingestion_date": "2026-01-20",
  "source": "adzuna",
  "jobs": [
    {
      "job_id": "12345",
      "title": "Data Engineer",
      "company": "Amazon",
      "city": "Seattle",
      "country": "US",
      "salary": "$90k-$120k",
      "description": "Work with Python and SQL",
      "posted_date": "2026-01-19"
    }
  ]
}
This structure will be used for ALL days.

## Ingestion Flow Diagram
Adzuna API
     |
     v
Fetch US pages ----\
Fetch UK pages -----> Combine jobs ---> Save JSON ---> Upload to Google Drive
Fetch AU pages ----/
