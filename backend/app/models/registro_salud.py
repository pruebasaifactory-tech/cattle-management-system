
"""Registro de salud para cada vaca."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.vaca import Vaca


class TipoSalud(str, enum.Enum):
    """Enumeración de eventos médicos soportados por el sistema."""

    VACUNACION = "vacunacion"
    DESPARASITACION = "desparasitacion"
    REVISION = "revision"
    TRATAMIENTO = "tratamiento"
    OTRO = "otro"

    @classmethod
    def from_text(cls, raw: str) -> "TipoSalud":
        """Map user provided text to a valid enum value."""
        normalized = raw.strip().lower()
        for item in cls:
            if normalized == item.value:
                return item
        return cls.OTRO

    def requires_follow_up(self) -> bool:
        """Return True when the record type typically needs follow-up checks."""
        return self in {TipoSalud.TRATAMIENTO, TipoSalud.REVISION}


class RegistroSalud(Base):
    """Evento médico registrado para una vaca."""

    __tablename__ = "registros_salud"
    __table_args__ = {"comment": "Historial médico detallado"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_vaca: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vacas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[TipoSalud] = mapped_column(SAEnum(TipoSalud, name="tipo_salud"), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medicamento: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dosis: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    veterinario: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vaca: Mapped["Vaca"] = relationship("Vaca", back_populates="registros_salud")

    PAYLOAD_FIELDS = {"fecha", "tipo", "descripcion", "medicamento", "dosis", "veterinario"}

    @property
    def descripcion_resumida(self) -> Optional[str]:
        """Return a truncated description for UI listings."""
        if not self.descripcion:
            return None
        return self.descripcion if len(self.descripcion) < 60 else f"{self.descripcion[:57]}..."

    @property
    def requiere_medicamento(self) -> bool:
        """Indicate whether medication information is needed."""
        return self.tipo in {TipoSalud.TRATAMIENTO, TipoSalud.VACUNACION} and not self.medicamento

    def asignar_medicamento(self, nombre: str, dosis: Optional[str] = None) -> None:
        if not nombre:
            raise ValueError("El nombre del medicamento es obligatorio")
        self.medicamento = nombre
        self.dosis = dosis

    def asignar_profesional(self, nombre: str) -> None:
        if not nombre.strip():
            raise ValueError("Debe especificarse el nombre del veterinario")
        self.veterinario = nombre.strip()

    def resumen(self) -> str:
        desc = self.descripcion_resumida or "sin descripcion"
        return f"{self.fecha.isoformat()} - {self.tipo.value} ({desc})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "id_vaca": str(self.id_vaca),
            "fecha": self.fecha.isoformat(),
            "tipo": self.tipo.value,
            "descripcion": self.descripcion,
            "medicamento": self.medicamento,
            "dosis": self.dosis,
            "veterinario": self.veterinario,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    def update_from_payload(self, payload: Dict[str, Any]) -> None:
        for key in self.PAYLOAD_FIELDS:
            if key not in payload:
                continue
            if key == "tipo":
                self.tipo = TipoSalud.from_text(payload[key])
            elif key == "fecha":
                value = payload[key]
                self.fecha = value if isinstance(value, date) else date.fromisoformat(value)
            else:
                setattr(self, key, payload[key])

    @classmethod
    def crear_desde_payload(cls, *, vaca: "Vaca", payload: Dict[str, Any]) -> "RegistroSalud":
        payload = payload.copy()
        payload["tipo"] = TipoSalud.from_text(payload["tipo"])
        fecha = payload["fecha"]
        fecha = fecha if isinstance(fecha, date) else date.fromisoformat(fecha)
        registro = cls(
            vaca=vaca,
            fecha=fecha,
            tipo=payload["tipo"],
            descripcion=payload.get("descripcion"),
            medicamento=payload.get("medicamento"),
            dosis=payload.get("dosis"),
            veterinario=payload.get("veterinario"),
        )
        return registro

    def dias_desde_evento(self) -> int:
        return (date.today() - self.fecha).days

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RegistroSalud {self.tipo.value} {self.fecha}>"


__all__ = ["RegistroSalud", "TipoSalud"]
