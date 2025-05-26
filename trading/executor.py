import yaml
from pathlib import Path
from typing import List
from .intelligence.rules import Signal
from .broker.fyers import FyersBroker
from .broker.mock import MockBroker

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _load_config():
    with open(CONFIG_DIR / "settings.yaml") as f:
        return yaml.safe_load(f)


def _get_broker():
    cfg = _load_config()
    if cfg.get("broker") == "fyers":
        return FyersBroker()
    return MockBroker()


def execute(signals: List[Signal]):
    if not signals:
        print("[Executor] No signals.")
        return
    broker = _get_broker()
    for s in signals:
        print(f"[Executor] Executing {s.side} on {s.symbol} (conf {s.confidence:.2f})")
        broker.place_order(symbol=s.symbol, side=s.side, qty=1)
