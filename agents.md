# AI Agent Guidance — SpendSmart

## Purpose
This file constrains how AI coding agents (GitHub Copilot, GPT-4, Claude, Gemini, etc.)
should generate and modify code in this project. Treat these as non-negotiable rules,
not suggestions.

---

## Architecture Rules

### Layer Separation (CRITICAL)
The codebase is divided into four layers. **Never mix responsibilities**:

| Layer | Location | Allowed to do | Never do |
|---|---|---|---|
| Models | `app/models/` | Define schema, constraints, `to_dict()` | Business logic, HTTP parsing |
| Schemas | `app/schemas/` | Validate/deserialize input | DB calls, service calls |
| Services | `app/services/` | Business logic, DB ops | `request`, `jsonify`, HTTP concerns |
| Routes | `app/routes/` | Parse request, call service, return response | Any business logic |

### Database
- **Use the ORM** (`db.session`, Model.query). Never write raw SQL unless using SQLAlchemy `text()` explicitly.
- **Do not bypass constraints**. If a DB constraint exists (CHECK, UNIQUE), do not add application-level code that silently ignores it.
- **Do not lazy-load in list endpoints**. Load all needed relations eagerly or use explicit JOINs.

### Error Handling
- Services raise `ValueError` for domain errors (not found, invalid state).
- Routes return the error envelope: `{ "error": "...", "code": N }`.
- **Never swallow exceptions silently** (`except: pass` is forbidden).
- Log every exception before re-raising or handling.

---

## Coding Standards

### Python
- Python 3.11+. Use type hints on all function signatures.
- Line length ≤ 100 characters.
- Module docstrings required on all new files.
- No `global` state outside of SQLAlchemy models.
- Format with `black` before committing.

### JavaScript / React
- ES Modules only. No CommonJS (`require`).
- No inline styles in JSX beyond one-off layout adjustments; use CSS classes.
- API calls belong in `src/api/`. Components never import `axios` directly.
- Components that fetch data must handle loading and error states.

---

## Testing Requirements

For every new feature you add, you **must** also add:
1. **Unit tests** for any new schema validation rules (`tests/test_schemas.py`).
2. **Service tests** for any new business logic (`tests/test_services.py`).
3. **Route tests** for the new endpoint (`tests/test_routes.py`).

Test requirements:
- Each test must be independent (no shared mutable state between tests).
- Use the `db` fixture from `conftest.py`, not the development database.
- Assert on both the happy path and at least one error/edge case.

---

## What AI Agents Must NOT Do

1. **Do not remove validation** in schemas to "simplify" code.
2. **Do not add business logic to route handlers**.
3. **Do not use `db.engine.execute()` or `db.session.execute(text(...))`** without a code review comment explaining why the ORM cannot do it.
4. **Do not ignore constraint violations** — let them bubble up to the `IntegrityError` handler.
5. **Do not add new endpoints without corresponding tests**.
6. **Do not use mutable default arguments** in Python function signatures.
7. **Do not import Flask's `g`, `request`, or `current_app` inside service files**.

---

## Extension Guide

When adding a new resource (e.g., "savings goals"):

```
1. Create app/models/savings_goal.py       (model + to_dict)
2. Add to app/models/__init__.py
3. Create app/schemas/savings_goal.py      (schema + update schema)
4. Create app/services/savings_goal_service.py
5. Create app/routes/savings_goals.py      (blueprint)
6. Register blueprint in app/__init__.py
7. Add tests: test_schemas, test_services, test_routes
```

This is the **only** acceptable order. Do not skip steps or merge layers.
