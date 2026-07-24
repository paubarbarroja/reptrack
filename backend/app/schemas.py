from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Exercise ---

class ExerciseCreate(BaseModel):
    name: str
    muscle_group: Optional[str] = None


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    muscle_group: Optional[str] = None


# --- Workout set ---

class WorkoutSetCreate(BaseModel):
    exercise_id: int
    set_number: int = 1
    weight_kg: float
    reps: int
    rpe: Optional[float] = None


class WorkoutSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    exercise_id: int
    exercise_name: Optional[str] = None
    set_number: int
    weight_kg: float
    reps: int
    rpe: Optional[float] = None


# --- Workout session ---

class WorkoutSessionCreate(BaseModel):
    date: Optional[date] = None
    notes: Optional[str] = None
    sets: List[WorkoutSetCreate] = []


class WorkoutSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    notes: Optional[str] = None
    sets: List[WorkoutSetOut] = []


# --- Progress ---

class ProgressPoint(BaseModel):
    date: date
    max_weight_kg: float
    volume_kg: float  # sum(weight * reps) for that day


class ProgressOut(BaseModel):
    exercise_id: int
    exercise_name: str
    points: List[ProgressPoint]
