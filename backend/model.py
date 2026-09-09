# model.py
# ─────────────────────────────────────────────────────────────────
# Database schema, connection helpers, Pydantic request models,
# and auth utilities. Imported by all other backend modules.
# ─────────────────────────────────────────────────────────────────
from __future__ import annotations
import sqlite3
import hashlib
import secrets
from typing import Optional
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# ── SECURITY SCHEME ────────────────────────────────────────────────
security = HTTPBearer()

# ── DATABASE ────────────────────────────────────────────────────────
DB_PATH = "neobank.db"

def get_db() -> sqlite3.Connection:
    """Open and return a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # enables dict-style access: row["email"]
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


def init_db():
    """Create all tables and seed demo data on first run."""
    conn = get_db()
    c = conn.cursor()

    # users — authentication table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name  TEXT    NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # sessions — one token per login
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token      TEXT    PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # accounts — bank account per user
    c.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL UNIQUE,
            balance    REAL    DEFAULT 0.0,
            acc_type   TEXT    DEFAULT 'savings',
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # transactions — full history
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            type       TEXT    NOT NULL,
            amount     REAL    NOT NULL,
            note       TEXT    DEFAULT '',
            timestamp  TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)

    # chat_history — persisted conversation per user
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            role       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            timestamp  TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── Seed demo user ──────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        hashed = hash_password("demo1234")
        c.execute("INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
                  ("Demo User", "demo@neobank.com", hashed))
        c.execute("INSERT INTO accounts (user_id, balance, acc_type) VALUES (?, ?, ?)",
                  (1, 25000.0, "savings"))
        seed_txns = [
            (1, "deposit",  25000.0, "Opening balance"),
            (1, "withdraw",  3000.0, "ATM withdrawal"),
            (1, "deposit",   8000.0, "Salary credit"),
            (1, "withdraw",  1500.0, "Online shopping"),
            (1, "transfer",  2000.0, "To friend"),
        ]
        for t in seed_txns:
            c.execute("INSERT INTO transactions (account_id, type, amount, note) VALUES (?, ?, ?, ?)", t)

    conn.commit()
    conn.close()


# ── HELPERS ────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """SHA-256 hash of the password. Never store plain text."""
    return hashlib.sha256(password.encode()).hexdigest()


def make_token(user_id: int) -> str:
    """Generate a secure 64-char hex session token and persist it."""
    token = secrets.token_hex(32)
    conn = get_db()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    FastAPI dependency — validates Bearer token and returns user dict.
    Used with Depends(get_current_user) on every protected route.
    """
    token = creds.credentials
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.full_name, u.email
        FROM users u JOIN sessions s ON u.id = s.user_id
        WHERE s.token = ?
    """, (token,))
    user = c.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    return dict(user)


def fetch_account(user_id: int, conn: sqlite3.Connection) -> dict:
    """Fetch the bank account for a user. Raises 404 if not found."""
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))
    acc = c.fetchone()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return dict(acc)


# ── PYDANTIC REQUEST MODELS ────────────────────────────────────────
class RegisterReq(BaseModel):
    full_name: str
    email: str
    password: str
    initial_deposit: Optional[float] = 0.0
    acc_type: Optional[str] = "savings"   # savings | checking | premium


class LoginReq(BaseModel):
    email: str
    password: str


class TxnReq(BaseModel):
    amount: float
    note: Optional[str] = ""


class TransferReq(BaseModel):
    to_email: str
    amount: float
    note: Optional[str] = ""


class ChatReq(BaseModel):
    message: str


class BotActionReq(BaseModel):
    """Request body for UI automation bot commands."""
    command: str   # e.g. "deposit 5000" or "withdraw 300 for food"
