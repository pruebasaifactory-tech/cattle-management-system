
"""Registro histórico de peso por animal."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.vaca import Vaca


class UnidadPeso(str, enum.Enum):
    """Unidades soportadas para el registro de peso."""

    KILOGRAMO = "kg"
    LIBRA = "lb"

    def to_kilos(self, value: float) -> float:
        return value if self == UnidadPeso.KILOGRAMO else value * 0.453592


class MetodoPesaje(str, enum.Enum):
    """Describe cómo se capturó la medición de peso."""

    MANUAL = "manual"
    BASCULA = "bascula"
    AUTOMATICO = "automatico"


class RegistroPeso(Base):
    """Modelo ORM que guarda cada registro de peso."""

    __tablename__ = "registros_peso"
    __table_args__ = {"comment": "Historial de pesaje"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_vaca: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vacas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    peso: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unidad: Mapped[UnidadPeso] = mapped_column(SAEnum(UnidadPeso, name="unidad_peso"), nullable=False)
    metodo: Mapped[MetodoPesaje] = mapped_column(
        SAEnum(MetodoPesaje, name="metodo_pesaje"), nullable=False, default=MetodoPesaje.MANUAL
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vaca: Mapped["Vaca"] = relationship("Vaca", back_populates="registros_peso")

    @property
    def peso_formateado(self) -> str:
        """Return a human friendly formatted weight string."""
        return f"{float(self.peso):.2f} {self.unidad.value}"

    def peso_en_kilos(self) -> float:
        return self.unidad.to_kilos(float(self.peso))

    def variacion_respecto(self, anterior: Optional["RegistroPeso"]) -> Optional[float]:
        if not anterior:
            return None
        return round(self.peso_en_kilos() - anterior.peso_en_kilos(), 2)

    def actualizar_peso(self, nuevo_peso: float, unidad: Optional[UnidadPeso] = None) -> None:
        if nuevo_peso <= 0:
            raise ValueError("El peso debe ser positivo")
        self.peso = round(nuevo_peso, 2)
        if unidad:
            self.unidad = unidad

    def descripcion(self, anterior: Optional["RegistroPeso"] = None) -> str:
        variacion = ""
        if anterior:
            diff = self.variacion_respecto(anterior)
            if diff is not None:
                signo = "+" if diff >= 0 else ""
                variacion = f"({signo}{diff} kg)"
        return f"{self.fecha.isoformat()} - {self.peso_formateado} {variacion}".strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "id_vaca": str(self.id_vaca),
            "fecha": self.fecha.isoformat(),
            "peso": float(self.peso),
            "unidad": self.unidad.value,
            "metodo": self.metodo.value,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def crear(
        cls,
        *,
        vaca: "Vaca",
        fecha: date,
        peso: float,
        unidad: UnidadPeso = UnidadPeso.KILOGRAMO,
        metodo: MetodoPesaje = MetodoPesaje.MANUAL,
    ) -> "RegistroPeso":
        registro = cls(vaca=vaca, fecha=fecha, peso=peso, unidad=unidad, metodo=metodo)
        return registro

    @staticmethod
    def peso_promedio(registros: list["RegistroPeso"]) -> Optional[float]:
        if not registros:
            return None
        kilos = [registro.peso_en_kilos() for registro in registros]
        return round(sum(kilos) / len(kilos), 2)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RegistroPeso {self.peso} {self.unidad.value} {self.fecha}>"


__all__ = ["RegistroPeso", "UnidadPeso", "MetodoPesaje"]
