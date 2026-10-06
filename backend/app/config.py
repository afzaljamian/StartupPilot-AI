from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'StartupPilot AI'
    environment: str = 'development'
    demo_mode: bool = True
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.8-flash'
    tavily_api_key: str = ''
    mongodb_uri: str = 'mongodb://localhost:27017'
    mongodb_db: str = 'startuppilot'
    jwt_secret: str = 'change-me-in-production'
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 60 * 24
    redis_url: str = 'redis://localhost:6379/0'
    frontend_url: str = 'http://localhost:5173'
    cors_origins: str = 'http://localhost:5173,http://localhost:3000'
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(',') if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
