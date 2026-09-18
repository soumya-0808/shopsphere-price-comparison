from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ShopSphere API"
    database_url: str = "postgresql+psycopg://shopsphere:shopsphere@db:5432/shopsphere"
    secret_key: str = "change-this-in-production"
    access_token_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
