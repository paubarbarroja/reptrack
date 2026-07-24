from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import auth as auth_router
from .routers import exercises as exercises_router
from .routers import workouts as workouts_router
from .routers import progress as progress_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RepTrack API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(exercises_router.router)
app.include_router(workouts_router.router)
app.include_router(progress_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
