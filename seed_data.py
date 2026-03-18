"""seed_data.py — Populate the dashboard database with sample holdings and watchlist entries.

Run once before starting the app for the first time:
    python seed_data.py
"""

from db import init_db
from portfolio_tracker import add_holding


def seed() -> None:
    conn = init_db()

    # Holdings
    add_holding(conn, "AAPL", 10, 150.00, "2026-01-15")
    add_holding(conn, "NVDA", 5, 800.00, "2026-02-01")
    add_holding(conn, "MSFT", 8, 400.00, "2026-02-15")

    # Watchlist
    conn.execute(
        "INSERT OR IGNORE INTO watchlist (ticker, alert_above, alert_below) "
        "VALUES (?, ?, ?)",
        ("AAPL", 200, 140),
    )
    conn.execute(
        "INSERT OR IGNORE INTO watchlist (ticker, alert_above, alert_below) "
        "VALUES (?, ?, ?)",
        ("TSLA", 300, 150),
    )
    conn.commit()
    conn.close()
    print("Seeded holdings and watchlist")


if __name__ == "__main__":
    seed()
