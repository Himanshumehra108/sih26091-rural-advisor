from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/rural_advisor'
    jwt_secret_key: str = 'change-me'
    llm_api_key: str | None = None
    bhashini_api_key: str | None = None

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
