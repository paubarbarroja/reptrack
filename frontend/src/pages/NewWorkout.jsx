import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";

const RPE_OPTIONS = [
  { value: "", label: "Sin RPE" },
  { value: "10", label: "10 · Fallo total" },
  { value: "9.5", label: "9.5" },
  { value: "9", label: "9 · 1 rep en reserva" },
  { value: "8.5", label: "8.5" },
  { value: "8", label: "8 · 2 reps en reserva" },
  { value: "7.5", label: "7.5" },
  { value: "7", label: "7 · 3 reps en reserva" },
  { value: "6.5", label: "6.5" },
  { value: "6", label: "6 · Esfuerzo moderado" },
  { value: "5", label: "≤5 · Calentamiento / fácil" },
];

function emptySet(exerciseId) {
  return { exercise_id: exerciseId, set_number: 1, weight_kg: "", reps: "", rpe: "" };
}

export default function NewWorkout() {
  const [exercises, setExercises] = useState([]);
  const [newExerciseName, setNewExerciseName] = useState("");
  const [notes, setNotes] = useState("");
  const [sets, setSets] = useState([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api.listExercises().then((data) => {
      setExercises(data);
      if (data.length) setSets([emptySet(data[0].id)]);
    });
  }, []);

  async function addExercise(e) {
    e.preventDefault();
    if (!newExerciseName.trim()) return;
    try {
      const exercise = await api.createExercise({ name: newExerciseName.trim() });
      setExercises((prev) => [...prev, exercise]);
      setNewExerciseName("");
      setSets((prev) => (prev.length ? prev : [emptySet(exercise.id)]));
    } catch (err) {
      setError(err.message);
    }
  }

  function updateSet(index, field, value) {
    setSets((prev) => prev.map((s, i) => (i === index ? { ...s, [field]: value } : s)));
  }

  function addSetRow() {
    const lastExerciseId = sets.length ? sets[sets.length - 1].exercise_id : exercises[0]?.id;
    setSets((prev) => [...prev, emptySet(lastExerciseId)]);
  }

  function removeSetRow(index) {
    setSets((prev) => prev.filter((_, i) => i !== index));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const payload = {
        notes,
        sets: sets.map((s) => ({
          exercise_id: Number(s.exercise_id),
          set_number: Number(s.set_number) || 1,
          weight_kg: Number(s.weight_kg),
          reps: Number(s.reps),
          rpe: s.rpe ? Number(s.rpe) : null,
        })),
      };
      await api.createSession(payload);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h1>Registrar entreno</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h3>Añadir ejercicio nuevo</h3>
        <p className="hint">
          Créalo solo la primera vez que lo hagas — luego lo tendrás disponible para reutilizar en cualquier entreno.
        </p>
        <form onSubmit={addExercise} className="inline-form">
          <input
            placeholder="p. ej. Sentadilla"
            value={newExerciseName}
            onChange={(e) => setNewExerciseName(e.target.value)}
          />
          <button className="btn secondary" type="submit">Añadir</button>
        </form>
      </div>

      <form onSubmit={onSubmit} className="card">
        <div className="field">
          <label>Notas (opcional)</label>
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="p. ej. sensaciones del día, dolores, cambios de rutina..."
          />
        </div>

        <h3>Series</h3>
        <p className="hint">
          Añade una fila por cada serie que hagas: elige el ejercicio, el peso usado, las repeticiones
          que completaste y, si quieres, el RPE (lo duro que te resultó, del 1 al 10).
        </p>
        {exercises.length === 0 && <p className="hint">Añade al menos un ejercicio arriba antes de registrar series.</p>}
        {sets.map((s, i) => (
          <div className="set-card" key={i}>
            <div className="field set-field-exercise">
              <label>Ejercicio</label>
              <select value={s.exercise_id} onChange={(e) => updateSet(i, "exercise_id", e.target.value)}>
                {exercises.map((ex) => (
                  <option key={ex.id} value={ex.id}>{ex.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Peso (kg)</label>
              <input
                type="number" step="0.5" min="0" placeholder="p. ej. 60"
                value={s.weight_kg} onChange={(e) => updateSet(i, "weight_kg", e.target.value)} required
              />
            </div>
            <div className="field">
              <label>Repeticiones</label>
              <input
                type="number" min="1" placeholder="p. ej. 8"
                value={s.reps} onChange={(e) => updateSet(i, "reps", e.target.value)} required
              />
            </div>
            <div className="field set-field-rpe">
              <label>RPE (opcional) — esfuerzo percibido, 1-10</label>
              <select value={s.rpe} onChange={(e) => updateSet(i, "rpe", e.target.value)}>
                {RPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="set-field-remove">
              <button type="button" className="btn danger" onClick={() => removeSetRow(i)}>Quitar serie</button>
            </div>
          </div>
        ))}

        <button type="button" className="btn secondary" onClick={addSetRow} disabled={!exercises.length}>
          + Añadir serie
        </button>

        <div style={{ marginTop: 16 }}>
          <button className="btn" type="submit" disabled={!sets.length}>Guardar entreno</button>
        </div>
      </form>
    </div>
  );
}
