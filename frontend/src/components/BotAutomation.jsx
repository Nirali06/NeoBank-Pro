// BotAutomation.jsx — FINAL FIX
// ─────────────────────────────────────────────────────────────────
// ROOT CAUSE OF DOUBLE EXECUTION (definitive):
//
// React StrictMode (development) intentionally mounts → unmounts →
// remounts every component to detect side effects. This caused:
//
//   Mount 1:  useEffect runs → runAutomation() starts → API call #1
//   Unmount:  cleanup runs  → activeRef.current = false (stops run #1
//             mid-way but the fetch() already went out)
//   Mount 2:  useEffect runs → runAutomation() starts → API call #2
//
// Additionally, ChatBot.jsx called setAutomationActions(data.actions)
// which created a NEW array reference each time, causing the
// useEffect([actions]) dependency to re-fire even when actions
// hadn't logically changed.
//
// FIXES APPLIED:
//
// 1. hasRunRef — a ref that is set to true the instant runAutomation()
//    is called. If it's already true, the function returns immediately.
//    This survives StrictMode's double-mount because refs persist
//    across the unmount/remount cycle unlike state.
//
// 2. The cleanup function no longer sets activeRef.current = false.
//    Instead activeRef is only set false AFTER the full sequence
//    completes. This prevents the unmount from cancelling a running
//    automation mid-way.
//
// 3. In ChatBot.jsx (see that file) — automationActions is now stored
//    as a ref + state pair so the actions array identity is stable.
// ─────────────────────────────────────────────────────────────────

import { useEffect, useRef, useState, useCallback } from "react";

const CURSOR_SIZE = 28;

export default function BotAutomation({ actions, token, onComplete, onProgress }) {
  const cursorPosRef = useRef({ x: -100, y: -100 });
  const [cursorPos, setCursorPos] = useState({ x: -100, y: -100 });
  const [isActive,  setIsActive]  = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [clickAnim, setClickAnim] = useState(false);

  // activeRef — controls the animation loop (cursor movement steps)
  const activeRef = useRef(false);

  // hasRunRef — THE KEY FIX:
  // Set to true the first time runAutomation() is entered.
  // Any subsequent call (from StrictMode remount) returns immediately.
  // Refs survive the StrictMode unmount/remount cycle, so this
  // prevents the double-execution completely.
  const hasRunRef = useRef(false);

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  const moveCursorTo = useCallback(async (targetX, targetY, durationMs = 600) => {
    const steps    = 30;
    const stepTime = durationMs / steps;
    const startX   = cursorPosRef.current.x === -100 ? window.innerWidth / 2 : cursorPosRef.current.x;
    const startY   = cursorPosRef.current.y === -100 ? window.innerHeight / 2 : cursorPosRef.current.y;
    for (let i = 0; i <= steps; i++) {
      if (!activeRef.current) return;
      const t     = i / steps;
      const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      const pos   = {
        x: startX + (targetX - startX) * eased,
        y: startY + (targetY - startY) * eased,
      };
      cursorPosRef.current = pos;
      setCursorPos({ ...pos });
      await sleep(stepTime);
    }
  }, []);

  const getCenter = (selector) => {
    const el = document.querySelector(selector);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  };

  // Tab navigation only — calls el.click() on tabs (safe, not on submit)
  const simulateClick = useCallback(async (selector) => {
    const pos = getCenter(selector);
    if (!pos) return false;
    await moveCursorTo(pos.x, pos.y, 500);
    setClickAnim(true);
    await sleep(180);
    setClickAnim(false);
    const el = document.querySelector(selector);
    if (el) el.click();
    await sleep(350);
    return true;
  }, [moveCursorTo]);

  // Visual-only cursor move over submit button — NO click, NO API call
  const moveCursorOverButton = useCallback(async (selector) => {
    const pos = getCenter(selector);
    if (!pos) return;
    await moveCursorTo(pos.x, pos.y, 380);
    // Block any accidental click from reaching React's onClick handler
    const el = document.querySelector(selector);
    const guard = (e) => { e.stopImmediatePropagation(); e.preventDefault(); };
    if (el) el.addEventListener("click", guard, { capture: true });
    setClickAnim(true);
    await sleep(200);
    setClickAnim(false);
    await sleep(150);
    if (el) el.removeEventListener("click", guard, { capture: true });
  }, [moveCursorTo]);

  // Type full value at once — prevents character corruption
  const typeIntoInput = useCallback(async (selector, value) => {
    const el = document.querySelector(selector);
    if (!el) return;
    const pos = getCenter(selector);
    if (pos) {
      await moveCursorTo(pos.x, pos.y, 350);
      setClickAnim(true);
      await sleep(120);
      setClickAnim(false);
    }
    el.focus();
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, "value"
    ).set;
    // Clear then set full value — ONE operation, no corruption
    nativeSetter.call(el, "");
    el.dispatchEvent(new Event("input", { bubbles: true }));
    await sleep(60);
    nativeSetter.call(el, String(value));
    el.dispatchEvent(new Event("input", { bubbles: true }));
    await sleep(280);
  }, [moveCursorTo]);

  // Direct API call — the ONLY place the banking API is called
  const executeAction = useCallback(async (action) => {
    const headers = {
      "Authorization": `Bearer ${token}`,
      "Content-Type":  "application/json",
    };
    let res;
    if (action.action === "deposit") {
      res = await fetch("http://localhost:8000/account/deposit", {
        method: "POST", headers,
        body: JSON.stringify({ amount: action.amount, note: action.note || "Bot deposit" }),
      });
    } else if (action.action === "withdraw") {
      res = await fetch("http://localhost:8000/account/withdraw", {
        method: "POST", headers,
        body: JSON.stringify({ amount: action.amount, note: action.note || "Bot withdrawal" }),
      });
    } else if (action.action === "transfer") {
      if (!action.to_email) {
        return { ok: false, data: { detail: "Recipient email is required for transfer" } };
      }
      res = await fetch("http://localhost:8000/account/transfer", {
        method: "POST", headers,
        body: JSON.stringify({
          to_email: action.to_email,
          amount:   action.amount,
          note:     action.note || "Bot transfer",
        }),
      });
    } else {
      return { ok: true, data: { message: "Done" } };
    }
    const data = await res.json();
    return { ok: res.ok, data };
  }, [token]);

  // Main automation sequence
  const runAutomation = useCallback(async () => {
    if (!actions || actions.length === 0) return;

    // KEY FIX: If already running (StrictMode remount), return immediately
    if (hasRunRef.current) return;
    hasRunRef.current = true;
    activeRef.current = true;
    setIsActive(true);

    for (let i = 0; i < actions.length; i++) {
      if (!activeRef.current) break;
      const action = actions[i];
      setStatusMsg(`Step ${i + 1}/${actions.length}: ${action.description}`);

      try {
        if (action.action === "navigate" || action.action === "show_balance") {
          setStatusMsg(`Opening ${action.tab || "home"} tab…`);
          await simulateClick(`[data-tab="${action.tab || "home"}"]`);
          await sleep(400);

        } else if (action.action === "deposit") {
          await simulateClick(`[data-tab="deposit"]`);
          await sleep(450);
          setStatusMsg(`Typing ₹${action.amount.toLocaleString("en-IN")}…`);
          await typeIntoInput("#bot-amount-input", action.amount);
          if (action.note) { setStatusMsg("Typing note…"); await typeIntoInput("#bot-note-input", action.note); }
          setStatusMsg("Confirming deposit…");
          await moveCursorOverButton("#bot-submit-btn");
          const { ok, data } = await executeAction(action);
          if (!ok) { setStatusMsg(`❌ ${data.detail || "Deposit failed"}`); onProgress && onProgress({ action, result: data, error: true }); }
          else      { onProgress && onProgress({ action, result: data }); }
          await sleep(900);

        } else if (action.action === "withdraw") {
          await simulateClick(`[data-tab="withdraw"]`);
          await sleep(450);
          setStatusMsg(`Typing ₹${action.amount.toLocaleString("en-IN")}…`);
          await typeIntoInput("#bot-amount-input", action.amount);
          if (action.note) { setStatusMsg("Typing note…"); await typeIntoInput("#bot-note-input", action.note); }
          setStatusMsg("Confirming withdrawal…");
          await moveCursorOverButton("#bot-submit-btn");
          const { ok, data } = await executeAction(action);
          if (!ok) { setStatusMsg(`❌ ${data.detail || "Withdrawal failed"}`); onProgress && onProgress({ action, result: data, error: true }); }
          else      { onProgress && onProgress({ action, result: data }); }
          await sleep(900);

        } else if (action.action === "transfer") {
          if (!action.to_email) {
            setStatusMsg("❌ No recipient email");
            onProgress && onProgress({ action, result: { detail: "Please specify a recipient email." }, error: true });
            await sleep(1200);
            continue;
          }
          await simulateClick(`[data-tab="transfer"]`);
          await sleep(450);
          setStatusMsg(`Typing recipient: ${action.to_email}…`);
          await typeIntoInput("#bot-email-input", action.to_email);
          setStatusMsg(`Typing ₹${action.amount.toLocaleString("en-IN")}…`);
          await typeIntoInput("#bot-amount-input", action.amount);
          if (action.note) { setStatusMsg("Typing note…"); await typeIntoInput("#bot-note-input", action.note); }
          setStatusMsg("Sending transfer…");
          await moveCursorOverButton("#bot-submit-btn");
          const { ok, data } = await executeAction(action);
          if (!ok) { setStatusMsg(`❌ ${data.detail || "Transfer failed"}`); onProgress && onProgress({ action, result: data, error: true }); }
          else      { onProgress && onProgress({ action, result: data }); }
          await sleep(900);
        }
      } catch (err) {
        setStatusMsg(`❌ Error: ${err.message}`);
        onProgress && onProgress({ action, result: { detail: err.message }, error: true });
        await sleep(1200);
      }
    }

    setStatusMsg("✅ All done!");
    await sleep(1600);
    // Only reset refs AFTER full sequence — not in cleanup
    activeRef.current        = false;
    cursorPosRef.current     = { x: -100, y: -100 };
    setIsActive(false);
    setCursorPos({ x: -100, y: -100 });
    onComplete && onComplete();
  }, [actions, simulateClick, moveCursorOverButton, typeIntoInput, executeAction, onProgress, onComplete]);

  useEffect(() => {
    if (actions && actions.length > 0) {
      runAutomation();
    }
    // KEY FIX: cleanup does NOT reset activeRef or hasRunRef.
    // If we reset activeRef here, StrictMode's unmount would cancel
    // the running automation, then remount would start it again = double call.
    return () => {};
  }, [actions, runAutomation]);

  if (!isActive) return null;

  return (
    <>
      <div style={{
        position: "fixed", top: 16, left: "50%", transform: "translateX(-50%)",
        zIndex: 9998, background: "#0a1628", border: "1px solid #38bdf8",
        borderRadius: 10, padding: "10px 22px", fontSize: 13,
        color: "#7dd3fc", fontFamily: "'Plus Jakarta Sans',sans-serif",
        boxShadow: "0 4px 20px rgba(56,189,248,0.2)",
        display: "flex", alignItems: "center", gap: 10,
        maxWidth: "85vw", overflow: "hidden",
      }}>
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#38bdf8", flexShrink: 0, animation: "nbpulse 1s infinite" }} />
        🤖 {statusMsg}
      </div>

      <div style={{
        position: "fixed",
        left: cursorPos.x - CURSOR_SIZE / 2,
        top:  cursorPos.y - CURSOR_SIZE / 2,
        width: CURSOR_SIZE, height: CURSOR_SIZE,
        pointerEvents: "none", zIndex: 9997,
      }}>
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 4L11.5 19L13.5 13L19.5 11L4 4Z" fill="#38bdf8" stroke="#fff" strokeWidth="1.5" strokeLinejoin="round" />
        </svg>
        {clickAnim && (
          <div style={{
            position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -50%)",
            width: 40, height: 40, borderRadius: "50%",
            border: "2px solid #38bdf8",
            animation: "nbripple .4s ease-out forwards",
          }} />
        )}
      </div>

      <style>{`
        @keyframes nbpulse  { 0%,100%{opacity:1} 50%{opacity:.4} }
        @keyframes nbripple { from{transform:translate(-50%,-50%) scale(.5);opacity:1} to{transform:translate(-50%,-50%) scale(2);opacity:0} }
      `}</style>
    </>
  );
}
