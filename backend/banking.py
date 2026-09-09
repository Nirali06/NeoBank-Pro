# banking.py — Banking operation routes
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from model import get_db, get_current_user, fetch_account, TxnReq, TransferReq

router = APIRouter(prefix="/account")

@router.get("")
def get_account(user=Depends(get_current_user)):
    conn = get_db()
    acc = fetch_account(user["id"], conn)
    conn.close()
    return {**acc, "full_name": user["full_name"], "email": user["email"]}

@router.get("/transactions")
def get_transactions(limit: int = 50, user=Depends(get_current_user)):
    conn = get_db()
    acc = fetch_account(user["id"], conn)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE account_id = ? ORDER BY timestamp DESC, id DESC LIMIT ?",
              (acc["id"], limit))
    txns = [dict(r) for r in c.fetchall()]
    conn.close()
    return txns

@router.post("/deposit")
def deposit(data: TxnReq, user=Depends(get_current_user)):
    if data.amount <= 0:
        raise HTTPException(400, "Amount must be greater than zero")
    conn = get_db()
    acc = fetch_account(user["id"], conn)
    new_bal = acc["balance"] + data.amount
    conn.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_bal, acc["id"]))
    conn.execute("INSERT INTO transactions (account_id, type, amount, note) VALUES (?, ?, ?, ?)",
                 (acc["id"], "deposit", data.amount, data.note))
    conn.commit()
    conn.close()
    return {"message": "Deposit successful", "new_balance": new_bal}

@router.post("/withdraw")
def withdraw(data: TxnReq, user=Depends(get_current_user)):
    if data.amount <= 0:
        raise HTTPException(400, "Amount must be greater than zero")
    conn = get_db()
    acc = fetch_account(user["id"], conn)
    if acc["balance"] < data.amount:
        conn.close()
        raise HTTPException(400, f"Insufficient balance. Available: ₹{acc['balance']:.2f}")
    new_bal = acc["balance"] - data.amount
    conn.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_bal, acc["id"]))
    conn.execute("INSERT INTO transactions (account_id, type, amount, note) VALUES (?, ?, ?, ?)",
                 (acc["id"], "withdraw", data.amount, data.note))
    conn.commit()
    conn.close()
    return {"message": "Withdrawal successful", "new_balance": new_bal}

@router.post("/transfer")
def transfer(data: TransferReq, user=Depends(get_current_user)):
    if data.amount <= 0:
        raise HTTPException(400, "Amount must be greater than zero")
    if data.to_email.strip().lower() == user["email"].lower():
        raise HTTPException(400, "Cannot transfer to your own account")
    conn = get_db()
    c = conn.cursor()
    from_acc = fetch_account(user["id"], conn)
    if from_acc["balance"] < data.amount:
        conn.close()
        raise HTTPException(400, f"Insufficient balance. Available: ₹{from_acc['balance']:.2f}")
    c.execute("SELECT u.id, u.full_name, a.id AS acc_id FROM users u JOIN accounts a ON u.id = a.user_id WHERE u.email = ?",
              (data.to_email.strip().lower(),))
    recipient = c.fetchone()
    if not recipient:
        conn.close()
        raise HTTPException(404, "Recipient email not found in NeoBank")
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (data.amount, from_acc["id"]))
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (data.amount, recipient["acc_id"]))
    conn.execute("INSERT INTO transactions (account_id, type, amount, note) VALUES (?, ?, ?, ?)",
                 (from_acc["id"], "transfer", data.amount, f"To {recipient['full_name']}: {data.note}"))
    conn.execute("INSERT INTO transactions (account_id, type, amount, note) VALUES (?, ?, ?, ?)",
                 (recipient["acc_id"], "deposit", data.amount, f"From {user['full_name']}: {data.note}"))
    conn.commit()
    conn.close()
    return {"message": f"₹{data.amount:.2f} transferred to {recipient['full_name']}"}
