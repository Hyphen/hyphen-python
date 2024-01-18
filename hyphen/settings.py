from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    legacy_api_key: str = None
    development_hyphen_uri: AnyHttpUrl = "https://engine.dev.hyphen.ai"

# singleton
settings = Settings()