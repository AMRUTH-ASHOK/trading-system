from dataclasses import dataclass
import pandas as pd
from typing import List
from pathlib import Path
import yaml

# Fix path resolution to point to the correct config directory
CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

# Load settings
with open(CONFIG_DIR / "settings.yaml", "r") as f:
    settings = yaml.safe_load(f)

@dataclass
class Signal:
    symbol: str
    side: str  # "BUY" | "SELL"
    confidence: float
    timestamp: pd.Timestamp


def generate_signals(feat_df: pd.DataFrame) -> List[Signal]:
    """Very simple SMA crossover rule."""
    signals: List[Signal] = []
    default_confidence = settings.get("default_signal_confidence", 0.6)  # Use configured value or default
    
    for sym, grp in feat_df.groupby("symbol"):
        if len(grp) < 2:
            continue
        last = grp.iloc[-1]
        prev = grp.iloc[-2]
        # bullish crossover
        if prev["sma_fast"] < prev["sma_slow"] and last["sma_fast"] > last["sma_slow"]:
            signals.append(Signal(symbol=sym, side="BUY", confidence=default_confidence, timestamp=last["timestamp"]))
        # bearish crossover
        if prev["sma_fast"] > prev["sma_slow"] and last["sma_fast"] < last["sma_slow"]:
            signals.append(Signal(symbol=sym, side="SELL", confidence=default_confidence, timestamp=last["timestamp"]))
    return signals
