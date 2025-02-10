from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = "sk-61a8675148454f47a9c75ccf8d1c6a0b"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 