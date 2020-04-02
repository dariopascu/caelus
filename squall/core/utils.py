import logging


def change_logging_level(level):
    logging.getLogger().setLevel(level)
