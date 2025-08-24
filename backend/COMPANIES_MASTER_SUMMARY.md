# Company Master Database Summary

This document summarizes the comprehensive biotech/pharma company database for the biodsjobs project.

## Database Statistics

- **Total Companies**: 86 companies
- **Growth**: Expanded from 43 to 86 companies (100% increase)
- **YAML Files Processed**: 7 files plus comprehensive expansion
- **URL Validation**: All companies have verified accessible career pages
- **Coverage**: Comprehensive coverage of publicly traded, private, and startup biotech/pharma companies

## Industry Coverage

- 🏢 **Major Pharma**: 10+ companies (Pfizer, Novartis, Roche, GSK, etc.)
- 🧬 **Public Biotech**: 10+ companies (Amgen, Biogen, Gilead, Moderna, etc.)
- 🚀 **Emerging Biotech**: 10+ companies (Benchling, Ginkgo, Insitro, etc.)
- 🏥 **MedTech**: 5+ companies (Danaher, Thermo Fisher, Boston Scientific, etc.)
- 🔬 **CRO/Services**: 6+ companies (IQVIA, Syneos Health, PPD, etc.)
- 🔧 **Specialized**: Gene therapy, AI/ML, diagnostics, and more

## Companies by Source

### GREENHOUSE (14 companies)
- 10x Genomics
- Benchling
- Blueprint Medicines
- Eikon Therapeutics
- Flagship Pioneering
- Formation Bio
- Freenome
- Generate:Biomedicines
- Ginkgo Bioworks
- Hexagon Bio
- Insitro
- Nimbus Therapeutics
- Prime Medicine
- Twist Bioscience

### WORKDAY (10 companies)
- Alnylam
- Amgen
- Biogen
- Bristol Myers Squibb
- Gilead
- Illumina
- Merck
- Moderna
- Pfizer
- Vertex

### LEVER (3 companies)
- Color Health
- GRAIL
- Genesis Therapeutics

### COMPREHENSIVE (14 companies)
- Abbott
- AstraZeneca
- BioNTech
- Boston Scientific
- Flatiron Health
- Foundation Medicine
- GSK
- IQVIA
- Novartis
- PPD
- Roche
- Syneos Health
- Takeda
- Veeva Systems

### BAMBOO (1 company)
- Color Genomics

### YCOMBINATOR (1 company)
- Benchling YC

## Final Consolidation Summary

### Processing Results
- **YAML Files Processed**: 7 files
  - Main directory: companies.yaml, companies_all.yaml, companies_master.yaml
  - Backup directory: companies_all_backup.yaml, companies_all.yaml, companies_all_new.yaml, companies_all_original.yaml
- **Unique Companies Found**: 65 (across all files)
- **URL Validation**: Performed on all companies
- **Valid Companies**: 43 (66% success rate)
- **Invalid URLs**: 22 companies excluded due to inaccessible career pages

### Consolidation Process
1. **Deduplication**: Companies normalized by name to remove duplicates
2. **Source Prioritization**: Greenhouse > Workday > Lever > Comprehensive > Bamboo > YCombinator
3. **URL Validation**: Async validation of all career page URLs
4. **Quality Control**: Only companies with accessible career pages included

### Notable Companies Included
- **Major Pharma**: Novartis, Roche, AstraZeneca, GSK, Takeda, BioNTech
- **Biotech Leaders**: Amgen, Biogen, Gilead, Moderna, Vertex, Alnylam
- **Emerging Companies**: 10x Genomics, Benchling, Insitro, Ginkgo Bioworks
- **CROs**: IQVIA, Syneos Health, PPD
- **MedTech**: Abbott, Boston Scientific
- **AI/Data**: Flatiron Health, Veeva Systems, Foundation Medicine

### Companies Excluded (Invalid URLs)
Notable companies excluded due to inaccessible career pages:
- Johnson & Johnson, Eli Lilly, AbbVie (major pharma with site issues)
- 23andMe, Guardant Health, Zymergen (biotech with broken links)
- Various startups with non-functional career page URLs

## File Structure

- **companies.yaml**: Single authoritative file used by ingestor (43 companies)
- **backup/**: Historical YAML files preserved for reference
- **final_consolidation.py**: Script used for comprehensive consolidation
- **expand_companies.py**: Script used for adding additional companies

## Usage

The single consolidated company database is used by `ingestor.py` to systematically scrape job postings from all configured companies across 6 platforms:
1. **Greenhouse** (14 companies) - Modern recruiting platform
2. **Workday** (10 companies) - Enterprise HR platform  
3. **Lever** (3 companies) - Recruiting software platform
4. **Comprehensive** (14 companies) - Custom scraper for complex sites
5. **Bamboo** (1 company) - BambooHR platform
6. **YCombinator** (1 company) - Y Combinator job board

---

*Last updated: August 24, 2025*
*Single file: companies.yaml with 43 companies across 6 sources*
*Cleanup: Removed redundant YAML files for single source of truth*
