# Roomora AI 🛋️

AI interior designer — upload a room photo, set a budget (INR), pick a style,
get an AI-curated furniture plan with live Telegraph prices.

**Hackathon:** Telegraph Season II · Apps & Agents · Mission 15 · Deadline Dec 1 2026 23:59 UTC  
**Stack:** FastAPI · React + Vite · SQLite  
**Status:** Phase 1 complete — full skeleton, mock services, all tests passing.

---

## Project layout

```
roomora-ai/
├── backend/
│   ├── config.py            # all settings (reads .env, mock mode by default)
│   ├── db.py                # SQLite setup — designs table
│   ├── main.py              # FastAPI app + API routes
│   ├── requirements.txt     # Python dependencies
│   ├── data/
│   │   └── catalog.py       # mock furniture catalog (INR prices)
│   ├── services/
│   │   ├── vision.py        # room analysis (mock → real OpenRouter in Phase 2)
│   │   ├── designer.py      # design plan builder
│   │   └── pricing.py       # pricing (mock → real Telegraph in Phase 2)
│   └── tests/
│       ├── test_routes.py   # route tests via FastAPI TestClient
│       ├── test_designer.py # unit tests for the designer service
│       └── test_pricing.py  # unit tests for the pricing service
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # single-page design UI
│   │   └── index.css        # styles
│   ├── package.json
│   └── vite.config.js
├── .env.example             # copy to .env and fill in keys — never commit .env
├── .gitignore
├── ROADMAP.md
└── README.md                ← you are here
```

---

## Backend — PowerShell setup (Windows)

Run all commands from the **`roomora-ai`** folder.

### 1 · Create a virtual environment

```powershell
py -m venv .venv
```

### 2 · Activate it

```powershell
.venv\Scripts\Activate.ps1
```

> If you get a script-execution error, run this **once** as Administrator:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3 · Install dependencies

```powershell
pip install -r backend\requirements.txt
```

### 4 · Create your `.env` file

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in your Telegraph and OpenRouter keys.  
In Phase 1 (mock mode) the keys are not used — you can leave them as-is.

### 5 · Start the backend server

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- API root: <http://127.0.0.1:8000/api/health>  
- Interactive docs: <http://127.0.0.1:8000/docs>  
- Stop with **Ctrl+C**.

### 6 · Run the tests (no server needed)

```powershell
pytest backend\tests\ -v
```

Expected: **35 passed**.

---

## Frontend — PowerShell setup (Windows)

Open a **second** PowerShell window for the frontend.

### 1 · Go to the frontend folder

```powershell
cd frontend
```

### 2 · Install dependencies

```powershell
npm install
```

### 3 · Start the Vite dev server

```powershell
npm run dev
```

App available at <http://localhost:5173> (Vite prints the exact URL).  
Stop with **Ctrl+C**.

> The backend must be running on port 8000 for API calls to work.  
> The app reads `VITE_API_URL` from `frontend/.env` (defaults to `http://localhost:8000`).

---

## API routes

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check — returns `{status, app, mode}` |
| `GET` | `/api/catalog` | List furniture items with INR prices |
| `POST` | `/api/design` | Upload photo + budget + style → design plan |
| `GET` | `/api/receipts` | List all past designs (newest first) |

### POST `/api/design` — form fields

| Field | Type | Validation |
|-------|------|-----------|
| `photo` | file | jpg / png / webp, max 8 MB |
| `budget_inr` | int | 5,000 – 50,00,000 |
| `style` | str | `minimalist` · `modern` · `japanese` · `scandinavian` · `luxury` |

---

## Environment variables (section 6)

See [`.env.example`](.env.example) for the full list with comments.

| Variable | Default | Purpose |
|----------|---------|---------|
| `ROOMORA_MODE` | `mock` | `mock` = Phase 1 placeholders, `real` = Phase 2 live APIs |
| `TELEGRAPH_BEARER_KEY` | _(empty)_ | Telegraph API key — backend only, never expose |
| `OPENROUTER_API_KEY` | _(empty)_ | OpenRouter key for vision model |
| `TELEGRAPH_MAX_SPEND_USD` | `1.0` | Safety cap per Telegraph call |
| `MAX_UPLOAD_MB` | `8` | Maximum photo upload size |

---

## Rules

- Keep code simple and commented.
- Never commit keys — use `.env` (listed in `.gitignore`).
- The Telegraph key **must stay on the backend only** — never send it to the frontend.
- Telegraph endpoint: `POST https://backend.telegraphprotocol.com/agent/chat`, Bearer auth, always set `maxSpendUsd`. Network: Sepolia testnet.
- `Mock` = placeholder · `Real` = verified working.

---

## Phase 2 (not yet done)

- Real room analysis via OpenRouter vision model.
- Real Telegraph purchase — receipt ID + USD cost saved per item.
- Budget-aware plan using live prices.
- Redesigned room image generation.

---

## Suggested commit message

```
feat: Phase 1 complete — API, mock services, React UI, 35 tests passing
```
