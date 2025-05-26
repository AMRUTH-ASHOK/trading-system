"""Backtesting module for the trading system."""

from .engine import BacktestEngine
from .portfolio import Portfolio
from .performance import calculate_performance_metrics

__all__ = ['BacktestEngine', 'Portfolio', 'calculate_performance_metrics'] 