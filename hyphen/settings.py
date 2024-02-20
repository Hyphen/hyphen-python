from typing import Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    hyphen_client_id: Optional[str] = None
    hyphen_client_secret: Optional[str] = None
    development_hyphen_uri: AnyHttpUrl = "https://engine.dev.hyphen.ai"
    local_hyphen_uri: AnyHttpUrl = "http://localhost:8000"
    local_hyphen_db_username: str = None
    local_hyphen_db_password: str = None

# singleton
settings = Settings()