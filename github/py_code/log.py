import logging

def set_log(e):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    fh = logging.FileHandler('error.log')
    fh.setFormatter(LOG_FORMAT)
    logger.addHandler(fh)
    logger.error(e)