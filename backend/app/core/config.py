"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    database_url: str = "mysql+pymysql://root:Ga0binGB@localhost:3306/ontology"
    DEBUG: bool = True  # Default to True for development
    
    class Config:
        # Make .env file optional - only load if it exists
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_ignore_empty = True


settings = Settings()

