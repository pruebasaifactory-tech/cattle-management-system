"""Paquete principal del backend.

Este módulo expone utilidades ligeras para obtener metadatos del proyecto y
mantener centralizada la definición de los microservicios principales.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata as _metadata
from typing import Dict, Tuple

_MICROSERVICE_NAMES: Tuple[str, ...] = ("auth", "cattle", "reports")


def get_version(default: str = "0.1.0") -> str:
    """Devuelve la versión instalada del paquete.

    Cuando la app se ejecuta fuera de un entorno instalado con `pip`,
    se regresa el valor por defecto para mantener compatibilidad.
    """

    try:
        return _metadata.version("cattle-backend")
    except _metadata.PackageNotFoundError:
        return default


def list_microservices() -> Tuple[str, ...]:
    """Enumeración inmutable de microservicios declarados."""

    return _MICROSERVICE_NAMES


@dataclass(frozen=True)
class ServiceMetadata:
    """Mantiene metadatos mínimos para cada microservicio."""

    name: str
    description: str
    docs_url: str


def describe_services() -> Dict[str, ServiceMetadata]:
    """Construye un diccionario con descripciones de referencia."""

    return {
        "auth": ServiceMetadata(
            name="auth",
            description="Gestión de usuarios, roles y emisión de JWT",
            docs_url="/docs#auth",
        ),
        "cattle": ServiceMetadata(
            name="cattle",
            description="Registro y administración de ganado, salud y peso",
            docs_url="/docs#cattle",
        ),
        "reports": ServiceMetadata(
            name="reports",
            description="Generación de reportes CSV y agregaciones",
            docs_url="/docs#reports",
        ),
    }


__all__ = [
    "ServiceMetadata",
    "describe_services",
    "get_version",
    "list_microservices",
]
