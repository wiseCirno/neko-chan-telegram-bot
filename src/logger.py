import sys

from loguru import logger

import src.config as config

logger.remove()

if config.IS_DEBUG_MODE:
    logger.add(sys.stderr, level = "DEBUG")
    logger.debug("DEBUG MODE ON")
else:
    logger.add(sys.stderr, level = "INFO")
