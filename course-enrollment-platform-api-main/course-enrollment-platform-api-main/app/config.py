from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./enrollment.db"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    rate_limit_register: str = "5/minute"
    rate_limit_login: str = "10/minute"
    rate_limit_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
