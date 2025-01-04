import os
import sys
from datetime import datetime
from typing import Optional

from loguru import logger as _logger

logger = _logger

current_path = os.path.dirname(os.path.abspath("__file__"))
log_path = os.path.join(
    current_path, "logs", datetime.now().strftime("%Y-%m-%d") + ".log"
)

def error_or_exception(message: str, exception: Optional[Exception], verbose: bool = True):
    logger.remove()
    logger.add(sys.stderr)
    logger.add(sink=log_path, level="INFO", rotation="10 MB")
    if verbose:
        logger.exception(message)
    else:
        logger.critical(f"{message} {exception!r}")
