# BioDSJobs - Biotech Job Aggregation Platform

## Overview
A comprehensive job aggregation platform specifically designed for biotech, pharmaceutical, and life sciences companies. The system scrapes job postings from multiple sources including Greenhouse, Workday, Lever, Bamboo, and company career pages.

## Current Performance
- **Total Jobs:** 638+ active positions
- **Companies:** 75+ biotech/pharma companies  
- **Success Rate:** ~85% of companies returning jobs
- **Update Frequency:** Configurable (default: every 6 hours)

## Architecture

### Backend Components
- **FastAPI Application** (`app.py`) - REST API server
- **Job Ingestor** (`ingestor.py`) - Main scraping orchestrator
- **Database Layer** (`db.py`, `models.py`) - SQLAlchemy with SQLite
- **Advanced Scraper** (`advanced_scraper.py`) - Enhanced scraping engine
- **Specialized Scrapers** (`scrapers/`) - Platform-specific scrapers

### Frontend
- **Single Page Application** (`frontend/index.html`) - Modern web interface
- **Features:** Job filtering, pagination, search, responsive design

## Key Features

### Advanced Scraping Capabilities
1. **Multi-Platform Support**
   - Greenhouse API integration
   - Workday API detection and scraping
   - Lever API support
   - iCIMS platform detection
   - Bamboo HR integration
   - Generic HTML parsing

2. **Intelligent Content Detection**
   - Automatic site type detection
   - JSON-LD structured data parsing
   - Dynamic content handling
   - Biotech keyword filtering

3. **Robust Error Handling**
   - Graceful fallbacks between scraping methods
   - Rate limiting and retry logic
   - Comprehensive logging

### Job Processing
- **Biotech Relevance Filtering:** Advanced keyword matching
- **Deduplication:** Prevents duplicate job entries
- **Data Validation:** Ensures job data quality
- **URL Normalization:** Handles relative and absolute URLs

## Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment (recommended)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd biodsjobs

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database
cd backend
python -c "from db import init_db; init_db()"
```

### Running the Application
```bash
# Start the backend server
cd backend
python start_server.py

# Access the application
# Frontend: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## Configuration

### Adding New Companies
Edit `backend/companies.yaml`:

```yaml
greenhouse:
  - company: Company Name
    token: company-token
    careers_url: https://boards.greenhouse.io/company-token

workday:
  - company: Company Name
    token: company-token
    careers_url: https://company.wd1.myworkdayjobs.com/careers

comprehensive:
  - company: Company Name
    token: company-token
    careers_url: https://company.com/careers
```

## API Endpoints

### Jobs
- `GET /jobs` - Retrieve jobs with filtering
  - Parameters: `location`, `job_type`, `company`, `limit`, `offset`
- `GET /jobs/{job_id}` - Get specific job details

### Companies
- `GET /companies` - List all companies
- `GET /companies/{company_id}/jobs` - Get jobs for specific company

### System
- `POST /trigger-ingestion` - Manually trigger job scraping
- `GET /health` - System health check

## Enhanced Scraping Engine

The `AdvancedScraper` class provides sophisticated scraping capabilities:

1. **Site Type Detection** - Analyzes page content to determine platform type
2. **API-First Approach** - Attempts API endpoints before HTML parsing
3. **Fallback Strategies** - Multiple parsing approaches for resilience
4. **Content Extraction** - JSON-LD structured data parsing and advanced CSS selectors

## Deployment

### Production Deployment
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "start_server.py"]
```

## Contributing

### Adding New Scrapers
1. Create scraper file in `scrapers/` directory
2. Implement `fetch_company_jobs(token)` function
3. Add company configurations to `companies.yaml`
4. Update ingestor to include new scraper

## Ethics & Compliance
- **Respects Terms of Service**: Only scrapes from sources that provide public APIs or explicitly allow programmatic access
- **Rate limiting**: All requests are rate-limited to avoid overwhelming servers
- **Legal sources only**: LinkedIn, Indeed, Glassdoor excluded due to ToS restrictions
- **Preferred sources**: Company ATS systems (Lever, Greenhouse), Y Combinator, and company career pages

## License
MIT License - see LICENSE file for details
