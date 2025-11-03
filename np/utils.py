from np import DEV
import logging

from PySide6.QtCore import QSettings

settings = QSettings()
def _setupLogger(name, log_file = None, level=logging.ERROR):
    if DEV:
        level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(level)


    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

log = _setupLogger("now-playing")

