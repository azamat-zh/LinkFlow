import { Link, Route, Routes } from "react-router-dom";
import { useState, useEffect } from "react";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Onboarding from "./pages/Onboarding";

export default function App() {
  // Check localStorage first, then fall back to system preference
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("linkflow-theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    const root = document.documentElement; // <html> tag
    if (darkMode) {
      root.classList.add("dark");
      localStorage.setItem("linkflow-theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("linkflow-theme", "light");
    }
  }, [darkMode]);

  return (
    <>
      <nav>
        <span style={{ fontWeight: 700, fontSize: 20, color: "var(--primary)", letterSpacing: "-0.02em" }}>
          ✦ LinkFlow
        </span>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <Link to="/">Onboard</Link>
          <Link to="/match">Match</Link>
          <Link to="/dashboard">Dashboard</Link>
          
          {/* Dark Mode Toggle Button */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              background: "var(--bg-surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              cursor: "pointer",
              fontSize: 16,
              padding: "6px 10px",
              lineHeight: 1,
              marginLeft: 8,
              transition: "all 0.2s",
              display: "flex",
              alignItems: "center",
              boxShadow: "var(--shadow-sm)"
            }}
            aria-label="Toggle dark mode"
          >
            {darkMode ? "☀️" : "🌙"}
          </button>
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