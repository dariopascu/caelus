import logging

__az_logger = logging.getLogger('az')
__az_logger.setLevel(logging.INFO)

__all__ = [
    'auth',
    'storages',
]
