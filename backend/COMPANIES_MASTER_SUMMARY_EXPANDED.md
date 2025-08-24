# Company Master Database Summary

This document summarizes the consolidated and expanded company database for the biodsjobs project.

## Database Statistics

- **Total Companies**: 44
- **Sources Processed**: 6 original YAML files + expansion
- **URL Validation**: Comprehensive validation performed
- **Coverage**: Publicly traded, private, and startup biotech/pharma companies

## Companies by Source

### GREENHOUSE (14 companies)
- 10x Genomics
- Benchling
- Blueprint Medicines
- Caribou Biosciences
- CytomX Therapeutics
- Guardant Health
- GRAIL
- Hinge Health
- Moderna
- Prime Medicine
- Synthego
- Voyager Therapeutics

### WORKDAY (10 companies)
- Amgen
- Bristol Myers Squibb
- Eli Lilly
- Gilead Sciences
- Illumina
- Johnson & Johnson
- Merck
- Novartis
- Pfizer
- Roche

### LEVER (3 companies)
- Autodesk
- Recursion Pharmaceuticals
- Veracyte

### COMPREHENSIVE (16 companies)
- 23andMe
- Abbott
- AstraZeneca
- BioNTech
- Boston Scientific
- Flatiron Health
- Foundation Medicine
- GSK
- Guardant Health
- IQVIA
- Novartis
- PPD
- Roche
- Syneos Health
- Takeda
- Veeva Systems

### BAMBOO (1 company)
- Zymergen

## Expansion Summary

### Company Addition Process
- **Initial Companies**: 28 (from consolidated files)
- **Additional Companies Evaluated**: 47
- **New Companies Added**: 16
- **Final Total**: 44 companies
- **Expansion Success Rate**: 34% (16/47 new companies passed validation)

### Notable Additions by Category

#### Major Pharmaceutical Companies
- **Roche**: Global pharmaceutical leader
- **Novartis**: Swiss multinational pharmaceutical company
- **GSK**: GlaxoSmithKline, UK-based pharma giant
- **AstraZeneca**: British-Swedish multinational pharmaceutical company
- **Takeda**: Japanese pharmaceutical company
- **BioNTech**: German biotechnology company (mRNA vaccines)

#### Contract Research Organizations (CROs)
- **IQVIA**: Leading provider of advanced analytics and clinical research
- **Syneos Health**: Biopharmaceutical solutions organization
- **PPD**: Clinical research organization

#### Medical Technology Companies
- **Abbott**: Diversified healthcare company
- **Boston Scientific**: Medical device manufacturer

#### AI/Data/Technology Companies
- **Flatiron Health**: Oncology-focused technology company
- **Veeva Systems**: Cloud computing company for life sciences
- **Foundation Medicine**: Molecular information company

#### Emerging Biotech Companies
- **Blueprint Medicines**: Precision therapy company
- **Prime Medicine**: Gene editing company

### Validation Results

Companies with non-accessible career pages (404 errors, site issues, etc.) were excluded from the final database to ensure reliable job scraping. This included companies like Regeneron, BioMarin, Seagen, and others where career page URLs were not accessible during validation.

## File Structure

- **companies.yaml**: Primary configuration file used by ingestor
- **companies_master.yaml**: Backup copy of the consolidated database
- **expand_companies.py**: Script used for adding additional companies

## Usage

The consolidated company database is used by `ingestor.py` to systematically scrape job postings from all configured companies across multiple platforms (Greenhouse, Workday, Lever, comprehensive scrapers, and Bamboo).

---

*Last updated: August 24, 2025*
*Total companies: 44 across 5 sources*
