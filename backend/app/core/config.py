from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./document_intelligence.db"
    UPLOAD_DIR: str = "uploads"
    LOG_DIR: str = "logs"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_HOST: str = "http://localhost:11434"
    MAX_UPLOAD_SIZE_MB: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
