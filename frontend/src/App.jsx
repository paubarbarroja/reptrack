import { Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { isLoggedIn, clearToken } from "./api.js";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import NewWorkout from "./pages/NewWorkout.jsx";
import Progress from "./pages/Progress.jsx";

function RequireAuth({ children }) {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  return children;
}

function Topbar() {
  const navigate = useNavigate();
  const loggedIn = isLoggedIn();

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <nav className="topbar">
      <div>
        <span className="brand">RepTrack</span>
      </div>
      <div>
        {loggedIn ? (
          <>
            <Link to="/">Dashboard</Link>
            <Link to="/new">Registrar entreno</Link>
            <Link to="/progress">Progreso</Link>
            <button className="btn secondary" onClick={logout}>Salir</button>
          </>
        ) : (
          <>
            <Link to="/login">Entrar</Link>
            <Link to="/register">Crear cuenta</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <>
      <Topbar />
      <div className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/new"
            element={
              <RequireAuth>
                <NewWorkout />
              </RequireAuth>
            }
          />
          <Route
            path="/progress"
            element={
              <RequireAuth>
                <Progress />
              </RequireAuth>
            }
          />
        </Routes>
      </div>
    </>
  );
}
