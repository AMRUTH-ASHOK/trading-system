"""Backtesting engine for the trading system."""

import pandas as pd
from datetime import datetime
from pathlib import Path
import yaml
from typing import List, Dict, Optional
from ..intelligence import predict
from .portfolio import Portfolio
from .performance import calculate_performance_metrics, calculate_trade_metrics

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"

class BacktestEngine:
    def __init__(self):
        # Load settings
        with open(CONFIG_DIR / "settings.yaml", "r") as f:
            self.settings = yaml.safe_load(f)
            self.backtest_settings = self.settings.get("backtest", {})
        
        # Initialize portfolio
        self.portfolio = Portfolio(
            initial_capital=self.backtest_settings.get("initial_capital", 1000000),
            commission_rate=self.backtest_settings.get("commission_rate", 0.0020),
            slippage=self.backtest_settings.get("slippage", 0.0005)
        )
        
        # Initialize containers for results
        self.signals: List[dict] = []
        self.portfolio_values: List[dict] = []
    
    def run(self, data: pd.DataFrame, use_ml: bool = False) -> dict:
        """Run backtest on historical data."""
        # Ensure data is sorted
        data = data.sort_index()
        
        # Track portfolio value over time
        current_prices = {}
        
        # Process each timestamp
        for timestamp, group in data.groupby(level="timestamp"):
            # Update current prices
            for symbol, row in group.iterrows():
                current_prices[symbol[1]] = row["close"]
            
            # Generate signals
            signals = predict(group, use_ml=use_ml)
            
            # Execute trades based on signals
            for signal in signals:
                # Determine position size
                price = current_prices[signal.symbol]
                position_value = min(
                    self.portfolio.cash * 0.1,  # Use max 10% of portfolio per trade
                    self.settings["notional_cap"]  # Respect notional cap
                )
                quantity = int(position_value / price)
                
                if quantity > 0:
                    # Adjust quantity based on signal side
                    if signal.side == "SELL":
                        quantity = -quantity
                    
                    # Execute trade
                    self.portfolio.execute_trade(
                        symbol=signal.symbol,
                        quantity=quantity,
                        price=price,
                        timestamp=signal.timestamp
                    )
                    
                    # Record signal
                    self.signals.append({
                        "timestamp": signal.timestamp,
                        "symbol": signal.symbol,
                        "side": signal.side,
                        "confidence": signal.confidence,
                        "price": price,
                        "quantity": quantity
                    })
            
            # Record portfolio value
            self.portfolio_values.append({
                "timestamp": timestamp,
                "value": self.portfolio.get_total_value(current_prices)
            })
        
        # Calculate performance metrics
        portfolio_value_series = pd.Series(
            [v["value"] for v in self.portfolio_values],
            index=pd.DatetimeIndex([v["timestamp"] for v in self.portfolio_values])
        )
        
        performance_metrics = calculate_performance_metrics(portfolio_value_series)
        trade_metrics = calculate_trade_metrics(self.portfolio.trades)
        portfolio_summary = self.portfolio.get_performance_summary()
        
        return {
            "performance_metrics": performance_metrics,
            "trade_metrics": trade_metrics,
            "portfolio_summary": portfolio_summary,
            "signals": self.signals,
            "portfolio_values": self.portfolio_values,
            "trades": self.portfolio.trades
        }
    
    @staticmethod
    def load_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Load historical data for backtesting."""
        # Use settings if dates not provided
        if start_date is None:
            start_date = BacktestEngine.settings.get("backtest", {}).get("start_date")
        if end_date is None:
            end_date = BacktestEngine.settings.get("backtest", {}).get("end_date")
        
        if not start_date or not end_date:
            raise ValueError("Start date and end date must be provided either in settings or as parameters")
        
        # Convert dates to datetime
        start_dt = pd.Timestamp(start_date)
        end_dt = pd.Timestamp(end_date)
        
        # Load data from CSV files in the raw directory
        raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
        dfs = []
        
        for file in raw_dir.glob("*.csv"):
            df = pd.read_csv(file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df[(df["timestamp"] >= start_dt) & (df["timestamp"] <= end_dt)]
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            raise ValueError(f"No data found between {start_date} and {end_date}")
        
        # Combine all data
        combined_df = pd.concat(dfs)
        
        # Set multi-index
        combined_df = combined_df.set_index(["timestamp", "symbol"]).sort_index()
        
        return combined_df 