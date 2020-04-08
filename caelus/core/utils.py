import logging


def change_logging_level(logger_name, level):
    logging.getLogger(logger_name).setLevel(level)
