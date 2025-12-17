"""Utilidades compartidas del núcleo de la aplicación."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict


class AppEnv(str, Enum):
    """Entornos admitidos para el despliegue."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ServiceSlug(str, Enum):
    """Identificadores cortos de cada microservicio."""

    AUTH = "auth"
    CATTLE = "cattle"
    REPORTS = "reports"


@dataclass(frozen=True)
class CorePaths:
    """Agrupa rutas clave usadas por el backend."""

    base_dir: Path
    app_dir: Path
    config_dir: Path

    @staticmethod
    def discover(start: Path | None = None) -> "CorePaths":
        root = start or Path(__file__).resolve().parents[2]
        return CorePaths(
            base_dir=root,
            app_dir=root / "app",
            config_dir=root / "config",
        )


def service_prefix(service: ServiceSlug) -> str:
    """Genera un prefijo consistente para logs y métricas."""

    return f"svc.{service.value}"


def default_headers(service: ServiceSlug) -> Dict[str, str]:
    """Cabeceras comunes para peticiones salientes del servicio dado."""

    return {
        "X-Service-Name": service.value,
        "X-Service-Prefix": service_prefix(service),
    }


__all__ = [
    "AppEnv",
    "ServiceSlug",
    "CorePaths",
    "default_headers",
    "service_prefix",
]
