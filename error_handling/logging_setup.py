# File: error_handling/logging_setup.py
"""Logging configuration for the D&D system."""

import logging
import os
from datetime import datetime

def setup_dnd_logging(log_level=logging.INFO):
    """Set up comprehensive logging for the D&D system."""
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f'dnd_system_{timestamp}.log')
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.FileHandler(os.path.join(logs_dir, 'dnd_latest.log')),  # Always current
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    # Create specialized loggers
    loggers = {
        'DnDSystem': logging.getLogger('DnDSystem'),
        'SpellSystem': logging.getLogger('SpellSystem'),
        'AttackSystem': logging.getLogger('AttackSystem'),
        'CombatSystem': logging.getLogger('CombatSystem'),
        'ActionSystem': logging.getLogger('ActionSystem')
    }
    
    # Set log levels for different systems
    loggers['SpellSystem'].setLevel(logging.INFO)
    loggers['AttackSystem'].setLevel(logging.INFO)
    loggers['CombatSystem'].setLevel(logging.INFO)
    loggers['ActionSystem'].setLevel(logging.DEBUG)
    
    print(f"D&D System logging initialized. Log file: {log_file}")
    
    return loggers['DnDSystem']

def get_logger(name='DnDSystem'):
    """Get a logger for a specific system."""
    return logging.getLogger(name)

# Initialize logging when imported
dnd_logger = setup_dnd_logging()