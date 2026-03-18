from __future__ import annotations

import sqlite3


def add_holding(
    conn: sqlite3.Connection,
    ticker: str,
    shares: float,
    price: float,
    date: str = "",
) -> int:
    """Insert a new holding and return its row id.

    Args:
        conn: Open database connection from :func:`db.init_db`.
        ticker: Stock symbol.
        shares: Number of shares purchased.
        price: Purchase price per share.
        date: ISO date string for the purchase date (optional).

    Returns:
        The ``id`` of the newly inserted row.
    """
    cursor = conn.execute(
        "INSERT INTO holdings (ticker, shares, purchase_price, purchase_date) "
        "VALUES (?, ?, ?, ?)",
        (ticker, shares, price, date),
    )
    conn.commit()
    return cursor.lastrowid


def remove_holding(conn: sqlite3.Connection, holding_id: int) -> None:
    """Delete a holding by its id."""
    conn.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
    conn.commit()


def get_holdings(conn: sqlite3.Connection) -> list[dict]:
    """Return all holdings ordered by creation time (newest first).

    Returns:
        List of dicts with keys: id, ticker, shares, purchase_price,
        purchase_date, created_at.
    """
    rows = conn.execute(
        "SELECT * FROM holdings ORDER BY created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def calculate_portfolio_pnl(
    holdings: list[dict],
    current_prices: dict[str, float],
) -> dict:
    """Calculate aggregate portfolio profit / loss.

    Args:
        holdings: List of holding dicts (from :func:`get_holdings`).
        current_prices: Mapping of ticker → current price.  If a ticker is
            missing the purchase price is used as the current price.

    Returns:
        Dict with keys:
        - ``total_cost``    — total amount invested.
        - ``total_value``   — current market value.
        - ``total_pnl``     — absolute profit / loss (value - cost).
        - ``total_pnl_pct`` — percentage profit / loss.
    """
    total_cost = sum(h["shares"] * h["purchase_price"] for h in holdings)
    total_value = sum(
        h["shares"] * current_prices.get(h["ticker"], h["purchase_price"])
        for h in holdings
    )
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0.0
    return {
        "total_cost": total_cost,
        "total_value": total_value,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
    }
