"""Configuration management using Pydantic settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=3306, description="Database port")
    user: str = Field(default="root", description="Database user")
    password: str = Field(default="", description="Database password")
    name: str = Field(default="sportbet", description="Database name")
    charset: str = Field(default="utf8mb4", description="Database charset")

    model_config = SettingsConfigDict(env_prefix="DB_")

    @property
    def url(self) -> str:
        """Generate SQLAlchemy database URL."""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?charset={self.charset}"


class ScraperSettings(BaseSettings):
    """Scraper configuration."""

    base_url: str = Field(
        default="https://www.basketball-reference.com",
        description="Base URL for Basketball Reference",
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay: int = Field(default=2, description="Delay between retries in seconds")

    model_config = SettingsConfigDict(env_prefix="SCRAPER_")

    @field_validator("timeout", "retry_attempts", "retry_delay")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Validate that values are positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


class AnthropicSettings(BaseSettings):
    """Anthropic Claude API configuration."""

    api_key: str = Field(default="", description="Anthropic API key")

    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_")


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )
    format: Literal["json", "console"] = Field(default="json", description="Log format")
    file: str = Field(default="logs/nba_predictor.log", description="Log file path")

    model_config = SettingsConfigDict(env_prefix="LOG_")


class AppSettings(BaseSettings):
    """Application configuration."""

    env: Literal["development", "staging", "production"] = Field(
        default="development", description="Application environment"
    )
    current_season: str = Field(default="2024", description="Current NBA season")

    model_config = SettingsConfigDict(env_prefix="APP_")


class Settings(BaseSettings):
    """Main application settings."""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    scraper: ScraperSettings = Field(default_factory=ScraperSettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    app: AppSettings = Field(default_factory=AppSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
