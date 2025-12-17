
"""Vaca ORM model modeling cattle lifecycle."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:  # pragma: no cover
    from app.models.usuario import Usuario
    from app.models.registro_salud import RegistroSalud
    from app.models.registro_peso import RegistroPeso


class SexoVaca(str, enum.Enum):
    HEMBRA = "H"
    MACHO = "M"


class EstadoVaca(str, enum.Enum):
    ACTIVA = "activa"
    ENFERMA = "enferma"
    VENDIDA = "vendida"
    FALLECIDA = "fallecida"


class Vaca(Base):
    __tablename__ = "vacas"
    __table_args__ = (
        UniqueConstraint("identificador", name="uq_vacas_identificador"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identificador: Mapped[str] = mapped_column(String(64), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    raza: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sexo: Mapped[SexoVaca] = mapped_column(SAEnum(SexoVaca, name="sexo_vaca"), nullable=False)
    estado: Mapped[EstadoVaca] = mapped_column(
        SAEnum(EstadoVaca, name="estado_vaca"),
        nullable=False,
        default=EstadoVaca.ACTIVA,
    )
    peso_actual: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    propietario: Mapped["Usuario"] = relationship("Usuario", back_populates="vacas")
    registros_salud: Mapped[List["RegistroSalud"]] = relationship(
        "RegistroSalud",
        back_populates="vaca",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RegistroSalud.fecha.desc()",
    )
    registros_peso: Mapped[List["RegistroPeso"]] = relationship(
        "RegistroPeso",
        back_populates="vaca",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RegistroPeso.fecha.desc()",
    )

    def actualizar_peso(self, nuevo_peso: float) -> None:
        if nuevo_peso <= 0:
            raise ValueError("El peso debe ser positivo")
        self.peso_actual = round(float(nuevo_peso), 2)

    def actualizar_estado(self, nuevo_estado: EstadoVaca) -> None:
        """Update the cattle status ensuring consistent transitions."""
        if not isinstance(nuevo_estado, EstadoVaca):
            raise ValueError("Estado inválido para la vaca")
        self.estado = nuevo_estado

    @property
    def edad_en_dias(self) -> Optional[int]:
        if not self.fecha_nacimiento:
            return None
        return (date.today() - self.fecha_nacimiento).days

    def resumen(self) -> str:
        """Return a short textual summary useful for logging."""
        edad = self.edad_en_dias
        edad_txt = f"{edad} días" if edad is not None else "edad desconocida"
        return f"{self.identificador} - {self.estado} - {edad_txt}"

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Vaca {self.identificador} ({self.estado})>"


__all__ = ["Vaca", "SexoVaca", "EstadoVaca"]
