// ChatBot.jsx — Streaming AI chatbot with RAG + LangChain Agent + Bot Automation
import { useState, useEffect, useCallback, useRef } from "react";
import BotAutomation from "./BotAutomation";

const API = "http://localhost:8000";

const SUGGESTIONS = [
  "What's my balance?",
  "Show recent transactions",
  "Deposit 1000 for salary",
  "What are ATM fees?",
  "How do I transfer money?",
  "What is DICGC insurance?",
  "Daily transaction limits?",
  "How secure is NeoBank?",
];

// Render markdown-like bold text
function MsgContent({ text }) {
  const lines = text.split("\n");
  return (
    <div>
      {lines.map((line, i) => {
        const parts = line.split(/\*\*(.*?)\*\*/g);
        return (
          <div key={i} style={{ marginBottom: line === "" ? 4 : 1 }}>
            {parts.map((part, j) =>
              j % 2 === 1 ? <strong key={j}>{part}</strong> : part
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function ChatBot({ token, user, onRefreshAccount, onBotStart, onBotEnd, onShowTransactions }) {
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
                position:  data.position,
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

      {/* Floating button */}
      <button onClick={() => setOpen(o => !o)} style={{
        position: "fixed", bottom: 28, right: 28, zIndex: 500,
        width: 56, height: 56, borderRadius: "50%", border: "none",
        background: open ? "#0f2545" : "#0369a1",
        color: "#fff", fontSize: 22, cursor: "pointer",
        boxShadow: "0 4px 24px rgba(3,105,161,0.5)",
        display: "flex", alignItems: "center", justifyContent: "center",
        transition: "all .2s",
      }} title="NeoBank AI Assistant">
        {open ? "✕" : "🤖"}
        {!open && <div style={{ position:"absolute", top:2, right:2, width:12, height:12, borderRadius:"50%", background:"#22c55e", border:"2px solid #020912" }} />}
      </button>

      {/* Chat panel */}
      {open && (
        <div style={{
          position: "fixed", bottom: 100, right: 28, zIndex: 499,
          width: 380, height: 580, background: "#030c1b",
          border: "1px solid #0f2545", borderRadius: 16,
          display: "flex", flexDirection: "column",
          boxShadow: "0 8px 48px rgba(0,0,0,0.6)",
          animation: "chatUp .2s ease",
          fontFamily: "'Plus Jakarta Sans',sans-serif",
        }}>
          <style>{`@keyframes chatUp{from{transform:translateY(12px);opacity:0}to{transform:translateY(0);opacity:1}}
          @keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
          @keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-5px)}}
          `}</style>

          {/* Header */}
          <div style={{ padding:"13px 16px", borderBottom:"1px solid #0f2545", display:"flex", alignItems:"center", gap:10 }}>
            <div style={{ width:34, height:34, borderRadius:"50%", background:"#0369a1", display:"flex", alignItems:"center", justifyContent:"center", fontSize:16 }}>🤖</div>
            <div style={{ flex:1 }}>
              <div style={{ fontSize:13, fontWeight:700, color:"#e2e8f0" }}>NeoBank Assistant</div>
              <div style={{ fontSize:10, color:"#38bdf8", display:"flex", alignItems:"center", gap:5 }}>
                <span style={{ width:6, height:6, borderRadius:"50%", background:"#22c55e", display:"inline-block" }} />
                RAG + LangChain + Streaming
              </div>
            </div>
            <button onClick={clearChat} style={{ padding:"4px 9px", borderRadius:6, border:"1px solid #0f2545", background:"transparent", color:"#475569", fontSize:11, cursor:"pointer" }}>Clear</button>
          </div>

          {/* Messages */}
          <div style={{ flex:1, overflowY:"auto", padding:"12px 14px 8px" }}>
            {messages.map((m, i) => {
              const isBot = m.role === "assistant";
              return (
                <div key={i} style={{ display:"flex", justifyContent:isBot?"flex-start":"flex-end", marginBottom:10 }}>
                  {isBot && <div style={{ width:24, height:24, borderRadius:"50%", background:"#0369a1", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, flexShrink:0, marginRight:8, alignSelf:"flex-end" }}>🤖</div>}
                  <div style={{ maxWidth:"78%", display:"flex", flexDirection:"column", gap:4 }}>
                    <div style={{
                      padding:"9px 12px",
                      borderRadius: isBot ? "14px 14px 14px 2px" : "14px 14px 2px 14px",
                      background: isBot ? "#0a1628" : "#0369a1",
                      border: isBot ? "1px solid #0f2545" : "none",
                      fontSize:13, color:"#e2e8f0", lineHeight:1.6,
                    }}>
                      <MsgContent text={m.content || ""} />
                      {m.streaming && (
                        <span style={{ display:"inline-block", width:2, height:14, background:"#38bdf8", marginLeft:2, animation:"blink 1s infinite", verticalAlign:"middle" }} />
                      )}
                    </div>
                    {/* Tool badges */}
                    {isBot && m.tools && m.tools.length > 0 && (
                      <div style={{ display:"flex", gap:4, flexWrap:"wrap" }}>
                        {m.tools.map(t => (
                          <span key={t} style={{ fontSize:9, padding:"2px 7px", borderRadius:20, background:(toolColors[t]||"#38bdf8")+"22", color:toolColors[t]||"#38bdf8", border:`1px solid ${toolColors[t]||"#38bdf8"}44` }}>
                            {t.replace(/_/g," ")}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Typing dots */}
            {streaming && messages[messages.length-1]?.content === "" && (
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
                <div style={{ width:24, height:24, borderRadius:"50%", background:"#0369a1", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11 }}>🤖</div>
                <div style={{ padding:"10px 14px", borderRadius:"14px 14px 14px 2px", background:"#0a1628", border:"1px solid #0f2545" }}>
                  <div style={{ display:"flex", gap:5 }}>
                    {[0,1,2].map(d => <div key={d} style={{ width:6, height:6, borderRadius:"50%", background:"#38bdf8", animation:`bounce .9s ${d*.2}s infinite` }} />)}
                  </div>
                </div>
              </div>
            )}

            {/* Suggestions */}
            {messages.length <= 1 && (
              <div style={{ display:"flex", flexWrap:"wrap", gap:6, marginTop:6 }}>
                {SUGGESTIONS.map(s => (
                  <button key={s} onClick={() => setInput(s)} style={{ padding:"5px 10px", borderRadius:20, border:"1px solid #0f2545", background:"transparent", color:"#38bdf8", fontSize:11, cursor:"pointer", fontFamily:"'Plus Jakarta Sans',sans-serif" }}>{s}</button>
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div style={{ padding:"10px 12px", borderTop:"1px solid #0f2545" }}>
            {toolsUsed.length > 0 && (
              <div style={{ fontSize:10, color:"#334155", marginBottom:6 }}>
                Tools used: {toolsUsed.map(t => t.replace(/_/g," ")).join(", ")}
              </div>
            )}
            <div style={{ display:"flex", gap:8 }}>
              <input
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
                placeholder="Ask anything or say 'deposit 1000'…"
                style={{ flex:1, padding:"9px 12px", borderRadius:9, border:"1px solid #0f2545", background:"#050d1a", color:"#e2e8f0", fontSize:13, fontFamily:"'Plus Jakarta Sans',sans-serif", outline:"none" }}
              />
              <button onClick={send} disabled={!input.trim() || streaming} style={{ padding:"9px 14px", borderRadius:9, border:"none", background:!input.trim()||streaming?"#0f2545":"#0369a1", color:!input.trim()||streaming?"#334155":"#fff", fontSize:14, cursor:!input.trim()||streaming?"not-allowed":"pointer" }}>↑</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
