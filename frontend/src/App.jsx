import { Link, Route, Routes } from "react-router-dom";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Onboarding from "./pages/Onboarding";

export default function App() {
  return (
    <>
      <nav>
        <span style={{ fontWeight: 700, fontSize: 18, color: "var(--primary)" }}>LinkFlow</span>
        <div style={{ display: "flex", gap: 24 }}>
          <Link to="/">Onboard</Link>
          <Link to="/match">Match</Link>
          <Link to="/dashboard">Dashboard</Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Onboarding />} />
        <Route path="/match" element={<Chat />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </>
  );
}
