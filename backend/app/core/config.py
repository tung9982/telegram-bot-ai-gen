from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AetherFlow Engine"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    redis_url: str = Field(default="redis://localhost:6379/0")
    plugin_dir: str = "plugins"

    class Config:
        env_file = ".env"


settings = Settings()
