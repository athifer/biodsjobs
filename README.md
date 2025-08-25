# BioDSJobs - Biotech Job Aggregation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

A comprehensive job aggregation platform specifically designed for biotech, pharmaceutical, and life sciences companies. BioDSJobs aggregates data science and computational biology positions from multiple sources with intelligent filtering and modern web interface.

### 🎯 Built For
- **Data Scientists** in biotech/pharma
- **Bioinformaticians** and computational biologists  
- **Research Engineers** in life sciences
- **Machine Learning Engineers** working on healthcare
- **Biostatisticians** and clinical data analysts

## 📊 Current Performance

- **📋 Total Jobs:** 638+ active positions
- **🏢 Companies:** 75+ biotech/pharma companies  
- **✅ Success Rate:** ~85% of companies returning jobs
- **🔄 Update Frequency:** Automated every 6 hours
- **🎯 Relevance:** Advanced biotech keyword filtering

## 🏗️ Architecture

### Backend Components
- **🚀 FastAPI Application** (`app.py`) - High-performance REST API server
- **🔄 Job Ingestor** (`ingestor.py`) - Main scraping orchestrator with concurrent processing
- **💾 Database Layer** (`db.py`, `models.py`) - SQLAlchemy with SQLite (PostgreSQL ready)
- **🤖 Advanced Scraper** (`advanced_scraper.py`) - AI-powered scraping with site detection
- **🔌 Specialized Scrapers** (`scrapers/`) - Platform-specific optimized scrapers

### Frontend
- **💻 Modern SPA** (`frontend/index.html`) - Responsive single-page application
- **🎨 Features:** Real-time filtering, pagination, search, mobile-optimized design

## ✨ Key Features

### 🚀 Advanced Scraping Capabilities
1. **🌐 Multi-Platform Support**
   - Greenhouse API integration with rate limiting
   - Workday API detection and intelligent scraping
   - Lever API with host-based routing
   - iCIMS platform automatic detection
   - Bamboo HR integration
   - Generic HTML parsing with fallbacks

2. **🧠 Intelligent Content Detection**
   - Automatic site type detection (Workday, Greenhouse, etc.)
   - JSON-LD structured data parsing
   - Dynamic JavaScript content handling
   - Advanced biotech keyword filtering
   - Relevance scoring and ranking

3. **🛡️ Robust Error Handling**
   - Graceful fallbacks between scraping methods
   - Rate limiting and retry logic with exponential backoff
   - Individual company failure isolation
   - Comprehensive logging and monitoring

### 🔍 Job Processing
- **🎯 Biotech Relevance Filtering:** Machine learning-enhanced keyword matching
- **🔄 Smart Deduplication:** Prevents duplicate job entries across sources
- **✅ Data Validation:** Ensures job data quality and completeness
- **🔗 URL Normalization:** Handles relative and absolute URLs correctly

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (3.11+ recommended)
- **pip** or **conda** package manager
- **Virtual environment** (strongly recommended)

### 🎯 One-Command Setup
```bash
# Clone and deploy with automated script
git clone https://github.com/athifer/biodsjobs.git
cd biodsjobs
chmod +x deploy.sh
./deploy.sh
```

### 📋 Manual Installation
```bash
# Clone repository
git clone https://github.com/athifer/biodsjobs.git
cd biodsjobs

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database
cd backend
python -c "from db import init_db; init_db()"

# Run initial job ingestion
python ingestor.py
```

### 🚦 Running the Application
```bash
# Option 1: Smart startup (RECOMMENDED) 
./start_server.sh
# ✅ Automatically handles virtual environment
# ✅ Detects and uses available ports (8000, 8001, 8002, etc.)
# ✅ Shows helpful status information

# Stop the server
./stop_server.sh
# ✅ Cleanly stops all BioDSJobs servers

# Option 2: Manual startup
source .venv/bin/activate
cd backend
python start_server.py

# Option 3: Production startup
./start_production.sh
# ✅ Uses Gunicorn for production deployment

# Option 4: Development with auto-reload
source .venv/bin/activate
cd backend
uvicorn app:app --reload --port 8000
```

### 🌐 Access Points
- **Frontend:** http://localhost:8000 (or alternative port if 8000 is busy)
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

> **💡 Smart Port Detection:** The startup script automatically finds an available port if 8000 is in use!

## ⚙️ Configuration

### 🏢 Adding New Companies
Edit `backend/companies.yaml` to add companies to appropriate scraper platforms:

```yaml
# Greenhouse (preferred for startups/biotech)
greenhouse:
  - company: Company Name
    token: company-token
    careers_url: https://boards.greenhouse.io/company-token

# Workday (common for large pharma)
workday:
  - company: Company Name
    token: company-token
    careers_url: https://company.wd1.myworkdayjobs.com/careers

# Lever (growing biotech companies)
lever:
  - company: Company Name
    token: company-token
    host: jobs.lever.co/company-token
    careers_url: https://jobs.lever.co/company-token

# Comprehensive (custom company sites)
comprehensive:
  - company: Company Name
    token: company-token
    careers_url: https://company.com/careers
```

### 🔧 Environment Variables
Create a `.env` file for custom configuration:
```bash
DATABASE_URL=sqlite:///biodsjobs.db  # Use PostgreSQL for production
LOG_LEVEL=INFO
SCRAPING_INTERVAL=6  # Hours between automatic updates
MAX_CONCURRENT_REQUESTS=10
```

## 📡 API Reference

### 🔍 Jobs Endpoints
- `GET /api/jobs` - Retrieve jobs with advanced filtering
  - **Parameters:** `q` (search), `location`, `job_type`, `company`, `days`, `limit`, `offset`
  - **Example:** `/api/jobs?q=machine learning&location=San Francisco&days=7`

- `GET /api/jobs/{job_id}` - Get specific job details
- `GET /api/jobs/stats` - Get job statistics and counts

### 🏢 Companies Endpoints
- `GET /api/companies` - List all companies with job counts
- `GET /api/companies/{company_id}/jobs` - Get jobs for specific company

### 🔧 System Endpoints
- `POST /api/trigger-ingestion` - Manually trigger job scraping
- `GET /api/health` - System health check and status
- `GET /docs` - Interactive API documentation (Swagger UI)

### 📊 Example API Response
```json
{
  "jobs": [
    {
      "id": 1,
      "title": "Senior Data Scientist - Computational Biology",
      "company": "Genentech",
      "location": "South San Francisco, CA",
      "url": "https://careers.gene.com/jobs/123",
      "source": "greenhouse",
      "posted_at": "2025-08-24T10:30:00Z",
      "description": "Join our computational biology team..."
    }
  ],
  "total": 638,
  "page": 1,
  "limit": 25
}
```

## 🤖 Enhanced Scraping Engine

The `AdvancedScraper` class provides state-of-the-art scraping capabilities:

### 🔍 Intelligent Site Detection
- **Platform Recognition:** Automatically detects Workday, Greenhouse, Lever, iCIMS
- **Content Analysis:** Analyzes page structure and content type
- **Dynamic Adaptation:** Adjusts scraping strategy based on site characteristics

### 🎯 Multi-Strategy Approach
1. **API-First:** Attempts official APIs before HTML parsing
2. **Structured Data:** Parses JSON-LD and microdata formats
3. **Advanced CSS:** Uses intelligent selectors for job extraction
4. **Keyword Fallback:** Biotech-aware content discovery
5. **Error Recovery:** Graceful degradation with multiple fallbacks

### 🛡️ Reliability Features
- **Rate Limiting:** Respects server resources
- **Retry Logic:** Exponential backoff for failed requests
- **Error Isolation:** Individual company failures don't affect others
- **Monitoring:** Comprehensive logging and performance tracking

## 🚀 Deployment

### 🌟 Automated Deployment
```bash
# Production deployment with all optimizations
./deploy.sh --prod

# Development environment setup
./deploy.sh --dev

# Full deployment with interactive setup
./deploy.sh
```

### 🐳 Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Initialize database
RUN python -c "from db import init_db; init_db()"

EXPOSE 8000
CMD ["python", "start_server.py"]
```

```bash
# Build and run Docker container
docker build -t biodsjobs .
docker run -p 8000:8000 biodsjobs
```

### ⚡ Production with Gunicorn
```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000

# With systemd service (Linux)
sudo cp biodsjobs.service /etc/systemd/system/
sudo systemctl enable biodsjobs
sudo systemctl start biodsjobs
```

### ☁️ Cloud Deployment
The platform is ready for deployment on:
- **Heroku:** Use `Procfile` and `runtime.txt`
- **AWS:** EC2, ECS, or Lambda with API Gateway
- **Google Cloud:** App Engine or Cloud Run
- **Digital Ocean:** App Platform or Droplet

## 🛠️ Development

### 📁 Project Structure
```
biodsjobs/
├── 📚 README.md                    # This comprehensive guide
├── 🚀 deploy.sh                    # Automated deployment script
├── 🎨 frontend/
│   └── index.html                  # Modern SPA with pagination
└── ⚙️ backend/
    ├── 🌐 app.py                   # FastAPI server
    ├── 🔄 ingestor.py              # Main scraping orchestrator
    ├── 🤖 advanced_scraper.py      # AI-powered scraping engine
    ├── 🗄️ db.py, models.py         # Database layer
    ├── ⚙️ settings.py, util.py     # Configuration and utilities
    ├── 🏢 companies.yaml           # Company configurations
    ├── 📦 requirements.txt         # Python dependencies
    └── 🔌 scrapers/                # Platform-specific scrapers
        ├── greenhouse.py           # Greenhouse API integration
        ├── workday.py              # Workday scraping (enhanced)
        ├── comprehensive.py        # Generic site scraping (enhanced)
        ├── lever.py                # Lever API integration
        └── ycombinator.py          # Y Combinator integration
```

### 🔧 Adding New Scrapers
1. **Create scraper file** in `scrapers/` directory
2. **Implement required function:**
   ```python
   async def fetch_company_jobs(company_token: str) -> List[Dict[str, Any]]:
       # Your scraping logic here
       pass
   ```
3. **Add companies** to `companies.yaml` under appropriate section
4. **Update ingestor** to include new scraper in `main()` function
5. **Test thoroughly** with `python ingestor.py`

### 🧪 Testing
```bash
# Test individual scrapers
cd backend
python -c "from scrapers.greenhouse import fetch_company_jobs; print(len(fetch_company_jobs('benchling')))"

# Test full ingestion
python ingestor.py

# Test API endpoints
curl http://localhost:8000/api/jobs?limit=5
```

## 📊 Monitoring & Analytics

### 📈 Built-in Metrics
- **Job counts** by source, company, and date
- **Scraping success rates** and error tracking  
- **API response times** and request counts
- **Database performance** and query optimization

### 🔍 Logging
```bash
# View real-time logs
tail -f backend/biodsjobs.log

# Check error logs
grep ERROR backend/biodsjobs.log
```

### 📊 Performance Optimization
- **Database indexing** on commonly queried fields
- **Connection pooling** for concurrent requests
- **Caching** for frequently accessed data
- **Rate limiting** to prevent abuse

## 🤝 Contributing

### 🎯 Ways to Contribute
1. **🏢 Add new companies** to existing scrapers
2. **🔌 Create new platform scrapers** (BambooHR, Talentbrew, etc.)
3. **🎨 Improve the frontend** UI/UX
4. **🐛 Fix bugs** and improve error handling
5. **📚 Enhance documentation**
6. **🧪 Add tests** and improve code quality

### 📋 Development Workflow
1. **Fork** the repository
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Make changes** and test thoroughly
4. **Commit changes:** `git commit -m 'Add amazing feature'`
5. **Push to branch:** `git push origin feature/amazing-feature`
6. **Open Pull Request** with detailed description

### 🏗️ Code Style
- **Python:** Follow PEP 8, use type hints
- **JavaScript:** Use modern ES6+ features
- **Documentation:** Update README for new features
- **Testing:** Add tests for new functionality

## ⚖️ Ethics & Compliance

### 🛡️ Responsible Scraping
- **✅ Respects Terms of Service:** Only uses sources with public APIs or explicit permission
- **⏱️ Rate Limiting:** All requests are throttled to avoid server overload  
- **🚫 Excluded Sources:** LinkedIn, Indeed, Glassdoor (due to ToS restrictions)
- **✨ Preferred Sources:** Official company APIs and ATS systems
- **📞 Contact:** Provides mechanisms for takedown requests

### 🔒 Data Privacy
- **No Personal Data:** Only collects publicly posted job information
- **Minimal Storage:** Stores only job-relevant information
- **Regular Cleanup:** Automatically removes old job postings
- **Transparency:** Open source for full auditability

### 📜 Legal Compliance
- **MIT License:** Open source and commercially friendly
- **DMCA Compliance:** Respects intellectual property rights
- **API Guidelines:** Follows best practices for each platform
- **Terms Updates:** Regularly reviews and updates scraping policies

## 📞 Support & Community

### 🆘 Getting Help
- **📖 Documentation:** Start with this comprehensive README
- **🐛 Issues:** Report bugs on [GitHub Issues](https://github.com/athifer/biodsjobs/issues)
- **💡 Feature Requests:** Suggest improvements via GitHub
- **📧 Contact:** Reach out for takedown requests or compliance questions

### 🏆 Acknowledgments
Built with passion for the biotech community, using:
- **FastAPI** for high-performance APIs
- **SQLAlchemy** for robust database management
- **httpx** for async HTTP requests
- **BeautifulSoup** for HTML parsing
- **Modern JavaScript** for responsive frontend

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the biotech data science community**

*Helping computational biologists find their next opportunity in the life sciences.*
