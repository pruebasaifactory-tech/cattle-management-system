
"""Reporte ORM model."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, JSON, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.mutable import MutableDict

from app.core.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.usuario import Usuario


class TipoReporte(str, enum.Enum):
    """Tipos soportados de reportes para el sistema."""

    INVENTARIO = "inventario"
    SALUD = "salud"

    def descripcion(self) -> str:
        if self == TipoReporte.INVENTARIO:
            return "Listado completo de ganado con filtros básicos"
        return "Detalle de registros de salud por rango de fechas"

    @staticmethod
    def valores() -> tuple[str, ...]:
        return tuple(item.value for item in TipoReporte)


class EstadoReporte(str, enum.Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"


class Reporte(Base):
    """Modelo de reporte exportable almacenado en S3."""

    __tablename__ = "reportes"
    __table_args__ = {"comment": "Solicitudes de generación de reportes"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[TipoReporte] = mapped_column(SAEnum(TipoReporte, name="tipo_reporte"), nullable=False)
    parametros: Mapped[Dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), nullable=False, default=dict)
    estado: Mapped[EstadoReporte] = mapped_column(
        SAEnum(EstadoReporte, name="estado_reporte"), nullable=False, default=EstadoReporte.PENDIENTE
    )
    url_s3: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_solicitud: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_generacion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    autor: Mapped[Optional["Usuario"]] = relationship("Usuario", back_populates="reportes")

    @classmethod
    def crear(
        cls,
        *,
        autor: Optional["Usuario"],
        tipo: TipoReporte,
        parametros: Optional[Dict[str, Any]] = None,
    ) -> "Reporte":
        return cls(autor=autor, tipo=tipo, parametros=parametros or {})

    def marcar_en_proceso(self) -> None:
        self.estado = EstadoReporte.PROCESANDO

    def marcar_completado(self, url: str) -> None:
        self.estado = EstadoReporte.COMPLETADO
        self.url_s3 = url
        self.fecha_generacion = datetime.utcnow()

    def marcar_fallido(self) -> None:
        self.estado = EstadoReporte.FALLIDO
        self.fecha_generacion = datetime.utcnow()

    def es_descargable(self) -> bool:
        return self.estado == EstadoReporte.COMPLETADO and bool(self.url_s3)

    def actualizar_parametros(self, nuevos: Dict[str, Any]) -> None:
        self.parametros.update(nuevos)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "tipo": self.tipo.value,
            "estado": self.estado.value,
            "parametros": self.parametros,
            "url_s3": self.url_s3,
            "fecha_solicitud": self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            "fecha_generacion": self.fecha_generacion.isoformat() if self.fecha_generacion else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Reporte {self.tipo.value} {self.estado.value}>"


__all__ = ["Reporte", "TipoReporte", "EstadoReporte"]
