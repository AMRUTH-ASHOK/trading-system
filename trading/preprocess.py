import pandas as pd
from pathlib import Path
import yaml

# Fix path resolution to point to the correct directories
FEATURE_DIR = Path(__file__).resolve().parents[1] / "data" / "features"
CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
FEATURE_DIR.mkdir(exist_ok=True, parents=True)

# Load settings
with open(CONFIG_DIR / "settings.yaml", "r") as f:
    settings = yaml.safe_load(f)

def transform(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Generate feature set aggregated to 60-minute bars with TA indicators."""
    import ta

    # Get technical analysis parameters from settings
    rsi_period = settings.get("rsi_period", 14)
    sma_fast_period = settings.get("sma_fast_period", 10)
    sma_slow_period = settings.get("sma_slow_period", 20)

    # Reset index for processing
    df = raw_df.reset_index()
    # Resample to hourly OHLCV per symbol
    feats = []
    for sym, grp in df.groupby("symbol"):
        grp = grp.set_index("timestamp").sort_index()
        hourly = grp.resample("1h").agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }).dropna()
        hourly["rsi"] = ta.momentum.rsi(hourly["close"], window=rsi_period, fillna=False)
        hourly["sma_fast"] = hourly["close"].rolling(sma_fast_period).mean()
        hourly["sma_slow"] = hourly["close"].rolling(sma_slow_period).mean()
        hourly["symbol"] = sym
        feats.append(hourly.dropna())
    feat_df = pd.concat(feats).reset_index().rename(columns={"index": "timestamp"})
    
    # Save as CSV
    fname = FEATURE_DIR / f"features_{pd.Timestamp.now():%Y%m%d%H%M}.csv"
    feat_df.to_csv(fname, index=False)
    print(f"[Preprocess] Saved features to {fname}")
    
    return feat_df
