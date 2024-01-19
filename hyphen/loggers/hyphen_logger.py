import logging.config
import sys
import json_log_formatter  # noqa: pylint=unused-import

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
        "json": {
            "()": "json_log_formatter.VerboseJSONFormatter",
        },
        "curt": {
            "class": "hyphen.loggers.curt_formatter.CurtFormatter",
            "format": "%(levelname)s %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(message)s",
            "datefmt": "%-I:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "curt",
            "filters": ["healthcheck"],
        }
    },
    "filters": {
        "healthcheck": {
            "()": "hyphen.loggers.health_check_filter.HealthcheckFilter",
        }
    },
    "loggers": {
        "hyphen": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        }
    },
}
def get_logger(name: str):
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger("hyphen")
    return logger.getChild(name)