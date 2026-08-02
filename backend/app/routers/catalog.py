import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from .. import models, schemas, auth

router = APIRouter(prefix="/catalog", tags=["catalog"])

_CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "exercise_catalog.json"

with open(_CATALOG_PATH, encoding="utf-8") as f:
    _CATALOG: List[dict] = json.load(f)

# Lookup by lowercased name for exact-match muscle group prefill.
_CATALOG_BY_NAME = {item["name"].lower(): item for item in _CATALOG}


@router.get("/exercises", response_model=List[schemas.CatalogExerciseOut])
def search_catalog(
    q: Optional[str] = Query(None, min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_user),
):
    if not q:
        return _CATALOG[:limit]

    needle = q.strip().lower()
    matches = [
        item
        for item in _CATALOG
        if needle in item["name"].lower()
        or needle in (item.get("category") or "").lower()
        or needle in (item.get("target") or "").lower()
        or needle in (item.get("muscle_group") or "").lower()
    ]
    # Prioritize matches where the name starts with the query.
    matches.sort(key=lambda item: (not item["name"].lower().startswith(needle), item["name"]))
    return matches[:limit]
