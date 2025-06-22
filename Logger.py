import colorlog
import logging
from logging.handlers import RotatingFileHandler
import os

# Get the project directory (one level up from the current file)
project_directory = os.path.dirname(os.path.abspath(__file__))
print(f"Project directory: {project_directory}")  # Debug print

# Create logs directory in the project directory
log_directory = os.path.join(project_directory, 'logs')
print(f"Logs directory: {log_directory}")  # Debug print

if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    print(f"Created logs directory at: {log_directory}")  # Debug print

# Create file handler
log_file_path = os.path.join(log_directory, 'application.log')
print(f"Log file path: {log_file_path}")  # Debug print

file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1024 * 1024,  # 1MB
    backupCount=1
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Console handler with colors
console_handler = colorlog.StreamHandler()
console_handler.setFormatter(colorlog.ColoredFormatter(
    fmt='%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

logger.propagate = False

# Add a test log message
logger.info("Test log message")