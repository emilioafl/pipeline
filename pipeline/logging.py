import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

from pipeline.common.gitlab import PredefinedVariables

JOB_LOG_FILEPATH = f"/logs/{PredefinedVariables.CI_JOB_ID}.log"
MAX_BYTES = 5000000
BACKUP_COUNT = 5

def init_logger():
    LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s [logged at %(filename)s:%(lineno)d]"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = jsonlogger.JsonFormatter(LOG_FORMAT)

    # Log handler
    file_handler = RotatingFileHandler(
        filename=JOB_LOG_FILEPATH,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger