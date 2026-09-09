# playwright_bot.py
# ─────────────────────────────────────────────────────────────────
# PLAYWRIGHT BOT — UI Automation Agent
#
# This module parses natural language commands from the chatbot
# and converts them into structured UI action sequences that the
# React frontend executes via animated cursor automation.
#
# When user says "deposit 5000 and then withdraw 300":
#   1. Backend parses → [{action:"deposit", amount:5000}, {action:"withdraw", amount:300}]
#   2. Frontend receives action list
#   3. BotAutomation.jsx simulates cursor movement → clicks tab → fills form → submits
#
# This mimics how Playwright works:
#   playwright.click("#deposit-tab")
#   playwright.fill("#amount-input", "5000")
#   playwright.click("#submit-btn")
# ─────────────────────────────────────────────────────────────────
from __future__ import annotations
import re
from typing import List, Dict, Optional, Tuple


# ── ACTION TYPES ───────────────────────────────────────────────────
VALID_ACTIONS = {"deposit", "withdraw", "transfer", "navigate", "show_balance"}


# ── AMOUNT PARSER ──────────────────────────────────────────────────
def parse_amount(text: str) -> Optional[float]:
    """
    Extract a numeric amount from text.
    Handles: "5000", "5,000", "5k", "₹500", "5 thousand", "1.5 lakh"
    
    Examples:
        "deposit 5000"    → 5000.0
        "withdraw ₹1,500" → 1500.0
        "send 5k"         → 5000.0
        "2 lakh"          → 200000.0
    """
    text = text.lower().strip()
    # Remove currency symbols
    text = re.sub(r'[₹$,]', '', text)

    # Handle "1.5 lakh", "2 lakh"
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*lakh', text)
    if lakh_match:
        return float(lakh_match.group(1)) * 100000

    # Handle "5k", "10k"
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*k\b', text)
    if k_match:
        return float(k_match.group(1)) * 1000

    # Handle "5 thousand"
    thou_match = re.search(r'(\d+(?:\.\d+)?)\s*thousand', text)
    if thou_match:
        return float(thou_match.group(1)) * 1000

    # Standard number
    num_match = re.search(r'\d+(?:\.\d+)?', text)
    if num_match:
        return float(num_match.group())

    return None


def parse_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    return match.group() if match else None


# ── COMMAND PARSER ─────────────────────────────────────────────────
def parse_command(command: str) -> List[Dict]:
    """
    Parse a natural language banking command into a list of UI actions.
    
    Input: "deposit 5000 and then withdraw 300 for food"
    Output: [
        {"action": "deposit",  "amount": 5000, "note": ""},
        {"action": "withdraw", "amount": 300,  "note": "food"}
    ]
    
    Supported commands:
        "deposit [amount] [for note]"
        "withdraw [amount] [for note]"
        "transfer [amount] to [email] [for note]"
        "go to [tab]" / "show [tab]" / "navigate to [tab]"
        "show balance" / "check balance"
        "show history" / "view transactions"
    """
    command_lower = command.lower().strip()
    actions = []

    # ── Split compound commands ────────────────────────────────────
    # Split on: "and then", "then", "after that", "also", "and"
    separators = r'\band then\b|\bthen\b|\bafter that\b|\balso\b|\band\b'
    parts = re.split(separators, command_lower)
    parts = [p.strip() for p in parts if p.strip()]

    for part in parts:
        action = _parse_single_command(part)
        if action:
            actions.append(action)

    # If nothing parsed, try the whole command as one
    if not actions:
        action = _parse_single_command(command_lower)
        if action:
            actions.append(action)

    return actions


def _parse_note(text: str) -> str:
    """Extract note/description from command text (after 'for' keyword)."""
    for_match = re.search(r'\bfor\s+(.+)$', text)
    if for_match:
        note = for_match.group(1).strip()
        # Remove amounts from note
        note = re.sub(r'[\d,₹.]+\s*', '', note).strip()
        return note if len(note) > 1 else ""
    return ""


def _parse_single_command(text: str) -> Optional[Dict]:
    """Parse a single atomic command string into an action dict."""

    # ── DEPOSIT ────────────────────────────────────────────────────
    if re.search(r'\b(deposit|add money|credit|put in)\b', text):
        amount = parse_amount(text)
        if amount and amount > 0:
            return {
                "action": "deposit",
                "amount": amount,
                "note":   _parse_note(text),
                "description": f"Deposit ₹{amount:,.0f}"
            }

    # ── WITHDRAW ───────────────────────────────────────────────────
    elif re.search(r'\b(withdraw|take out|debit|cash out|pull out)\b', text):
        amount = parse_amount(text)
        if amount and amount > 0:
            return {
                "action": "withdraw",
                "amount": amount,
                "note":   _parse_note(text),
                "description": f"Withdraw ₹{amount:,.0f}"
            }

    # ── TRANSFER ───────────────────────────────────────────────────
    elif re.search(r'\b(transfer|send|pay|remit)\b', text):
        amount = parse_amount(text)
        email  = parse_email(text)
        if amount and amount > 0:
            return {
                "action":   "transfer",
                "amount":   amount,
                "to_email": email or "",
                "note":     _parse_note(text),
                "description": f"Transfer ₹{amount:,.0f}" + (f" to {email}" if email else "")
            }

    # ── NAVIGATE ───────────────────────────────────────────────────
    elif re.search(r'\b(go to|navigate to|open|show|take me to|switch to)\b', text):
        tab = _extract_tab(text)
        if tab:
            return {
                "action": "navigate",
                "tab":    tab,
                "description": f"Navigate to {tab.title()} tab"
            }

    # ── SHOW BALANCE ───────────────────────────────────────────────
    elif re.search(r'\b(balance|check balance|show balance|my balance)\b', text):
        return {
            "action": "show_balance",
            "description": "Show account balance"
        }

    # ── SHOW HISTORY ───────────────────────────────────────────────
    elif re.search(r'\b(history|transactions|statement|recent payments)\b', text):
        return {
            "action": "navigate",
            "tab":    "history",
            "description": "Navigate to History tab"
        }

    return None


def _extract_tab(text: str) -> Optional[str]:
    """Extract the target tab name from a navigation command."""
    tab_map = {
        "home":     ["home", "dashboard", "main"],
        "deposit":  ["deposit", "add money", "credit"],
        "withdraw": ["withdraw", "withdrawal", "debit"],
        "transfer": ["transfer", "send money", "pay"],
        "history":  ["history", "transactions", "statement", "activity"],
    }
    for tab, keywords in tab_map.items():
        for kw in keywords:
            if kw in text:
                return tab
    return None


# ── ACTION SEQUENCE BUILDER ────────────────────────────────────────
def build_action_sequence(command: str) -> Dict:
    """
    Main entry point called by chatbot.py.
    
    Returns:
    {
        "is_automation": bool,
        "actions": [...],          # list of action dicts
        "summary": "...",          # human-readable summary
        "reply": "...",            # chatbot response message
    }
    """
    actions = parse_command(command)

    if not actions:
        return {
            "is_automation": False,
            "actions": [],
            "summary": "",
            "reply": None
        }

    # Build human-readable summary
    descriptions = [a.get("description", a["action"]) for a in actions]
    if len(descriptions) == 1:
        summary = descriptions[0]
    elif len(descriptions) == 2:
        summary = f"{descriptions[0]} and then {descriptions[1]}"
    else:
        summary = ", ".join(descriptions[:-1]) + f", and finally {descriptions[-1]}"

    reply = (
        f"🤖 I'll automate that for you! Executing: **{summary}**\n\n"
        f"Watch the cursor — I'm navigating the UI and filling in the details automatically."
    )

    return {
        "is_automation": True,
        "actions": actions,
        "summary": summary,
        "reply": reply
    }


# ── VALIDATION ─────────────────────────────────────────────────────
def validate_actions(actions: List[Dict], current_balance: float) -> Tuple[bool, str]:
    """
    Validate a sequence of actions before execution.
    Checks: amounts positive, sufficient balance for withdrawals.
    
    Returns (is_valid, error_message)
    """
    running_balance = current_balance

    for action in actions:
        action_type = action.get("action")
        amount = action.get("amount", 0)

        if action_type in ("withdraw", "transfer"):
            if amount > running_balance:
                return False, (
                    f"Insufficient balance for {action_type} of ₹{amount:,.2f}. "
                    f"Available: ₹{running_balance:,.2f}"
                )
            running_balance -= amount

        elif action_type == "deposit":
            running_balance += amount

        if amount < 0:
            return False, f"Amount cannot be negative: ₹{amount}"

    return True, ""
