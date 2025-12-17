
"""Usuario ORM model with hashing and JWT helpers."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from app.models.vaca import Vaca
    from app.models.reporte import Reporte


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, enum.Enum):
    """Accepted roles for the system."""

    ADMIN = "admin"
    FIELD = "field"


class Usuario(Base):
    """User entity storing authentication credentials."""

    __tablename__ = "usuarios"
    __table_args__ = {"comment": "Usuarios autenticados del sistema"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="rol_usuario"),
        nullable=False,
        default=UserRole.FIELD,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    vacas: Mapped[List["Vaca"]] = relationship(
        "Vaca",
        back_populates="propietario",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reportes: Mapped[List["Reporte"]] = relationship(
        "Reporte",
        back_populates="autor",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def set_password(self, raw_password: str) -> None:
        if not raw_password or len(raw_password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        self.password_hash = pwd_context.hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password_hash)

    def generate_access_token(
        self,
        expires_minutes: Optional[int] = None,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        exp_minutes = expires_minutes or settings.security.access_token_exp_minutes
        payload: Dict[str, Any] = {
            "sub": str(self.id),
            "role": self.rol.value,
            "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, settings.security.secret_key, algorithm=settings.security.algorithm)

    @property
    def is_admin(self) -> bool:
        return self.rol == UserRole.ADMIN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol.value,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }


__all__ = ["Usuario", "UserRole"]
