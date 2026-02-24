# SpendSmart

Personal finance tracker with a layered Flask REST API, a React + Vite SPA, and a SQLite-first datastore (with optional PostgreSQL/Supabase support). The codebase is intentionally small and structured for correctness, testability, and ease of extension.

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Repository structure](#repository-structure)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Running locally](#running-locally)
- [Testing](#testing)
- [API](#api)
- [Architecture principles](#architecture-principles)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Transactions**: CRUD with filters and pagination.
- **Categories**: CRUD with validation (name/icon/color).
- **Budgets**: Monthly budgets with “spent / remaining” calculated from transactions.
- **Analytics**: Summary, breakdown, and trends endpoints for dashboarding.
- **AI (best-effort)**: Rule-based category suggestion for a transaction description (no API key required).

## Tech stack

### Backend

- **Python**: 3.11+
- **Flask**: 3.x
- **SQLAlchemy**: 2.x (via Flask-SQLAlchemy 3.x)
- **Marshmallow**: 3.x (request validation)
- **Testing**: pytest + pytest-flask
- **Logging**: structlog (JSON logs)
- **DataBase**: SupaBase(PostgresSql)

### Frontend

- **React**: 19.x
- **Vite**: 7.x
- **Routing**: React Router (v7)
- **Charts**: Recharts
- **HTTP**: Axios (single shared client)

## Repository structure

```
backend/
├── app/
│   ├── models/        # ORM models (DB schema + constraints)
│   ├── schemas/       # Marshmallow schemas (input validation)
│   ├── services/      # Business logic + DB operations (no Flask imports)
│   ├── routes/        # Flask blueprints (thin HTTP layer)
│   ├── database.py    # SQLAlchemy db instance + init logic
│   └── errors.py      # Centralized error handlers
├── tests/             # pytest: schema/service/route coverage
├── config.py          # development/testing/production config
└── run.py             # local dev entrypoint

frontend/
├── src/
│   ├── api/           # API modules built on a shared Axios client
│   ├── context/       # app context (cached categories, active month)
│   ├── components/    # reusable components (forms, tables, modals)
│   └── pages/         # dashboard + feature pages
└── vite.config.js
```

## Getting started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (recommended: 20+)

## Configuration

The backend loads a local `.env` (if present) via `python-dotenv`.

### Environment variables (backend)

- `FLASK_ENV`: `development` (default) / `testing` / `production`
- `DATABASE_URL`: Optional in development; **required** in production. When unset, development falls back to a local SQLite DB file.

Example `.env`:

```bash
FLASK_ENV=development
# Optional (development): Postgres/Supabase connection string
# DATABASE_URL=postgresql://...
```

### Databases

- **Development default**: `backend/spendsmart_dev.db` (SQLite)
- **Testing**: SQLite in-memory (`sqlite:///:memory:`)
- **Production**: PostgreSQL via `DATABASE_URL` (engine options enforce SSL)

## Running locally

### Backend (Flask API)

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

API will be available at `http://localhost:5000` (base path: `/api`).

### Frontend (React SPA)

```bash
cd frontend
npm install
npm run dev
```

App will be available at `http://localhost:5173`.

> Note: the frontend API base URL is configured in `frontend/src/api/client.js` and defaults to `http://localhost:5000/api`.

## Testing

Backend tests (schemas, services, and full HTTP integration tests):

```bash
cd backend
pytest -v
```

Coverage:

```bash
cd backend
coverage run -m pytest
coverage report -m
```

Frontend lint:

```bash
cd frontend
npm run lint
```

## API

Base URL: `http://localhost:5000/api`

### Endpoints (high level)

| Area | Method | Endpoint | Notes |
|---|---:|---|---|
| Transactions | GET | `/transactions` | Filters: `type`, `category_id`, `date_from`, `date_to`; pagination: `limit`, `offset` |
|  | POST | `/transactions` | Create |
|  | GET | `/transactions/:id` | Read |
|  | PUT | `/transactions/:id` | Update |
|  | DELETE | `/transactions/:id` | Delete |
| Categories | GET | `/categories` | List |
|  | POST | `/categories` | Create |
|  | GET | `/categories/:id` | Read |
|  | PUT | `/categories/:id` | Update |
|  | DELETE | `/categories/:id` | Delete |
| Budgets | GET | `/budgets?month=YYYY-MM` | List with computed actuals |
|  | POST | `/budgets` | Create |
| Analytics | GET | `/analytics/summary?month=YYYY-MM` | Income/expense/net |
|  | GET | `/analytics/breakdown?month=YYYY-MM` | By-category breakdown |
|  | GET | `/analytics/trends?months=6` | Multi-month trend data |
| AI | POST | `/ai/categorize` | `{ "description": "..." }` → `{ category, confidence }` |

### Error envelope

All error responses are normalized into a consistent JSON shape, for example:

```json
{ "error": "Validation failed", "code": 422, "details": { "field": ["..."] } }
```

## Architecture principles

- **Strict layering (Models → Schemas → Services → Routes)**:
  - Routes only parse input, call a service, and serialize output.
  - Services own business logic and DB operations and raise `ValueError` for domain/precondition issues.
  - Schemas validate request boundaries and exclude unknown fields for forward compatibility.
- **DB constraints are a safety net**: the database enforces invariants (e.g., non-negative amounts, unique monthly budgets).
- **Test-first ergonomics**: the testing config uses an in-memory SQLite DB to keep tests fast and isolated.
- **AI is optional**: categorization is best-effort and never blocks core flows; the UI debounces requests and ignores low-confidence results.

## Troubleshooting

- **Frontend can’t reach the API**: ensure the backend is running on port `5000` and `frontend/src/api/client.js` points to `http://localhost:5000/api`.
- **PowerShell activation blocked**: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (or activate via CMD) and retry.
- **Using Supabase/Postgres locally**: set `DATABASE_URL` in `.env`. SSL is enforced automatically for Postgres URLs.

## Contributing

- Follow the layer separation rules in `AGENTS.md` and project guidance in `CLAUDE.md`.
- Add tests for new schema/service/route behavior.
- Keep route handlers thin (no business logic).

## License

Add your preferred license (e.g., MIT) in a `LICENSE` file, then reference it here.
