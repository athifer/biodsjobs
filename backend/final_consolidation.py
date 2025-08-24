#!/usr/bin/env python3
"""
Final Consolidation of All Company YAML Files
Merges all company YAML files into a single authoritative database
"""

import yaml
import asyncio
import httpx
from pathlib import Path
from collections import defaultdict

async def validate_url(url: str) -> bool:
    """Check if a URL is accessible"""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.head(url)
            return 200 <= response.status_code < 400
    except Exception:
        return False

def normalize_company_name(name: str) -> str:
    """Normalize company name for deduplication"""
    return name.lower().strip().replace(' ', '').replace('.', '').replace(',', '')

def get_yaml_files():
    """Get all company YAML files to process"""
    backend_dir = Path(__file__).parent
    yaml_files = []
    
    # Main directory files
    for file in ['companies.yaml', 'companies_all.yaml', 'companies_master.yaml']:
        file_path = backend_dir / file
        if file_path.exists():
            yaml_files.append(file_path)
    
    # Backup directory files
    backup_dir = backend_dir / 'backup'
    if backup_dir.exists():
        for file in backup_dir.glob('*.yaml'):
            yaml_files.append(file)
    
    return yaml_files

def prioritize_source(source: str) -> int:
    """Return priority for source type (lower = higher priority)"""
    priorities = {
        'greenhouse': 1,
        'workday': 2,
        'lever': 3,
        'comprehensive': 4,
        'bamboo': 5
    }
    return priorities.get(source.lower(), 10)

async def main():
    """Consolidate all YAML files into a single comprehensive database"""
    print("Final Consolidation of All Company YAML Files")
    print("=" * 60)
    
    # Get all YAML files
    yaml_files = get_yaml_files()
    print(f"Found {len(yaml_files)} YAML files to process:")
    for file in yaml_files:
        print(f"  - {file}")
    
    # Company tracking
    all_companies = {}  # normalized_name -> best_company_data
    source_counts = defaultdict(int)
    
    # Process each YAML file
    print(f"\nProcessing YAML files...")
    for yaml_file in yaml_files:
        print(f"Processing: {yaml_file.name}")
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data:
                print(f"  ⚠️  Empty or invalid YAML file")
                continue
            
            # Handle different YAML structures
            if isinstance(data, dict):
                # Standard structure with sources
                for source, companies in data.items():
                    if isinstance(companies, list):
                        for company in companies:
                            if isinstance(company, dict) and 'company' in company:
                                normalized_name = normalize_company_name(company['company'])
                                
                                # Keep the best version (prioritize by source)
                                if normalized_name not in all_companies:
                                    all_companies[normalized_name] = {
                                        'data': company,
                                        'source': source,
                                        'priority': prioritize_source(source)
                                    }
                                else:
                                    current_priority = all_companies[normalized_name]['priority']
                                    new_priority = prioritize_source(source)
                                    if new_priority < current_priority:
                                        all_companies[normalized_name] = {
                                            'data': company,
                                            'source': source,
                                            'priority': new_priority
                                        }
            elif isinstance(data, list):
                # Simple list structure
                for company in data:
                    if isinstance(company, dict) and 'company' in company:
                        normalized_name = normalize_company_name(company['company'])
                        source = company.get('source', 'comprehensive')
                        
                        if normalized_name not in all_companies:
                            all_companies[normalized_name] = {
                                'data': company,
                                'source': source,
                                'priority': prioritize_source(source)
                            }
                        
        except Exception as e:
            print(f"  ❌ Error processing {yaml_file.name}: {e}")
            continue
    
    print(f"\nFound {len(all_companies)} unique companies before validation")
    
    # Validate URLs
    print(f"\nValidating company URLs...")
    validation_tasks = []
    company_list = []
    
    for normalized_name, company_info in all_companies.items():
        company_data = company_info['data']
        url = company_data.get('careers_url', '')
        if url:
            validation_tasks.append(validate_url(url))
            company_list.append((normalized_name, company_info))
    
    if validation_tasks:
        results = await asyncio.gather(*validation_tasks)
        
        valid_companies = {}
        for (normalized_name, company_info), is_valid in zip(company_list, results):
            company_data = company_info['data']
            source = company_info['source']
            
            if is_valid:
                valid_companies[normalized_name] = company_info
                source_counts[source] += 1
                print(f"✅ {company_data['company']}: {company_data['careers_url']}")
            else:
                print(f"❌ {company_data['company']}: {company_data['careers_url']}")
    
    # Organize by source
    final_data = defaultdict(list)
    for normalized_name, company_info in valid_companies.items():
        source = company_info['source']
        company_data = company_info['data'].copy()
        final_data[source].append(company_data)
    
    # Sort companies within each source
    for source in final_data:
        final_data[source].sort(key=lambda x: x['company'])
    
    # Convert to regular dict and sort sources by priority
    sorted_sources = sorted(final_data.keys(), key=prioritize_source)
    consolidated_data = {}
    for source in sorted_sources:
        consolidated_data[source] = final_data[source]
    
    # Save consolidated file
    backend_dir = Path(__file__).parent
    output_file = backend_dir / "companies_consolidated_final.yaml"
    
    with open(output_file, 'w') as f:
        yaml.dump(consolidated_data, f, default_flow_style=False, sort_keys=False,
                 allow_unicode=True, indent=2)
    
    # Replace the main companies.yaml file
    main_file = backend_dir / "companies.yaml"
    with open(main_file, 'w') as f:
        yaml.dump(consolidated_data, f, default_flow_style=False, sort_keys=False,
                 allow_unicode=True, indent=2)
    
    # Update master file
    master_file = backend_dir / "companies_master.yaml"
    with open(master_file, 'w') as f:
        yaml.dump(consolidated_data, f, default_flow_style=False, sort_keys=False,
                 allow_unicode=True, indent=2)
    
    # Print final summary
    total_companies = sum(len(companies) for companies in consolidated_data.values())
    
    print(f"\n{'='*60}")
    print("FINAL CONSOLIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"YAML files processed: {len(yaml_files)}")
    print(f"Total unique companies: {len(all_companies)}")
    print(f"Valid companies: {total_companies}")
    print(f"Sources: {len(consolidated_data)}")
    print()
    
    for source, companies in consolidated_data.items():
        print(f"{source.upper()}: {len(companies)} companies")
    
    print(f"\nFiles updated:")
    print(f"  - companies.yaml (main file)")
    print(f"  - companies_master.yaml (backup)")
    print(f"  - companies_consolidated_final.yaml (archive)")
    
    return consolidated_data

if __name__ == "__main__":
    asyncio.run(main())
