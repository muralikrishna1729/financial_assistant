import logging
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# ─────────────────────────────────────────────
# Logger Setup
# ─────────────────────────────────────────────

def get_logger(name: str = "financial_assistant") -> logging.Logger:
    """
    Creates and returns a logger that writes to:
      - Terminal (console) → for development
      - logs/app.log file  → for debugging later
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Format: timestamp | level | message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler 1: Console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Handler 2: File output
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Single shared instance — import this everywhere
logger = get_logger()