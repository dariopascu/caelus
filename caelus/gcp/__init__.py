import logging

__gcp_logger = logging.getLogger('gcp')
__gcp_logger.setLevel(logging.INFO)

__all__ = [
    'auth',
    'storages',
]
