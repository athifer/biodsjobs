
# bioinfojobs.com

An open-source website for bioinformatics jo## Ethics & Compliance
- **Respects Terms of Service**: Only scrapes from sources that provide public APIs or explicitly allow programmatic access.
- **Rate limiting**: All requests are rate-limited to avoid overwhelming servers.
- **Legal sources only**: LinkedIn, Indeed, Glassdoor, and similar sites are excluded due to ToS restrictions.
- **Preferred sources**: Company ATS systems (Lever, Greenhouse), Y Combinator, and company career pages.
- Provide a DMCA/contact page for takedown or update requests.nting, aggregating relevant roles from pharma/biotech company sites and ATS sources (Lever, Greenhouse, Y Combinator). Focuses on legally accessible sources with public APIs or job feeds, avoiding sites that prohibit scraping.

## Features
- Aggregates jobs from company career pages and ATS sources with public APIs.
- Extracts job title, company, post date, source, description, and relevance score.
- Deduplicates overlapping listings.
- Fast keyword search and filtering by source/company.
- **Automatic updates every 4 hours** - jobs are refreshed automatically in the background.
- **Legally compliant** - only uses sources that allow programmatic access (Lever, Greenhouse, Y Combinator).
- Extensible: add new compliant scrapers for more sources easily.

## Quickstart

### 1) Backend Setup
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure Companies & Sources
Edit YAML files in `backend/` (e.g. `companies_all.yaml`) to add companies and sources. Example:
```yaml
greenhouse:
  - company: Benchling
    token: benchling
    careers_url: https://boards.greenhouse.io/benchling
lever:
  - company: GRAIL
    host: jobs.lever.co/grailbio
    careers_url: https://jobs.lever.co/grailbio
```

### 3) Ingest Jobs
Run the ingestion script to fetch and store jobs in the database:
```bash
python ingestor.py
```

### 4) Run the API Server
```bash
uvicorn app:app --reload --port 8000
```

### 5) Frontend
Open `frontend/index.html` in your browser. It queries `http://localhost:8000/api/jobs` for live job data.

## Adding New Sources
- To add a new compliant job board or ATS source, create a new module in `backend/scrapers/` (e.g. `workday.py`, `bamboohr.py`).
- Only add sources that provide public APIs, RSS feeds, or explicitly allow programmatic access.
- Implement a function `fetch_company_jobs(company)` or similar, returning a list of job dicts.
- Wire the new scraper into `ingestor.py`, `scheduler.py`, and/or `app.py`.

## Relevance Scoring
- Keywords for scoring are set in `backend/settings.py`.
- Tune to prioritize skills, technologies, or job titles of interest.

## Database
- Uses SQLite by default (`bioinfojobs.db`).
- Switch to Postgres by changing `DATABASE_URL` in `settings.py` for production.

## Ethics & Compliance
- Respect each source’s Terms of Service and robots.txt. Many sites (e.g., LinkedIn/Indeed) prohibit scraping; prefer official APIs, RSS feeds, or public endpoints.
- Cache responses, rate-limit requests, and identify your crawler in headers if scraping.
- Provide a DMCA/contact page for takedown or update requests.

## Contributing
- PRs welcome for new sources, bug fixes, and features!
