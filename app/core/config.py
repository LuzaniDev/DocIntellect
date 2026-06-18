from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes centralizadas via env vars e .env"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "docintellect-rpa"
    app_version: str = "0.1.0"
    debug: bool = True
    secret_key: str = "change-me"

    database_url: str = "postgresql+asyncpg://docintellect:docintellect@localhost:5432/docintellect"
    database_sync_url: str = "postgresql://docintellect:docintellect@localhost:5432/docintellect"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    storage_backend: str = "local"
    storage_local_path: str = "./data/documents"
    s3_bucket: str = "docintellect-rpa"
    s3_region: str = "us-east-1"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    ocr_engine: str = "tesseract"
    ocr_lang: str = "por"
    tesseract_cmd: str = "/usr/bin/tesseract"

    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1

    pipeline_max_concurrency: int = 4
    pipeline_confidence_threshold: float = 0.7

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    streamlit_port: int = 8501
    tessdata_prefix: str = ""


settings = Settings()
