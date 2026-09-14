import os
import time
from datetime import datetime, timedelta, timezone

import requests

try:
    import yfinance as yf
except ImportError:
    yf = None



class MarketDataProvider:
    """Abstract interface for financial data providers."""

    def search(self, query: str):
        raise NotImplementedError

    def quote(self, symbol: str):
        raise NotImplementedError

    def history(self, symbol: str, range_name: str = "1M", interval: str = "1D"):
        raise NotImplementedError


class FinnhubProvider(MarketDataProvider):
    base_url = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("MARKET_API_KEY", "")
        self.session = requests.Session()

    def _require_key(self):
        if not self.api_key:
            raise ValueError(
                "MARKET_API_KEY is not configured. Set it in Docker or your environment before using market data."
            )

    def _request(self, endpoint: str, params: dict | None = None):
        self._require_key()
        payload = {"token": self.api_key}
        if params:
            payload.update(params)

        response = self.session.get(f"{self.base_url}{endpoint}", params=payload, timeout=15)
        response.raise_for_status()
        return response.json()

    def search(self, query: str):
        if not query or not query.strip():
            return []

        data = self._request("/search", {"q": query.strip()})
        results = data.get("result", [])
        normalized = []

        for item in results[:8]:
            symbol = item.get("symbol", "").strip()
            description = item.get("description") or item.get("displaySymbol") or symbol
            if not symbol:
                continue
            normalized.append(
                {
                    "symbol": symbol,
                    "name": description,
                    "type": item.get("type") or "unknown",
                    "exchange": item.get("exchange") or "",
                }
            )

        return normalized

    def quote(self, symbol: str):
        symbol = symbol.strip().upper()
        payload = self._request("/quote", {"symbol": symbol})

        if not payload:
            raise ValueError(f"No quote available for {symbol}.")

        price = payload.get("c")
        previous_close = payload.get("pc")
        change = payload.get("d")
        change_percent = payload.get("dp")

        if price is None and previous_close is None:
            raise ValueError(f"Symbol unavailable or market is closed: {symbol}")

        return {
            "symbol": symbol,
            "price": price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_percent,
            "market_status": "open" if payload.get("t") else "closed",
        }

    def _range_to_resolution(self, range_name: str, interval: str | None = None):
        key = (range_name or "1M").upper()
        if key == "1D":
            return "5"
        if key == "5D":
            return "30"
        if key == "1M":
            return "60"
        if key == "3M":
            return "D"
        if key == "6M":
            return "D"
        if key == "1Y":
            return "W"
        if key == "5Y":
            return "W"
        if key == "MAX":
            return "M"
        if interval:
            return interval
        return "D"

    def _range_to_from(self, range_name: str):
        now = datetime.now(timezone.utc)
        step = {
            "1D": timedelta(days=1),
            "5D": timedelta(days=5),
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "6M": timedelta(days=180),
            "1Y": timedelta(days=365),
            "5Y": timedelta(days=1825),
            "MAX": timedelta(days=3650),
        }.get((range_name or "1M").upper(), timedelta(days=30))
        return int((now - step).timestamp())

    def history(self, symbol: str, range_name: str = "1M", interval: str = "1D"):
        symbol = symbol.strip().upper()
        resolution = self._range_to_resolution(range_name, interval)
        from_ts = self._range_to_from(range_name)
        to_ts = int(time.time())

        data = self._request(
            "/stock/candle",
            {
                "symbol": symbol,
                "resolution": resolution,
                "from": from_ts,
                "to": to_ts,
            },
        )

        status = data.get("s")
        if status != "ok":
            return {"symbol": symbol, "candles": [], "error": "No candle data available for this symbol."}

        candles = []
        timestamps = data.get("t", [])
        opens = data.get("o", [])
        highs = data.get("h", [])
        lows = data.get("l", [])
        closes = data.get("c", [])
        volumes = data.get("v", [])

        for index, ts in enumerate(timestamps):
            candles.append(
                {
                    "time": int(ts),
                    "open": opens[index] if index < len(opens) else None,
                    "high": highs[index] if index < len(highs) else None,
                    "low": lows[index] if index < len(lows) else None,
                    "close": closes[index] if index < len(closes) else None,
                    "volume": volumes[index] if index < len(volumes) else 0,
                }
            )

        return {"symbol": symbol, "candles": candles}


class YFinanceProvider(MarketDataProvider):
    """Market data provider using yfinance (free, no API key required)."""

    def __init__(self):
        if not yf:
            raise ImportError("yfinance is not installed. Install it with: pip install yfinance")

    def search(self, query: str):
        """Search is not supported by yfinance, return empty."""
        if not query or not query.strip():
            return []
        return []

    def quote(self, symbol: str):
        symbol = symbol.strip().upper()
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or "currentPrice" not in info:
                raise ValueError(f"No data available for {symbol}")
            
            price = info.get("currentPrice")
            previous_close = info.get("previousClose")
            change = price - previous_close if price and previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return {
                "symbol": symbol,
                "price": price,
                "previous_close": previous_close,
                "change": change,
                "change_percent": change_percent,
                "market_status": "open",
            }
        except Exception as exc:
            raise ValueError(f"Could not fetch quote for {symbol}: {str(exc)}")

    def _range_to_period(self, range_name: str):
        """Convert range name to yfinance period."""
        key = (range_name or "1M").upper()
        mapping = {
            "1D": "1d",
            "5D": "5d",
            "1M": "1mo",
            "3M": "3mo",
            "6M": "6mo",
            "1Y": "1y",
            "5Y": "5y",
            "MAX": "max",
        }
        return mapping.get(key, "1mo")

    def _range_to_interval(self, range_name: str):
        """Convert range name to yfinance interval."""
        key = (range_name or "1M").upper()
        mapping = {
            "1D": "15m",   # 15-minute bars for 1 day
            "5D": "1h",    # 1-hour bars for 5 days
            "1M": "1d",    # Daily bars for 1 month
            "3M": "1d",    # Daily bars for 3 months
            "6M": "1d",    # Daily bars for 6 months
            "1Y": "1wk",   # Weekly bars for 1 year
            "5Y": "1wk",   # Weekly bars for 5 years
            "MAX": "1mo",  # Monthly bars for max
        }
        return mapping.get(key, "1d")

    def history(self, symbol: str, range_name: str = "1M", interval: str = "1D"):
        symbol = symbol.strip().upper()
        period = self._range_to_period(range_name)
        interval_val = self._range_to_interval(range_name)
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval_val)
            
            if hist.empty:
                return {"symbol": symbol, "candles": [], "error": f"No data available for {symbol}"}
            
            candles = []
            for idx, row in hist.iterrows():
                candles.append(
                    {
                        "time": int(idx.timestamp()),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": int(row["Volume"]),
                    }
                )
            
            return {"symbol": symbol, "candles": candles}
        except Exception as exc:
            return {"symbol": symbol, "candles": [], "error": f"Failed to fetch data: {str(exc)}"}


def create_market_provider():
    provider_name = os.getenv("MARKET_PROVIDER", "yfinance").lower()
    
    if provider_name == "finnhub":
        return FinnhubProvider()
    elif provider_name == "yfinance":
        return YFinanceProvider()
    else:
        # Default to yfinance
        return YFinanceProvider()


