"""
AWS Bedrock and Application Configuration
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Bedrock Configuration
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
    bedrock_embedding_model: str = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
    bedrock_max_tokens: int = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))
    
    # Evaluator Model (for LLM-as-a-judge)
    evaluator_model_id: str = os.getenv("EVALUATOR_MODEL_ID", "amazon.nova-pro-v1:0")
    evaluator_max_tokens: int = int(os.getenv("EVALUATOR_MAX_TOKENS", "4096"))
    
    # Vector Database (Pinecone)
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "financial-research-index")
    pinecone_dimension: int = int(os.getenv("PINECONE_DIMENSION", "1536"))
    
    # API Keys
    sec_api_key: Optional[str] = os.getenv("SEC_API_KEY")
    alpha_vantage_key: Optional[str] = os.getenv("ALPHA_VANTAGE_KEY")
    news_api_key: Optional[str] = os.getenv("NEWS_API_KEY")
    rapidapi_key: Optional[str] = os.getenv("RAPIDAPI_KEY")
    market_data_api_key: Optional[str] = os.getenv("MARKET_DATA_API_KEY")
    yfinance_timeout: int = int(os.getenv("YFINANCE_TIMEOUT", "30"))
    
    # Redis Cache
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Agent Configuration
    agent_max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
    agent_timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))
    agent_temperature: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    agent_top_p: float = float(os.getenv("AGENT_TOP_P", "0.9"))
    
    # Memory Configuration
    short_term_max_tokens: int = int(os.getenv("SHORT_TERM_MAX_TOKENS", "8000"))
    long_term_retention_days: int = int(os.getenv("LONG_TERM_RETENTION_DAYS", "365"))
    episodic_memory_enabled: bool = os.getenv("EPISODIC_MEMORY_ENABLED", "true").lower() == "true"
    
    # Error Handling
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_backoff_factor: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2"))
    fallback_chain_depth: int = int(os.getenv("FALLBACK_CHAIN_DEPTH", "3"))
    
    # Evaluation Configuration
    quality_threshold: float = float(os.getenv("QUALITY_THRESHOLD", "0.70"))
    hallucination_threshold: float = float(os.getenv("HALLUCINATION_THRESHOLD", "0.02"))
    min_tool_efficiency: float = float(os.getenv("MIN_TOOL_EFFICIENCY", "0.70"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/ara_agent.log")
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Misc
    environment: str = os.getenv("ENVIRONMENT", "development")
    app_name: str = os.getenv("APP_NAME", "ARA-1")
    version: str = os.getenv("VERSION", "1.0.0")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
