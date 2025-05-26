import logging
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Create logs directory
LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"
LOGS_DIR.mkdir(exist_ok=True, parents=True)

class PipelineContext:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PipelineContext()
        return cls._instance
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset context for new pipeline run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.pipeline_id = f"pipeline_{timestamp}_{uuid.uuid4().hex[:6]}"
        self.log_file = LOGS_DIR / f"{self.pipeline_id}.log"
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Remove existing handlers
        logging.getLogger().handlers = []
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - Pipeline %(pipeline_id)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name):
        """Get a logger with pipeline context"""
        logger = logging.getLogger(name)
        # Add pipeline_id to all log records
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.pipeline_id = self.pipeline_id
            return record
        logging.setLogRecordFactory(record_factory)
        return logger

# Global access to pipeline context
def get_pipeline_context():
    return PipelineContext.get_instance()

def get_logger(name):
    """Convenience function to get a logger"""
    return get_pipeline_context().get_logger(name) 