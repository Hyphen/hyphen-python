from typing import Optional
import logging

def get_logger(name: str, level:Optional[str]=None):
    """See library best practices for logging: https://docs.python.org/3/howto/logging.html#library-config"""
    logger = logging.getLogger("hyphen")
    logger.addHandler(logging.NullHandler())
    if level:
        logger.setLevel(level)
    return logger.getChild(name)