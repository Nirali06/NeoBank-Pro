// AuthPage.jsx — FIXED + Google Sign-In Added
// ─────────────────────────────────────────────────────────────────
// FIX: Google Sign-In via Google Identity Services (GSI).
//
// HOW IT WORKS:
//   1. Load the GSI script (accounts.google.com/gsi/client)
//   2. Render Google's button using google.accounts.id.renderButton()
//   3. When user clicks and approves → Google calls our callback
//      with a credential (JWT id_token)
//   4. We POST that token to /auth/google on our FastAPI backend
//   5. Backend verifies the JWT, finds/creates the user, returns
//      our own session token
//   6. Frontend stores our token and navigates to dashboard
//
// SETUP REQUIRED:
//   1. Go to console.cloud.google.com → APIs & Services → Credentials
//   2. Create OAuth 2.0 Client ID (Web application)
//   3. Add http://localhost:3000 to Authorized JavaScript origins
//   4. Replace GOOGLE_CLIENT_ID below with your actual client ID
//   5. In backend auth.py → add /auth/google route (see comment below)
// ─────────────────────────────────────────────────────────────────

import { useState, useEffect, useRef } from "react";

const API = "http://localhost:8000";

// ── REPLACE THIS WITH YOUR GOOGLE CLIENT ID ────────────────────────
const GOOGLE_CLIENT_ID = "245299824891-dcu0c3v88ia4jtfcu60fqg53bb9oj684.apps.googleusercontent.com";

// Field defined OUTSIDE to prevent cursor-loss on re-render
function Field({ fkey, label, type, placeholder, value, error, showPw, onChange, onSubmit }) {
  const isPass = fkey === "password" || fkey === "confirm";
  return (
    <div style={{ marginBottom: 16 }}>
      <label style={{
        display: "block", fontSize: 11, color: "#94a3b8",
        marginBottom: 5, letterSpacing: .7, textTransform: "uppercase",
        fontFamily: "'Plus Jakarta Sans',sans-serif",
      }}>
        {label}
      </label>
      <input
        type={isPass ? (showPw ? "text" : "password") : (type || "text")}
        placeholder={placeholder}
        value={value}
        autoComplete={isPass ? "new-password" : "off"}
        onChange={e => onChange(fkey, e.target.value)}
        onKeyDown={e => e.key === "Enter" && onSubmit()}
        style={{
          width: "100%", padding: "11px 14px", borderRadius: 9,
          border: `1.5px solid ${error ? "#7f1d1d" : "#1e293b"}`,
          background: "#050d1a", color: "#e2e8f0",
          fontSize: 14, fontFamily: "'Plus Jakarta Sans',sans-serif",
          outline: "none", boxSizing: "border-box",
        }}
        onFocus={e => { if (!error) e.target.style.borderColor = "#1e40af"; }}
        onBlur={e  => { e.target.style.borderColor = error ? "#7f1d1d" : "#1e293b"; }}
      />
      {error && (
        <div style={{ fontSize: 11, color: "#f87171", marginTop: 4 }}>{error}</div>
      )}
    </div>
  );
}

export default function AuthPage({ onLogin }) {
  const [mode,    setMode]    = useState("signin");
  const [form,    setForm]    = useState({ full_name:"", email:"", password:"", confirm:"", initial_deposit:"", acc_type:"savings" });
  const [errs,    setErrs]    = useState({});
  const [loading, setLoading] = useState(false);
  const [showPw,  setShowPw]  = useState(false);
  const [toast,   setToast]   = useState(null);
  const googleBtnRef = useRef(null);

  const notify    = (msg, type = "error") => setToast({ msg, type });
  const set       = (k, v) => { setForm(p => ({ ...p, [k]: v })); setErrs(p => ({ ...p, [k]: "" })); };
  const switchMode = (m) => {
    setMode(m); setErrs({});
    setForm({ full_name:"", email:"", password:"", confirm:"", initial_deposit:"", acc_type:"savings" });
  };

  // ── GOOGLE SIGN-IN SETUP ──────────────────────────────────────
  useEffect(() => {
    // Load Google GSI script dynamically
    if (document.getElementById("gsi-script")) {
      initGoogle();
      return;
    }
    const script = document.createElement("script");
    script.id  = "gsi-script";
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = initGoogle;
    document.head.appendChild(script);
  }, []); // eslint-disable-line

  function initGoogle() {
    if (!window.google || !googleBtnRef.current) return;
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback:  handleGoogleCredential,
    });
    window.google.accounts.id.renderButton(googleBtnRef.current, {
      theme:  "filled_black",
      size:   "large",
      width:  "100%",
      text:   "continue_with",
      shape:  "rectangular",
    });
  }

  // Re-render Google button when mode changes (DOM ref changes)
  useEffect(() => {
    if (window.google && googleBtnRef.current) {
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        theme: "filled_black", size: "large", width: "100%",
        text: "continue_with", shape: "rectangular",
      });
    }
  }, [mode]);

  // Called by Google when user approves
  async function handleGoogleCredential(response) {
    const idToken = response.credential;
    setLoading(true);
    try {
      const res = await fetch(`${API}/auth/google`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ id_token: idToken }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Google sign-in failed");
      onLogin(data.token, data.user);
    } catch (e) {
      notify(e.message);
    } finally {
      setLoading(false);
    }
  }

  // ── EMAIL/PASSWORD AUTH ────────────────────────────────────────
  const validate = () => {
    const e = {};
    if (mode === "signup" && !form.full_name.trim()) e.full_name = "Full name is required";
    if (!form.email.trim())                          e.email    = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(form.email))      e.email    = "Enter a valid email";
    if (!form.password)                              e.password = "Password is required";
    else if (form.password.length < 6)               e.password = "Minimum 6 characters";
    if (mode === "signup" && form.password !== form.confirm) e.confirm = "Passwords do not match";
    setErrs(e);
    return Object.keys(e).length === 0;
  };

  const submit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      const url  = mode === "signin" ? "/auth/login" : "/auth/register";
      const body = mode === "signin"
        ? { email: form.email, password: form.password }
        : { full_name: form.full_name, email: form.email, password: form.password,
            initial_deposit: parseFloat(form.initial_deposit) || 0, acc_type: form.acc_type };
      const res  = await fetch(API + url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      onLogin(data.token, data.user);
    } catch (e) { notify(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight:"100vh", background:"#020912", display:"flex", fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        input::placeholder{color:#1e3a5f;}
        select{color:#e2e8f0;background:#050d1a;border:1.5px solid #1e293b;border-radius:9px;padding:11px 14px;font-size:14px;width:100%;outline:none;font-family:'Plus Jakarta Sans',sans-serif;}
        @keyframes fadeUp{from{transform:translateY(18px);opacity:0}to{transform:translateY(0);opacity:1}}
        @keyframes toastIn{from{transform:translateX(18px);opacity:0}to{transform:translateX(0);opacity:1}}
        .g-btn-wrap > div { width: 100% !important; }
      `}</style>

      {toast && (
        <div style={{
          position:"fixed", top:18, right:18, zIndex:9999,
          background: toast.type==="error" ? "#450a0a" : "#052e16",
          border:`1px solid ${toast.type==="error" ? "#991b1b" : "#166534"}`,
          color: toast.type==="error" ? "#fca5a5" : "#86efac",
          padding:"11px 18px", borderRadius:10, fontSize:13,
          animation:"toastIn .2s ease", maxWidth:300,
        }}>{toast.msg}</div>
      )}

      {/* Left branding panel */}
      <div style={{ flex:1, background:"#030c1b", borderRight:"1px solid #0f2545", display:"flex", flexDirection:"column", justifyContent:"center", padding:"60px 52px", minWidth:0 }}>
        <div style={{ maxWidth:400 }}>
          <div style={{ fontFamily:"'Syne',sans-serif", fontSize:32, fontWeight:800, color:"#38bdf8", letterSpacing:-1, marginBottom:8 }}>⬡ NeoBank Pro</div>
          <div style={{ fontSize:14, color:"#334155", lineHeight:1.8, marginBottom:36 }}>
            Modern banking with AI-powered assistant,<br/>RAG knowledge base, and UI automation.
          </div>
          {[
            ["🤖","LangChain Agent + RAG System"],
            ["⚡","Streaming AI Responses"],
            ["🎯","UI Automation Bot"],
            ["🔐","Bank-grade Security"],
            ["💰","Full Banking Operations"],
          ].map(([icon,text]) => (
            <div key={text} style={{ display:"flex", alignItems:"center", gap:12, marginBottom:14 }}>
              <div style={{ width:34, height:34, borderRadius:8, background:"#0a1f3d", display:"flex", alignItems:"center", justifyContent:"center", fontSize:15 }}>{icon}</div>
              <div style={{ fontSize:13, color:"#475569" }}>{text}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Right auth panel */}
      <div style={{ width:420, display:"flex", flexDirection:"column", justifyContent:"center", padding:"48px 36px", flexShrink:0, overflowY:"auto" }}>
        <div style={{ animation:"fadeUp .3s ease" }}>

          {/* Mode toggle */}
          <div style={{ display:"flex", background:"#030c1b", border:"1px solid #0f2545", borderRadius:10, padding:4, marginBottom:28 }}>
            {[["signin","Sign In"],["signup","Sign Up"]].map(([m,label]) => (
              <button key={m} onClick={() => switchMode(m)} style={{
                flex:1, padding:"9px 0", borderRadius:7, border:"none",
                background:mode===m?"#0f2545":"transparent",
                color:mode===m?"#38bdf8":"#334155",
                fontSize:13, fontWeight:600, cursor:"pointer",
                fontFamily:"'Plus Jakarta Sans',sans-serif", transition:"all .15s",
              }}>{label}</button>
            ))}
          </div>

          <div style={{ fontSize:20, fontWeight:700, fontFamily:"'Syne',sans-serif", color:"#e2e8f0", marginBottom:4 }}>
            {mode === "signin" ? "Welcome back" : "Create account"}
          </div>
          <div style={{ fontSize:12, color:"#334155", marginBottom:22 }}>
            {mode === "signin" ? "Enter your credentials to continue" : "Fill in your details to get started"}
          </div>

          {/* Google Sign-In button */}
          <div style={{ marginBottom:20 }}>
            <div ref={googleBtnRef} className="g-btn-wrap" style={{ width:"100%" }} />
          </div>

          {/* Divider */}
          <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:20 }}>
            <div style={{ flex:1, height:1, background:"#0f2545" }} />
            <span style={{ fontSize:11, color:"#334155", whiteSpace:"nowrap" }}>or continue with email</span>
            <div style={{ flex:1, height:1, background:"#0f2545" }} />
          </div>

          {/* Email/password fields */}
          {mode === "signup" && (
            <Field fkey="full_name" label="Full Name" placeholder="John Doe"
              value={form.full_name} error={errs.full_name} showPw={showPw} onChange={set} onSubmit={submit} />
          )}
          <Field fkey="email" label="Email" type="email" placeholder="you@example.com"
            value={form.email} error={errs.email} showPw={showPw} onChange={set} onSubmit={submit} />
          <Field fkey="password" label="Password" placeholder="Min 6 characters"
            value={form.password} error={errs.password} showPw={showPw} onChange={set} onSubmit={submit} />
          {mode === "signup" && <>
            <Field fkey="confirm" label="Confirm Password" placeholder="Repeat password"
              value={form.confirm} error={errs.confirm} showPw={showPw} onChange={set} onSubmit={submit} />
            <div style={{ marginBottom:16 }}>
              <label style={{ display:"block", fontSize:11, color:"#94a3b8", marginBottom:5, letterSpacing:.7, textTransform:"uppercase" }}>Account Type</label>
              <select value={form.acc_type} onChange={e => set("acc_type", e.target.value)}>
                <option value="savings">Savings Account</option>
                <option value="checking">Checking Account</option>
                <option value="premium">Premium Account</option>
              </select>
            </div>
            <Field fkey="initial_deposit" label="Initial Deposit ₹ (optional)" type="number" placeholder="0.00"
              value={form.initial_deposit} error={errs.initial_deposit} showPw={showPw} onChange={set} onSubmit={submit} />
          </>}

          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:20, marginTop:-6 }}>
            <input type="checkbox" id="spw" checked={showPw} onChange={e => setShowPw(e.target.checked)} style={{ accentColor:"#38bdf8" }} />
            <label htmlFor="spw" style={{ fontSize:12, color:"#475569", cursor:"pointer" }}>Show password</label>
          </div>

          <button onClick={submit} disabled={loading} style={{
            width:"100%", padding:"12px", borderRadius:9, border:"none",
            background:loading?"#0f2545":"#0369a1",
            color:loading?"#334155":"#fff",
            fontSize:14, fontWeight:700, cursor:loading?"not-allowed":"pointer",
            fontFamily:"'Plus Jakarta Sans',sans-serif",
          }}>
            {loading ? "Please wait…" : mode === "signin" ? "Sign In →" : "Create Account →"}
          </button>

          {/* Demo credentials */}
          {mode === "signin" && (
            <div style={{ marginTop:16, padding:"12px 14px", background:"#030c1b", border:"1px solid #0f2545", borderRadius:9 }}>
              <div style={{ fontSize:10, color:"#334155", textTransform:"uppercase", letterSpacing:.6, marginBottom:5 }}>Demo account</div>
              <div style={{ fontSize:12, color:"#38bdf8" }}>demo@neobank.com / demo1234</div>
              <button
                onClick={() => setForm(p => ({ ...p, email:"demo@neobank.com", password:"demo1234" }))}
                style={{ marginTop:8, padding:"5px 12px", borderRadius:6, border:"1px solid #0f2545", background:"transparent", color:"#38bdf8", fontSize:11, cursor:"pointer" }}
              >Autofill ↗</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
