"""Cattle management router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.vaca import Vaca
from app.models.registro_salud import RegistroSalud
from app.models.registro_peso import RegistroPeso
from app.schemas.cattle import (
    CattleCreate, 
    CattleUpdate, 
    CattleResponse,
    HealthRecordCreate,
    WeightRecordCreate
)

router = APIRouter(prefix="/cattle", tags=["cattle"])


@router.get("/", response_model=List[CattleResponse])
def list_cattle(
    skip: int = 0,
    limit: int = 100,
    estado: str = None,
    db: Session = Depends(get_db)
):
    """List all cattle with optional filters."""
    query = db.query(Vaca)
    
    if estado:
        query = query.filter(Vaca.estado == estado)
    
    cattle = query.offset(skip).limit(limit).all()
    return cattle


@router.post("/", response_model=CattleResponse, status_code=status.HTTP_201_CREATED)
def create_cattle(cattle_data: CattleCreate, db: Session = Depends(get_db)):
    """Create a new cattle record."""
    # Check if identificador exists
    existing = db.query(Vaca).filter(Vaca.identificador == cattle_data.identificador).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cattle with this identificador already exists"
        )
    
    # Get first user as owner (mock)
    from app.models.usuario import Usuario
    user = db.query(Usuario).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users in system")
    
    cattle = Vaca(
        identificador=cattle_data.identificador,
        nombre=cattle_data.nombre,
        raza=cattle_data.raza,
        fecha_nacimiento=cattle_data.fecha_nacimiento,
        sexo=cattle_data.sexo,
        peso_actual=cattle_data.peso_actual,
        id_usuario=user.id
    )
    
    db.add(cattle)
    db.commit()
    db.refresh(cattle)
    
    return cattle


@router.get("/{cattle_id}", response_model=CattleResponse)
def get_cattle(cattle_id: str, db: Session = Depends(get_db)):
    """Get cattle by ID."""
    cattle = db.query(Vaca).filter(Vaca.id == cattle_id).first()
    if not cattle:
        raise HTTPException(status_code=404, detail="Cattle not found")
    return cattle


@router.put("/{cattle_id}", response_model=CattleResponse)
def update_cattle(
    cattle_id: str, 
    cattle_data: CattleUpdate, 
    db: Session = Depends(get_db)
):
    """Update cattle information."""
    cattle = db.query(Vaca).filter(Vaca.id == cattle_id).first()
    if not cattle:
        raise HTTPException(status_code=404, detail="Cattle not found")
    
    update_data = cattle_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cattle, field, value)
    
    db.commit()
    db.refresh(cattle)
    
    return cattle


@router.delete("/{cattle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cattle(cattle_id: str, db: Session = Depends(get_db)):
    """Delete cattle record."""
    cattle = db.query(Vaca).filter(Vaca.id == cattle_id).first()
    if not cattle:
        raise HTTPException(status_code=404, detail="Cattle not found")
    
    db.delete(cattle)
    db.commit()


@router.post("/health-records", status_code=status.HTTP_201_CREATED)
def create_health_record(record: HealthRecordCreate, db: Session = Depends(get_db)):
    """Create health record."""
    health_record = RegistroSalud(**record.model_dump())
    db.add(health_record)
    db.commit()
    return {"message": "Health record created"}


@router.post("/weight-records", status_code=status.HTTP_201_CREATED)
def create_weight_record(record: WeightRecordCreate, db: Session = Depends(get_db)):
    """Create weight record."""
    weight_record = RegistroPeso(**record.model_dump())
    db.add(weight_record)
    db.commit()
    return {"message": "Weight record created"}
