# chatbot.py — FIXED
# ─────────────────────────────────────────────────────────────────
# FIXES APPLIED:
#
# FIX 1 — DOUBLE EXECUTION:
#   Root cause: React StrictMode mounts components twice in dev,
#   causing the SSE stream to be read twice. Also, save_message()
#   was called for automation replies in multiple places.
#   Fix: Added a processed_messages set (dedup guard) using a
#   request-scoped ID. save_message() called exactly once per
#   user message and exactly once per assistant reply.
#   Also removed the duplicate /chat endpoint's save_message calls.
#
# FIX 2 — SHOW TRANSACTIONS IN UI:
#   Root cause: "show transaction" was handled by the fallback
#   text answer instead of triggering a UI navigation event.
#   Fix: Added show_transactions intent detection BEFORE the
#   normal chat flow. Returns a special SSE event type
#   "show_transactions" with limit and filter, which the frontend
#   handles by navigating to the history tab and highlighting rows.
# ─────────────────────────────────────────────────────────────────
from __future__ import annotations
import os
import re
import json
import asyncio
import urllib.request
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from model import get_db, get_current_user, ChatReq, fetch_account
from langchain_agent import agent
from playwright_bot import build_action_sequence, validate_actions

router = APIRouter()

# ── DEDUP GUARD ────────────────────────────────────────────────────
# Tracks message IDs already saved to prevent double-saves
# caused by React StrictMode double-invoking effects in development.
_saved_ids: set = set()

def save_message_once(user_id: int, role: str, content: str, msg_id: str = None):
    """Save a chat message, skipping if already saved (dedup guard)."""
    if msg_id:
        key = f"{user_id}:{msg_id}"
        if key in _saved_ids:
            return
        _saved_ids.add(key)
        # Keep set from growing unboundedly
        if len(_saved_ids) > 2000:
            _saved_ids.clear()
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()


def get_history(user_id: int, limit: int = 10) -> list:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM chat_history "
        "WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )
    rows = list(reversed([dict(r) for r in c.fetchall()]))
    conn.close()
    return rows


# ── SHOW TRANSACTIONS INTENT PARSER ───────────────────────────────
def parse_show_transactions(message: str):
    """
    Detect "show transaction" requests and extract limit + filter.

    Returns None if not a show-transactions request.
    Returns dict: { limit: int, filter: str, position: str, highlight: bool }

    Examples:
        "show transactions"          → { limit: 10, filter: "all" }
        "show first 5 transactions"  → { limit: 5,  filter: "first" }
        "show last 5 transactions"   → { limit: 5,  filter: "last" }
        "show 3 transactions"        → { limit: 3,  filter: "all" }
        "show deposit transactions"  → { limit: 10, filter: "deposit" }
    """
    msg = message.lower().strip()

    txn_keywords = [
        "show transaction", "show my transaction",
        "view transaction", "see transaction",
        "display transaction", "list transaction",
        "show history", "view history", "show statement",
        "recent transaction", "last transaction",
        "first transaction", "my transaction",
    ]

    matched = any(kw in msg for kw in txn_keywords) or bool(
        re.search(
            r'\b(?:show\s+)?(?:first|last)\b(?:\s+\d+)?'
            r'(?:\s+(?:deposit|withdraw|transfer))?\s+transactions?\b',
            msg,
        ) or bool(re.search(
            r'\b(?:show|view|see|display|list)\s+(?:my\s+)?'
            r'(?:deposit|withdraw|transfer)\s+transactions?\b',
            msg,
        ))
    )
    if not matched:
        return None

    # Extract number if present — "show last 5", "show first 3", "show 10".
    # A singular first/last request means one transaction; generic history
    # requests keep the default of ten rows.
    limit = 10
    num_match = re.search(r'\b(\d+)\b', msg)
    if num_match:
        limit = min(int(num_match.group(1)), 50)
    elif re.search(r'\b(first|last)\s+transaction\b', msg):
        limit = 1

    # Detect filter
    if "deposit" in msg:
        txn_filter = "deposit"
    elif "withdraw" in msg:
        txn_filter = "withdraw"
    elif "transfer" in msg:
        txn_filter = "transfer"
    elif "first" in msg:
        txn_filter = "all"
    else:
        txn_filter = "all"

    position = "last" if "last" in msg or "recent" in msg else "first"

    return {"limit": limit, "filter": txn_filter, "position": position, "highlight": True}


# ── ABOUT NEOBANK INTENT PARSER ───────────────────────────────────
def parse_about_neobank(message: str) -> bool:
    """
    Detect when user is asking about NeoBank itself.
    Returns True if the message is an "about us" intent.

    Examples that trigger:
        "tell me about neobank"
        "what is neobank"
        "who are you"
        "about neobank pro"
        "neobank history"
        "what does neobank do"
        "neobank information"
        "neobank details"
        "show about page"
        "open about us"
    """
    msg = message.lower().strip()

    about_keywords = [
        "about neobank",
        "about neo bank",
        "what is neobank",
        "who are you",
        "tell me about neobank",
        "neobank history",
        "neobank information",
        "neobank details",
        "what does neobank",
        "neobank founded",
        "neobank team",
        "neobank mission",
        "neobank vision",
        "show about",
        "open about",
        "go to about",
        "about page",
        "about us",
        "company info",
        "company details",
        "who made neobank",
        "neobank story",
        "neobank awards",
        "neobank features",
        "neobank overview",
    ]

    return any(kw in msg for kw in about_keywords)



# ── STREAMING HELPERS ──────────────────────────────────────────────
async def stream_claude(system_prompt: str, message: str) -> AsyncGenerator[str, None]:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        async for chunk in stream_text_fake(
            "I'm running in offline mode. Set ANTHROPIC_API_KEY for full AI responses."
        ):
            yield chunk
        return

    payload = json.dumps({
        "model":    "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "stream":   True,
        "system":   system_prompt,
        "messages": [{"role": "user", "content": message}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
            "accept":            "text/event-stream",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if data.get("type") == "content_block_delta":
                            text = data.get("delta", {}).get("text", "")
                            if text:
                                yield f"data: {json.dumps({'type':'delta','text':text})}\n\n"
                                await asyncio.sleep(0)
                    except json.JSONDecodeError:
                        pass
    except Exception:
        fallback = "Sorry, I had trouble connecting. Please try again."
        async for chunk in stream_text_fake(fallback):
            yield chunk

    yield f"data: {json.dumps({'type':'done'})}\n\n"


async def stream_text_fake(text: str, delay: float = 0.018) -> AsyncGenerator[str, None]:
    words = text.split(" ")
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        yield f"data: {json.dumps({'type':'delta','text':chunk})}\n\n"
        await asyncio.sleep(delay)
    yield f"data: {json.dumps({'type':'done'})}\n\n"


# ── FALLBACK ANSWERS ───────────────────────────────────────────────
def generate_fallback_answer(message: str, tool_results: dict, user: dict) -> str:
    name = user.get("full_name", "").split()[0] if user.get("full_name") else "there"
    msg  = message.lower()

    if "balance_info" in tool_results and any(
        w in msg for w in ["balance", "much", "funds", "available"]
    ):
        bal = tool_results["balance_info"]["balance"]
        return f"Hi {name}! Your current balance is **₹{bal:,.2f}**."

    if "spending_stats" in tool_results and any(
        w in msg for w in ["spent", "spending", "summary", "total"]
    ):
        ss = tool_results["spending_stats"]
        return (
            f"**Your Spending Summary, {name}:**\n\n"
            f"💰 Total Deposited: ₹{ss['total_deposited']:,.2f} ({ss['deposit_count']} deposits)\n"
            f"💸 Total Spent: ₹{ss['total_spent']:,.2f} "
            f"({ss['withdrawal_count']} withdrawals, {ss['transfer_count']} transfers)\n"
            f"📊 Net: ₹{ss['net']:,.2f}"
        )

    if "faq_context" in tool_results and tool_results["faq_context"]:
        best = tool_results["faq_context"][0]
        return (
            f"**{best['title']}**\n\n"
            f"{best['content'][:800]}\n\n"
            f"*Anything else I can help with, {name}?*"
        )

    return (
        f"Hi {name}! I'm your NeoBank AI Assistant. I can help you with:\n\n"
        f"• 💰 Check your **balance** and transactions\n"
        f"• 📋 View **spending summary**\n"
        f"• 🏦 **Bank policies**: fees, limits, security\n"
        f"• 🤖 **Automate** operations — say 'deposit 1000'\n"
        f"• 📊 **Show transactions** — say 'show last 5 transactions'\n\n"
        f"What would you like to know?"
    )


# ── STREAMING CHAT ENDPOINT ────────────────────────────────────────
@router.post("/chat/stream")
async def chat_stream(data: ChatReq, user: dict = Depends(get_current_user)):
    if not data.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    message  = data.message.strip()
    # Unique ID for this message — used by dedup guard
    import hashlib, time
    msg_id = hashlib.md5(
        f"{user['id']}:{message}:{int(time.time()*10)}".encode()
    ).hexdigest()

    # FIX 1: Save user message exactly once using dedup guard
    save_message_once(user["id"], "user", message, f"u:{msg_id}")
    history = get_history(user["id"])

    # ── FIX 2: SHOW TRANSACTIONS INTENT ───────────────────────────
    txn_params = parse_show_transactions(message)
    if txn_params:
        direction = txn_params["position"]
        transaction_word = "transaction" if txn_params["limit"] == 1 else "transactions"
        transaction_scope = "" if txn_params["filter"] == "all" else f" {txn_params['filter']}"
        reply = (
            f"Sure! Opening the **History** tab and highlighting "
            f"your {direction} {txn_params['limit']}{transaction_scope} "
            f"{transaction_word} for you."
        )
        save_message_once(user["id"], "assistant", reply, f"a:{msg_id}")

        async def txn_stream():
            async for chunk in stream_text_fake(reply, delay=0.015):
                yield chunk
            # Send UI navigation event to frontend
            yield f"data: {json.dumps({'type':'show_transactions','limit':txn_params['limit'],'filter':txn_params['filter'],'position':txn_params['position'],'highlight':True})}\n\n"

        return StreamingResponse(
            txn_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # ── ABOUT NEOBANK INTENT ──────────────────────────────────────
    # If user asks about NeoBank, send a navigate_to SSE event.
    # Frontend (ChatBot.jsx) intercepts this and redirects to
    # the About Us page at http://localhost:3000/aboutus
    if parse_about_neobank(message):
        name  = user.get("full_name", "").split()[0] or "there"
        reply = (
            f"Of course, {name}! Let me take you to our **About Us** page "
            f"where you can learn all about NeoBank Pro — our story, mission, "
            f"team, awards, and everything we offer. Opening it now! 🚀"
        )
        save_message_once(user["id"], "assistant", reply, f"a:{msg_id}")

        async def about_stream():
            async for chunk in stream_text_fake(reply, delay=0.015):
                yield chunk
            # Send navigate_to event — frontend opens /aboutus
            yield f"data: {json.dumps({'type':'navigate_to','url':'/aboutus','target':'_self'})}\n\n"

        return StreamingResponse(
            about_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # ── AUTOMATION COMMAND CHECK ───────────────────────────────────
    automation_keywords = [
        "deposit", "withdraw", "transfer", "send money", "add money",
        "take out", "go to", "navigate", "open tab", "take me to", "switch to",
    ]
    is_automation = any(kw in message.lower() for kw in automation_keywords)

    if is_automation:
        bot_result = build_action_sequence(message)
        if bot_result["is_automation"]:
            conn = get_db()
            try:
                acc = fetch_account(user["id"], conn)
                current_balance = acc["balance"]
            finally:
                conn.close()

            is_valid, err_msg = validate_actions(bot_result["actions"], current_balance)
            if not is_valid:
                reply = f"⚠️ Cannot execute: {err_msg}"
                save_message_once(user["id"], "assistant", reply, f"a:{msg_id}")

                async def error_stream():
                    async for chunk in stream_text_fake(reply):
                        yield chunk
                    yield f"data: {json.dumps({'type':'automation_error','message':err_msg})}\n\n"

                return StreamingResponse(
                    error_stream(),
                    media_type="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
                )

            reply = bot_result["reply"]
            # FIX 1: Save automation reply exactly once
            save_message_once(user["id"], "assistant", reply, f"a:{msg_id}")

            async def automation_stream():
                async for chunk in stream_text_fake(reply, delay=0.015):
                    yield chunk
                yield f"data: {json.dumps({'type':'automation','actions':bot_result['actions'],'summary':bot_result['summary']})}\n\n"

            return StreamingResponse(
                automation_stream(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

    # ── NORMAL CHAT — AGENT + STREAM ──────────────────────────────
    agent_result  = agent.run(message, user, history)
    system_prompt = agent.build_system_prompt(
        user, agent_result["context"], agent_result["history_str"]
    )
    full_reply_parts = []

    async def chat_generator():
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if api_key:
            async for chunk in stream_claude(system_prompt, message):
                if chunk.startswith("data:"):
                    try:
                        payload = json.loads(chunk[5:].strip())
                        if payload.get("type") == "delta":
                            full_reply_parts.append(payload.get("text", ""))
                    except Exception:
                        pass
                yield chunk
        else:
            fallback = generate_fallback_answer(
                message, agent_result["tool_results"], user
            )
            full_reply_parts.append(fallback)
            async for chunk in stream_text_fake(fallback):
                yield chunk

        # FIX 1: Save reply exactly once after streaming completes
        full_reply = "".join(full_reply_parts)
        if full_reply:
            save_message_once(user["id"], "assistant", full_reply, f"a:{msg_id}")

        yield f"data: {json.dumps({'type':'meta','tools_used':[tc['tool'] for tc in agent_result['tool_calls']]})}\n\n"

    return StreamingResponse(
        chat_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── ABOUT US REDIRECT ─────────────────────────────────────────────
# When user visits http://localhost:8000/aboutus from the browser
# or the chatbot triggers a redirect, this returns the React page URL.
from fastapi.responses import RedirectResponse

@router.get("/aboutus")
def about_us_page():
    """
    Redirect to the React About Us page.
    The AI concierge sends navigate_to SSE event pointing to /aboutus.
    Visiting http://localhost:8000/aboutus also redirects here.
    """
    return RedirectResponse(url="http://localhost:3000/aboutus", status_code=302)


# ── CHAT HISTORY ENDPOINTS ─────────────────────────────────────────
@router.get("/chat/history")
def chat_history(user: dict = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT role, content, timestamp FROM chat_history "
        "WHERE user_id = ? ORDER BY timestamp ASC LIMIT 50",
        (user["id"],),
    )
    msgs = [dict(r) for r in c.fetchall()]
    conn.close()
    return msgs


@router.delete("/chat/history")
def clear_history(user: dict = Depends(get_current_user)):
    conn = get_db()
    conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user["id"],))
    conn.commit()
    conn.close()
    return {"message": "Chat history cleared"}
