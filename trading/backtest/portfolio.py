"""Portfolio management for backtesting."""

from dataclasses import dataclass, field
from typing import Dict, List
import pandas as pd
from pathlib import Path
import yaml

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

# Load settings
with open(CONFIG_DIR / "settings.yaml", "r") as f:
    settings = yaml.safe_load(f)
    backtest_settings = settings.get("backtest", {})

@dataclass
class Position:
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0
    realized_pnl: float = 0.0
    
    def update(self, qty: int, price: float, commission: float = 0.0):
        """Update position with a new trade."""
        if self.quantity == 0:  # New position
            self.quantity = qty
            self.avg_price = price
        else:  # Existing position
            if (self.quantity > 0 and qty < 0) or (self.quantity < 0 and qty > 0):
                # Closing or reducing position
                close_qty = min(abs(self.quantity), abs(qty))
                self.realized_pnl += (price - self.avg_price) * close_qty * (1 if self.quantity > 0 else -1)
                self.quantity += qty
                if self.quantity != 0:  # Position still open
                    self.avg_price = price
            else:  # Adding to position
                self.avg_price = (self.avg_price * self.quantity + price * qty) / (self.quantity + qty)
                self.quantity += qty
        
        # Deduct commission
        self.realized_pnl -= commission

@dataclass
class Portfolio:
    initial_capital: float = backtest_settings.get("initial_capital", 1000000)
    commission_rate: float = backtest_settings.get("commission_rate", 0.0020)
    slippage: float = backtest_settings.get("slippage", 0.0005)
    cash: float = field(init=False)
    positions: Dict[str, Position] = field(default_factory=dict)
    trades: List[dict] = field(default_factory=list)
    
    def __post_init__(self):
        self.cash = self.initial_capital
    
    def get_position(self, symbol: str) -> Position:
        """Get or create position for symbol."""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]
    
    def execute_trade(self, symbol: str, quantity: int, price: float, timestamp: pd.Timestamp):
        """Execute a trade and update portfolio."""
        # Apply slippage
        executed_price = price * (1 + self.slippage if quantity > 0 else 1 - self.slippage)
        
        # Calculate commission
        commission = abs(quantity * executed_price * self.commission_rate)
        
        # Update position
        position = self.get_position(symbol)
        position.update(quantity, executed_price, commission)
        
        # Update cash
        trade_value = quantity * executed_price
        self.cash -= (trade_value + commission)
        
        # Record trade
        self.trades.append({
            "timestamp": timestamp,
            "symbol": symbol,
            "quantity": quantity,
            "price": executed_price,
            "commission": commission,
            "cash": self.cash
        })
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value including cash and positions."""
        position_value = sum(
            pos.quantity * current_prices.get(pos.symbol, pos.avg_price)
            for pos in self.positions.values()
        )
        return self.cash + position_value
    
    def get_performance_summary(self) -> dict:
        """Get summary of portfolio performance."""
        if not self.trades:
            return {
                "total_trades": 0,
                "total_commission": 0.0,
                "realized_pnl": 0.0,
                "ending_cash": self.cash,
                "return_pct": 0.0
            }
        
        total_commission = sum(trade["commission"] for trade in self.trades)
        realized_pnl = sum(pos.realized_pnl for pos in self.positions.values())
        return_pct = (self.cash - self.initial_capital) / self.initial_capital * 100
        
        return {
            "total_trades": len(self.trades),
            "total_commission": total_commission,
            "realized_pnl": realized_pnl,
            "ending_cash": self.cash,
            "return_pct": return_pct
        } 