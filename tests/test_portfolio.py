import unittest
import pandas as pd
from trading.backtest.portfolio import Portfolio, Position

class TestPosition(unittest.TestCase):
    def setUp(self):
        self.position = Position(symbol="TEST")
    
    def test_new_position(self):
        """Test opening a new position"""
        self.position.update(qty=100, price=10.0)
        self.assertEqual(self.position.quantity, 100)
        self.assertEqual(self.position.avg_price, 10.0)
        self.assertEqual(self.position.realized_pnl, 0.0)
    
    def test_add_to_position(self):
        """Test adding to an existing position"""
        self.position.update(qty=100, price=10.0)
        self.position.update(qty=50, price=12.0)
        self.assertEqual(self.position.quantity, 150)
        self.assertAlmostEqual(self.position.avg_price, 10.67, places=2)
    
    def test_reduce_position(self):
        """Test partially closing a position"""
        self.position.update(qty=100, price=10.0)
        self.position.update(qty=-50, price=15.0)
        self.assertEqual(self.position.quantity, 50)
        self.assertEqual(self.position.avg_price, 10.0)
        self.assertAlmostEqual(self.position.realized_pnl, 250.0)  # (15-10) * 50
    
    def test_close_position(self):
        """Test completely closing a position"""
        self.position.update(qty=100, price=10.0)
        self.position.update(qty=-100, price=15.0)
        self.assertEqual(self.position.quantity, 0)
        self.assertAlmostEqual(self.position.realized_pnl, 500.0)  # (15-10) * 100

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio(
            initial_capital=100000,
            commission_rate=0.002,
            slippage=0.0005
        )
    
    def test_initial_state(self):
        """Test portfolio initialization"""
        self.assertEqual(self.portfolio.cash, 100000)
        self.assertEqual(len(self.portfolio.positions), 0)
        self.assertEqual(len(self.portfolio.trades), 0)
    
    def test_execute_trade(self):
        """Test trade execution with commission and slippage"""
        timestamp = pd.Timestamp("2024-01-01")
        self.portfolio.execute_trade("TEST", 100, 10.0, timestamp)
        
        # Check position
        position = self.portfolio.get_position("TEST")
        self.assertEqual(position.quantity, 100)
        self.assertGreater(position.avg_price, 10.0)  # Due to slippage
        
        # Check cash (price + slippage + commission)
        expected_price = 10.0 * (1 + self.portfolio.slippage)
        expected_commission = expected_price * 100 * self.portfolio.commission_rate
        expected_cash = 100000 - (expected_price * 100 + expected_commission)
        self.assertAlmostEqual(self.portfolio.cash, expected_cash, places=2)
    
    def test_portfolio_value(self):
        """Test portfolio value calculation"""
        # Execute some trades
        timestamp = pd.Timestamp("2024-01-01")
        self.portfolio.execute_trade("TEST1", 100, 10.0, timestamp)
        self.portfolio.execute_trade("TEST2", 50, 20.0, timestamp)
        
        # Calculate total value
        current_prices = {"TEST1": 12.0, "TEST2": 22.0}
        total_value = self.portfolio.get_total_value(current_prices)
        
        # Position values: TEST1 = 100 * 12.0 = 1200, TEST2 = 50 * 22.0 = 1100
        position_value = 1200 + 1100
        expected_total = self.portfolio.cash + position_value
        self.assertAlmostEqual(total_value, expected_total, places=2)
    
    def test_performance_summary(self):
        """Test performance summary calculation"""
        # Execute trades
        timestamp = pd.Timestamp("2024-01-01")
        self.portfolio.execute_trade("TEST", 100, 10.0, timestamp)
        self.portfolio.execute_trade("TEST", -100, 15.0, timestamp)
        
        summary = self.portfolio.get_performance_summary()
        self.assertGreater(summary["realized_pnl"], 0)
        self.assertEqual(summary["total_trades"], 2)
        self.assertGreater(summary["total_commission"], 0)

if __name__ == "__main__":
    unittest.main() 