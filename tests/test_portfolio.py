import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db import init_db
from portfolio_tracker import (
    add_holding,
    remove_holding,
    get_holdings,
    calculate_portfolio_pnl,
)


def test_add_and_get_holdings(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    add_holding(conn, "AAPL", 10, 150.00, "2026-01-15")
    add_holding(conn, "NVDA", 5, 800.00, "2026-02-01")
    holdings = get_holdings(conn)
    assert len(holdings) == 2
    tickers = {h["ticker"] for h in holdings}
    assert "AAPL" in tickers
    assert "NVDA" in tickers
    conn.close()


def test_remove_holding(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    hid = add_holding(conn, "AAPL", 10, 150.00, "2026-01-15")
    remove_holding(conn, hid)
    assert len(get_holdings(conn)) == 0
    conn.close()


def test_calculate_pnl():
    holdings = [
        {"ticker": "AAPL", "shares": 10, "purchase_price": 150.00},
        {"ticker": "NVDA", "shares": 5, "purchase_price": 800.00},
    ]
    prices = {"AAPL": 175.00, "NVDA": 850.00}
    pnl = calculate_portfolio_pnl(holdings, prices)
    assert pnl["total_cost"] == 10 * 150 + 5 * 800
    assert pnl["total_value"] == 10 * 175 + 5 * 850
    assert pnl["total_pnl"] == 500.0
    assert abs(pnl["total_pnl_pct"] - 9.09) < 0.1


def test_calculate_pnl_no_holdings():
    pnl = calculate_portfolio_pnl([], {})
    assert pnl["total_cost"] == 0
    assert pnl["total_value"] == 0
    assert pnl["total_pnl"] == 0
    assert pnl["total_pnl_pct"] == 0.0


def test_calculate_pnl_missing_price_uses_purchase_price():
    holdings = [{"ticker": "AAPL", "shares": 10, "purchase_price": 150.00}]
    pnl = calculate_portfolio_pnl(holdings, {})
    assert pnl["total_pnl"] == 0.0


def test_db_tables_created(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "holdings" in tables
    assert "watchlist" in tables
    conn.close()
