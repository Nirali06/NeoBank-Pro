# langchain_agent.py
# ─────────────────────────────────────────────────────────────────
# LangChain-style Agent implementation for NeoBank.
#
# WHAT IS A LANGCHAIN AGENT?
# An agent is an LLM that can:
#   1. Receive a user question
#   2. Decide which TOOL to call to get information
#   3. Call the tool and observe the result
#   4. Repeat (reason → act → observe) until it has enough info
#   5. Generate a final answer grounded in real data
#
# This implements the ReAct (Reasoning + Acting) pattern:
#   Thought: What do I need to answer this?
#   Action:  Call tool X with input Y
#   Observation: Tool returned Z
#   Thought: Now I know enough to answer
#   Final Answer: ...
#
# TOOLS AVAILABLE:
#   - get_balance        : Live account balance
#   - get_transactions   : Recent transaction history
#   - get_spending_stats : Aggregated spending summary
#   - rag_search         : Knowledge base FAQ retrieval
#   - get_account_info   : Account type, creation date etc.
# ─────────────────────────────────────────────────────────────────
from __future__ import annotations
import re
from typing import List, Dict, Any, Callable, Optional
from model import get_db, fetch_account
from rag_engine import rag


# ── TOOL DEFINITIONS ──────────────────────────────────────────────
# Each tool is a Python function + metadata (name, description).
# The agent planner reads descriptions to decide which tool to use.

class Tool:
    """Represents a callable tool available to the agent."""
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    def run(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)


def tool_get_balance(user_id: int) -> Dict:
    """
    TOOL: get_balance
    Returns the user's current account balance.
    Use when user asks: "what is my balance", "how much money do I have"
    """
    conn = get_db()
    try:
        acc = fetch_account(user_id, conn)
        return {
            "balance": acc["balance"],
            "acc_type": acc.get("acc_type", "savings"),
            "account_id": acc["id"]
        }
    finally:
        conn.close()


def tool_get_transactions(user_id: int, limit: int = 5) -> List[Dict]:
    """
    TOOL: get_transactions
    Returns the most recent transactions.
    Use when: "show my transactions", "recent payments", "last transfer"
    """
    conn = get_db()
    try:
        acc = fetch_account(user_id, conn)
        c = conn.cursor()
        c.execute("""
            SELECT type, amount, note, timestamp
            FROM transactions
            WHERE account_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
        """, (acc["id"], limit))
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()


def tool_get_spending_stats(user_id: int) -> Dict:
    """
    TOOL: get_spending_stats
    Returns aggregated financial summary: total in/out, counts, net.
    Use when: "spending summary", "how much spent", "total deposits"
    """
    conn = get_db()
    try:
        acc = fetch_account(user_id, conn)
        c = conn.cursor()
        c.execute("SELECT type, amount FROM transactions WHERE account_id = ?", (acc["id"],))
        rows = c.fetchall()
        total_in    = sum(r["amount"] for r in rows if r["type"] == "deposit")
        total_out   = sum(r["amount"] for r in rows if r["type"] != "deposit")
        count_dep   = sum(1 for r in rows if r["type"] == "deposit")
        count_wd    = sum(1 for r in rows if r["type"] == "withdraw")
        count_tr    = sum(1 for r in rows if r["type"] == "transfer")
        return {
            "total_deposited":   total_in,
            "total_spent":       total_out,
            "deposit_count":     count_dep,
            "withdrawal_count":  count_wd,
            "transfer_count":    count_tr,
            "net":               total_in - total_out,
        }
    finally:
        conn.close()


def tool_rag_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    TOOL: rag_search
    Searches the knowledge base for relevant banking information.
    Use when: policy questions, fee questions, how-to questions,
              ATM fees, account types, insurance, security etc.
    """
    results = rag.retrieve(query, top_k=top_k)
    return results


def tool_get_account_info(user_id: int) -> Dict:
    """
    TOOL: get_account_info
    Returns full account metadata.
    Use when: "what type of account", "when did I open account"
    """
    conn = get_db()
    try:
        acc = fetch_account(user_id, conn)
        c = conn.cursor()
        c.execute("SELECT full_name, email, created_at FROM users WHERE id = ?", (user_id,))
        user = dict(c.fetchone())
        return {**acc, **user}
    finally:
        conn.close()


# ── AGENT PLANNER ─────────────────────────────────────────────────
# Decides which tools to call based on user message keywords.
# In a full LangChain implementation, this would be done by the LLM
# using function-calling / tool-use API. Here we use keyword routing.

INTENT_TOOL_MAP = {
    "get_balance": [
        "balance", "much money", "how much", "funds", "available",
        "account balance", "current balance"
    ],
    "get_transactions": [
        "transaction", "history", "recent", "last", "payment",
        "transfer", "sent", "received", "statement"
    ],
    "get_spending_stats": [
        "spent", "spending", "summary", "total", "deposited",
        "withdrawn", "net", "overall", "breakdown"
    ],
    "get_account_info": [
        "account type", "savings", "checking", "premium",
        "opened", "account number", "when did", "what kind"
    ],
    "rag_search": [
        "fee", "charge", "limit", "policy", "how to", "atm",
        "insurance", "fdic", "dicgc", "security", "fraud",
        "interest", "minimum balance", "kyc", "open account",
        "contact", "support", "phone", "transfer", "imps",
        "neft", "rtgs", "upi", "maximum", "daily limit",
        "monthly limit", "lost", "stolen", "block card",
        "password", "reset", "encryption", "data protection",
        "premium account", "about neobank", "what is"
    ]
}


def plan_tools(message: str) -> List[str]:
    """
    AGENT PLANNING STEP (ReAct: Reason)
    Analyse the message and return list of tool names to call.
    Always includes rag_search for knowledge base coverage.
    """
    msg_lower = message.lower()
    selected = set()

    for tool_name, keywords in INTENT_TOOL_MAP.items():
        for kw in keywords:
            if kw in msg_lower:
                selected.add(tool_name)
                break

    # Always search RAG for any question
    selected.add("rag_search")

    # Prioritize order: live data first, then knowledge base
    priority = ["get_balance", "get_transactions", "get_spending_stats",
                "get_account_info", "rag_search"]
    return [t for t in priority if t in selected]


# ── AGENT RUNNER ──────────────────────────────────────────────────
class NeoBankAgent:
    """
    LangChain-style ReAct Agent for NeoBank.
    
    Implements the Reason → Act → Observe loop:
    1. REASON: plan_tools() decides what to look up
    2. ACT:    call each tool with user context
    3. OBSERVE: collect all tool outputs
    4. GENERATE: build enriched prompt for LLM / fallback
    """

    def __init__(self):
        self.tools = {
            "get_balance":       tool_get_balance,
            "get_transactions":  tool_get_transactions,
            "get_spending_stats": tool_get_spending_stats,
            "rag_search":        tool_rag_search,
            "get_account_info":  tool_get_account_info,
        }

    def run(self, message: str, user: dict, history: list) -> Dict:
        """
        Run the agent loop and return:
        {
            "tool_calls": [...],   # which tools were called
            "tool_results": {...}, # what each tool returned
            "context": "...",      # formatted context string for LLM
            "history_str": "...",  # conversation history string
        }
        """
        user_id = user["id"]

        # ── STEP 1: REASON (plan) ──────────────────────────────────
        tools_to_call = plan_tools(message)
        tool_calls = []
        tool_results = {}

        # ── STEP 2: ACT (call tools) ──────────────────────────────
        for tool_name in tools_to_call:
            try:
                if tool_name == "get_balance":
                    result = tool_get_balance(user_id)
                    tool_results["balance_info"] = result
                    tool_calls.append({"tool": tool_name, "result": result})

                elif tool_name == "get_transactions":
                    result = tool_get_transactions(user_id, limit=5)
                    tool_results["recent_transactions"] = result
                    tool_calls.append({"tool": tool_name, "result": result})

                elif tool_name == "get_spending_stats":
                    result = tool_get_spending_stats(user_id)
                    tool_results["spending_stats"] = result
                    tool_calls.append({"tool": tool_name, "result": result})

                elif tool_name == "get_account_info":
                    result = tool_get_account_info(user_id)
                    tool_results["account_info"] = result
                    tool_calls.append({"tool": tool_name, "result": result})

                elif tool_name == "rag_search":
                    result = tool_rag_search(message)
                    tool_results["faq_context"] = result
                    tool_calls.append({"tool": tool_name, "result": result})

            except Exception as e:
                tool_calls.append({"tool": tool_name, "error": str(e)})

        # ── STEP 3: OBSERVE (format context) ──────────────────────
        context_parts = []

        if "balance_info" in tool_results:
            bi = tool_results["balance_info"]
            context_parts.append(
                f"LIVE ACCOUNT DATA:\n"
                f"- Current Balance: ₹{bi['balance']:,.2f}\n"
                f"- Account Type: {bi.get('acc_type', 'savings').title()}"
            )

        if "spending_stats" in tool_results:
            ss = tool_results["spending_stats"]
            context_parts.append(
                f"SPENDING SUMMARY:\n"
                f"- Total Deposited: ₹{ss['total_deposited']:,.2f} ({ss['deposit_count']} deposits)\n"
                f"- Total Spent: ₹{ss['total_spent']:,.2f} "
                f"({ss['withdrawal_count']} withdrawals, {ss['transfer_count']} transfers)\n"
                f"- Net: ₹{ss['net']:,.2f}"
            )

        if "recent_transactions" in tool_results:
            txns = tool_results["recent_transactions"]
            if txns:
                lines = ["RECENT TRANSACTIONS (latest 5):"]
                for t in txns:
                    icon = "↓" if t["type"] == "deposit" else ("↑" if t["type"] == "withdraw" else "⇄")
                    lines.append(
                        f"  {icon} {t['type'].upper()} ₹{t['amount']:,.2f}"
                        f" — {t['note'] or 'no note'} [{t['timestamp'][:10]}]"
                    )
                context_parts.append("\n".join(lines))

        if "faq_context" in tool_results and tool_results["faq_context"]:
            lines = ["KNOWLEDGE BASE (Bank Policy / FAQ):"]
            for doc in tool_results["faq_context"][:3]:
                lines.append(f"\n[{doc['title']}]\n{doc['content'][:600]}...")
            context_parts.append("\n".join(lines))

        context_str = "\n\n".join(context_parts)

        # ── Build conversation history string ──────────────────────
        history_str = ""
        if history:
            history_str = "CONVERSATION HISTORY:\n"
            for msg in history[-8:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_str += f"{role}: {msg['content'][:200]}\n"

        return {
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "context": context_str,
            "history_str": history_str,
        }

    def build_system_prompt(self, user: dict, context: str, history_str: str) -> str:
        """Build the full system prompt injected into the LLM call."""
        return f"""You are NeoBank Assistant — an intelligent, friendly AI banking assistant.

You have access to the user's live account data and NeoBank's complete policy knowledge base.

CAPABILITIES:
- Answer questions about account balance, transactions, spending
- Explain NeoBank policies: fees, limits, security, insurance, account types
- Guide users through banking operations
- Provide personalized financial insights

RULES:
1. Always use the provided CONTEXT to answer. Never invent account numbers or balances.
2. Be concise but complete. Use ₹ for Indian rupee amounts.
3. Address user by first name: {user['full_name'].split()[0]}
4. For operations (deposit/withdraw): guide user to the correct tab or say you can do it automatically
5. If context doesn't have the answer, say so honestly
6. Keep responses under 300 words unless detailed explanation needed

USER: {user['full_name']} ({user['email']})

{history_str}

RETRIEVED CONTEXT:
{context}
"""


# ── SINGLETON INSTANCE ─────────────────────────────────────────────
agent = NeoBankAgent()
