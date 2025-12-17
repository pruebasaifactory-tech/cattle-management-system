"""Utilities for importing and enumerating ORM models."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module, reload
from typing import Dict, List, Tuple, Type

from sqlalchemy.orm import DeclarativeMeta

MODEL_MODULES: Tuple[str, ...] = (
    "app.models.usuario",
    "app.models.vaca",
    "app.models.registro_salud",
    "app.models.registro_peso",
    "app.models.reporte",
)


def _discover_models() -> Tuple[DeclarativeMeta, ...]:
    """Import modules lazily and cache discovered declarative classes."""
    discovered: List[DeclarativeMeta] = []
    for dotted_path in MODEL_MODULES:
        module = import_module(dotted_path)
        for attr in vars(module).values():
            if isinstance(getattr(attr, "__mro__", ()), tuple) and hasattr(attr, "__tablename__"):
                discovered.append(attr)  # type: ignore[arg-type]
    unique = list(dict.fromkeys(discovered))
    return tuple(unique)


@lru_cache(maxsize=1)
def all_models() -> Tuple[DeclarativeMeta, ...]:
    """Return all mapped classes ensuring modules are imported."""
    return _discover_models()


def model_by_name(name: str) -> Type[DeclarativeMeta]:
    """Return the model class matching *name* regardless of casing."""
    normalized = name.lower()
    for model in all_models():
        if model.__name__.lower() == normalized or model.__tablename__.lower() == normalized:
            return model
    raise LookupError(f"Modelo '{name}' no encontrado")


def metadata_summary() -> str:
    """Produce a textual summary of the mapped tables."""
    lines = ["Modelos registrados:"]
    for model in all_models():
        lines.append(f"- {model.__tablename__} ({model.__name__})")
    return "\n".join(lines)


def iter_model_names() -> Tuple[str, ...]:
    """Return the tuple of model class names."""
    return tuple(model.__name__ for model in all_models())


def ensure_imported() -> None:
    """Idempotent helper that forces model modules to be imported."""
    _ = all_models()


def reload_models() -> Tuple[DeclarativeMeta, ...]:
    """Force a reload of model modules (useful when running in notebooks)."""
    all_models.cache_clear()
    for dotted_path in MODEL_MODULES:
        module = import_module(dotted_path)
        reload(module)
    return _discover_models()


def primary_keys_map() -> Dict[str, str]:
    """Return a mapping of table name to primary key column name."""
    mapping: Dict[str, str] = {}
    for model in all_models():
        pk = list(model.__table__.primary_key.columns)[0].name  # type: ignore[attr-defined]
        mapping[model.__tablename__] = pk
    return mapping


from app.models.usuario import Usuario  # noqa: E402
from app.models.vaca import Vaca  # noqa: E402
from app.models.registro_salud import RegistroSalud  # noqa: E402
from app.models.registro_peso import RegistroPeso  # noqa: E402
from app.models.reporte import Reporte  # noqa: E402


__all__ = [
    "Usuario",
    "Vaca",
    "RegistroSalud",
    "RegistroPeso",
    "Reporte",
    "all_models",
    "model_by_name",
    "metadata_summary",
    "iter_model_names",
    "ensure_imported",
    "reload_models",
    "primary_keys_map",
]
