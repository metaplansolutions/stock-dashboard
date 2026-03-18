import pandas as pd
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent / "sample_data"


def get_price_history(ticker: str, period: str = "1mo", demo_mode: bool = False) -> pd.DataFrame:
    """Return OHLCV price history for a ticker.

    Args:
        ticker: Stock symbol (e.g. 'AAPL').
        period: yfinance period string (e.g. '1mo', '5d').
        demo_mode: If True, use bundled sample CSV instead of live API.

    Returns:
        DataFrame indexed by date with columns: open, high, low, close, volume.
        Returns empty DataFrame on failure.
    """
    if demo_mode:
        return _load_sample(ticker)
    try:
        import yfinance as yf
        data = yf.Ticker(ticker).history(period=period)
        data.columns = [c.lower().replace(" ", "_") for c in data.columns]
        return data
    except Exception:
        return _load_sample(ticker)


def get_current_price(ticker: str, demo_mode: bool = False) -> float:
    """Return most recent closing price for a ticker.

    Returns 0.0 if no data is available.
    """
    df = get_price_history(ticker, period="5d", demo_mode=demo_mode)
    if df.empty:
        return 0.0
    return float(df["close"].iloc[-1])


def _load_sample(ticker: str) -> pd.DataFrame:
    """Load from bundled sample CSV; returns empty DataFrame if ticker not found."""
    csv_path = SAMPLE_DIR / "prices.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df[df["ticker"] == ticker].copy()
    if df.empty:
        return pd.DataFrame()
    df = df.set_index("date").sort_index()
    return df
