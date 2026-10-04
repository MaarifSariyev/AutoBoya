import os
from typing import List, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Azerbaijan Paint Formula Platform"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://paint_user:paint_password@localhost:5432/paint_db"

    # Security & Auth
    SECRET_KEY: str = "change-this-development-secret-before-startup"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Default Admin
    ADMIN_EMAIL: str = "admin@paintformula.az"
    ADMIN_PASSWORD: str = "change-this-admin-password-before-startup"
    ADMIN_FULL_NAME: str = "Master Paint Expert"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.ENVIRONMENT.lower() == "production":
            if len(self.SECRET_KEY) < 32 or self.SECRET_KEY == "change-this-development-secret-before-startup":
                raise ValueError("Production SECRET_KEY must be a unique value of at least 32 characters.")
            if len(self.ADMIN_PASSWORD) < 12 or self.ADMIN_PASSWORD == "change-this-admin-password-before-startup":
                raise ValueError("Production ADMIN_PASSWORD must be a unique value of at least 12 characters.")
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
