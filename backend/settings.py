from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./bioinfojobs.db"
    # Comma-separated list of keywords to score relevance (simple example)
    KEYWORDS: str = "bioinformatics,computational biology,NGS,genomics,transcriptomics,proteomics,RNA-seq,variant calling,ML,machine learning,statistics,R,Python"

settings = Settings()
