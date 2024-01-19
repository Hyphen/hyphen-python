from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    legacy_api_key: str = None
    development_hyphen_uri: AnyHttpUrl = "https://engine.dev.hyphen.ai"
    local_api_key: str = None
    local_hyphen_uri: AnyHttpUrl = "http://localhost:8000"
    local_hyphen_db_username: str = None
    local_hyphen_db_password: str = None

# singleton
settings = Settings()