import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { api } from "../api.js";

export default function Progress() {
  const [exercises, setExercises] = useState([]);
  const [exerciseId, setExerciseId] = useState(null);
  const [points, setPoints] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listExercises().then((data) => {
      setExercises(data);
      if (data.length) setExerciseId(data[0].id);
    });
  }, []);

  useEffect(() => {
    if (!exerciseId) return;
    api
      .getProgress(exerciseId)
      .then((data) => setPoints(data.points))
      .catch((e) => setError(e.message));
  }, [exerciseId]);

  return (
    <div>
      <h1>Progreso</h1>
      {error && <p className="error">{error}</p>}
      {exercises.length === 0 && <p>Todavía no tienes ejercicios registrados.</p>}

      {exercises.length > 0 && (
        <div className="field" style={{ maxWidth: 300 }}>
          <label>Ejercicio</label>
          <select value={exerciseId ?? ""} onChange={(e) => setExerciseId(Number(e.target.value))}>
            {exercises.map((ex) => (
              <option key={ex.id} value={ex.id}>{ex.name}</option>
            ))}
          </select>
        </div>
      )}

      {points.length === 0 && exerciseId && <p>Aún no hay datos para este ejercicio.</p>}

      {points.length > 0 && (
        <div className="card" style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2c2f38" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ background: "#171a21", border: "1px solid #2c2f38" }} />
              <Legend />
              <Line type="monotone" dataKey="max_weight_kg" name="Peso máx (kg)" stroke="#22c55e" strokeWidth={2} />
              <Line type="monotone" dataKey="volume_kg" name="Volumen (kg)" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
