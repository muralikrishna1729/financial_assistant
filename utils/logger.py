import logging
import os
from datetime import datetime

LOG_PATH = "logs"
LOG_FILE_PATH = "logs/" 
def setup_logging():
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(log_folder,f"{timestamp}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename), 
            logging.StreamHandler()         # Prints to your terminal
        ],
        force = True
    )
    logger = logging.getLogger("FinancialAgent")
    logger.info(f"--- New Session Started: {log_filename} ---")
    return logger

logger = setup_logging()