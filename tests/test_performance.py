import unittest
import pandas as pd
import numpy as np
from trading.backtest.performance import calculate_performance_metrics, calculate_trade_metrics

class TestPerformanceMetrics(unittest.TestCase):
    def setUp(self):
        # Create sample portfolio values
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        # Simulate a portfolio that grows from 100k to 120k with some volatility
        values = np.linspace(100000, 120000, len(dates))
        values = values * (1 + np.random.normal(0, 0.01, len(dates)))  # Add noise
        self.portfolio_values = pd.Series(values, index=dates)
    
    def test_empty_portfolio(self):
        """Test metrics calculation with empty portfolio"""
        empty_values = pd.Series(dtype=float)
        metrics = calculate_performance_metrics(empty_values)
        
        self.assertEqual(metrics["total_return"], 0.0)
        self.assertEqual(metrics["annualized_return"], 0.0)
        self.assertEqual(metrics["sharpe_ratio"], 0.0)
        self.assertEqual(metrics["max_drawdown"], 0.0)
        self.assertEqual(metrics["volatility"], 0.0)
        self.assertEqual(metrics["win_rate"], 0.0)
    
    def test_positive_performance(self):
        """Test metrics calculation with positive performance"""
        metrics = calculate_performance_metrics(self.portfolio_values)
        
        # Portfolio grew from 100k to ~120k
        self.assertGreater(metrics["total_return"], 15.0)  # Should be around 20%
        self.assertGreater(metrics["annualized_return"], 15.0)
        self.assertGreater(metrics["sharpe_ratio"], 0.0)
        self.assertGreater(metrics["volatility"], 0.0)
        self.assertLess(metrics["max_drawdown"], 100.0)
    
    def test_negative_performance(self):
        """Test metrics calculation with negative performance"""
        # Reverse the portfolio values to simulate losses
        losing_values = self.portfolio_values[::-1]
        metrics = calculate_performance_metrics(losing_values)
        
        self.assertLess(metrics["total_return"], 0.0)
        self.assertLess(metrics["annualized_return"], 0.0)
        self.assertLess(metrics["sharpe_ratio"], 0.0)
        self.assertGreater(metrics["max_drawdown"], 0.0)

class TestTradeMetrics(unittest.TestCase):
    def setUp(self):
        # Create sample trades
        self.trades = [
            {
                "timestamp": pd.Timestamp("2024-01-01"),
                "symbol": "TEST",
                "price": 100.0,
                "quantity": 100,
                "commission": 20.0
            },
            {
                "timestamp": pd.Timestamp("2024-01-02"),
                "symbol": "TEST",
                "price": 110.0,
                "quantity": -50,
                "commission": 11.0
            },
            {
                "timestamp": pd.Timestamp("2024-01-03"),
                "symbol": "TEST",
                "price": 105.0,
                "quantity": -50,
                "commission": 10.5
            }
        ]
    
    def test_empty_trades(self):
        """Test metrics calculation with no trades"""
        metrics = calculate_trade_metrics([])
        
        self.assertEqual(metrics["avg_trade_return"], 0.0)
        self.assertEqual(metrics["avg_trade_duration"], 0.0)
        self.assertEqual(metrics["profit_factor"], 0.0)
        self.assertEqual(metrics["avg_commission"], 0.0)
    
    def test_trade_metrics(self):
        """Test trade metrics calculation"""
        metrics = calculate_trade_metrics(self.trades)
        
        # Average commission should be (20 + 11 + 10.5) / 3
        self.assertAlmostEqual(metrics["avg_commission"], 13.83, places=2)
        
        # Trade duration should be 2 days
        self.assertAlmostEqual(metrics["avg_trade_duration"], 48.0, places=2)  # hours
        
        # Should have positive returns (bought at 100, sold at 110 and 105)
        self.assertGreater(metrics["avg_trade_return"], 0.0)
        self.assertGreater(metrics["profit_factor"], 1.0)

if __name__ == "__main__":
    unittest.main() 