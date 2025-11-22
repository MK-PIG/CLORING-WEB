import logging
import os
LOG_DIR = os.environ.get('LOG_DIR', '/app/data')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'CLORING.log')


def setup_info_logger():
    """Сетап логгера для информаци о рабое проекта

    Returns:
        Logger: логгер для общей информации
    """
    logger = logging.getLogger("INFO_logger")
    logger.setLevel(logging.INFO)

    file_handler_info = logging.FileHandler(LOG_FILE)
    file_handler_info.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler_info.setFormatter(formatter)

    logger.addHandler(file_handler_info)

    return logger


def setup_er_logger():
    """Сетап логгера для ошибок

    Returns:
        Logger: логгер для ошибок
    """
    er_logger = logging.getLogger("ERROR_logger")
    er_logger.setLevel(logging.ERROR)

    file_handler_errors = logging.FileHandler(LOG_FILE)
    file_handler_errors.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler_errors.setFormatter(formatter)

    er_logger.addHandler(file_handler_errors)

    return er_logger


def setup_fatal_logger():
    """Сетап логгера для фатальных ошибок

    Returns:
        Logger: логгер фатальных ошибок
    """
    fat_logger = logging.getLogger("FATAL_logger")
    fat_logger.setLevel(logging.FATAL)

    file_handler_fatal = logging.FileHandler(LOG_FILE)
    file_handler_fatal.setLevel(logging.FATAL)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler_fatal.setFormatter(formatter)

    fat_logger.addHandler(file_handler_fatal)

    return fat_logger


info_logger = setup_info_logger()

er_logger = setup_er_logger()

ft_logger = setup_fatal_logger()
