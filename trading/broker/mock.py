from pathlib import Path
import sqlite3
import datetime as dt

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "orders.sqlite"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _init():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                symbol TEXT,
                side TEXT,
                qty INTEGER
            )"""
        )

_init()


class MockBroker:
    def place_order(self, symbol: str, side: str, qty: int = 1):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO orders (ts, symbol, side, qty) VALUES (?,?,?,?)",
                (dt.datetime.now().isoformat(), symbol, side, qty),
            )
        print(f"[MOCK] {side} {qty} {symbol}")
        return {"status": "ok"}
