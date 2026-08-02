"""Migración auto-aplicada y siembra del catálogo global de ejercicios.

Antes de este cambio, `exercises` era una tabla por-usuario (columna owner_id
+ unique(owner_id, name)). Ahora `exercises` es un catálogo global: el mismo
listado para todo el mundo, sembrado una vez desde data/exercise_catalog.json
(un dataset externo recortado a solo texto: nombre, categoría y grupo
muscular — sin imágenes ni vídeos, por la licencia no-comercial del dataset
original).

`models.Base.metadata.create_all()` no altera tablas ya existentes, así que
en un despliegue que ya tenía la tabla `exercises` con la columna owner_id
hace falta migrarla a mano antes de poder sembrar el catálogo. Esta función
se ejecuta en cada arranque, es idempotente y no toca workout_sessions ni
workout_sets (el historial de entrenos existente se conserva intacto).
"""

import json
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from . import models

_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "exercise_catalog.json"


def migrate_legacy_exercise_table() -> None:
    inspector = inspect(engine)
    if "exercises" not in inspector.get_table_names():
        return  # tabla nueva, create_all() la creará ya con el esquema correcto

    columns = {c["name"] for c in inspector.get_columns("exercises")}
    if "owner_id" not in columns:
        return  # ya migrada

    unique_constraint_names = {uc["name"] for uc in inspector.get_unique_constraints("exercises")}

    with engine.begin() as conn:
        for uc in inspector.get_unique_constraints("exercises"):
            if set(uc.get("column_names", [])) == {"owner_id", "name"}:
                conn.execute(text(f'ALTER TABLE exercises DROP CONSTRAINT IF EXISTS "{uc["name"]}"'))
        conn.execute(text("ALTER TABLE exercises DROP COLUMN IF EXISTS owner_id"))
        conn.execute(text("ALTER TABLE exercises ADD COLUMN IF NOT EXISTS category VARCHAR"))

        if "uq_exercise_name" not in unique_constraint_names:
            # Distintos usuarios podían tener ejercicios con el mismo nombre bajo el
            # esquema antiguo. Antes de hacer el nombre único a nivel global, fusiona
            # duplicados (por nombre, sin distinguir mayúsculas): conserva la fila con
            # id más bajo y repunta los sets que colgaban de las duplicadas, para no
            # perder historial de entrenos.
            rows = conn.execute(text("SELECT id, name FROM exercises ORDER BY id")).fetchall()
            seen = {}
            for row_id, name in rows:
                key = (name or "").strip().lower()
                if key in seen:
                    keep_id = seen[key]
                    conn.execute(
                        text("UPDATE workout_sets SET exercise_id = :keep WHERE exercise_id = :dup"),
                        {"keep": keep_id, "dup": row_id},
                    )
                    conn.execute(text("DELETE FROM exercises WHERE id = :dup"), {"dup": row_id})
                else:
                    seen[key] = row_id
            conn.execute(text("ALTER TABLE exercises ADD CONSTRAINT uq_exercise_name UNIQUE (name)"))


def seed_exercise_catalog() -> int:
    if not _CATALOG_PATH.exists():
        return 0

    with open(_CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)

    db: Session = SessionLocal()
    try:
        existing_names = {
            name.lower() for (name,) in db.query(models.Exercise.name).all()
        }
        seen = set(existing_names)
        inserted = 0
        for item in catalog:
            name = (item.get("name") or "").strip()
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            db.add(
                models.Exercise(
                    name=name,
                    category=item.get("category"),
                    muscle_group=item.get("target") or item.get("muscle_group"),
                )
            )
            inserted += 1
        if inserted:
            db.commit()
        return inserted
    finally:
        db.close()
