'''
@Time    : 2022/2/28 11:14
@Author  : leeguandon@gmail.com
'''
import logging

logger_initialized = {}

def get_logger(name,log_file=None,log_level=logging.INFO,file_mode="w"):
    logger = logging.getLogger(name)
    if name in logger_initialized:
        return logger

    stream_handler = logging.StreamHandler()
    handlers = [stream_handler]

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    logger.setLevel(log_level)

    logger_initialized[name] = True

    return logger