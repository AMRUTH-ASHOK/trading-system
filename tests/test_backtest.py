import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from trading.backtest.engine import BacktestEngine

class TestBacktestEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data and configuration"""
        # Create test data directory
        cls.test_data_dir = Path("data/test")
        cls.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate sample price data
        dates = pd.date_range(start="2024-01-01", end="2024-01-31", freq="1H")
        symbols = ["TEST1", "TEST2"]
        
        data = []
        for symbol in symbols:
            # Generate random walk prices
            prices = 100 * (1 + np.random.normal(0, 0.01, len(dates)).cumsum())
            prices = np.maximum(prices, 50)  # Ensure positive prices
            
            df = pd.DataFrame({
                "timestamp": dates,
                "symbol": symbol,
                "open": prices,
                "high": prices * 1.01,
                "low": prices * 0.99,
                "close": prices * (1 + np.random.normal(0, 0.001, len(dates))),
                "volume": np.random.randint(1000, 10000, len(dates))
            })
            data.append(df)
        
        # Combine and save test data
        combined_df = pd.concat(data)
        combined_df.to_csv(cls.test_data_dir / "test_data.csv", index=False)
        
        # Create test configuration
        cls.test_config = {
            "mode": "backtest",
            "backtest": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "initial_capital": 100000,
                "commission_rate": 0.002,
                "slippage": 0.0005
            },
            "symbols": symbols,
            "position_limit": 100,
            "notional_cap": 10000
        }
    
    def setUp(self):
        """Initialize backtest engine for each test"""
        self.engine = BacktestEngine()
        # Override settings for testing
        self.engine.settings = self.test_config
    
    def test_data_loading(self):
        """Test historical data loading"""
        data = self.engine.load_data("2024-01-01", "2024-01-31")
        
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data.index.get_level_values("symbol").unique()), 2)
        self.assertTrue(all(col in data.columns for col in ["open", "high", "low", "close", "volume"]))
    
    def test_backtest_execution(self):
        """Test full backtest execution"""
        data = self.engine.load_data("2024-01-01", "2024-01-31")
        results = self.engine.run(data, use_ml=False)
        
        # Check results structure
        self.assertIn("performance_metrics", results)
        self.assertIn("trade_metrics", results)
        self.assertIn("portfolio_summary", results)
        self.assertIn("signals", results)
        self.assertIn("portfolio_values", results)
        self.assertIn("trades", results)
        
        # Check performance metrics
        perf = results["performance_metrics"]
        self.assertIsInstance(perf["total_return"], float)
        self.assertIsInstance(perf["sharpe_ratio"], float)
        self.assertIsInstance(perf["max_drawdown"], float)
        
        # Check portfolio values
        self.assertGreater(len(results["portfolio_values"]), 0)
        self.assertTrue(all(isinstance(v["value"], (int, float)) for v in results["portfolio_values"]))
    
    def test_risk_limits(self):
        """Test that risk limits are respected"""
        data = self.engine.load_data("2024-01-01", "2024-01-31")
        results = self.engine.run(data, use_ml=False)
        
        # Check position limits
        position_sizes = [abs(t["quantity"]) for t in results["trades"]]
        self.assertTrue(all(size <= self.test_config["position_limit"] for size in position_sizes))
        
        # Check notional caps
        trade_values = [abs(t["quantity"] * t["price"]) for t in results["trades"]]
        self.assertTrue(all(value <= self.test_config["notional_cap"] for value in trade_values))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        import shutil
        shutil.rmtree(cls.test_data_dir)

if __name__ == "__main__":
    unittest.main() 