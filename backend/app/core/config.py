"""
Application configuration settings.
MDP Platform V3.1 - Metadata-Driven Architecture
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # V3.1 Database: ontology_meta_new (Metadata storage)
    database_url: str = "mysql+pymysql://root:Ga0binGB@localhost:3306/ontology_meta_new"
    DEBUG: bool = True  # Default to True for development
    
    # Legacy database (for reference/migration)
    legacy_database_url: str = "mysql+pymysql://root:Ga0binGB@localhost:3306/ontology"
    
    # Raw Store Database: mdp_raw_store (Synced data storage)
    raw_store_database_url: str = "mysql+pymysql://root:Ga0binGB@localhost:3306/mdp_raw_store"
    
    # ==========================================
    # Elasticsearch Configuration
    # ==========================================
    elasticsearch_host: str = "http://127.0.0.1:9200"
    elasticsearch_index_name: str = "mdp_text_documents"
    elasticsearch_objects_index: str = "mdp_objects"  # Object Explorer index
    elasticsearch_request_timeout: int = 30
    elasticsearch_verify_certs: bool = False
    elasticsearch_number_of_shards: int = 1
    elasticsearch_number_of_replicas: int = 0
    
    # ==========================================
    # Vector Store Configuration (ChromaDB)
    # ==========================================
    chroma_db_path: str = "data/chroma_vector_store"
    
    # ==========================================
    # Ollama LLM Configuration (Chat2App)
    # ==========================================
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ollama_timeout: int = 120  # 本地 LLM 响应可能较慢
    ollama_temperature: float = 0.1  # 低温度确保输出稳定
    
    class Config:
        # Make .env file optional - only load if it exists
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_ignore_empty = True


settings = Settings()

