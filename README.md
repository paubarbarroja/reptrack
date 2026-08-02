# RepTrack

Webapp de seguimiento de entrenos para gimnasio: registra ejercicios, series (peso y repeticiones)
y visualiza tu progreso en gráficos por ejercicio.

## Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL, auth con JWT.
- **Frontend**: React + Vite + React Router + Recharts.
- **Infra**: Docker Compose (postgres + api + web servido con nginx, que hace de proxy a `/api`).

## Funcionalidad

- Registro / login de usuario (cada usuario ve solo sus datos).
- Alta de ejercicios propios (nombre + grupo muscular opcional).
- Registrar una sesión de entreno con varias series: ejercicio, peso (kg), reps, RPE opcional.
- Dashboard con historial de sesiones.
- Página de progreso: gráfico de evolución de peso máximo y volumen (peso × reps) por ejercicio a lo largo del tiempo.

## Levantar en local

```bash
cp .env.example .env   # y cambia SECRET_KEY
docker compose up -d --build
```

- Frontend: http://localhost:8080
- API (docs Swagger): http://localhost:8000/docs si expones el puerto del servicio `api`,
  o vía `http://localhost:8080/api/docs` a través del proxy de nginx.

## Desarrollo sin Docker

```bash
# backend
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://reptrack:reptrack@localhost:5432/reptrack
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev   # usa VITE_API_URL=http://localhost:8000 en un .env si hace falta
```

## Estructura

```
backend/
  app/
    main.py          # FastAPI app + routers
    models.py         # User, Exercise, WorkoutSession, WorkoutSet
    schemas.py         # Pydantic
    auth.py             # JWT + hashing
    routers/            # auth, exercises, workouts, progress
frontend/
  src/
    api.js             # cliente fetch + token
    App.jsx             # rutas
    pages/               # Login, Register, Dashboard, NewWorkout, Progress
```

## Pendiente / ideas futuras

- Plantillas de rutina reutilizables.
- Exportar historial a CSV.
- Comparativa entre ejercicios / grupos musculares.
