// App.jsx — WITH ROUTING for /aboutus
// ─────────────────────────────────────────────────────────────────
// ADDED: Client-side routing so /aboutus renders AboutUs.jsx
// instead of the default Dashboard.
//
// HOW IT WORKS:
//   React does not have a built-in router. We implement a minimal
//   one using window.location.pathname + popstate event listener.
//
//   Routes:
//     /             → AuthPage or Dashboard (based on session)
//     /aboutus      → AboutUs page (public, no auth needed)
//
// AI CONCIERGE FLOW:
//   1. User types "tell me about neobank" in chatbot
//   2. chatbot.py detects intent → sends SSE event:
//        { type: "navigate_to", url: "/aboutus" }
//   3. ChatBot.jsx intercepts event → after 1.8s delay:
//        window.location.href = "http://localhost:3000/aboutus"
//   4. App.jsx sees pathname = "/aboutus" → renders <AboutUs />
//   5. User sees the full About Us page
//   6. "← Dashboard" button calls onBack() → history.back()
//
// ALSO: FastAPI /aboutus endpoint redirects browser to this URL
//   http://localhost:8000/aboutus → 302 → http://localhost:3000/aboutus
// ─────────────────────────────────────────────────────────────────

import { useState, useEffect } from "react";
import AuthPage  from "./components/AuthPage";
import Dashboard from "./components/Dashboard";
import AboutUs   from "./components/AboutUs";
const API = "http://localhost:8000";

// Simple path-based router hook
function useRoute() {
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    // Listen for back/forward browser navigation
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = (to) => {
    window.history.pushState({}, "", to);
    setPath(to);
  };

  return { path, navigate };
}

// Storage: sessionStorage clears on browser close
const storage = sessionStorage;

export default function App() {
  const { path, navigate }    = useRoute();
  const [token,    setToken]  = useState(null);
  const [user,     setUser]   = useState(null);
  const [checking, setChecking] = useState(true);

  // Validate stored session on mount
  useEffect(() => {
    const storedToken = storage.getItem("nb_token");
    const storedUser  = storage.getItem("nb_user");

    if (!storedToken || !storedUser) {
      setChecking(false);
      return;
    }

    fetch(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${storedToken}` },
    })
      .then(res => { if (!res.ok) throw new Error("expired"); return res.json(); })
      .then(userData => { setToken(storedToken); setUser(userData); })
      .catch(() => {
        storage.removeItem("nb_token");
        storage.removeItem("nb_user");
      })
      .finally(() => setChecking(false));
  }, []);

  const handleLogin = (t, u) => {
    storage.setItem("nb_token", t);
    storage.setItem("nb_user", JSON.stringify(u));
    setToken(t); setUser(u);
  };

  const handleLogout = () => {
    storage.removeItem("nb_token");
    storage.removeItem("nb_user");
    localStorage.removeItem("nb_token");
    localStorage.removeItem("nb_user");
    setToken(null); setUser(null);
  };

  // ── LOADING SPINNER ──────────────────────────────────────────
  if (checking) {
    return (
      <div style={{ minHeight:"100vh", background:"#020912", display:"flex", alignItems:"center", justifyContent:"center", flexDirection:"column", gap:16 }}>
        <div style={{ width:38, height:38, border:"3px solid #0f2545", borderTop:"3px solid #38bdf8", borderRadius:"50%", animation:"spin .8s linear infinite" }} />
        <div style={{ fontSize:13, color:"#334155", fontFamily:"'Plus Jakarta Sans',sans-serif" }}>Verifying session…</div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  // ── ROUTING ──────────────────────────────────────────────────
  // /aboutus — public page, no auth required
  if (path === "/aboutus") {
    return (
      <AboutUs
        token={token}
        user={user}
        onBack={() => {
          // Go back to previous page, or home if no history
          if (window.history.length > 1) {
            window.history.back();
          } else {
            navigate("/");
          }
        }}
      />
    );
  }

  // / — auth or dashboard
  if (!token || !user) return <AuthPage onLogin={handleLogin} />;
  return <Dashboard token={token} user={user} onLogout={handleLogout} />;
}
