import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app


def test_dashboard_loads():
    app = create_app(demo_mode=True)
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Stock Dashboard" in resp.data


def test_api_prices():
    app = create_app(demo_mode=True)
    client = app.test_client()
    resp = client.get("/api/prices/AAPL")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "prices" in data
    assert len(data["prices"]) > 0


def test_api_prices_unknown_ticker_returns_404():
    app = create_app(demo_mode=True)
    client = app.test_client()
    resp = client.get("/api/prices/ZZZZ")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_portfolio_page_loads():
    app = create_app(demo_mode=True)
    client = app.test_client()
    resp = client.get("/portfolio")
    assert resp.status_code == 200
    assert b"Portfolio" in resp.data


def test_watchlist_page_loads():
    app = create_app(demo_mode=True)
    client = app.test_client()
    resp = client.get("/watchlist")
    assert resp.status_code == 200
    assert b"Watchlist" in resp.data


def test_add_holding_api():
    app = create_app(demo_mode=True)
    client = app.test_client()
    resp = client.post(
        "/api/holdings",
        json={"ticker": "AAPL", "shares": 10, "price": 150.0, "date": "2026-01-15"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "id" in data
    assert isinstance(data["id"], int)


def test_delete_holding_api():
    app = create_app(demo_mode=True)
    client = app.test_client()
    # Add first
    add_resp = client.post(
        "/api/holdings",
        json={"ticker": "NVDA", "shares": 5, "price": 800.0},
    )
    hid = add_resp.get_json()["id"]
    # Now delete
    del_resp = client.delete("/api/holdings/" + str(hid))
    assert del_resp.status_code == 200
    assert del_resp.get_json()["ok"] is True
