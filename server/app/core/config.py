from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/rural_advisor'
    jwt_secret_key: str = 'change-me'
    llm_api_key: str | None = None
    llm_provider: str = 'openai'  # openai | anthropic | groq | openai_compatible
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.3
    llm_timeout_seconds: float = 45.0
    bhashini_api_key: str | None = None
    sarvam_api_key: str | None = None

    # OpenStreetMap stack (Nominatim + Overpass + OSRM). Public demos are
    # rate-limited; point these at self-hosted instances for production.
    nominatim_base_url: str = 'https://nominatim.openstreetmap.org'
    overpass_url: str = 'https://overpass-api.de/api/interpreter'
    osrm_base_url: str = 'https://router.project-osrm.org'
    osm_user_agent: str = 'RuralAdvisor/1.0 (SIH rural feasibility advisor)'
    geo_http_timeout_seconds: float = 25.0
    nominatim_min_interval_seconds: float = 1.1

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
