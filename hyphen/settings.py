from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    hyphen_client_id: Optional[str] = None
    hyphen_client_secret: Optional[str] = None

# singleton
settings = Settings()