# main.py — NeoBank Pro API entry point
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import init_db
from auth import router as auth_router
from banking import router as banking_router
from chatbot import router as chatbot_router


app = FastAPI(title="NeoBank Pro API", version="5.0.0",
              description="Banking API with LangChain Agent, RAG, Streaming Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router)
app.include_router(banking_router)
app.include_router(chatbot_router)

@app.get("/")
def root():
    return {"status": "NeoBank Pro API v5.0 running", "docs": "/docs"}
