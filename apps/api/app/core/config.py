from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "Plot API"
    ENVIRONMENT: str = "development"

    @property
    def DEBUG(self) -> bool:
        return self.ENVIRONMENT == "development"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth0
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_ALGORITHMS: list[str] = ["RS256"]

    # CORS — comma-separated in env: ALLOWED_ORIGINS=https://plot.app,https://www.plot.app
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()  # type: ignore[call-arg]
