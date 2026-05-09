"""Unified logging system for NOVA-SHIELD"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


class IconFormatter(logging.Formatter):
    """Add icons to log levels"""
    
    ICON_MAP = {
        logging.DEBUG: "[DEBUG]",
        logging.INFO: "[INFO]",
        logging.WARNING: "[WARN]",
        logging.ERROR: "[ERROR]",
        logging.CRITICAL: "[CRIT]"
    }
    
    def format(self, record):
        record.icon = self.ICON_MAP.get(record.levelno, "[LOG]")
        return super().format(record)


def setup_logger(name, log_level=logging.INFO, log_file=None):
    """Setup logger with console and file handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Console handler with icons
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = IconFormatter(
        '%(asctime)s | %(icon)s %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
    return logger


def get_logger(name):
    """Get configured logger"""
    return logging.getLogger(name)