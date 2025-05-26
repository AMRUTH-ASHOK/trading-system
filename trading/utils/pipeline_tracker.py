import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from .logging_utils import get_pipeline_context, get_logger

logger = get_logger(__name__)

class PipelineTracker:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[2] / "data"
        self.pipeline_id = get_pipeline_context().pipeline_id
        self.pipeline_dir = self.base_dir / "pipelines" / self.pipeline_id
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata
        self.metadata = {
            "pipeline_id": self.pipeline_id,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "raw_data": {},
            "features": {},
            "signals": [],
            "trades": []
        }
        self._save_metadata()
    
    def _save_metadata(self):
        """Save pipeline metadata"""
        with open(self.pipeline_dir / "metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def save_raw_data(self, df: pd.DataFrame):
        """Save raw market data"""
        file_path = self.pipeline_dir / "raw_data.csv"
        df.to_csv(file_path)
        self.metadata["raw_data"] = {
            "file": str(file_path),
            "symbols": df.index.get_level_values("symbol").unique().tolist(),
            "start_time": df.index.get_level_values("timestamp").min().isoformat(),
            "end_time": df.index.get_level_values("timestamp").max().isoformat()
        }
        self._save_metadata()
        logger.debug(f"Saved raw data for {len(self.metadata['raw_data']['symbols'])} symbols")
    
    def save_features(self, df: pd.DataFrame):
        """Save computed features"""
        file_path = self.pipeline_dir / "features.csv"
        df.to_csv(file_path, index=False)
        self.metadata["features"] = {
            "file": str(file_path),
            "feature_columns": [col for col in df.columns if col not in ["timestamp", "symbol"]],
            "symbols": df["symbol"].unique().tolist(),
            "start_time": df["timestamp"].min().isoformat(),
            "end_time": df["timestamp"].max().isoformat()
        }
        self._save_metadata()
        logger.debug(f"Saved features: {', '.join(self.metadata['features']['feature_columns'])}")
    
    def add_signal(self, signal_dict):
        """Add a trading signal"""
        self.metadata["signals"].append(signal_dict)
        self._save_metadata()
        logger.debug(f"Added signal: {signal_dict}")
    
    def add_trade(self, trade_dict):
        """Add an executed trade"""
        self.metadata["trades"].append(trade_dict)
        self._save_metadata()
        logger.debug(f"Added trade: {trade_dict}")
    
    def complete_pipeline(self, status="completed", error=None):
        """Mark pipeline as complete"""
        self.metadata["status"] = status
        if error:
            self.metadata["error"] = str(error)
        self._save_metadata()
        logger.info(f"Pipeline {self.pipeline_id} {status}")
    
    @classmethod
    def list_pipelines(cls):
        """List all pipeline runs"""
        pipeline_dir = Path(__file__).resolve().parents[2] / "data" / "pipelines"
        results = []
        for meta_file in pipeline_dir.glob("*/metadata.json"):
            with open(meta_file) as f:
                metadata = json.load(f)
                results.append(metadata)
        return sorted(results, key=lambda x: x["timestamp"], reverse=True)
    
    @classmethod
    def load_pipeline(cls, pipeline_id):
        """Load a specific pipeline's data"""
        pipeline_dir = Path(__file__).resolve().parents[2] / "data" / "pipelines" / pipeline_id
        
        # Load metadata
        with open(pipeline_dir / "metadata.json") as f:
            metadata = json.load(f)
        
        # Load raw data
        raw_data = None
        if (pipeline_dir / "raw_data.csv").exists():
            raw_data = pd.read_csv(pipeline_dir / "raw_data.csv")
            raw_data["timestamp"] = pd.to_datetime(raw_data["timestamp"])
            raw_data.set_index(["timestamp", "symbol"], inplace=True)
        
        # Load features
        features = None
        if (pipeline_dir / "features.csv").exists():
            features = pd.read_csv(pipeline_dir / "features.csv")
            features["timestamp"] = pd.to_datetime(features["timestamp"])
        
        return {
            "metadata": metadata,
            "raw_data": raw_data,
            "features": features
        } 