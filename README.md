# NeoBank Pro

NeoBank Pro is a full-stack digital banking prototype with a React web interface and a FastAPI backend. It combines everyday banking operations with an AI concierge that can answer policy questions, inspect account data, stream responses, and automate selected dashboard actions through the UI.

> **Prototype notice:** This project is intended for development and demonstration. It is not production-ready banking software. Do not use real customer data, credentials, or financial accounts.

## Features

### Banking

- User registration and email/password sign-in
- Optional Google sign-in integration
- Session-based Bearer-token authentication
- SQLite database created automatically on first backend start
- Savings, checking, and premium account types
- Deposits and withdrawals with balance validation
- Transfers between registered NeoBank users
- Transaction history and account summaries
- Seeded demo account for local exploration

### AI concierge

- Streaming chat over Server-Sent Events (SSE)
- Optional Claude integration through the Anthropic API
- Offline fallback responses when no Anthropic API key is configured
- Local RAG knowledge base for questions about accounts, fees, limits, KYC, security, support, and banking policies
- LangChain-style ReAct agent implemented in Python without the LangChain package
- Tools for balance, transactions, spending statistics, account details, and knowledge-base search
- Persistent chat history stored per user
- Natural-language commands for deposits, withdrawals, transfers, navigation, balance checks, and transaction history
- Chat commands that navigate to the About Us page or open and highlight dashboard history

### Frontend experience

- React 18 single-page application
- Sign-in and account creation screens
- Banking dashboard with Home, Deposit, Withdraw, Transfer, and History tabs
- Animated UI automation bot for chatbot-generated action sequences
- Public `/aboutus` page with company information, products, team, timeline, awards, and contact details
- Session persistence using browser `sessionStorage`

## Technology Stack

| Area | Technology |
| --- | --- |
| Frontend | React 18, React Router DOM 6, Create React App / `react-scripts` |
| Backend | Python, FastAPI, Pydantic |
| Server | Uvicorn / ASGI |
| Database | SQLite 3 through Python's standard library |
| Authentication | Bearer session tokens, SHA-256 password hashing |
| AI provider | Anthropic Claude API, optional |
| Retrieval | Local TF-IDF-style RAG engine using Python standard library |
| Automation | Backend command parser plus React `BotAutomation` component |

## Project Structure

```text
neobank-pro project/
├── backend/
│   ├── main.py              # FastAPI application and CORS configuration
│   ├── auth.py              # Registration, login, logout, and Google auth
│   ├── banking.py           # Account and transaction endpoints
│   ├── chatbot.py           # SSE chat endpoint and intent handling
│   ├── model.py             # SQLite schema, database helpers, and Pydantic models
│   ├── langchain_agent.py   # LangChain-style tool-planning agent
│   ├── rag_engine.py        # Local document retrieval
│   ├── knowledge_base.py   # Banking FAQ and policy documents
│   ├── playwright_bot.py   # Natural-language automation parser and validator
│   └── ...
├── frontend/
│   ├── package.json
│   ├── public/index.html
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── AuthPage.jsx
│           ├── Dashboard.jsx
│           ├── ChatBot.jsx
│           ├── BotAutomation.jsx
│           └── AboutUs.jsx
├── .gitignore               # Local secrets, databases, caches, and build output
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9 or newer
- Node.js 16 or newer and npm
- A modern browser
- An Anthropic API key only if you want live Claude responses

## Installation

### 1. Clone or open the project

```bash
cd "neobank-pro project"
```

### 2. Create and activate a Python virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install uvicorn
```

The requirements file contains the core Python packages and optional package notes. `uvicorn` is currently commented out there, so it is installed explicitly above.

### 4. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Configuration

The backend works without external configuration by using the local fallback chatbot. To enable Claude streaming responses, set `ANTHROPIC_API_KEY` before starting the backend:

Linux/macOS:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

The application sends requests to the Anthropic Messages API using the model configured in `backend/chatbot.py`. Without the key, the local agent and fallback response path remain available.

Google sign-in is optional. The current Google client ID is configured directly in `backend/auth.py`; production deployments should move this value to environment configuration and register the correct frontend origin in Google Cloud Console.

## Running the Project

Use two terminals from the project root.

### Terminal 1: start the backend

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API root: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json
- About Us redirect: http://localhost:8000/aboutus

### Terminal 2: start the frontend

```bash
cd frontend
npm start
```

Open http://localhost:3000 in a browser. The frontend expects the backend at `http://localhost:8000`, and the backend CORS configuration currently allows `http://localhost:3000`.

For a production frontend build:

```bash
cd frontend
npm run build
```

The generated static files are placed in `frontend/build/`. The project does not currently include a production web server configuration.

## Demo Account

On the first backend start, the database is created as `backend/neobank.db` when the server is launched from the `backend` directory. If no users exist, the backend seeds:

| Field | Value |
| --- | --- |
| Name | Demo User |
| Email | `demo@neobank.com` |
| Password | `demo1234` |
| Initial balance | ₹25,000 |
| Account type | Savings |

The seeded account also includes sample deposit, withdrawal, salary, shopping, and transfer transactions.

To reset local demo data, stop the backend, remove `backend/neobank.db`, and start the backend again:

```bash
rm backend/neobank.db
```

On Windows, delete the file through File Explorer or run:

```powershell
Remove-Item backend\neobank.db
```

## API Overview

All routes below, except the root and documentation routes, are served by the backend at `http://localhost:8000`. Protected routes require:

```http
Authorization: Bearer <token>
```

### Public routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | API status and docs link |
| `POST` | `/auth/register` | Create a user and account |
| `POST` | `/auth/login` | Sign in and receive a session token |
| `POST` | `/auth/google` | Sign in with a verified Google ID token |
| `GET` | `/docs` | Interactive Swagger documentation |

### Authenticated routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/auth/me` | Return the current user |
| `POST` | `/auth/logout` | Delete the current session token |
| `GET` | `/account` | Return account and user details |
| `GET` | `/account/transactions?limit=50` | Return transaction history, newest first with stable ID ordering |
| `POST` | `/account/deposit` | Deposit `{ "amount": 1000, "note": "Salary" }` |
| `POST` | `/account/withdraw` | Withdraw `{ "amount": 250, "note": "Cash" }` |
| `POST` | `/account/transfer` | Transfer `{ "to_email": "user@example.com", "amount": 500, "note": "Dinner" }` |
| `GET` | `/chat/history` | Return recent chat messages |
| `POST` | `/chat/stream` | Stream chatbot output as SSE |

Example authenticated request:

```bash
curl http://localhost:8000/account \
  -H "Authorization: Bearer <token>"
```

The complete request and response schemas are available in Swagger at `/docs`.

## Chatbot Commands

The assistant supports ordinary questions and special commands. Examples:

```text
What is my balance?
Show my spending summary
What are the savings account requirements?
Show transactions
Show first 5 transactions
Show first transaction
Show the last 5 transactions
Show last 2 transactions
Show last transaction
Show last 2 deposit transactions
Deposit 1000 for groceries
Withdraw 300
Transfer 500 to user@example.com
Go to history
Tell me about NeoBank
```

Transaction commands navigate to the History tab and highlight the matching rows:

- `show transactions` highlights the first 10 rows in the displayed history.
- `first N transactions` highlights the first `N` rows.
- `last N transactions` highlights the last `N` rows in the account timeline, meaning the oldest `N` transactions. This includes the original opening balance when it is within the requested range.
- `last transaction` highlights the oldest transaction, normally the account-opening transaction.
- Type filters can be combined with a range, for example `last 2 deposit transactions`.

The transaction API returns rows newest first using `timestamp DESC, id DESC`, which makes ordering deterministic when several transactions share the same timestamp. The chatbot sends the requested range, type filter, and first/last position to the dashboard through a `show_transactions` SSE event.

Other chat responses use `text/event-stream`. The frontend consumes `delta`, `done`, `automation`, `automation_error`, `show_transactions`, and `navigate_to` events to update the interface.

## Database

SQLite tables are initialized by `init_db()` in `backend/model.py`:

- `users`: identity and password hashes
- `sessions`: active Bearer tokens
- `accounts`: one account per user
- `transactions`: deposits, withdrawals, and transfers
- `chat_history`: persisted assistant conversations

The database path is relative to the process working directory and is configured as `neobank.db`. Run the backend from `backend/` to keep the database in that directory.

## Development Notes

- Backend imports are written for execution from the `backend/` directory, so start Uvicorn there.
- The frontend uses fixed API URLs in its components; changing the backend host or port requires updating those values.
- The RAG engine is local and does not require a vector database or embedding service.
- The automation module parses commands on the backend, but the actual animated interaction is performed by the React frontend.
- Server-side Playwright is not required for the current automation flow; `playwright_bot.py` is a parser and validator.
- Frontend tests can be started with `npm test` when test files are added.
- Transaction history requests are ordered by timestamp and transaction ID so chatbot highlighting remains stable for records created at the same time.
- The root `.gitignore` excludes `.env` files, SQLite databases, Python caches, `node_modules`, React build output, logs, and editor files. `frontend/package-lock.json` remains tracked.

## Current Limitations and Security Considerations

This repository is a learning/demo application and needs additional work before any real deployment:

- Passwords currently use SHA-256 directly; use a slow password hashing algorithm such as Argon2 or bcrypt in production.
- Session tokens do not currently have an expiry or refresh flow.
- Secrets and the Google client ID should be supplied through environment variables or a secret manager.
- CORS is configured for one local frontend origin.
- SQLite is suitable for local development, not high-volume banking workloads.
- Transactions and session handling need stronger concurrency, audit, and authorization controls.
- Add HTTPS, CSRF protections where applicable, rate limiting, input validation, monitoring, backups, and a formal compliance review before deployment.
- Direct money movement should still be treated as demo functionality until it has production-grade authorization, audit logging, concurrency controls, and test coverage.

## Troubleshooting

### `ModuleNotFoundError` when starting FastAPI

Activate the virtual environment and reinstall dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install uvicorn
```

### The frontend cannot reach the API

Confirm that:

1. Uvicorn is running on port `8000`.
2. The React app is running on port `3000`.
3. The browser is not blocking requests because the frontend origin differs from the configured CORS origin.

### The chatbot says it is in offline mode

This is expected when `ANTHROPIC_API_KEY` is not set. The local RAG and fallback paths should still respond to supported questions.

### The demo account is missing

Stop the backend, remove `backend/neobank.db`, and restart it. Seeding occurs only when the database has no users.

## ✍️ Author

**Nirali Soni**
* **Role:** Artificial Intelligence Engineer
* **GitHub:** [@Nirali06](https://github.com/Nirali06)
* **LinkedIn:** [Nirali Soni](https://linkedin.com/in/nirali-soni-3683821a5)
* **Email:** niralisoni0606@gmail.com


## License

No license file is currently included. Add an explicit license before distributing the project.
