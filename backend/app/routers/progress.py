from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{exercise_id}", response_model=schemas.ProgressOut)
def get_progress(
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

    sets = (
        db.query(models.WorkoutSet, models.WorkoutSession.date)
        .join(models.WorkoutSession, models.WorkoutSet.session_id == models.WorkoutSession.id)
        .filter(
            models.WorkoutSet.exercise_id == exercise_id,
            models.WorkoutSession.owner_id == current_user.id,
        )
        .all()
    )

    by_date = defaultdict(list)
    for workout_set, session_date in sets:
        by_date[session_date].append(workout_set)

    points = []
    for d in sorted(by_date.keys()):
        day_sets = by_date[d]
        max_weight = max(s.weight_kg for s in day_sets)
        volume = sum(s.weight_kg * s.reps for s in day_sets)
        points.append(schemas.ProgressPoint(date=d, max_weight_kg=max_weight, volume_kg=volume))

    return schemas.ProgressOut(exercise_id=exercise.id, exercise_name=exercise.name, points=points)
