from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AFFILIATE_CODE: str = "default_code"
    HODLHODL_API_URL: str = "https://hodlhodl.com/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()