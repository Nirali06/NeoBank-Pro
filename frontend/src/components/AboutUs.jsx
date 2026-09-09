// AboutUs.jsx
// ─────────────────────────────────────────────────────────────────
// Full About Us page for NeoBank Pro.
// Route: http://localhost:3000/aboutus
//
// AI Concierge Integration:
//   When user types "about neobank", "who are you", "tell me about
//   neobank" etc. in the chatbot, chatbot.py detects the intent and
//   sends SSE event: { type: "navigate_to", url: "/aboutus" }
//   ChatBot.jsx intercepts → window.location.href = /aboutus
//   App.jsx routing → renders this component.
//
// Also accessible directly:
//   http://localhost:8000/aboutus → FastAPI 302 redirect → /aboutus
// ─────────────────────────────────────────────────────────────────


import ChatBot from "./ChatBot";
import { useState, useEffect, useCallback, useRef } from "react";
//import Dashboard from "./Dashboard";
import BotAutomation from "./BotAutomation"; 

const API = "http://localhost:8000";





// ── ANIMATED STAT COUNTER ─────────────────────────────────────
function AnimatedStat({ end, suffix = "", prefix = "", duration = 2000 }) {
  const ref        = useRef(null);
  const startedRef = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !startedRef.current) {
        startedRef.current = true;
        const startTime = performance.now();
        const animate = (now) => {
          const elapsed  = now - startTime;
          const progress = Math.min(elapsed / duration, 1);
          const eased    = 1 - Math.pow(1 - progress, 3);
          const current  = Math.floor(eased * end);
          el.textContent = prefix + current.toLocaleString("en-IN") + suffix;
          if (progress < 1) requestAnimationFrame(animate);
          else el.textContent = prefix + end.toLocaleString("en-IN") + suffix;
        };
        requestAnimationFrame(animate);
      }
    }, { threshold: 0.3 });
    observer.observe(el);
    return () => observer.disconnect();
  }, [end, suffix, prefix, duration]);

  return (
    <span ref={ref} style={{ fontFamily: "'Syne', sans-serif" }}>
      {prefix}0{suffix}
    </span>
  );
}

// ── TEAM CARD ─────────────────────────────────────────────────
function TeamCard({ name, role, emoji, bio }) {
  return (
    <div
      style={{ background: "#0a1628", border: "1px solid #0f2545", borderRadius: 14, padding: "24px 22px", display: "flex", flexDirection: "column", gap: 12, transition: "transform .2s, border-color .2s", cursor: "default" }}
      onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-4px)"; e.currentTarget.style.borderColor = "#38bdf8"; }}
      onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.borderColor = "#0f2545"; }}
    >
      <div style={{ fontSize: 40 }}>{emoji}</div>
      <div>
        <div style={{ fontSize: 16, fontWeight: 700, fontFamily: "'Syne', sans-serif", color: "#e2e8f0" }}>{name}</div>
        <div style={{ fontSize: 12, color: "#38bdf8", marginTop: 2 }}>{role}</div>
      </div>
      <div style={{ fontSize: 13, color: "#475569", lineHeight: 1.6 }}>{bio}</div>
    </div>
  );
}

// ── VALUE CARD ────────────────────────────────────────────────
function ValueCard({ icon, title, desc }) {
  return (
    <div style={{ background: "#030c1b", border: "1px solid #0f2545", borderRadius: 12, padding: "22px 20px", flex: "1 1 200px" }}>
      <div style={{ fontSize: 28, marginBottom: 12 }}>{icon}</div>
      <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", fontFamily: "'Syne', sans-serif", marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 12, color: "#475569", lineHeight: 1.6 }}>{desc}</div>
    </div>
  );
}

// ── TIMELINE ITEM ─────────────────────────────────────────────
function TimelineItem({ year, title, desc, isLast }) {
  return (
    <div style={{ display: "flex", gap: 20 }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ width: 14, height: 14, borderRadius: "50%", background: "#38bdf8", border: "3px solid #0a1628", flexShrink: 0, marginTop: 4 }} />
        {!isLast && <div style={{ width: 2, flex: 1, background: "#0f2545", marginTop: 6 }} />}
      </div>
      <div style={{ paddingBottom: isLast ? 0 : 28 }}>
        <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 1, marginBottom: 4 }}>{year}</div>
        <div style={{ fontSize: 15, fontWeight: 600, fontFamily: "'Syne', sans-serif", color: "#e2e8f0", marginBottom: 4 }}>{title}</div>
        <div style={{ fontSize: 13, color: "#475569", lineHeight: 1.6 }}>{desc}</div>
      </div>
    </div>
  );
}

// ── MAIN ABOUT US PAGE ────────────────────────────────────────
export default function AboutUs({ onBack, token, user }) {
  const F = "'Plus Jakarta Sans', sans-serif";
  const S = "'Syne', sans-serif";

  const [open,      setOpen]      = useState(false);
  const [messages,  setMessages]  = useState([]);
  const [input,     setInput]     = useState("");
  const [streaming, setStreaming] = useState(false);
  const [toolsUsed, setToolsUsed] = useState([]);
  const [automationActions, setAutomationActions] = useState(null);
  // Ref holds same value as state — used to prevent StrictMode
  // double-mount from re-triggering the useEffect in BotAutomation.
  // We reset this ref when automation completes so next command works.
  const automationActionsRef = useRef(null);
  // botKey: incremented each time a new automation command arrives.
  // Passed as key prop to BotAutomation — forces a full remount
  // (resetting hasRunRef) for each new command while preventing
  // StrictMode's artificial remount from running it twice.
  const [botKey, setBotKey] = useState(0);
  const bottomRef   = useRef(null);
  const esRef       = useRef(null);
  const inputRef    = useRef(null);

  const api = useCallback(async (path, opts = {}) => {
    const res = await fetch(API + path, {
      ...opts,
      headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json", ...opts.headers },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    return data;
  }, [token]);

  // Load chat history on open
  useEffect(() => {
    if (!open || messages.length > 0) return;
    api("/chat/history").then(hist => {
      if (hist.length === 0) {
        setMessages([{
          role: "assistant",
          content: `Hi ${user.full_name.split(" ")[0]}! 👋 I'm your NeoBank AI assistant powered by **LangChain Agent** and **RAG**.\n\nI can:\n• Answer questions about bank policies, fees, limits\n• Check your balance and transactions\n• **Automate UI** — say "deposit 1000 and withdraw 500"\n\nWhat can I help you with?`,
          tools: []
        }]);
      } else {
        setMessages(hist.map(m => ({ ...m, tools: [] })));
      }
    }).catch(() => {});
  }, [open, api, user, messages.length]);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming]);

  const send = async () => {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    setToolsUsed([]);

    setMessages(p => [...p, { role: "user", content: text, tools: [] }]);
    setStreaming(true);

    // Add streaming placeholder for assistant
    setMessages(p => [...p, { role: "assistant", content: "", tools: [], streaming: true }]);

    try {
      // Use EventSource-compatible fetch for SSE
      const response = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Chat error");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const dataStr = line.slice(5).trim();
          try {
            const data = JSON.parse(dataStr);

            if (data.type === "delta") {
              // Append streaming text to last message
              setMessages(p => {
                const msgs = [...p];
                const last = msgs[msgs.length - 1];
                if (last.role === "assistant") {
                  msgs[msgs.length - 1] = { ...last, content: last.content + data.text };
                }
                return msgs;
              });
            } else if (data.type === "meta") {
              setToolsUsed(data.tools_used || []);
              setMessages(p => {
                const msgs = [...p];
                msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], streaming: false, tools: data.tools_used || [] };
                return msgs;
              });
            } else if (data.type === "show_transactions") {
              // Navigate to history tab and highlight matching transactions
              onShowTransactions && onShowTransactions({
                limit:     data.limit,
                filter:    data.filter,
                highlight: data.highlight,
              });
              setMessages(p => {
                const msgs = [...p];
                msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], streaming: false };
                return msgs;
              });
            } else if (data.type === "navigate_to") {
              // AI Concierge navigation — redirect to About Us or any page.
              // The backend sends this when user asks "about neobank",
              // "who are you", "tell me about neobank" etc.
              // We wait 1.8s so the streaming reply text finishes rendering
              // before the navigation happens — better UX.
              setMessages(p => {
                const msgs = [...p];
                msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], streaming: false };
                return msgs;
              });
              const targetUrl = data.url || "/aboutus";
              const delay     = 1800;
              setTimeout(() => {
                if (data.target === "_blank") {
                  // Open in new tab
                  window.open(`http://localhost:3000${targetUrl}`, "_blank");
                } else {
                  // Navigate in same tab
                  window.location.href = `http://localhost:3000${targetUrl}`;
                }
              }, delay);
            } else if (data.type === "automation") {
              // Trigger UI automation
              setMessages(p => {
                const msgs = [...p];
                msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], streaming: false };
                return msgs;
              });
              onBotStart && onBotStart();
              // Store in ref for stable reference, update state to trigger render
              automationActionsRef.current = data.actions;
              setBotKey(k => k + 1);   // new key = new BotAutomation instance = hasRunRef resets
              setAutomationActions(data.actions);
            } else if (data.type === "done") {
              setMessages(p => {
                const msgs = [...p];
                msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], streaming: false };
                return msgs;
              });
            }
          } catch {}
        }
      }
    } catch (err) {
      setMessages(p => {
        const msgs = [...p];
        msgs[msgs.length - 1] = { role: "assistant", content: `Sorry, error: ${err.message}`, tools: [], streaming: false };
        return msgs;
      });
    } finally {
      setStreaming(false);
    }
  };

  const clearChat = async () => {
    await api("/chat/history", { method: "DELETE" });
    setMessages([{ role: "assistant", content: `Chat cleared! How can I help you, ${user.full_name.split(" ")[0]}?`, tools: [] }]);
  };

  const toolColors = {
    get_balance:       "#34d399",
    get_transactions:  "#60a5fa",
    get_spending_stats:"#f59e0b",
    rag_search:        "#a78bfa",
    get_account_info:  "#38bdf8",
  };
  
  return (
    <>
      {/* Bot automation overlay */}
      {automationActions && (
        <BotAutomation
          key={botKey}
          actions={automationActions}
          token={token}
          onComplete={() => {
              setAutomationActions(null);
              onBotEnd && onBotEnd();
              onRefreshAccount && onRefreshAccount();
            }}
          onProgress={({ action, result, error }) => {
            if (error) {
              setMessages(p => [...p, {
                role: "assistant",
                content: "❌ **" + action.description + " failed**\n" + (result.detail || result.message || "Unknown error"),
                tools: []
              }]);
            } else {
              const bal = result.new_balance ? "\nNew balance: ₹" + result.new_balance.toLocaleString("en-IN") : "";
              setMessages(p => [...p, {
                role: "assistant",
                content: "✅ **" + action.description + "**\n" + (result.message || "Done") + bal,
                tools: []
              }]);
            }
          }}
        />
      )}



      {/*useEffect(() => { refresh(); }, [refresh]);
      useEffect(() => { window.scrollTo({ top: 0, behavior: "smooth" }); }, [refresh]);*/}

      return (
        <div style={{ minHeight: "100vh", background: "#020912", color: "#e2e8f0", fontFamily: F }}>
          <style>{`
            @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
            * { box-sizing: border-box; margin: 0; padding: 0; }
            @keyframes fadeUp { from{transform:translateY(24px);opacity:0} to{transform:translateY(0);opacity:1} }
            @keyframes pulse  { 0%,100%{opacity:1} 50%{opacity:.4} }
            ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-thumb{background:#0f2545;border-radius:4px;}
            a.nb-nav:hover { color: #38bdf8 !important; }
          `}</style>

          {/* ── HEADER ── */}
          <div style={{ borderBottom: "1px solid #0a1a30", background: "#030c1b", padding: "14px 32px", display: "flex", alignItems: "center", gap: 20, position: "sticky", top: 0, zIndex: 100 }}>
            <span style={{ fontFamily: S, fontSize: 19, fontWeight: 800, color: "#38bdf8" }}>⬡ NeoBank Pro</span>
            <div style={{ flex: 1 }} />
            <nav style={{ display: "flex", gap: 24 }}>
              {[["#about","About"],["#mission","Mission"],["#team","Team"],["#timeline","Story"],["#contact","Contact"]].map(([href, label]) => (
                <a key={href} href={href} className="nb-nav" style={{ fontSize: 13, color: "#475569", textDecoration: "none", transition: "color .15s" }}>{label}</a>
              ))}
            </nav>
            {onBack && (
              <button onClick={onBack} style={{ padding: "7px 16px", borderRadius: 8, border: "1px solid #0f2545", background: "transparent", color: "#475569", fontSize: 12, cursor: "pointer", fontFamily: F }}>
                ← Dashboard
              </button>
            )}
          </div>

          {/* ── HERO ── */}
          <section id="about" style={{ padding: "80px 32px 60px", maxWidth: 900, margin: "0 auto", textAlign: "center", animation: "fadeUp .5s ease" }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "#0a1628", border: "1px solid #1e40af", borderRadius: 20, padding: "5px 16px", marginBottom: 24 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#38bdf8", display: "inline-block", animation: "pulse 1.5s infinite" }} />
              <span style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 1, textTransform: "uppercase" }}>RBI Licensed · DICGC Insured · Est. 2020</span>
            </div>
            <h1 style={{ fontFamily: S, fontSize: 52, fontWeight: 800, letterSpacing: -2, marginBottom: 20, lineHeight: 1.1 }}>
              Banking built for<br /><span style={{ color: "#38bdf8" }}>the digital age</span>
            </h1>
            <p style={{ fontSize: 17, color: "#475569", lineHeight: 1.8, maxWidth: 640, margin: "0 auto 40px" }}>
              NeoBank Pro is India's most advanced digital banking platform — combining full-featured banking
              operations with a first-of-its-kind AI concierge that understands you, remembers your
              preferences, and acts on your behalf.
            </p>
            <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
              <a href="#mission" style={{ padding: "12px 28px", borderRadius: 9, background: "#0369a1", color: "#fff", fontSize: 14, fontWeight: 700, textDecoration: "none" }}>Our Mission →</a>
              <a href="#contact" style={{ padding: "12px 28px", borderRadius: 9, border: "1px solid #0f2545", background: "transparent", color: "#38bdf8", fontSize: 14, fontWeight: 600, textDecoration: "none" }}>Contact Us</a>
            </div>
          </section>

          {/* ── STATS ── */}
          <section style={{ background: "#030c1b", borderTop: "1px solid #0a1a30", borderBottom: "1px solid #0a1a30", padding: "48px 32px" }}>
            <div style={{ maxWidth: 900, margin: "0 auto", display: "flex", flexWrap: "wrap" }}>
              {[
                { label: "Customers",          end: 2000000, suffix: "+" },
                { label: "Daily Transactions", end: 500000,  suffix: "+" },
                { label: "Cities Served",      end: 500,     suffix: "+" },
                { label: "Uptime SLA",         end: 99,      suffix: ".9%" },
              ].map(({ label, end, suffix }, i) => (
                <div key={label} style={{ flex: "1 1 200px", textAlign: "center", padding: "24px 16px", borderRight: i < 3 ? "1px solid #0f2545" : "none" }}>
                  <div style={{ fontSize: 40, fontWeight: 800, color: "#38bdf8", marginBottom: 6 }}>
                    <AnimatedStat end={end} suffix={suffix} />
                  </div>
                  <div style={{ fontSize: 12, color: "#475569", textTransform: "uppercase", letterSpacing: 1 }}>{label}</div>
                </div>
              ))}
            </div>
          </section>

          {/* ── MISSION ── */}
          <section id="mission" style={{ padding: "72px 32px", maxWidth: 900, margin: "0 auto" }}>
            <div style={{ textAlign: "center", marginBottom: 48 }}>
              <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>Our Purpose</div>
              <h2 style={{ fontFamily: S, fontSize: 36, fontWeight: 800, letterSpacing: -1, marginBottom: 16 }}>Mission & Vision</h2>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20, marginBottom: 56 }}>
              <div style={{ background: "#030c1b", border: "1px solid #1e40af", borderRadius: 14, padding: "28px 24px" }}>
                <div style={{ fontSize: 28, marginBottom: 16 }}>🎯</div>
                <div style={{ fontFamily: S, fontSize: 18, fontWeight: 700, color: "#e2e8f0", marginBottom: 12 }}>Our Mission</div>
                <p style={{ fontSize: 14, color: "#475569", lineHeight: 1.8 }}>
                  To make banking accessible, transparent, and intelligent for every Indian — eliminating
                  hidden fees, confusing terms, and unnecessary branch visits through the power of AI.
                </p>
              </div>
              <div style={{ background: "#030c1b", border: "1px solid #0f2545", borderRadius: 14, padding: "28px 24px" }}>
                <div style={{ fontSize: 28, marginBottom: 16 }}>🔭</div>
                <div style={{ fontFamily: S, fontSize: 18, fontWeight: 700, color: "#e2e8f0", marginBottom: 12 }}>Our Vision</div>
                <p style={{ fontSize: 14, color: "#475569", lineHeight: 1.8 }}>
                  A future where your bank knows you deeply, anticipates your needs, and takes action on
                  your behalf — so banking fades into the background and you focus on what matters most.
                </p>
              </div>
            </div>
            <div style={{ textAlign: "center", marginBottom: 32 }}>
              <h3 style={{ fontFamily: S, fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Core Values</h3>
            </div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
              <ValueCard icon="🔍" title="Transparency"   desc="No hidden fees. No fine print. Every charge explained clearly before you commit." />
              <ValueCard icon="🔐" title="Security First"  desc="Bank-grade AES-256 encryption, 2FA, and AI fraud detection on every transaction." />
              <ValueCard icon="⚡" title="Always Instant"  desc="Every transfer, every deposit, every inquiry — resolved in seconds, not days." />
              <ValueCard icon="🤝" title="Customer First"  desc="Every feature and design decision made with the customer at the centre." />
              <ValueCard icon="🤖" title="AI-Powered"      desc="The most advanced AI concierge in Indian banking — remembers you and acts for you." />
            </div>
          </section>

          {/* ── PRODUCTS ── */}
          <section style={{ background: "#030c1b", borderTop: "1px solid #0a1a30", borderBottom: "1px solid #0a1a30", padding: "72px 32px" }}>
            <div style={{ maxWidth: 900, margin: "0 auto" }}>
              <div style={{ textAlign: "center", marginBottom: 48 }}>
                <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>Platform</div>
                <h2 style={{ fontFamily: S, fontSize: 36, fontWeight: 800, letterSpacing: -1 }}>What NeoBank Pro Offers</h2>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20 }}>
                {[
                  ["💰","Savings Account",     "4.5% p.a. interest, zero balance option, instant account opening with video KYC."],
                  ["🏦","Checking Account",    "Unlimited transactions, overdraft facility, multi-user access for businesses."],
                  ["💎","Premium Account",     "Dedicated RM, lounge access, zero forex markup, 5× reward points."],
                  ["🔄","Instant Transfers",   "NEFT, IMPS, RTGS, UPI — all free, all instant, available 24×7×365."],
                  ["🤖","AI Concierge",        "RAG-powered chatbot that knows your preferences and automates banking tasks."],
                  ["📊","Smart Analytics",     "Spending insights, category-wise breakdowns, and personalized financial tips."],
                  ["🛡️","Fraud Protection",   "ML-powered real-time fraud detection with zero-liability policy."],
                  ["🌍","International",       "SWIFT transfers, multi-currency support, zero forex markup for premium users."],
                ].map(([icon, title, desc]) => (
                  <div key={title} style={{ background: "#020912", border: "1px solid #0f2545", borderRadius: 12, padding: "22px 20px" }}>
                    <div style={{ fontSize: 28, marginBottom: 10 }}>{icon}</div>
                    <div style={{ fontFamily: S, fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 6 }}>{title}</div>
                    <div style={{ fontSize: 12, color: "#475569", lineHeight: 1.6 }}>{desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* ── TEAM ── */}
          <section id="team" style={{ padding: "72px 32px", maxWidth: 900, margin: "0 auto" }}>
            <div style={{ textAlign: "center", marginBottom: 48 }}>
              <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>People</div>
              <h2 style={{ fontFamily: S, fontSize: 36, fontWeight: 800, letterSpacing: -1, marginBottom: 12 }}>Leadership Team</h2>
              <p style={{ fontSize: 14, color: "#475569" }}>The people building the future of banking</p>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20 }}>
              <TeamCard emoji="👩‍💼" name="Priya Sharma"  role="CEO & Co-Founder"     bio="Ex-Goldman Sachs. 15 years in fintech. Built India's first real-time payments infrastructure at NPCI." />
              <TeamCard emoji="👨‍💻" name="Arjun Mehta"   role="CTO & Co-Founder"     bio="Former Google Brain engineer. Pioneered conversational AI for financial services. IIT Bombay alumnus." />
              <TeamCard emoji="👩‍🔬" name="Kavita Nair"   role="Chief AI Officer"     bio="PhD in NLP from Stanford. Designed the RAG concierge system and LangChain agent framework." />
              <TeamCard emoji="👨‍⚖️" name="Rahul Desai"   role="Chief Risk Officer"   bio="20 years in banking regulation. Ex-RBI senior officer. Ensures full compliance and customer protection." />
              <TeamCard emoji="👩‍🎨" name="Meera Iyer"    role="Chief Design Officer" bio="Ex-Apple Design. Created NeoBank's intuitive interface that makes complex banking feel effortless." />
              <TeamCard emoji="👨‍💼" name="Sanjay Gupta"  role="Chief Banking Officer" bio="Led digital transformation at HDFC Bank. Expert in Indian banking regulations and product strategy." />
            </div>
          </section>

          {/* ── TIMELINE ── */}
          <section id="timeline" style={{ background: "#030c1b", borderTop: "1px solid #0a1a30", borderBottom: "1px solid #0a1a30", padding: "72px 32px" }}>
            <div style={{ maxWidth: 600, margin: "0 auto" }}>
              <div style={{ textAlign: "center", marginBottom: 48 }}>
                <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>Journey</div>
                <h2 style={{ fontFamily: S, fontSize: 36, fontWeight: 800, letterSpacing: -1 }}>Our Story</h2>
              </div>
              {[
                { year: "2020", title: "Founded in Mumbai",        desc: "NeoBank incorporated with ₹50 crore seed funding. Received RBI in-principle approval for payments bank license.", isLast: false },
                { year: "2021", title: "First 100,000 Customers",  desc: "Launched savings and checking accounts. India's fastest digital bank to reach 1 lakh customers in 8 months.", isLast: false },
                { year: "2022", title: "Full Banking License",      desc: "Received full commercial banking license from RBI. Launched Premium accounts and international wire transfers.", isLast: false },
                { year: "2022", title: "Best Digital Bank Award",   desc: "Won Banking Technology Award for Best Digital Bank India. Crossed ₹1,000 crore in deposits.", isLast: false },
                { year: "2023", title: "AI Concierge Launch",       desc: "Launched India's first RAG-powered banking AI concierge with streaming UX and UI automation capabilities.", isLast: false },
                { year: "2024", title: "2 Million Customers",       desc: "Crossed 2 million active customers. Expanded to 500 cities. Launched LangChain agent v2 with persistent memory.", isLast: false },
                { year: "2025", title: "NeoBank Pro",               desc: "Launched NeoBank Pro — the most advanced AI banking platform in India with full concierge automation.", isLast: true },
              ].map(item => <TimelineItem key={item.title} {...item} />)}
            </div>
          </section>

          {/* ── AWARDS ── */}
          <section style={{ padding: "72px 32px", maxWidth: 900, margin: "0 auto" }}>
            <div style={{ textAlign: "center", marginBottom: 48 }}>
              <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>Recognition</div>
              <h2 style={{ fontFamily: S, fontSize: 36, fontWeight: 800, letterSpacing: -1 }}>Awards & Certifications</h2>
            </div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "center" }}>
              {[
                ["🏆","Best Digital Bank India",   "Banking Technology Awards 2022, 2023"],
                ["🥇","Fastest Growing Fintech",   "Economic Times Awards 2023"],
                ["🔐","PCI-DSS Level 1",           "Highest payment security certification"],
                ["🏛️","RBI RegTech Award",         "Innovation in regulatory technology 2023"],
                ["⭐","DICGC Member",              "Deposits insured up to ₹5,00,000"],
                ["✅","ISO 27001 Certified",        "Information security management"],
              ].map(([icon, title, sub]) => (
                <div key={title} style={{ background: "#030c1b", border: "1px solid #0f2545", borderRadius: 12, padding: "20px 24px", textAlign: "center", flex: "1 1 160px" }}>
                  <div style={{ fontSize: 32, marginBottom: 8 }}>{icon}</div>
                  <div style={{ fontFamily: S, fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 4 }}>{title}</div>
                  <div style={{ fontSize: 11, color: "#475569" }}>{sub}</div>
                </div>
              ))}
            </div>
          </section>

          {/* ── CONTACT ── */}
          <section id="contact" style={{ background: "#030c1b", borderTop: "1px solid #0a1a30", padding: "72px 32px" }}>
            <div style={{ maxWidth: 900, margin: "0 auto" }}>
              <div style={{ textAlign: "center", marginBottom: 48 }}>
                <div style={{ fontSize: 11, color: "#38bdf8", letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>Get in Touch</div>
                <h2 style={{ fontFamily: S, fontSize: 36, fontWeight: 800, letterSpacing: -1, marginBottom: 12 }}>Contact NeoBank Pro</h2>
                <p style={{ fontSize: 14, color: "#475569" }}>We're here 24×7. Pick the channel that works best for you.</p>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 20 }}>
                {[
                  ["📞","Customer Care",   "1800-NEOBANK",         "1800-636-2265 · 24×7 Free"],
                  ["💎","Premium Support", "1800-NEO-PREM",         "30-second answer guarantee"],
                  ["📧","Email Support",   "support@neobank.com",   "Response within 24 hours"],
                  ["🚨","Fraud Hotline",   "fraud@neobank.com",     "Response within 4 hours"],
                  ["💬","Live Chat",       "In-app 24×7",           "Average response: 2 minutes"],
                  ["📍","Headquarters",    "NeoBank Tower, Mumbai", "BKC, Bandra East, 400051"],
                ].map(([icon, title, info, sub]) => (
                  <div key={title} style={{ background: "#020912", border: "1px solid #0f2545", borderRadius: 12, padding: "22px 20px" }}>
                    <div style={{ fontSize: 26, marginBottom: 10 }}>{icon}</div>
                    <div style={{ fontFamily: S, fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 4 }}>{title}</div>
                    <div style={{ fontSize: 13, color: "#38bdf8", marginBottom: 4 }}>{info}</div>
                    <div style={{ fontSize: 11, color: "#475569" }}>{sub}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>
          

          {/* ── FOOTER ── */}
          <footer style={{ borderTop: "1px solid #0a1a30", padding: "32px", textAlign: "center" }}>
            <div style={{ fontFamily: S, fontSize: 18, fontWeight: 800, color: "#38bdf8", marginBottom: 8 }}>⬡ NeoBank Pro</div>
            <div style={{ fontSize: 12, color: "#1e3a5f", marginBottom: 4 }}>Regulated by Reserve Bank of India · DICGC Insured · PCI-DSS Level 1</div>
            <div style={{ fontSize: 11, color: "#0f2545" }}>© 2020–2025 NeoBank Technologies Pvt. Ltd. All rights reserved.</div>
          </footer>
          <ChatBot
            token={token}
            
          />
        </div>
      
    </>
  );
}