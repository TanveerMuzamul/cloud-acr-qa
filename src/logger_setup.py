import logging
from pathlib import Path


def setup_logger(log_file: str = "logs/pipeline.log") -> logging.Logger:
    logger = logging.getLogger("acr_qa")
    logger.setLevel(logging.INFO)

    # prevent duplicate handlers if you run multiple times
    if logger.handlers:
        return logger

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized")
    return logger