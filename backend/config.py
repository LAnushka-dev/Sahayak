import os

class Settings:
    PROJECT_NAME: str = "Sahayak Backend"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super_secret_sahayak_jwt_key_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database: MySQL default with automatic SQLite fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sahayak.db")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    JINA_API_KEY: str = os.getenv("JINA_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/sahayak-dispatch")

settings = Settings()
