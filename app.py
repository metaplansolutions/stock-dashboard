from flask import Flask, render_template, jsonify, request

from data_source import get_price_history, get_current_price
from portfolio_tracker import (
    add_holding,
    remove_holding,
    get_holdings,
    calculate_portfolio_pnl,
)
from db import init_db


def create_app(demo_mode: bool = False) -> Flask:
    """Flask application factory.

    Args:
        demo_mode: When True the app uses bundled sample data instead of
            live yfinance API calls.  Useful for testing and portfolio demos.

    Returns:
        Configured :class:`flask.Flask` application instance.
    """
    app = Flask(__name__)
    app.config["DEMO_MODE"] = demo_mode
    conn = init_db()

    # ------------------------------------------------------------------ pages

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/portfolio")
    def portfolio():
        holdings = get_holdings(conn)
        prices = {
            h["ticker"]: get_current_price(
                h["ticker"], demo_mode=app.config["DEMO_MODE"]
            )
            for h in holdings
        }
        pnl = calculate_portfolio_pnl(holdings, prices)
        return render_template(
            "portfolio.html", holdings=holdings, prices=prices, pnl=pnl
        )

    @app.route("/watchlist")
    def watchlist():
        rows = conn.execute("SELECT * FROM watchlist").fetchall()
        return render_template(
            "watchlist.html", watchlist=[dict(r) for r in rows]
        )

    # ----------------------------------------------------------------- API

    @app.route("/api/prices/<ticker>")
    def api_prices(ticker):
        df = get_price_history(ticker, demo_mode=app.config["DEMO_MODE"])
        if df.empty:
            return jsonify({"error": "No data"}), 404
        prices = [
            {
                "date": str(d),
                "open": r.get("open", 0),
                "high": r.get("high", 0),
                "low": r.get("low", 0),
                "close": r["close"],
                "volume": r.get("volume", 0),
            }
            for d, r in df.iterrows()
        ]
        return jsonify({"ticker": ticker, "prices": prices})

    @app.route("/api/holdings", methods=["POST"])
    def api_add_holding():
        data = request.json
        hid = add_holding(
            conn,
            data["ticker"],
            float(data["shares"]),
            float(data["price"]),
            data.get("date", ""),
        )
        return jsonify({"id": hid}), 201

    @app.route("/api/holdings/<int:hid>", methods=["DELETE"])
    def api_remove_holding(hid):
        remove_holding(conn, hid)
        return jsonify({"ok": True})

    @app.route("/api/watchlist", methods=["POST"])
    def api_add_watchlist():
        data = request.json
        ticker = data.get("ticker", "").upper().strip()
        if not ticker:
            return jsonify({"error": "ticker required"}), 400
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (ticker, alert_above, alert_below) "
            "VALUES (?, ?, ?)",
            (ticker, data.get("alert_above"), data.get("alert_below")),
        )
        conn.commit()
        return jsonify({"ok": True}), 201

    @app.route("/api/watchlist/<int:wid>", methods=["DELETE"])
    def api_remove_watchlist(wid):
        conn.execute("DELETE FROM watchlist WHERE id = ?", (wid,))
        conn.commit()
        return jsonify({"ok": True})

    return app


if __name__ == "__main__":
    create_app(demo_mode=True).run(debug=True, port=5001)
