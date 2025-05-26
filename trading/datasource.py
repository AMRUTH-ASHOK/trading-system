import os
import datetime as dt
from pathlib import Path
from typing import List
import pandas as pd

try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None  # allows unit tests without dep

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def _load_secrets() -> dict:
    import yaml
    with open(CONFIG_DIR / "secrets.yaml", "r") as f:
        return yaml.safe_load(f)


def _get_fyers_client():
    secrets = _load_secrets()
    if fyersModel is None:
        raise ImportError("Install fyers-apiv3 for live data: pip install fyers-apiv3")
    fyers = fyersModel.FyersModel(client_id=secrets["client_id"], token=secrets["access_token"], is_async=False)
    return fyers


def fetch(symbols: List[str] = None, lookback_hours: int = None) -> pd.DataFrame:
    """Fetch OHLCV minute bars for the past lookback_hours for each symbol."""
    import yaml
    # Load settings
    with open(CONFIG_DIR / "settings.yaml") as f:
        cfg = yaml.safe_load(f)
    
    # Get symbols and lookback_hours from config
    if symbols is None:
        symbols = cfg["symbols"]
    if lookback_hours is None:
        lookback_hours = cfg.get("lookback_hours", 24)  # default to 24 if not specified
    
    # Calculate date range for historical data
    end = dt.datetime.now()
    start = end - dt.timedelta(hours=lookback_hours)
    
    # Ensure we're not requesting future data and use only dates
    if end.date() > dt.datetime.now().date():
        end = dt.datetime.now()
        start = end - dt.timedelta(hours=lookback_hours)
    
    print(f"[DataSource] Fetching data from {start.date()} to {end.date()} (lookback: {lookback_hours} hours)")
    
    data_frames = []
    fyers = _get_fyers_client()

    for sym in symbols:
        try:
            # Fyers history endpoint: max 60 days, resolution 1 data
            resp = fyers.history({
                "symbol": sym,
                "resolution": "1",
                "date_format": "1",
                "range_from": start.date().strftime("%Y-%m-%d"),
                "range_to": end.date().strftime("%Y-%m-%d"),
                "cont_flag": "1"
            })
            if isinstance(resp, dict):
                if resp.get("s") == "ok" and resp.get("candles"):
                    df = pd.DataFrame(resp["candles"], columns=["timestamp", "open", "high", "low", "close", "volume"])
                    df["symbol"] = sym
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                    data_frames.append(df)
                elif resp.get("s") == "no_data":
                    print(f"[DataSource] No data available for {sym} in the specified date range")
                else:
                    print(f"[DataSource] Invalid response for {sym}: {resp}")
        except Exception as exc:
            print(f"[DataSource] Failed to fetch {sym}: {exc}")
    
    if not data_frames:
        raise RuntimeError("No data fetched!")
    
    df_all = pd.concat(data_frames).set_index(["timestamp", "symbol"]).sort_index()
    # Save as CSV
    fname = RAW_DIR / f"raw_{end:%Y%m%d%H%M}.csv"
    df_all.to_csv(fname)
    print(f"[DataSource] Saved raw data to {fname}")
    return df_all
