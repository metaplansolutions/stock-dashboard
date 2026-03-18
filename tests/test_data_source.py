import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_source import get_price_history, get_current_price


def test_get_price_history_sample_mode():
    df = get_price_history("AAPL", period="1mo", demo_mode=True)
    assert len(df) > 0
    assert "close" in df.columns


def test_get_current_price_sample_mode():
    price = get_current_price("AAPL", demo_mode=True)
    assert isinstance(price, float)
    assert price > 0


def test_get_price_history_all_tickers():
    for ticker in ["AAPL", "NVDA", "MSFT"]:
        df = get_price_history(ticker, period="1mo", demo_mode=True)
        assert len(df) > 0, f"No data for {ticker}"
        assert "close" in df.columns


def test_get_price_history_unknown_ticker_returns_empty():
    df = get_price_history("ZZZZ", period="1mo", demo_mode=True)
    assert df.empty


def test_get_current_price_unknown_returns_zero():
    price = get_current_price("ZZZZ", demo_mode=True)
    assert price == 0.0
