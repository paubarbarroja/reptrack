import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

export default function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listSessions()
      .then(setSessions)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function onDelete(id) {
    await api.deleteSession(id);
    setSessions((prev) => prev.filter((s) => s.id !== id));
  }

  return (
    <div>
      <h1>Tus entrenos</h1>
      {error && <p className="error">{error}</p>}
      {loading && <p>Cargando...</p>}
      {!loading && sessions.length === 0 && (
        <div className="card">
          <p>Todavía no has registrado ningún entreno.</p>
          <Link className="btn" to="/new">Registrar el primero</Link>
        </div>
      )}
      {sessions.map((session) => (
        <div className="card" key={session.id}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <h3>{session.date}</h3>
            <button className="btn danger" onClick={() => onDelete(session.id)}>Eliminar</button>
          </div>
          {session.notes && <p>{session.notes}</p>}
          <ul>
            {session.sets.map((set) => (
              <li key={set.id}>
                {set.exercise_name}: {set.weight_kg} kg × {set.reps} reps
                {set.rpe ? ` (RPE ${set.rpe})` : ""}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
