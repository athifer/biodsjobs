# Master Companies Lookup - Summary Report

## Overview
This file contains the comprehensive master lookup of all biotech/life sciences companies collected from all YAML configuration files, including those in the backup folder. Each company has been validated for URL accessibility and deduplicated.

## Data Sources Processed
- `companies.yaml` 
- `companies_all.yaml`
- `backup/companies_all_backup.yaml`
- `backup/companies_all.yaml`
- `backup/companies_all_new.yaml`
- `backup/companies_all_original.yaml`

## Validation Process
- **Total unique companies found**: 43
- **Companies with valid URLs**: 28 (65% success rate)
- **Companies with invalid URLs**: 15 (filtered out)

## Final Results

### Companies by Source Platform

#### GREENHOUSE (12 companies)
- 10x Genomics
- Benchling  
- Eikon Therapeutics
- Flagship Pioneering
- Formation Bio
- Freenome
- Generate:Biomedicines
- Ginkgo Bioworks
- Hexagon Bio
- Insitro
- Nimbus Therapeutics
- Twist Bioscience

#### WORKDAY (10 companies)
- Alnylam
- Amgen
- Bristol Myers Squibb
- Gilead
- Illumina
- Johnson & Johnson
- Merck
- Moderna
- Pfizer
- Vertex

#### LEVER (3 companies)
- Color Health
- GRAIL
- Genesis Therapeutics

#### COMPREHENSIVE (2 companies)
- 23andMe
- Guardant Health

#### BAMBOO (1 company)
- Color Genomics

## URL Domains Distribution
- **boards.greenhouse.io**: 12 companies
- **jobs.lever.co**: 3 companies
- **Various Workday domains**: 7 companies
- **Other career sites**: 6 companies

## Filtered Out (Invalid URLs)
Companies removed due to 404/500 errors or inaccessible URLs:
- Zymergen
- Recursion Pharmaceuticals  
- Tempus Labs
- Biogen
- Eli Lilly
- AbbVie
- Incyte
- Berkeley Lights
- Synthetic Biologics
- AngelList/Wellfound companies (Newomics, Variant Bio, Deep Genomics, Atomwise, Insilico Medicine, Owkin)

## Output Files
- **Primary**: `companies.yaml` - Clean master configuration for ingestor
- **Reference**: `companies_master.yaml` - Complete validated lookup
- **Documentation**: `COMPANIES_MASTER_SUMMARY.md` - This summary

## Usage
The `companies.yaml` file should be used as the single source of truth for the job ingestor. It contains only validated, working companies with accessible career pages.

**Total Valid Companies: 28**  
**Total Sources: 5**  
**Validation Date: August 24, 2025**
