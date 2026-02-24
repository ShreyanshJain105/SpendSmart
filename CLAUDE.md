---
description: 
alwaysApply: true
---

# CLAUDE.md — Instructions for Claude (and Other AI Assistants)

This file provides explicit guidance when using Claude (or any AI assistant) to work
on SpendSmart. Read `agents.md` first for architectural constraints — this file
supplements those rules with Claude-specific prompting context.

---

## Project Context

**SpendSmart** is a personal finance tracker.

- **Backend**: Python 3.11 / Flask 3 / SQLAlchemy 2 / Marshmallow 3 / SQLite
- **Frontend**: React 18 / Vite / Recharts / React Router v6
- **Test runner**: pytest + pytest-flask

The system is intentionally **small and layered**. Its value is in correctness and
maintainability, not feature count.

---

## When Generating Code

### DO
- Follow the four-layer architecture strictly: Model → Schema → Service → Route.
- Add structured logging (`structlog.get_logger()`) to every new service method.
- Return `ValueError` from services when a precondition is violated.
- Write tests for every new piece of logic.
- Prefer explicit over implicit (e.g., `db.session.get(Model, id)` over `.query.filter_by`).
- Use `decimal.Decimal` for monetary amounts (not `float`).

### DON'T
- Do not add any logic to route handlers beyond: parse → call service → serialize.
- Do not modify `app/errors.py` to silence specific error types.
- Do not use `flask.abort()` — raise Python exceptions instead, let the error handlers
  translate them to responses.
- Do not add new dependencies without updating `requirements.txt`.
- Do not generate code that assumes a specific database beyond SQLite/SQLAlchemy ORM
  (no raw SQL, no PostgreSQL-specific syntax).

---

## Test Instructions

When asked to write tests:
- Always use the `db` and `client` fixtures from `tests/conftest.py`.
- Always wrap DB code in `with app.app_context()`.
- For route tests, use `post_json` / `put_json` helpers from `test_routes.py`.
- Every new test class should test: one success case, one validation failure, one not-found.

---

## Commit Messages

Use conventional commits:
```
feat(transactions): add date-range filter to list endpoint
fix(budgets): correct actuals calculation for partial month
test(schemas): add edge cases for negative amount validation
```

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---|---|
| Putting SQL queries in routes | Move to a service method |
| Using `float` for money | Use `decimal.Decimal` |
| Catching `Exception` broadly | Catch specific exceptions |
| `session.add` without `session.commit` | Always commit in the service method that owns the transaction |
| Skipping `db.session.refresh(obj)` after commit in tests | Always refresh to re-load the state from DB |

---

## Suggested Prompts for Common Tasks

**Add a new endpoint:**
> "Following the existing pattern in `app/routes/transactions.py` and
> `app/services/transaction_service.py`, add a [describe feature] endpoint.
> Register the blueprint in `app/__init__.py` and write pytest tests."

**Debug a validation error:**
> "A marshmallow ValidationError is being raised for field `[field]`.
> Show me the schema and help me understand why the value `[value]` is invalid."

**Write tests for an existing feature:**
> "Using `tests/conftest.py` fixtures, write pytest tests for
> `app/services/budget_service.py`'s `get_with_actuals` method.
> Test the empty case, single-budget case, and over-budget case."
