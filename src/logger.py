import datetime
import os
import sys

from loguru import logger

from src.config import IS_DEBUG_MODE, LOG_PATH

logger.remove()


def cleanup_old_logs(log_folder: str, retention_days: int = 7):
    cutoff = datetime.datetime.now() - datetime.timedelta(days = retention_days)
    for filename in os.listdir(log_folder):
        if filename.startswith("log_") and filename.endswith(".log"):
            try:
                if datetime.datetime.strptime(filename[4:-4], "%Y-%m-%d") < cutoff:
                    file_path = os.path.join(log_folder, filename)
                    os.remove(file_path)
                    logger.info(f"Deleted old log file: {filename}")
            except ValueError:
                logger.warning(f"Skipping file with unexpected name format: {filename}")
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {e}")


current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_file_path = os.path.join(LOG_PATH, f"log_{current_date}.log")

if IS_DEBUG_MODE:
    logger.add(sys.stderr, level = "DEBUG")
    logger.add(log_file_path, level = "DEBUG", rotation = "00:00", encoding = "utf-8")
    logger.debug("DEBUG MODE ON")
else:
    logger.add(sys.stderr, level = "INFO")
    logger.add(log_file_path, level = "INFO", rotation = "00:00", encoding = "utf-8")

cleanup_old_logs(LOG_PATH)
