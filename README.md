# bioinfojobs (starter)

A minimal end-to-end prototype for aggregating bioinformatics roles from common ATS sources (Lever, Greenhouse).

## Quickstart

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 2) Ingest some companies
Edit `backend/companies.yaml` to include the ATS source and company handle/token.
Examples:
```yaml
companies:
  - { source: lever, company: recursionsciences }   # change to real handle
  - { source: greenhouse, company: modernatx }      # change to real board token
```
Then run:
```bash
cd backend
python ingestor.py
```

### 3) Frontend
Open `frontend/index.html` in your browser. It queries `http://localhost:8000/api/jobs`.

## Notes

- Relevance scoring is a simple keyword-based heuristic. Tune keywords in `backend/settings.py`.
- Storage is SQLite by default (`bioinfojobs.db`). Swap `DATABASE_URL` to Postgres for production.
- Add new sources by creating a module in `backend/scrapers/` and wiring it in `app.py`.

## Ethics & Compliance

- Always respect each source’s Terms of Service and robots.txt. Many sites (e.g., LinkedIn/Indeed) prohibit scraping. Prefer official APIs, RSS feeds, or company ATS JSON endpoints (Lever/Greenhouse are widely used and provide public endpoints).
- Cache responses, rate-limit, and identify your crawler in headers if you add HTTP scraping.
- Provide a DMCA/contact page for takedown or update requests.
