from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = ""
    add_local_suffix: bool = True
    auto_display_console: bool = True
    ignore_folders: Union[str, List[str]] = ["node_modules/", ".git/", "__pycache__/"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("ignore_folders", mode="before")
    @classmethod
    def parse_ignore_folders(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
