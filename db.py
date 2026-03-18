import sqlite3


def init_db(db_path: str = "dashboard.db") -> sqlite3.Connection:
    """Initialise the SQLite database and return an open connection.

    Creates tables if they do not already exist.  Caller is responsible for
    closing the connection.

    Args:
        db_path: File path for the SQLite database.  Defaults to
            ``dashboard.db`` in the current working directory.

    Returns:
        An open :class:`sqlite3.Connection` with ``row_factory`` set to
        :class:`sqlite3.Row`.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker         TEXT    NOT NULL,
            shares         REAL    NOT NULL,
            purchase_price REAL    NOT NULL,
            purchase_date  TEXT,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker      TEXT    UNIQUE NOT NULL,
            alert_above REAL,
            alert_below REAL
        )
    """)
    conn.commit()
    return conn
