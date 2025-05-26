from typing import Dict
import json
from pathlib import Path

try:
    from fyers_apiv3 import fyersModel
except ImportError:
    fyersModel = None

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def _load_secrets() -> Dict:
    import yaml
    with open(CONFIG_DIR / "secrets.yaml", "r") as f:
        return yaml.safe_load(f)


class FyersBroker:
    def __init__(self):
        if fyersModel is None:
            raise ImportError("Install fyers-apiv3 to use FyersBroker")
        sec = _load_secrets()
        self.client = fyersModel.FyersModel(client_id=sec["client_id"], token=sec["access_token"], is_async=False)

    def place_order(self, symbol: str, side: str, qty: int = 1):
        side_num = 1 if side == "BUY" else -1
        order = {
            "symbol": symbol,
            "qty": qty,
            "type": 2,  # market
            "side": side_num,
            "productType": "CNC",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
        }
        resp = self.client.place_order(order)
        print("[FYERS] Order resp", json.dumps(resp, indent=2))
        return resp
