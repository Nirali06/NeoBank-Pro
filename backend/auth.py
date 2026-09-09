from __future__ import annotations
from pydantic import BaseModel
# auth.py — Authentication routes
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from model import (get_db, hash_password, make_token, get_current_user,
                   security, RegisterReq, LoginReq)
import sqlite3


router = APIRouter(prefix="/auth")

@router.post("/register", status_code=201)
def register(data: RegisterReq):
    if not data.full_name.strip():
        raise HTTPException(400, "Full name is required")
    if not data.email.strip() or "@" not in data.email:
        raise HTTPException(400, "Valid email is required")
    if len(data.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    if data.initial_deposit < 0:
        raise HTTPException(400, "Initial deposit cannot be negative")

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
                  (data.full_name.strip(), data.email.strip().lower(), hash_password(data.password)))
        uid = c.lastrowid
        c.execute("INSERT INTO accounts (user_id, balance, acc_type) VALUES (?, ?, ?)",
                  (uid, data.initial_deposit, data.acc_type or "savings"))
        acc_id = c.lastrowid
        if data.initial_deposit > 0:
            c.execute("INSERT INTO transactions (account_id, type, amount, note) VALUES (?, ?, ?, ?)",
                      (acc_id, "deposit", data.initial_deposit, "Opening balance"))
        conn.commit()
        token = make_token(uid)
        return {"token": token, "user": {"id": uid, "full_name": data.full_name, "email": data.email}}
    except sqlite3.IntegrityError:
        raise HTTPException(400, "This email is already registered")
    finally:
        conn.close()


@router.post("/login")
def login(data: LoginReq):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (data.email.strip().lower(),))
    user = c.fetchone()
    conn.close()
    if not user:
        raise HTTPException(401, "No account found with this email")
    if user["password"] != hash_password(data.password):
        raise HTTPException(401, "Incorrect password. Please try again.")
    token = make_token(user["id"])
    return {"token": token, "user": {"id": user["id"], "full_name": user["full_name"], "email": user["email"]}}


@router.post("/logout")
def logout(creds: HTTPAuthorizationCredentials = Depends(security)):
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (creds.credentials,))
    conn.commit()
    conn.close()
    return {"message": "Signed out successfully"}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


# ── GOOGLE SIGN-IN ─────────────────────────────────────────────────
# Requires: pip install google-auth
# SETUP: Replace YOUR_GOOGLE_CLIENT_ID with your actual client ID
#        from console.cloud.google.com

GOOGLE_CLIENT_ID = "245299824891-dcu0c3v88ia4jtfcu60fqg53bb9oj684.apps.googleusercontent.com"

class GoogleAuthReq(BaseModel):
    id_token: str

@router.post("/google")
def google_signin(data: GoogleAuthReq):
    """
    Verify Google ID token and sign in / register the user.
    Called after Google's frontend SDK returns a credential JWT.
    """
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests

        # Verify the token with Google
        id_info = google_id_token.verify_oauth2_token(
            data.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ImportError:
        # google-auth not installed — return helpful error
        raise HTTPException(
            400,
            "Google auth requires: pip install google-auth. "
            "Add it to requirements.txt and restart the backend."
        )
    except Exception as e:
        raise HTTPException(401, f"Invalid Google token: {str(e)}")

    email     = id_info.get("email", "").lower()
    full_name = id_info.get("name", email.split("@")[0].title())

    if not email:
        raise HTTPException(400, "Google account has no email")

    conn = get_db()
    c = conn.cursor()

    # Check if user already exists
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()

    if user:
        # Existing user — just create new session
        uid = user["id"]
    else:
        # New user — auto-register with random password (Google users won't use it)
        import secrets as _secrets
        random_pw = hash_password(_secrets.token_hex(16))
        c.execute(
            "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
            (full_name, email, random_pw)
        )
        uid = c.lastrowid
        # Create account with zero balance
        c.execute("INSERT INTO accounts (user_id, balance, acc_type) VALUES (?, ?, ?)",
                  (uid, 0.0, "savings"))
        conn.commit()

    conn.close()
    token = make_token(uid)
    return {
        "token": token,
        "user":  {"id": uid, "full_name": full_name, "email": email},
    }
