from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    APP_ENV: str = 'development'
    JWT_SECRET: str = 'development-only-secret-change-me-123456789'
    DATABASE_URL: str = 'sqlite:///./jitflow.db'
    AD_MODE: str = 'fake'
    AD_SERVER: str = 'dc01.corp.local'
    AD_PORT: int = 636
    AD_USE_SSL: bool = True
    AD_VALIDATE_CERT: bool = True
    AD_CA_CERT_FILE: str | None = None
    AD_BIND_DN: str = ''
    AD_BIND_PASSWORD: str = ''
    AD_BASE_DN: str = 'DC=corp,DC=local'
    LLM_ENABLED: bool = False
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str = 'https://api.openai.com/v1'
    LLM_MODEL: str = 'gpt-4o-mini'
    MAX_DURATION_MINUTES: int = 480
    MAX_PROTECTED_DURATION_MINUTES: int = 120
    REVOKE_SCAN_INTERVAL_SECONDS: int = 15
    REVOKE_MAX_RETRIES: int = 5
    ALERT_WEBHOOK_URL: str | None = None
    API_URL: str = 'http://127.0.0.1:8080'

@lru_cache
def get_settings(): return Settings()
settings = get_settings()
