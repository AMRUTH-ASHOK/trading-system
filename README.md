# Trading System

A configurable and extensible trading system that supports both live trading and backtesting capabilities.

## Features

### 1. Dual Mode Operation
- **Live Trading**: Real-time market data processing and trade execution
- **Backtesting**: Historical data analysis with comprehensive performance metrics

### 2. Configurable Settings
All system parameters are configurable through `config/settings.yaml`:
- Trading parameters (symbols, position limits, notional caps)
- Technical analysis parameters
- ML model parameters
- UI customization
- Backtesting parameters

### 3. Core Components

#### Live Trading Pipeline
1. **Data Source**: Real-time market data fetching
2. **Preprocessing**: Technical feature computation
3. **Intelligence**: Signal generation (rule-based and ML-based)
4. **Execution**: Trade execution through configured broker

#### Backtesting System
1. **Portfolio Management**: Position tracking and P&L calculation
2. **Performance Analytics**: 
   - Total and annualized returns
   - Sharpe ratio
   - Maximum drawdown
   - Volatility
   - Win rate
3. **Trade Analytics**:
   - Average trade return
   - Trade duration metrics
   - Profit factor
   - Commission impact

### 4. Configuration Options

```yaml
# Mode Selection
mode: "live" | "backtest"

# Backtest Settings
backtest:
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"
  initial_capital: 1000000
  commission_rate: 0.0020
  slippage: 0.0005

# Trading Parameters
symbols: ["NSE:RELIANCE-EQ", "NSE:TCS-EQ"]
lookback_hours: 480
position_limit: 100
notional_cap: 100000
schedule: "cron:* * * * *"
broker: "fyers" | "mock"

# Technical Analysis
sma_fast_period: 10
sma_slow_period: 20
rsi_period: 14

# ML Parameters
ml_confidence_buy_threshold: 0.55
ml_confidence_sell_threshold: 0.45
```

## Directory Structure

```
trading-system/
├── config/
│   └── settings.yaml       # System configuration
├── trading/
│   ├── backtest/          # Backtesting components
│   ├── datasource/        # Market data handling
│   ├── intelligence/      # Signal generation
│   ├── preprocess/        # Feature computation
│   ├── executor/          # Trade execution
│   └── utils/             # Utility functions
├── data/
│   └── raw/               # Historical data for backtesting
└── main.py                # System entry point
```

## Usage

1. Configure the system through `config/settings.yaml`
2. Run in live mode:
   ```python
   python -m trading.main
   ```
3. Run in backtest mode:
   - Set `mode: "backtest"` in settings.yaml
   - Configure backtest parameters
   - Run the same command

## Performance Tracking

The system maintains detailed logs and tracks:
- Pipeline execution IDs
- Raw data snapshots
- Generated features
- Trading signals
- Execution results
- Performance metrics

## UI Customization

The UI is fully configurable through settings.yaml:
- Chart dimensions and colors
- Font sizes and weights
- Color scheme
- Layout parameters
- Component styling

## System Overview

When you run `python -m trading.main`, the system operates as follows:

### 1. Program Initialization
- Loads `main.py` script
- Processes required imports (yaml, BackgroundScheduler, local modules)
- Executes `main()` function

### 2. Configuration Loading
Reads `config/settings.yaml` containing:
- Trading symbols (["NSE:RELIANCE", "NSE:TCS"])
- Lookback period (24 hours)
- Position limits (100 shares)
- Schedule ("cron:0 * * * *" - runs every hour)
- Broker choice ("fyers" or "mock")

### 3. Scheduler Setup
- Creates BackgroundScheduler instance
- Parses cron expression from settings
- Schedules `pipeline()` function to run every hour
- Starts the scheduler

### 4. Trading Pipeline
Each scheduler trigger executes these steps:

#### a. Data Fetching (`datasource.fetch()`)
```python
- Loads broker credentials from secrets.yaml
- Connects to Fyers API
- For each symbol (RELIANCE, TCS):
  - Fetches last 24 hours of minute-by-minute data
  - Gets OHLCV (Open, High, Low, Close, Volume) data
- Saves raw data to data/raw/raw_YYYYMMDDHHMM.parquet
```

#### b. Feature Engineering (`preprocess.transform()`)
```python
- Takes raw minute data
- Resamples to hourly bars
- Calculates technical indicators:
  - RSI (Relative Strength Index)
  - SMA Fast (10-period Simple Moving Average)
  - SMA Slow (30-period Simple Moving Average)
- Saves features to data/features/features_YYYYMMDDHHMM.parquet
```

#### c. Signal Generation (`intelligence.predict()`)
```python
- If use_ml=False (default):
  - Uses rules.generate_signals():
    - Checks for SMA crossovers
    - Generates BUY signal when fast SMA crosses above slow SMA
    - Generates SELL signal when fast SMA crosses below slow SMA
    - Each signal includes: symbol, side (BUY/SELL), confidence (0.6), timestamp
- If use_ml=True:
  - Would use trained ML model to predict trading signals
```

#### d. Order Execution (`executor.execute()`)
```python
- For each trading signal:
  - Gets broker instance (Fyers or Mock) based on settings
  - If using FyersBroker:
    - Places real market orders via Fyers API
  - If using MockBroker:
    - Records paper trades in SQLite database (data/orders.sqlite)
  - Logs execution details
```

### 5. Continuous Operation
- Program runs indefinitely, with scheduler triggering pipeline every hour
- Can be stopped with Ctrl+C
- All data is saved to disk for analysis:
  - Raw market data in `data/raw/`
  - Feature data in `data/features/`
  - Mock trades in `data/orders.sqlite`

### 6. Optional Dashboard
Running `streamlit run streamlit_app.py` provides a web interface showing:
- Latest feature calculations
- Recent paper trades (if using mock broker)

## System Architecture

The system follows a typical algorithmic trading pipeline:
```
Data → Features → Signals → Execution
```

It's designed to either paper trade (mock broker) or live trade (Fyers), depending on configuration in `settings.yaml`. 