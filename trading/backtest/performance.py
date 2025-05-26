"""Performance metrics calculation for backtesting."""

import pandas as pd
import numpy as np
from typing import List, Dict

def calculate_performance_metrics(portfolio_values: pd.Series) -> Dict[str, float]:
    """Calculate key performance metrics from a series of portfolio values."""
    if len(portfolio_values) < 2:
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "win_rate": 0.0
        }
    
    # Calculate returns
    returns = portfolio_values.pct_change().dropna()
    
    # Total return
    total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
    
    # Annualized return (assuming daily data)
    days = (portfolio_values.index[-1] - portfolio_values.index[0]).days
    annualized_return = ((1 + total_return/100) ** (365/days) - 1) * 100 if days > 0 else 0
    
    # Volatility (annualized)
    volatility = returns.std() * np.sqrt(252) * 100
    
    # Sharpe ratio (assuming risk-free rate of 4%)
    risk_free_rate = 0.04
    excess_returns = returns - risk_free_rate/252
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std() if returns.std() > 0 else 0
    
    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.expanding().max()
    drawdowns = (cumulative - rolling_max) / rolling_max
    max_drawdown = abs(drawdowns.min()) * 100
    
    # Win rate
    win_rate = (returns > 0).mean() * 100
    
    return {
        "total_return": round(total_return, 2),
        "annualized_return": round(annualized_return, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown": round(max_drawdown, 2),
        "volatility": round(volatility, 2),
        "win_rate": round(win_rate, 2)
    }

def calculate_trade_metrics(trades: List[dict]) -> Dict[str, float]:
    """Calculate trade-specific metrics."""
    if not trades:
        return {
            "avg_trade_return": 0.0,
            "avg_trade_duration": 0.0,
            "profit_factor": 0.0,
            "avg_commission": 0.0
        }
    
    df = pd.DataFrame(trades)
    
    # Average trade return
    trade_returns = df.groupby("symbol").apply(lambda x: x["price"].pct_change()).dropna()
    avg_trade_return = trade_returns.mean() * 100
    
    # Average trade duration
    trade_durations = df.groupby("symbol").apply(
        lambda x: (x["timestamp"].max() - x["timestamp"].min()).total_seconds() / 3600
    )
    avg_trade_duration = trade_durations.mean()
    
    # Profit factor (absolute ratio of gains to losses)
    gains = trade_returns[trade_returns > 0].sum()
    losses = abs(trade_returns[trade_returns < 0].sum())
    profit_factor = gains / losses if losses != 0 else float('inf')
    
    # Average commission
    avg_commission = df["commission"].mean()
    
    return {
        "avg_trade_return": round(avg_trade_return, 2),
        "avg_trade_duration": round(avg_trade_duration, 2),
        "profit_factor": round(profit_factor, 2),
        "avg_commission": round(avg_commission, 2)
    } 