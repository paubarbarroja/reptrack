from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=List[schemas.ExerciseOut])
def list_exercises(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Exercise)
        .filter(models.Exercise.owner_id == current_user.id)
        .order_by(models.Exercise.name)
        .all()
    )


@router.post("", response_model=schemas.ExerciseOut, status_code=201)
def create_exercise(
    payload: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    existing = (
        db.query(models.Exercise)
        .filter(models.Exercise.owner_id == current_user.id, models.Exercise.name == payload.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes un ejercicio con ese nombre")

    exercise = models.Exercise(
        owner_id=current_user.id, name=payload.name, muscle_group=payload.muscle_group
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}", status_code=204)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    exercise = (
        db.query(models.Exercise)
        .filter(models.Exercise.id == exercise_id, models.Exercise.owner_id == current_user.id)
        .first()
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    db.delete(exercise)
    db.commit()
