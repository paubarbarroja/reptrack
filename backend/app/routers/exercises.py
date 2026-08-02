from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=List[schemas.ExerciseOut])
def list_exercises(
    q: Optional[str] = Query(None, min_length=1, description="Filtra por nombre/categoría/músculo"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Catálogo global de ejercicios: el mismo listado para todos los usuarios."""
    query = db.query(models.Exercise)
    if q:
        needle = f"%{q.strip()}%"
        query = query.filter(
            models.Exercise.name.ilike(needle)
            | models.Exercise.category.ilike(needle)
            | models.Exercise.muscle_group.ilike(needle)
        )
    return query.order_by(models.Exercise.name).all()
