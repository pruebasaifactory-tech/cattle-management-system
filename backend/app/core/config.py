"""Centralized configuration helpers for the Vacuno backend."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

_ALLOWED_ENVIRONMENTS = {"development", "staging", "production", "test"}
_DEFAULT_DB_PORT = 5432
_DEFAULT_TOKEN_EXP_MINUTES = 60


def _clean(value: Optional[str], default: Optional[str] = None) -> Optional[str]:
    """Return a trimmed environment value or *default* when the value is empty."""
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def _as_bool(value: Optional[str], default: bool = False) -> bool:
    """Translate textual truthy/falsey values to booleans."""
    if value is None:
        return default
    return value.strip().lower() in {"true", "1", "yes", "on"}


def _as_int(value: Optional[str], default: int) -> int:
    """Safely cast a string to int while falling back to *default*."""
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


@dataclass
class DatabaseConfig:
    """Database connection options used throughout the backend."""

    host: str = "localhost"
    port: int = _DEFAULT_DB_PORT
    name: str = "vacuno"
    user: str = "postgres"
    password: str = "postgres"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    ssl_mode: Optional[str] = None

    def sqlalchemy_dsn(self) -> str:
        """Build a SQLAlchemy-friendly DSN string for PostgreSQL."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    def engine_kwargs(self) -> Dict[str, Any]:
        """Return keyword arguments passed into :func:`sqlalchemy.create_engine`."""
        kwargs: Dict[str, Any] = {
            "echo": self.echo,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_pre_ping": True,
        }
        if self.ssl_mode:
            kwargs.setdefault("connect_args", {})["sslmode"] = self.ssl_mode
        return kwargs


@dataclass
class SecurityConfig:
    """Security knobs for JWT and password hashing."""

    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_exp_minutes: int = _DEFAULT_TOKEN_EXP_MINUTES
    password_salt_rounds: int = 12


@dataclass
class AppConfig:
    """Application level metadata used by logging and diagnostics."""

    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])


@dataclass
class Settings:
    """Aggregated configuration pointer exposed as a singleton."""

    database: DatabaseConfig
    security: SecurityConfig
    app: AppConfig

    @classmethod
    def from_env(cls, env: Optional[Dict[str, str]] = None) -> "Settings":
        env_map = os.environ if env is None else env
        db = DatabaseConfig(
            host=_clean(env_map.get("POSTGRES_HOST"), "localhost"),
            port=_as_int(env_map.get("POSTGRES_PORT"), _DEFAULT_DB_PORT),
            name=_clean(env_map.get("POSTGRES_DB"), "vacuno"),
            user=_clean(env_map.get("POSTGRES_USER"), "postgres"),
            password=_clean(env_map.get("POSTGRES_PASSWORD"), "postgres"),
            echo=_as_bool(env_map.get("SQL_ECHO"), False),
            pool_size=_as_int(env_map.get("SQL_POOL_SIZE"), 5),
            max_overflow=_as_int(env_map.get("SQL_MAX_OVERFLOW"), 10),
            ssl_mode=_clean(env_map.get("SQL_SSL_MODE")),
        )
        security = SecurityConfig(
            secret_key=_clean(env_map.get("SECRET_KEY"), "change-me"),
            algorithm=_clean(env_map.get("JWT_ALGORITHM"), "HS256"),
            access_token_exp_minutes=_as_int(
                env_map.get("ACCESS_TOKEN_EXPIRE_MINUTES"), _DEFAULT_TOKEN_EXP_MINUTES
            ),
            password_salt_rounds=_as_int(env_map.get("PASSWORD_SALT_ROUNDS"), 12),
        )
        env_name = _clean(env_map.get("APP_ENV"), "development").lower()
        if env_name not in _ALLOWED_ENVIRONMENTS:
            env_name = "development"
        app = AppConfig(
            environment=env_name,
            debug=_as_bool(env_map.get("APP_DEBUG"), env_name != "production"),
            log_level=_clean(env_map.get("LOG_LEVEL"), "INFO"),
        )
        return cls(database=db, security=security, app=app)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "database": self.database.__dict__,
            "security": self.security.__dict__,
            "app": {
                "environment": self.app.environment,
                "debug": self.app.debug,
                "log_level": self.app.log_level,
                "project_root": str(self.app.project_root),
            },
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached :class:`Settings` instance."""
    return Settings.from_env()


settings = get_settings()

__all__ = [
    "DatabaseConfig",
    "SecurityConfig",
    "AppConfig",
    "Settings",
    "settings",
    "get_settings",
]
