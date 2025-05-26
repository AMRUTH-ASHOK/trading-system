from typing import List
import pandas as pd
from . import rules, model as ml_model
from dataclasses import asdict
from pathlib import Path
import yaml

# Fix the path resolution to point to the correct config directory
CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

# Load settings
with open(CONFIG_DIR / "settings.yaml", "r") as f:
    settings = yaml.safe_load(f)

def predict(feat_df: pd.DataFrame, use_ml: bool = False) -> List[rules.Signal]:
    if use_ml:
        mdl = ml_model.load_model()
        proba = ml_model.predict_proba(mdl, feat_df)
        last_rows = feat_df.assign(confidence=proba).iloc[-len(proba):]
        sigs = []
        
        # Get ML thresholds from settings
        buy_threshold = settings.get("ml_confidence_buy_threshold", 0.55)
        sell_threshold = settings.get("ml_confidence_sell_threshold", 0.45)
        
        for _, row in last_rows.iterrows():
            side = "BUY" if row.confidence > buy_threshold else "SELL" if row.confidence < sell_threshold else None
            if side:
                sigs.append(rules.Signal(symbol=row.symbol, side=side, confidence=float(row.confidence), timestamp=row.timestamp))
        return sigs
    else:
        return rules.generate_signals(feat_df)
