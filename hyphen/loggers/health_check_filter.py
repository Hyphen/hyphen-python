import logging

class HealthcheckFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().find(" / ") == -1