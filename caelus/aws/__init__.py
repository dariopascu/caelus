import logging

__aws_logger = logging.getLogger('aws')
__aws_logger.setLevel(logging.INFO)

__all__ = [
    'auth',
    'storages',
    'users',
]
