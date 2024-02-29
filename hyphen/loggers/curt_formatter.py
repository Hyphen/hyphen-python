from pathlib import Path
from copy import copy
import logging


class CurtFormatter(logging.Formatter):
    def format(self, record):
        # Replace the levelname with its first letter colored
        try:
            record = copy(record)  # don't leak to other formatters
        except TypeError:
            # let it be verbose if there's a problem with the traceback
            return super().format(record)

        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        bold_red = "\x1b[31;1m"
        green = "\x1b[32;20m"
        reset = "\x1b[0m"

        match record.levelno:
            case logging.INFO:
                record.levelname = f"{green}{record.levelname[0]}{reset}"
            case logging.WARNING:
                record.levelname = f"{yellow}{record.levelname[0]}{reset}"
            case logging.ERROR:
                record.levelname = f"{bold_red}{record.levelname[0]}{reset}"
            case logging.CRITICAL:
                record.levelname = f"{bold_red}{record.levelname[0]}{reset}"
            case _:
                record.levelname = f"{grey}{record.levelname[0]}{reset}"

        # Replace filename with just the end of the path
        record.filename = Path(record.filename).name
        return super().format(record)
