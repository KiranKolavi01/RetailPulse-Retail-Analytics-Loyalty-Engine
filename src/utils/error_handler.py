import logging
import os
import time
from datetime import datetime
from functools import wraps

# Setup basic rotating functionality for daily logs manually or using TimeRotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

# Define central log folder
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Application logger configuration
def setup_logger():
    logger = logging.getLogger("RetailPulse")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        current_date = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(LOG_DIR, f'retailpulse_{current_date}.log')
        
        # Use TimedRotatingFileHandler to rotate midnight
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
        handler.suffix = "%Y%m%d"
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Also console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()

# --- Custom Exception Hierarchy ---
class RetailPulseError(Exception):
    """Base exception for RetailPulse"""
    pass

class DatabaseError(RetailPulseError):
    """Connection, query, table issues"""
    pass

class FileError(RetailPulseError):
    """Missing files, permission errors"""
    pass

class ETLError(RetailPulseError):
    """Validation, transformation failures"""
    pass

class AnalyticsError(RetailPulseError):
    """Calculation, prediction errors"""
    pass

class DataValidationError(RetailPulseError):
    """Invalid data format/values"""
    pass

class ConfigurationError(RetailPulseError):
    """Missing config, invalid settings"""
    pass


# --- Utilities ---
def validate_file_exists(file_path: str):
    if not os.path.isfile(file_path):
        raise FileError(f"File not found: {file_path}")

def validate_directory_exists(dir_path: str):
    if not os.path.isdir(dir_path):
        raise FileError(f"Directory not found: {dir_path}")


# --- Decorators ---
def handle_exceptions(func):
    """Decorator for consistent error handling on all functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RetailPulseError as e:
            logger.error(f"RetailPulseError in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            raise RetailPulseError(f"Unexpected error in {func.__name__}: {str(e)}") from e
    return wrapper

def retry_on_error(retries=3, delay=1, exceptions=(Exception,)):
    """Decorator for transient failures"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    logger.warning(f"Attempt {attempt}/{retries} failed in {func.__name__}: {str(e)}")
                    if attempt >= retries:
                        logger.error(f"All {retries} retries failed for {func.__name__}")
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
