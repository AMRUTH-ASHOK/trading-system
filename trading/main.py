import yaml
import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from . import datasource, preprocess, intelligence, executor
from .utils.logging_utils import get_logger, get_pipeline_context
from .utils.pipeline_tracker import PipelineTracker
from .backtest import BacktestEngine

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
logger = get_logger(__name__)


def _load_config():
    with open(CONFIG_DIR / "settings.yaml") as f:
        config = yaml.safe_load(f)
    logger.debug(f"Loaded settings: {config}")
    return config


def pipeline():
    """Execute one iteration of the trading pipeline"""
    # Reset pipeline context for new run
    get_pipeline_context().reset()
    tracker = PipelineTracker()
    logger.info(f"Starting pipeline {tracker.pipeline_id}")
    
    try:
        # Step 1: Fetch market data
        logger.info("Step 1: Fetching market data...")
        raw = datasource.fetch()
        tracker.save_raw_data(raw)
        logger.info(f"✓ Fetched data for {len(raw.index.get_level_values('symbol').unique())} symbols")
        
        # Step 2: Compute technical features
        logger.info("Step 2: Computing technical features...")
        feats = preprocess.transform(raw)
        tracker.save_features(feats)
        logger.info(f"✓ Generated {len([c for c in feats.columns if c not in ['timestamp', 'symbol']])} features")
        
        # Step 3: Generate trading signals
        logger.info("Step 3: Generating trading signals...")
        signals = intelligence.predict(feats, use_ml=False)
        for sig in signals:
            tracker.add_signal({
                "timestamp": sig.timestamp.isoformat(),
                "symbol": sig.symbol,
                "side": sig.side,
                "confidence": sig.confidence
            })
        logger.info(f"✓ Generated {len(signals)} trading signals")
        
        # Step 4: Execute trades
        logger.info("Step 4: Executing trades...")
        for sig in signals:
            try:
                resp = executor.execute([sig])
                tracker.add_trade({
                    "signal": {
                        "timestamp": sig.timestamp.isoformat(),
                        "symbol": sig.symbol,
                        "side": sig.side
                    },
                    "execution": resp
                })
            except Exception as e:
                logger.error(f"Failed to execute trade for {sig.symbol}: {e}")
        logger.info("✓ Trade execution complete")
        
        tracker.complete_pipeline()
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        tracker.fail_pipeline(str(e))
        raise


def run_backtest(start_date: str = None, end_date: str = None, use_ml: bool = False) -> dict:
    """Run backtest mode with historical data."""
    logger.info("Starting backtest mode...")
    
    try:
        # Initialize backtest engine
        engine = BacktestEngine()
        
        # Load historical data
        logger.info("Loading historical data...")
        data = engine.load_data(start_date, end_date)
        logger.info(f"Loaded data for {len(data.index.get_level_values('symbol').unique())} symbols")
        
        # Run backtest
        logger.info("Running backtest...")
        results = engine.run(data, use_ml=use_ml)
        
        # Log summary
        logger.info("Backtest complete. Summary:")
        logger.info(f"Total Return: {results['performance_metrics']['total_return']}%")
        logger.info(f"Sharpe Ratio: {results['performance_metrics']['sharpe_ratio']}")
        logger.info(f"Max Drawdown: {results['performance_metrics']['max_drawdown']}%")
        logger.info(f"Total Trades: {results['portfolio_summary']['total_trades']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise


def main():
    """Main entry point for the trading system"""
    logger.info("Trading system starting")
    cfg = _load_config()
    
    # Check mode
    mode = cfg.get("mode", "live")
    
    if mode == "backtest":
        # Run in backtest mode
        backtest_cfg = cfg.get("backtest", {})
        results = run_backtest(
            start_date=backtest_cfg.get("start_date"),
            end_date=backtest_cfg.get("end_date"),
            use_ml=False
        )
        logger.info("Backtest completed successfully")
        return results
    
    else:
        # Run in live mode
        logger.info("Initializing scheduler...")
        sched = BackgroundScheduler()
        cron_expr = cfg.get("schedule", "* * * * *")  # default to every minute
        if cron_expr.startswith("cron:"):
            cron_expr = cron_expr[5:]  # Remove the 'cron:' prefix
        minute, hour, dom, month, dow = cron_expr.strip().split()
        
        sched.add_job(pipeline, "cron", 
                     minute=minute, hour=hour, 
                     day=dom, month=month, 
                     day_of_week=dow)
        
        sched.start()
        logger.info(f"Scheduler started with cron: '{cron_expr}'")
        logger.info("System is running. Press Ctrl+C to exit.")
        
        # Run pipeline immediately on startup
        logger.info("Running initial pipeline...")
        pipeline()
        
        try:
            import time
            while True:
                time.sleep(10)  # Check for Ctrl+C every 10 seconds
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sched.shutdown()
            logger.info("System stopped.")

if __name__ == "__main__":
    main()
