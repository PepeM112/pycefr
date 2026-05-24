from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = ""
    add_local_suffix: bool = True
    auto_display_console: bool = True
    ignore_folders: Union[str, List[str]] = ["node_modules/", ".git/", "__pycache__/"]
    python_threshold_percentage: int = 50
    cors_origins: Union[str, List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("ignore_folders", "cors_origins", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
