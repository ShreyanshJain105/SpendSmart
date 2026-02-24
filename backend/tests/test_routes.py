"""
HTTP integration tests — exercise the full request/response cycle via
Flask's test client.

These verify that:
- Routes correctly accept/reject inputs
- Error envelopes are consistent
- Status codes match HTTP conventions
"""
import json
import pytest


JSON = "application/json"


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type=JSON)


def put_json(client, url, data):
    return client.put(url, data=json.dumps(data), content_type=JSON)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

class TestCategoryRoutes:
    def test_create_category(self, client):
        r = post_json(client, "/api/categories", {"name": "Food", "icon": "🍔", "color": "#f97316"})
        assert r.status_code == 201
        body = r.get_json()
        assert body["name"] == "Food"
        assert "id" in body

    def test_list_categories(self, client):
        post_json(client, "/api/categories", {"name": "Rent", "icon": "🏠", "color": "#8b5cf6"})
        r = client.get("/api/categories")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_create_duplicate_category_returns_409(self, client):
        post_json(client, "/api/categories", {"name": "Unique"})
        r = post_json(client, "/api/categories", {"name": "Unique"})
        assert r.status_code == 409

    def test_create_category_invalid_color_returns_422(self, client):
        r = post_json(client, "/api/categories", {"name": "Bad", "color": "red"})
        assert r.status_code == 422
        body = r.get_json()
        assert body["code"] == 422
        assert "details" in body

    def test_get_nonexistent_category_returns_400(self, client):
        r = client.get("/api/categories/9999")
        # ValueError is mapped to 400 by error handler
        assert r.status_code == 400

    def test_delete_category(self, client):
        r = post_json(client, "/api/categories", {"name": "ToDelete"})
        cat_id = r.get_json()["id"]
        r2 = client.delete(f"/api/categories/{cat_id}")
        assert r2.status_code == 200


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

class TestTransactionRoutes:
    def _create_category(self, client):
        r = post_json(client, "/api/categories", {"name": "Misc"})
        return r.get_json()["id"]

    def test_create_transaction(self, client):
        cat_id = self._create_category(client)
        r = post_json(client, "/api/transactions", {
            "amount": 75.50,
            "type": "expense",
            "description": "Groceries",
            "category_id": cat_id,
            "date": "2024-03-10",
        })
        assert r.status_code == 201
        body = r.get_json()
        assert float(body["amount"]) == 75.5
        assert body["type"] == "expense"

    def test_create_transaction_missing_type_returns_422(self, client):
        r = post_json(client, "/api/transactions", {"amount": 10})
        assert r.status_code == 422

    def test_create_transaction_zero_amount_returns_422(self, client):
        r = post_json(client, "/api/transactions", {"amount": 0, "type": "expense"})
        assert r.status_code == 422

    def test_list_transactions_filter_by_type(self, client):
        post_json(client, "/api/transactions", {"amount": 100, "type": "income", "date": "2024-03-01"})
        post_json(client, "/api/transactions", {"amount": 20, "type": "expense", "date": "2024-03-02"})
        r = client.get("/api/transactions?type=income")
        body = r.get_json()
        assert all(t["type"] == "income" for t in body["data"])

    def test_list_transactions_pagination(self, client):
        for i in range(5):
            post_json(client, "/api/transactions", {"amount": i + 1, "type": "expense", "date": "2024-03-01"})
        r = client.get("/api/transactions?limit=3&offset=0")
        body = r.get_json()
        assert len(body["data"]) == 3
        assert body["total"] == 5

    def test_update_transaction(self, client):
        r = post_json(client, "/api/transactions", {"amount": 10, "type": "expense", "date": "2024-03-01"})
        t_id = r.get_json()["id"]
        r2 = put_json(client, f"/api/transactions/{t_id}", {"amount": 99})
        assert r2.status_code == 200
        assert float(r2.get_json()["amount"]) == 99.0

    def test_delete_transaction(self, client):
        r = post_json(client, "/api/transactions", {"amount": 5, "type": "expense", "date": "2024-03-01"})
        t_id = r.get_json()["id"]
        r2 = client.delete(f"/api/transactions/{t_id}")
        assert r2.status_code == 200
        r3 = client.get(f"/api/transactions/{t_id}")
        assert r3.status_code == 400  # raises ValueError → 400


# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------

class TestBudgetRoutes:
    def _create_category(self, client, name="Housing"):
        r = post_json(client, "/api/categories", {"name": name})
        return r.get_json()["id"]

    def test_create_budget(self, client):
        cat_id = self._create_category(client)
        r = post_json(client, "/api/budgets", {
            "category_id": cat_id,
            "month": "2024-03",
            "limit_amount": 1500,
        })
        assert r.status_code == 201
        body = r.get_json()
        assert body["month"] == "2024-03"
        assert float(body["limit_amount"]) == 1500.0

    def test_invalid_month_format_returns_422(self, client):
        cat_id = self._create_category(client, name="Rent2")
        r = post_json(client, "/api/budgets", {
            "category_id": cat_id,
            "month": "March-2024",
            "limit_amount": 500,
        })
        assert r.status_code == 422

    def test_list_budgets_with_actuals(self, client):
        cat_id = self._create_category(client, name="Food2")
        post_json(client, "/api/budgets", {"category_id": cat_id, "month": "2024-03", "limit_amount": 400})
        post_json(client, "/api/transactions", {"amount": 100, "type": "expense", "date": "2024-03-01", "category_id": cat_id})
        r = client.get("/api/budgets?month=2024-03")
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) == 1
        assert data[0]["spent"] == 100.0
        assert data[0]["remaining"] == 300.0


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class TestAnalyticsRoutes:
    def test_summary_empty_month(self, client):
        r = client.get("/api/analytics/summary?month=2000-01")
        assert r.status_code == 200
        body = r.get_json()
        assert body["income"] == 0.0
        assert body["net"] == 0.0

    def test_trends_default(self, client):
        r = client.get("/api/analytics/trends")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

class TestAiRoutes:
    def test_categorize_known(self, client):
        r = post_json(client, "/api/ai/categorize", {"description": "Netflix subscription"})
        assert r.status_code == 200
        body = r.get_json()
        assert "category" in body
        assert "confidence" in body

    def test_categorize_missing_description_returns_422(self, client):
        r = post_json(client, "/api/ai/categorize", {})
        assert r.status_code == 422

    def test_error_envelope_shape(self, client):
        r = post_json(client, "/api/ai/categorize", {})
        body = r.get_json()
        assert "error" in body
        assert "code" in body
