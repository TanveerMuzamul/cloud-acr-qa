import logging
import os

def get_logger(name="acr_qa"):
    os.makedirs("../logs", exist_ok=True)
    log_path = "../logs/pipeline.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if you run multiple times
    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger