// Dashboard.jsx — Banking dashboard with bot-automation compatible input IDs
import { useState, useEffect, useCallback, useRef } from "react";
import ChatBot from "./ChatBot";

const API = "http://localhost:8000";
const fmt = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(n);
const fmtDate = (ts) => new Date(ts).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });

function Toast({ msg, type, onClose }) {
  useEffect(() => { const t = setTimeout(onClose, 3500); return () => clearTimeout(t); }, [onClose]);
  const ok = type === "success";
  return <div style={{ position:"fixed", top:18, right:18, zIndex:9999, background:ok?"#052e16":"#450a0a", border:`1px solid ${ok?"#166534":"#991b1b"}`, color:ok?"#86efac":"#fca5a5", padding:"11px 18px", borderRadius:10, fontSize:13, fontFamily:"'Plus Jakarta Sans',sans-serif", maxWidth:320, animation:"toastIn .2s ease", lineHeight:1.5 }}>{msg}</div>;
}

export default function Dashboard({ token, user, onLogout }) {
  const [account,  setAccount]  = useState(null);
  const [txns,     setTxns]     = useState([]);
  const [tab,      setTab]      = useState("home");
  const [amount,   setAmount]   = useState("");
  const [note,     setNote]     = useState("");
  const [toEmail,  setToEmail]  = useState("");
  const [loading,  setLoading]  = useState(false);
  const [fetching, setFetching] = useState(true);
  const [toast,    setToast]    = useState(null);
  // botMode: true while BotAutomation is running.
  // Disables all submit button onClick handlers so the bot's
  // executeAction() is the ONLY code path that calls the API.
  const [botMode,   setBotMode]  = useState(false);
  // highlightedTxns: controls which rows to highlight when chatbot navigates to history
  const [highlightedTxns, setHighlightedTxns] = useState(null);
  // { limit, filter, highlight } — null means no highlight active
  const transactionRefs = useRef(new Map());

  const notify = (msg, type = "success") => setToast({ msg, type });

  const api = useCallback(async (path, opts = {}) => {
    const res = await fetch(API + path, { ...opts, headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json", ...opts.headers } });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    return data;
  }, [token]);

  const refresh = useCallback(async () => {
    try {
      const [acc, t] = await Promise.all([api("/account"), api("/account/transactions")]);
      setAccount(acc); setTxns(Array.isArray(t) ? t : []);
    } catch (e) {
      if (e.message.includes("Session")) onLogout();
      else notify(e.message, "error");
    } finally { setFetching(false); }
  }, [api, onLogout]);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    if (tab !== "history" || !highlightedTxns?.highlight || highlightedTxns.position !== "last") return;

    const filteredRows = txns.filter(row => (
      highlightedTxns.filter === "all" || row.type === highlightedTxns.filter
    ));
    const oldestRow = filteredRows[filteredRows.length - 1];
    if (!oldestRow) return;

    requestAnimationFrame(() => {
      transactionRefs.current.get(oldestRow.id)?.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    });
  }, [tab, txns, highlightedTxns]);

  const doAction = async (path, body) => {
    setLoading(true);
    try {
      const data = await api(path, { method: "POST", body: JSON.stringify(body) });
      notify(data.message);
      setAmount(""); setNote(""); setToEmail("");
      refresh();
    } catch (e) { notify(e.message, "error"); }
    finally { setLoading(false); }
  };

  const handleSignOut = async () => { try { await api("/auth/logout", { method: "POST" }); } catch {} onLogout(); };

  const S = {
    inp: { width:"100%", padding:"10px 14px", borderRadius:9, border:"1.5px solid #0f2545", background:"#050d1a", color:"#e2e8f0", fontSize:14, fontFamily:"'Plus Jakarta Sans',sans-serif", outline:"none", boxSizing:"border-box" },
    lbl: { display:"block", fontSize:11, color:"#64748b", marginBottom:5, letterSpacing:.6, textTransform:"uppercase", fontFamily:"'Plus Jakarta Sans',sans-serif" },
    btn: (bg, dis) => ({ width:"100%", padding:"12px", borderRadius:9, border:"none", background:dis?"#0f2545":bg, color:dis?"#334155":"#fff", fontSize:14, fontWeight:700, cursor:dis?"not-allowed":"pointer", fontFamily:"'Plus Jakarta Sans',sans-serif" }),
  };

  const TABS = [["home","🏠 Home"],["deposit","💰 Deposit"],["withdraw","💸 Withdraw"],["transfer","🔄 Transfer"],["history","📋 History"]];
  const TXN = { deposit:{color:"#34d399",bg:"#05291a",icon:"↓"}, withdraw:{color:"#f87171",bg:"#290505",icon:"↑"}, transfer:{color:"#60a5fa",bg:"#05152a",icon:"⇄"} };
  const totalIn  = txns.filter(t=>t.type==="deposit").reduce((s,t)=>s+t.amount,0);
  const totalOut = txns.filter(t=>t.type!=="deposit").reduce((s,t)=>s+t.amount,0);

  if (fetching) return <div style={{ minHeight:"100vh", background:"#020912", display:"flex", alignItems:"center", justifyContent:"center" }}><div style={{ color:"#1e3a5f", fontFamily:"'Plus Jakarta Sans',sans-serif", fontSize:14 }}>Loading…</div></div>;

  return (
    <div style={{ minHeight:"100vh", background:"#020912", color:"#e2e8f0", fontFamily:"'Plus Jakarta Sans',sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
        *{box-sizing:border-box;} input::placeholder{color:#1e3a5f;}
        @keyframes toastIn{from{transform:translateX(18px);opacity:0}to{transform:translateX(0);opacity:1}}
        @keyframes fadeUp{from{transform:translateY(12px);opacity:0}to{transform:translateY(0);opacity:1}} @keyframes nbpulse2{0%,100%{opacity:1}50%{opacity:.3}}
        .nb-txn:hover{background:#050d1a;} .nb-tab:hover{color:#94a3b8!important;}
        input:focus{border-color:#1e40af!important;}
        ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-thumb{background:#0f2545;border-radius:4px;}
      `}</style>

      {toast && <Toast msg={toast.msg} type={toast.type} onClose={() => setToast(null)} />}

      {/* Chatbot */}
      <ChatBot
          token={token}
          user={user}
          onRefreshAccount={refresh}
          onBotStart={() => setBotMode(true)}
          onBotEnd={() => { setBotMode(false); setAmount(""); setNote(""); setToEmail(""); }}
          onShowTransactions={({ limit, filter, position, highlight }) => {
            // Navigate to history tab
            setTab("history");
            // Set highlight config — Dashboard uses this to style matching rows
            setHighlightedTxns({ limit, filter, position, highlight });
            // Auto-clear highlight after 6 seconds
            setTimeout(() => setHighlightedTxns(null), 6000);
          }}
        />

      {/* Header */}
      <div style={{ borderBottom:"1px solid #0a1a30", background:"#030c1b", padding:"14px 28px", display:"flex", alignItems:"center", gap:16, position:"sticky", top:0, zIndex:100 }}>
        <span style={{ fontFamily:"'Syne',sans-serif", fontSize:19, fontWeight:800, color:"#38bdf8" }}>⬡ NeoBank Pro</span>
        <div style={{ flex:1 }} />
        <div style={{ fontSize:13, color:"#334155" }}>
          Signed in as <span style={{ color:"#7dd3fc", fontWeight:600 }}>{user.full_name}</span>
          {account && <span style={{ marginLeft:8, fontSize:11, color:"#1e3a5f" }}>({(account.acc_type||"savings").toUpperCase()})</span>}
        </div>
        <button onClick={handleSignOut} style={{ padding:"7px 16px", borderRadius:8, border:"1px solid #0f2545", background:"transparent", color:"#475569", fontSize:12, cursor:"pointer" }}>Sign Out</button>
      </div>

      <div style={{ maxWidth:820, margin:"0 auto", padding:"28px 20px" }}>

        {/* Balance hero */}
        {account && (
          <div style={{ background:"#030c1b", border:"1px solid #0a1a30", borderRadius:18, padding:"28px 28px 22px", marginBottom:20, animation:"fadeUp .3s ease" }}>
            <div style={{ fontSize:11, color:"#1e3a5f", letterSpacing:1, textTransform:"uppercase", marginBottom:8 }}>Available Balance</div>
            <div style={{ fontSize:44, fontWeight:800, fontFamily:"'Syne',sans-serif", color:"#fff", letterSpacing:-1, marginBottom:4 }}>{fmt(account.balance)}</div>
            <div style={{ fontSize:12, color:"#1e3a5f", marginBottom:24 }}>{account.email} · Account #{account.id}</div>
            <div style={{ display:"flex", gap:10, flexWrap:"wrap" }}>
              {[["Total Credited",fmt(totalIn),"#34d399","#052e16"],["Total Debited",fmt(totalOut),"#f87171","#450a0a"],["Transactions",`${txns.length}`,"#60a5fa","#0c1a35"]].map(([l,v,c,bg]) => (
                <div key={l} style={{ background:bg, border:`1px solid ${c}22`, borderRadius:10, padding:"10px 16px", flex:"1 1 130px" }}>
                  <div style={{ fontSize:10, color:c, opacity:.7, textTransform:"uppercase", letterSpacing:.5, marginBottom:4 }}>{l}</div>
                  <div style={{ fontSize:17, fontWeight:700, color:c, fontFamily:"'Syne',sans-serif" }}>{v}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab bar — data-tab attributes enable bot navigation */}
        <div style={{ display:"flex", background:"#030c1b", border:"1px solid #0a1a30", borderRadius:12, padding:4, marginBottom:22, overflowX:"auto", gap:2 }}>
          {TABS.map(([id,label]) => (
            <button key={id} data-tab={id} className="nb-tab" onClick={() => setTab(id)} style={{ flex:"1 0 auto", padding:"9px 14px", borderRadius:8, border:"none", background:tab===id?"#0a1a30":"transparent", color:tab===id?"#38bdf8":"#334155", fontSize:12, fontWeight:600, cursor:"pointer", fontFamily:"'Plus Jakarta Sans',sans-serif", whiteSpace:"nowrap", transition:"all .12s" }}>{label}</button>
          ))}
        </div>

        {/* HOME */}
        {tab === "home" && (
          <div style={{ animation:"fadeUp .25s ease" }}>
            <div style={{ fontSize:12, color:"#1e3a5f", marginBottom:12, textTransform:"uppercase", letterSpacing:.5 }}>Recent Activity</div>
            {txns.length === 0
              ? <div style={{ background:"#030c1b", border:"1px solid #0a1a30", borderRadius:12, padding:40, textAlign:"center", color:"#1e3a5f", fontSize:14 }}>No transactions yet. Try asking the bot to deposit!</div>
              : txns.slice(0,8).map(t => {
                const m = TXN[t.type]||TXN.deposit;
                return (
                  <div key={t.id} className="nb-txn" style={{ display:"flex", alignItems:"center", gap:14, padding:"11px 8px", borderBottom:"1px solid #030c1b", borderRadius:6, transition:"background .1s" }}>
                    <div style={{ width:38, height:38, borderRadius:"50%", background:m.bg, color:m.color, border:`1px solid ${m.color}33`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:15, flexShrink:0 }}>{m.icon}</div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontSize:13, color:"#cbd5e1", fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{t.note||t.type}</div>
                      <div style={{ fontSize:11, color:"#1e3a5f", marginTop:2 }}>{fmtDate(t.timestamp)}</div>
                    </div>
                    <div style={{ fontSize:14, fontWeight:700, color:m.color, fontFamily:"'Syne',sans-serif", flexShrink:0 }}>{t.type==="deposit"?"+":"−"}{fmt(t.amount)}</div>
                  </div>
                );
              })
            }
            {txns.length > 8 && <button onClick={() => setTab("history")} style={{ width:"100%", marginTop:10, padding:"10px", borderRadius:8, border:"1px solid #0a1a30", background:"transparent", color:"#334155", fontSize:12, cursor:"pointer" }}>View all {txns.length} →</button>}
          </div>
        )}

        {/* DEPOSIT — inputs have bot-automation IDs */}
        {tab === "deposit" && (
          <div style={{ maxWidth:380, animation:"fadeUp .25s ease" }}>
            <div style={{ fontSize:18, fontWeight:700, fontFamily:"'Syne',sans-serif", marginBottom:4 }}>Deposit Funds</div>
            <div style={{ fontSize:12, color:"#334155", marginBottom:22 }}>Add money to your account</div>
            <div style={{ marginBottom:14 }}>
              <label style={S.lbl}>Amount (₹)</label>
              <input id="bot-amount-input" style={S.inp} type="number" min="1" placeholder="Enter amount" value={amount} onChange={e => setAmount(e.target.value)} />
            </div>
            <div style={{ marginBottom:22 }}>
              <label style={S.lbl}>Note (optional)</label>
              <input id="bot-note-input" style={S.inp} type="text" placeholder="e.g. Salary…" value={note} onChange={e => setNote(e.target.value)} />
            </div>
            <button id="bot-submit-btn" data-bot-controlled="true" style={S.btn("#059669", loading||!amount||botMode)} disabled={loading||!amount||botMode} onClick={() => { if (botMode) return; doAction("/account/deposit", { amount: parseFloat(amount), note }); }}>
              {loading ? "Processing…" : "💰 Deposit Money"}
            </button>
          </div>
        )}

        {/* WITHDRAW */}
        {tab === "withdraw" && (
          <div style={{ maxWidth:380, animation:"fadeUp .25s ease" }}>
            <div style={{ fontSize:18, fontWeight:700, fontFamily:"'Syne',sans-serif", marginBottom:4 }}>Withdraw Funds</div>
            {account && <div style={{ fontSize:12, color:"#1e3a5f", marginBottom:22 }}>Available: <span style={{ color:"#7dd3fc", fontWeight:600 }}>{fmt(account.balance)}</span></div>}
            <div style={{ marginBottom:14 }}>
              <label style={S.lbl}>Amount (₹)</label>
              <input id="bot-amount-input" style={S.inp} type="number" min="1" placeholder="Enter amount" value={amount} onChange={e => setAmount(e.target.value)} />
            </div>
            <div style={{ marginBottom:22 }}>
              <label style={S.lbl}>Note (optional)</label>
              <input id="bot-note-input" style={S.inp} type="text" placeholder="e.g. ATM…" value={note} onChange={e => setNote(e.target.value)} />
            </div>
            <button id="bot-submit-btn" data-bot-controlled="true" style={S.btn("#dc2626", loading||!amount||botMode)} disabled={loading||!amount||botMode} onClick={() => { if (botMode) return; doAction("/account/withdraw", { amount: parseFloat(amount), note }); }}>
              {loading ? "Processing…" : "💸 Withdraw Money"}
            </button>
          </div>
        )}

        {/* TRANSFER */}
        {tab === "transfer" && (
          <div style={{ maxWidth:380, animation:"fadeUp .25s ease" }}>
            <div style={{ fontSize:18, fontWeight:700, fontFamily:"'Syne',sans-serif", marginBottom:4 }}>Transfer Funds</div>
            <div style={{ fontSize:12, color:"#334155", marginBottom:22 }}>Send to another NeoBank user</div>
            <div style={{ marginBottom:14 }}>
              <label style={S.lbl}>Recipient Email</label>
              <input id="bot-email-input" style={S.inp} type="email" placeholder="recipient@example.com" value={toEmail} onChange={e => setToEmail(e.target.value)} />
            </div>
            <div style={{ marginBottom:14 }}>
              <label style={S.lbl}>Amount (₹)</label>
              <input id="bot-amount-input" style={S.inp} type="number" min="1" placeholder="Enter amount" value={amount} onChange={e => setAmount(e.target.value)} />
            </div>
            <div style={{ marginBottom:22 }}>
              <label style={S.lbl}>Note (optional)</label>
              <input id="bot-note-input" style={S.inp} type="text" placeholder="e.g. Rent…" value={note} onChange={e => setNote(e.target.value)} />
            </div>
            <button id="bot-submit-btn" data-bot-controlled="true" style={S.btn("#1d4ed8", loading||!amount||!toEmail||botMode)} disabled={loading||!amount||!toEmail||botMode} onClick={() => { if (botMode) return; doAction("/account/transfer", { to_email: toEmail, amount: parseFloat(amount), note }); }}>
              {loading ? "Processing…" : "🔄 Send Money"}
            </button>
          </div>
        )}

        {/* HISTORY */}
        {tab === "history" && (
          <div style={{ animation:"fadeUp .25s ease" }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:12 }}>
              <div style={{ fontSize:12, color:"#1e3a5f", textTransform:"uppercase", letterSpacing:.5 }}>All Transactions ({txns.length})</div>
              {highlightedTxns && (
                <div style={{ fontSize:11, color:"#38bdf8", background:"#0a1f3d", border:"1px solid #1e40af", borderRadius:20, padding:"3px 10px", display:"flex", alignItems:"center", gap:6 }}>
                  <span style={{ width:6, height:6, borderRadius:"50%", background:"#38bdf8", display:"inline-block", animation:"nbpulse2 1s infinite" }} />
                  Bot highlighted {highlightedTxns.limit} rows
                  <button onClick={() => setHighlightedTxns(null)} style={{ marginLeft:4, background:"transparent", border:"none", color:"#475569", cursor:"pointer", fontSize:11, padding:0 }}>✕</button>
                </div>
              )}
            </div>
            {txns.length === 0
              ? <div style={{ background:"#030c1b", border:"1px solid #0a1a30", borderRadius:12, padding:40, textAlign:"center", color:"#1e3a5f", fontSize:14 }}>No transactions yet.</div>
              : txns.map((t, rowIndex) => {
                const m = TXN[t.type]||TXN.deposit;
                return (() => {
                    // Determine if this row should be highlighted by chatbot request
                    let isHighlighted = false;
                    if (highlightedTxns && highlightedTxns.highlight) {
                      const { limit, filter, position = "first" } = highlightedTxns;
                      const filteredRows = txns.filter(row => filter === "all" || row.type === filter);
                      const filteredIndex = filteredRows.indexOf(t);
                      const matchesFilter = filteredIndex !== -1;
                      const start = position === "last"
                        ? Math.max(filteredRows.length - limit, 0)
                        : 0;
                      isHighlighted = matchesFilter
                        && filteredIndex >= start
                        && filteredIndex < start + limit;
                    }
                    return (
                      <div
                        key={t.id}
                        ref={node => {
                          if (node) transactionRefs.current.set(t.id, node);
                          else transactionRefs.current.delete(t.id);
                        }}
                        className="nb-txn"
                        style={{
                        display:"flex", alignItems:"center", gap:14,
                        padding:"11px 8px", borderBottom:"1px solid #030c1b",
                        borderRadius:6, transition:"background .3s",
                        background: isHighlighted ? "#0a1f3d" : "transparent",
                        outline: isHighlighted ? "1.5px solid #38bdf8" : "none",
                        outlineOffset: isHighlighted ? "-1px" : "0",
                      }}>
                        <div style={{ width:38, height:38, borderRadius:"50%", background:m.bg, color:m.color, border:`1px solid ${m.color}33`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:15, flexShrink:0 }}>{m.icon}</div>
                        <div style={{ flex:1, minWidth:0 }}>
                          <div style={{ fontSize:13, color:"#cbd5e1", fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{t.note||t.type}</div>
                          <div style={{ fontSize:11, color:"#1e3a5f", marginTop:2 }}>{fmtDate(t.timestamp)}</div>
                        </div>
                        <div style={{ textAlign:"right", flexShrink:0 }}>
                          <div style={{ fontSize:14, fontWeight:700, color:m.color, fontFamily:"'Syne',sans-serif" }}>{t.type==="deposit"?"+":"−"}{fmt(t.amount)}</div>
                          <div style={{ fontSize:10, color:"#1e3a5f", marginTop:2, textTransform:"capitalize" }}>{t.type}</div>
                          {isHighlighted && <div style={{ fontSize:9, color:"#38bdf8", marginTop:2 }}>● highlighted</div>}
                        </div>
                      </div>
                    );
                  })();
              })
            }
          </div>
        )}
      </div>
    </div>
  );
}
