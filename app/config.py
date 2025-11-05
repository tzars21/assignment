from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    agno_api_provider: str = Field("openai", env="AGNO_API_PROVIDER")
    provider: str = Field("openai", env="AGNO_API_PROVIDER")
    max_upload_bytes: int = Field(5 * 1024 * 1024, env="MAX_UPLOAD_BYTES")
    host: str = Field("127.0.0.1", env="HOST")
    port: int = Field(8000, env="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
