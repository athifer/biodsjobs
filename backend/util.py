from typing import List, Dict
import re
from settings import settings

KEYWORDS = [k.strip().lower() for k in settings.KEYWORDS.split(',') if k.strip()]

def score_job(job: Dict, search_query: str = None) -> float:
    """Enhanced relevance scoring based on keyword matches in title + description with weighted priorities.
    
    Args:
        job: Job dictionary with title, description, etc.
        search_query: Optional search term to boost relevance for specific searches
    """
    title = (job.get('title') or '').lower()
    description = (job.get('description') or '').lower()
    
    score = 0
    
    # If there's a search query, prioritize exact matches
    if search_query and search_query.strip():
        query_terms = [term.strip().lower() for term in search_query.split() if term.strip()]
        
        for term in query_terms:
            # Exact phrase match in title gets highest boost
            if term in title:
                if len(term) > 3:  # Avoid boosting short common words
                    score += 15
            # Exact phrase match in description gets medium boost  
            elif term in description:
                if len(term) > 3:
                    score += 8
            
            # Partial word matches (for terms like "bioinformatics" matching "bioinformatician")
            title_words = title.split()
            desc_words = description.split()
            
            for word in title_words:
                if term in word and len(term) > 3:
                    score += 10
            
            for word in desc_words:
                if term in word and len(term) > 3:
                    score += 5
    
    # High-priority bioinformatics keywords (higher weight)
    primary_keywords = [
        'bioinformatics', 'bioinformatician', 'computational biology', 'computational biologist',
        'genomics', 'transcriptomics', 'proteomics', 'metabolomics',
        'ngs', 'rna-seq', 'chip-seq', 'atac-seq', 'single cell', 'single-cell',
        'variant calling', 'gwas', 'metagenomics', 'phylogenetics',
        'multi-omic', 'multiomics', 'epigenomics'
    ]
    
    # Data science specific keywords
    data_science_keywords = [
        'data scientist', 'data science', 'machine learning engineer', 'ml engineer',
        'data analyst', 'data engineer', 'analytics', 'statistician',
        'artificial intelligence', 'ai engineer', 'deep learning', 'neural networks'
    ]
    
    # Medium-priority technical keywords
    technical_keywords = [
        'python', 'r programming', 'perl', 'bash', 'linux',
        'machine learning', 'deep learning', 'statistics', 'statistical',
        'data science', 'algorithm', 'pipeline', 'workflow',
        'docker', 'cloud computing', 'aws', 'gcp', 'azure',
        'sql', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'
    ]
    
    # Lower-priority general keywords
    general_keywords = [
        'analysis', 'modeling', 'visualization', 'database',
        'api', 'git', 'software engineering', 'automation'
    ]
    
    # Choose keyword set based on search query context
    if search_query:
        query_lower = search_query.lower()
        if any(term in query_lower for term in ['data scien', 'data analy', 'ml engineer', 'machine learning']):
            # Boost data science keywords for data science searches
            primary_keywords = data_science_keywords + primary_keywords
        elif any(term in query_lower for term in ['bioinformatics', 'computational biology', 'genomics']):
            # Keep bioinformatics keywords as primary for bio searches
            pass
    
    # Score title matches (higher weight for title)
    for kw in primary_keywords:
        # Use word boundaries but handle hyphenated terms
        pattern = r'\b' + re.escape(kw).replace(r'\-', r'[-\s]?') + r'\b'
        if re.search(pattern, title):
            score += 10  # High weight for primary keywords in title
        elif re.search(pattern, description):
            score += 5   # Medium weight for primary keywords in description
    
    for kw in technical_keywords:
        pattern = r'\b' + re.escape(kw).replace(r'\-', r'[-\s]?') + r'\b'
        if re.search(pattern, title):
            score += 3   # Medium weight for technical keywords in title
        elif re.search(pattern, description):
            score += 1   # Low weight for technical keywords in description
    
    for kw in general_keywords:
        pattern = r'\b' + re.escape(kw).replace(r'\-', r'[-\s]?') + r'\b'
        if re.search(pattern, title):
            score += 1   # Low weight for general keywords in title
        elif re.search(pattern, description):
            score += 0.5 # Very low weight for general keywords in description
    
    # Bonus for multiple relevant indicators
    relevant_indicators = sum(1 for kw in primary_keywords[:12] 
                            if re.search(r'\b' + re.escape(kw).replace(r'\-', r'[-\s]?') + r'\b', 
                                       title + " " + description))
    if relevant_indicators >= 3:
        score += 5  # Bonus for jobs with multiple relevant indicators
    
    # Penalty for wet-lab focused roles (only for bioinformatics searches)
    if not search_query or 'bioinformatics' in search_query.lower():
        wet_lab_keywords = [
            'wet lab', 'wetlab', 'laboratory technician', 'bench scientist', 'assay development',
            'cell culture', 'molecular cloning', 'pcr', 'western blot',
            'immunohistochemistry', 'flow cytometry', 'microscopy', 'lab technician'
        ]
        
        wet_lab_mentions = sum(1 for kw in wet_lab_keywords 
                              if re.search(r'\b' + re.escape(kw).replace(r'\-', r'[-\s]?') + r'\b', 
                                         title + " " + description))
        
        # Apply penalty if wet-lab keywords are prominent but bioinformatics is not in title
        if wet_lab_mentions >= 2 and not any(re.search(r'\b' + re.escape(kw).replace(r'\-', r'[-\s]?') + r'\b', title) 
                                             for kw in primary_keywords[:4]):  # Only check core bioinformatics terms
            score = score * 0.3  # Reduce score significantly for wet-lab heavy roles
    
    return float(max(0, min(100, score * 2)))  # Scale to 0-100 range
