from datetime import date as date_type
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _serialize_session(session: models.WorkoutSession) -> schemas.WorkoutSessionOut:
    return schemas.WorkoutSessionOut(
        id=session.id,
        date=session.date,
        notes=session.notes,
        sets=[
            schemas.WorkoutSetOut(
                id=s.id,
                exercise_id=s.exercise_id,
                exercise_name=s.exercise.name if s.exercise else None,
                set_number=s.set_number,
                weight_kg=s.weight_kg,
                reps=s.reps,
                rpe=s.rpe,
            )
            for s in session.sets
        ],
    )


@router.get("", response_model=List[schemas.WorkoutSessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    sessions = (
        db.query(models.WorkoutSession)
        .options(joinedload(models.WorkoutSession.sets).joinedload(models.WorkoutSet.exercise))
        .filter(models.WorkoutSession.owner_id == current_user.id)
        .order_by(models.WorkoutSession.date.desc())
        .all()
    )
    return [_serialize_session(s) for s in sessions]


@router.post("", response_model=schemas.WorkoutSessionOut, status_code=201)
def create_session(
    payload: schemas.WorkoutSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    exercise_ids = {s.exercise_id for s in payload.sets}
    if exercise_ids:
        owned = (
            db.query(models.Exercise.id)
            .filter(models.Exercise.id.in_(exercise_ids), models.Exercise.owner_id == current_user.id)
            .all()
        )
        owned_ids = {row[0] for row in owned}
        if owned_ids != exercise_ids:
            raise HTTPException(status_code=400, detail="Algún ejercicio no es válido")

    session = models.WorkoutSession(
        owner_id=current_user.id,
        date=payload.date or date_type.today(),
        notes=payload.notes,
    )
    db.add(session)
    db.flush()

    for s in payload.sets:
        db.add(
            models.WorkoutSet(
                session_id=session.id,
                exercise_id=s.exercise_id,
                set_number=s.set_number,
                weight_kg=s.weight_kg,
                reps=s.reps,
                rpe=s.rpe,
            )
        )

    db.commit()
    db.refresh(session)
    return _serialize_session(session)


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    session = (
        db.query(models.WorkoutSession)
        .filter(models.WorkoutSession.id == session_id, models.WorkoutSession.owner_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    db.delete(session)
    db.commit()
