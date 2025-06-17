# File: error_handling/logging_setup.py
"""Enhanced logging configuration for the D&D system with advanced features."""

import logging
import logging.handlers
import os
import json
import sys
import functools
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import threading

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output to improve readability."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to the log level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging - useful for log analysis tools."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, 'creature_name'):
            log_entry['creature_name'] = record.creature_name
        if hasattr(record, 'spell_name'):
            log_entry['spell_name'] = record.spell_name
        if hasattr(record, 'combat_round'):
            log_entry['combat_round'] = record.combat_round
        
        return json.dumps(log_entry)

class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""
    
    def __init__(self):
        super().__init__()
        self.context = threading.local()
    
    def filter(self, record):
        # Add context information if available
        if hasattr(self.context, 'current_creature'):
            record.creature_name = self.context.current_creature
        if hasattr(self.context, 'current_spell'):
            record.spell_name = self.context.current_spell
        if hasattr(self.context, 'combat_round'):
            record.combat_round = self.context.combat_round
        
        return True
    
    def set_context(self, **kwargs):
        """Set context information for subsequent log messages."""
        for key, value in kwargs.items():
            setattr(self.context, key, value)
    
    def clear_context(self):
        """Clear all context information."""
        self.context = threading.local()

class PerformanceLogger:
    """Logger for tracking performance metrics."""
    
    def __init__(self, logger_name='Performance'):
        self.logger = logging.getLogger(logger_name)
        self.operation_times = {}
    
    def start_operation(self, operation_name: str):
        """Start timing an operation."""
        import time
        self.operation_times[operation_name] = time.time()
    
    def end_operation(self, operation_name: str, log_level=logging.INFO):
        """End timing an operation and log the duration."""
        import time
        if operation_name in self.operation_times:
            duration = time.time() - self.operation_times[operation_name]
            self.logger.log(log_level, f"Operation '{operation_name}' took {duration:.3f} seconds")
            del self.operation_times[operation_name]
            return duration
        return None

class LogManager:
    """Central manager for all logging configuration and setup."""
    
    def __init__(self):
        self.loggers = {}
        self.context_filter = ContextFilter()
        self.performance_logger = PerformanceLogger()
        self.log_directory = Path('logs')
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            'log_level': logging.INFO,
            'console_output': True,
            'file_output': True,
            'json_output': False,
            'colored_console': True,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5,
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'date_format': '%Y-%m-%d %H:%M:%S'
        }
    
    def setup_logging(self, config: Optional[Dict] = None) -> logging.Logger:
        """Set up comprehensive logging with enhanced features."""
        # Update config with any provided overrides
        if config:
            self.config.update(config)
        
        # Create logs directory
        self.log_directory.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config['log_level'])
        
        # Clear any existing handlers
        root_logger.handlers.clear()
        
        # Set up file logging with rotation
        if self.config['file_output']:
            self._setup_file_logging(root_logger)
        
        # Set up console logging
        if self.config['console_output']:
            self._setup_console_logging(root_logger)
        
        # Set up JSON logging if requested
        if self.config['json_output']:
            self._setup_json_logging(root_logger)
        
        # Create specialized loggers
        self._setup_specialized_loggers()
        
        # Add context filter to all loggers
        for handler in root_logger.handlers:
            handler.addFilter(self.context_filter)
        
        main_logger = logging.getLogger('DnDSystem')
        main_logger.info(f"D&D System logging initialized with enhanced features")
        
        return main_logger
    
    def _setup_file_logging(self, logger):
        """Set up rotating file logging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_directory / f'dnd_system_{timestamp}.log'
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config['max_file_size'],
            backupCount=self.config['backup_count']
        )
        file_handler.setLevel(self.config['log_level'])
        
        # Standard formatter for files
        file_formatter = logging.Formatter(
            self.config['log_format'],
            datefmt=self.config['date_format']
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Also create a "latest" symlink/copy
        latest_log = self.log_directory / 'dnd_latest.log'
        latest_handler = logging.FileHandler(latest_log, mode='w')
        latest_handler.setLevel(self.config['log_level'])
        latest_handler.setFormatter(file_formatter)
        logger.addHandler(latest_handler)
    
    def _setup_console_logging(self, logger):
        """Set up console logging with optional colors."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.config['log_level'])
        
        if self.config['colored_console']:
            console_formatter = ColoredFormatter(
                self.config['log_format'],
                datefmt=self.config['date_format']
            )
        else:
            console_formatter = logging.Formatter(
                self.config['log_format'],
                datefmt=self.config['date_format']
            )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    def _setup_json_logging(self, logger):
        """Set up JSON structured logging."""
        json_file = self.log_directory / 'dnd_system.jsonl'
        json_handler = logging.FileHandler(json_file)
        json_handler.setLevel(self.config['log_level'])
        json_handler.setFormatter(JSONFormatter())
        logger.addHandler(json_handler)
    
    def _setup_specialized_loggers(self):
        """Set up specialized loggers for different systems."""
        # System-specific loggers with appropriate levels
        systems = {
            'DnDSystem': logging.INFO,
            'SpellSystem': logging.INFO,
            'AttackSystem': logging.INFO,
            'CombatSystem': logging.INFO,
            'ActionSystem': logging.DEBUG,
            'InitiativeSystem': logging.INFO,
            'DamageSystem': logging.INFO,
            'ConditionSystem': logging.INFO,
            'Performance': logging.INFO
        }
        
        for system_name, level in systems.items():
            logger = logging.getLogger(system_name)
            logger.setLevel(level)
            self.loggers[system_name] = logger
    
    def get_logger(self, name='DnDSystem') -> logging.Logger:
        """Get a logger for a specific system."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            logger.setLevel(self.config['log_level'])
            self.loggers[name] = logger
        return self.loggers[name]
    
    def set_context(self, **kwargs):
        """Set logging context for all subsequent log messages."""
        self.context_filter.set_context(**kwargs)
    
    def clear_context(self):
        """Clear logging context."""
        self.context_filter.clear_context()
    
    def log_performance(self, operation_name: str, duration: float, details: Optional[Dict] = None):
        """Log performance information."""
        message = f"PERFORMANCE: {operation_name} took {duration:.3f}s"
        if details:
            message += f" - {details}"
        self.performance_logger.logger.info(message)
    
    def get_log_stats(self) -> Dict:
        """Get statistics about current logging setup."""
        root_logger = logging.getLogger()
        return {
            'log_directory': str(self.log_directory),
            'log_level': logging.getLevelName(self.config['log_level']),
            'handlers_count': len(root_logger.handlers),
            'specialized_loggers': list(self.loggers.keys()),
            'log_files': [f.name for f in self.log_directory.glob('*.log')] if self.log_directory.exists() else []
        }
    
    def emergency_log(self, message: str, details: Optional[Dict] = None):
        """Emergency logging that writes directly to file even if logging is broken."""
        try:
            emergency_file = self.log_directory / 'emergency.log'
            with open(emergency_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"[{timestamp}] EMERGENCY: {message}\n")
                if details:
                    f.write(f"[{timestamp}] DETAILS: {json.dumps(details)}\n")
        except Exception as e:
            # Last resort - print to stderr
            print(f"EMERGENCY LOG FAILED: {message} | Error: {e}", file=sys.stderr)

# Global log manager instance
log_manager = LogManager()

# Legacy functions for backward compatibility
def setup_dnd_logging(log_level=logging.INFO, **kwargs):
    """Set up D&D logging (legacy interface)."""
    config = {'log_level': log_level, **kwargs}
    return log_manager.setup_logging(config)

def get_logger(name='DnDSystem'):
    """Get a logger for a specific system (legacy interface)."""
    return log_manager.get_logger(name)

# Context managers for enhanced logging
class LoggingContext:
    """Context manager for adding context to log messages."""
    
    def __init__(self, **context):
        self.context = context
    
    def __enter__(self):
        log_manager.set_context(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        log_manager.clear_context()

class PerformanceContext:
    """Context manager for tracking operation performance."""
    
    def __init__(self, operation_name: str, logger_name='Performance'):
        self.operation_name = operation_name
        self.logger = logging.getLogger(logger_name)
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        if self.start_time:
            duration = time.time() - self.start_time
            if exc_type:
                self.logger.warning(f"Operation '{self.operation_name}' failed after {duration:.3f}s: {exc_val}")
            else:
                self.logger.info(f"Operation '{self.operation_name}' completed in {duration:.3f}s")

# Initialize the logging system when module is imported
dnd_logger = log_manager.setup_logging()

# Enhanced Combat System integration
class EnhancedCombatLogging:
    """Enhanced logging specifically for combat operations."""
    
    @staticmethod
    def log_combat_start(participants, round_number=1):
        """Log the start of combat with participants."""
        logger = get_logger('CombatSystem')
        participant_names = [p.name for p in participants if hasattr(p, 'name')]
        
        with LoggingContext(combat_round=round_number):
            logger.info(f"Combat started with {len(participants)} participants: {', '.join(participant_names)}")
    
    @staticmethod
    def log_turn_start(creature, round_number, turn_number):
        """Log the start of a creature's turn."""
        logger = get_logger('CombatSystem')
        
        with LoggingContext(creature_name=creature.name, combat_round=round_number, turn_number=turn_number):
            logger.info(f"Turn started: {creature.name} (Round {round_number}, Turn {turn_number})")
    
    @staticmethod
    def log_action_attempt(performer, action_name, target=None):
        """Log an action attempt."""
        logger = get_logger('ActionSystem')
        target_info = f" against {target.name}" if target and hasattr(target, 'name') else ""
        
        with LoggingContext(creature_name=performer.name, action_name=action_name):
            logger.info(f"Action attempt: {performer.name} tries {action_name}{target_info}")
    
    @staticmethod
    def log_spell_cast(caster, spell_name, targets=None, spell_level=None):
        """Log spell casting with details."""
        logger = get_logger('SpellSystem')
        target_names = []
        if targets:
            if hasattr(targets, '__iter__') and not isinstance(targets, str):
                target_names = [t.name for t in targets if hasattr(t, 'name')]
            elif hasattr(targets, 'name'):
                target_names = [targets.name]
        
        target_info = f" targeting {', '.join(target_names)}" if target_names else ""
        level_info = f" at level {spell_level}" if spell_level else ""
        
        with LoggingContext(creature_name=caster.name, spell_name=spell_name):
            logger.info(f"Spell cast: {caster.name} casts {spell_name}{level_info}{target_info}")
    
    @staticmethod
    def log_damage_dealt(target, damage_amount, damage_type, source=None):
        """Log damage being dealt."""
        logger = get_logger('DamageSystem')
        source_info = f" from {source.name}" if source and hasattr(source, 'name') else ""
        
        context = {'creature_name': target.name, 'damage_amount': damage_amount, 'damage_type': damage_type}
        if source and hasattr(source, 'name'):
            context['damage_source'] = source.name
        
        with LoggingContext(**context):
            logger.info(f"Damage dealt: {target.name} takes {damage_amount} {damage_type} damage{source_info}")
    
    @staticmethod
    def log_condition_change(creature, condition, added=True):
        """Log condition additions or removals."""
        logger = get_logger('ConditionSystem')
        action = "gained" if added else "lost"
        
        with LoggingContext(creature_name=creature.name, condition=condition):
            logger.info(f"Condition change: {creature.name} {action} {condition} condition")
    
    @staticmethod
    def log_combat_end(winner=None, reason="Combat ended"):
        """Log the end of combat."""
        logger = get_logger('CombatSystem')
        winner_info = f" - Winner: {winner}" if winner else ""
        logger.info(f"Combat ended: {reason}{winner_info}")

# Utility functions for common logging patterns
def log_with_performance(operation_name: str, logger_name='Performance'):
    """Decorator to automatically log operation performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceContext(operation_name, logger_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def log_system_health():
    """Log current system health and statistics."""
    logger = get_logger('DnDSystem')
    
    # Get error statistics
    from error_handling.error_handler import DnDErrorHandler
    error_stats = DnDErrorHandler.get_error_metrics()
    
    # Get logging statistics
    log_stats = log_manager.get_log_stats()
    
    logger.info(f"System Health Check:")
    logger.info(f"  Total errors: {error_stats['total_errors']}")
    logger.info(f"  Recent errors: {error_stats['recent_errors_count']}")
    logger.info(f"  Log files: {len(log_stats['log_files'])}")
    logger.info(f"  Active loggers: {len(log_stats['specialized_loggers'])}")

# Export enhanced combat logging for use in other modules
__all__ = [
    'setup_dnd_logging', 'get_logger', 'dnd_logger', 'log_manager',
    'LoggingContext', 'PerformanceContext', 'EnhancedCombatLogging',
    'log_with_performance', 'log_system_health'
]