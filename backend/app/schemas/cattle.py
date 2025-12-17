"""Cattle management schemas."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class CattleCreate(BaseModel):
    identificador: str = Field(..., max_length=64)
    nombre: str = Field(..., max_length=120)
    raza: Optional[str] = Field(None, max_length=120)
    fecha_nacimiento: Optional[date] = None
    sexo: str = Field(..., pattern="^(H|M)$")
    peso_actual: Optional[float] = Field(None, gt=0)


class CattleUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=120)
    raza: Optional[str] = Field(None, max_length=120)
    estado: Optional[str] = None
    peso_actual: Optional[float] = Field(None, gt=0)


class CattleResponse(BaseModel):
    id: str
    identificador: str
    nombre: str
    raza: Optional[str]
    fecha_nacimiento: Optional[date]
    sexo: str
    estado: str
    peso_actual: Optional[float]
    
    class Config:
        from_attributes = True


class HealthRecordCreate(BaseModel):
    id_vaca: str
    fecha: date
    tipo: str
    descripcion: Optional[str] = None
    medicamento: Optional[str] = None
    dosis: Optional[str] = None
    veterinario: Optional[str] = None


class WeightRecordCreate(BaseModel):
    id_vaca: str
    fecha: date
    peso: float = Field(..., gt=0)
    unidad: str = Field(default="kg")
    metodo: str = Field(default="manual")
